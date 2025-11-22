import re
from db_functions import insert_summary, insert_sentiment, get_group_messages,get_group_title_by_id
from datetime import timedelta, datetime
from .ollama_query import query_ollama

async def generate_multiple_analysis(group_ids: list[int]):
    results = []
    for group_id in group_ids:
        group_title = await get_group_title_by_id(group_id)
        if group_title:
            try:
                await generate_analysis(group_id, group_title, "1 week")
                results.append((group_id, "Success"))
            except Exception as e:
                results.append((group_id, "Failed"))
        else:
            results.append((group_id, "No Title"))

    return results

def partition_analysis(response_text: str):
    summary_match = re.search(r'\*\*1\.\s*Group Summary:\*\*\s*(.*?)(?=\n\*\*2)', response_text, re.DOTALL)
    sentiment_match = re.search(r'\*\*2\.\s*Overall Mood:\*\*\s*(.*?)(?=\n\*\*3)', response_text, re.DOTALL)
    marketing_match = re.search(r'\*\*3\.\s*Brand/Products Popularity Assessment:\*\*\s*(.*)', response_text, re.DOTALL)

    summary = summary_match.group(1).strip() if summary_match else "No summary available."
    sentiment_tone = sentiment_match.group(1).strip() if sentiment_match else "NIL"
    marketing_potential = marketing_match.group(1).strip() if marketing_match else "No marketing insights provided."

    return summary, sentiment_tone, marketing_potential

async def generate_analysis(group_id: int, group_title: str, date_range: str):
    today = datetime.strptime(get_datetime(), "%Y-%m-%d %H:%M:%S")
    if date_range == "1 week":
        start_date = today - timedelta(weeks=1)
    elif date_range == "1 month":
        start_date = today - timedelta(days=30)
    elif date_range == "3 months":
        start_date = today - timedelta(days=90)
    else:
        start_date = today - timedelta(weeks=1)

    messages = await get_group_messages(10, group_id, start_date)

    if not messages:
        return

    combined_messages = "\n".join(messages)

    response_text = query_ollama(group_title, combined_messages)

    summary, sentiment_tone, marketing_potential = partition_analysis(response_text)

    await insert_summary({
        "group_id": group_id,
        "curr_date": get_datetime(),
        "summary": summary
    })

    await insert_sentiment({
        "group_id": group_id,
        "curr_date": get_datetime(),
        "sentiment_tone": sentiment_tone,
        "marketing_potential": marketing_potential
    })

    return True
