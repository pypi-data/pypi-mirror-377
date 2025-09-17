import time
from ..database.redis_client import redis_client
from fastapi import Request, HTTPException, Depends
from .rbac import RBAC
from ..logger import logger

class PyRate:

    @staticmethod
    def rate_limiter(rate: int, burst: int):
        """
        Returns a dependency function for FastAPI
        """
        def dependency(request: Request):
            client_ip = request.client.host
            key_tokens = f"tokens:{client_ip}"
            key_timestamp = f"timestamp:{client_ip}"
            now = time.time()

            tokens = redis_client.get(key_tokens)
            tokens = float(tokens) if tokens else burst

            last_refill = redis_client.get(key_timestamp)
            last_refill = float(last_refill) if last_refill else now

            elapsed = now - last_refill
            tokens = min(burst, tokens + elapsed * rate)

            if tokens < 1:
                logger.warning(f"'Too many requests' to endpoint: '{request.url.path}'")
                raise HTTPException(status_code=429, detail="Too many requests")

            tokens -= 1
            redis_client.set(key_tokens, tokens)
            redis_client.set(key_timestamp, now)

        return dependency


