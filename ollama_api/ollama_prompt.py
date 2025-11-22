import os
import ollama
from collections import defaultdict
import sys

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, parent_dir)

from misc_functions import *

MODEL = 'llama3.1'

def query_ollama(group, combined_messages):
    if not combined_messages:
        return "No messages available."

    prompt = f"""
    You are an SOCMINT analyst analyzing a community chat group titled **"{group}"**. Based on the messages provided below, please perform the following:

    1. **Group Summary**  
    # Provide a concise summary of the group's main discussions and focus.  

    2. **Overall Mood**  
    Indicate the general tone of the messages: Positive, Neutral, or Negative.

    3. **Brand/Products Popularity Assessment**  
    - Assess whether specific brands, services, or products are being discussed frequently.  
    - Identify which types of products or services are most relevant to this group's interests.  
    - Recommend suitable groups or platforms for marketing.  
    - Suggest the best timing for campaigns.

    Use the following exact format for your response (do not deviate from it):

    **1. Group Summary:** <summary text>

    **2. Overall Mood:** <Positive/Neutral/Negative>

    **3. Brand/Products Popularity Assessment:** <marketing insights>

    ---

    Messages:
    {combined_messages}
    """

    try:
        response = ollama.chat(model=MODEL, messages=[
        {"role": "user", "content": prompt}
        ])
        response_text = response.get("message", {}).get("content", "No response received")
        return response_text
    except Exception as e:
        return "Error querying Ollama."
		
		
		
		from misc_functions import *
