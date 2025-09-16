from datetime import datetime, timedelta

from src.types import EXP_UNIT_T


def new_expiration_date(current_datetime: datetime, unit: EXP_UNIT_T, value: int) -> datetime:
    match unit:
        case "m":
            return current_datetime + timedelta(minutes=value)
        case "h":
            return current_datetime + timedelta(hours=value)
        case "d":
            return current_datetime + timedelta(days=value)
        case "w":
            return current_datetime + timedelta(weeks=value)
        case _:
            raise ValueError(f"Invalid time unit: {unit}")
