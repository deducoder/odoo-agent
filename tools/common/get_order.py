import os
import json
import requests
from datetime import datetime, timedelta
from typing import Optional
from dotenv import load_dotenv

from server import mcp  # Importa clase `mcp` desde el módulo `server`

load_dotenv()  # Carga las variables de entorno desde el archivo `.env`

from utils.date_parser import date_parser  # Importa función de parseo de periodos
from utils.order_type_map import order_type_map  # importa mapeo de tipos de orden


@mcp.tool()
def get_order(order_type: str, period: str = "", year: Optional[int] = None):
    """
    Recupera órdenes de Odoo a través de un Workflow de n8n
    Argumentos:
        order_type (str): Modelo de Odoo equivalente al tipo de orden
        month (str): Nombre del mes de la orden
        year (int): Año de la orden
    """
    n8n_base_url = os.getenv("N8N_BASE_URL")  # Obtiene variable desde el archivo .env
    n8n_webhook_path = os.getenv(
        "N8N_WEBHOOK_PATH"
    )  # Obtiene variable desde el archivo .env

    if not n8n_base_url or not n8n_webhook_path:  # Verifica integridad de las variables
        error = "Variables de entorno N8N_BASE_URL o N8N_WEBHOOK_PATH no definidas"
        print(error)
        return {"status": "error", "message": error}

    if (
        order_type in order_type_map.values()
    ):  # Verifica si la entrada contiene el recurso
        resource = order_type
    else:  # Mapea el tipo de orden a un recurso para el nodo de Odoo en n8n
        resource = order_type_map.get(order_type.lower())

    if not resource:  # Verifica existencia del recurso en la consulta
        error = f"Tipo de orden no soportado: {order_type}"
        print(error)
        return {"status": "error", "message": error}

    start_date, end_date, error = date_parser(
        period, year
    )  # Usar la nueva función para obtener el rango de fechas

    if error:  # Vertifica si la respueta del parser es un error
        print(error)
        return {"status": "error", "message": error}

    if not start_date or not end_date:  # Verifica si la respuesta contiene los valores
        return {"status": "error", "message": "No se pudo obtener el rango de fechas"}

    date_filer = ""  # Variable de tipo de modelo para los filtros de fechas

    if (
        resource == "purchase.order"
    ):  # Verifica si el modelo de filtro a usar es para órdenes de compra
        date_filer = "date_order"
    elif (
        resource == "mrp.production"
    ):  # Verifica si el modelo de filtro a usar es para órdenes de fabricación
        date_filer = "create_date"

    payload = {  # Construye estructura del JSON para enviar a n8n
        "tool": "get_order",
        "resource": resource,
        "options": {"fields": []},
        "filters": [],
    }

    payload["filters"].extend(
        [
            {
                "field": date_filer,
                "operator": "greaterOrEqual",
                "value": start_date.strftime("%Y-%m-%d %H:%M:%S"),
            },
            {
                "field": date_filer,
                "operator": "lesserOrEqual",
                "value": end_date.strftime("%Y-%m-%d %H:%M:%S"),
            },
        ]
    )

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
