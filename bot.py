import urllib.request
import urllib.parse
import json
import time
import os

TOKEN = '8638299750:AAEz2B0sw1tvsNVfIqX4qaqD23y89J-Zyi8'
BASE_URL = f"https://api.telegram.org/bot{TOKEN}/"

def get_updates(offset=None):
    url = BASE_URL + "getUpdates?timeout=30"
    if offset:
        url += f"&offset={offset}"
    try:
        req = urllib.request.urlopen(url, timeout=90)
        return json.loads(req.read().decode('utf-8'))
    except Exception:
        return None

def send_message(chat_id, text):
    url = BASE_URL + "sendMessage"
    params = urllib.parse.urlencode({'chat_id': chat_id, 'text': text}).encode('utf-8')
    try:
        urllib.request.urlopen(url, data=params, timeout=90)
    except Exception as e:
        print("کێشە ل فرێکرنا پەیامێ:", e)

def download_and_send_video(chat_id, video_url):
    filename = "temp_tiktok.mp4"
    try:
        # ١. دابەزاندنا ڤیدیۆیێ بۆ سەر مۆبایلێ
        req = urllib.request.Request(video_url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=90) as response, open(filename, 'wb') as out_file:
            out_file.write(response.read())

        # ٢. فرێکرنا ڤیدیۆیێ وەک فایلی بۆ تێلیگرامێ
        boundary = '----WebKitFormBoundary7MA4YWxkTrZu0gW'
        body = []

        # chat_id
        body.append(f'--{boundary}\r\nContent-Disposition: form-data; name="chat_id"\r\n\r\n{chat_id}'.encode('utf-8'))
        # caption
        body.append(f'--{boundary}\r\nContent-Disposition: form-data; name="caption"\r\n\r\nفەرموو ئەڤە ڤیدیۆیا تە ب بێ لۆگۆ ✨'.encode('utf-8'))
        
        # video file
        with open(filename, 'rb') as f:
            file_content = f.read()
            body.append(f'--{boundary}\r\nContent-Disposition: form-data; name="video"; filename="video.mp4"\r\nContent-Type: video/mp4\r\n\r\n'.encode('utf-8') + file_content)

        body.append(f'--{boundary}--\r\n'.encode('utf-8'))
        payload = b'\r\n'.join(body)

        request = urllib.request.Request(
            BASE_URL + "sendVideo",
            data=payload,
            headers={'Content-Type': f'multipart/form-data; boundary={boundary}'},
            method='POST'
        )

        urllib.request.urlopen(request, timeout=90)
        print("ڤیدیۆ ب سەرکەفتنی هاتە فرێکرن! 🎉")

    except Exception as e:
        print("کێشە ل داگرتن/فرێکرنێ:", e)
        send_message(chat_id, "❌ ئاریشەک چێبوو ل فرێکرنا ڤیدیۆیێ.")

    finally:
        # پاکژکرنا فایلی ژ سەر مۆبایلێ
        if os.path.exists(filename):
            os.remove(filename)

def get_tiktok_no_watermark(tiktok_url):
    api_url = f"https://www.tikwm.com/api/?url={urllib.parse.quote(tiktok_url)}"
    try:
        req = urllib.request.Request(api_url, headers={'User-Agent': 'Mozilla/5.0'})
        res = urllib.request.urlopen(req, timeout=90)
        data = json.loads(res.read().decode('utf-8'))
        
        if data.get("code") == 0:
            return "https://www.tikwm.com" + data["data"]["play"]
        else:
            return None
    except Exception as e:
        print("کێشە ل وەرگرتنا لینکێ:", e)
        return None

print("🚀 بۆتێ دابەزاندنا تیک تۆکێ (ب فرێکرنا دروست) یێ ئۆنلاینە...")
last_update_id = None

while True:
    updates = get_updates(last_update_id)
    if updates and updates.get("ok"):
        for update in updates.get("result", []):
            last_update_id = update["update_id"] + 1
            if "message" in update and "text" in update["message"]:
                chat_id = update["message"]["chat"]["id"]
                user_text = update["message"]["text"].strip()
                
                if user_text == "/start":
                    send_message(chat_id, "بخێر بێی! لینکێ ڤیدیۆیا تیک تۆکێ بهنێرە دا ب بێ لۆگۆ بۆ تە بەردەست بکەم 📥")
                elif "tiktok.com" in user_text:
                    send_message(chat_id, "⏳ ل چاڤەڕێیێ ببه... ڤیدیۆ یا دهێتە ئامادەکرن...")
                    
                    video_url = get_tiktok_no_watermark(user_text)
                    if video_url:
                        download_and_send_video(chat_id, video_url)
                    else:
                        send_message(chat_id, "❌ نەشیا ڤیدیۆیێ بهنێریت. لینکێ خۆ ڕاست بکە.")
                else:
                    send_message(chat_id, "هیڤیە لینکەکێ دروست یێ تیک تۆکێ (tiktok.com) بهنێرە.")
                    
    time.sleep(1)
