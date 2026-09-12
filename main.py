import httpx
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

app = FastAPI()

TELEGRAM_BOT_TOKEN = "8909841952:AAEaInTW2VGYirq2TN1qslFQBJw7XjKq7b8"

async def send_msg(chat_id: int, text: str):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    async with httpx.AsyncClient() as client:
        await client.post(url, json={"chat_id": chat_id, "text": text, "parse_mode": "Markdown"})

@app.get("/")
@app.post("/")
async def handle_root(request: Request):
    if request.method == "POST":
        try:
            data = await request.json()
            message = data.get("message", {})
            text = message.get("text", "")
            chat_id = message.get("chat", {}).get("id")

            if chat_id and text:
                if text.startswith("/start"):
                    await send_msg(chat_id, "👋 Bot aktif! `/bilgi 1875588196 eu` şeklinde kullanabilirsin.")
                    return JSONResponse(status_code=200, content={"status": "ok"})

                if text.startswith("/bilgi") or text.startswith("/info"):
                    parts = text.split()
                    if len(parts) < 2:
                        await send_msg(chat_id, "⚠️ Lütfen bir UID girin.\nÖrnek: `/bilgi 1875588196 eu`")
                        return JSONResponse(status_code=200, content={"status": "ok"})

                    uid = parts[1]
                    region = parts[2].lower() if len(parts) > 2 else "eu"

                    # Dış API sorgusu
                    api_url = f"https://free-fire-api-five.vercel.app/api/player?uid={uid}&region={region}"
                    
                    async with httpx.AsyncClient() as client:
                        try:
                            res = await client.get(api_url, timeout=10.0)
                            if res.status_code == 200:
                                p = res.json()
                                reply = (
                                    f"🎮 **Free Fire Oyuncu Bilgisi**\n\n"
                                    f"👤 **Hesap Adı:** {p.get('nickname', 'Bilinmiyor')}\n"
                                    f"🌍 **Bölge:** {p.get('region', region.upper())}\n"
                                    f"📅 **Kuruluş:** {p.get('account_created', 'Bilinmiyor')}\n"
                                    f"⏰ **Son Giriş:** {p.get('last_login', 'Bilinmiyor')}\n"
                                    f"👍 **Beğeni:** {p.get('likes', 0)}\n"
                                    f"🛡️ **Birlik:** {p.get('guild_name', 'Bir birliğe üye değil')}"
                                )
                            else:
                                reply = f"❌ Oyuncu bulunamadı (Kod: {res.status_code})."
                        except Exception as err:
                            reply = f"⚠️ API Bağlantı Hatası: {str(err)}"

                    await send_msg(chat_id, reply)

        except Exception as e:
            # En azından ne hata aldığımızı bot kendisi Telegram'a yazsın
            print(f"Hata: {e}")

        return JSONResponse(status_code=200, content={"status": "ok"})

    return {"status": "online", "message": "Bot is running"}
