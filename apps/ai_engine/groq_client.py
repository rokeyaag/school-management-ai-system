from groq import Groq
from decouple import config

client = Groq(api_key=config('GROQ_API_KEY'))

def chat(messages, model='meta-llama/llama-4-scout-17b-16e-instruct'):
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        max_tokens=1024,
        temperature=0.7,
    )
    return response.choices[0].message.content