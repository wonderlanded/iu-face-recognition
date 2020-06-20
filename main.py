import os
from os.path import isfile, join
import datetime
import re
import random

import discord
from discord.ext import commands
import face_recognition

# import progressbar
import logging, sys

import config
log_format = logging.Formatter('[%(asctime)s] [%(filename)s] [%(name)s:%(module)s] [%(levelname)s]: %(message)s')
log_level = logging.INFO
stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setFormatter(log_format)

log = logging.getLogger("discord")
log.setLevel(log_level)
log.addHandler(stream_handler)

log = logging.getLogger("wonder")
log.setLevel(logging.DEBUG)
log.addHandler(stream_handler)



startTime = datetime.datetime.now()

sampleFiles = ['./sample/' + f for f in os.listdir('./sample') if isfile(join('./sample', f))]

import config

bot = commands.Bot(command_prefix=config.prefix)
def loadImage(path, index):
    image = face_recognition.load_image_file(path)
    res = face_recognition.face_encodings(image)
    # bar.update(index)
    print(f'[{index}/{len(filtered)}] {path}')
    return res[0] if res else None

def filterNone(a):
    if a != None: return True
    else: return False

def isIU(a):
    if a > 0.6: return True
    else: return False

# bar = progressbar.ProgressBar(max_value=len(sampleFiles))

if len(sampleFiles) < (config.limit if config.limit else len(sampleFiles)):
    print('올바르지 않은 리밋입니다. (`config.limit`)')
    exit(0)
filtered = random.sample(sampleFiles, k=config.limit if config.limit else len(sampleFiles))
encoded = [ loadImage(el, filtered.index(el)+1) for el in filtered]
faces = [ el for el in encoded if el is not None]

endTime = datetime.datetime.now()
print(faces)
if len(faces)/len(filtered) < 0.5: 
    print(f'\n{"="*70}\n인식된 이미지의 수가 너무 적습니다. ({len(faces)/len(filtered)*100}%)')
    exit(0)
else: print(f'\n{"="*70}\nSuccessfully loaded {len(faces)} file(s) of {len(filtered)}. ({len(faces)/len(filtered)*100}% 인식되었습니다.)')

print(endTime - startTime)

@bot.event
async def on_ready():
    print(f'Client Ready')

@bot.event
async def on_message(message):
    await bot.process_commands(message)
    if message.author == bot.user or message.content.startswith(config.prefix): return
        
    if len(message.attachments) > 0 and re.compile(r'[\w-]+.(jpg|png|jpeg)').search(message.attachments[0].filename):
        fp = './images/{0.id}-{0.filename}'.format(message.attachments[0])
        print(fp)
        await message.attachments[0].save(fp, use_cached=True)

        image = face_recognition.load_image_file(fp)
        image_encoded = face_recognition.face_encodings(image)

        if not image_encoded: return os.remove(fp)
        res = [ 1-r for r in face_recognition.face_distance(faces, image_encoded[0]) ]
        print(f'{message.author.id} {len(list(filter(isIU, res)))}')
        if len(list(filter(isIU, res))) > round(len(faces) * 0.3) or 1 in res: await message.add_reaction('❤️')
        os.remove(fp)
@bot.command()
async def match(ctx):
    if(not ctx.message.attachments): return
    else:
        if len(ctx.message.attachments) > 0 and re.compile(r'[\w-]+.(jpg|png|jpeg)').search(ctx.message.attachments[0].filename):
            fp = './images/{0.id}-{0.filename}'.format(ctx.message.attachments[0])
            await ctx.message.attachments[0].save(fp, use_cached=True)

            image = face_recognition.load_image_file(fp)
            image_encoded = face_recognition.face_encodings(image)
            if not image_encoded:
                await ctx.send('얼굴을 감지할 수 없습니다.')
                return os.remove(fp)
            res = [ 1-r for r in face_recognition.face_distance(faces, image_encoded[0]) ]
            if(1 in res): await ctx.send('하나 이상의 데이터에 100% 일치합니다.')
            else: await ctx.send(f'학습데이터 {len(faces)}건중 {len(list(filter(isIU, res)))}건에 해당합니다.')
            os.remove(fp)
@bot.command()
async def test(ctx, arg):
    await ctx.send(arg)


bot.run(config.token)