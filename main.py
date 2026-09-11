# Koruyucu Kaynak Lisansı v1.0 (PSL-1.0)
# Telif hakkı (c) 2025 Kaif

import asyncio
import json
from fastapi import FastAPI, HTTPException, Request

from pydantic import BaseModel

app = FastAPI()

class LikeRequest(BaseModel):
    uid: str
    region: str = "ind"

@app.get("/")
def read_root():
    return {"status": "online", "message": "Free Fire Like API"}

@app.api_route("/like", methods=["GET", "POST"])
async def send_like(
    server_name: str = None, 
    uid: str = None, 
    region: str = "ind", 
    data: LikeRequest = None
):
    req_uid = uid or (data.uid if data else None)
    req_region = server_name or region or (data.region if data else "ind")
    
    if not req_uid:
        raise HTTPException(status_code=400, detail="UID missing")
        
    return {"status": "success", "uid": req_uid, "region": req_region}

async def send_like(data: LikeRequest):
    if not data.uid:
        raise HTTPException(status_code=400, detail="UID gereklidir.")
    return {"status": "success", "uid": data.uid, "message": "Beğeni isteği işleme alındı."}
