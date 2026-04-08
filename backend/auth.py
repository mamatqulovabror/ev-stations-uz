from jose import jwt
from datetime import datetime, timedelta

SECRET_KEY = "SECRET123"
ALGORITHM = "HS256"

def create_token(user_id: int):
    payload = {
        "user_id": user_id,
        "exp": datetime.utcnow() + timedelta(days=7)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
