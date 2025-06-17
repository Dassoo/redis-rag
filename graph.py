from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.constants import Send
from langgraph.graph import END, StateGraph, START
from config.redis_config import RedisConnection
from config.log_config import LoggingConfig
from config.decorators import node
from schemas.models import EvaluationState, Evaluation
from handlers.input_handler import InputHandler
from handlers.output_handler import OutputHandler

from rich.panel import Panel
from pathlib import Path
from dotenv import load_dotenv

import base64
import shutil
import time
import os

load_dotenv()
start_time = time.time()
console = LoggingConfig().console

# Redis store
redis_init = RedisConnection(os.getenv("REDIS_URL"))
vectorstore = redis_init.get_vectorstore()

# Nodes
@node
def human_feedback_node(state: EvaluationState):
    """No-op node that should be interrupted on user input"""
    return state

@node
def init_evaluation(state: EvaluationState):
    return [
        Send("conduct_evaluation", {
            "model": model,
            "evaluations": state.get("evaluations", []),
            "input_image": state["input_image"],
            "human_feedback": state.get("human_feedback", "")
        })
        for model in llm_list
    ]

@node
def conduct_evaluation(state: EvaluationState):
    evaluation = image_scan(state)
    return {"evaluations": state.get("evaluations", []) + [evaluation]}

@node
def evaluation_summary(state: EvaluationState):
    handler = OutputHandler()
    state = handler.summary(state)
    return state


# Image scan and helper functions
def encode_image(image_path: str) -> str:
    """Encode image to base64"""
    with open(image_path, "rb") as img:
        return base64.b64encode(img.read()).decode()


def image_scan(state: EvaluationState) -> Evaluation:
    b64 = encode_image(state["input_image"])
    structured_llm = state["model"].with_structured_output(Evaluation)
    prompt = f"""
        You are a historical‐document expert. Provide:
        1) A perfect literal transcription in the original language, respecting the original orthography, punctuation, spacing and formatting.
        2) An English translation (if the document is already written in modern English, leave the "translation" field empty instead).
        3) A list of English keywords about the document. IMPORTANT: use capital letters initials only for proper names.

        Consider that sometimes the document page may end with a truncated word, which is finishing on the next page.
        In this case, don't complete the word.

        Sometimes there is no text since the picture may represent just a cover, an illustration or a blank page. In that case, just
        keep the related fields empty.

        Take into account the user feedback about the document (if any): {state.get('human_feedback','')}
        """
    result = structured_llm.invoke([
        SystemMessage(content=prompt),
        HumanMessage(content=[
            {"type":"image_url","image_url":{"url":f"data:image/jpeg;base64,{b64}"}},
            {"type":"text","text":"Please analyze this document."}
        ])
    ])
    state['human_feedback'] = None
    # Use the actual model name from the model's configuration
    result.model = state["model"].model
    return result


# Assemble and run graph
llm_list = [ ChatGoogleGenerativeAI(model="gemini-2.5-pro-preview-06-05", temperature=0) ]

builder = StateGraph(EvaluationState)
builder.add_node("human_feedback_node", human_feedback_node)
builder.add_node("conduct_evaluation", conduct_evaluation)
builder.add_node("evaluation_summary", evaluation_summary)

builder.add_edge(START, "human_feedback_node")
builder.add_conditional_edges("human_feedback_node", init_evaluation, ["conduct_evaluation"])
builder.add_edge("conduct_evaluation", "evaluation_summary")
builder.add_edge("evaluation_summary", END)

graph = builder.compile(checkpointer=MemorySaver(), interrupt_before=["human_feedback_node"])


# Input config
INPUT_PATH = Path("samples/tensorflow.pdf")  # Can be a folder or a PDF
TEMP_IMAGE_DIR = Path(INPUT_PATH.stem)
TEMP_IMAGE_DIR.mkdir(exist_ok=True)

image_files = InputHandler().extract(INPUT_PATH)

feedback = input("Would you like to give some human-in-the-loop feedback for every scanned page? (y/n)")
if feedback.lower() == "y":
    feedback = True
else:
    feedback = False

# Loop over images
for image_path in image_files:
    image_id = Path(image_path).stem

    console.rule(f"Processing {Path(image_path).name}", style="event")

    try:
        thread = {"configurable": {"thread_id": f"{INPUT_PATH.name}:{image_id}"}}
        initial_state = {
            "evaluations": [],
            "model": llm_list,
            "input_image": str(image_path),
            "human_feedback": ""
        }

        # Run graph verbose
        for event in graph.stream(initial_state, thread, stream_mode="values"):
            console.print(Panel.fit(str(event), title="📦 Event", border_style="event"))

        if feedback:
            feedback = console.input("[feedback]Insert feedback:[/feedback] ")
        graph.update_state(thread, {"human_feedback": feedback}, as_node="human_feedback_node")

        # Resume from feedback node
        for event in graph.stream(None, thread, stream_mode="updates"):
            console.print(Panel.fit(str(event), title="📦 Event", border_style="event"))

    except Exception as e:
        console.print(f"❌ Error processing {Path(image_path).name}: {e}", style="error")

console.print(f"Execution time: --- {time.time() - start_time:.2f} seconds ---", style="system")

# if INPUT_PATH.suffix.lower() == ".pdf":
#     shutil.rmtree(TEMP_IMAGE_DIR)