from fastapi import Depends, HTTPException, status, Request
from ..database.redis_client import redis_client
from .token import Token
from ..logger import logger

class RBAC:
    """
    class methods to deal with RBAC.
    Recieve "roles" (list) as a parameter and match with redis db.
    """
    @staticmethod
    def require_token(request: Request):
        token = request.cookies.get("token")
        if not token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication token is missing."
            )
        payload = Token.decode_token(token=token)  # your custom decode wrapper
        user_id: str = payload.get("user_id")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token is missing required user information."
            )
        return user_id
    
    @staticmethod
    def require_role(roles: list):
        def role_checker(
            cred_user_id: str = Depends(RBAC.require_token),
            request: Request = None
        ):
            stored_roles = redis_client.hget(f"user_id:{cred_user_id}", "roles")
            if not stored_roles:
                logger.warning(f"User '{cred_user_id}' has no roles assigned | Endpoint: '{request.url.path}'")
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="No roles assigned. Access denied."
                )
            user_roles = stored_roles.decode().split(",")
            if any(role in user_roles for role in roles):
                return cred_user_id
            logger.warning(
                f"'Unauthorized' access attempt | User: '{cred_user_id}' | Endpoint: '{request.url.path}'"
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to access this endpoint."
            )
        return role_checker