from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from graph.llm import structured, TOOL_NOTE

load_dotenv()


class GradeDocuments(BaseModel):
    """Binary score for relevance check on retrieved documents."""

    binary_score: str = Field(
        description="Must be exactly 'yes' or 'no'. 'yes' if the document is relevant "
        "to the question, 'no' if it is not."
    )


structured_llm_grader = structured(GradeDocuments)

system = (
    "You are a grader assessing the relevance of a retrieved document to a user question.\n"
    "If the document contains keywords or semantic meaning related to the question, "
    "grade it as relevant.\n"
    "Give a binary score of exactly 'yes' or 'no'." + TOOL_NOTE
)

grade_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system),
        ("human", "Retrieved document: \n\n {document} \n\n User Question: {question}"),
    ]
)

retrieval_grader = grade_prompt | structured_llm_grader
