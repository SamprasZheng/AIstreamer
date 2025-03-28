from twitchio.ext import commands
import asyncio
import os
import edge_tts
import uuid
from dotenv import load_dotenv
from openai import OpenAI
from pydub import AudioSegment
import winsound

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
TWITCH_TOKEN = os.getenv("TWITCH_TOKEN")
CHANNEL_NAME = os.getenv("CHANNEL_NAME")



client = OpenAI(api_key=OPENAI_API_KEY)



async def speak(text):
    uid = uuid.uuid4().hex
    mp3_file = f"response_{uid}.mp3"
    wav_file = f"response_{uid}.wav"

    # 用 edge-tts 產生 mp3
    communicate = edge_tts.Communicate(text, voice="zh-CN-YunxiNeural")
    await communicate.save(mp3_file)

    # 轉成 wav
    audio = AudioSegment.from_mp3(mp3_file)
    audio.export(wav_file, format="wav")

    # 播放並等待完成
    winsound.PlaySound(wav_file, winsound.SND_FILENAME)

    # 刪除檔案
    try:
        os.remove(mp3_file)
        os.remove(wav_file)
    except Exception as e:
        print(f"刪除失敗：{e}")


def chat_response(user_msg):
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "你是波卡鯊，在充滿風險和機遇的浩瀚加密海洋中，以穩重且幽默的風格回應觀眾。"},
            {"role": "user", "content": user_msg}
        ]
    )
    return response.choices[0].message.content

# 📡 Twitch Bot
class Bot(commands.Bot):

    def __init__(self):
        super().__init__(
            token=TWITCH_TOKEN,
            prefix='!',
            initial_channels=['polkasharks']
        )

    async def event_ready(self):
        print(f'✅ 已登入：{self.nick}')

    async def event_message(self, message):
        if message.echo:
            return

        user = message.author.name
        content = message.content
        print(f"{user}: {content}")

        reply = chat_response(content)
        print(f"polkasharks: {reply}")

        await speak(reply)  # 播放語音

bot = Bot()
bot.run()
