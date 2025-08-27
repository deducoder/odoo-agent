import os
import json
import requests
from typing import Optional
from dotenv import load_dotenv

from server import mcp  # Importa clase `mcp` desde el módulo `server`

load_dotenv()  # Carga las variables de entorno desde el archivo `.env`


@mcp.tool()
def get_order_line(orders: list):
    """
    Recupera las líneas de producto de una o varias órdenes de compra
    Argumentos:
        orders (list): Lista de órdenes obtenidas desde `get_order` o una lista de nombres
    """
    n8n_base_url = os.getenv("N8N_BASE_URL")  # Obtiene variable desde el archivo .env
    n8n_webhook_path = os.getenv(
        "N8N_WEBHOOK_PATH"
    )  # Obtiene variable desde el archivo .env

    if not n8n_base_url or not n8n_webhook_path:  # Verifica integridad de las variables
        error = "Variables de entorno N8N_BASE_URL o N8N_WEBHOOK_PATH no definidas"
        print(error)
        return {"status": "error", "message": error}

    orders_data = (
        []
    )  # Variable de almacenamiento de IDs o nombres para filtros de incidencia
    resource = ""  # Tipo de recurso a usar según el tipo de entrada recibida
    filter_field = ""

    if orders and isinstance(
        orders[0], dict
    ):  # Evalua si la entrada es una lista de diccionarios
        try:
            orders_data = [
                order["id"] for order in orders
            ]  # Busca ID en el diccionario
            resource = "purchase.order.line"  # Define el recurso a usar
            filter_field = "order_id"  # Define el filtro a usar
        except KeyError as e:
            error = f"Error al extraer los IDs, la entrada no contiene clave `id`: {e}"
            print(error)
            return {"status": "error", "message": error}
    else:
        orders_data = orders  # Define la entrada como argumento
        resource = "purchase.order"  # Define el recurso a usar
        filter_field = "display_name"  # Define el filtro a usar

    payload = {  # Construye estructura del JSON para enviar a n8n
        "tool": "get_order_line",
        "resource": resource,
        "options": {"fields": []},
        "filters": [{"field": filter_field, "operator": "in", "value": orders_data}],
    }

    try:  # Envia el JSON al webhook de n8n
        headers = {"Content-Type": "application/json"}  # Define cabezera de la consulta
        response = requests.post(
            f"{n8n_base_url}/{n8n_webhook_path}",  # URL del Webhook
            headers=headers,
            data=json.dumps(payload),  # JSON a enviar
        )
        response.raise_for_status()  # Obtiene el estado
        return response.json()  # Regresa la respuesta de n8n

    except requests.exceptions.RequestException as es:
        error = f"Error al conectar con n8n: {es}"
        print(error)
        return {"status": "error", "message": error}
