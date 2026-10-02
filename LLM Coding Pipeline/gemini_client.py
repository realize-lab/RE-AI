# gemini_client.py
import os
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    raise ValueError("GEMINI_API_KEY not found in .env")

# Configure Gemini
genai.configure(api_key=API_KEY)

MODEL_NAME = "gemini-2.5-pro"



def call_gemini(prompt: str, system_instruction: str | None = None) -> str | None:
    """
    Sends a prompt to Gemini and returns the model's text output.

    If the response is blocked by safety filters or contains
    no valid text Part, returns None instead of raising.
    """
    generation_config = {
        "temperature": 0.0,
    }

    if system_instruction:
        print("system instruction")
        model = genai.GenerativeModel(
            model_name=MODEL_NAME,
            system_instruction=system_instruction,
            generation_config=generation_config,
        )
    else:
        model = genai.GenerativeModel(
            model_name=MODEL_NAME,
            generation_config=generation_config,
        )

    # Call the API with explicit safety settings
    response = model.generate_content(
        prompt,
    )

    print("response:", response)

    # If there are no candidates at all, it's almost certainly safety
    candidates = getattr(response, "candidates", None)
    if not candidates:
        # Log some diagnostics so you can see WHY it blocked
        pf = getattr(response, "prompt_feedback", None)
        print("⚠️ Gemini returned no candidates (likely safety blocked).")
        if pf is not None:
            print("   prompt_feedback.block_reason:", getattr(pf, "block_reason", None))
            print("   prompt_feedback.safety_ratings:", getattr(pf, "safety_ratings", None))
        return None

    # Try the quick accessor; if that still fails, treat as blocked
    try:
        return response.text
    except Exception as e:
        print(f"⚠️ Gemini response had no text (possibly safety-blocked): {e}")
        # You can still inspect safety ratings on the first candidate
        try:
            cand = response.candidates[0]
            print("   candidate.finish_reason:", getattr(cand, "finish_reason", None))
            print("   candidate.safety_ratings:", getattr(cand, "safety_ratings", None))
        except Exception:
            pass
        return None
