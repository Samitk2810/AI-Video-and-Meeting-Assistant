from langchain_mistralai import ChatMistralAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.runnables import RunnablePassthrough, RunnableLambda

import os 

def get_llm():
    return ChatMistralAI(model = "mistral-small-latest", mistral_api_key = os.environ.get("MISTRAL_API_KEY"), temperature=0.3)

def split_transcripts(transcripts):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=3000, chunk_overlap=200)
    return text_splitter.split_text(transcripts)

def summarize(transcripts):
    llm = get_llm()
    map_prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a helpful assistant that summarizes portion of transcripts concisely."),
        ("human", "{text}")
    ]
    )
    map_chain = map_prompt | llm | StrOutputParser()
    chunks = split_transcripts(transcripts)
    chunk_summaries = []
    for chunk in chunks:
        summary = map_chain.invoke({"text": chunk})
        chunk_summaries.append(summary)
    combined =  "\n\n".join(chunk_summaries)
    combined_prompt = ChatPromptTemplate.from_messages([
        ("system", "Combine these partial summaries into one final professional summary in bullet points."),
        ("human", "{text}")
    ]
    )
    combined_chain = RunnablePassthrough() | RunnableLambda(lambda x: {"text": x}) | combined_prompt | llm | StrOutputParser()
    return combined_chain.invoke(combined)

def generate_title(summary):
    llm = get_llm()
    title_prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a helpful assistant that generates a concise and professional title (max 8 words) for the following summary. Only return the title without any additional text."),
        ("human", "{text}")
    ]
    )
    title_chain = RunnablePassthrough() | RunnableLambda(lambda x: {"text": x}) | title_prompt | llm | StrOutputParser()
    return title_chain.invoke(summary[:2000])