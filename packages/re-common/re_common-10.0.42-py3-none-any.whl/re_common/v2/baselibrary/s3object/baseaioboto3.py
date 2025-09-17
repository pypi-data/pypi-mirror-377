import aioboto3
import aiofiles
from aiobotocore.config import AioConfig


# config = AioConfig(connect_timeout=600000, read_timeout=600000, retries={'max_attempts': 3},
#                    max_pool_connections=10)

class BaseAioBoto3(object):

    def __init__(self, aws_access_key_id, aws_secret_access_key, endpoint_url,
                 config=AioConfig(max_pool_connections=10)):
        self.aws_access_key_id = aws_access_key_id
        self.aws_secret_access_key = aws_secret_access_key
        self.endpoint_url = endpoint_url
        self.config = config
        self.boto_session = None

    async def initialize_class_variable(self):
        if self.boto_session is None:
            self.boto_session = aioboto3.Session(
                aws_access_key_id=self.aws_access_key_id,
                aws_secret_access_key=self.aws_secret_access_key,
            )

    async def read_minio_data(self, bucket, key):
        await self.initialize_class_variable()
        async with self.boto_session.client("s3", endpoint_url=self.endpoint_url, config=self.config) as s3:
            s3_ob = await s3.get_object(Bucket=bucket, Key=key)
            result = await s3_ob["Body"].read()
            return result

    # 异步下载大文件
    async def download_file(self, bucket: str, key: str, local_path: str):
        await self.initialize_class_variable()
        async with self.boto_session.client("s3", endpoint_url=self.endpoint_url, config=self.config) as s3:
            response = await s3.get_object(Bucket=bucket, Key=key)
            body = response["Body"]

            # 用异步方式写入本地
            async with aiofiles.open(local_path, "wb") as f:
                while True:
                    chunk = await body.read(10 * 1024 * 1024)  # 每次读 10MB
                    if not chunk:
                        break
                    await f.write(chunk)

        return local_path
