from numpy import result_type
from pandas.core.arrays.base import ExtensionArraySupportsAnyAll
import requests
import re
# Ollama details
OLLAMA_HOST = "http://localhost:11434"  # default
OLLAMA_MODEL = "phi3"

def generate_flashcards(content, subject=None):
    system_prompt = (
        "You are a helpful assistant tasked with generating flashcards strictly from the provided content.\n"
        "Only generate questions and answers based on the content—do NOT guess or invent information.\n\n"
        "Instructions:\n"
        "- Generate exactly 5 to 10 flashcards.\n"
        "- Each flashcard should include a concise, factually accurate question and answer.\n"
        "- Format strictly as:\n"
        "1. Question: <your question>\n"
        "   Answer: <a correct, standalone answer>\n\n"
    )

    if subject:
        system_prompt += f"The subject is: {subject}\n"

    # Final prompt with content boundaries
    full_prompt = (
        f"{system_prompt}"
        f"\n--- START OF CONTENT ---\n{content}\n--- END OF CONTENT ---"
    )

    try:
        response = requests.post(
            f"{OLLAMA_HOST}/api/generate",
            json={
                "model": OLLAMA_MODEL,
                "prompt": full_prompt,
                "temperature": 0.2,
                "num_predict": 512,
                "stream": False
            }
        )
        response.raise_for_status()
        return response.json()["response"].strip()

    except Exception as e:
        return f"Error generating flashcards: {e}"
def clean_text(text):
    import re
    # Remove extra spaces and cleanup
    text = re.sub(r"^(Flashcard\s*\d+:|\d+\.)", "", text)
    return text.strip().replace("\n", " ")
def classify_difficulty(word):
    if len(word)<=6:
        return "EASY"
    elif len(word)<=10 :
        return "MEDIUM" 
    else :
        return "HARD"

def parse_flashcards(raw_output):
    """
    Parses flashcards from raw model output with relaxed formatting expectations.
    Supports:
    - Optional numbering (1., Flashcard 1:, etc.)
    - Variations in spacing, colon use, and capitalization
    """

    # Normalize line endings and spacing
    text = raw_output.strip().replace("\r\n", "\n")

    # Pattern explanation:
    # - Accepts optional numbering like "1." or "Flashcard 1:"
    # - Flexible matching of "Question:" and "Answer:" with varied spacing and optional colons
    pattern = r"""
        (?:Flashcard\s*\d+:|\d+\.)?\s*          # Optional "Flashcard 1:" or "1."
        [Qq]uestion[:\s]*                       # "Question" with optional colon/space
        (.*?)                                   # Capture question (non-greedy)
        \n+                                     # One or more newlines
        [Aa]nswer[:\s]*                         # "Answer" with optional colon/space
        (.*?)(?=\n(?:Flashcard\s*\d+:|\d+\.|\Z)) # Capture answer until next flashcard or end
    """

    matches = re.findall(pattern, text, re.DOTALL | re.VERBOSE)

    flashcards = []
    for q, a in matches:
        q = clean_text(q)
        a = clean_text(a)
        if q and a:
            flashcards.append({
                "question": q,
                "answer": a,
                "difficulty": classify_difficulty(q)
            })

    return flashcards
