from .redis_client import redis_client

class Data:

    def load_role():
        try:
            redis_client.hset("role:root", mapping={"name": "root"})
            redis_client.hset("role:admin", mapping={"name": "admin"})
            redis_client.hset("role:editor", mapping={"name": "editor"})
            redis_client.hset("role:viewer", mapping={"name": "viewer"})
        except Exception as e:
            return {f"Failed to load role data: {e}"}
    
    def load_user():
        try:
            redis_client.hset(
            "user_id:root",
            mapping={
                "username": "default_user",
                "password": "unique_password",
                "roles": ",".join(["root", "admin"])
            }
        )
        except Exception as e:
            return {f"Failed to load users: {e}"}

    @staticmethod
    def load_data():
        """
        This will load some initially required data like
        roles - ["root", "admin", "user"]
        and dummy users- ["user1", "user2"]
        *** YOU CAN ADD OR REMOVE THIS DATA ANYTIME YOU WANT ***
        *** YOU CAN ADD NEW ROLES AND USERS ***
        """
        try:
            Data.load_role()
            Data.load_user()
            print("Default roles and admin user initialized.")
        except Exception as e:
            return {f"Failed to execute LOAD DATA function. {e}"}
    
    @staticmethod    
    def create_user(user_id: str, username: str, password: str, roles: list):
        for role in roles:
                if not redis_client.hgetall(f"role:{role}"):
                    print(f"Role '{role}' not found. Please create the role first using create_role().")
                    return False
        if redis_client.keys(f"user_id:{user_id}"):
            print("User ID already exists. Please choose a different identifier.")
            return False
        try:
            from ..logger import logger
            redis_client.hset(
                f"user_id:{user_id}",
                mapping={
                    "username": username,
                    "password": password,
                    "roles": ",".join(roles) 
                }
            )
            logger.info(f"New user created. User ID: {user_id}, Username: {username}")
            print("User successfully saved to the database.")
            return True
        except Exception as e:
            return {f"Failed to add new user {e}"}
    
    @staticmethod
    def create_role(role: str):
        if redis_client.keys(f"role:{role}"):
            print("Role already exists in the database. Skipping creation.")
            return False
        try:
            from ..logger import logger
            redis_client.hset(f"role:{role}", mapping={"name": f"{role}"})
            logger.info(f"New role created. Role: {role}")
            print("Role successfully saved to the database.")
            return True
        except Exception as e:
            raise e
