import os
import discord
from discord.ext.commands import Bot, CommandNotFound, Context
from dotenv import load_dotenv
import random
import asyncio
from PIL import Image, ImageEnhance, ImageFilter
import pytesseract
import io
import database
from quiz import generate_quiz, update_settings
from getimage import download_image
from getstock import get_stock_info
from texting import send_text
from chatgpt import ask, generate_image
from utils import read_settings

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
intents = discord.Intents.default()
intents.message_content = True
client = Bot("!", intents=intents)
settings = read_settings()


@client.event
async def on_ready():
    print(f"{client.user} has connected to Discord!")


@client.event
async def on_command_error(ctx, error):
    if isinstance(error, CommandNotFound):
        return
    raise error


client.remove_command("help")


@client.command()
async def help(ctx: Context):
    embed = discord.Embed(
        title="Help",
        description="List of commands are:",
        color=discord.Color.green(),
    )

    embed.add_field(
        name="!gpt [prompt]",
        value="Generates text based on GPT-4.",
        inline=False,
    )
    embed.add_field(
        name="!dalle [prompt]",
        value="Generates an image based on the DALL-E 2 model.",
        inline=False,
    )
    embed.add_field(
        name="!bing [query]",
        value="Fetches an image based on the query from Bing.",
        inline=False,
    )
    embed.add_field(
        name="!stock [stock]", value="Fetches stock information.", inline=False
    )
    embed.add_field(
        name="!randomcountry", value="Fetches a random country.", inline=False
    )
    embed.add_field(
        name="!text [number] [message]",
        value="Sends a text message to the specified number.",
        inline=False,
    )
    embed.add_field(
        name="!OCR [image]",
        value="Uses optical character recognition to read text from an image",
        inline=False,
    )
    embed.add_field(
        name="!quiz [subject]",
        value="Generates a quiz question.",
        inline=False,
    )
    quiz_set_desc = (
        "Set quiz settings. Valid settings and their ranges are:\n"
        "- `time [5-60]`: The time limit for answering a quiz question.\n"
        "- `difficulty [1-10]`: The difficulty level of quiz questions.\n"
        "- `choices [2-7]`: The number of answer choices in quiz questions."
    )
    embed.add_field(
        name="!quiz set [setting] [value]", value=quiz_set_desc, inline=False
    )

    await ctx.send(embed=embed)


@client.command()
async def gpt(ctx, *args):
    await ctx.send(ask(os.getenv("API_KEY"), " ".join(args)))


@client.command()
async def dalle(ctx, *, prompt: str):
    api_key = os.getenv("API_KEY")
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
    send_text(
        destination_number,
        message,
        os.getenv("SOURCE_NUMBER"),
        os.getenv("ACCOUNT_SID"),
        os.getenv("AUTH_TOKEN"),
    )
    await ctx.send("Message has been sent")


@client.command()
async def OCR(ctx):
    if len(ctx.message.attachments) == 0:
        await ctx.send("Please attach an image.")
        return

    attachment = ctx.message.attachments[0]
    image_data = await attachment.read()

    image = Image.open(io.BytesIO(image_data))

    # Preprocessing
    image = image.convert('L')  # Convert to grayscale
    image = image.filter(ImageFilter.SHARPEN)  # Apply sharpen filter
    enhancer = ImageEnhance.Contrast(image)
    image = enhancer.enhance(2)  # Increase contrast

    text = pytesseract.image_to_string(image)

    if len(text) == 0:
        await ctx.send("No text found.")
    else:
        await ctx.send(f"Extracted text: {text}")


# we need to grab the settings here
@client.command()
async def quiz(ctx, *args):
    if args and args[0].lower() == 'settings':
        await quiz_settings(ctx)
        return
    elif len(args) >= 3 and args[0].lower() == 'set':
        await ctx.send(update_settings(settings, args[1], args[2]))
        return
 
    subject = " ".join(args)
    quiz = generate_quiz(settings, subject)

    if type(quiz) == str:
        await ctx.send(quiz)

    embed = discord.Embed(
        title=f"Quiz on {subject}",
        description=f"Time: {settings['time']} seconds",
        color=discord.Color.blue(),
    )
    embed.add_field(name="Question", value=quiz["question"], inline=False)
    choice_text = "\n".join(quiz["choices"])
    embed.add_field(name="Choices", value=choice_text, inline=False)

    await ctx.send(embed=embed)

    def check_answer(m):
        return m.channel == ctx.channel and m.content.upper() in [
            chr(65 + i) for i in range(settings["choices"])
        ]
    try:
        msg = await client.wait_for("message", timeout=settings["time"],
                                    check=check_answer)
    except asyncio.TimeoutError:
        response = f"Time's up! The correct answer was {quiz['answer']}"
    else:
        user_answer_label = msg.content.upper()
        is_correct = user_answer_label == quiz["answer"]
        response = f"{'Correct' if is_correct else 'Wrong'}! The answer was {quiz['answer']}."

    await ctx.send(response)


@client.command()
async def quiz_settings(ctx: Context):
    embed = discord.Embed(
        title="Current Quiz Settings", color=discord.Color.blue()
    )

    embed.add_field(
        name="Time", value=f"{settings['time']} seconds", inline=True
    )
    embed.add_field(
        name="Difficulty",
        value=f"{settings['difficulty']} out of 10",
        inline=True,
    )
    embed.add_field(
        name="Choices", value=f"{settings['choices']} choices", inline=True
    )

    await ctx.send(embed=embed)


client.run(TOKEN)
