import requests
import hashlib
import psutil
import os
import time
import nextcord 
import random
import imdb
import emoji
import youtube_dl
import instagramy
from instagramy import *
from instascrape import *
import urllib.parse
import urllib
import aiohttp
import traceback
import aiofiles
import assets
import random
import json
import re as regex

from io import BytesIO
from nextcord import SlashOption
from dotenv import load_dotenv
from functools import lru_cache
from datetime import datetime
from collections import Counter
from requests.models import PreparedRequest
from requests.exceptions import MissingSchema
from typing import List, Union

ydl_op = {
    "format": "bestaudio/best",
    "postprocessors": [
        {
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "384",
        }
    ],
}
SVG2PNG_API_URI = os.getenv("svg2pnguri")
SVG2PNG_API_TOKEN = os.getenv("svg2pngtoken")

m_options = [
    'title',
    'description',
    'color',
    'footer',
    'thumbnail',
    'image',
    'author',
    'url',
    'fields'
]

Emoji_alphabets = [chr(i) for i in range(127462,127488)]
FORCED_ACTIVITY = None

load_dotenv()

def activities(client):
    if FORCED_ACTIVITY:
        return nextcord.Activity(type=nextcord.ActivityType.watching, name=FORCED_ACTIVITY)
    all_activities = [
        nextcord.Activity(type=nextcord.ActivityType.watching, name="Dark Knight Rises"),
        nextcord.Activity(type=nextcord.ActivityType.listening, name="Something in the way"),
        nextcord.Activity(type=nextcord.ActivityType.listening, name=f"{len(client.guilds)} servers"),
        nextcord.Activity(type=nextcord.ActivityType.watching, name="Nextcord People do their magic"),
        nextcord.Activity(type=nextcord.ActivityType.listening, name="Wayne Enterprises"),
        nextcord.Activity(type=nextcord.ActivityType.watching, name="Raimi Trilogy with Thwipper"),
        nextcord.Activity(type=nextcord.ActivityType.watching, name="New Updates")
    ]
    return random.choice(all_activities)
    
@lru_cache(maxsize = 512)
def youtube_info(url):
    with youtube_dl.YoutubeDL(ydl_op) as ydl:
        info = ydl.extract_info(url, download=False)
    return info

def timestamp(i):
    return datetime.fromtimestamp(i)

def convert_to_url(name):
    name = urllib.parse.quote(name)
    return name


def quad(eq):
    if "x^2" not in eq:
        return "x^2 not found, try again"
    print(eq)
    eq = eq.replace("2+", "2 + ")
    eq = eq.replace("2-", "2 - ")
    eq = eq.replace("x+", "x + ")
    eq = eq.replace("x-", "x - ")

    # try to get correct equation
    parts = [x.strip() for x in eq.split(" ")]
    a, b, c = 0, 0, 0
    for i in parts:
        if i == " ":
            parts.remove(" ")

    for index, part in enumerate(parts):
        if part in ["+", "-"]:
            continue

        symbol = -1 if index - 1 >= 0 and parts[index - 1] == "-" else 1

        if part.endswith("x^2"):
            coeff = part[:-3]
            a = float(coeff) if coeff != "" else 1
            a *= symbol
        elif part.endswith("x"):
            coeff = part[:-1]
            b = float(coeff) if coeff != "" else 1
            b *= symbol
        elif part.isdigit():
            c = symbol * float(part)

    determinant = b ** 2 - (4 * a * c)

    if determinant < 0:
        return "Not Real"
    if determinant == 0:
        root = -b / (2 * a)
        return "Equation has one root:" + str(root)

    if determinant > 0:
        determinant = determinant ** 0.5
        root1 = (-b + determinant) / (2 * a)
        root2 = (-b - determinant) / (2 * a)
        return "This equation has two roots: " + str(root1) + "," + str(root2)


