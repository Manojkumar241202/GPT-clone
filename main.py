import chainlit as cl
import openai
import os

os.environ['OPENAI_API_KEY'] = "Give Your OPENAI API Key"
openai.api_key = os.getenv("OPENAI_API_KEY")
@cl.on_message
async def main(message:str):
    print(message.content)
    response=openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role":"assistant","content":"You're a amazing assistant that is obessed with potato chips"},
            {"role":"user","content":message.content}
        ],
        temperature=0.5
    )
    print(response)
    await cl.Message(content=response.choices[0].message.content).send()