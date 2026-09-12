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

                    # Farklı API uç noktaları
                    api_urls = [
                        f"https://free-fire-api-five.vercel.app/api/player?uid={uid}&region={region}",
                        f"https://ff-api.vercel.app/info?uid={uid}&region={region}",
                        f"https://api.garenafreefire.org/info?uid={uid}&region={region}"
                    ]

                    p = None
                    status_details = []

                    async with httpx.AsyncClient() as client:
                        for url in api_urls:
                            try:
                                res = await client.get(url, timeout=6.0)
                                if res.status_code == 200:
                                    res_data = res.json()
                                    if isinstance(res_data, dict) and len(res_data) > 0:
                                        p = res_data
                                        break
                                else:
                                    status_details.append(f"{res.status_code}")
                            except Exception as err:
                                status_details.append("Timeout/Hata")

                    if p:
                        account = p.get("AccountInfo", p.get("basicInfo", p))
                        name = account.get("AccountName") or account.get("nickname") or account.get("name") or "Bulunamadı"
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
                        reply = f"❌ Dış API'ler yanıt vermiyor ({', '.join(status_details)}).\nUID: `{uid}` - Bölge: `{region.upper()}`\n\n💡 *Bölge kodunu (me, eu, sg, ind) değiştirmeyi deneyebilirsin.*"

                    await send_msg(chat_id, reply)

        except Exception as e:
            print(f"Hata: {e}")

        return JSONResponse(status_code=200, content={"status": "ok"})

    return {"status": "online", "message": "Bot is active"}
