import httpx
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

app = FastAPI()

TELEGRAM_BOT_TOKEN = "8909841952:AAEaInTW2VGYirq2TN1qslFQBJw7XjKq7b8"
EXTERNAL_API = "https://free-fire-api-five.vercel.app/api/player"

async def send_telegram_message(chat_id: int, text: str):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "Markdown"}
    async with httpx.AsyncClient() as client:
        await client.post(url, json=payload)

@app.get("/")
@app.post("/")
async def root_handler(request: Request):
    # Telegram webhook varsayılan ana dizine (/) istek gönderirsa da yakala
    if request.method == "POST":
        return await handle_telegram_update(request)
    return {"status": "online", "message": "FF Stat API & Webhook Active"}

@app.api_route("/webhook", methods=["GET", "POST"])
async def webhook_handler(request: Request):
    if request.method == "POST":
        return await handle_telegram_update(request)
    return {"status": "webhook endpoint ready"}

async def handle_telegram_update(request: Request):
    try:
        data = await request.json()
        message = data.get("message", {})
        text = message.get("text", "")
        chat_id = message.get("chat", {}).get("id")

        if not chat_id or not text:
            return JSONResponse(status_code=200, content={"status": "ignored"})

        if text.startswith("/bilgi") or text.startswith("/info"):
            parts = text.split()
            if len(parts) < 2:
                await send_telegram_message(chat_id, "Lütfen bir UID girin.\nÖrnek: `/bilgi 1875588196 eu`")
                return JSONResponse(status_code=200, content={"status": "ok"})

            uid = parts[1]
            region = parts[2].lower() if len(parts) > 2 else "eu"

            async with httpx.AsyncClient() as client:
                try:
                    res = await client.get(f"{EXTERNAL_API}?uid={uid}&region={region}", timeout=10.0)
                    if res.status_code == 200:
                        p = res.json()
                        reply = (
                            f"🎮 **Free Fire Oyuncu Bilgisi**\n\n"
                            f"👤 **Hesap Adı:** {p.get('nickname', 'Bilinmiyor')}\n"
                            f"🌍 **Bölge:** {p.get('region', region.upper())}\n"
                            f"📅 **Kuruluş Tarihi:** {p.get('account_created', 'Bilinmiyor')}\n"
                            f"⏰ **Son Giriş:** {p.get('last_login', 'Bilinmiyor')}\n"
                            f"👍 **Beğeni Sayısı:** {p.get('likes', 0)}\n"
                            f"🛡️ **Birlik:** {p.get('guild_name', 'Bir birliğe üye değil')}"
                        )
                    else:
                        reply = "❌ Oyuncu bulunamadı. UID veya bölgeyi kontrol edin."
                except Exception as e:
                    reply = f"⚠️ Oyun API Hatası: {str(e)}"

            await send_telegram_message(chat_id, reply)

    except Exception as e:
        print(f"Hata: {str(e)}")

    return JSONResponse(status_code=200, content={"status": "ok"})
