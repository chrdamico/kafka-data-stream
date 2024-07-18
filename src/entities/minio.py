from pydantic import BaseModel


class MinioConnectionInformation(BaseModel):
    connection_string: str
    access_key: str
    secret_key: str
    bucket_name: str