def get_sessionid(username, password):
    url = "https://i.instagram.com/api/v1/accounts/login/"

    def generate_device_id(username, password):
        m = hashlib.md5()
        m.update(username.encode() + password.encode())

        seed = m.hexdigest()
        volatile_seed = "12345"

        m = hashlib.md5()
        m.update(seed.encode("utf-8") + volatile_seed.encode("utf-8"))
        return "android-" + m.hexdigest()[:16]

    device_id = generate_device_id(username, password)

    payload = {
        "username": username,
        "device_id": device_id,
        "password": password,
    }

    headers = {
        "Accept": "*/*",
        "Content-type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Accept-Language": "en-US",
        "referer": "https://www.instagram.com/accounts/login/",
        "User-Agent": "Instagram 10.26.0 Android",
    }

    response = requests.post(url, headers=headers, data=payload)
    if response.status_code == 200:
        return response.cookies.get_dict()["sessionid"]

    return response.text

async def wolf_spoken(wolfram, question):
    question = convert_to_url(question)
    url = f"http://api.wolframalpha.com/v1/spoken?appid={wolfram}&i={question}"
    return await get_async(url)

def get_it():
    username = str(os.getenv("username"))
    password = str(os.getenv("password"))
    return get_sessionid(username, password)


def instagram_get1(account, color, SESSIONID):
    try:
        user = InstagramUser(account, sessionid=SESSIONID)
        all_posts = user.posts
        list_of_posts = []
        number = 0
        for i in all_posts[0:7]:
            url = i.post_url
            pos = Post(url)
            headers = {
                "user-agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Mobile Safari/537.36 Edg/87.0.664.57",
                "cookie": "sessionid=" + SESSIONID + ";",
            }            
            pos.scrape(headers=headers)
            print(user.posts[number].comments)
            thumb = user.profile_picture_url
            embed = cembed(
                title="Instagram", color=color,
                footer=str(user.posts[number].comments) + " comments",
                image=user.posts[number].post_source,
                thumbnail=thumb
            )
            list_of_posts.append((embed, url))
            number += 1
        return list_of_posts
    except instagramy.core.exceptions.UsernameNotFound:
        return "User Not Found, please check the spelling"
    except Exception:
        print(traceback.print_exc())
        #SESSIONID = get_it()
        return SESSIONID

@lru_cache(maxsize=512)
async def get_youtube_url(url):
    """
    gets the list of url from a channel url
    """
    st = await get_async(url)
    li = regex.findall(r"watch\?v=(\S{11})", st)
    return [f"https://youtube.com/watch?v={w}" for w in li]


def get_if_process_exists(name):
    return (
        len(
            [
                i
                for i in [p.info["name"] for p in psutil.process_iter(["name"])]
                if i.find(name) != -1
            ]
        )>0
    )


def cembed(
    title=None, description=None, thumbnail=None, picture=None, url=None, color=nextcord.Color.dark_theme(), footer=None, author = False, fields = None, image = None
):
    embed = nextcord.Embed()
    if color != nextcord.Color.dark_theme():
        if type(color) == int:
            embed = nextcord.Embed(color=nextcord.Color(value=color))
        else:
            embed = nextcord.Embed(color=color)
    if title:
        embed.title = title
    if description:
        embed.description = description
    if thumbnail:
        embed.set_thumbnail(url=thumbnail)
    if picture:
        embed.set_image(url=picture)
    if image:
        embed.set_image(url=image)
    if url:
        embed.url = url
    if fields:
        for i in fields:
            embed.add_field(**i)
    if footer:
        if isinstance(footer, str):
            embed.set_footer(text=footer)
        else:
            embed.set_footer(
                text=footer.get("text", "Footer Error"),
                icon_url=footer.get("icon_url", "https://colourlex.com/wp-content/uploads/2021/02/vine-black-painted-swatch.jpg")
            )
    if author:
        if isinstance(author, str):
            embed.set_author(name=author)
        elif isinstance(author, dict):
            embed.set_author(**author)
        elif isinstance(author, nextcord.member.Member):
            embed.set_author(name=author.name, icon_url = safe_pfp(author)) 
        pass
        
    return embed
    
