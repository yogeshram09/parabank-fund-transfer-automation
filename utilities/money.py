"""Currency helpers: Decimal avoids floating-point balance calculation errors."""
import re
from decimal import Decimal , InvalidOperation


def parse_money ( value ) :
    """Extract a Decimal amount from UI strings such as '$1,234.50'."""
    cleaned = re.sub(r"[^0-9.\-]" , "" , str(value))
    try :
        return Decimal(cleaned)
    except InvalidOperation as exc :
        raise ValueError(f"Cannot parse currency value from UI: {value!r}") from exc
