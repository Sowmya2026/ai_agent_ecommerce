import google.generativeai as genai
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=api_key)
model = genai.GenerativeModel(model_name="models/gemini-1.5-flash")

def ask_llm_gemini(question: str) -> dict:
    prompt = f"""
You are an assistant that generates SQL queries for SQLite based on user questions.
Assume the following tables exist:

- total_sales(date TEXT, item_id INTEGER, total_sales REAL, total_units_ordered INTEGER)
- ad_sales(date TEXT, item_id INTEGER, ad_sales REAL, impressions INTEGER, ad_spend REAL, clicks INTEGER, units_sold INTEGER)
- eligibility(eligibility_datetime_utc TEXT, item_id INTEGER, eligibility TEXT, message TEXT)

Step 1: Convert the user's question into a valid SQL query.
Step 2: Respond with both:
- The SQL query
- A short human-readable explanation of what the query does.

Format:
SQL: <the SQL>
Explanation: <the explanation>

Question: {question}
"""
    try:
        response = model.generate_content(prompt)
        raw_output = response.text.strip()

        sql = ""
        explanation = ""
        if "SQL:" in raw_output and "Explanation:" in raw_output:
            parts = raw_output.split("Explanation:")
            sql = parts[0].replace("SQL:", "").strip()
            explanation = parts[1].strip()
        else:
            sql = raw_output.strip()

        if sql.startswith("```sql"):
            sql = sql.replace("```sql", "").replace("```", "").strip()

        return {"sql": sql, "explanation": explanation}
    except Exception as e:
        return {"sql": "-- Error from Gemini API", "explanation": str(e)}
