from langchain_core.documents import Document
from rich.prompt import Prompt
from rich.panel import Panel
from config.redis_config import RedisConnection
from config.log_config import LoggingConfig
from schemas.models import InputCheck
from agents.extensions.models.litellm_model import LitellmModel
from agents import (
    Agent,
    InputGuardrail,
    GuardrailFunctionOutput,
    Runner,
    InputGuardrailTripwireTriggered,
    OutputGuardrailTripwireTriggered,
    RunContextWrapper,
    TResponseInputItem,
)
from typing import Any
from dotenv import load_dotenv

import asyncio
import os


# Config
load_dotenv()
console = LoggingConfig().console

redis_init = RedisConnection(os.getenv("REDIS_URL"))
vectorstore = redis_init.get_vectorstore()

model = LitellmModel(model="gemini/gemini-2.5-flash-preview-05-20", api_key=os.getenv("GOOGLE_API_KEY"))

# Agents and functions
async def guardrail_function(ctx: RunContextWrapper[Any], agent: Agent, input: str | list[TResponseInputItem]) -> GuardrailFunctionOutput:
    result = await Runner.run(guardrail_agent, input, context=ctx.context)
    final_output = result.final_output_as(InputCheck)
    return GuardrailFunctionOutput(
        output_info=final_output,
        tripwire_triggered=not final_output.is_content_or_search_related,
    )

def retrieve_relevant_evaluations(query: str, k: int) -> list[Document]:
    """Perform semantic similarity search from Redis vectorstore."""
    return vectorstore.similarity_search(query, k=k)

def build_prompt(query: str, context_docs: list[Document]) -> list:
    context = "\n\n".join(
        f"[{doc.metadata.get('book_id', 'unknown')} / {doc.metadata.get('image_id', 'unknown')}] {doc.page_content.strip()}"
        for doc in context_docs
    )
    system_prompt = f"""
        You are a helpful assistant that answers questions about historical documents, which are grouped by book.

        Each page has been analyzed with a transcription, a translation, and some keywords.
        Here are some relevant excerpts from the stored data:

        {context}

        Now answer this question in the most complete way you can: "{query}"
        """
    return [{"role": "system", "content": system_prompt}, {"role": "user", "content": query}]


def context_retrieval(user_input: str):
    relevant_docs = retrieve_relevant_evaluations(user_input, k=5)
    new_messages = build_prompt(user_input, relevant_docs)
    return new_messages


guardrail_agent = Agent(
    name="Input Check",
    instructions="Check if the user input is related to a query search using the stored documents.",
    output_type=InputCheck,
    model=model,
)

query_agent = Agent(
    name="Query Agent",
    instructions="Answer the user query using the stored documents.",
    input_guardrails=[
        InputGuardrail(guardrail_function=guardrail_function),
    ],
    model=model,
)

async def chat_loop():
    console.print("Chat session started. Type 'exit' to quit.\n", style="system")
    
    try:
        user_input = Prompt.ask("You", console=console, style="input")
        if user_input.strip().lower() in {"exit", "quit"}:
            console.print("\nGoodbye!", style="system")
            return
        new_messages = context_retrieval(user_input)
        response = await Runner.run(query_agent, new_messages)
        console.print(Panel.fit(response.final_output, title="📜 Assistant", title_align="left", border_style="assistant"))

        while True:
            user_input = Prompt.ask("You", console=console)
            if user_input.strip().lower() in {"exit", "quit"}:
                console.print("\nGoodbye!", style="system")
                return
            new_messages = context_retrieval(user_input)
            new_input = response.to_input_list() + new_messages
            response = await Runner.run(query_agent, new_input)
            console.print(Panel.fit(response.final_output, title="📜 Assistant", title_align="left", border_style="assistant"))
    except InputGuardrailTripwireTriggered or OutputGuardrailTripwireTriggered:
        console.print("Request not supported")
    except Exception as e:
        console.print(f"An error occurred: {e}")


if __name__ == "__main__":
    asyncio.run(chat_loop())
