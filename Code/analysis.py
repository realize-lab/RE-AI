import pandas as pd
import csv
import math
from sklearn.linear_model import LinearRegression
from mappings import QualtricsMapping
from system_components import SystemComponents
import statsmodels.api as sm 
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from scipy.stats import kruskal
from scipy.stats import spearmanr
import os

from scipy.stats import ttest_ind

df = pd.read_csv(
    "CLEAN_all_finished_responses.csv",
    encoding="utf-8",
    encoding_errors="replace",
    quoting=csv.QUOTE_ALL
)

# df_raw = pd.read_csv(
#     "RAW_all_finished_responses.csv",
#     encoding="utf-8",
#     encoding_errors="replace",
#     quoting=csv.QUOTE_ALL
# )


# df = pd.read_csv(
#     "CLEAN_prolific_responses.csv",
#     encoding="utf-8",
#     encoding_errors="replace",
#     quoting=csv.QUOTE_ALL
# )

# df = pd.read_csv(
#     "CLEAN_other_responses.csv",
#     encoding="utf-8",
#     encoding_errors="replace",
#     quoting=csv.QUOTE_ALL
# )


df["participant_id"] = df["Q20_Id"]
# df_raw["participant_id"] = df_raw["Q20_Id"]

# ids_df = set(df["participant_id"].dropna().unique())
# ids_raw = set(df_raw["participant_id"].dropna().unique())

# only_in_df = ids_df - ids_raw
# only_in_df_raw = ids_raw - ids_df

# print("Only in df:", sorted(only_in_df))
# print("Only in df_raw:", sorted(only_in_df_raw))

# did_not_follow_training = ['F_10D7KwSWQn1RsT6', 'F_114RXPlx0Hqo2Mk', 'F_269ZGwaqgHKP6rF', 'F_27qb5aMSqOdOLEy', 
#                            'F_3hgRPr8FepQ2Zqp', 'F_3niQlp7p6n09NTE', 'F_PTaTvAQN9FLMjxT', 'F_ea21IrsxYCPiIal', 
#                            'F_vVO4QoxcdEpBBKN']

# exclude_ids = set(did_not_follow_training)

# # did the people who got training write more 

# # Filter out excluded participants
# df = df[~df["participant_id"].isin(exclude_ids)].copy()

# print(f"Excluded {len(exclude_ids)} participants; remaining: {df['participant_id'].nunique()}")
# print(df.head())

df["ai_theoretical_understanding"] = df["Q77"].apply(QualtricsMapping.map_ai_knowledge) 
df["ai_practical_experience"] = df["Q217b"].apply(QualtricsMapping.map_ai_practical_experience)
df["system_reference"] = df["Q94_10_TEXT"].apply(QualtricsMapping.map_system_component_reference) 
df["reference_freq"] = df["Q74_2"].apply(QualtricsMapping.map_reference_freq) 
df["current_job"] = df["Q86_2_TEXT"].apply(QualtricsMapping.map_current_employment) 
df["current_education"] = df["Q71"].apply(QualtricsMapping.map_current_education) 

def print_info(col):
        mean, sd = df.loc[:, col].mean() , df.loc[:, col].std()
        median = df.loc[:, col].median() 
        Min, Max = df.loc[:, col].min() , df.loc[:, col].max()
        sz = len(df.loc[:, col])
        print(f"{col:30} avg={mean:.2f}, med={median:.2f}, +- {sd:.2f}, range {Min:.1f}-{Max:.1f}, {sz} entries") 

# print_info("ai_theoretical_understanding") 
# print_info("ai_practical_experience") 
# print_info("system_reference") 
# print_info("reference_freq") 

def non_none_to_one(val):
        if not val or pd.isna(val): return 0
        return 1 

df["treatment_re"]  = df["Q21_Id"].apply(non_none_to_one) 
df["treatment_mod"] = df["Q99_Id"].apply(non_none_to_one)
df["treatment_min"] = df["Q109_Id"].apply(non_none_to_one) 
df["treatment_amount"] = (df["treatment_re"]*3) + (df["treatment_mod"]*2) + (df["treatment_min"])

def assign_treatment(row):
    if row["treatment_re"] == 1:
        return "RE"
    if row["treatment_mod"] == 1:
        return "Modified-RE"
    if row["treatment_min"] == 1:
        return "Minimal"
    return None

