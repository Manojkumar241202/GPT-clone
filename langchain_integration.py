import chainlit as cl
import openai
from langchain import OpenAI,PromptTemplate,LLMChain
import os
os.environ['OPENAI_API_KEY'] = "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"
openai.api_key = os.getenv("OPENAI_API_KEY")

template="Answer this Question :{question}"
@cl.on_chat_start
def main():
    prompt=PromptTemplate(template=template,input_variables=['question'])
    llm_chain=LLMChain(prompt=prompt,
                       llm=OpenAI(temperature=1,streaming=True,verbose=True)
                       )
    cl.user_session.set("llm_chain",llm_chain)
    
@cl.on_message
async def main(message):
    llm_chain=cl.user_session.get("llm_chain")
    res=await llm_chain.acall(message.content,callbacks=[cl.AsyncLangchainCallbackHandler()])
    await cl.Message(content=res['text']).send()