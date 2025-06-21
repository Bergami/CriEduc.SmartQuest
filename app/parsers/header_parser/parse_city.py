from app.core.cities import CITIES_ES


def parse_city(header: str) -> str | None:
    """Extract city name appearing in the header."""
    for city in CITIES_ES:
        if city.upper() in header.upper():
            return city
    return None
