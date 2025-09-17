import typer
import shutil
import os
from dotenv import load_dotenv
import time

app = typer.Typer()

def starter(project_name) -> bool:
    try:
        from .database.redis_client import redis_client
        print("Loading .env ...")
        print("Loaded .env to system...")
        print("Checking Redis connection...")
        time.sleep(1)
        if redis_client.ping()!=None:
            print("Redis connection established successfully.")
            time.sleep(1)
            # Enable Append Only File
            redis_client.config_set("appendonly", "yes")
            redis_client.config_set("appendfsync", "everysec")
            print("AOF persistence enabled.")
            time.sleep(1)
            return True
        if redis_client.ping()==None:
            print("Redis connection failed.")
            return False
    except Exception as e:
        print("Unable to establish connection with Redis.")
        shutil.rmtree(project_name)
        raise e

@app.command()
def action():
    try:
        project_name = typer.prompt("Project name:->").strip()
        is_redis = typer.prompt("Is Redis currently running? (yes/no): ").strip().lower()
        if is_redis=="yes":
            redis_host = typer.prompt("Enter the Redis host (e.g., 'localhost' for local instance): ").strip().lower()
            redis_port = typer.prompt("Port of Redis:->").strip().lower()
            redis_db_no = typer.prompt("Enter the Redis database number (e.g., '0', '1'): ").strip().lower()
            want_dummy_data = typer.prompt("Do you want to load dummy data for testing? (yes/no): ").strip().lower()
            secret_key = typer.prompt("Do you want to set your own secret key? (Type your unique key(string) or NO): ").strip().lower()
            # Create project folder
            os.makedirs(project_name, exist_ok=True)
            # Create .env file
            env_content = f"""
        REDIS_HOST={redis_host}
        REDIS_PORT={redis_port}
        REDIS_DB_NUMBER={redis_db_no}
                            """
            if secret_key=="yes":
                env_content += f"\nSECRET_KEY={secret_key}"
            elif secret_key=="no":
                print("SECRET_KEY must be set in 'Production' ! Please configure it as an environment variable.")
                time.sleep(2)
            with open(f"{project_name}/.env", "w") as f:
                f.write(env_content)
            # explicitly load the .env file you just created
            env_path = os.path.join(project_name, ".env")
            load_dotenv(dotenv_path=env_path, override=True)
            # Define folders and files
            folders = ["static", "src", "tests", "logs"]
            files = [".gitignore", "requirements.txt", "README.md", "LICENSE"]
            # Create folders
            print(f"Creating Project Structure for: {project_name}")
            time.sleep(1)
            for folder in folders:
                folder_path = os.path.join(project_name, folder)
                os.makedirs(folder_path, exist_ok=True)
            # Create files
            for file in files:
                file_path = os.path.join(project_name, file)
                if not os.path.exists(file_path):
                    with open(file_path, "w") as f:
                        if file == "README.md":
                            f.write("# Project Title\n\nProject description goes here.\n")
                        elif file == "requirements.txt":
                            f.write("# Add project dependencies here\n")
                        elif file == ".gitignore":
                            f.write("__pycache__/\n*.pyc\n.env\n")
                else:
                    print(f"File already exists: {file_path}")
            """
            Check Redis connection
            """
            starter(project_name)
            """
            Creating Required Files & Folders
            """
            if want_dummy_data=="yes":
                from .database.db import Data
                Data.load_data()
                print("Loading default users and roles...")
                time.sleep(1)
            # If everything goes well then your have your Project Folder.
            typer.echo(f"Project {project_name} created with .env file \u2764 \U0001F680")
        elif is_redis=="no":
            print("A running Redis instance is required for Pysible to function.\nPlease start Redis before continuing.")
    except Exception as e:
        return e

def main():
    app()
