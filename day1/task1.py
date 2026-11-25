!pip install -q openai

from google.colab import userdata
from openai import OpenAI

client = OpenAI(
    api_key=userdata.get("agent1"),
    base_url="https://api.groq.com/openai/v1",
)

response = client.chat.completions.create(
    model="openai/gpt-oss-20b",
    messages=[
        {"role": "system", "content": "You are a funny joker"},
        {"role": "user", "content": "tell me a joke"},
    ],
)

print(response.choices[0].message.content)
