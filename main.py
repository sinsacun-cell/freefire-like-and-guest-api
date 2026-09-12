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

                    # Dış kaynak API'leri (güncel ve aktif gateway'ler)
                    api_urls = [
                        f"https://freefireapi.com.br/api/search_id?id={uid}&region={region}",
                        f"https://api.garenafreefire.org/info?uid={uid}&region={region}"
                    ]

                    p = None
                    last_err = ""

                    async with httpx.AsyncClient(follow_redirects=True) as client:
                        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
                        for url in api_urls:
                            try:
                                res = await client.get(url, timeout=6.0, headers=headers)
                                if res.status_code == 200:
                                    res_data = res.json()
                                    if isinstance(res_data, dict) and len(res_data) > 0:
                                        p = res_data
                                        break
                                else:
                                    last_err = f"HTTP {res.status_code}"
                            except Exception as err:
                                last_err = "Bağlantı Zaman Aşımı"

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
                        reply = (
                            f"❌ **API Sunucu Hatası ({last_err})**\n\n"
                            f"Ücretsiz sorgu sunucuları şu an bakımdadır.\n"
                            f"UID: `{uid}` - Bölge: `{region.upper()}`"
                        )

                    await send_msg(chat_id, reply)

        except Exception as e:
            print(f"Hata: {e}")

        return JSONResponse(status_code=200, content={"status": "ok"})

    return {"status": "online", "message": "Bot is active"}