df["treatment"] = df.apply(assign_treatment, axis=1)
df = df.dropna(subset=["treatment"])
                
# print_info("treatment_re") 
# print_info("treatment_mod") 
# print_info("treatment_min") 
# print_info("treatment_amount") 

df["data_correct"] = 0
df["learning_correct"] = 0
df["model_correct"] = 0
df["system_correct"] = 0
df["training_correct"] = 0

answer_key = SystemComponents.global_answer_key_community_all

def grade_responses(response_columns, scenario_num, answer_key, participant_ids):
    scenario_names = {1: "cady", 2: "josie", 3: "ben", 4: "megan"}
    scenario = scenario_names[scenario_num]
    key = answer_key[scenario]
    question_keys = ["data", "learning", "model", "system", "training"]
    correct_keys = ["data_correct", "learning_correct", "model_correct", "system_correct", "training_correct"]
    for p in participant_ids: 
        for i, category in enumerate(question_keys):
            this_response = (df.loc[ df["participant_id"] == p, response_columns[i] ]).iat[0].lower()
            correct_answers = [ans.strip().lower() for ans in key[category]]
            correct = any([ ans in this_response for ans in correct_answers ])
            if correct:
              (df.loc[ df["participant_id"] == p, correct_keys[i] ]) = (df.loc[ df["participant_id"] == p, correct_keys[i] ]) + 1 

cady_columns = ["Q44", "Q45", "Q46", "Q47", "Q48"]
josie_columns = ["Q188", "Q189", "Q190", "Q191", "Q192"]
ben_columns = ["Q210", "Q211", "Q212", "Q213", "Q214"]
megan_columns = ["Q232", "Q233", "Q234", "Q235", "Q236"]

grade_responses(cady_columns, 1, answer_key, df["participant_id"])
grade_responses(josie_columns, 2, answer_key, df["participant_id"])
grade_responses(ben_columns, 3, answer_key, df["participant_id"])
grade_responses(megan_columns, 4, answer_key, df["participant_id"])
df["total_correct"] = df["data_correct"] + df["learning_correct"] + df["model_correct"] + df["system_correct"] + df["training_correct"] 

# print_info("data_correct") 
# print_info("learning_correct") 
# print_info("model_correct") 
# print_info("system_correct") 
# print_info("training_correct") 
# print_info("total_correct") 



usdf = pd.read_csv(
    "User Story Analysis.csv",
    encoding="utf-8",
    encoding_errors="replace",
    quoting=csv.QUOTE_ALL
)

total_us = len(usdf)
formatted_us = (usdf["followed_format"] == 1).sum()
not_formatted_us = total_us - formatted_us

pct_excluded = 100 * not_formatted_us / total_us if total_us > 0 else float("nan")
pct_included = 100 * formatted_us / total_us if total_us > 0 else float("nan")

# print("\n===== User Story Format Filtering =====")
# print(f"Total user stories:                {total_us}")
# print(f"Followed format (included):        {formatted_us} ({pct_included:.2f}%)")
# print(f"Did NOT follow format (excluded):  {not_formatted_us} ({pct_excluded:.2f}%)")
    
# Keep only stories that followed the correct format
usdf = usdf[usdf["followed_format"] == 1].copy()

df["followed_format"] = df["participant_id"].map(
usdf.groupby("participant_id")["followed_format"].max()
).fillna(0)


df["negotiable"] = 0
df["valuable"] = 0
df["testable"] = 0

# Loop over participants that remain in df

# print(len(df["participant_id"].unique()))

for p in df["participant_id"].unique():
    usdf_filtered = usdf[usdf["participant_id"] == p]
    if usdf_filtered.empty:
        continue  # no formatted stories for this participant

    df.loc[df["participant_id"] == p, "negotiable"] = usdf_filtered["Negotiable"].sum()
    df.loc[df["participant_id"] == p, "valuable"]   = usdf_filtered["Valuable"].sum()
    df.loc[df["participant_id"] == p, "testable"]   = usdf_filtered["Testable"].sum()

df["nvt"] = df["negotiable"] + df["valuable"] + df["testable"]

# Count how many *formatted* user stories each participant wrote
us_counts = usdf.groupby("participant_id")["Negotiable"].count().rename("num_us_formatted")
df["num_us"] = df["participant_id"].map(us_counts).fillna(0)

# Compute mean NVT only for participants with formatted stories
df["mean_nvt"] = df["nvt"] / df["num_us"].replace({0: np.nan})

