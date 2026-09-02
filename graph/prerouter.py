"""Zero-LLM-call fast path for classifying obviously-greeting input.

The LLM router costs ~0.7s per question. Greetings are trivially recognizable
with string matching, so we skip the model entirely for them.
"""
import re

GREETINGS = {
    "hi", "hii", "hiya", "hello", "hey", "heya", "yo", "sup", "howdy",
    "good morning", "good afternoon", "good evening", "greetings",
    "hi there", "hello there", "hey there", "whats up", "what's up",
    "how are you", "how's it going", "hows it going",
}

# "what can you do", "who are you", "help", etc. -- answered by the same greeting.
CAPABILITY_PATTERNS = (
    re.compile(r"^\s*(help|start|menu)\s*[!.?]*\s*$", re.I),
    re.compile(r"\b(what|which)\s+(can|do)\s+you\s+(do|help|answer|know)", re.I),
    re.compile(r"\bwho\s+are\s+you\b", re.I),
    re.compile(r"\bwhat\s+are\s+you\b", re.I),
)


def _normalize(text: str) -> str:
    return re.sub(r"[^\w\s']", "", text or "").strip().lower()


def is_greeting(question: str) -> bool:
    """True for greetings and 'what can you do'-style questions."""
    normalized = _normalize(question)
    # Empty or punctuation-only input ("", "?????") -> greeting, which tells the
    # user what the bot does. More useful than a refusal for accidental input.
    if not normalized:
        return True

    if normalized in GREETINGS:
        return True

    # "hi, how many teams are in the NFL?" is a real question, not a greeting --
    # only treat a leading greeting as one when nothing else follows.
    words = normalized.split()
    if len(words) <= 3 and any(normalized.startswith(g) for g in GREETINGS):
        return True

    return any(p.search(question) for p in CAPABILITY_PATTERNS)


# Strong signals that a question is about the NFL. Hitting one of these lets us skip
# the LLM router entirely and go straight to retrieval.
NFL_TERMS = (
    "nfl", "super bowl", "superbowl", "touchdown", "quarterback", "linebacker",
    "field goal", "end zone", "endzone", "punt", "fumble", "interception",
    "american football", "afc", "nfc", "playoff", "pro bowl", "hall of fame",
    "running back", "wide receiver", "tight end", "safety", "cornerback",
    "lineman", "sack", "blitz", "two-point", "extra point", "kickoff",
    "draft", "combine", "preseason", "franchise tag", "gridiron", "scrimmage",
)

TEAMS = (
    "cardinals", "falcons", "ravens", "bills", "panthers", "bears", "bengals",
    "browns", "cowboys", "broncos", "lions", "packers", "texans", "colts",
    "jaguars", "chiefs", "raiders", "chargers", "rams", "dolphins", "vikings",
    "patriots", "saints", "giants", "jets", "eagles", "steelers", "49ers",
    "niners", "seahawks", "buccaneers", "titans", "commanders",
)

# Phrases that indicate an attempt to override instructions. These always go to the
# LLM router (which refuses) -- never to the fast path.
INJECTION_MARKERS = (
    "ignore", "disregard", "forget", "system prompt", "your instructions",
    "you are now", "pretend", "role-play", "roleplay", "act as", "jailbreak",
    "override", "verbatim", "repeat your", "reveal", "bypass", "dan mode",
)


def looks_like_injection(question: str) -> bool:
    lowered = (question or "").lower()
    return any(marker in lowered for marker in INJECTION_MARKERS)


def is_clearly_nfl(question: str) -> bool:
    """True only for unambiguous NFL questions with no injection markers.

    Conservative by design: anything that fails this still goes to the LLM router,
    so a false negative costs latency, never correctness.
    """
    if looks_like_injection(question):
        return False
    lowered = _normalize(question)
    return any(t in lowered for t in NFL_TERMS) or any(t in lowered for t in TEAMS)
