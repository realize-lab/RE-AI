# pipeline_recast_excel.py
import json
import time
import random
import csv
import argparse

import pandas as pd
from gemini_client import call_gemini

# INPUT_XLSX = "user_stories_RE.csv"
# OUTPUT_XLSX = "user_stories_RE_qualitative.csv"

CADY = """Hello! My name is Cady, and I work at our local emergency dispatch center. On a normal day, I help answer emergency calls, document information, prioritize which resources need to be sent out, and coordinate with first responders. 
We get all sorts of calls, from minor injuries to people being trapped and unable to move, which all demand different levels of resources. During times of high call activity, it's hard to process incoming calls, prioritize them accurately, and dispatch the right resources as fast as we can. Because of this, my manager is thinking about how we can revamp our dispatch system to better handle these surges.
We've unfortunately had incidents where calls got delayed because we simply couldn't process them fast enough. In one case, there was a huge earthquake and a family trapped in their home didn't get immediate attention because their call got buried under dozens of minor injury reports. We tried our best to get through the queues, but we can never really predict what will happen.
Usually, people calling in around here are only speaking English. I was even wondering if we could use something like Siri or some technology that can already interpret English calls. Those exist, right? I guess they wouldn't really be able to recognize emergency calls though since they're not really like normal conversations most of the time. I also wouldn't want some Siri-thing to mistakenly say that some situation isn't serious when it is. For example, sometimes we get calls where someone is ordering a pizza, but they're really reporting a domestic abuse situation. 
At least a consistent thing is that people typically report the same types of emergencies: broken bones, chest pain, house fires, gas leaks, people stuck in elevators. But every once in a while we get a weird or unexpected call, like a grown adult who got stuck in a kitchen chair. It's entertaining to look back at our logs and listen to the crazy calls. 
There really is a lot of information to process during every call. First, someone has to figure out exactly what the caller is saying and type that information into the system. Then they have to determine how urgent the situation is and whether it is life-threatening or something that can wait. Finally, they have to decide what kinds of resources to allocate: ambulance, fire department, search and rescue, police, or some combination. The process of logging all this information is arduous, but as a result we have a lot of recordings of calls and records of what resources were deployed for each call.

I recently pitched an idea to our leadership team for a smart dispatch tool that could take over dispatch for the more routine calls and route the complicated ones to humans. Leadership thought this kind of tool might be useful, but they also raised some concerns. What if the system misses something important during one of those rare, weird cases? What if it doesn't understand the local quirks, like how certain backroads flood after an earthquake or how it's faster to take a side street to the hospital than the main road? Also, apparently our whole tech allocation for the year is only for a couple of regular office computers, so we can only rely on cloud-based services if we need something stronger. 
Personally, I think we can't rely on a smart system for every case. But for the common calls like broken arms, smoke alarms, and minor injuries, I think automation could help us manage the call volume and let humans focus on the high-stakes situations where experience really matters.
"""

JOSIE = """
I'm Josie, and I work for NRG. We manage the energy and power stations around this side of the state. Most days, I'm out in the field checking on substations, monitoring power lines, and honestly, just making sure nothing's on fire. Literally and figuratively. 
But lately, man. The weather's been crazy, and it's been throwing everything off. When it gets hot, the grid gets seriously stressed. Some areas suck up a ton of electricity trying to keep AC units blasting, while others just can't get enough. We've even had reports of elderly residents getting heatstroke because their homes can't stay cool. My manager's been pushing hard for us to fix it.
The town next to us actually upgraded to this really slick smart grid setup. It can shift power dynamically based on who needs it most. Our residents deserve the same thing, and we've been trying to convince the higher-ups to invest in new infrastructure so we can either join their grid or build a smart system of our own. 
I'm not gonna lie…I don't totally get the technical side. There's something about a fancy algorithm one of their engineers cooked up for their grid. My manager's got some contacts over there, so maybe we can snag their secret sauce and use it as a starting point. And if I remember correctly, we do have some beefy computers that we can work with, but not much budget for anything else.
I think there's a catch, though. Their town's full of shiny new buildings that are pretty easy to work with. Ours is a patchwork of half old, half brand-new developments. That means whatever system we use might need some serious tweaks to actually work here. Also, we don't even have a perfect map of where the old stuff and new stuff is. No one's bothered to lay it out properly, and Google Maps around here is slow to catch up, even if the buildings are already wired into the grid and pulling power.
The good news is, we already collect tons of data: power loads, substation temperatures, wind patterns, weather forecasts, all time-stamped and updated every minute, which is pretty great. But man, one thing I wish we had is better visibility between substations. Right now, we can see what's happening at each station, but not how the power's doing on the lines between them.
That means even if we think we're sending enough power somewhere, houses stuck between two substations in our “blind spots” might not actually be getting what they need. We only find out if they call to complain, or if they don't, which we just have to assume means they're fine. And even then, every resident's different. Some people don't mind a short outage now and then. Others absolutely need steady, reliable power 24/7. Luckily, we've kept a list of complaints so we know who to give some extra attention to already.
The dream is to have a system smart enough to read all the data, predict what's coming, and balance power on its own so we're not stuck playing whack-a-mole every time the weather changes or everyone cranks their AC. I think the most important thing is probably that our system is accurate to our town. Since we won't get regular severe weather for months, we have some time to spare before we want to get something up and running.

"""

