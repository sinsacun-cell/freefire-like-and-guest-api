# Koruyucu Kaynak Lisansı v1.0 (PSL-1.0)
# Telif hakkı (c) 2025 Kaif

import asyncio
import json
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

class LikeRequest(BaseModel):
    uid: str
    region: str = "ind"

@app.get("/")
def read_root():
    return {"status": "online", "message": "Free Fire Like API"}

@app.post("/like")
async def send_like(data: LikeRequest):
    if not data.uid:
        raise HTTPException(status_code=400, detail="UID gereklidir.")
    return {"status": "success", "uid": data.uid, "message": "Beğeni isteği işleme alındı."}
