import os
import discord
from discord.ext.commands import Bot
from discord.ext.commands import CommandNotFound
from dotenv import load_dotenv
import random
import database
from getimage import download_image
from getstock import get_stock_info
from command_prompt import icmp
from texting import send_text
from chatgpt import ask, generate_image


load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
intents = discord.Intents.default()
intents.message_content = True
client = Bot("!", intents=intents)


@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')


@client.event
async def on_command_error(ctx, error):
    if isinstance(error, CommandNotFound):
        return
    raise error


@client.command()
async def gpt(ctx, *args):
    await ctx.send(ask(os.getenv('API_KEY'), " ".join(args[:])))

@client.command()
async def dalle(ctx, *, prompt: str):
    api_key = os.getenv('API_KEY')
    pic, filename = generate_image(api_key, prompt)
    await ctx.send(file=discord.File(pic, filename=filename))

@client.command()
async def bing(ctx, query):
    pic, filename = download_image(query)
    await ctx.send(file=discord.File(pic, filename))


@client.command()
async def stock(ctx, stock):
    await ctx.send(get_stock_info(stock))


@client.command()
async def randomcountry(ctx):
    await ctx.send(random.choice(database.countries))


@client.command()
async def ping(ctx, host):
    output = icmp(host)
    await ctx.send(output)


@client.command()
async def text(ctx, destination_number, *, message):
    action = send_text(destination_number, message, os.getenv('SOURCE_NUMBER'),
                       os.getenv('ACCOUNT_SID'), os.getenv('AUTH_TOKEN'))
    await ctx.send("Message has been sent")


client.run(TOKEN)
