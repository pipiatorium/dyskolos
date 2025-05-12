
# copyright 2025--DO NOT EDIT THE CODE IN THIS PAGE

import random
import os
import json
import datetime
import base64

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
def get_data_path(filename): return os.path.join(SCRIPT_DIR, filename)

THEMES = {
    "Μυθολογία": get_data_path("mythology_words_encoded.txt"),
    "Φιλοσοφία": get_data_path("philosophy_words_encoded.txt"),
    "Ἀθήναις": get_data_path("Ἀθήναις_words_encoded.txt"),
    "Θέατρον": get_data_path("theatre_words_encoded.txt"),
}
POSSIBLE_LENGTHS = [4, 4, 4, 4, 4, 4, 4, 4, 4, 5, 5, 6]

GREEK_UI = {
    "not_enough_letters": json.dumps("Λείπει γράμματα!"),
    "not_in_word_list": json.dumps("Οὐκ ἔστιν ἐν λόγοις!"),
    "excellent": json.dumps("Ἄριστα!"),
    "reveal_used": json.dumps("Ἤδη ἐχρήσω!"),
    "no_more_reveal": json.dumps("Οὐκ ἔστι γράμματα δεῖξαι!"),
    "revealed": json.dumps("Ἐδείχθη:"),
    "cannot_reveal_full": json.dumps("Οὐ δύναμαι δεῖξαι - πλῆρες;"),
    "error_init": json.dumps("Σφάλμα ἐν ἀρχῇ."),
    "theme_label": "Θέμα·",
    "letters_label": "Γράμματα",
    "word_was_label": "Ὁ λόγος ἦν:",
    "word_explanation_label": json.dumps("Λόγος σημαίνει:"),  # New: Word explanation label
    "reveal_button_label": "Δεῖξον γράμμα (1 χρῆσις)",
    "play_again_button_label": "Παῖζε Πάλιν"
}

# Enhanced HTML template with debugging capability
# Simplified HTML template with reliable debugging
HTML_TEMPLATE = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Ἑλληνική Λέξις ({GREEK_UI['theme_label']} {{theme_name_placeholder}})</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="data:image/svg+xml,&lt;svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'&gt;&lt;text x='50' y='50' font-size='90' fill='red' dominant-baseline='middle' text-anchor='middle'&gt;Δ&lt;/text&gt;&lt;/svg&gt;" rel="icon"/>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">
 