# print_info("negotiable")
# print_info("valuable")
# print_info("testable")
# print_info("nvt")
# print_info("mean_nvt")




#=====================================================================================#

INPUT_XLSX = "ac_data/ac_with_llm_2.xlsx"
acdf = pd.read_excel(INPUT_XLSX)

total_ac = len(acdf)
kept_ac = (acdf["followed_ac_format"] == 1).sum()
# print(f"AC rows before: {total_ac}, after: {kept_ac}, excluded: {total_ac - kept_ac}")

acdf = acdf[acdf["followed_ac_format"] == 1].copy()


# Initialize participant-level AC aggregates
df["ac_Verifiable"] = 0
# df["ac_Traceable"] = 0
df["ac_Atomic"] = 0
df["ac_II"] = 0
# df["ac_Unambiguous"] = 0

for p in df["participant_id"].unique():
    acdf_filtered = acdf[acdf["participant_id"] == p]

    # if acdf_filtered.empty:
    #     print(f"Warning: No acceptance criteria found for participant {p}")
    #     continue

    df.loc[df["participant_id"] == p, "ac_Verifiable"] = acdf_filtered["llm_Verifiable"].sum(skipna=True)
    # df.loc[df["participant_id"] == p, "ac_Traceable"] = acdf_filtered["llm_Traceable"].sum(skipna=True)
    df.loc[df["participant_id"] == p, "ac_Atomic"] = acdf_filtered["llm_Atomic"].sum(skipna=True)
    df.loc[df["participant_id"] == p, "ac_II"] = acdf_filtered["llm_II"].sum(skipna=True)

# Total AC quality score per participant (analogous to nvt)
df["ac_score"] = (
    df["ac_Verifiable"]+
    # df["ac_Traceable"]+
    df["ac_Atomic"]+
    df["ac_II"]
)

# print_info("ac_Verifiable")
# print_info("ac_Traceable")
# print_info("ac_Atomic")
# print_info("ac_II")
# print_info("ac_score")


# df["is_good_at_ac"] = df["ac_score"]>= df["ac_score"].median() 
# df["is_good_at_nvt"] = df["nvt"] >= df["nvt"].median() 
# df["is_good_at_ac"] = df["ac_score"]>= df["ac_score"].median() 


# Count how many AC rows each participant wrote
ac_counts = acdf.groupby("participant_id")["llm_Verifiable"].count().rename("num_ac")
df["num_ac"] = df["participant_id"].map(ac_counts).fillna(0)

df["mean_ac_score"] = df["ac_score"] / df["num_ac"].replace({0: np.nan})





df_valid = df.dropna(subset=["total_correct"])

# Sort by total_correct
df_sorted = df_valid.sort_values(by="total_correct", ascending=False)





ssf_files = [
    "user_stories_RE_qualitative_coded.csv",
    "user_stories_Minimal_qualitative_coded.csv",
    "user_stories_ModifiedRE_qualitative_coded.csv",
]

ssf_all = pd.concat([pd.read_csv(f) for f in ssf_files], ignore_index=True)

ssf_agg = ssf_all.groupby("participant_id")["llm_ssf"].mean().rename("mean_ssf").reset_index() # calculate mean ssf for each participant

df = df.merge(ssf_agg, on="participant_id", how="left")



aggregated_coding = "US_MERGED_HCD_VSD_FILLED_QUALITATIVE.csv"
coded = pd.read_csv(aggregated_coding, quoting=csv.QUOTE_ALL)

needed_cols = ["participant_id", "llm_hcd", "llm_vsd", "llm_alignment"]
missing = [c for c in needed_cols if c not in coded.columns]
if missing:
    raise KeyError(f"Missing columns in {aggregated_coding}: {missing}")

# can grade user stories even if they didnt follow format
# coded = coded[coded["followed_format"] == 1].copy()

# Convert to numeric in case they were read as strings
for c in ["llm_hcd", "llm_vsd", "llm_alignment"]:
    coded[c] = pd.to_numeric(coded[c], errors="coerce")

# Participant-level aggregation (mean across user stories)
hcd_vsd_agg = (
    coded.groupby("participant_id")[["llm_hcd", "llm_vsd", "llm_alignment"]]
    .mean()
    .rename(columns={
        "llm_hcd": "mean_hcd",
        "llm_vsd": "mean_vsd",
        "llm_alignment": "mean_alignment",
    })
    .reset_index()
)

