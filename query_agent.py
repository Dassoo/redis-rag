from langchain_core.documents import Document
from config.redis_config import RedisConnection
from config.log_config import LoggingConfig
from config.llm_config import LLMConfig
from schemas.models import QueryCheck, QueryGraph
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
from rich.prompt import Prompt
from rich.panel import Panel
from typing import Any
import asyncio
import os

# Config
console = LoggingConfig().console

# Get query model from config
llm_config = LLMConfig()
model = llm_config.get_model('query')

# Agents and functions
async def guardrail_function(ctx: RunContextWrapper[Any], agent: Agent, input: str | list[TResponseInputItem]) -> GuardrailFunctionOutput:
    result = await Runner.run(guardrail_agent, input, context=ctx.context)
    final_output = result.final_output_as(QueryCheck)
    return GuardrailFunctionOutput(
        output_info=final_output,
        tripwire_triggered=not final_output.is_content_or_search_related,
    )

def retrieve_relevant_evaluations(query: str, k: int) -> list[Document]:
    """Perform semantic similarity search from Redis vectorstore."""
    redis_init = RedisConnection(os.getenv("REDIS_URL"))
    vectorstore = redis_init.get_vectorstore()
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
    output_type=QueryCheck,
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

graph_agent = Agent(
    name="Graph Agent",
    instructions="Based on the query, build a relationship graph. Do not add any additional text or explanation. Only return the required graph.",
    output_type=QueryGraph,
    model=model,
)

async def chat_loop():
    console.print("\nChat session started. Type 'exit' to quit. Add '-g' to the query to build a relationship graph.", style="system")
    console.print("The query must be fitting the stored documents or it will be rejected.", style="system")

    try:
        conversation_history = []

        while True:
            user_input = Prompt.ask("\n[input]You[/input]", console=console)
            if user_input.strip().lower() in {"exit", "quit"}:
                console.print("\nGoodbye!", style="system")
                break

            console.print("\nThinking...", style="system")
            new_messages = context_retrieval(user_input)
            full_input = conversation_history + new_messages

            response = await Runner.run(query_agent, full_input)
            console.print(Panel.fit(response.final_output, title="📜 Assistant", title_align="left", border_style="assistant"))

            # Makes graph only if user input ends with "-g"
            if user_input.endswith("-g"):
                console.print("\nBuilding connections...", style="system")
                graph_response = await Runner.run(graph_agent, full_input)
                console.print(graph_response.final_output, style="assistant")

            conversation_history = response.to_input_list()

    except (InputGuardrailTripwireTriggered, OutputGuardrailTripwireTriggered):
        console.print("❌ Request not supported", style="error")
    except Exception as e:
        console.print(f"❌ An error occurred: {e}", style="error")


async def redis_store():
    redis_init = RedisConnection(os.getenv("REDIS_URL"))
    redis_init.read_vectorstore()


if __name__ == "__main__":
    console.print("\nWelcome to the Redis RAG Query Agent", style="info")
    console.print("""
    [info]Available Options:[/info]
    [green]chat[/green] - Start a chat session with the RAG system
    [blue]store[/blue] - Connect to Redis and display available documents
    [red]exit[/red] - Exit the program
    """, highlight=False)
    
    selection = Prompt.ask(
        "\n[input]Please select an option:[/input]",
        choices=["chat", "store", "exit"],
        console=console
    )
    
    if selection == "chat":
        asyncio.run(chat_loop())
    elif selection == "store":
        asyncio.run(redis_store())
    elif selection == "exit":
        console.print("\nGoodbye!", style="system")
        exit()
