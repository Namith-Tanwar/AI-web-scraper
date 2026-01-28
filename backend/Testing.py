from scraper import scrape_page
from utils import extract_body_only, clean_body, split_dom_content
from llm import parse_with_ollama

if __name__ == "__main__":
    url = "https://www.timesjobs.com/job-search?keywords=%22python%22%2C&location=&experience=&refreshed=true"

    print("Scraping page...")
    html = scrape_page(url)
    print(html)

    print("Extracting body...")
    body = extract_body_only(html)
    print(body)

    print("Cleaning text...")
    cleaned = clean_body(body)
    print(cleaned)
    print("Splitting into chunks...")
    chunks = split_dom_content(cleaned)

    print(f"Total chunks created: {len(chunks)}")

    print("Sending chunks to LLM...")
    result = parse_with_ollama(
        chunks,
        parse_description="all jobs with their salaries"
    )

    print("\n====== FINAL AI OUTPUT ======\n")
    print(result)
