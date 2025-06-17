from pydantic import BaseModel, Field
from typing import List, Annotated, Any
from typing_extensions import TypedDict
from operator import add

# Single document page evaluation
class Evaluation(BaseModel):
    model: str = Field(description="LLM version used to scan the document.")
    transcription: str = Field(description="Literal transcription of the document.")
    translation: str = Field(description="English translation of the document.")
    keywords: List[str] = Field(description="List of keywords about the document.")

# LangChain graph state
class EvaluationState(TypedDict):
    evaluations: Annotated[List[Evaluation], add]
    model: Any = Field(description="LLM version used to scan the document.")
    input_image: str = Field(description="Input image path.")
    human_feedback: str = Field(description="(Optional) Feedback from the user about the document.")

# Query guardrail
class QueryCheck(BaseModel):
    is_content_or_search_related: bool = Field(description="Check whether the query is related to the content or to a search in the documents.")
    reasoning: str = Field(description="Explain why the query is related to the content or search in the documents.")

# Connections to the subject of the user query
class QueryGraphConnection(BaseModel):
    connection_name: str = Field(description="The name of the connection, which may be a name, an object, a place, etc.")
    source: str = Field(description="The source of the connection, which is the document name and page number.")
    reasoning: str = Field(description="The reasoning of the connection, which is the reason why the connection exists. Explain why this connection is relevant to the query.")
    strength: float = Field(description="The strength of the connection, which is a float between 0 and 1.")

# Generated graph from user query
class QueryGraph(BaseModel):
    subject: str = Field(description="The subject of the query, which is the name of the person, place, or thing that the user is asking about.")
    connections: Annotated[List[QueryGraphConnection], add]
