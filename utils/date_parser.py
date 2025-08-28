import re
from datetime import datetime, timedelta
from typing import Optional
from .month_map import month_map


def date_parser(period: str, year: Optional[int] = None):
    """
    Calcula el rango de fechas de inicio y fin basado en un periodo de tiempo.

    Argumentos:
        period (str): Periodo de tiempo, ejemplo: hoy, ayer, esta semana, enero, 18 de agosto
        year (int): Año opcional, por defecto el año actual
    """

    current_date = (
        datetime.now()
    )  # Obtiene la fecha y hora actual para los cálculos relativos
    period = period.lower()

    if year is None:  # Si no se especifica el año, usa el año actual por defecto
        year = current_date.year

    match = re.match(
        r"(\d{1,2})\s+de\s+([a-zA-Z]+)", period
    )  # Usa una expresión regular para detectar el formato "día de mes"

    if (
        match
    ):  # Si la expresión regular encuentra una coincidencia, procesa el formato de fecha específica
        day = int(match.group(1))
        month_name = match.group(2)
        month_number = month_map.get(month_name)

        if month_number is None:  # Verifica si el nombre del mes es válido
            return None, None, f"Mes no soportado en la fecha `{month_name}`"

        try:  # Construye las fechas de inicio y fin para ese día específico
            start_date = datetime(year, month_number, day)
            end_date = start_date.replace(hour=23, minute=59, second=59)
            return start_date, end_date, None
        except ValueError as e:
            return None, None, f"Fecha inválida: {e}"

    elif period == "hoy":  # Calcula el inicio y fin del día actual
        start_date = current_date.replace(hour=0, minute=0, second=0)
        end_date = start_date.replace(hour=23, minute=59, second=59)

    elif period == "ayer":  # Calcula el inicio y fin del día anterior
        yesterday = current_date - timedelta(days=1)
        start_date = yesterday.replace(hour=0, minute=0, second=0)
        end_date = yesterday.replace(hour=23, minute=59, second=59)

    elif period == "esta semana":  # Calcula el inicio y fin de la semana actual
        start_date = current_date - timedelta(days=current_date.weekday())
        start_date = start_date.replace(hour=0, minute=0, second=0)
        end_date = start_date + timedelta(days=6)
        end_date = end_date.replace(hour=23, minute=59, second=59)

    elif (
        "último" in period or "últimos" in period
    ):  # Lógica para periodos de tiempo "últimos X meses/años"
        try:
            parts = period.split()
            number = int(parts[1])
            unit = parts[2]
            if "mes" in unit:
                start_date = current_date - timedelta(days=30 * number)
                end_date = current_date
            elif "año" in unit:
                start_date = current_date - timedelta(days=365 * number)
                end_date = current_date
            else:
                raise ValueError
            start_date = start_date.replace(hour=0, minute=0, second=0)
            end_date = end_date.replace(hour=23, minute=59, second=59)
        except (ValueError, IndexError):
            return None, None, f"Formato de periodo no soportado: {period}"

    elif (
        period in month_map
    ):  # Lógica para el nombre de un mes específico (ej. "enero")
        month_number = month_map.get(period)
        if year is None:
            year = current_date.year
        start_date = datetime(year, month_number, 1)  # type: ignore
        if month_number == 12:  # Lógica para caso especial del mes de diciembre
            end_date = datetime(year + 1, 1, 1) - timedelta(seconds=1)
        else:
            end_date = datetime(year, month_number + 1, 1) - timedelta(seconds=1)  # type: ignore

    else:
        return None, None, f"Periodo no soportado: {period}"

    return start_date, end_date, None
