import os
import discord
from discord.ext.commands import Bot, CommandNotFound, Context
from dotenv import load_dotenv
import random
import database  # Your own database module
from getimage import download_image  # Your own getimage module
from getstock import get_stock_info  # Your own getstock module
from texting import send_text  # Your own texting module
from chatgpt import ask, generate_image  # Your own chatgpt module

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

# Unload the default help command to use a custom one
client.remove_command('help')

@client.command()
async def help(ctx: Context):
    embed = discord.Embed(title="Help", description="List of commands are:", color=discord.Color.green())
    embed.add_field(name="!gpt [args]", value="Generates text based on GPT-4", inline=False)
    embed.add_field(name="!dalle [prompt]", value="Generates an image based on the DALL-E 2 model", inline=False)
    embed.add_field(name="!bing [query]", value="Fetches an image based on the query from Bing", inline=False)
    embed.add_field(name="!stock [stock]", value="Fetches stock information", inline=False)
    embed.add_field(name="!randomcountry", value="Fetches a random country", inline=False)
    embed.add_field(name="!text [number] [message]", value="Sends a text message to the specified number", inline=False)

    await ctx.send(embed=embed)

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
async def text(ctx, destination_number, *, message):
    action = send_text(destination_number, message, os.getenv('SOURCE_NUMBER'), os.getenv('ACCOUNT_SID'), os.getenv('AUTH_TOKEN'))
    await ctx.send("Message has been sent")

client.run(TOKEN)