# Merge into main df
df = df.merge(hcd_vsd_agg, on="participant_id", how="left")


US_CODED_CSV = "US_MERGED_HCD_VSD_FILLED_QUALITATIVE.csv"  

us = pd.read_csv(US_CODED_CSV, quoting=csv.QUOTE_ALL)
us["participant_id"] = us["participant_id"].astype(str)

# target = df[df["participant_id"] == "F_1IAByy2XkufX845"] 

# print (target)
# print(target[["participant_id"], "scenario", "llm_ssf"]].to_string(index=False))

metric_cols = ["llm_ssf", "llm_hcd", "llm_vsd", "llm_alignment"]
present_metrics = [c for c in metric_cols if c in us.columns]
missing_metrics = [c for c in metric_cols if c not in us.columns]

if len(present_metrics) == 0:
    raise KeyError(
        f"No expected user story metric columns found in {US_CODED_CSV}. "
        f"Expected one or more of: {metric_cols}"
    )

for c in present_metrics:
    us[c] = pd.to_numeric(us[c], errors="coerce")

# =========================
# Per-row "story quality" proxy
# =========================
# Mean across whatever metrics are present (e.g., if llm_ssf isn't in this file, it'll average HCD/VSD/Alignment only)
us["story_quality"] = us[present_metrics].mean(axis=1, skipna=True)

# =========================
# Participant-level aggregation
# =========================
per_p_story = (
    us.groupby("participant_id")[present_metrics + ["story_quality"]]
      .mean()
      .reset_index()
      .rename(columns={
          "story_quality": "mean_story_quality"
      })
)

# Merge with performance
perf = df[["participant_id", "total_correct"]].copy()
perf["participant_id"] = perf["participant_id"].astype(str)

plot_df = per_p_story.merge(perf, on="participant_id", how="inner").dropna(subset=["total_correct"]).copy()


################
# Analysis of what kinds of AC get rated in MoSCoW
#################


aggregated_ac_coding = "pipeline_with_ac_grading.csv"
coded = pd.read_csv(aggregated_ac_coding, quoting=csv.QUOTE_ALL)

needed_cols = ["participant_id", "user_story_relevance", "scenario_scope_validity"]
missing = [c for c in needed_cols if c not in coded.columns]
if missing:
    raise KeyError(f"Missing columns in {aggregated_ac_coding}: {missing}")

# can also grade acceptance criteria even if they didn't follow format
# coded = coded[coded["followed_ac_format"] == 1].copy()


# Convert to numeric in case they were read as strings
for c in ["user_story_relevance", "scenario_scope_validity"]:
    coded[c] = pd.to_numeric(coded[c], errors="coerce")

# Participant-level aggregation (mean across user stories)
ac_agg = (
    coded.groupby("participant_id")[["user_story_relevance", "scenario_scope_validity"]]
    .mean()
    .rename(columns={
        "user_story_relevance": "mean_user_story_relevance",
        "scenario_scope_validity": "mean_scenario_validity",
    })
    .reset_index()
)

# aggregated the acceptance criteria that were written in response to a user story

# Merge into main df
df = df.merge(ac_agg, on="participant_id", how="left")






coded = pd.read_csv(aggregated_ac_coding, quoting=csv.QUOTE_ALL)

needed_cols = ["participant_id", "user_story_relevance", "scenario_scope_validity", "moscow_label"]
missing = [c for c in needed_cols if c not in coded.columns]
if missing:
    raise KeyError(f"Missing columns in {aggregated_ac_coding}: {missing}")

# Optional: can also grade acceptance criteria even if they didn't follow format
# coded = coded[coded["followed_ac_format"] == 1].copy()

# Convert to numeric in case they were read as strings
for c in ["user_story_relevance", "scenario_scope_validity"]:
    coded[c] = pd.to_numeric(coded[c], errors="coerce")








coded["moscow_label"] = coded["moscow_label"].astype(str).str.strip().str.lower()

coded = coded[coded["moscow_label"].isin(["m", "s", "c", "w"])].copy()

for col in ["scenario_scope_validity", "user_story_relevance"]:
    coded[col] = pd.to_numeric(coded[col], errors="coerce")

# AC quality proxy per row (mean of scope validity + relevance)
coded["ac_quality"] = coded[["scenario_scope_validity", "user_story_relevance"]].mean(axis=1, skipna=True)

