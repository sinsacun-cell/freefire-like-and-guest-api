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
    return {"status": "online", "message": "API Active"}

@app.api_route("/like", methods=["GET", "POST"])
async def send_like(
    request: Request,
    server_name: str = None, 
    uid: str = None, 
    region: str = "ind", 
    data: LikeRequest = None
):
    req_uid = uid or (data.uid if data else None)
    req_region = server_name or region or (data.region if data else "ind")
    
    if not req_uid:
        try:
            body_data = await request.json()
            req_uid = body_data.get("uid")
            req_region = body_data.get("server_name") or body_data.get("region") or req_region
        except Exception:
            pass

    if not req_uid:
        raise HTTPException(status_code=400, detail="UID missing")

    return {
        "status": "success", 
        "message": f"Like request processed for UID: {req_uid}",
        "uid": req_uid, 
        "region": req_region
    }
