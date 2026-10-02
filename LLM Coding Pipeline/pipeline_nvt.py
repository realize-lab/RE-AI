# pipeline_recast_excel.py
import json
import time
import random
import argparse
import csv
import re

import pandas as pd
from gemini_client import call_gemini

INPUT_XLSX = "user_stories_AI_AC_long.csv"
OUTPUT_XLSX = "1_NVT_grading_AI"

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
You are an expert requirements engineer evaluating acceptance criteria
for software requirements in an AI for Social Good context. This is a mock development scenario.

You will receive:
- A scenario description
- A user story written by a participant.

You must evaluate the user story according to a binary rubric, scoring each
dimension as 0 (does not meet) or 1 (meets).

Follow the rubric exactly and be as consistent as possible.

Return valid JSON only.

"""

RUBRIC_TEXT = """
You are evaluating ONE user story.

Score each of the following dimensions as either 0 or 1:

1. Negotiable (0/1)
Definition:
- A story is negotiable if it expresses a need or goal that allows for multiple plausible design responses. 

Score 1 if:
- The user story expresses a need or goal without prescribing a specific implementation, algorithm, model type, or system architecture.
Score 0 if:
- It specifies how the system must be built (e.g., “integrate an AI classifier,” “use automation,” “build modifications on top of legacy systems”)

2. Valuable (0/1)
Definition:
- A story is valuable if it describes a benefit for the stakeholder.

Score 1 if:
- The story clearly describes how it helps the stakeholder identified in the user story
Score 0 if:
- The story has an unclear or generic benefit
Note: Efficiency only counts as Valuable if the story explicitly connects speed or automation to reduced harm, increased fairness, or improved access for people.

3. Testable (0/1)
Definition:
- A story is testable if success could be evaluated using observable evidence, either qualitative or quantitative. 

Score 1 if:
- The outcome can be plausibly evaluated by observing system behavior, decisions, or user experience
(e.g., flagged cases, explanations shown, turnaround time, feedback loops)
Score 0 if:
- Success is described in vague, totalizing, or aspirational terms (e.g., “every detail,” “accurate judgment,” “be fair”) 
and determining success would require inventing metrics, baselines, or audits not stated or implied in the story.

You must output STRICT JSON with integer 0/1 scores and brief rationales (1-2 sentences each).
""".strip()

PROMPT_TEMPLATE = """
You are evaluating a user story written as part of requirements engineering for a stakeholder scenario.

[Scenario Name]
{scenario_name}

[Scenario Description]
{scenario_text}

[User Story]
{user_story}

[Rubric]
{rubric_text}

Now evaluate the user story according to the rubric.

Output ONLY a single JSON object with exactly the following keys:
- "negotiable" (0 or 1)
- "negotiable_rationale" (string, 1-2 sentences)
- "valuable" (0 or 1)
- "valuable_rationale" (string, 1-2 sentences)
- "testable" (0 or 1)
- "testable_rationale" (string, 1-2 sentences)

