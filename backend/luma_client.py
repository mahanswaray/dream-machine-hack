import os
from lumaai import AsyncLumaAI

luma_client = AsyncLumaAI(
    auth_token=os.environ.get("LUMAAI_API_KEY"),
)