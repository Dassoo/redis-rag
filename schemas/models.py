from pydantic import BaseModel
from typing import List, Annotated, Any
from typing_extensions import TypedDict
from operator import add

# Single document page
class Evaluation(BaseModel):
    model: str
    transcription: str
    translation: str
    keywords: List[str]

# LangChain state
class EvaluationState(TypedDict):
    evaluations: Annotated[List[Evaluation], add]
    model: Any
    input_image: str
    human_feedback: str

# Query guardrail
class QueryCheck(BaseModel):
    is_content_or_search_related: bool
    reasoning: str
