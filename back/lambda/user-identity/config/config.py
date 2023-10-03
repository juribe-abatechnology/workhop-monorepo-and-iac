import os

secrets_manager = os.getenv('SECRET_MANAGER')

env = {
    "secrets": os.getenv('SECRET_MANAGER'),
    
}


ENGINE1="postgres"