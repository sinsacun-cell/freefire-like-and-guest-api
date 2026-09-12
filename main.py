import httpx
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

app = FastAPI()

@app.get("/")
def read_root():
    return {"status": "online", "message": "FF Stat API Active"}

@app.api_route("/info", methods=["GET", "POST"])
async def get_player_info(request: Request, uid: str = None, region: str = "ind"):
    if not uid:
        try:
            body_data = await request.json()
            uid = body_data.get("uid")
            region = body_data.get("region", "ind")
        except Exception:
            pass

    if not uid:
        return JSONResponse(status_code=400, content={"status": "error", "message": "UID eksik"})

    api_url = f"https://free-fire-api-five.vercel.app/api/player?uid={uid}&region={region}"
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(api_url, timeout=10.0)
            if response.status_code == 200:
                p = response.json()
                return JSONResponse(content={
                    "status": "success",
                    "nickname": p.get("nickname", "Bilinmiyor"),
                    "created_at": p.get("account_created", "Bilinmiyor"),
                    "last_login": p.get("last_login", "Bilinmiyor"),
                    "likes": p.get("likes", 0),
                    "guild": p.get("guild_name", "Bir birliğe üye değil"),
                    "region": p.get("region", region.upper())
                })
            else:
                return JSONResponse(content={"status": "error", "message": "Oyuncu bulunamadı."})
        except Exception as e:
            return JSONResponse(content={"status": "error", "message": f"Bağlantı hatası: {str(e)}"})