def imdb_embed(movie="",re={8:5160}):
    """
    Returns details about a movie as an embed in discord
    Parameters include movies
    """
    if movie == "":
        return cembed(
            title="Oops",
            description="You must enter a movie name",
            color=nextcord.Color.red(),
        )
    try:
        ia = imdb.IMDb()
        movie = ia.search_movie(movie)
        title = movie[0]["title"]
        mov = ia.get_movie(movie[0].getID())
        di = {
            'Cast' : ', '.join([str(i) for i in mov['cast']][:5]),
            'writer': ', '.join([str(j) for j in mov['writer']]),
            'Rating': ':star:'*int(mov['rating']),
            'Genres': ', '.join(mov['genres']),
            'Year' : mov['year']
        }
        di['Director']: mov.get('director')
        plot = mov['plot'][0]
        image = movie[0]["full-size cover url"]
        embed = cembed(
            title=mov['title'],
            description=plot,
            color=re[8],
            image = image
        )
        n=0
        for i in di:
            n+=1
            embed.add_field(name=i, value=di[i], inline=(n%3==0))
        return embed
    except Exception as e:
        print(traceback.format_exc())
        return cembed(
            title="Oops",
            description="Something went wrong, check if the name is correct",
            color=re[8],
        )

async def redd(ctx, account="wholesomememes", number = 25, single=True):
    a = await get_async(f"https://meme-api.herokuapp.com/gimme/{account}/{number}",kind="json")
    embeds = []
    bot = getattr(ctx, 'bot', getattr(ctx, 'client', None))
    if 'message' in a.keys():
        return [cembed(
            title="Oops",
            description=a['message'],
            color=bot.re[8]
        )]
    memes = a['memes']
    for i in memes:
        embed = cembed(
            title=i['title'],
            image=i['url'],
            url=i['postLink'],
            footer=i['author']+" | "+str(i['ups'])+" votes",
            color=bot.re[8],
            thumbnail=bot.user.avatar.url
        )
        if not ctx.channel.nsfw:
            if i['nsfw']:
                continue
        embeds.append(embed)
    if embeds == []:
        embed = cembed(
            title="Something seems wrong",
            description="There are no posts in this accounts, or it may be `NSFW`",
            color = bot.re[8]
        )
        embeds.append(embed)
    return embeds
        

def protect(text):
    return (
        str(text).find("username") == -1
        and str(text).find("os.") == -1
        and str(text).find("ctx.") == -1
        and str(text).find("__import__") == -1
        and str(text).find("sys.") == -1
        and str(text).find("psutil.") == -1
        and str(text).find("clear") == -1
        and str(text).find("dev_users") == -1
        and str(text).find("remove") == -1
        and str(text).find("class.") == -1
        and str(text).find("subclass()") == -1
        and str(text).find("client") == -1
        and str(text).find("quit") == -1
        and str(text).find("exit") == -1
        and str(text).find("while True") == -1
    )


async def devop_mtext(client, channel, color):
    await channel.delete_messages(
        [i async for i in channel.history(limit=100) if not i.pinned][:100]
    )
    text_dev = (
        "You get to activate and reset certain functions in this channel \n"
        "💾 for saving to file \n"
        "⭕ for list of all servers \n"
        "❌ for exiting \n"
        "🔥 for restart\n"
        "📊 for current load\n"
        "❕ for current issues\n"
        "" + emoji.emojize(":satellite:") + " for speedtest\n"
        "" + emoji.emojize(":black_circle:") + " for clear screen\n"
    )
    embed = cembed(
        title="DEVOP", description=text_dev, color=color,footer="Good day Master Wayne"
    )
    embed.set_thumbnail(url=client.user.avatar.url)
    mess = await channel.send(embed=embed)
    await mess.add_reaction("💾")
    await mess.add_reaction("⭕")
    await mess.add_reaction("❌")
    await mess.add_reaction(emoji.emojize(":fire:"))
    await mess.add_reaction(emoji.emojize(":bar_chart:"))
    await mess.add_reaction("❕")
    await mess.add_reaction(emoji.emojize(":satellite:"))
    await mess.add_reaction(emoji.emojize(":black_circle:"))
    await mess.add_reaction(emoji.emojize(":laptop:"))


