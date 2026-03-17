from groq import Groq
from flask import current_app
import json
import re

def get_ai_scores(option_name, criteria_list, doc_context=None):
    """
    Uses Groq LLM to analyze document text (if provided) or use internal knowledge
    to score an option against criteria.
    """
    client = Groq(api_key=current_app.config['GROQ_API_KEY'])
    model = current_app.config['GROQ_MODEL_NAME']
    
    # Construct the prompt
    criteria_desc = "\n".join([f"- {c['name']} (ID: {c['id']}) - Direction: {c['direction']}" for c in criteria_list])
    
    context_part = f"Document Context:\n{doc_context}\n" if doc_context else "No document provided. Use your internal general knowledge to estimate values for this well-known option."
    
    prompt = f"""
    Analyze the following for the option "{option_name}".
    Extract or estimate raw numerical values for each of the criteria below.
    ALSO provide a short 1-sentence rationale/evidence for why you gave that score.
    
    {context_part}
    
    Criteria:
    {criteria_desc}
    
    Return the results EXACTLY as a JSON object with this structure:
    {{
        "scores": {{
            "CRITERION_ID": RAW_VALUE,
            ...
        }},
        "rationales": {{
            "CRITERION_ID": "Detailed reason...",
            ...
        }}
    }}
    Do not include any other text in your response.
    """
    
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "You are a precise data extraction and estimation assistant. You output valid JSON with 'scores' and 'rationales' keys."
                },
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            model=model,
            response_format={"type": "json_object"}
        )
        
        response_text = chat_completion.choices[0].message.content
        return json.loads(response_text)
    except Exception as e:
        print(f"Error calling Groq: {e}")
        return None
