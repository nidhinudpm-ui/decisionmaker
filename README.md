# Decision Companion System

A hybrid decision support tool that combines deterministic mathematical scoring with AI-powered data extraction.

## Core Philosophy
This system is designed to be **explainable and objective**. While it uses Large Language Models (LLMs) to read and extract specifications from documents (like car brochures or resumes), the final decision is calculated using a **transparent, non-AI weighted scoring engine**.

## Key Features
- **Deterministic Scoring:** Uses Multi-Criteria Decision Analysis (MCDA) to rank options.
- **AI Extraction (Groq):** Powered by Llama 3.3 70B for high-speed document analysis.
- **Evidence-Backed:** Every score extracted by AI comes with a rationale/quote from the source document.
- **Dynamic Setup:** Users define their own goals, criteria, and importance weights.

## How it Works (The Logic)
1. **Setup:** The user defines a goal and several weighted criteria (e.g., "Price (40%)", "Safety (60%)").
2. **Data Input:** The user adds options and attaches PDFs for each.
3. **AI Extraction:** The system uses Groq to read the PDF and extract numerical values for each criterion.
4. **Normalization:** Since you can't compare "Dollars" to "Star Ratings", the system normalizes all values to a 0-10 scale.
5. **Weighted Total:** The final score is the sum of (Normalized Score × Weight).

## AI Justification & Limitations
**Role of AI:** We use AI exclusively for **parsing unstructured text** into structured data. LLMs are excellent at finding a "Price" or "Battery Life" hidden in a 10-page PDF, which saves the user hours of manual reading.

**Limitations:** 
- AI extraction can occasionally misinterpret complex tables.
- Currently processes the first 8,000 characters of a document (Naive Context).
- **Control:** The user can always override AI scores with manual data if needed.

## Setup
1. Clone the repository.
2. Install dependencies: `pip install -r requirements.txt`.
3. Create a `.env` file and add your `GROQ_API_KEY`.
4. Run the app: `python app.py`.
5. Open `http://127.0.0.1:8080`.
