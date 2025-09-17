from datetime import datetime, timedelta
from jose import jwt, JWTError
import os

DEFAULT_SECRET_KEY = ".P-L-E-A-S-E-@-C-H-A-N-G-E-@-T-H-I-S-@-K-E-Y."
SECRET_KEY = os.getenv("SECRET_KEY", DEFAULT_SECRET_KEY)
ALGORITHM = "HS256"
ACCESS_EXPIRE_MIN = 30

class Token:
    
    @staticmethod
    def create_token(user_id: str):
        expire = datetime.now() + timedelta(minutes=ACCESS_EXPIRE_MIN)
        to_encode = {"user_id": user_id, "exp": expire}
        return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    @staticmethod
    def decode_token(token: str):
        try:
            return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        except JWTError:
            return None