BEN = """Hi, my name is Ben. I work for the local government, in the branch that handles public assistance programs.
Our team is responsible for reviewing applications from people who are seeking things like housing support, food assistance, or medical subsidies. We have clear guidelines for who qualifies, such as income limits, residency status, and family size. But the reality is that it's not always black and white.
Sometimes applicants' situations don't fit neatly into a checkbox. They might have informal income sources, missing documents, or complicated living arrangements. Figuring out if someone truly meets the eligibility criteria requires a lot of effort. Form field data in our application often leaves out the content that truly exposes their situation. The best fix would be a full overhaul of the application system, but given its age and technical complexity, our only practical option is to build on top of it. Luckily, our engineers regularly receive external training on the latest software and AI methods, so they have the expertise to enhance and build on top of these older systems.
We get a large volume of applications every month, and our team struggles to keep up. We want to be fair and thorough, but the caseload makes it hard. Some people who urgently need help might end up waiting longer than they should. That means that mothers who need support with getting baby formula have to wait, or someone experiencing homelessness might not get access to resources for weeks or months.
We really need to reduce our workload. I'm reading so many applications that as the day goes on, I'm so fatigued that I just can't pick out the finer details from applications anymore. We're hoping to get some sort of automated system that could help our staff by reviewing applications and putting them into buckets of “likely eligible, unclear, or likely ineligible.” That way, we could quickly review their information, accept or reject the clear ones, and follow up with individuals to collect additional details for the ambiguous cases. I'm not sure if it should give us the answers directly, because I'm scared that if it makes a mistake then it would reflect poorly on us workers. 
We know it wouldn't be perfect, which is why we'd keep our staff involved. This kind of categorization is really nuanced, which is why we have such experienced workers handling these cases. The system might not get everything right at first, but if we could flag correct or incorrect suggestions, maybe it could learn over time. 
If we can build something like this, it would help us serve our community faster and more fairly. It would make sure the right help reaches the people who need it most, without overwhelming the people who work so hard to process every case.

"""

MEGAN = """Hi, my name is Megan. I work at a public high school in a lower-income urban area. Our school serves a very diverse population: students come from different racial backgrounds, immigrant families, foster care, single-parent households, and more. Over the years I've learned that a lot of our students have responsibilities outside of school, like working part-time, caring for younger siblings, or dealing with unstable living situations.
I have a lot of experience counseling students, but my caseload is over 300 students per semester. There's no way I can give every student the time and attention they deserve individually, but I can't just focus on a few groups either… Everyone deserves support.
Most days, I meet with students briefly in one on one meetings for 15 to 20 minutes. We go over their grades, attendance records, and talk about their career or college plans. My main goal is to spot problems early, while there's still time to intervene and offer help before small issues turn into big things we can't fix.
Some of the biggest challenges I face are the hidden problems. Students often don't tell me everything upfront, which I understand! It can be hard to open up and be vulnerable. But sometimes, I only find out that a student was homeless after they've already dropped out. And unless there's something obvious, like a student failing all their classes, it's really hard to know who needs urgent help. It's also difficult to spot patterns across students. For example, if a whole group starts disengaging because an entire block lost internet access, I might not realize it until it's too late.
I have access to individual student files, but we don't have clear labels like “at-risk” or “fine.” I can see obvious things like grades and absences, but most of the real risk factors — the things happening outside of school — aren't visible right away.
Our administration thought that part of the problem might be that students are too embarrassed to share their struggles directly with counselors. So they sent out an anonymous survey asking students about their living situations. The questions were things like, “Do you have reliable transportation to school?” and “Are you the full-time caretaker for another family member?”  I think the admin plans to send out these surveys every few months to make sure that we stay relatively up to date without overwhelming the kids. We have some of these survey responses now, but it's so much data that it's been overwhelming to sort through and make sense of it. 
What I really want is to figure out what the biggest struggles are for our students, and more importantly, how those struggles affect their academic performance. I want to understand what's causing students to struggle, not just list out the problems they're facing. That way, we can actually simulate interventions and see what might help.
For example, if we find that lack of transportation is one of the biggest issues, and that it's causing poor attendance, which leads to lower grades, maybe we can find a way to provide transportation. Otherwise, if I didn't know about the transportation problem, I might just push students into tutoring to fix their grades, without realizing that they physically can't even get to school.

"""

