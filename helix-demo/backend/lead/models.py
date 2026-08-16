"""
Structured output schema. The LLM is forced (via LangChain's
`with_structured_output`) to fill this Pydantic model from the free-text
conversation — this is the difference between "a chatbot that talks" and
"a chatbot that feeds clean rows into a CRM".
"""
from typing import Optional, Literal
from pydantic import BaseModel, Field


class LeadProfile(BaseModel):
    name: Optional[str] = Field(None, description="Lead's full name if mentioned")
    company: Optional[str] = Field(None, description="Company or business name if mentioned")
    email: Optional[str] = Field(None, description="Email address if mentioned")
    phone: Optional[str] = Field(None, description="Phone number if mentioned")

    budget_range: Optional[Literal["high", "medium", "low", "unknown"]] = Field(
        None, description="Rough budget signal inferred from the conversation"
    )
    is_decision_maker: Optional[bool] = Field(
        None, description="Whether the lead sounds like the final decision maker"
    )
    need_clarity: Optional[Literal["strong", "moderate", "weak", "unknown"]] = Field(
        None, description="How clear and pressing their business need/pain point is"
    )
    timeline: Optional[Literal["immediate", "this_quarter", "exploring", "unknown"]] = Field(
        None, description="How soon they want to buy/implement"
    )

    summary: str = Field("", description="One-sentence summary of what the lead wants")
    ready_for_handoff: bool = Field(
        False, description="True once enough BANT info has been gathered to hand this to sales"
    )
    next_question: Optional[str] = Field(
        None, description="The single best next question to ask the lead if not ready_for_handoff"
    )