<style>
    body {{ font-family: 'Inter', sans-serif; touch-action: manipulation; }}
    .tile {{ width: 55px; height: 55px; border: 2px solid #d3d6da; display: flex; justify-content: center; align-items: center; font-size: 3rem; font-weight: bold; text-transform: uppercase; transition: transform 0.3s ease, background-color 0.5s ease, border-color 0.5s ease; box-sizing: border-box; }}
    .tile.filled {{ border-color: #878a8c; }}
    .tile.flip {{ transform: rotateX(180deg); }}
    .correct {{ background-color: #6aaa64; border-color: #6aaa64; color: white; }}
    .present {{ background-color: #c9b458; border-color: #c9b458; color: white; }}
    .absent {{ background-color: #787c7e; border-color: #787c7e; color: white; }}
    .key {{ height: 50px; min-width: 35px; padding: 0 8px; margin: 2px; border-radius: 4px; display: flex; justify-content: center; align-items: center; font-size: 1rem; font-weight: bold; background-color: #d3d6da; cursor: pointer; text-transform: uppercase; transition: background-color 0.2s ease; box-sizing: border-box; }}
    .key:hover {{ background-color: #b0b3b8; }}
    .key.wide {{/* ... */ }}
    .key[data-key="enter"] {{ font-size: 1.5rem; color: #10B981; font-weight: bold; }}
    .key.disabled-key {{
        opacity: 0.6; /* Dim the key */
        cursor: not-allowed; /* Show disabled cursor */
        pointer-events: none; /* Optional: Prevent click events directly via CSS */
    }}
    .key.disabled-key:hover {{
        background-color: #787c7e; /* Keep hover same as absent color */
    }}
        button:disabled {{ /* ... */ }}       
        button:disabled {{ background-color: #cccccc; color: #666666; cursor: not-allowed; opacity: 0.7; }}
        @media (max-width: 640px) {{ .tile {{ width: 15vw; height: 15vw; max-width: 50px; max-height: 50px; font-size: 1.8rem; }} .key {{ height: 45px; min-width: 7vw; padding: 0 4px; font-size: 1.6rem; margin: 1px; }} .key.wide {{ min-width: 12vw; padding: 0 8px; }} #keyboard {{ padding: 5px 1px; }} .action-button {{ font-size: 0.9rem; padding: 6px 10px;}} }}
        @media (max-width: 380px) {{ .key {{ min-width: 9vw; padding: 0 2px; font-size: 0.8rem; }} .key.wide {{ min-width: 15vw; padding: 0 5px; }} }}
        @keyframes shake {{ 0%, 100% {{ transform: translateX(0); }} 10%, 30%, 50%, 70%, 90% {{ transform: translateX(-5px); }} 20%, 40%, 60%, 80% {{ transform: translateX(5px); }} }} .animate-shake {{ animation: shake 0.5s ease-in-out; }}
        @keyframes dance {{ 0%, 100% {{ transform: translateY(0); }} 50% {{ transform: translateY(-8px) scale(1.03); }} }} .animate-dance {{ animation: dance 0.5s ease-in-out; }}
        @keyframes reveal {{ 0% {{ transform: scale(1); background-color: #eee; }} 50% {{ transform: scale(1.1); background-color: #6aaa64; color: white; }} 100% {{ transform: scale(1); background-color: #6aaa64; }} }} .tile.revealed {{ animation: reveal 0.6s ease-out; background-color: #6aaa64; border-color: #6aaa64; color: white; }}
    .tile.correct, .key.correct {{ 
    background-color: #6aaa64 !important; 
    border-color: #6aaa64 !important; 
    color: white !important; 
}}

.tile.present, .key.present {{ 
    background-color: #c9b458 !important; 
    border-color: #c9b458 !important; 
    color: white !important; 
}}

.tile.absent, .key.absent {{ 
    background-color: #787c7e !important; 
    border-color: #787c7e !important; 
    color: white !important; 
}}

/* New styles for explanation container */
.fade-out {{ opacity: 0; transition: opacity 0.5s ease-out; }}
.fade-in {{ opacity: 1; transition: opacity 0.5s ease-in; }}
#explanation {{ 
    max-width: 600px; 
    margin: 0 auto; 
    padding: 20px; 
    background-color: #f8f9fa; 
    border-radius: 8px; 
    box-shadow: 0 2px 10px rgba(0,0,0,0.1); 
}}
.explanation-header {{ 
    font-size: 1.2rem; 
    font-weight: bold; 
    margin-bottom: 10px; 
    color: #333; 
}}
.explanation-content {{ 
    font-size: 1rem; 
    line-height: 1.5; 
    color: #555; 
}}

</style>
</head>
<body class="bg-gray-100 flex flex-col items-center justify-start min-h-screen p-2 sm:p-4">

    <header class="text-center mb-4">
        <h1 class="text-3xl sm:text-4xl font-bold text-gray-800">Λεξιτήρα</h1>
        <p class="text-sm text-gray-600">{GREEK_UI['theme_label']} {{theme_name_placeholder}}</p>
    </header>
    <div id="message-container" class="h-4 mb-2 text-center font-semibold text-red-600"><p id="message"></p></div>
    <div id="grid-container" class="grid grid-rows-6 gap-1 mb-4"></div>
    <!-- New explanation container, hidden by default -->
    <div id="explanation" class="mb-4 hidden"></div>
    <div id="keyboard" class="w-full max-w-xl p-1 bg-gray-200 rounded-md"></div>
    
    <div class="flex space-x-4 mt-4 items-center">
        <button id="reveal-letter" class="action-button px-2 py-1 bg-yellow-500 text-white font-normal rounded-lg shadow-md hover:bg-yellow-600 focus:outline-none focus:ring-2 focus:ring-yellow-400 focus:ring-opacity-75 disabled:opacity-50 disabled:cursor-not-allowed text-sm">
            {GREEK_UI['reveal_button_label']}
        </button>
        <button id="play-again" class="action-button px-2 py-1 bg-blue-600 text-white font-normal rounded-lg shadow-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-400 focus:ring-opacity-75 hidden text-sm">
            {GREEK_UI['play_again_button_label']}
        </button>
        <a href="https://forms.gle/H991LsbtHGPKSP9M6"
        target="_blank"
        class="action-button px-2 py-1 bg-green-500 text-white font-normal rounded-lg shadow-sm hover:bg-green-600 focus:outline-none focus:ring-2 focus:ring-green-300 focus:ring-opacity-75 text-sm">
            Subscribe
        </a>
        <div class="social-icons-row">
            <a href="https://www.paypal.com/donate/?hosted_button_id=FLR49G2DRY2SL" target="_blank" aria-label="Donate">
                <i class="fas fa-hand-holding-usd" style="font-size: 36px;"></i>
            </a>
        </div>
    </div>

    <!-- Pass UI constants to the JS file -->
    <script>
        // Define game config in a way that's easy to debug
        const gameConfig = {{
            WORD_LENGTH: parseInt("{{word_length}}"),
            MAX_GUESSES: 6,
            targetWord: {{target_word_placeholder}},
            targetExplanation: {{target_explanation_placeholder}},
            GREEK_WORDS: {{word_list_placeholder}},
            themeName: "{{theme_name_placeholder}}",
            // Pass all UI message constants
            MSG_NOT_ENOUGH_LETTERS: {GREEK_UI['not_enough_letters']},
            MSG_NOT_IN_WORD_LIST: {GREEK_UI['not_in_word_list']},
            MSG_EXCELLENT: {GREEK_UI['excellent']},
            MSG_REVEAL_USED: {GREEK_UI['reveal_used']},
            MSG_NO_MORE_REVEAL: {GREEK_UI['no_more_reveal']},
            MSG_REVEALED: {GREEK_UI['revealed']},
            MSG_CANNOT_REVEAL_FULL: {GREEK_UI['cannot_reveal_full']},
            MSG_ERROR_INIT: {GREEK_UI['error_init']},
            LABEL_WORD_WAS: "{GREEK_UI['word_was_label']}",
            
            LABEL_WORD_EXPLANATION: {GREEK_UI['word_explanation_label']}
        }};

    </script>
    
    <!-- Reference the external JavaScript file -->
    <script src="wordle_game.js"></script>
</body>
</html>
"""

def load_words_from_file(filename):
    """Loads words from a file, assuming they are Base64 encoded with optional descriptions."""
    words = []
    descriptions = {}  # New dictionary to store word -> description mappings
    print(f"Loading and decoding 'encrypted' words from: {filename}") 
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                
                # Skip empty lines or comments
                if not line or line.startswith('#'): 
                    continue
                
                # Split the line at comma to separate word and description
                parts = line.split(',', 1)
                encoded_word = parts[0].strip()
                description = parts[1].strip() if len(parts) > 1 else ""
                    
                try:
                    # Decode from Base64
                    decoded_bytes = base64.b64decode(encoded_word)
                    # Decode bytes to string using UTF-8
                    word = decoded_bytes.decode('utf-8').lower() 
                    
                    # Strip whitespace after decoding
                    word = word.strip() 

                    # Validation: Ensure it's alphabetic AND not empty after stripping
                    if word and word.isalpha(): 
                        words.append(word)
                        if description:  # Store the description if it exists
                            descriptions[word] = description
                except (base64.binascii.Error, UnicodeDecodeError) as decode_error:
                    print(f"Warning: Could not decode line '{encoded_word}' in {filename}. Error: {decode_error}")
                    
        if not words: 
            print(f"Warning: No valid words found/decoded in {filename}.")
        else:
            print(f"Successfully decoded {len(words)} words with {len(descriptions)} descriptions.") 
        return words, descriptions
        
    except FileNotFoundError:
        print(f"Error: Word file '{filename}' not found.")
        return None, None
    except Exception as e:
        print(f"An error occurred while reading {filename}: {e}")
        return [], {}
       
def filter_words_by_length(word_list, length):
    """Filter words to only include those of the specified length."""
    return [word for word in word_list if len(word) == length]

def choose_theme_and_length(themes_dict, possible_lengths):
    available_themes = list(themes_dict.keys())
    if not available_themes:
        print("Error: No themes defined.")
        return None, None, None, None, None

    try:
        sys_random = random.SystemRandom()
        chosen_theme_name = sys_random.choice(available_themes)
    except NotImplementedError:
        chosen_theme_name = random.choice(available_themes)

    word_file = themes_dict[chosen_theme_name]
    print(f"Selected theme: {chosen_theme_name} (using file: {word_file})")

    # Updated to handle descriptions as well
    result = load_words_from_file(word_file)
    if result is None or result[0] is None:
        print(f"Cannot proceed without words for theme '{chosen_theme_name}'.")
        return None, None, None, None, None
    
    all_words, all_descriptions = result

    valid_lengths = []
    words_by_length = {}
    descriptions_by_length = {}
    
    for length in possible_lengths:
        filtered = filter_words_by_length(all_words, length)
        if filtered:
            valid_lengths.append(length)
            words_by_length[length] = filtered
            
            # Filter descriptions to match the filtered words
            filtered_descriptions = {word: all_descriptions.get(word, "") 
                                    for word in filtered if word in all_descriptions}
            descriptions_by_length[length] = filtered_descriptions

    if not valid_lengths:
        print(f"Error: No words of lengths {possible_lengths} found in {word_file}.")
        return None, None, None, None, None

    try:
        chosen_length = sys_random.choice(valid_lengths)
    except NameError:
         chosen_length = random.choice(valid_lengths)

    print(f"Selected word length: {chosen_length}")
    filtered_word_list = words_by_length[chosen_length]
    filtered_descriptions = descriptions_by_length[chosen_length]
    
    return chosen_theme_name, chosen_length, filtered_word_list, word_file, filtered_descriptions
def choose_target_word(word_list, descriptions=None):
    if not word_list: 
        return None, None
    
    try:
        sys_random = random.SystemRandom()
        chosen_word = sys_random.choice(word_list)
    except NotImplementedError:
        chosen_word = random.choice(word_list)
    
    # Get the description for the chosen word, if available
    description = ""
    if descriptions and chosen_word in descriptions:
        description = descriptions[chosen_word]
    
    return chosen_word, description


def generate_html_file(output_filepath, theme_name, word_length, target_word, word_list, target_description=""):
    # 1. Prepare JavaScript variables (theme_name_for_js, etc.)
    #    - This logic is UNCHANGED by the filename/path modifications.
    theme_name_for_js = theme_name
    word_length_js = str(word_length)
    target_word_js = json.dumps(target_word)
    word_list_js = json.dumps(word_list)

    # 2. Get the HTML template content
    html_content = HTML_TEMPLATE # Assumes HTML_TEMPLATE is defined elsewhere

    # 3. Replace placeholders in the HTML template
    html_content = html_content.replace("{target_explanation_placeholder}", json.dumps(target_description))
    html_content = html_content.replace("{theme_name_placeholder}", theme_name_for_js)
    html_content = html_content.replace("{word_length}", word_length_js)
    html_content = html_content.replace("{target_word_placeholder}", target_word_js)
    html_content = html_content.replace("{word_list_placeholder}", word_list_js)


    placeholders_found = []
    # ...(placeholder checks)...
    try:
        # Use the full filepath passed into the function
        with open(output_filepath, 'w', encoding='utf-8') as f: # <-- Uses the full path
            f.write(html_content)
        # Print messages using the full filepath
        print(f"Successfully generated game file: '{output_filepath}'")
        print(f"Theme: {theme_name}, Length: {word_length}, Target Word: {target_word.upper()}")
        if not placeholders_found: print(f"Open '{output_filepath}' in your web browser to play.")
    except IOError as e: print(f"Error writing file '{output_filepath}': {e}")
    except Exception as e: print(f"Unexpected error writing file: {e}")
    
if __name__ == "__main__":
    print(f"--- Generating Attic Greek Wordle HTML Game ---")
    print(f"Script location: {SCRIPT_DIR}")

    theme, length, words_for_length, source_file, descriptions = choose_theme_and_length(THEMES, POSSIBLE_LENGTHS)

    if theme and length and words_for_length and source_file:
        print(f"Found {len(words_for_length)} words of length {length} in {source_file}.")
        if descriptions: # Check if descriptions dictionary exists
             print(f"Words with descriptions: {len(descriptions)}")

        # choose_target_word returns a tuple: (word, description)
        word_tuple = choose_target_word(words_for_length, descriptions) 

        if word_tuple and word_tuple[0]: # Check if a word was actually chosen
            actual_target_word = word_tuple[0]
            actual_target_description = word_tuple[1]

            output_filename_base = "λεξιτήρα.html"
            parent_dir = os.path.dirname(SCRIPT_DIR)
            repo_root_dir = os.path.dirname(parent_dir)
            target_subdir = 'docs'
            output_dir_absolute = os.path.join(repo_root_dir, target_subdir)
            os.makedirs(output_dir_absolute, exist_ok=True)
            output_filepath = os.path.join(output_dir_absolute, output_filename_base)

            print(f"Generating HTML file '{output_filepath}'...")
            generate_html_file(
                output_filepath, 
                theme, 
                length, 
                actual_target_word,       # Pass the string here
                words_for_length, 
                actual_target_description # Pass the description string here
            )
        else:
            print("Error: Could not choose target word.")
    else:
        print("Could not prepare game data. Halting.")
    print("------------------------------------------------------------------")
