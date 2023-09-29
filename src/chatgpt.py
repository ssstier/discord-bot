import openai
from io import BytesIO
import base64


def ask(api_key, prompt):
    openai.api_key = api_key
    message = {
        "role": "user",
        "content": prompt
    }
    result = openai.ChatCompletion.create(model="gpt-4", messages=[message])
    return result.choices[0].message.content[:2000]


def generate_image(api_key, prompt):
    openai.api_key = api_key
    response = openai.Image.create(prompt=prompt, model="image-alpha-001",
                                   response_format="b64_json")

    # Access the base64 data from the response
    base64_data = response['data'][0]['b64_json']

    # Decode Base64 data to bytes
    image_data = base64.b64decode(base64_data)

    # Return a BytesIO object and filename
    return BytesIO(image_data), "generated_image.jpg"
