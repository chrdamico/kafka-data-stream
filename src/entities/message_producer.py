from pydantic import BaseModel


class ImageSize(BaseModel):
    width: int
    height: int
    channels: int
