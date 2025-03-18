import asyncio
import os
import math
import re
from datetime import datetime
from typing import Dict, Any, List, Tuple
from anthropic import AsyncAnthropic

import os
import inspect

# Print script location to check which file is actually running
print(f"Running script from: {inspect.getfile(inspect.currentframe())}")
print(f"Current directory: {os.getcwd()}")
print(f"Environment variables: {list(os.environ.keys())}")

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

    async def analyze(self, prompt_content: str) -> Dict[str, Any]:
        try:
            response = await self.client.messages.create(
                model="claude-3-7-sonnet-20250219",
                max_tokens=1024,
                system=self.system_prompt,
                messages=[{"role": "user", "content": prompt_content}]
            )
            
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
            return {
                "agent": self.name,
                "response": f"Analysis failed: {str(e)}",
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
            system_prompt="""Write a complete chronicle in authentic Attic Greek as if you are an observer of 5th century BCE Athenian life. Your account should:

                1. Begin with a specific, descriptive title that reflects the unique content of this particular chronicle (avoid generic titles like 'Life in Athens' or 'Life of Athenians'). Titles should be creative and hint at the main event, character, or situation described in the story.
    
                2. Use vocabulary and expressions exclusively from attested Attic Greek sources (no Koine Greek or later terms)

                3. Include a mix of:
                - Everyday scenes from the Agora, households, or workshops
                - Entertaining anecdotes or humorous incidents
                - References to contemporary figures and landmarks
                - Observations on festivals, theater performances, or athletic contests

                4. Balance serious matters (politics, commerce, military news) with lighter aspects of Athenian life (gossip, celebrations, family events)

                5. Write in clear Attic prose suitable for intermediate Greek language students

                6. Ensure all cultural references and social practices are historically accurate for 5th century BCE Athens

                7. Include at least one brief conversation in authentic Attic dialect

                Your chronicle should be 200-300 words in length, written entirely in Attic Greek with proper accentuation."""
        )

async def write_story():
    writer = AtticGreekWriter()
    
    prompt = "Write a unique chronicle in Attic Greek about a specific incident, character, or event in 5th century BCE Athens. Create a distinctive title that reflects the specific content of your chronicle." 
    print("\nAsking writer to create a story...")
    result = await writer.analyze(prompt)
    
    print(f"\n✍️ STORY FROM {result['agent'].upper()}")
    print("=" * 50)
    print(result['response'].strip())

    # Extract the title (first line) and remaining story
    lines = result['response'].split('\n')
    headline = lines[0].strip() if lines else "Untitled Story"
    
    # Story content is everything after the title
    story_body = '\n'.join(lines[1:]).strip() if len(lines) > 1 else ""

    return story_body, result['tokens'], {
        "headline": headline
    }

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

def save_to_website(story, corrected_story, metadata):
    today = datetime.now()
    date_str = today.strftime("%Y%m%d")  # Keep this for filenames
    
    # Generate both formats
    human_date = today.strftime("%B %d, %Y")  # Keep for reference or fallback
    attic_date = convert_to_attic_date(today)  # Attic date
    
    # Create simplified Attic date format for display: Month name + day number, year
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
    
    # Format story content
    story_content = ""
    paragraphs = [p.strip() for p in corrected_story.split("\n\n") if p.strip()]

    # Skip first paragraph if it contains the headline
    if paragraphs and headline.strip() in paragraphs[0]:
        paragraphs = paragraphs[1:]

    for i, p in enumerate(paragraphs):
        if i == 0:  # First paragraph after skipping title
            story_content += f'<p id="continue-reading">{p}</p>\n'
        else:
            story_content += f"<p>{p}</p>\n"
    
    # Read template
    with open(template_path, "r", encoding="utf-8") as f:
        template = f.read()
    
    # In your HTML template replacements and story cards, use:
    # Simplified date in display, full attic date in tooltip
    date_span = f'<span class="story-date" title="{attic_date}">{simple_month} {today.day}, {today.year}</span>'
    
    # Replace placeholders using the appropriate date format
    story_html = template.replace("{{STORY_TITLE}}", headline)
    story_html = story_html.replace("{{STORY_DATE}}", date_span)
    story_html = story_html.replace("{{STORY_CONTENT}}", story_content)
    
    # Save story page
    with open(os.path.join(stories_path, filename), "w", encoding="utf-8") as f:
        f.write(story_html)
    
    print(f"Story saved to: {os.path.join(stories_path, filename)}")
    
    # Update index page
    index_path = os.path.join(docs_path, "index.html")
    try:
        with open(index_path, "r", encoding="utf-8") as f:
            index_content = f.read()
            
        # Create excerpt from actual story content, not the title
        if len(paragraphs) >= 2:
            # Use the second paragraph for the excerpt (first paragraph might be the title)
            excerpt = paragraphs[1][:100] + "..." if len(paragraphs[1]) > 100 else paragraphs[1]
        elif len(paragraphs) == 1:
            # If there's only one paragraph, use it but check it's not just the title
            if paragraphs[0].strip() != headline.strip():
                excerpt = paragraphs[0][:100] + "..." if len(paragraphs[0]) > 100 else paragraphs[0]
            else:
                excerpt = "Συνέχισε για να διαβάσεις την ιστορία..."  # "Continue to read the story" in Greek
        else:
            excerpt = "Συνέχισε για να διαβάσεις την ιστορία..."  # Default if no paragraphs
            
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
        else:
            # If no featured story section, add after featured-story section tag
            featured_section = r'<section class="featured-story">'
            if featured_section in index_content:
                index_content = re.sub(featured_section, f'{featured_section}\n{featured_story}', index_content)
        
        # Add new story to grid (at beginning) - BUT ONLY if it's not already in the index
        story_grid = r'<div class="story-grid">'
        if story_grid in index_content:
            # Check if this is a brand new story (not already in the index)
            if filename not in index_content:
                index_content = re.sub(story_grid, f'{story_grid}\n{story_card}', index_content)
            else:
                print(f"Story already exists in index, only updating featured section")
        
        # Write updated index.html
        with open(index_path, "w", encoding="utf-8") as f:
            f.write(index_content)
            
        print(f"Index.html updated successfully")
        
    except Exception as e:
        print(f"Error updating index.html: {e}")
        # If index doesn't exist, create a basic one
        # create_index_html(docs_path, filename, headline, attic_date, excerpt)
        # 
                       
async def main():
    # Verify API key at startup
    try:
        test_client = AsyncAnthropic(api_key=API_KEY)
    except Exception as e:
        print(f"Error: Invalid API key configuration: {e}")
        return

    print("\n🌟 ATTIC GREEK STORY GENERATOR 🌟")
    print("=" * 50)
    
    # Step 1: Writer creates story
    story, writer_tokens, metadata = await write_story()
    
    # Step 2: Editor corrects the story
    corrected_story, review_tokens = await review_story(story, metadata)
    
    # Step 3: Save the corrected story to the website
    if corrected_story:
        save_to_website(story, corrected_story, metadata)
        
        # Track input and output tokens separately
        total_tokens = writer_tokens + review_tokens
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
        print(f"3. Story published to website")
        print("=" * 50)

if __name__ == "__main__":
    asyncio.run(main())
