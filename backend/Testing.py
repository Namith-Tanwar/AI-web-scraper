"""
Quick manual smoke test for the scrape -> clean -> chunk -> LLM pipeline.
Run locally with: python Testing.py
Requires OPENAI_API_KEY (or LLM_PROVIDER=ollama) set in the environment.
"""
from dotenv import load_dotenv
load_dotenv()

from scraper import scrape_page
from utils import extract_body_only, clean_body, split_dom_content
from llm import parse_with_llm

if __name__ == "__main__":
    url = "https://www.timesjobs.com/job-search?keywords=%22python%22%2C&location=&experience=&refreshed=true"

    print("Scraping page...")
    html = scrape_page(url)

    print("Extracting body...")
    body = extract_body_only(html)

    print("Cleaning text...")
    cleaned = clean_body(body)

    print("Splitting into chunks...")
    chunks = split_dom_content(cleaned)
    print(f"Total chunks created: {len(chunks)}")

    print("Sending chunks to LLM...")
    result = parse_with_llm(chunks, parse_description="all jobs with their salaries")

    print("\n====== FINAL AI OUTPUT ======\n")
    print(result)
