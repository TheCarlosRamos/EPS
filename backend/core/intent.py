import re

def parse_intent(query: str) -> dict:
    q = query.strip()
    if re.match(r"\d{3}\.?\d{3}\.?\d{3}-?\d{2}", q):
        return {"type": "CPF", "value": q}
    if "@" in q:
        return {"type": "EMAIL", "value": q}
    if re.match(r"\+?\d{8,13}", q):
        return {"type": "PHONE", "value": q}
    return {"type": "NAME", "value": q}