SCENARIO_TEXT = {
    "cady": CADY,
    "josie": JOSIE,
    "ben": BEN,
    "megan": MEGAN,
}


SYSTEM_INSTRUCTION = """
You are an expert qualitative coder.
You will evaluate a participant-written user story for:
(1) HCD indicators (Human-Centered Design)
(2) VSD indicators (Value-Sensitive Design)
(3) Alignment indicators

Use ONLY the provided rubric. Do not infer unstated information.
Return ONLY valid JSON that matches the required schema exactly.
""".strip()

RUBRIC_TEXT = """
HCD indicator score (0.0, 0.5, 1.0):
- 1.0: The user story explicitly centers a human stakeholder AND includes at least one concrete human need/constraint/risk
       (e.g., access, safety, workload, capacity, usability, trust, vulnerability, inclusion/exclusion, context).
- 0.5: The story mentions a human stakeholder/user, but human needs/constraints are vague, generic, or only implied.
- 0.0: The story is system/technical-centric with no meaningful human stakeholder framing.

VSD indicator score (0.0, 0.5, 1.0):
- 1.0: The story explicitly references a stakeholder value or ethical objective
       (e.g., fairness/equity, autonomy, accountability, privacy, transparency, inclusion, harm avoidance),
       OR describes an explicit normative tradeoff tied to stakeholder goals.
- 0.5: The story mentions generic improvement goals (efficiency, accuracy, speed, better service) without explicit value framing.
- 0.0: No values or normative goals are expressed in the user story.



ALIGNMENT indicator score (0.0, 0.5, 1.0)
- 1.0: The actor in the user story (the “As a …” person or clearly implied stakeholder) is pursuing a goal that is plausible for 
their role and fits the scenario's context (responsibilities, constraints, or impacts).
- 0.5: The actor-goal link is partly plausible, but either the role is vague/ambiguous, or the goal is generic/weakly justified, 
or the connection to the scenario is indirect.
- 0.0: The actor is miscast for the scenario or the goal is implausible/mis-scoped for that actor in this scenario 
(wrong role, unrealistic responsibility, or unrelated objective).

Rules:
- Score only from the user story text.
- Evaluate the goal/objective (what the story is trying to achieve), not writing quality or format compliance.
- If the goal is not stated, infer only if it is explicitly implied
""".strip()

PROMPT_TEMPLATE = """
You are evaluating ONE user story.

[Scenario Name]
{scenario_name}

[Scenario Description]
{scenario_text}

[User Story]
{user_story}

[Rubric]
{rubric_text}

Task:
1) Score HCD indicator: 0.0, 0.5, or 1.0.
2) Score VSD indicator: 0.0, 0.5, or 1.0.
3) Score ALIGNMENT indicator: 0.0, 0.5, or 1.0
3) Provide brief rationales (1-2 sentences each).

Output ONLY a JSON object with exactly these keys:
- "scenario_name"
- "hcd"
- "vsd"
- "alignment"
- "rationale" (object with keys "hcd", "vsd", "alignment")
""".strip()



def build_prompt(user_story: str, scenario_name: str) -> str:
    scenario_key = (scenario_name or "").strip().lower()
    scenario_text = SCENARIO_TEXT.get(scenario_key, "")
    return PROMPT_TEMPLATE.format(
        scenario_name=scenario_key,
        scenario_text=scenario_text,
        user_story=(user_story or "").strip(),
        rubric_text=RUBRIC_TEXT,
    )

def _normalize_score(x):
    if isinstance(x, str):
        x = x.strip()
    if x in [0, 0.0, "0", "0.0"]:
        return 0.0
    if x in [0.5, "0.5"]:
        return 0.5
    if x in [1, 1.0, "1", "1.0"]:
        return 1.0
    return None

