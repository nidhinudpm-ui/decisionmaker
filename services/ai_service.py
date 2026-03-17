from groq import Groq
from flask import current_app
import json
import re

def get_ai_scores(option_name, document_text, criteria_list):
    """
    Uses Groq LLM to analyze document text and score an option against criteria.
    criteria_list: List of dicts with {id, name, direction, weight}
    """
    client = Groq(api_key=current_app.config['GROQ_API_KEY'])
    model = current_app.config['GROQ_MODEL_NAME']
    
    # Construct the prompt
    criteria_desc = "\n".join([f"- {c['name']} (ID: {c['id']}) - Direction: {c['direction']}" for c in criteria_list])
    
    prompt = f"""
    Analyze the following document for the option "{option_name}".
    Extract raw numerical values or estimates for each of the following criteria.
    ALSO provide a short 1-sentence rationale/evidence for why you gave that score based on the text.
    
    Criteria:
    {criteria_desc}
    
    Document Text:
    {document_text[:8000]}
    
    Return the results EXACTLY as a JSON object with this structure:
    {{
        "scores": {{
            "CRITERION_ID": RAW_VALUE,
            ...
        }},
        "rationales": {{
            "CRITERION_ID": "Evidence found in text...",
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
                    "content": "You are a precise data extraction assistant. You output valid JSON with 'scores' and 'rationales' keys."
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
