from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import sqlite3

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


def init_db():
    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS votes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            reg_id TEXT UNIQUE,
            count INTEGER
        )
    """)
    candidates = ["CAND_A", "CAND_B", "CAND_C", "CAND_D", "CAND_E"]
    for reg_id in candidates:
        c.execute("INSERT OR IGNORE INTO votes (reg_id, count) VALUES (?, ?)", (reg_id, 0))
    conn.commit()
    conn.close()

init_db()


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute("SELECT reg_id, count FROM votes")
    votes = c.fetchall()
    conn.close()
    return templates.TemplateResponse("index.html", {"request": request, "votes": votes})


@app.post("/vote")
async def vote(option: str = Form(...)):
    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute("UPDATE votes SET count = count + 1 WHERE reg_id = ?", (option,))
    conn.commit()
    c.execute("SELECT reg_id, count FROM votes")
    votes = c.fetchall()
    conn.close()
    return JSONResponse({"votes": votes})
