from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import (create_engine, Column, Integer, DateTime,
                        String, Text, ForeignKey)
from sqlalchemy.orm import sessionmaker, declarative_base, Session, relationship
import datetime, json, os, uuid
from typing import List, Dict

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_URL   = f"sqlite:///{os.path.join(BASE_DIR,'responses.db')}"
engine   = create_engine(DB_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autoflush=False)
Base = declarative_base()

class Pair(Base):
    __tablename__ = "pairs"
    id            = Column(Integer, primary_key=True, index=True)
    token_creator = Column(String, unique=True, index=True)
    token_target  = Column(String, unique=True, index=True)
    created_at    = Column(DateTime, default=datetime.datetime.utcnow)
    responses     = relationship("Response", back_populates="pair")

class Response(Base):
    __tablename__ = "responses"
    id          = Column(Integer, primary_key=True, index=True)
    pair_id     = Column(Integer, ForeignKey("pairs.id"))
    role        = Column(String)  # 'creator' or 'target'
    timestamp   = Column(DateTime, default=datetime.datetime.utcnow)
    target_name = Column(String(120))
    answers     = Column(Text)  # JSON blob
    pair        = relationship("Pair", back_populates="responses")

Base.metadata.create_all(bind=engine)

# Load static questions once
with open("questions.json", encoding="utf-8") as f:
    QUESTIONS = json.load(f)

MESSAGE_MAP = {
    "A1": ("Same vibe",                "You and your partner see the connection at the same level."),
    "A2": ("Trust level",              "You both feel the same level of trust for sharing secrets."),
    "A3": ("Support system",           "You both seek each other's support in similar ways."),
    "A4": ("Comfortable touch",        "You agree on the amount of physical contact right now."),
    "A5": ("Social circle",            "You both have similar views on introducing each other to friends/family."),
    "A6": ("Conflict style",           "You handle disagreements in a similar way."),
    "A7": ("Shared activities",        "You both have similar levels of shared routines."),
    "B1": ("More hangouts!",           "You both want to spend more one-on-one time together."),
    "B2": ("Define the relationship",  "Both of you would like a clearer, more solid label."),
    "B3": ("Deeper talks",             "You're ready to share deeper feelings."),
    "B4": ("Extra hugs 🙌",            "More hugging or hand-holding sounds good to both of you."),
    "B5": ("Date time ❤️",             "You're both open to going on dates."),
    "B6": ("Kiss vibes 💋",            "If it feels mutual, you'd both enjoy a kiss."),
    "B7": ("Future intimacy",          "You're both okay exploring sexual intimacy later."),
    "B8": ("Meet the circle",          "Introducing each other to close friends or family feels right."),
    "B9": ("Adventure duo",            "Planning a trip or project together excites both of you."),
    "B10": ("Roomies someday?",        "Living under one roof is on both your minds.")
}

app = FastAPI()
templates = Jinja2Templates(directory="templates")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ---------------------- UTIL: simple matching ----------------------
YES = {"Yes", "Maybe"}             # positive answers for Section B

def load_answers(resp: Response):
    return json.loads(resp.answers)

def intersect_answers(r1: Response, r2: Response) -> List[Dict]:
    """Compare answers between two responses and return matching insights."""
    matches = []
    answers1 = json.loads(r1.answers)
    answers2 = json.loads(r2.answers)
    
    for q_code in answers1:
        # Skip if question not in both responses
        if q_code not in answers2:
            continue
            
        v1 = answers1[q_code]
        v2 = answers2[q_code]
        
        # Skip if either person skipped the question
        if v1 == "Skip" or v2 == "Skip":
            continue
            
        # Skip if either answer is None or empty
        if not v1 or not v2:
            continue
            
        # Only add to matches if both answered the same way
        if v1 == v2 and q_code in MESSAGE_MAP:
            title, body = MESSAGE_MAP[q_code]
            matches.append({"title": title, "body": body})
            
    return matches
# -------------------------------------------------------------------

@app.get("/", response_class=RedirectResponse)
def root():
    return "/survey/form"

# ---------- CREATOR ----------
@app.get("/survey/form")
def show_creator_form(request: Request):
    return templates.TemplateResponse("form.html",
                                      {"request": request, "questions": QUESTIONS})

@app.post("/survey/submit")
async def submit_creator(request: Request, db: Session = Depends(get_db)):
    form = await request.form()
    target = form["target_name"]
    answers = {q["code"]: form.get(q["code"]) for q in QUESTIONS}

    # create pair + tokens
    t_creator = uuid.uuid4().hex
    t_target  = uuid.uuid4().hex
    pair = Pair(token_creator=t_creator, token_target=t_target)
    db.add(pair); db.flush()  # get pair.id

    db.add(Response(pair_id=pair.id, role="creator",
                    target_name=target, answers=json.dumps(answers)))
    db.commit()

    share_url   = f"/fill/{t_target}"
    result_url  = f"/result/{t_creator}"
    return templates.TemplateResponse("share.html",
            {"request": request, "share_url": share_url, "result_url": result_url})

# ---------- TARGET ----------
@app.get("/fill/{token}")
def show_target_form(token: str, request: Request, db: Session = Depends(get_db)):
    pair = db.query(Pair).filter(Pair.token_target == token).first()
    if not pair:
        raise HTTPException(404)
    return templates.TemplateResponse("form.html",
            {"request": request, "questions": QUESTIONS,
             "token": token})   # hidden field added via Jinja

@app.post("/fill/{token}")
async def submit_target(token: str, request: Request, db: Session = Depends(get_db)):
    pair = db.query(Pair).filter(Pair.token_target == token).first()
    if not pair:
        raise HTTPException(404)
    form = await request.form()
    target = form["target_name"]
    answers = {q["code"]: form.get(q["code"]) for q in QUESTIONS}
    db.add(Response(pair_id=pair.id, role="target",
                    target_name=target, answers=json.dumps(answers)))
    db.commit()
    return RedirectResponse(f"/result/{token}", status_code=303)

# ---------- RESULT ----------
@app.get("/result/{token}")
def show_result(token: str, request: Request, db: Session = Depends(get_db)):
    # token may be creator or target
    pair = db.query(Pair).filter((Pair.token_creator==token)|(Pair.token_target==token)).first()
    if not pair:
        raise HTTPException(404)
    if len(pair.responses) < 2:
        return templates.TemplateResponse("waiting.html", {"request": request, "token": token})
    r1, r2 = pair.responses
    matches = intersect_answers(r1, r2)
    
    # Determine which token is the partner's
    partner_token = pair.token_target if token == pair.token_creator else pair.token_creator
    
    return templates.TemplateResponse("result.html",
            {"request": request, "matches": matches, "token": token, "partner_token": partner_token}) 