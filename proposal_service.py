# proposal_service.py
import os
import json
import re
from dotenv import load_dotenv
from google import genai  # Ensure your module and API key are correctly set up

load_dotenv()  # Load variables from .env file

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
try:
    MAX_PROMPT_LENGTH = int(os.getenv("MAX_PROMPT_LENGTH", "1000"))
except ValueError:
    MAX_PROMPT_LENGTH = 1000
try:
    MAX_TOKEN_LIMIT = int(os.getenv("MAX_TOKEN_LIMIT", "250"))
except ValueError:
    MAX_TOKEN_LIMIT = 250

SECTION_PROMPT_TEMPLATE = os.getenv(
    "SECTION_PROMPT_TEMPLATE",
    "Consultancy Firm: {firm}\nClient: {client}\nProduct: {product}\nProposal Date: {proposal_date}\n\nGuidelines for '{section_name}': Provide a concise summary.\n\nGenerate the final draft for the '{section_name}' section of the proposal for the above product. Output only the final polished summary in approximately 150 words. Do NOT include any chain-of-thought, intermediate reasoning, filler phrases, or meta commentary. Provide a clear, direct, and professional summary containing only the essential key points."
)

def clean_output(text):
    """
    Remove filler phrases and chain-of-thought artifacts from the generated output.
    """
    fillers = [
        "Okay, let's craft",
        "I understand",
        "Based on the provided context",
        "Here's what I can infer",
        "I will focus on",
        "Please provide the",
        "Draft",
        "Chain-of-thought:",
        "intermediate steps",
        "**Acceptance of Proposal** ",
        "**Executive Summary** ",
        "**About Us** ",
        "**Understanding the Client’s Needs** ",
        "**Scope of Work** ",
        "**Deliverables** ",
        "**Timeline** ",
        "**Pricing and Payment Terms** ",
        "**Client Responsibilities** ",
        "**Confidentiality & Compliance** ",
        "**Terms & Conditions** ",
        "Executive Summary",
        "About Us",
        "Understanding the Client’s Needs",
        "Scope of Work",
        "Deliverables",
        "Timeline",
        "Pricing and Payment Terms",
        "Client Responsibilities",
    ]
    for phrase in fillers:
        text = text.replace(phrase, "")
    return re.sub(r'\s+', ' ', text).strip()

def split_prompt(prompt, max_chars=MAX_PROMPT_LENGTH):
    parts = []
    sentences = re.split(r'([.?!\n])', prompt)
    current_part = ""
    for sentence in sentences:
        if len(current_part) + len(sentence) > max_chars:
            if current_part:
                parts.append(current_part)
            current_part = sentence
        else:
            current_part += sentence
    if current_part:
        parts.append(current_part)
    return parts

def gemini_completion(prompt, max_tokens=MAX_TOKEN_LIMIT, temperature=0.5):
    client = genai.Client(api_key=GEMINI_API_KEY)
    def call_api(segment):
        response = client.models.generate_content(
            model="gemini-2.0-flash-thinking-exp-01-21",
            contents=segment
        )
        return response.text.strip() if response.text else "Error generating response."
    if len(prompt) > MAX_PROMPT_LENGTH:
        segments = split_prompt(prompt)
        results = [call_api(seg) for seg in segments]
        return "\n".join(results)
    else:
        return call_api(prompt)

def generate_section_content(section_name, firm, client_name, product, proposal_date, default_guideline):
    """
    Generate the final polished summary for a given section.
    The output (approximately 150 words) will contain only the key points.
    """
    guidelines = os.getenv("SECTION_GUIDELINES")
    if guidelines:
        try:
            guidelines = json.loads(guidelines)
        except Exception:
            guidelines = {}
    else:
        guidelines = {}
    # Use the specific guideline if available, otherwise default.
    guideline = guidelines.get(section_name, default_guideline)
    
    prompt = SECTION_PROMPT_TEMPLATE.format(
        firm=firm,
        client=client_name,
        product=product,
        proposal_date=proposal_date,
        section_name=section_name,
        guideline=guideline
    )
    raw_output = gemini_completion(prompt)
    return clean_output(raw_output)

# Default slide mapping (used for PPT generation)
slide_section_mapping = {
    1: "Executive Summary",
    2: "About Us",
    3: "Understanding the Client’s Needs",
    4: "Scope of Work",
    5: "Deliverables",
    6: "Timeline",
    7: "Pricing and Payment Terms",
    8: "Client Responsibilities",
    9: "Confidentiality & Compliance",
    10: "Terms & Conditions",
    11: "Acceptance of Proposal"
}

if __name__ == "__main__":
    # Simple test of generate_section_content for a given section
    test = generate_section_content("Executive Summary", "Test Firm", "Test Client", "Test Product", "01-01-2025", "Default guideline")
    print(test)
