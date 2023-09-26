import os
import discord
from discord.ext.commands import Bot, CommandNotFound, Context
from dotenv import load_dotenv
import random
import asyncio
import json
import re
import database
from getimage import download_image
from getstock import get_stock_info
from texting import send_text
from chatgpt import ask, generate_image

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
intents = discord.Intents.default()
intents.message_content = True
client = Bot("!", intents=intents)


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
        name="!gpt [args]",
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
async def quiz(ctx, *subject, **kwargs):
    try:
        with open("settings.json", "r") as f:
            settings = json.load(f)
    except FileNotFoundError:
        settings = {"time": 20, "difficulty": 5, "choices": 4}

    if subject[0].lower() == "set":
        if len(subject) >= 3:
            setting_name = subject[1].lower()
            try:
                value = int(subject[2])
            except ValueError:
                await ctx.send("Invalid value type. Must be an integer.")
                return

            if setting_name == "time":
                if not (5 <= value <= 60):
                    await ctx.send(
                        "Time setting must be between 5 and 60 seconds."
                    )
                    return

            elif setting_name == "difficulty":
                if not (1 <= value <= 10):
                    await ctx.send(
                        "Difficulty setting must be between 1 and 10."
                    )
                    return

            elif setting_name == "choices":
                if not (2 <= value <= 7):
                    await ctx.send(
                        "Invalid choices setting. Must be between 2 and 7."
                    )
                    return

            else:
                await ctx.send(
                    "Invalid setting. Use 'time', 'difficulty', or 'choices'."
                )
                return

            settings[setting_name] = value
            with open("settings.json", "w") as f:
                json.dump(settings, f)
            await ctx.send(
                f"Settings have been updated. Set {setting_name} to {value}."
            )
            return
        else:
            await ctx.send(
                "Error - format should be !quiz set <setting_name> <value>"
            )
            return

    elif subject[0].lower() == "settings":
        # handle displaying settings
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
        return

    else:
        subject = " ".join(subject)
        time = settings.get("time", 20)
        difficulty = settings.get("difficulty", 5)
        choices = settings.get("choices", 4)

        if (
            not (1 <= settings["difficulty"] <= 10)
            or not (5 <= settings["time"] <= 60)
            or not (2 <= settings["choices"] <= 7)
        ):
            await ctx.send("Invalid settings.")
            return

        prompt = (
            f"A quiz consists of 3 sections: Question:, Choices:, and "
            f"Answer:. Each section should be separated by a new line. "
            f"The format of a quiz must be as follows: Question: What "
            f"is 2 + 2? Choices: A) 3 B) 4 C) 5 D) 6 Answer: B "
            f"Generate a quiz question on the subject of {subject} "
            f"with a difficulty level of {difficulty} on a scale of 1-10 "
            f"where 1 is the easiest and 10 is the most difficult. "
            f"Provide {choices} answer choices."
        )

        api_key = os.getenv("API_KEY")
        response = ask(api_key, prompt)

        try:
            match = re.search(
                r"Question:\s*(.*?)\nChoices:\s*(.*?)\nAnswer:\s*(.*)",
                response,
                re.DOTALL,
            )
            if not match:
                await ctx.send(
                    "Failed to generate a quiz question. Please try again."
                )
                return

            question = match.group(1).strip()
            answer_choices_text = match.group(2).replace("\n", " ").strip()
            correct_answer = match.group(3).strip()
            answer_choices = re.split(r" (?=[A-Z]\))", answer_choices_text)

        except Exception:
            await ctx.send(
                "Failed to generate a quiz question. Please try again."
            )
            return

        embed = discord.Embed(
            title=f"Quiz on {subject}",
            description=f"Time: {time} seconds",
            color=discord.Color.blue(),
        )
        embed.add_field(name="Question", value=question, inline=False)
        choice_text = "\n".join(answer_choices)
        embed.add_field(name="Choices", value=choice_text, inline=False)

        await ctx.send(embed=embed)

        def check_answer(m):
            return m.channel == ctx.channel and m.content.upper() in [
                chr(65 + i) for i in range(choices)
            ]

        try:
            msg = await client.wait_for(
                "message", timeout=time, check=check_answer
            )
        except asyncio.TimeoutError:
            await ctx.send(
                "Time's up! The correct answer was " +
                f"{correct_answer.split(') ')[0]}."
            )

        else:
            user_answer_label = msg.content.upper()
            correct_answer_label = correct_answer.split(") ")[0]
            if user_answer_label == correct_answer_label:
                await ctx.send(
                    f"Correct! The answer was {correct_answer_label}."
                )
            else:
                await ctx.send(
                    f"Wrong! The correct answer was {correct_answer_label}."
                )


@client.command()
async def settings(ctx: Context):
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
