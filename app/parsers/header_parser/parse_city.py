from app.data.cities import CITIES_ES
from typing import List, Optional, Union

def parse_city(header: str) -> Optional[str]:
    """Extract city name appearing in the header."""
    for city in CITIES_ES:
        if city.upper() in header.upper():
            return city
    return None
