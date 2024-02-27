from decimal import Decimal, InvalidOperation

def is_decimal(s):
    try:
        Decimal(s)
        return True
    except InvalidOperation:
        return False