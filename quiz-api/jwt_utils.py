import jwt
import datetime

secret = "secret"

def build_token():
    """Construit un JWT valide pour 1 heure"""
    payload = {
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1),
        "iat": datetime.datetime.utcnow(),
        "sub": "admin"
    }
    token = jwt.encode(payload, secret, algorithm="HS256")
    return token

def decode_token(token):
    """Vérifie et décode un JWT"""
    try:
        decoded = jwt.decode(token, secret, algorithms=["HS256"])
        return decoded
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None
