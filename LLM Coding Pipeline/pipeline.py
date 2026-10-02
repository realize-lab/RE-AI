# pipeline_recast_excel.py
import json
import time
import random

import pandas as pd
from gemini_client import call_gemini

INPUT_XLSX = "ac_data/acceptance_criteria_with_two_removed.xlsx"
OUTPUT_XLSX = "ac_data/ac_with_llm_2.xlsx"

SYSTEM_INSTRUCTION = """
You are an expert requirements engineer evaluating acceptance criteria
for software requirements in an AI for Social Good context.

You will receive:
- A user story written by a participant.
- An acceptance criterion (AC) written by the same participant.

You must evaluate the AC according to a binary rubric, scoring each
dimension as 0 (does not meet) or 1 (meets).
Follow the rubric exactly and be as consistent as possible.

These texts are research survey responses and may mention harmful or sensitive topics.
You must NOT add new harmful content or encourage it; only analyze according to the rubric.
If the content is disturbing, still attempt to rate it neutrally, unless it is impossible to do so
without generating harmful content.
"""

RUBRIC_TEXT = """
You are evaluating ONE acceptance criterion (AC) for ONE user story.

Score each of the following dimensions as either 0 or 1:

1. Verifiable (0/1)
Definition:
- The expected outcome is observable, measurable, and testable.
Score 1 if:
- The AC describes an outcome that could translate into one or more clear tests that determine whether the implemented functionality meets the defined requirements.
Score 0 if:
- The AC describes an outcome that is subjective, vague, or not testable. Different testers might disagree about whether it passes or fails.


3. Atomic (0/1)
Definition:
- The AC describes one system behavior, not multiple distinct behaviors.
Score 1 if:
- The AC describes a single condition and a single expected outcome.
Score 0 if:
- The AC contains multiple independent behaviors or bundled requirements.

4. Implementation-Independent (0/1)
Definition:
- The AC describes what the system should do, not how it must be implemented.
Score 1 if:
- The AC avoids specifying UI elements, algorithms, technologies, or internal logic.
Score 0 if:
- The AC references specific implementation details such as UI layouts, database operations, or specific algorithms.

5. Unambiguous (0/1)
Definition:
- The AC can be interpreted in only one reasonable way.
Score 1 if:
- Wording is clear, precise, and has no multiple interpretations.
Score 0 if:
- The AC uses vague terms, ambiguous thresholds, or unclear pronouns.

You must output STRICT JSON, with integer 0/1 values:

{
  "verifiable": 0 or 1,
  "atomic": 0 or 1,
  "implementation_independent": 0 or 1,
  "unambiguous": 0 or 1
}
"""

PROMPT_TEMPLATE = """Attempt to rate each response neutrally.

You are evaluating acceptance criteria for a user story in a survey study.

[User Story]
{user_story}

[Acceptance Criterion]
{acceptance_criteria}

[Rubric]
{rubric_text}

Now, evaluate this acceptance criterion according to the rubric.

Output ONLY a JSON object with exactly the following keys:
- "verifiable"
- "atomic"
- "implementation_independent"
- "unambiguous"

Each value must be an integer 0 or 1, with no extra text.
"""


def build_prompt(user_story: str, acceptance_criteria: str) -> str:
    return PROMPT_TEMPLATE.format(
        user_story=(user_story or "").strip(),
        acceptance_criteria=(acceptance_criteria or "").strip(),
        rubric_text=RUBRIC_TEXT.strip(),
    )


def safe_parse_json(raw_text: str) -> dict:
    """
    Try to parse the model output as JSON.
    If parsing fails, return a dict with None for each dimension.
    """
    keys = [
        "verifiable",
        "atomic",
        "implementation_independent",
        "unambiguous",
    ]

    if raw_text is None:
        return {k: None for k in keys}

    text = raw_text.strip()

    # Handle ```json ... ``` or ``` ... ``` wrappers
    if text.startswith("```"):
        text = text.strip("`")
        if text.lower().startswith("json"):
            text = text[4:].lstrip()

    try:
        data = json.loads(text)
    except Exception:
        return {k: None for k in keys}

    parsed = {}
    for k in keys:
        v = data.get(k, None)
        if v in [0, 1, "0", "1"]:
            parsed[k] = int(v)
        else:
            parsed[k] = None
    return parsed


