import chainlit as cl
import os

from langchain.chat_models import ChatOpenAI
from langchain.agents import load_tools,initialize_agent,AgentType
import openai
os.environ['OPENAI_API_KEY'] = "Give Your OPENAI API key"
openai.api_key = os.getenv("OPENAI_API_KEY")



@cl.on_chat_start
def start():
    llm=ChatOpenAI(temperature=0.5)
    tools = load_tools(
        ["arxiv"]
    )
    agent_chain = initialize_agent(
        tools,
        llm,
        max_iteration=5,
        agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        handling_parsing_erros=True,
        verbose=True
    )
    cl.user_session.set("agent",agent_chain)

@cl.on_message
async def main(message):
    llm_chain=cl.user_session.get("agent")
    cb=cl.LangchainCallbackHandler(stream_final_answer=True)
    await cl.make_async(llm_chain.run)(message.content,callbacks=[cb])
    