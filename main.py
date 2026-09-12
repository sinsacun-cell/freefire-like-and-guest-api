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
                    await send_msg(chat_id, "👋 Bot aktif!\nKullanım: `/bilgi 1875588196 sg`")
                    return JSONResponse(status_code=200, content={"status": "ok"})

                if text.startswith("/bilgi") or text.startswith("/info"):
                    parts = text.split()
                    if len(parts) < 2:
                        await send_msg(chat_id, "⚠️ Lütfen bir UID girin.\nÖrnek: `/bilgi 1875588196 sg`")
                        return JSONResponse(status_code=200, content={"status": "ok"})

                    uid = parts[1]
                    region = parts[2].lower() if len(parts) > 2 else "sg"

                    # Garena sunucu uç noktası (JSON formatlı sorgu gateway)
                    url = f"https://region-api.freefiremobile.com/api/get_player_info?uid={uid}&region={region}"

                    async with httpx.AsyncClient(follow_redirects=True) as client:
                        headers = {
                            "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 11; Redmi Note 13 Pro Build/RP1A.200720.011)"
                        }
                        try:
                            res = await client.get(url, timeout=8.0, headers=headers)
                            if res.status_code == 200:
                                p = res.json()
                                name = p.get("nickname") or p.get("Name") or p.get("AccountName") or "Bilinmiyor"
                                level = p.get("level") or p.get("Level") or "—"
                                likes = p.get("likes") or p.get("Likes") or 0

                                reply = (
                                    f"🎮 **Free Fire Oyuncu Bilgisi**\n\n"
                                    f"👤 **Hesap Adı:** `{name}`\n"
                                    f"⭐ **Seviye:** {level}\n"
                                    f"🌍 **Bölge:** {region.upper()}\n"
                                    f"👍 **Beğeni Sayısı:** {likes}"
                                )
                            else:
                                reply = (
                                    f"⚠️ **Servis Bakımda (HTTP {res.status_code})**\n\n"
                                    f"Kamuya açık Free Fire API servisleri şu an kapalı olduğu için veriler çekilemiyor.\n"
                                    f"Aranan UID: `{uid}` - Bölge: `{region.upper()}`"
                                )
                        except Exception as e:
                            reply = f"⚠️ Bağlantı Zaman Aşımı: Dış API sunucuları yanıt vermiyor."

                    await send_msg(chat_id, reply)

        except Exception as e:
            print(f"Hata: {e}")

        return JSONResponse(status_code=200, content={"status": "ok"})

    return {"status": "online", "message": "Bot is active"}
