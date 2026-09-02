from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableSequence
from pydantic import BaseModel, Field
from graph.llm import structured, TOOL_NOTE

load_dotenv()


class GradeHallucinations(BaseModel):
    """Binary score for hallucinations present in the generation answer."""

    binary_score: bool = Field(
        description="true if the generation is grounded in / supported by the facts, "
        "false otherwise"
    )


structured_llm_grader = structured(GradeHallucinations)

system = (
    "You are a grader assessing whether an LLM generation is grounded in / supported by "
    "a set of documents.\n"
    "Give a binary score: true means the answer is grounded in / supported by the set "
    "of facts." + TOOL_NOTE
)

hallucination_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system),
        ("human", "Set of facts: \n\n {documents} \n\n LLM generation: {generation}"),
    ]
)

hallucination_grader: RunnableSequence = hallucination_prompt | structured_llm_grader
