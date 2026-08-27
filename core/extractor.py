# Actionable items, decisions, questions

from langchain_mistralai import ChatMistralAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_text_splitters import RecursiveCharacterTextSplitter
import os


def get_llm():
    return ChatMistralAI(
        model="mistral-small-latest",
        mistral_api_key=os.environ.get("MISTRAL_API_KEY"),
        temperature=0.2
    )


def split_transcript(transcript):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=3000,
        chunk_overlap=200
    )

    return text_splitter.split_text(transcript)


def build_chain(system_prompt):
    llm = get_llm()

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "{text}")
    ])

    return prompt | llm | StrOutputParser()


def extract_action_items(chunks, chain):

    results = []

    for chunk in chunks:
        result = chain.invoke({"text": chunk})
        results.append(result)

    return "\n\n".join(results)


def extract_key_decisions(chunks, chain):

    results = []

    for chunk in chunks:
        result = chain.invoke({"text": chunk})
        results.append(result)

    return "\n\n".join(results)


def extract_questions(chunks, chain):

    results = []

    for chunk in chunks:
        result = chain.invoke({"text": chunk})
        results.append(result)

    return "\n\n".join(results)


def extract_all(transcript):

    # Split ONCE
    chunks = split_transcript(transcript)

    # Build chains ONCE
    action_chain = build_chain(
        """ You are an expert meeting analyst.

            From the meeting transcript section, extract all action items.

            For each provide:
            - Task description
            - Owner (who is responsible)
            - Deadline (if mentioned, else write 'Not specified')

            Format as a numbered list.

            If none are found, say:
            'No action items found.'"""
    )

    decision_chain = build_chain(
        """ You are an expert meeting analyst.

            From the meeting transcript section, extract all key decisions made.

            Format as a numbered list.

            If none are found, say:
            'No key decisions found.'"""
    )

    question_chain = build_chain(
        """ You are an expert meeting analyst.

            From the meeting transcript section, extract all unresolved questions
            or topics needing follow-up.

            Format as a numbered list.

            If none are found, say:
            'No open questions found.'"""
    )

    # Reuse the SAME chunks
    action_items = extract_action_items(
        chunks,
        action_chain
    )

    decisions = extract_key_decisions(
        chunks,
        decision_chain
    )

    questions = extract_questions(
        chunks,
        question_chain
    )

    return {
        "action_items": action_items,
        "decisions": decisions,
        "questions": questions
    }