Rules:
- Use integer values 0/1 for the three scores.
- Each rationale must be 1-2 sentences (not bullets), grounded in the scenario and the user story.
- No extra keys. No extra text outside the JSON.
""".strip()


def build_prompt(*, scenario_name: str, scenario_text: str, user_story: str) -> str:
    return PROMPT_TEMPLATE.format(
        scenario_name=(scenario_name or "").strip(),
        scenario_text=(scenario_text or "").strip(),
        user_story=(user_story or "").strip(),
        rubric_text=RUBRIC_TEXT,
    )


def safe_parse_json(raw_text: str) -> dict:
    keys_int = ["negotiable", "valuable", "testable"]
    keys_str = ["negotiable_rationale", "valuable_rationale", "testable_rationale"]

    if raw_text is None:
        out = {k: None for k in keys_int + keys_str}
        return out

    text = raw_text.strip()

    # Remove ```json ... ``` fences safely
    fence_match = re.match(r"^```(?:json)?\s*(.*?)\s*```$", text, flags=re.DOTALL | re.IGNORECASE)
    if fence_match:
        text = fence_match.group(1).strip()

    try:
        data = json.loads(text)
    except Exception:
        out = {k: None for k in keys_int + keys_str}
        return out

    parsed = {}

    # Parse 0/1 scores
    for k in keys_int:
        v = data.get(k, None)
        if v in [0, 1, "0", "1"]:
            parsed[k] = int(v)
        else:
            parsed[k] = None

    # Parse rationale strings
    for k in keys_str:
        v = data.get(k, None)
        if isinstance(v, str):
            v_clean = v.strip()
            parsed[k] = v_clean if v_clean else None
        else:
            parsed[k] = None

    return parsed


def call_gemini_with_retry(prompt, system_instruction=None, max_retries=8):
    delay = 1.0  # starting delay in seconds

    for attempt in range(1, max_retries + 1):
        try:
            return call_gemini(prompt, system_instruction=system_instruction)
        except Exception as e:
            error_msg = str(e).lower()

            rate_limited = any(
                substring in error_msg
                for substring in ["rate", "quota", "429", "resource exhausted", "try again later", "too many requests"]
            )

            if rate_limited:
                print(f"⚠️ Rate limit on attempt {attempt}/{max_retries}: {e}")
                sleep_time = delay + random.uniform(0, 0.5)
                print(f"   → Waiting {sleep_time:.2f}s before retrying...")
                time.sleep(sleep_time)
                delay *= 2
                continue

            print(f"❌ Non-rate-limit Gemini error: {e}")
            return None

    print("❌ Exhausted all retries calling Gemini. Returning None.")
    return None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_csv", required=True)
    parser.add_argument("--output_csv", required=True)
    parser.add_argument("--limit", type=int, default=None, help="Optional row limit for testing")
    args = parser.parse_args()

    df = pd.read_csv(
        args.input_csv,
        encoding="utf-8",
        encoding_errors="replace",
        quoting=csv.QUOTE_ALL
    )

    if args.limit is not None:
        df = df.iloc[: args.limit].copy()

    required_cols = ["participant_id", "scenario", "stakeholder_number", "user_story"]
    missing = [c for c in required_cols if c not in df.columns]
    if missing:
        raise ValueError(f"Input CSV is missing required columns: {missing}")

    llm_negotiable = []
    llm_valuable = []
    llm_testable = []
    llm_negotiable_r = []
    llm_valuable_r = []
    llm_testable_r = []
    raw_llm_output = []

    for i, row in df.iterrows():
        raw_user_story = row.get("user_story", None)
        scenario_key = (row.get("scenario", "") or "").strip().lower()
        scenario_text = SCENARIO_TEXT.get(scenario_key, "")
        scenario_name = scenario_key if scenario_key else "unknown"

        print(f"Row {i}: participant_id={row.get('participant_id', 'NA')} scenario={scenario_name}")

        if raw_user_story is None or pd.isna(raw_user_story) or str(raw_user_story).strip() == "":
            print("  Skipping row: user_story is empty/NaN")
            llm_negotiable.append(None)
            llm_valuable.append(None)
            llm_testable.append(None)
            llm_negotiable_r.append(None)
            llm_valuable_r.append(None)
            llm_testable_r.append(None)
            raw_llm_output.append("")
            continue

        followed_format = row.get("followed_format", None)

        if followed_format == 0:
            print("  Skipping row: user story does not follow required format")
            llm_negotiable.append(None)
            llm_valuable.append(None)
            llm_testable.append(None)
            llm_negotiable_r.append(None)
            llm_valuable_r.append(None)
            llm_testable_r.append(None)
            raw_llm_output.append("SKIPPED_FORMAT")
            continue

        if scenario_text.strip() == "":
            print("  Warning: scenario text not found for scenario value:", scenario_key)

        prompt = build_prompt(
            scenario_name=scenario_name,
            scenario_text=scenario_text,
            user_story=str(raw_user_story),
        )

        response_text = call_gemini_with_retry(prompt, system_instruction=SYSTEM_INSTRUCTION)

        if response_text is None:
            print("  Gemini returned no text (error, blocked, or retries exhausted).")
            llm_negotiable.append(None)
            llm_valuable.append(None)
            llm_testable.append(None)
            llm_negotiable_r.append(None)
            llm_valuable_r.append(None)
            llm_testable_r.append(None)
            raw_llm_output.append("BLOCKED_OR_ERROR")
            continue

        parsed = safe_parse_json(response_text)
        raw_llm_output.append(response_text)

        llm_negotiable.append(parsed["negotiable"])
        llm_valuable.append(parsed["valuable"])
        llm_testable.append(parsed["testable"])
        llm_negotiable_r.append(parsed["negotiable_rationale"])
        llm_valuable_r.append(parsed["valuable_rationale"])
        llm_testable_r.append(parsed["testable_rationale"])

    df["llm_Negotiable"] = llm_negotiable
    df["llm_Valuable"] = llm_valuable
    df["llm_Testable"] = llm_testable
    df["llm_Negotiable_rationale"] = llm_negotiable_r
    df["llm_Valuable_rationale"] = llm_valuable_r
    df["llm_Testable_rationale"] = llm_testable_r
    df["llm_raw_output"] = raw_llm_output

    df.to_csv(args.output_csv, index=False, quoting=csv.QUOTE_ALL)
    print(f"Done! Saved LLM-annotated data to: {args.output_csv}")


if __name__ == "__main__":
    main()