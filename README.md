# discord-bot

A multifunctional Discord bot offering features like stock data, text and image generation, quizzes, and more.

----

## Setup and Installation
### 1. Clone the respository

```
git clone https://github.com/ssstier/discord-bot.git
cd discord-bot
```

### 2. Install dependencies

```
pip install -r requirements.txt
```
### 3. Environment Configuration
Ensure to fill out the .env file in the root directory with the required API keys and configurations. The template is already in place.

### 4. Start the Bot
```
python3 src/bot.py
```

----
## Commands
    !gpt [prompt]: Generate text based on GPT-4.
    !dalle [prompt]: Generate an image based on the DALL-E 2 model.
    !bing [query]: Fetch an image from Bing based on the query.
    !stock [stock]: Get stock information.
    !randomcountry: Retrieve a random country's details.
    !text [number] [message]: Send a text message.
    !OCR [image]: Recognize text from an image using OCR.
    !quiz [subject]: Produce a quiz question.
    !quiz set [setting] [value]: Adjust quiz settings.
    !quiz settings: shows current quiz settings
    !help: displays all commands

## License
This project is under the [MIT License](https://github.com/ssstier/discord-bot/blob/main/LICENSE).
