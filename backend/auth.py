
from fastapi import Header, HTTPException
import jwt, time
SECRET='pcdf-secret'
def get_current_user(authorization: str = Header(...)):
    try:
        token=authorization.split()[1]
        payload=jwt.decode(token, SECRET, algorithms=['HS256'])
        return payload
    except Exception:
        raise HTTPException(401,'Invalid token')
