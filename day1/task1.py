!pip install -q openai

from google.colab import userdata
from openai import OpenAI

client = OpenAI(
    api_key=userdata.get("agent1"),
    base_url="https://api.groq.com/openai/v1"
)

SYSTEM = """
You are an AI Car Showroom Assistant.

Your job is to help customers explore cars, understand features,
compare models, and choose suitable vehicles.

You represent a car showroom.

Guidelines:
1. Greet customers politely.
2. Answer questions about available cars.
3. Explain car features, specifications, and variants.
4. Help customers compare different cars.
5. Recommend cars based on customer requirements.
6. Keep responses clear and easy to understand.
7. Never invent vehicle specifications or prices.
8. If information is unavailable, politely say that it needs confirmation.
9. Ask relevant questions when additional information is required.
10. Maintain a professional and friendly conversation.
"""

response = client.chat.completions.create(
    model="openai/gpt-oss-20b",
    messages=[
        {"role": "system", "content": SYSTEM},
        {"role": "user", "content": "Hello! I am looking for a new car."}
    ],
    temperature=0.2
)

print(response.choices[0].message.content)
print("\nToken Usage:", response.usage)
