"""Default prompt for ReAct agent."""

from pathlib import Path

# TODO: have formatting instructions be a part of react output parser
with (Path(__file__).parents[0] / Path("system_header_template.md")).open("r") as f:
    __BASE_REACT_CHAT_SYSTEM_HEADER = f.read()

REACT_CHAT_SYSTEM_HEADER = __BASE_REACT_CHAT_SYSTEM_HEADER.replace(
    "{context_prompt}", "", 1
)

CONTEXT_REACT_CHAT_SYSTEM_HEADER = __BASE_REACT_CHAT_SYSTEM_HEADER.replace(
    "{context_prompt}",
    """
Here is some context to help you answer the question and plan:
{context}
""",
    1,
)


with (Path(__file__).parents[0] / Path("router_template.md")).open("r") as f:
    ROUTER_PROMPT = f.read()

with (Path(__file__).parents[0] / Path("answer_template.md")).open("r") as f:
    ANSWER_PROMPT = f.read()

with (Path(__file__).parents[0] / Path("clean_web_text.md")).open("r") as f:
    CLEAN_WEB_TEXT = f.read()

with (Path(__file__).parents[0] / Path("summary_review.md")).open("r") as f:
    SUMMARY_REVIEW = f.read()

with (Path(__file__).parents[0] / Path("summary_description.md")).open("r") as f:
    SUMMARY_DESCRIPTION = f.read()
