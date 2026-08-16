"""
Deterministic BANT-based lead scoring.

Deliberately kept as plain, explainable rules rather than "ask the LLM for a
score" — sales teams need to trust and audit why a lead was marked hot, and
rule-based scoring is easy to tune without re-prompting.

BANT = Budget, Authority, Need, Timeline.
"""
from backend.lead.models import LeadProfile


def score_lead(lead: LeadProfile) -> int:
    score = 0

    # Budget
    if lead.budget_range in ("high", "medium"):
        score += 25
    elif lead.budget_range == "low":
        score += 10

    # Authority (is this person the decision maker?)
    if lead.is_decision_maker is True:
        score += 25
    elif lead.is_decision_maker is None:
        score += 10

    # Need (how clear/strong is the pain point?)
    if lead.need_clarity == "strong":
        score += 25
    elif lead.need_clarity == "moderate":
        score += 15
    elif lead.need_clarity == "weak":
        score += 5

    # Timeline
    if lead.timeline == "immediate":
        score += 25
    elif lead.timeline == "this_quarter":
        score += 15
    elif lead.timeline == "exploring":
        score += 5

    return min(score, 100)


def classify(score: int, threshold: int) -> str:
    if score >= threshold:
        return "hot"
    if score >= threshold - 30:
        return "warm"
    return "cold"
