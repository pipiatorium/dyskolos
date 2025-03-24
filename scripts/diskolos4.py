import asyncio
import os
import math
import re
import json
from datetime import datetime
from typing import Dict, Any, List, Tuple
from anthropic import AsyncAnthropic
import os
import inspect
from difflib import SequenceMatcher
import random

# Print script location to check which file is actually running
print(f"Running script from: {inspect.getfile(inspect.currentframe())}")
print(f"Current directory: {os.getcwd()}")
print(f"Environment variables: {list(os.environ.keys())}")

# ==============LOAD AND SAVE HISTORY==================
def load_story_history():
    """Load the history of generated story configurations"""
    history_file = os.path.join(os.path.dirname(__file__), "story_history.json")
    
    if os.path.exists(history_file):
        try:
            with open(history_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading story history: {e}")
    
    # Return default structure if file doesn't exist or has issues
    return {
        "recent_combinations": [],
        "last_by_day": {str(i): {} for i in range(7)},
        "technique_counter": 0
    }

def save_story_history(history):
    """Save the updated story history"""
    history_file = os.path.join(os.path.dirname(__file__), "story_history.json")
    
    try:
        with open(history_file, "w", encoding="utf-8") as f:
            json.dump(history, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Error saving story history: {e}")
        
# ===============END LOAD AND SAVE HISTORY===================

# =================NARRATIVE===================
# Story elements
GENRES = [
    "διήγημα περὶ ἀρετῆς",  # virtue story
    "κωμῳδία",              # comedy
    "τραγῳδία",             # tragedy
    "μῦθος",                # myth/fable
    "ἱστορικὴ ἀφήγησις",    # historical narrative
    "διάλογος φιλοσοφικός", # philosophical dialogue
    "ῥητορικὸς λόγος"       # rhetorical speech
]

PROTAGONISTS = [
    "ἔμπορος",       # merchant
    "στρατηγός",     # general
    "φιλόσοφος",     # philosopher
    "τεχνίτης",      # craftsman
    "γεωργός",       # farmer
    "ἱερεύς",        # priest
    "ῥήτωρ",         # orator
    "ναύτης",        # sailor
    "γυνὴ ἀθηναία",  # Athenian woman
    "μέτοικος"       # resident foreigner
]

SETTINGS = [
    "ἀγορά",        # marketplace
    "ἐκκλησία",     # assembly
    "θέατρον",      # theater
    "οἰκία",        # home
    "λιμήν",        # harbor
    "γυμνάσιον",    # gymnasium
    "ἀγρός",        # field/countryside
    "συμπόσιον",    # symposium
    "δικαστήριον",  # court
    "τείχη"         # city walls
]

PLOT_ELEMENTS = [
    "στάσις πολιτική",      # political unrest
    "ἔρως",                 # love
    "ναυμαχία",             # naval battle
    "πανήγυρις",            # festival
    "μυστήρια",             # mysteries
    "ἀγὼν δικανικός",       # legal dispute
    "ἑορτὴ θρησκευτική",    # religious ceremony
    "ἐπιδημία",             # epidemic
    "θυσία",                # sacrifice
    "συμπόσιον"             # symposium
]

# Narrative techniques - provide variety in storytelling approaches
NARRATIVE_TECHNIQUES = [
    "Διήγησαι τὴν ἱστορίαν ἐκ τοῦ πρώτου προσώπου.",  # First-person narrative
    "Χρῆσαι διαλόγῳ μεταξὺ τῶν προσώπων τῆς ἱστορίας.", # Use dialogue between characters
    "Ἄρξαι ἀπὸ τοῦ τέλους καὶ πρὸς τὴν ἀρχὴν βάδιζε.", # Start from end and work backwards
    "Διήγησαι ὡς ἐπιστολὴν πρός τινα φίλον.",  # Frame as letter to a friend
    "Ἔκθες τὴν ἱστορίαν ὡς μῦθον διδακτικόν.",  # Present as instructive fable
    "Διήγησαι ὡς μάρτυς τῶν γεγονότων.",  # Narrate as witness to events
    "Παρουσίασον ὡς λόγον ἐν τῇ ἐκκλησίᾳ.",  # Present as speech in assembly
    "Περίγραψον ὡς ἀφήγησιν ἐν συμποσίῳ.",  # Describe as tale told at symposium
    "Συμπερίλαβε ὄνειρον σημαντικὸν τῇ διηγήσει.", # Include significant dream
    "Χρῆσαι παραλλήλοις πλοκαῖς δυοῖν προσώποιν."  # Use parallel storylines
]
# =============END NARRATIVE===============

def generate_story_config():
    """Generate a story configuration that avoids recent combinations"""
    # Load story history
    history = load_story_history()
    recent_combinations = history["recent_combinations"]
    
    # Get current day of week (0=Monday, 6=Sunday)
    day_of_week = datetime.now().weekday()
    day_key = str(day_of_week)
    
    # Get last configuration used for this day of week
    last_by_day = history["last_by_day"][day_key]
    
    # Select narrative technique using counter
    technique_counter = history["technique_counter"]
    technique = NARRATIVE_TECHNIQUES[technique_counter % len(NARRATIVE_TECHNIQUES)]
    
    # Try to find a unique combination
    for _ in range(20):  # Limit attempts
        genre = random.choice(GENRES)
        protagonist = random.choice(PROTAGONISTS)
        setting = random.choice(SETTINGS)
        plot = random.choice(PLOT_ELEMENTS)
        
        # Create tuple of core elements
        combination = (genre, protagonist, setting, plot)
        
        # Check if combination was used recently
        if combination not in recent_combinations:
            # Also check if too similar to last story for this day
            if (last_by_day.get("genre") != genre or 
                last_by_day.get("protagonist") != protagonist or
                last_by_day.get("setting") != setting):
                
                # Update history
                if len(recent_combinations) >= 10:
                    recent_combinations.pop(0)  # Remove oldest
                recent_combinations.append(combination)
                
                # Update last used for this day
                history["last_by_day"][day_key] = {
                    "genre": genre,
                    "protagonist": protagonist,
                    "setting": setting,
                    "plot": plot,
                    "technique": technique
                }
                
                # Update technique counter
                history["technique_counter"] = (technique_counter + 1) % len(NARRATIVE_TECHNIQUES)
                
                # Save updated history
                save_story_history(history)
                
                # Return the configuration
                return {
                    "genre": genre,
                    "protagonist": protagonist,
                    "setting": setting,
                    "plot": plot,
                    "technique": technique,
                    "day_of_week": day_of_week
                }
    
    # If no suitable combination found, fall back to a random one
    return {
        "genre": random.choice(GENRES),
        "protagonist": random.choice(PROTAGONISTS),
        "setting": random.choice(SETTINGS),
        "plot": random.choice(PLOT_ELEMENTS),
        "technique": technique,
        "day_of_week": day_of_week
    }


def load_api_key():
    try:
        if 'ANTHROPIC_API_KEY' not in os.environ:
            raise ValueError("ANTHROPIC_API_KEY environment variable not found")
            
        api_key = os.environ.get('ANTHROPIC_API_KEY')
        
        if not api_key:
            raise ValueError("API key is empty")
        
        return api_key
    except Exception as e:
        print(f"Error reading API key: {e}")
        exit(1)

# Get API key at module level
API_KEY = load_api_key()

class Agent:
    def __init__(self, name: str, role: str, system_prompt: str):
        self.name = name
        self.role = role
        self.system_prompt = system_prompt
        self.client = AsyncAnthropic(api_key=API_KEY)

# Add these modifications to your analyze method in the Agent class:

    async def analyze(self, prompt_content: str) -> Dict[str, Any]:
        try:
            print(f"Starting {self.name} API call...")
            response = await self.client.messages.create(
                model="claude-3-7-sonnet-20250219",
                max_tokens=2048,
                system=self.system_prompt,
                messages=[{"role": "user", "content": prompt_content}]
            )
            print(f"Completed {self.name} API call")
            
            # Handle the response content properly
            content = response.content
            if isinstance(content, list):
                content = content[0].text if hasattr(content[0], 'text') else str(content[0])
            
            return {
                "agent": self.name,
                "response": content,
                "tokens": response.usage.input_tokens + response.usage.output_tokens
            }
        except Exception as e:
            error_msg = f"Analysis failed for {self.name}: {str(e)}"
            print(error_msg)
            # Return a valid dictionary with error information instead of None
            return {
                "agent": self.name,
                "response": error_msg,
                "tokens": 0
            }

class DiskolosEditor(Agent):
    def __init__(self):
        super().__init__(
            name="Diskolos",
            role="Editor",
            system_prompt="You are an Attic Greek grammarian. Your job is to review and correct stories written in Attic Greek. Simply provide the corrected version of the story without any explanations, comments, or notes about errors. Just return the corrected title and story text."
        )

class AtticGreekWriter(Agent):
    def __init__(self):
        super().__init__(
            name="Attic Greek Writer",
            role="Writer",
            system_prompt="""You are an expert in authentic Attic Greek prose from the 5th century BCE Athens. 
            
            When writing stories:
            1. Always begin with a specific, descriptive title
            2. Use vocabulary and expressions exclusively from attested Attic Greek sources
            3. Ensure all cultural references are historically accurate for 5th century BCE Athens
            4. Write in clear Attic prose suitable for intermediate Greek language students
            5. Include proper Greek accentuation throughout
            6. Keep stories between 200-500 words in length
            
            For each writing task, follow the specific instructions provided in the prompt regarding genre, characters, setting, plot, and narrative technique."""
        )

class AtticVocabularyAgent(Agent):
    def __init__(self):
        super().__init__(
            name="Vocabulary Extractor",
            role="Philologist",
            system_prompt="""You are an expert Attic Greek philologist. Your task is to analyze the provided Attic Greek story and identify difficult words that intermediate-level students would struggle with.
            
            For each paragraph:
            1. Select 4-6 challenging words or phrases
            2. Provide the exact Latin equivalent (no English translations)
            
            Format your response as a valid JSON object where:
            - Each key is the paragraph text (the full paragraph)
            - Each value is an array of objects with "word" and "latin" properties
            
            IMPORTANT FORMATTING RULES:
            1. Use double quotes for ALL strings in the JSON
            2. Do not use trailing commas
            3. Make sure all brackets and braces are properly closed
            4. Your entire response must be a single valid JSON object
            5. Do not include any explanation text outside the JSON object
            
            Example format:
            {
              "Ὄρθρος ἦν, καὶ πολλοὶ τῶν Ἀθηναίων εἰς τὴν ἀγορὰν συνέρρεον.": [
                {"word": "συνέρρεον", "latin": "confluo"}
              ],
              "Ἐγὼ δὲ παρὰ τῇ Ποικίλῃ στοᾷ ἑστὼς τοὺς φίλους προσεδεχόμην.": [
                {"word": "ἑστώς", "latin": "stans"}, 
                {"word": "προσεδεχόμην", "latin": "exspectabam"}
              ]
            }"""
        )


def similarity_ratio(a, b):
    """Return a similarity ratio between two strings"""
    return SequenceMatcher(None, a, b).ratio()

    
async def write_story():
    writer = AtticGreekWriter()
    
    # Get a diverse story configuration
    config = generate_story_config()
    print(f"\nGenerated story configuration: {config}")
    
    # Create dynamic prompt
    prompt = f"Γράψον {config['genre']} περὶ {config['protagonist']} ἐν {config['setting']} περὶ {config['plot']}. {config['technique']}"
    print("\nAsking writer to create a story with prompt: " + prompt)
    
    try:
        result = await writer.analyze(prompt)
        
        if not result:
            print("Error: Writer returned None instead of a response")
            return "Error generating story", 0, {"headline": "Story Generation Error"}
            
        print(f"\n✍️ STORY FROM {result['agent'].upper()}")
        print("=" * 50)
        print(result['response'].strip())

        # Extract the title (first line) and remaining story
        lines = result['response'].split('\n')
        headline = lines[0].strip() if lines else "Untitled Story"
        
        # Story content is everything after the title
        story_body = '\n'.join(lines[1:]).strip() if len(lines) > 1 else ""

        return story_body, result.get('tokens', 0), {
            "headline": headline,
            "config": config  # Store the configuration in metadata
        }
    except Exception as e:
        print(f"Error in write_story: {str(e)}")
        return "Error generating story.", 0, {"headline": "Story Generation Error"}
        
async def review_story(story, metadata):
    editor = DiskolosEditor()
    prompt = f"""Please review the following Attic Greek story:

Title: {metadata["headline"]}

{story}

Provide corrections if needed and approve for publication if it meets standards of classical Attic Greek."""
    
    print("\nSending story to Diskolos for grammar review...")
    result = await editor.analyze(prompt)
    
    print(f"\n📝 REVIEW FROM {result['agent'].upper()}")
    print("=" * 50)
    print(result['response'].strip())
    
    return result['response'], result['tokens']

async def extract_vocabulary(story, metadata):
    vocab_agent = AtticVocabularyAgent()
    prompt = f"""Please analyze the following Attic Greek story and extract difficult vocabulary with Latin equivalents:

Title: {metadata["headline"]}

{story}

Extract 1-3 challenging words per paragraph with their Latin equivalents."""
    
    print("\nExtracting vocabulary with Latin equivalents...")
    result = await vocab_agent.analyze(prompt)
    
    print(f"\n📚 VOCABULARY FROM {result['agent'].upper()}")
    print("=" * 50)
    print(result['response'].strip())
    
    # First attempt: try parsing the raw JSON response
    try:
        vocab_data = json.loads(result['response'])
        print(f"\nSuccessfully parsed vocabulary data: {len(vocab_data)} paragraphs")
        return vocab_data, result['tokens']
    except json.JSONDecodeError as e:
        print(f"Warning: Could not parse vocabulary response as JSON. Error: {e}")
        
        # Second attempt: fix common JSON issues
        fixed_json = result['response'].strip()
        
        # 1. Remove any text before the first { or after the last }
        start_idx = fixed_json.find('{')
        end_idx = fixed_json.rfind('}')
        if start_idx != -1 and end_idx != -1:
            fixed_json = fixed_json[start_idx:end_idx+1]
            print("Trimmed JSON to extract just the object")
        
        # 2. Fix trailing commas in arrays and objects
        fixed_json = re.sub(r',\s*}', '}', fixed_json)
        fixed_json = re.sub(r',\s*]', ']', fixed_json)
        
        try:
            vocab_data = json.loads(fixed_json)
            print("Successfully parsed fixed JSON!")
            return vocab_data, result['tokens']
        except json.JSONDecodeError:
            print("Automatic JSON fixing failed. Attempting manual parsing...")
            
            # Third attempt: fall back to manual parsing
            vocab_data = parse_vocabulary_manually(result['response'])
            print(f"Manually extracted {len(vocab_data)} paragraph entries")
            return vocab_data, result['tokens']

def parse_vocabulary_manually(response_text):
    """Parse vocabulary data from a potentially malformed JSON response"""
    vocab_dict = {}
    
    print("Attempting manual parsing of vocabulary data...")
    
    # Look for patterns that match paragraph-vocabulary pairs
    import re
    
    # First try to extract complete paragraph-vocabulary entries
    entry_pattern = r'"([^"]+)"\s*:\s*\[(.*?)\]'
    for entry_match in re.finditer(entry_pattern, response_text, re.DOTALL):
        try:
            paragraph = entry_match.group(1)
            items_text = entry_match.group(2)
            
            # Extract word-latin pairs
            vocab_items = []
            item_pattern = r'\{\s*"word"\s*:\s*"([^"]+)"\s*,\s*"latin"\s*:\s*"([^"]+)"\s*\}'
            for item_match in re.finditer(item_pattern, items_text):
                word = item_match.group(1)
                latin = item_match.group(2)
                vocab_items.append({"word": word, "latin": latin})
            
            if vocab_items:
                vocab_dict[paragraph] = vocab_items
                print(f"Manually extracted {len(vocab_items)} items for paragraph: {paragraph[:30]}...")
        except Exception as e:
            print(f"Error parsing entry: {e}")
    
    print(f"Manual parsing complete. Found {len(vocab_dict)} paragraphs with vocabulary.")
    return vocab_dict

# ============== date conversion ================
def greek_numeral(number):
    """Simple conversion for small numbers to Greek text numbers"""
    greek_numbers = {
        1: "πρώτῃ",
        2: "δευτέρᾳ",
        3: "τρίτῃ",
        4: "τετάρτῃ",
        5: "πέμπτῃ",
        6: "ἕκτῃ",
        7: "ἑβδόμῃ",
        8: "ὀγδόῃ",
        9: "ἐνάτῃ",
        10: "δεκάτῃ"
    }
    return greek_numbers.get(number, str(number))

def greek_number_to_text(number):
    """Convert a number to Greek text format for Olympiad years"""
    # Only handling numbers we need for Olympiads in modern era
    if number <= 10:
        return greek_numeral(number)
    # For larger numbers a more complex system would be needed
    return f"{number}"

def get_attic_month(date_obj):
    """
    Get appropriate Attic month based on Gregorian date with adjustments for transitions.
    The Attic calendar was lunar-based, so months don't align perfectly with our calendar.
    This function adjusts transition points between months to better reflect actual usage.
    """
    # Base month mapping
    attic_months = {
        1: "Ποσειδεών",    # Poseideon (Dec/Jan)
        2: "Γαμηλιών",     # Gamelion (Jan/Feb)
        3: "Ἀνθεστηριών",  # Anthesterion (Feb/Mar)
        4: "Ἐλαφηβολιών",  # Elaphebolion (Mar/Apr)
        5: "Μουνιχιών",    # Mounichion (Apr/May)
        6: "Θαργηλιών",    # Thargelion (May/Jun)
        7: "Σκιροφοριών",  # Skirophorion (Jun/Jul)
        8: "Ἑκατομβαιών",  # Hekatombaion (Jul/Aug)
        9: "Μεταγειτνιών", # Metageitnion (Aug/Sep)
        10: "Βοηδρομιών",  # Boedromion (Sep/Oct)
        11: "Πυανεψιών",   # Pyanepsion (Oct/Nov)
        12: "Μαιμακτηριών" # Maimakterion (Nov/Dec)
    }
    
    # Apply adjustments for dates near month transitions
    month = date_obj.month
    day = date_obj.day
    
    # Setting transition points around mid-month (day 15)
    # These adjustments attempt to better align with lunar months
    if month == 1 and day >= 15:
        return "Γαμηλιών"      # Mid-Jan → Gamelion
    elif month == 2 and day >= 15:
        return "Ἀνθεστηριών"   # Mid-Feb → Anthesterion
    elif month == 3 and day >= 15:
        return "Ἐλαφηβολιών"   # Mid-Mar → Elaphebolion
    elif month == 4 and day >= 15:
        return "Μουνιχιών"     # Mid-Apr → Mounichion
    elif month == 5 and day >= 15:
        return "Θαργηλιών"     # Mid-May → Thargelion
    elif month == 6 and day >= 15:
        return "Σκιροφοριών"   # Mid-Jun → Skirophorion
    elif month == 7 and day >= 15:
        return "Ἑκατομβαιών"   # Mid-Jul → Hekatombaion
    elif month == 8 and day >= 15:
        return "Μεταγειτνιών"  # Mid-Aug → Metageitnion
    elif month == 9 and day >= 15:
        return "Βοηδρομιών"    # Mid-Sep → Boedromion
    elif month == 10 and day >= 15:
        return "Πυανεψιών"     # Mid-Oct → Pyanepsion
    elif month == 11 and day >= 15:
        return "Μαιμακτηριών"  # Mid-Nov → Maimakterion
    elif month == 12 and day >= 15:
        return "Ποσειδεών"     # Mid-Dec → Poseideon
    
    # For dates in the first half of each month, use the previous month in the Attic calendar
    if month == 1 and day < 15:
        return "Ποσειδεών"     # Early Jan → Poseideon
    elif month == 2 and day < 15:
        return "Γαμηλιών"      # Early Feb → Gamelion
    elif month == 3 and day < 15:
        return "Ἀνθεστηριών"   # Early Mar → Anthesterion
    elif month == 4 and day < 15:
        return "Ἐλαφηβολιών"   # Early Apr → Elaphebolion
    elif month == 5 and day < 15:
        return "Μουνιχιών"     # Early May → Mounichion
    elif month == 6 and day < 15:
        return "Θαργηλιών"     # Early Jun → Thargelion
    elif month == 7 and day < 15:
        return "Σκιροφοριών"   # Early Jul → Skirophorion
    elif month == 8 and day < 15:
        return "Ἑκατομβαιών"   # Early Aug → Hekatombaion
    elif month == 9 and day < 15:
        return "Μεταγειτνιών"  # Early Sep → Metageitnion
    elif month == 10 and day < 15:
        return "Βοηδρομιών"    # Early Oct → Boedromion
    elif month == 11 and day < 15:
        return "Πυανεψιών"     # Early Nov → Pyanepsion
    elif month == 12 and day < 15:
        return "Μαιμακτηριών"  # Early Dec → Maimakterion
    
    # Fallback (should never reach here with the comprehensive conditions above)
    return attic_months[month]

def convert_to_attic_date(date_obj):
    """
    Convert a modern date to the Attic calendar format.
    
    Parameters:
    date_obj (datetime): A datetime object representing a modern date
    
    Returns:
    str: A string with the date in Attic Greek format
    """
    # Get the appropriate Attic month using our new function
    attic_month = get_attic_month(date_obj)
    
    # Convert day to lunar cycle (simplified)
    day = date_obj.day
    
    if day <= 10:
        day_phrase = f"{greek_numeral(day)} ἱσταμένου"
    elif day <= 20:
        day_phrase = f"{greek_numeral(day - 10)} ἐπὶ δέκα"
    else:
        # Counting backwards from 30 for the last phase
        days_remaining = 30 - day + 1
        day_phrase = f"{greek_numeral(days_remaining)} φθίνοντος"
    
    # Convert year to Olympiad
    # First Olympic games were held in 776 BCE
    year_ce = date_obj.year
    years_since_first_olympiad = year_ce + 776 - 1  # -1 because there's no year 0
    olympiad_number = math.ceil(years_since_first_olympiad / 4)
    olympiad_year = (years_since_first_olympiad % 4) or 4
    
    olympiad_text = f"Ὀλυμπιάδος {greek_number_to_text(olympiad_number)} ἔτους {greek_number_to_text(olympiad_year)}"
    
    # Combine all parts
    attic_date = f"{attic_month} {day_phrase}, {olympiad_text}"
    
    return attic_date

# ===============end date conversion ================

# ================SAVE STORY=================
def save_to_website(story, corrected_story, vocab_data, metadata):
    from difflib import SequenceMatcher
    
    def similarity_ratio(a, b):
        """Return a similarity ratio between two strings"""
        return SequenceMatcher(None, a, b).ratio()
    
    today = datetime.now()
    date_str = today.strftime("%Y%m%d")
    
    # Generate both formats
    human_date = today.strftime("%B %d, %Y")
    attic_date = convert_to_attic_date(today)
    
    # Create simplified Attic date format for display
    simple_month = get_attic_month(today)
    
    # Paths (template in same dir as script)
    script_dir = os.path.dirname(__file__)
    docs_path = os.path.join(os.path.dirname(script_dir), "docs")
    stories_path = os.path.join(docs_path, "stories")
    template_path = os.path.join(script_dir, "story_template.html")
    
    os.makedirs(stories_path, exist_ok=True)
    
    # Get metadata and clean up any # symbols
    headline = metadata["headline"]
    headline = headline.replace('#', '').strip()
    
    # Create filename
    cleaned_headline = re.sub(r'[^\w\s-]', '', headline.lower())
    cleaned_headline = re.sub(r'[\s-]+', '-', cleaned_headline)
    cleaned_headline = cleaned_headline[:40].strip('-')
    filename = f"{date_str}-{cleaned_headline}.html"
    
    # Parse the corrected story into paragraphs
    paragraphs = [p.strip() for p in corrected_story.split("\n\n") if p.strip()]
    
    # Skip first paragraph if it contains the headline
    if paragraphs and headline.strip() in paragraphs[0]:
        print(f"Skipping first paragraph as it contains the headline")
        paragraphs = paragraphs[1:]
    
    # Process vocabulary tooltips (same as original code)
    story_content = ""
    vocab_matches = 0
    vocab_words_highlighted = 0
    
    for i, paragraph in enumerate(paragraphs):
        # Create a version of the paragraph with highlighted vocabulary words
        marked_paragraph = paragraph
        
        # Find matching vocabulary for this paragraph
        matches = []
        
        # First try exact match
        if paragraph in vocab_data and vocab_data[paragraph]:
            print(f"Found exact match for paragraph {i}")
            matches = vocab_data[paragraph]
            vocab_matches += 1
        else:
            # Try to find closest matching paragraph using similarity ratio
            best_match = None
            highest_similarity = 0.6  # Set minimum threshold for similarity
            
            for key in vocab_data:
                # Skip empty keys
                if not key.strip():
                    continue
                    
                sim = similarity_ratio(paragraph, key)
                if sim > highest_similarity:
                    highest_similarity = sim
                    best_match = key
            
            # If we found a reasonable match, use its vocabulary
            if best_match:
                print(f"Paragraph {i}: Found similar match with similarity {highest_similarity:.2f}")
                matches = vocab_data[best_match]
                vocab_matches += 1
            else:
                print(f"Paragraph {i}: No matching vocabulary found")
        
        # For each vocabulary word, highlight it in the text with tooltips
        for j, item in enumerate(matches):
            greek_word = item['word']
            latin = item['latin']
            
            # Replace the word with a highlighted version with tooltip
            pattern = rf'\b{re.escape(greek_word)}\b'
            replacement = f'<span class="highlighted-word">{greek_word}<span class="tooltip">{latin}</span></span>'
            
            if re.search(pattern, marked_paragraph):
                marked_paragraph = re.sub(pattern, replacement, marked_paragraph, 1)
                vocab_words_highlighted += 1
            else:
                print(f"Warning: Could not find word '{greek_word}' in paragraph {i}")
        
        # Generate HTML for this paragraph
        paragraph_html = f'''
        <div class="text greek{' id="continue-reading"' if i == 0 else ''}">
            {marked_paragraph}
        </div>
        '''
        
        story_content += paragraph_html
    
    print(f"\nFound vocabulary matches for {vocab_matches} out of {len(paragraphs)} paragraphs")
    print(f"Added tooltips for {vocab_words_highlighted} vocabulary words in the text")
    
    # Read template
    try:
        with open(template_path, "r", encoding="utf-8") as f:
            template = f.read()
        print(f"Successfully read template from {template_path}")
    except Exception as e:
        print(f"Error reading template: {e}")
        return
    
    # Create the date span for display
    date_span = f'<span class="story-date" title="{attic_date}">{simple_month} {today.day}, {today.year}</span>'
    
    # Replace placeholders in the template
    story_html = template.replace("{{STORY_TITLE}}", headline)
    story_html = story_html.replace("{{STORY_DATE}}", date_span)
    
    # Check if template supports tooltips or marginalia
    if "{{STORY_CONTENT_WITH_TOOLTIPS}}" in template:
        story_html = story_html.replace("{{STORY_CONTENT_WITH_TOOLTIPS}}", story_content)
        print("Used {{STORY_CONTENT_WITH_TOOLTIPS}} placeholder in template")
    elif "{{STORY_CONTENT_WITH_VOCAB}}" in template:
        story_html = story_html.replace("{{STORY_CONTENT_WITH_VOCAB}}", story_content)
        print("Used {{STORY_CONTENT_WITH_VOCAB}} placeholder in template")
    else:
        # Fallback: Replace {{STORY_CONTENT}} instead
        print("Note: Template doesn't have tooltip or marginalia placeholders, using {{STORY_CONTENT}} instead.")
        story_html = story_html.replace("{{STORY_CONTENT}}", story_content)
    
    # Save story page
    story_path = os.path.join(stories_path, filename)
    try:
        with open(story_path, "w", encoding="utf-8") as f:
            f.write(story_html)
        print(f"Story saved to: {story_path}")
    except Exception as e:
        print(f"Error saving story: {e}")
        return
    
    # Update index page
    index_path = os.path.join(docs_path, "index.html")
    try:
        with open(index_path, "r", encoding="utf-8") as f:
            index_content = f.read()
            
        # Create excerpt from actual story content, not the title
        if len(paragraphs) >= 2:
            # Use the second paragraph for the excerpt
            excerpt = paragraphs[1][:100] + "..." if len(paragraphs[1]) > 100 else paragraphs[1]
        elif len(paragraphs) == 1:
            # If there's only one paragraph, use it but check it's not just the title
            if paragraphs[0].strip() != headline.strip():
                excerpt = paragraphs[0][:100] + "..." if len(paragraphs[0]) > 100 else paragraphs[0]
            else:
                excerpt = "Συνέχισε για να διαβάσεις την ιστορία..."
        else:
            excerpt = "Συνέχισε για να διαβάσεις την ιστορία..."
            
        # Story card for story grid
        story_card = f'''
        <div class="story-card">
            <h3 class="story-title">{headline}</h3>
            <div class="story-meta">
                {date_span}
            </div>
            <p class="story-excerpt">{excerpt}</p>
            <a href="stories/{filename}#continue-reading" class="read-more">Συνέχισε →</a>
        </div>
        '''
        
        # Featured story for top of page
        featured_story = f'''
        <div class="story-card featured">
            <h2 class="story-title">{headline}</h2>
            <div class="story-meta">
                {date_span}
            </div>
            <div class="story-excerpt">
                <p>{excerpt}</p>
                <a href="stories/{filename}#continue-reading" class="read-more">Συνέχισε →</a>
            </div>
        </div>
        '''
        
        # Update featured story section
        featured_pattern = r'<div class="story-card featured">[\s\S]*?</div>\s*</div>'
        if re.search(featured_pattern, index_content):
            index_content = re.sub(featured_pattern, featured_story, index_content, flags=re.DOTALL)
            print("Updated featured story section in index.html")
        else:
            # If no featured story section, add after featured-story section tag
            featured_section = r'<section class="featured-story">'
            if featured_section in index_content:
                index_content = re.sub(featured_section, f'{featured_section}\n{featured_story}', index_content)
                print("Added featured story to featured-story section")
        
        # Add new story to grid (at beginning) - BUT ONLY if it's not already in the index
        story_grid = r'<div class="story-grid">'
        if story_grid in index_content:
            # Check if this is a brand new story (not already in the index)
            if filename not in index_content:
                # Extract all existing story cards
                story_grid_pattern = r'<div class="story-grid">([\s\S]*?)</div>\s*</section>'
                match = re.search(story_grid_pattern, index_content, re.DOTALL)
                
                if match:
                    existing_cards = match.group(1)
                    
                    # Extract individual story cards
                    card_pattern = r'<div class="story-card">[\s\S]*?</div>\s*'
                    card_matches = re.findall(card_pattern, existing_cards)
                    
                    # Keep only the most recent 3 cards (plus our new one = 4 total)
                    # This ensures total of 4 existing cards + 1 new card = 5 cards
                    limited_cards = card_matches[:3] if len(card_matches) > 3 else card_matches
                    
                    # Create new story grid content with new card at the top
                    new_grid_content = f'{story_grid}\n{story_card}\n{"".join(limited_cards)}'
                    
                    # Replace entire story grid section
                    index_content = re.sub(story_grid_pattern, new_grid_content + '</div>\n</section>', index_content, flags=re.DOTALL)
                    print(f"Added new story card to story grid and limited to 5 total stories")
                else:
                    # If pattern not found, just add the new card
                    index_content = re.sub(story_grid, f'{story_grid}\n{story_card}', index_content)
                    print(f"Added new story card to empty story grid")
            else:
                print(f"Story already exists in index, only updating featured section")
        
        # Write updated index.html
        with open(index_path, "w", encoding="utf-8") as f:
            f.write(index_content)
            
        print(f"Index.html updated successfully")
        
    except Exception as e:
        print(f"Error updating index.html: {e}")
        print("This is non-critical - the story page was still created successfully")
# ==============END SAVE STORY==================
# ==============record story generation==========
def record_story_generation(metadata, tokens):
    """Record story generation details for analytics"""
    log_file = os.path.join(os.path.dirname(__file__), "story_generation_log.json")
    
    # Create the entry for this story
    entry = {
        "date": datetime.now().isoformat(),
        "headline": metadata.get("headline", "Untitled"),
        "config": metadata.get("config", {}),
        "tokens": tokens
    }
    
    # Load existing log if available
    try:
        if os.path.exists(log_file):
            with open(log_file, "r", encoding="utf-8") as f:
                log = json.load(f)
        else:
            log = []
            
        # Add new entry
        log.append(entry)
        
        # Save updated log
        with open(log_file, "w", encoding="utf-8") as f:
            json.dump(log, f, ensure_ascii=False, indent=2)
            
    except Exception as e:
        print(f"Error recording story generation: {e}")

async def main():
    # Verify API key at startup
    try:
        test_client = AsyncAnthropic(api_key=API_KEY)
    except Exception as e:
        print(f"Error: Invalid API key configuration: {e}")
        return

    print("\n🌟 ATTIC GREEK STORY GENERATOR 🌟")
    print("=" * 50)
    
    try:
        # Step 1: Writer creates story
        story, writer_tokens, metadata = await write_story()

        # Step 2: Record story generation for analytics
        record_story_generation(metadata, writer_tokens)
        
        # Step 3: Editor corrects the story
        corrected_story, review_tokens = await review_story(story, metadata)
        
        # Step 4: Extract vocabulary with Latin equivalents
        print("\nExtracting vocabulary with Latin equivalents...")
        vocab_data, vocab_tokens = await extract_vocabulary(corrected_story, metadata)
        
        # Debug vocabulary extraction
        print("\n📚 VOCABULARY DATA DEBUGGING:")
        print("=" * 50)
        print(f"Type of vocab_data: {type(vocab_data)}")
        print(f"Number of paragraphs with vocabulary: {len(vocab_data)}")
        
        if vocab_data:
            # Show a sample of the vocabulary data
            sample_key = next(iter(vocab_data))
            print(f"\nSample paragraph key: {sample_key[:50]}..." if len(sample_key) > 50 else sample_key)
            print(f"Sample vocabulary entries: {vocab_data[sample_key]}")
            
            # Count total vocab items
            total_items = sum(len(items) for items in vocab_data.values())
            print(f"Total vocabulary items: {total_items}")
        else:
            print("WARNING: No vocabulary data was extracted!")
        
        # Step 4: Save the corrected story with vocabulary to the website
        if corrected_story:
            save_to_website(story, corrected_story, vocab_data, metadata)
            
            # Track tokens for all agents
            total_tokens = writer_tokens + review_tokens + vocab_tokens
            input_tokens = total_tokens * 0.7  # Approximate input tokens
            output_tokens = total_tokens * 0.3  # Approximate output tokens
            
            # Calculate cost with new pricing
            input_cost = (input_tokens / 1000000) * 3.00
            output_cost = (output_tokens / 1000000) * 15.00
            total_cost = input_cost + output_cost
            
            print(f"\n💰 Estimated API Cost: ${total_cost:.4f}")
            
            # Print workflow summary
            print("\n🔄 WORKFLOW SUMMARY:")
            print("=" * 50)
            print(f"1. Writer wrote '{metadata['headline']}'")
            print(f"2. Diskolos corrected the story")
            print(f"3. Vocabulary agent extracted {len(vocab_data)} paragraphs with vocabulary")
            print(f"4. Story published to website with tooltips")
            print("=" * 50)
            
    except Exception as e:
        print(f"Error during execution: {e}")
        import traceback
        traceback.print_exc()

    
if __name__ == "__main__":
    asyncio.run(main())