# Participant-level mean AC quality, separately for each MoSCoW label
per_p_label = (
    coded.groupby(["participant_id", "moscow_label"])["ac_quality"]
    .mean()
    .reset_index()
    .rename(columns={"ac_quality": "mean_ac_quality_for_label"})
)

# =========================
# Merge with performance
# =========================
perf = df[["participant_id", "total_correct"]].copy()
perf["participant_id"] = perf["participant_id"].astype(str)

plot_df = per_p_label.merge(perf, on="participant_id", how="inner")
plot_df = plot_df.dropna(subset=["mean_ac_quality_for_label", "total_correct"]).copy()



# Isolate only Must-labeled ACs
must = coded[coded["moscow_label"] == "m"].copy()

# Participant-level mean quality of Must ACs
must_quality = (
    must.groupby("participant_id")[["scenario_scope_validity", "user_story_relevance"]]
        .mean()
        .rename(columns={
            "scenario_scope_validity": "mean_scope_validity_must",
            "user_story_relevance": "mean_relevance_must",
        })
)

# Composite quality score for Must ACs (equal weighting of both dimensions)
must_quality["mean_must_ac_quality"] = (
    must_quality["mean_scope_validity_must"] + must_quality["mean_relevance_must"]
) / 2

must_quality = must_quality.reset_index()

# Merge into your participant-level dataframe
df = df.merge(must_quality[["participant_id", "mean_must_ac_quality"]], 
              on="participant_id", how="left")

# Fill participants who never used Must with 0 for the regression (keeps them in analysis)
df["mean_must_ac_quality"] = df["mean_must_ac_quality"].fillna(0)



coded["ac_quality"] = coded[["scenario_scope_validity", "user_story_relevance"]].mean(axis=1, skipna=True)

# =========================
# Aggregate by MoSCoW label
# =========================
agg = (
    coded.groupby("moscow_label")[["ac_quality", "scenario_scope_validity", "user_story_relevance"]]
         .mean()
         .reset_index()
)

# Rename for readability in plot
agg["moscow_label"] = agg["moscow_label"].map({
    "m": "Must",
    "s": "Should",
    "c": "Could",
    "w": "Won't"
})




COVARS = [
    "ai_theoretical_understanding",
    "ai_practical_experience",
    "current_job",
    "current_education"
]


def ols_with_controls(df, y, focal_x, covars=COVARS, label=""):
    tmp = df[[y, focal_x]].dropna().copy()  # drop NA only for y and focal X
    for c in covars:
        tmp[c] = df[c]  # attach controls without requiring them all to be non-NA

    # Drop rows where controls are missing too, otherwise statsmodels may error
    tmp = tmp[[y, focal_x] + covars].replace([np.inf, -np.inf], np.nan).dropna().copy()

    X = sm.add_constant(tmp[[focal_x] + covars])
    # model = sm.OLS(tmp[y], X).fit()
    model = sm.OLS(tmp[y], X).fit(cov_type="HC3")

    print(f"\n=== {label}: {y} ~ {focal_x} + controls ===")
    print(model.summary())

    # Effect size: partial R^2 for the focal predictor
    t_val = model.tvalues[focal_x]
    df_resid = model.df_resid
    partial_r2 = (t_val ** 2) / ((t_val ** 2) + df_resid)

    print(f"\nEffect size for {focal_x}:")
    print(f"Partial R^2 = {partial_r2:.4f}")

    residuals = model.resid

    from scipy.stats import shapiro
    stat, p = shapiro(residuals)
    print(f"Shapiro-Wilk test: W = {stat:.3f}, p = {p:.3f}")
    if p < 0.05:
        print("Residuals deviate significantly from normality (p < .05)")
    else:
        print("No evidence to reject normality (p ≥ .05)")

    return model
# def ols_with_controls(df, y, focal_x, covars=COVARS, label=""):
#     tmp = df[[y, focal_x]].dropna().copy()  # drop NA only for y and focal X
#     for c in covars:
#         tmp[c] = df[c]  # attach controls without requiring them all to be non-NA
    
#     X = sm.add_constant(tmp[[focal_x] + covars])
#     model = sm.OLS(tmp[y], X).fit()

#     print(f"\n=== {label}: {y} ~ {focal_x} + controls ===")
#     print(model.summary())

#     residuals = model.resid

