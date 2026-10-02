import re
import pandas as pd

# 1 is numbers
# 2 is text
RETURN_MODE = 1

class QualtricsMapping:

    

    @staticmethod
    def normalize_text(text):
        if pd.isnull(text):
            # print("was empty")
            return ""
        # Remove non-printable characters, normalize whitespace, lowercase
        text = str(text)
        text = re.sub(r"[^\x20-\x7E]", "", text)  # remove non-ASCII printable chars
        text = re.sub(r"\s+", " ", text)          # normalize all whitespace
        return text.strip().lower()

    @staticmethod
    def map_ai_knowledge(val):
        val = QualtricsMapping.normalize_text(val)

        if RETURN_MODE == 1:
            if "no knowledge" in val:
                return 1
            elif "basic familiarity" in val:
                return 2
            elif "moderate understanding" in val:
                return 3
            elif "strong understanding" in val:
                return 4
            elif "expert-level knowledge" in val:
                return 5
            exit(1) 
            return None

        else:
            if "no knowledge" in val:
                return "no knowledge" 
            elif "basic familiarity" in val:
                return "basic familiarity"
            elif "moderate understanding" in val:
                return "moderate understanding"
            elif "strong understanding" in val:
                return "strong understanding"
            elif "expert-level knowledge" in val:
                return "expert-level knowledge"
            exit(1) 
            return None

    @staticmethod
    def map_ai_practical_experience(val):
        val = QualtricsMapping.normalize_text(val)
        if RETURN_MODE == 1:
            if "no experience" in val:
                return 1
            elif "minimal experience" in val:
                return 2
            elif "some experience" in val:
                return 3
            elif "substantial experience" in val:
                return 4
            elif "expert-level experience" in val:
                return 5
            exit(1) 
            return None

        else:
            if "no experience" in val:
                return "no experience"
            elif "minimal experience" in val:
                return "minimal experience"
            elif "some experience" in val:
                return "some experience"
            elif "substantial experience" in val:
                return "substantial experience"
            elif "expert-level experience" in val:
                return "expert-level experience"
            exit(1) 
            return None

    @staticmethod
    def map_system_component_reference(val):
        val = QualtricsMapping.normalize_text(val)

        if RETURN_MODE == 1:
            if "at all" in val:
                return 1
            elif "glanced" in val:
                return 2
            elif "skimmed" in val:
                return 3
            elif "referred" in val:
                return 4
            elif "carefully" in val:
                return 5
            elif "other":
                return 6
            exit(1) 

        else:
            if "at all" in val:
                return "didn't-look"
            elif "glanced" in val:
                return "glanced"
            elif "skimmed" in val:
                return "skimmed"
            elif "referred" in val:
                return "referred"
            elif "carefully" in val:
                return "carefully"
            elif "other":
                return "other"
            exit(1) 

    @staticmethod
    def map_reference_freq(val):
        # val = QualtricsMapping.normalize_text(val)
        # print(val)
        float_val = float(val)
        try:
                return int(float_val)
        except Exception as e:
                return 0 


        


    @staticmethod
    def map_ai_background(val):
        val = QualtricsMapping.normalize_text(val)




    @staticmethod
    def map_ai_research_experience(val):
        val = QualtricsMapping.normalize_text(val)
        if RETURN_MODE == 1:
            if "no" in val:
                return 0
            elif "class project":
                return 1
            elif "research":
                return 2
            elif "industry":
                return 3

        else:
            if "no" in val:
                return "no-ai-research-exp"
            elif "class project":
                return "class-ai-research-exp"
            elif "research":
                return "research-ai-research-exp"
            elif "industry":
                return "industry-ai-research-exp"

    @staticmethod
    def map_ai_social_good_experience(val):
        val = QualtricsMapping.normalize_text(val)

        if RETURN_MODE == 1:
            if "no" in val:
                return 0
            else:
                return 1
        else:

            if "no" in val:
                return "no-social-good"
            else:
                return "yes-social-good"

    @staticmethod
    def map_degree_completion(val):
        val = QualtricsMapping.normalize_text(val)

        if RETURN_MODE == 1:
            if "bachelor" in val:
                return 1
            elif "master" in val:
                return 2
            elif "phd" in val:
                return 3
            elif "none" in val:
                return 0
            else:
                return None

        else:
            if "bachelor" in val:
                return "bachelor"
            elif "master" in val:
                return "master"
            elif "phd" in val:
                return "phd"
            elif "none" in val:
                return "none"
            else:
                return None

    @staticmethod
    def map_current_education(val):
        val = QualtricsMapping.normalize_text(val)

        if RETURN_MODE == 1:
            if "undergraduate" in val:
                return 1
            elif "master" in val:
                return 2
            elif "phd" in val:
                return 3
            elif "not currently" in val:
                return 0
            else:
                return None
        else:
            if "undergraduate" in val:
                return "undergraduate"
            elif "master" in val:
                return "master"
            elif "phd" in val:
                return "phd"
            elif "not currently" in val:
                return "not currently"
            else:
                return None

    @staticmethod
    def map_current_employment(val):
        val = QualtricsMapping.normalize_text(val)

        if RETURN_MODE == 1:

            if "related field in industry" in val:
                return 0
            elif "related field in academia" in val:
                return 1
            elif "in another field in industry" in val:
                return 2
            elif "in another field in academia" in val:
                return 3
            elif "self employed" in val:
                return 4
            else:
                return 5
            
        else:

            if "related field in industry" in val:
                return "cs-industry"
            elif "related field in academia" in val:
                return "cs-academia"
            elif "in another field in industry" in val:
                return "other-industry"
            elif "in another field in academia" in val:
                return "other-academia"
            elif "self employed" in val:
                return "self-employed"
            else:
                return "not-working"

        

    @staticmethod
    def map_age(val):
        val = QualtricsMapping.normalize_text(val)
        if RETURN_MODE == 1:
            if "less than" in val:
                return 0
            elif "18 - 24" in val:
                return 1
            elif "25 - 39" in val:
                return 2
            elif "40" in val:
                return 3
            else:
                return None
        else:

            if "less than" in val:
                return "< 18"
            elif "18 - 24" in val:
                return "18 - 24"
            elif "25 - 39" in val:
                return "25 - 39"
            elif "40" in val:
                return "> 40"
            else:
                return None


    @staticmethod
    def map_gender(val):
        val = QualtricsMapping.normalize_text(val)
        if RETURN_MODE == 1:
            if "woman" in val:
                return 0
            elif "man" in val:
                return 1
            elif "binary" in val:
                return 2
            elif "queer" in val:
                return 3
            elif "self-describe" in val:
                return 4
            elif "prefer not" in val:
                return 5
            else:
                return None
        else:

            if "woman" in val:
                return "woman"
            elif "man" in val:
                return "man"
            elif "binary" in val:
                return "non-binary"
            elif "queer" in val:
                return "queer"
            elif "self-describe" in val:
                return "self-describe"
            elif "prefer not" in val:
                return "prefer-not"
            else:
                return None


    question_map = {
        "cady": {
            1: {"US": "Q103", "AC": "Q114", "M": "Q115"},
            2: {"US": "Q300", "AC": "Q116", "M": "Q117"},
            3: {"US": "Q109", "AC": "Q119", "M": "Q120"},
            4: {"US": "Q110", "AC": "Q121", "M": "Q122"},
            5: {"US": "Q111", "AC": "Q123", "M": "Q124"},
        },
        "josie": {
            1: {"US": "Q173", "AC": "Q174", "M": "Q175"},
            2: {"US": "Q176", "AC": "Q177", "M": "Q178"},
            3: {"US": "Q179", "AC": "Q180", "M": "Q181"},
            4: {"US": "Q182", "AC": "Q183", "M": "Q184"},
            5: {"US": "Q185", "AC": "Q186", "M": "Q187"},
        },
        "ben": {
            1: {"US": "Q195", "AC": "Q196", "M": "Q197"},
            2: {"US": "Q198", "AC": "Q199", "M": "Q200"},
            3: {"US": "Q201", "AC": "Q202", "M": "Q203"},
            4: {"US": "Q204", "AC": "Q205", "M": "Q206"},
            5: {"US": "Q207", "AC": "Q208", "M": "Q209"},
        },
        "megan": {
            1: {"US": "Q217", "AC": "Q218", "M": "Q219"},
            2: {"US": "Q220", "AC": "Q221", "M": "Q222"},
            3: {"US": "Q223", "AC": "Q224", "M": "Q225"},
            4: {"US": "Q226", "AC": "Q227", "M": "Q228"},
            5: {"US": "Q229", "AC": "Q230", "M": "Q231"},
        }
    }



    def split_user_stories(raw_text):
        if pd.isna(raw_text) or not str(raw_text).strip():
            return []

        # Keep your normalization + whitespace collapse
        text = QualtricsMapping.normalize_text(str(raw_text))
        text = re.sub(r'\s+', ' ', text).strip()

        # Insert separators BEFORE inline enumerations like "2. as"/"3) Given"
        text = re.sub(
            r'(?<!^)\s*(?=(\d+[\.\)])\s*(?:as|given)\b)',
            ' ||| ',
            text,
            flags=re.IGNORECASE
        )

        # Split when a period/semicolon is directly followed by a new story ("as"/"given")
        text = re.sub(r'\.\s*(?=(?:as|given)\b)', '. ||| ', text, flags=re.IGNORECASE)
        text = re.sub(r';\s*(?=(?:as|given)\b)', '; ||| ', text, flags=re.IGNORECASE)

        # Split on our hard separators or newlines
        parts = re.split(r'\s*\|\|\|\s*|(?:\r?\n)+', text)

        stories = []
        for p in parts:
            s = p.strip().strip('"').strip("'")
            if not s:
                continue

            # Skip fragments that are just a list marker like "2." or "3)"
            if re.fullmatch(r'\(?\d+\s*[\.\)]', s):
                continue

            # Strip a leading enumeration (but otherwise keep text unchanged)
            s = re.sub(r'^\s*\(?\d+\s*[\.\)]\s*', '', s)

            # Require that a story starts with "as"/"given"
            if not re.match(r'^(?:as|given)\b', s, flags=re.IGNORECASE):
                continue

            stories.append(s)

        return stories




        
    def split_ac(raw_text):
        """Split a free-text cell into separate acceptance criteria in GWT format."""
        if pd.isna(raw_text) or not str(raw_text).strip():
            return []

        text = QualtricsMapping.normalize_text(raw_text)

        # Use lookahead so 'given' stays attached to its clause.
        parts = re.split(r"(?=\bGiven\b)", text, flags=re.IGNORECASE)

        given_parts = []
        for part in parts:
            # Keep only strings that start with Given
            if re.search(r"^\s*\bGiven\b", part, flags=re.IGNORECASE):
                cleaned = part.strip()
                given_parts.append(cleaned)

        return given_parts
    

