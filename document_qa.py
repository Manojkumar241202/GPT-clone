from langchain.document_loaders import PyPDFLoader,TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.chat_models import ChatOpenAI
from langchain.chains import RetrievalQAWithSourcesChain
import chainlit as cl
import os
import openai
text_splitter =RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=1000)
os.environ['OPENAI_API_KEY'] = "Give Your OPENAI API key"
openai.api_key = os.getenv("OPENAI_API_KEY")
embeddings=OpenAIEmbeddings()

welcome_message="Welcome to document chatbot"

def process_file(file):
    print(type(file))
    import tempfile
    Loader=PyPDFLoader
    if file.type=="text/plain":
        Loader=TextLoader
    elif file.type==".pdf":
        Loader =PyPDFLoader
    with tempfile.NamedTemporaryFile() as tmpfile:
        tmpfile.write(file.content)
        loader=Loader(tmpfile.name)
        documents=loader.load()
        docs=text_splitter.split_documents(documents)
        for i,doc in enumerate(docs):
            doc.metadata["source"] = f"source{i}"
    return docs
    
def get_docsearch(file):
    docs=process_file(file)
    
    #save the user session
    cl.user_session.set("docs",docs)
    
    #create unique namespace for the file
    docsearch=Chroma.from_documents(docs,embeddings)
    return docsearch
    
    
@cl.on_chat_start
async def start():
    #sending an image with the local file path 
    await cl.Message(content="Now you can chat with your pdfs").send()
    files=None
    while files is None:
        files=await cl.AskFileMessage(
            content=welcome_message,
            accept=["plain/text",".pdf"],
            max_size_mb=20,
            timeout=180
        ).send()
    file=files[0]
    
    msg=cl.Message(content=f"Processig {file.name}...")
    await msg.send()
    
    #no sync implemented in Pinecone client, fallback to sync
    docsearch = await cl.make_async(get_docsearch)(file)
    
    chain = RetrievalQAWithSourcesChain.from_chain_type(
        llm=ChatOpenAI(temperature=0.5,streaming=True),
        retriever=docsearch.as_retriever(max_token_limits=4097)
    )
    
    #let user know system is ready
    msg.content=f"{file.name} processed. You can ask any questions"
    await msg.update()
    
    cl.user_session.set("chain",chain)

@cl.on_message
async def main(message):
    chain=cl.user_session.get("chain")
    # Optionally, you can also pass the prefix tokens that will be used to identify the final answer
    #answer_prefix_tokens=["FINAL", "ANSWER"]

    cb=cl.AsyncLangchainCallbackHandler(
        stream_final_answer=True,
    )
    res=await chain.acall(message.content,callbacks = [cb])
    cb.has_streamed_final_answer=True
    sources=res['sources'].strip()
    answer=res['answer']
    source_elements=[]
    
    #get the documents from the user's session
    docs=cl.user_session.get("docs")
    metadata=[doc.metadata for doc in docs]
    all_sources=[m['source'] for m in metadata]
    if sources:
        found_sources=[]
        
        #add the sources to the message
        for source in sources.split(","):
            source_name=source.strip().replace(".","")
            
            #get the index of the source
            try:
                index=all_sources.index(source_name)
            except:
                continue
            text=docs[index].page_content
            found_sources.append(source_name)
            source_elements.append(cl.Text(content=text,name=source_name))
            
        if found_sources:
            answer+=f"\nSources:  {', '.join(found_sources)}"
        else:
            answer+="\n No sources found"
        
        # if cb.has_streamed_final_answer:
        #     cb.final_stream.elements=source_elements
        #     await cb.final_stream.update()
        # else:
        await cl.Message(content=answer,elements=source_elements).send()
            
            
            
    
