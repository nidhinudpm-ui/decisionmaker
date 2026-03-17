from groq import Groq
from flask import current_app
import json

def generate_decision_summary(goal, rankings):
    """
    Generates a high-level comparison summary using the LLM.
    """
    client = Groq(api_key=current_app.config['GROQ_API_KEY'])
    model = current_app.config['GROQ_MODEL_NAME']
    
    # Format rankings for the prompt
    comparison_data = []
    for rank in rankings:
        comparison_data.append({
            "name": rank['name'],
            "score": rank['total_score'],
            "details": rank['rationales']
        })
    
    prompt = f"""
    Based on the following decision goal and rankings, provide a professional 2-3 paragraph comparison summary.
    Identify the clear winner, explain its strengths, and compare it against the runner-ups based on the data provided.
    
    Goal: {goal}
    
    Rankings & Rationales:
    {json.dumps(comparison_data, indent=2)}
    
    Speak directly to the user. Be objective and highlight key trade-offs.
    """
    
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "You are a professional decision advisor. You provide insightful comparisons based on data."
                },
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            model=model
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        print(f"Error generating summary: {e}")
        return "Comparison summary could not be generated at this time."