#     from scipy.stats import shapiro
#     stat, p = shapiro(residuals)
#     print(f"Shapiro-Wilk test: W = {stat:.3f}, p = {p:.3f}")
#     if p < 0.05:
#         print("Residuals deviate significantly from normality (p < .05)")
#     else:
#         print("No evidence to reject normality (p ≥ .05)")

#     return model

def ols_with_controls2(df, y, focal_x, covars=COVARS, label="", as_category=False):
    needed = [y, focal_x] + covars
    tmp = df[needed].replace([np.inf, -np.inf], np.nan).dropna().copy()
    tmp = tmp.reset_index(drop=True)

    if as_category:
        # Treat focal_x like group membership, not a linear number
        dummies = pd.get_dummies(tmp[focal_x], prefix=focal_x, drop_first=True).astype(int)
        X = pd.concat([dummies, tmp[covars]], axis=1)
        focal_terms = list(dummies.columns)
    else:
        X = tmp[[focal_x] + covars]
        focal_terms = [focal_x]

    X = sm.add_constant(X)
    y_vec = tmp[y]

    # Safety check
    print("\nMissing values in X:")
    print(X.isna().sum()[X.isna().sum() > 0])
    print("\nInfinite values in X:")
    print(np.isinf(X.select_dtypes(include=[np.number])).sum())

    model = sm.OLS(y_vec, X).fit()

    print(f"\n=== {label}: {y} ~ {focal_x} + controls ===")
    if as_category:
        print(f"Treating {focal_x} as categorical.")
        print("\nGroup means:")
        print(tmp.groupby(focal_x)[y].agg(["count", "mean", "std", "median"]))

    print(model.summary())

    if as_category and len(focal_terms) > 1:
        hypothesis = " = 0, ".join(focal_terms) + " = 0"
        print("\nOverall treatment effect:")
        print(model.f_test(hypothesis))

    from scipy.stats import shapiro
    stat, p = shapiro(model.resid)
    print(f"Shapiro-Wilk test: W = {stat:.3f}, p = {p:.3f}")

    return model



ols_with_controls2(df, "mean_nvt", "treatment_amount",
                  label="Training effect on INVEST quality",
                  as_category=True)

ols_with_controls2(df, "mean_ac_score", "treatment_amount",
                  label="Training effect on AC quality",
                  as_category=True)

ols_with_controls2(df, "mean_ssf", "treatment_amount",
                  label="Training effect on SSF",
                  as_category=True)

ols_with_controls2(df, "mean_alignment", "treatment_amount",
                  label="Training effect on Alignment",
                  as_category=True)

ols_with_controls2(df, "mean_hcd", "treatment_amount",
                  label="Training effect on HCD",
                  as_category=True)

ols_with_controls2(df, "mean_vsd", "treatment_amount",
                  label="Training effect on VSD",
                  as_category=True)


# ols_with_controls(df, "total_correct", "treatment_amount", label="Training effect on correctness")
# ols_with_controls(df, "mean_ssf", "treatment_amount", label="Training effect on SSF")
# ols_with_controls(df, "mean_nvt", "treatment_amount", label="Training effect on INVEST quality")
# ols_with_controls(df, "mean_ac_score", "treatment_amount", label="Training effect on AC quality")

ols_with_controls(df, "total_correct", "mean_nvt", label="Controlled NVT")
ols_with_controls(df, "total_correct", "mean_ac_score", label="Controlled AC")

ols_with_controls(df, "total_correct", "mean_ssf", label="Controlled SSF")
ols_with_controls(df, "total_correct", "mean_alignment", label="Controlled SSF")
ols_with_controls(df, "total_correct", "mean_hcd", label="Controlled SSF")
ols_with_controls(df, "total_correct", "mean_vsd", label="Controlled SSF")

# ols_with_controls(df, "total_correct", "mean_user_story_relevance", label="Controlled SSF")
# ols_with_controls(df, "total_correct", "mean_scenario_validity", label="Controlled SSF")


ols_with_controls(df, "total_correct", "reference_freq", label="Controlled SSF")
ols_with_controls(df, "total_correct", "system_reference", label="Controlled SSF")


ols_with_controls(df,"total_correct", "mean_must_ac_quality", label="Do participants who marked higher-quality ACs as Must perform better on AI component task?")
# ols_with_controls(df,"total_correct", "mean_wont_ac_quality", label="Do participants who reject lower-quality ACs (Won't) perform better on the AI component task?")



