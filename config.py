import os

# 访问令牌
ACCESS_TOKEN = os.getenv('ACCESS_TOKEN', 'your_access_token_here')

# MinIO 配置
MINIO_CONFIG = {
    "endpoint": os.getenv('MINIO_ENDPOINT', 'localhost:9000'),
    "access_key": os.getenv('MINIO_ACCESS_KEY', 'admin'),
    "secret_key": os.getenv('MINIO_SECRET_KEY', 'admin123'),
}

# 桶名称
BUCKET_NAME = os.getenv('BUCKET_NAME', 'videos')