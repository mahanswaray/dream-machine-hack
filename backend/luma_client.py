import os
from lumaai import LumaAI

luma_client = LumaAI(auth_token=os.environ.get("LUMAAI_API_KEY"))