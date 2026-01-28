from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

from scraper import scrape_page
from utils import extract_body_only, clean_body, split_dom_content
from llm import parse_with_ollama

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],       
    allow_credentials=True,
    allow_methods=["*"],       
    allow_headers=["*"],       
)


class ScrapeRequest(BaseModel):
    url: str
    parse_description: str


@app.post("/scrape")
def scrape(req: ScrapeRequest):
    html = scrape_page(req.url)
    body = extract_body_only(html)
    cleaned = clean_body(body)
    chunks = split_dom_content(cleaned)
    result = parse_with_ollama(chunks, req.parse_description)
    return {"result": result}