def safe_parse_json_hcd_vsd(raw_text: str) -> dict:
    keys = ["scenario_name", "hcd", "vsd", "rationale"]
    if raw_text is None:
        return {k: None for k in keys}

    text = raw_text.strip()

    # Handle ```json ... ``` wrappers
    if text.startswith("```"):
        text = text.strip("`")
        if text.lower().startswith("json"):
            text = text[4:].lstrip()

    try:
        data = json.loads(text)
    except Exception:
        return {k: None for k in keys}

    # --- scenario name ---
    scenario_name = data.get("scenario_name", None)
    if scenario_name is not None:
        scenario_name = str(scenario_name).strip().lower()

    # --- extract scores (handle both schemas) ---
    hcd_obj = data.get("hcd", None)
    vsd_obj = data.get("vsd", None)
    alignment_obj = data.get("alignment", None)

    # If Gemini returns {"hcd": {"score": 1.0, ...}}, pull the score
    if isinstance(hcd_obj, dict):
        hcd_score = hcd_obj.get("score", None)
    else:
        hcd_score = hcd_obj

    if isinstance(vsd_obj, dict):
        vsd_score = vsd_obj.get("score", None)
    else:
        vsd_score = vsd_obj

    if isinstance(alignment_obj, dict):
        alignment_score = alignment_obj.get("score", None)
    else:
        alignment_score = alignment_obj

    hcd_score = _normalize_score(hcd_score)
    vsd_score = _normalize_score(vsd_score)
    alignment_score = _normalize_score(alignment_score)

    # --- rationale ---
    ra = data.get("rationale") or {}
    rationale = {
        "hcd": str(ra.get("hcd", "") or "").strip(),
        "vsd": str(ra.get("vsd", "") or "").strip(),
        "alignment": str(ra.get("alignment", "") or "").strip()
    }

    return {
        "scenario_name": scenario_name,
        "hcd": hcd_score,
        "vsd": vsd_score,
        "alignment": alignment_score,
        "rationale": rationale,
    }

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
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_csv", required=True, help="Path to input user stories CSV")
    parser.add_argument("--output_csv", required=True, help="Path to output CSV with HCD/VSD coding")
    parser.add_argument("--limit", type=int, default=None, help="Optional row limit for testing")
    args = parser.parse_args()

    df = pd.read_csv(
        args.input_csv,
        encoding="utf-8",
        encoding_errors="replace",
        quoting=csv.QUOTE_ALL,
    )

    required_cols = ["participant_id", "scenario", "stakeholder_number", "user_story"]
    missing = [c for c in required_cols if c not in df.columns]
    if missing:
        raise ValueError(f"Input CSV missing required columns: {missing}")

    df["scenario"] = df["scenario"].astype(str).str.strip().str.lower()
    df["scenario_is_known"] = df["scenario"].isin(SCENARIO_TEXT.keys())

    if args.limit is not None:
        df = df.iloc[: args.limit].copy()

    llm_hcd = []
    llm_vsd = []
    llm_alignment = []
    llm_hcd_rationale = []
    llm_vsd_rationale = []
    llm_alignment_rationale = []
    llm_scenario_name_echo = []
    raw_llm_output = []

    for i, row in df.iterrows():
        pid = row.get("participant_id", "NA")
        scenario = row.get("scenario", "")
        user_story = row.get("user_story", None)

        print(f"Row {i}: participant_id={pid}, scenario={scenario}")

        if pd.isna(user_story) or str(user_story).strip() == "":
            llm_hcd.append(None)
            llm_vsd.append(None)
            llm_alignment.append(None)
            llm_hcd_rationale.append("")
            llm_vsd_rationale.append("")
            llm_alignment_rationale.append("")
            llm_scenario_name_echo.append(scenario)
            raw_llm_output.append("")
            continue

        prompt = build_prompt(str(user_story), scenario)

        response_text = call_gemini_with_retry(
            prompt,
            system_instruction=SYSTEM_INSTRUCTION,
        )

        if response_text is None:
            llm_hcd.append(None)
            llm_vsd.append(None)
            llm_alignment.append(None)
            llm_hcd_rationale.append("")
            llm_vsd_rationale.append("")
            llm_alignment_rationale.append("")
            llm_scenario_name_echo.append(scenario)
            raw_llm_output.append("")
            continue

        parsed = safe_parse_json_hcd_vsd(response_text)

        raw_llm_output.append(response_text)
        llm_hcd.append(parsed.get("hcd", None))
        llm_vsd.append(parsed.get("vsd", None))
        llm_alignment.append(parsed.get("alignment", None))
        llm_hcd_rationale.append(parsed.get("rationale", {}).get("hcd", ""))
        llm_vsd_rationale.append(parsed.get("rationale", {}).get("vsd", ""))
        llm_alignment_rationale.append(parsed.get("rationale", {}).get("alignment", ""))
        llm_scenario_name_echo.append(parsed.get("scenario_name", scenario))

    # Attach outputs
    df["llm_hcd"] = llm_hcd
    df["llm_vsd"] = llm_vsd
    df["llm_alignment"] = llm_alignment
    df["llm_hcd_rationale"] = llm_hcd_rationale
    df["llm_vsd_rationale"] = llm_vsd_rationale
    df["llm_alignment_rationale"] = llm_alignment_rationale
    df["llm_scenario_name"] = llm_scenario_name_echo
    df["llm_raw_json_hcd_vsd"] = raw_llm_output

    df.to_csv(args.output_csv, index=False, encoding="utf-8", quoting=csv.QUOTE_ALL)
    print(f"Done! Saved HCD/VSD-annotated data to: {args.output_csv}")


if __name__ == "__main__":
    main()