async def wait_for_confirm(ctx, client, message, color=61620,usr=None):
    mess = await ctx.channel.send(
        embed=nextcord.Embed(
            title="Confirmation", description=message, color=nextcord.Color(color)
        )
    )
    await mess.add_reaction(emoji.emojize(":check_mark_button:"))
    await mess.add_reaction(emoji.emojize(":cross_mark_button:"))

    person=usr

    def check(reaction, user):
        a = user == getattr(ctx, 'author', getattr(ctx,'user',None)) if person is None else person == user
        return (
            reaction.message.id == mess.id
            and reaction.emoji
            in [emoji.emojize(":check_mark_button:"), emoji.emojize(":cross_mark_button:")]
            and a
        )

    reaction, user = await client.wait_for("reaction_add", check=check)
    if reaction.emoji == emoji.emojize(":check_mark_button:"):
        await mess.delete()
        return True
    if reaction.emoji == emoji.emojize(":cross_mark_button:"):
        await mess.delete()
        await ctx.channel.send(
            embed=nextcord.Embed(
                title="Ok cool", description="Aborted", color=nextcord.Color(color)
            )
        )
        return False


def equalise(all_strings):
    maximum = max(list(map(len, all_strings)))
    a = {}
    _ = [a.update({i: i + " " * (maximum - len(i))}) for i in all_strings]
    return a

def reset_emo(client):
    emo = assets.Emotes(client)
    return emo
    
def youtube_download(url):
    with youtube_dl.YoutubeDL(ydl_op) as ydl:
        info=ydl.extract_info(url, download=False) 
        URL = info["formats"][0]["url"]
    return URL

def youtube_download1(url):
    with youtube_dl.YoutubeDL(ydl_op) as ydl:
        info=ydl.extract_info(url, download=False)
        name=info['title']
        URL = info["formats"][0]["url"]
    return (URL, name)

def subtract_list(l1, l2):
    a = []
    for i in l1:
        if i not in l2:
            a.append(i)
    return a

def extract_color(color):
    try:
        color_temp = (
            int("0x" + str(hex(color))[2:4], 16),
            int("0x" + str(hex(color))[4:6], 16),
            int("0x" + str(hex(color))[6:8], 16),
        )
        return color_temp
    except:
        pass


def svg2png(url: str):
    """Convert SVG image (url) to PNG format."""
    # print(SVG2PNG_API_URI, SVG2PNG_API_TOKEN)
    res = requests.get(
        SVG2PNG_API_URI, params=[("url", url), ("token", SVG2PNG_API_TOKEN)]
    )
    return res.content



async def get_name(url):
    '''
    get Youtube Video Name through Async
    '''
    a = await get_async(url)
    return (
        a[a.find("<title>") + len("<title>") : a.find("</title>")]
        .replace("&amp;", "&")
        .replace(" - YouTube", "")
        .replace("&#39;", "'")
    )

async def get_async(url, headers = {}, kind = "content"):
    '''
    Simple Async get request
    '''
    output = ""
    async with aiohttp.ClientSession(headers=headers) as session:
        async with session.get(url) as resp:
            if kind == "json":                
                try:
                    output = await resp.json()
                except Exception as e:
                    print(e)
                    output = await resp.text()
            elif kind.startswith("file>"):
                f = await aiofiles.open(kind[5:], mode = "wb")
                await f.write(await resp.read())
                await f.close()
                return
            elif kind == "fp":
                output = BytesIO(await resp.read())
            else:
                output = await resp.text()
                
        await session.close()
    return output
    
async def post_async(api, header = {}, json = {}, output = "content"):
    async with aiohttp.ClientSession() as session:
        async with session.post(api, headers=header, json=json) as resp:
            if resp.headers['Content-Type'] != 'application/json':
                return await resp.read()
            return await resp.json()
            
