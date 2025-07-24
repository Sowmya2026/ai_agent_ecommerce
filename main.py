
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from datetime import datetime
import uuid
import os
import json
import csv

from query_llm import ask_llm_gemini
from sql_utils import run_query

app = FastAPI()
templates = Jinja2Templates(directory="templates")

chat_sessions = {}

@app.get("/", response_class=HTMLResponse)
def read_form(request: Request):
    session_id = str(uuid.uuid4())
    chat_sessions[session_id] = []
    return templates.TemplateResponse("index.html", {"request": request, "session_id": session_id, "history": []})

@app.post("/ask", response_class=HTMLResponse)
def ask_question(request: Request, session_id: str = Form(...), question: str = Form(...)):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    llm_output = ask_llm_gemini(question)
    sql = llm_output.get("sql", "")
    explanation = llm_output.get("explanation", "")
    result = run_query(sql)

    chart_data = None
    chart_type = "bar"
    if isinstance(result, list) and result and isinstance(result[0], dict):
        keys = list(result[0].keys())
        if len(keys) == 2:
            x_vals = [row[keys[0]] for row in result]
            y_vals = [row[keys[1]] for row in result]
            if all(isinstance(y, (int, float)) for y in y_vals):
                chart_data = {
                    "labels": x_vals,
                    "values": y_vals,
                    "label": keys[1]
                }
                if len(set(x_vals)) <= 5:
                    chart_type = "pie"

    chat_sessions[session_id].append({
        "question": question,
        "sql": sql,
        "explanation": explanation,
        "result": result,
        "time": timestamp,
        "chart_data": chart_data,
        "chart_type": chart_type
    })

    return templates.TemplateResponse("index.html", {
        "request": request,
        "session_id": session_id,
        "history": chat_sessions[session_id][::-1]
    })

@app.post("/clear")
def clear_session(request: Request, session_id: str = Form(...)):
    chat_sessions[session_id] = []
    return templates.TemplateResponse("index.html", {
        "request": request,
        "session_id": session_id,
        "history": []
    })

@app.post("/export")
def export_session(session_id: str = Form(...)):
    session_data = chat_sessions.get(session_id, [])
    if not session_data:
        return {"error": "No chat history found."}

    export_folder = "exports"
    os.makedirs(export_folder, exist_ok=True)

    json_path = os.path.join(export_folder, f"{session_id}.json")
    with open(json_path, "w") as jf:
        json.dump(session_data, jf, indent=2)

    csv_path = os.path.join(export_folder, f"{session_id}.csv")
    with open(csv_path, "w", newline="", encoding="utf-8") as cf:
        writer = csv.DictWriter(cf, fieldnames=["time", "question", "sql", "explanation"])
        writer.writeheader()
        for row in session_data:
            writer.writerow({
                "time": row["time"],
                "question": row["question"],
                "sql": row["sql"],
                "explanation": row["explanation"]
            })

    return FileResponse(json_path, media_type='application/json', filename=f"{session_id}.json")

