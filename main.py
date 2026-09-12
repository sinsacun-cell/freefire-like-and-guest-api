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
                    await send_msg(chat_id, "👋 Bot aktif! Kullanım: `/bilgi 1875588196 sg`")
                    return JSONResponse(status_code=200, content={"status": "ok"})

                if text.startswith("/bilgi") or text.startswith("/info"):
                    parts = text.split()
                    if len(parts) < 2:
                        await send_msg(chat_id, "⚠️ Lütfen bir UID girin.\nÖrnek: `/bilgi 1875588196 sg`")
                        return JSONResponse(status_code=200, content={"status": "ok"})

                    uid = parts[1]
                    region = parts[2].lower() if len(parts) > 2 else "sg"

                    # Farklı aktif Free Fire API servislerini sırayla dene
                    api_urls = [
                        f"https://region-info.vercel.app/api/player?uid={uid}&region={region}",
                        f"https://free-fire-info-api.vercel.app/api/info?uid={uid}&region={region}",
                        f"https://ff-info-api.vercel.app/info?uid={uid}&region={region}"
                    ]

                    p = None
                    async with httpx.AsyncClient() as client:
                        for url in api_urls:
                            try:
                                res = await client.get(url, timeout=6.0)
                                if res.status_code == 200:
                                    p = res.json()
                                    break
                            except Exception:
                                continue

                    if p:
                        # API yanıt yapısına göre esnek veri çekme
                        name = p.get('nickname') or p.get('AccountName') or p.get('name') or p.get('basicInfo', {}).get('nickname', 'Bilinmiyor')
                        reg = p.get('region') or p.get('AccountRegion') or region.upper()
                        likes = p.get('likes') or p.get('Likes') or p.get('basicInfo', {}).get('liked', 0)
                        level = p.get('level') or p.get('Level') or p.get('basicInfo', {}).get('level', '—')

                        reply = (
                            f"🎮 **Free Fire Oyuncu Bilgisi**\n\n"
                            f"👤 **Hesap Adı:** `{name}`\n"
                            f"⭐ **Seviye:** {level}\n"
                            f"🌍 **Bölge:** {reg}\n"
                            f"👍 **Beğeni Sayısı:** {likes}"
                        )
                    else:
                        reply = "❌ Oyuncu bilgisi çekilemedi. UID veya Bölgeyi kontrol edin (Örn: sg, eu, ind)."

                    await send_msg(chat_id, reply)

        except Exception as e:
            print(f"Hata: {e}")

        return JSONResponse(status_code=200, content={"status": "ok"})

    return {"status": "online", "message": "Bot is running"}
