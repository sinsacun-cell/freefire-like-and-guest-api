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

                    # Farklı aktif gateway sorgu adresleri
                    urls = [
                        f"https://freefireapi.com.br/api/search_id?id={uid}&region={region}",
                        f"https://ff-api-like.vercel.app/info?uid={uid}&region={region}",
                        f"https://free-fire-api-five.vercel.app/api/player?uid={uid}&region={region}"
                    ]

                    p = None
                    err_msg = ""

                    async with httpx.AsyncClient(follow_redirects=True) as client:
                        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
                        for url in urls:
                            try:
                                res = await client.get(url, timeout=5.0, headers=headers)
                                if res.status_code == 200:
                                    data_json = res.json()
                                    if isinstance(data_json, dict) and len(data_json) > 0:
                                        p = data_json
                                        break
                                else:
                                    err_msg = f"HTTP {res.status_code}"
                            except Exception as ex:
                                err_msg = str(ex)

                    if p:
                        account = p.get("basicInfo") or p.get("AccountInfo") or p
                        name = account.get("nickname") or account.get("AccountName") or account.get("name") or "Bilinmiyor"
                        level = account.get("level") or account.get("AccountLevel") or "—"
                        likes = account.get("liked") or account.get("AccountLikes") or account.get("likes") or 0

                        reply = (
                            f"🎮 **Free Fire Oyuncu Bilgisi**\n\n"
                            f"👤 **Hesap Adı:** `{name}`\n"
                            f"⭐ **Seviye:** {level}\n"
                            f"🌍 **Bölge:** {region.upper()}\n"
                            f"👍 **Beğeni Sayısı:** {likes}"
                        )
                    else:
                        reply = f"❌ Oyuncu bilgisi çekilemedi ({err_msg}).\nUID: `{uid}` - Bölge: `{region.upper()}`"

                    await send_msg(chat_id, reply)

        except Exception as e:
            print(f"Hata: {e}")

        return JSONResponse(status_code=200, content={"status": "ok"})

    return {"status": "online", "message": "Bot is active"}
