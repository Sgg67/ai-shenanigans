from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableSequence
from pydantic import BaseModel, Field
from graph.llm import structured, TOOL_NOTE

load_dotenv()


class GradeAnswer(BaseModel):
    """Binary score for whether the answer addresses the question."""

    binary_score: bool = Field(
        description="true if the answer resolves the question, false otherwise"
    )


structured_llm_grader = structured(GradeAnswer)

system = (
    "You grade whether an LLM generation addresses the user's question.\n"
    "Answer true if the generation is a relevant, on-topic attempt to answer the question.\n"
    "Do NOT judge factual accuracy or completeness -- only whether it addresses the "
    "question." + TOOL_NOTE
)

answer_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system),
        ("human", "User question: \n\n {question} \n\n LLM generation: {generation}"),
    ]
)

answer_grader: RunnableSequence = answer_prompt | structured_llm_grader
