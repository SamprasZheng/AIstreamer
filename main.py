from twitchio.ext import commands
import asyncio
import os
import edge_tts
import uuid
from dotenv import load_dotenv
from openai import OpenAI
from pydub import AudioSegment
import winsound
import json
import random
import sys

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
TWITCH_TOKEN = os.getenv("TWITCH_TOKEN")

with open("D:/AItwitch/keywords.json", "r", encoding="utf-8") as f:
    KEYWORD_REPLIES = json.load(f)


client = OpenAI(api_key=OPENAI_API_KEY)

# KEYWORD_REPLIES = {
#     "nft": "NFT 只是數位收藏？才不止如此呢～",
#     "比特幣": "比特幣，還是鏈上海洋中的旗艦級存在啊。",
#     "bitcoin": "比特幣，還是鏈上海洋中的旗艦級存在啊。",
#     "以太坊": "以太坊就像是這片海中的魔法發動器！",
#     "ethereum": "以太坊就像是這片海中的魔法發動器！",
#     "帥": "哼，我當然是最帥的加密鯊啦～",
#     "gm": "gm gm，早安啊冒險者 🐬"
# }

async def check_keywords_and_reply(message):
    content = message.content.lower()

    for keyword, replies in KEYWORD_REPLIES.items():
        if keyword in content:
            reply = random.choice(replies)
            await message.channel.send(reply) 
            await speak(reply)                
            return True
    return False




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

@commands.command(name="指令")
async def show_keywords(self, ctx):
    keyword_list = list(KEYWORD_REPLIES.keys())
    # 可選排序
    keyword_list.sort()
    keywords_str = "可用關鍵字：「" + "、".join(keyword_list) + "」"
    await ctx.send(keywords_str)



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
        
        await self.handle_commands(message)

        user = message.author.name
        content = message.content
        print(f"{user}: {content}")

        hit = await check_keywords_and_reply(message)
        if hit:
            return  # 命中關鍵字就不用再呼叫 GPT

        # GPT 回應流程
        reply = chat_response(content)
        print(f"polkasharks: {reply}")
        await message.channel.send(reply)
        await speak(reply)


bot = Bot()
bot.run()
