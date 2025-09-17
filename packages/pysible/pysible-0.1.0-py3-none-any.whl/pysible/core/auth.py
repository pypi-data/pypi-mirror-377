from ..database.redis_client import redis_client
from fastapi.responses import JSONResponse
from .token import Token
from fastapi import HTTPException, status
from ..logger import logger

class Auth:

    @staticmethod
    def login(form_data):
        user_key = f"user_id:{form_data.username}"
        # Check if user exists
        if not redis_client.exists(user_key):
            logger.warning(f"Login failed | Username: {form_data.username} | Reason: user not found")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password."
            )
        stored_password = redis_client.hget(user_key, "password")
        if not stored_password:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password."
            )
        access_token = Token.create_token(user_id=form_data.username)
        response = JSONResponse(content={"message": "Login successful."})
        response.set_cookie(
            key="token",
            value=access_token,
            httponly=True,
            secure=True,      # important for production
            samesite="Strict" # prevents CSRF
        )
        logger.info(f"User '{form_data.username}' logged in successfully.")
        return response
        
    @staticmethod
    def logout(user_id: str ):
        if not user_id:
            logger.warning("Logout attempt without authentication.")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required. Please log in first."
            )
        response = JSONResponse(content={"message": f"User '{user_id}' logged out successfully."})
        response.delete_cookie(key="token")
        logger.info(f"User '{user_id}' logged out successfully.")
        return response
            