def suicide_m(client,color):
    return cembed(
        title="Suicide and Self harm prevention",
        description='\n'.join([i.strip() for i in """ 
    You are not alone ...
    And your Life is worth a lot ..
    SPEAK OUT !!


    If you're having any suicidal thoughts, please seek help immediately. Talk about what bothers you and what can be done to solve the problem


    international suicide helplines>>> https://www.opencounseling.com/suicide-hotlines
        """.split('\n')]),
        color=color,
        thumbnail=client.user.avatar.url,
        picture="https://www.humanium.org/en/wp-content/uploads/2019/09/shutterstock_1140282473-scaled.jpg"
    )

def check_end(s : str):
    if not s.endswith("/videos"):
        return s+"/videos"
    return s

def check_voice(ctx):
    try:
        mem = [str(names) for names in ctx.guild.voice_client.channel.members]
    except:
        mem = []
    return mem.count(str(getattr(ctx, 'author', getattr(ctx, 'user', None)))) > 0

async def player_reaction(mess):
    await mess.add_reaction("⏮")
    await mess.add_reaction("⏸")
    await mess.add_reaction("▶")
    await mess.add_reaction("🔁")
    await mess.add_reaction("⏭")
    await mess.add_reaction("⏹")
    await mess.add_reaction(emoji.emojize(":keycap_*:"))
    await mess.add_reaction(emoji.emojize(":upwards_button:"))
    await mess.add_reaction(emoji.emojize(":downwards_button:"))
    await mess.add_reaction(emoji.emojize(":musical_note:"))

def remove_all(original,s):
    for i in s:
        original.replace(i,"")
    return original

def safe_pfp(user):
    if user is None: return
    if type(user) == nextcord.guild.Guild:
        return user.icon.url if user.icon else None
    pfp = user.default_avatar.url
    if user.avatar:
        return user.avatar.url
    return pfp

def defa(*types, default = None, choices=[], required = False):
    if types == []: return SlashOption(default = default, required = False)
    if choices != []:
        return SlashOption(choices=choices, default = default, required = required)   
    return SlashOption(channel_types = types, required = required)

async def ly(song, re):
    j = await get_async(f"https://api.popcat.xyz/lyrics?song={convert_to_url(song)}",kind="json")
    return cembed(
        title=j.get('title',"Couldnt get title"),
        description=j.get('lyrics',"Unavailable"),
        color=re[8],
        thumbnail=j.get('image'),
        footer=j.get('artist',"Unavailable")
    )

async def isReaction(ctx, embed, clear = False):
    if type(ctx) == nextcord.message.Message:
        message = await ctx.edit(embed=embed)
    else:
        message = await ctx.send(embed=embed)
    if clear:
        try:
            await message.clear_reactions()
        except:
            pass

def uniq(li):
    return list(Counter(li).keys())

def timestamp(i):
    return time.ctime(i)

class SpaceX:
    def __init__(self,color):
        self.name = None
        self.time = None
        self.fno = None
        self.thumbnail = None
        self.youtube = None
        self.wikipedia = None
        self.crew = []
        self.id = None
        self.color = color
        
    async def setup(self):
        js = await get_async("https://api.spacexdata.com/v4/launches/latest", kind="json")
        self.name = js['name']
        self.time = timestamp(int(js['date_unix']))
        self.thumbnail = js['links']['patch']['large']
        self.youtube = js['links']['webcast']
        self.wikipedia = js['links']['wikipedia']
        self.crew = js['crew']
        self.id = js['id']
        self.fno = js['flight_number']

    async def history(self):
        jso = await get_async("https://api.spacexdata.com/v4/history", kind = "json")
        embeds = []
        for i in jso[::-1]:
            embed = cembed(
                title=i['title'],
                description=i['details'],
                color=self.color,
                thumbnail="https://www.spacex.com/static/images/share.jpg",
                footer = i['id'] + " | " + str(timestamp(i['event_date_unix']))
            )
            embeds.append(embed)
        print("Done")
        return embeds

