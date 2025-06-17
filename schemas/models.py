from pydantic import BaseModel, Field
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

class QueryGraphConnection(BaseModel):
    connection_name: str = Field(description="The name of the connection, which may be a name, an object, a place, etc.")
    source: str = Field(description="The source of the connection, which is the document name and page number.")
    reasoning: str = Field(description="The reasoning of the connection, which is the reason why the connection exists. Explain why this connection is relevant to the query.")
    strength: float = Field(description="The strength of the connection, which is a float between 0 and 1.")

# Generated graph from user query
class QueryGraph(BaseModel):
    subject: str = Field(description="The subject of the query, which is the name of the person, place, or thing that the user is asking about.")
    connections: Annotated[List[QueryGraphConnection], add]
