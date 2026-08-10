import uuid
import traceback
from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI, BackgroundTasks, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

from scraper import scrape_page
from utils import extract_body_only, clean_body, split_dom_content
from llm import parse_with_llm

app = FastAPI(title="AI Web Scraper API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*",
        "https://web-scraper-frontend-production.up.railway.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory job store. Simple and fine for a demo/portfolio deployment;
# a production version would back this with Redis/Postgres so jobs
# survive a restart.
JOBS: dict[str, dict] = {}


class ScrapeRequest(BaseModel):
    url: str
    parse_description: str


def run_scrape_job(job_id: str, url: str, parse_description: str):
    try:
        JOBS[job_id]["status"] = "scraping"
        html = scrape_page(url)

        body = extract_body_only(html)
        cleaned = clean_body(body)

        if not cleaned:
            JOBS[job_id] = {
                "status": "error",
                "error": "No readable content found on that page.",
            }
            return

        chunks = split_dom_content(cleaned)

        JOBS[job_id]["status"] = "parsing"
        result = parse_with_llm(chunks, parse_description)

        JOBS[job_id] = {"status": "done", "result": result}

    except Exception as e:
        traceback.print_exc()
        JOBS[job_id] = {"status": "error", "error": str(e)}


@app.post("/scrape")
def scrape(req: ScrapeRequest, background_tasks: BackgroundTasks):
    job_id = str(uuid.uuid4())
    JOBS[job_id] = {"status": "pending"}

    background_tasks.add_task(
        run_scrape_job, job_id, req.url, req.parse_description
    )

    return {"job_id": job_id}


@app.get("/status/{job_id}")
def get_status(job_id: str):
    job = JOBS.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


@app.get("/health")
def health():
    return {"status": "ok"}
