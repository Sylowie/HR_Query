import re

def format_llm_reply(text: str) -> str:
    """
    Post-process the LLM reply to make it easier to read:

    - Put bold headings like **Something** on their own lines.
    - Put each bullet (• or *) on its own line.
    - Collapse excessive blank lines.
    """
    if not text:
        return text

    # 1) Headings: bold phrases starting with a capital letter → separate block
    # e.g. "**Supporting Individual Employees...**" or "**Summary**"
    def heading_repl(match: re.Match) -> str:
        heading = match.group(1).strip()
        return f"\n\n**{heading}**\n\n"

    text = re.sub(r"\*\*([A-Z][^*]+?)\*\*", heading_repl, text)

    # 2) Ensure bullets are on their own line
    #    "* text" or "• text" → newline before them
    text = re.sub(r"\s*\*\s+", r"\n* ", text)   # markdown bullets
    text = re.sub(r"\s*•\s+", r"\n• ", text)    # unicode bullets

    # 3) Collapse 3+ newlines into 2
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()
