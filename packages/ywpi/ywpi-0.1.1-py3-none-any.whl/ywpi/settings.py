import os

YWPI_HUB_HOST = os.getenv('YWPI_HUB_HOST', 'localhost:50051')

# By default name of the working directory
env_project_name = os.getenv('YWPI_PROJECT_NAME')
YWPI_PROJECT_NAME = env_project_name if env_project_name is not None else os.path.split(os.getcwd())[1]

# gRPC settings
YWPI_GRPC_MAX_MESSAGE_SIZE = int(os.getenv('YWPI_GRPC_MAX_MESSAGE_SIZE', 1024 * 1024 * 1024)) # Default 1G
