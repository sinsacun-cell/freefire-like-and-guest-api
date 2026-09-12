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
                    await send_msg(chat_id, "👋 Bot aktif ve hazır!\nKullanım: `/bilgi 1875588196 sg`")
                    return JSONResponse(status_code=200, content={"status": "ok"})

                if text.startswith("/bilgi") or text.startswith("/info"):
                    parts = text.split()
                    if len(parts) < 2:
                        await send_msg(chat_id, "⚠️ Lütfen bir UID girin.\nÖrnek: `/bilgi 1875588196 sg`")
                        return JSONResponse(status_code=200, content={"status": "ok"})

                    uid = parts[1]
                    region = parts[2].lower() if len(parts) > 2 else "sg"

                    # Dış Free Fire API Sorgusu
                    api_url = f"https://free-fire-api-five.vercel.app/api/player?uid={uid}&region={region}"

                    async with httpx.AsyncClient() as client:
                        try:
                            res = await client.get(api_url, timeout=8.0)
                            if res.status_code == 200:
                                p = res.json()
                                account = p.get("AccountInfo", p.get("basicInfo", p))
                                name = account.get("AccountName") or account.get("nickname") or account.get("name") or "Bilinmiyor"
                                level = account.get("AccountLevel") or account.get("level") or "—"
                                likes = account.get("AccountLikes") or account.get("likes") or account.get("liked") or 0

                                reply = (
                                    f"🎮 **Free Fire Oyuncu Bilgisi**\n\n"
                                    f"👤 **Hesap Adı:** `{name}`\n"
                                    f"⭐ **Seviye:** {level}\n"
                                    f"🌍 **Bölge:** {region.upper()}\n"
                                    f"👍 **Beğeni Sayısı:** {likes}"
                                )
                            else:
                                reply = f"⚠️ Dış API Yanıtı: HTTP {res.status_code}"
                        except Exception as err:
                            reply = f"⚠️ Bağlantı Hatası: {str(err)}"

                    await send_msg(chat_id, reply)

        except Exception as e:
            print(f"Hata: {e}")

        return JSONResponse(status_code=200, content={"status": "ok"})

    return {"status": "online", "message": "Bot is active"}
