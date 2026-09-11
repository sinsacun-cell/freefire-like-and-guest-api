import httpx
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel

app = FastAPI()

class UserRequest(BaseModel):
    uid: str
    region: str = "ind"

@app.get("/")
def read_root():
    return {"status": "online", "message": "FF Stat API Active"}

@app.api_route("/info", methods=["GET", "POST"])
async def get_player_info(
    request: Request,
    uid: str = None, 
    region: str = "ind", 
    data: UserRequest = None
):
    req_uid = uid or (data.uid if data else None)
    req_region = region or (data.region if data else "ind")
    
    if not req_uid:
        try:
            body_data = await request.json()
            req_uid = body_data.get("uid")
            req_region = body_data.get("region") or req_region
        except Exception:
            pass

    if not req_uid:
        raise HTTPException(status_code=400, detail="UID eksik")

    # Oyun verilerini çeken servis
    api_url = f"https://free-fire-api-five.vercel.app/api/player?uid={req_uid}&region={req_region}"
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(api_url, timeout=10.0)
            if response.status_code == 200:
                p = response.json()
                
                return {
                    "status": "success",
                    "nickname": p.get("nickname", "Bilinmiyor"),
                    "created_at": p.get("account_created", "Bilinmiyor"),
                    "last_login": p.get("last_login", "Bilinmiyor"),
                    "likes": p.get("likes", 0),
                    "guild": p.get("guild_name", "Bir birliğe üye değil")
                }
            else:
                return {"status": "error", "message": "Oyuncu bulunamadı."}
        except Exception as e:
            return {"status": "error", "message": f"Bağlantı hatası: {str(e)}"}