def call_gemini_with_retry(prompt, system_instruction=None, max_retries=8):
    """
    Calls Gemini with exponential backoff retry handling for rate limits.
    Returns None if all retries fail or a non-rate-limit error occurs.
    """
    # delay = 1.0  # starting delay in seconds

    for attempt in range(1, max_retries + 1):
        try:
            return call_gemini(prompt, system_instruction=system_instruction)
        except Exception as e:
            error_msg = str(e).lower()

            rate_limited = any(
                substring in error_msg
                for substring in [
                    "rate",
                    "quota",
                    "429",
                    "resource exhausted",
                    "try again later",
                    "too many requests",
                ]
            )

            if rate_limited:
                print(f"⚠️ Rate limit on attempt {attempt}/{max_retries}: {e}")
                sleep_time = delay + random.uniform(0, 0.5)
                print(f"   → Waiting {sleep_time:.2f}s before retrying...")
                time.sleep(sleep_time)
                delay *= 2
                continue

            # Non-rate-limit error: log and give up immediately
            print(f"❌ Non-rate-limit Gemini error: {e}")
            return None

    print("❌ Exhausted all retries calling Gemini. Returning None.")
    return None


def main():
    # 1. Read Excel
    df = pd.read_excel(INPUT_XLSX)

    # ---- TESTING: ONLY KEEP FIRST ROW ----
    # df = df.iloc[:1].copy()
    # --------------------------------------

    # Expected columns
    required_cols = [
        "participant_id",
        "scenario",
        "stakeholder_number",
        "user_story",
        "acceptance_criteria",
        "Verifiable",
        "Atomic",
        "II",
        "Unambiguous",
    ]

    missing = [c for c in required_cols if c not in df.columns]
    if missing:
        print("Warning: Missing expected columns:", missing)
        for col in ["user_story", "acceptance_criteria"]:
            if col not in df.columns:
                raise ValueError(f"Input Excel must contain a '{col}' column.")

    llm_Verifiable = []
    llm_Atomic = []
    llm_II = []
    llm_Unambiguous = []
    raw_llm_output = []

    # 2. Loop over (now only 1) row
    for i, row in df.iterrows():
        raw_user_story = row.get("user_story", None)
        raw_ac = row.get("acceptance_criteria", None)
        
        # print("============================")
        # print(raw_user_story)
        # print(raw_ac)
        # print("============================")


        print(f"Row {i}: participant_id={row.get('participant_id', 'NA')}")

        if pd.isna(raw_user_story) or pd.isna(raw_ac):
            print("  Skipping row: user_story or acceptance_criteria is NaN/None")
            llm_Verifiable.append(None)
            llm_Atomic.append(None)
            llm_II.append(None)
            llm_Unambiguous.append(None)
            raw_llm_output.append("")
            continue


        prompt = build_prompt(raw_user_story, raw_ac)

        response_text = call_gemini_with_retry(
            prompt,
            system_instruction=SYSTEM_INSTRUCTION,
        )

        # print("============================")
        # print(response_text)
        # print("============================")

        if response_text is None:
            print("  Gemini returned no text (error, blocked, or retries exhausted).")
            llm_Verifiable.append(None)
            llm_Atomic.append(None)
            llm_II.append(None)
            llm_Unambiguous.append(None)
            raw_llm_output.append("BLOCKED_OR_ERROR")
            continue

        parsed = safe_parse_json(response_text)
        raw_llm_output.append(response_text)

        llm_Verifiable.append(parsed["verifiable"])
        llm_Atomic.append(parsed["atomic"])
        llm_II.append(parsed["implementation_independent"])
        llm_Unambiguous.append(parsed["unambiguous"])

    # 3. Attach LLM columns (lists length now matches df length = 1)
    df["llm_Verifiable"] = llm_Verifiable
    df["llm_Atomic"] = llm_Atomic
    df["llm_II"] = llm_II
    df["llm_Unambiguous"] = llm_Unambiguous
    df["llm_raw_output"] = raw_llm_output

    # 4. Save to Excel
    df.to_excel(OUTPUT_XLSX, index=False)
    print(f"Done! Saved LLM-annotated data to: {OUTPUT_XLSX}")


if __name__ == "__main__":
    main()