class Meaning:
    def __init__(self,word,color):
        self.word = word,
        self.url = "https://api.dictionaryapi.dev/api/v2/entries/en/"+convert_to_url(word)
        self.result = None
        self.embeds = []
        self.color = color
        self.thumbnail = "https://i.pinimg.com/originals/75/7c/da/757cda6d9ac2a7f0db09c41b83931b53.png"

    async def setup(self):
        self.result = await get_async(self.url, kind="json")
        return self.result

    def create_texts(self):
        if self.result == None:
            raise IndexError("Run setup first |coro|")
        elif type(self.result) == dict:
            a = cembed(
                title=self.result['title'],
                description=self.result['message'],
                color = self.color,
                thumbnail = "https://c.tenor.com/IHdlTRsmcS4AAAAC/404.gif"
            )
            self.embeds.append(a)
        else:
            r = self.result
            description=f"**Phonetics**: {r[0].get('phonetic')}\n"
            description+=f"**Part of speech**: {r[0]['meanings'][0].get('partOfSpeech')}"
            embed=cembed(
                title=r[0]['word'],
                description=description,
                color=self.color,
                thumbnail=self.thumbnail
            )
            self.embeds.append(embed)
            definitions = r[0]['meanings'][0]['definitions']
            page = 0
            for i in definitions:
                page+=1
                des = i['definition']
                example = i.get('example')
                synonyms = i.get('synonyms')
                antonyms = i.get('antonyms')
                if example is None:
                    example = f"{page} of {len(definitions)}"
                embed = cembed(
                    title = r[0]['word'],
                    description = des,
                    color=self.color,
                    footer = example,
                    thumbnail=self.thumbnail
                )
                if synonyms and synonyms != []:
                    embed.add_field(
                        name="Synonyms",
                        value=', '.join(synonyms),
                        inline=True
                    )
                if antonyms and antonyms != []:
                    embed.add_field(
                        name="Antonyms",
                        value=','.join(antonyms),
                        inline=True
                    )
                self.embeds.append(embed)
        return self.embeds

async def animals(client, ctx, color, number = 10):
    d2 = await get_async(f"https://zoo-animal-api.herokuapp.com/animals/rand/{number}",kind="json")
    user = getattr(ctx,'author',getattr(ctx,'user',None))
    icon_url = safe_pfp(user)
    embeds = []
    for d in d2:    
        embed=cembed(
            title=d['name'],
            description=d['diet'],
            color=color,
            thumbnail=client.user.avatar.url,
            image=d['image_link'],
            footer=d['active_time']
        )
        embed.set_author(name=user.name,icon_url=icon_url)
        d1 = {
            'Latin name': d['latin_name'],
            'Animal Type': d['animal_type'],
            'Length': f"{d['length_min']} to {d['length_max']} feet",
            'Weight': f"{int(float(d['weight_min'])*0.453592)} to {int(float(d['weight_max'])*0.453592)} kg",
            'Life Span': f"{d['lifespan']} years",
            'Habitat': f"{d['habitat']}, {d['geo_range']}"
        }
        for i in d1.items():
            embed.add_field(name=i[0], value=i[1], inline=True)
    
        embeds.append(embed)
    return embeds

def audit_check(log):
    latest = log[0]
    che = log[:10]
    initiators = Counter([i.user for i in che])
    for i in initiators:
        tim = time.time()-120
        offensive = [
            nextcord.AuditLogAction.kick,
            nextcord.AuditLogAction.ban,
            nextcord.AuditLogAction.channel_delete,
        ]
        actions = [j.action for j in che if j.user == i and j.action in offensive and j.created_at.timestamp()>tim]
        if len(actions)>5:
            return i      
        
    

def check_command(ctx):
    a = ctx.bot.config['commands']
    if a.get(str(ctx.command.name)):
        if ctx.guild.id in a[ctx.command.name]:
            return False
    return True

