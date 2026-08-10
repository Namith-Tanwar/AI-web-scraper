import os
from langchain_core.prompts import ChatPromptTemplate

LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openai").lower()

template = (
    "You are tasked with extracting specific information from the following text content: {dom_content}. "
    "Please follow these instructions carefully: \n\n"
    "1. **Extract Information:** Only extract the information that directly matches the provided description: {parse_description}. "
    "2. **No Extra Content:** Do not include any additional text, comments, or explanations in your response. "
    "3. **Empty Response:** If no information matches the description, return an empty string (''). "
    "4. **Direct Data Only:** Your output should contain only the data that is explicitly requested, with no other text."
)


def _build_model():
    if LLM_PROVIDER == "ollama":
        from langchain_ollama import OllamaLLM
        return OllamaLLM(model=os.getenv("OLLAMA_MODEL", "llama3.1"))

    # default: OpenAI
    from langchain_openai import ChatOpenAI
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError(
            "OPENAI_API_KEY is not set. Set it as an environment variable, "
            "or set LLM_PROVIDER=ollama to use a local model instead."
        )
    return ChatOpenAI(
        model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        api_key=api_key,
        temperature=0,
    )


def parse_with_llm(dom_chunks, parse_description):
    model = _build_model()
    prompt = ChatPromptTemplate.from_template(template)
    chain = prompt | model

    parsed_result = []

    for i, chunk in enumerate(dom_chunks, start=1):
        response = chain.invoke(
            {"dom_content": chunk, "parse_description": parse_description}
        )
        # OllamaLLM returns a plain string; ChatOpenAI returns a message object
        text = response.content if hasattr(response, "content") else response

        print(f"parsed batch {i} of {len(dom_chunks)}")
        parsed_result.append(text)

    return "\n".join(r for r in parsed_result if r and r.strip())