async def quo(color):
    a = await get_async("https://api.quotable.io/random", kind="json")
    footer = ', '.join(a['tags'])
    description = a['content']
    title = a['author']
    return cembed(
        title=title,
        description=description,
        footer=footer,
        color=color
    )

co = """
import nextcord
import assets
import time
import traceback
import External_functions as ef
from nextcord.ext import commands

# Use nextcord.slash_command()

def requirements():
    return []

class <name>(commands.Cog):
    def __init__(self, client):
        self.client = client


def setup(client,**i):
    client.add_cog(<name>(client,**i))
""".strip()

def cog_creator(name: str):
    if f"{name}.py" in os.listdir("cogs/"):
        return "Already exists"

    with open(f"cogs/{name}.py", "w") as f:
        f.write(co.replace("<name>",name))

    return "Done"

class Attributor:
    def __init__(self, data: dict):
        for i in data:
            setattr(self, i, data[i])


class Pokemon:
    def __init__(self):
        self.pokemons = {}
        for i in requests.get("https://pokeapi.co/api/v2/pokemon/?limit=1000000").json()['results']:
            self.pokemons.update({i['name']:i['url']})

    def search(self, name: str):
        return [i for i in self.pokemons if name.lower() in i.lower()][:25]

    async def get_stats(
        self, 
        pokemon: str, 
        embed: bool = False, 
        color = 28656
    ):
        try:
            d = await get_async(
                self.pokemons[pokemon],
                kind="json"
            )
        except:
            if embed:
                return(cembed(description="Not found", color=color))
            return{"message": "Not Found"}
        
        if not embed: return d            
        embed=cembed(
            title="Pokemon",
            color=color,
            thumbnail=d['sprites']['front_default']
        )
        for i in d['stats']:
            embed.add_field(
                name=i['stat']['name'],
                value=i['base_stat']
            )
        embed.add_field(
            name="Weight",
            value=d['weight']
        )
        
        embed.add_field(
            name="Abilities",
            value="\n".join([i['ability']['name'] for i in d['abilities']])
        )
        return embed
        
        
        
def validate_url(url: str) -> bool:
    """
    Checks if the url is valid or not
    """
    prepared_request = PreparedRequest()
    try:
        prepared_request.prepare_url(url, None)
        return True
    except MissingSchema as e:
        return False

class TechTerms:
    def __init__(self):
        pass
        
    async def search(self, query):
        '''
        async search a query from techterms.com
        '''
        if not query: 
            l = await get_async("https://techterms.com/ac?query=a")
        else: 
            l = await get_async(f"https://techterms.com/ac?query={query}")
        return [i['value'] for i in json.loads(l)]
        
    async def get_page_as_embeds(self, query):
        url = f"https://techterms.com/definition/{convert_to_url(query.lower())}"
        content = await get_async(url)
        if "Term not found" in content:
            return [{
                'title': "Not found",
                'description': "The definition that you're looking for is not available in TechTerms"
            }]
        soup = BeautifulSoup(content, 'html.parser')
        l = soup.find_all('div', class_ = "card hasheader")[0]
        line = chr(9600)*30
        title = l.h1.get_text()
        embeds = []
        ps = l.find_all('p')
        n = 0
        for i in ps:
            n+=1
            description = f"```\n{line}\n{i.get_text()}\n{line}\n```"
            embed = {
                'title': title,
                'description': description,
                'url': url,
                'footer': {
                    'text': f'Source: TechTerms.com | {n} of {len(ps)}',
                    'icon_url': 'https://play-lh.googleusercontent.com/heAUDFlRj040etj32Pve296Az4r_sgsUECjZNqSJOQAWA96qeqWdfE0pxtx-JNbIbG4'
                },
                'image': "https://play-lh.googleusercontent.com/MDWegEXmQwrcDJBbgjO_83EHp4-PIBdb_IXfYcUQLO5JmQ9w7Td-ZOZ7mKx12Rvctpz4=w600-h300-pc0xffffff-pd"
            }
            embeds.append(embed)
        return embeds

class Proton:
    def __init__(self):
        m = requests.get("https://protondb.max-p.me/games").json()
        self.games = []
        for i in m:
            t = list(i.items())
            self.games.append((t[0][1],t[1][1]))

    def search_game(self, name):
        search_results = []
        name = name.lower()
        for i in self.games:
            if name in i[1].lower():
                search_results.append(i)
        return search_results

    async def report(self, name):
        if self.search_game(name) == []:
            return []
        id = self.search_game(name)[0][0]
        
        report = await get_async(f'https://protondb.max-p.me/games/{id}/reports', kind ="json")        
        reports = []
        for i in report:            
            details  = f"```\n{i['notes'] if i['notes'] else '-'}\n```\n\n```yml\nCompatibility: {i['rating']}\nOperating System: {i['os']}\nGPU Driver: {i['gpuDriver']}\nProton: {i['protonVersion']}\nSpecs: {i['specs']}\n```"    
            
            reports.append({
                'title': str([j[1] for j in self.games if j[0]==id][0]),
                'description': details,
                'footer': timestamp(int(i['timestamp'])),
                'thumbnail': "https://live.mrf.io/statics/i/ps/www.muylinux.com/wp-content/uploads/2019/01/ProtonDB.png?width=1200&enable=upscale",
                'image': "https://pcgw-community.sfo2.digitaloceanspaces.com/monthly_2020_04/chrome_a3Txoxr2j5.jpg.4679e68e37701c9fbd6a0ecaa116b8e5.jpg"
            })
        return reports

class PublicAPI:
    def __init__(self, client):
        self.BASE_URL = "https://api.publicapis.org/entries"
        self.data = {}
        self.all_names = []
        self.client = client
        self.author = None
        

    async def update(self, author):
        if self.data == {}:
            self.data = await get_async(self.BASE_URL, kind = "json")
            self.all_names = [i['API'] for i in self.data['entries']]
        self.author = author

    def search_result(self, name):
        if not self.data:
            return []
        
        return [i for i in self.all_names if name.lower() in i.lower()]

    def find(self, name):
        return self.all_names.index(name)

    def flush(self):
        self.data.clear()
        self.all_names.clear()

    def return_embed(self, index, color):
        if index == -1:
            return cembed(
                title = "Not Found",
                description = "The API you're looking for is not found",
                color = color,
                
            )
        info = self.data['entries'][index]
        return cembed(
            title = info['API'],
            description = info['Description'],
            color = color,
            url = info.get('Link'),
            fields = [
                {'name': k, 'value': v if v else "-", 'inline': False} for k, v in info.items()
            ],
            footer = f"{self.data['count']} Entries",
            author = self.author,
            thumbnail = "https://www.elemental.co.za/cms/resources/uploads/blog/86/926f6aaba773.png"
        )



def delete_all(s: str, ch: Union[List, str]):
    for i in ch:
        s = s.replace(i,"")
    return s

class MineCraft:
    def __init__(self, client):
        self.client = client
        self.BASE_URL = "https://www.digminecraft.com/"
        self.HTML = requests.get("https://www.digminecraft.com/effects/index.php").content.decode()
        self.soup = BeautifulSoup(self.HTML, 'html.parser')
        self.CATEGORIES = {}

    def all_categories(self):        
        for category in self.soup.find_all('div', class_="menu")[1:]:
            for tables in category.find_all('ul'):
                for rows in tables.find_all('li'):
                    if a := rows.a:
                        self.CATEGORIES.update({a.get_text():self.BASE_URL+a['href']})

        return self.CATEGORIES

    async def get_options(self, URL):
        strings = ""
        self.HTML = await get_async(URL)
        self.soup = BeautifulSoup(self.HTML, 'html.parser')

        for i in self.soup.find_all('a', class_="list-group-item"):
            strings+=f"[{i.get_text().strip()}](https://www.digminecraft.com{i['href']})\n"

        return strings
