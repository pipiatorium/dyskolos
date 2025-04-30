import random
import os
import json
import datetime
import base64

THEMES = {
    "Μυθολογία": "mythology_words_encoded.txt",
    "Φιλοσοφία": "philosophy_words_encoded.txt",
    "Ἀθήναις": "Ἀθήναις_words_encoded.txt",
    "Θέατρον": "theatre_words_encoded.txt",
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
    "theme_label": "Θέμαe·",
    "letters_label": "Γράμματα",
    "word_was_label": "Ὁ λόγος ἦν:",
    "reveal_button_label": "Δεῖξον γράμμα (1 χρῆσις)",
    "play_again_button_label": "Παῖζε Πάλιν"
}

HTML_TEMPLATE = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Ἑλληνική Λέξις ({GREEK_UI['theme_label']} {{theme_name_placeholder}})</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap" rel="stylesheet">
    <style>
        body {{ font-family: 'Inter', sans-serif; touch-action: manipulation; }}
        .tile {{ width: 55px; height: 55px; border: 2px solid #d3d6da; display: flex; justify-content: center; align-items: center; font-size: 1.8rem; font-weight: bold; text-transform: uppercase; transition: transform 0.3s ease, background-color 0.5s ease, border-color 0.5s ease; box-sizing: border-box; }}
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
        @media (max-width: 640px) {{ .tile {{ width: 15vw; height: 15vw; max-width: 50px; max-height: 50px; font-size: 1.5rem; }} .key {{ height: 45px; min-width: 7vw; padding: 0 4px; font-size: 0.9rem; margin: 1px; }} .key.wide {{ min-width: 12vw; padding: 0 8px; }} #keyboard {{ padding: 5px 1px; }} .action-button {{ font-size: 0.9rem; padding: 6px 10px;}} }}
        @media (max-width: 380px) {{ .key {{ min-width: 9vw; padding: 0 2px; font-size: 0.8rem; }} .key.wide {{ min-width: 15vw; padding: 0 5px; }} }}
        @keyframes shake {{ 0%, 100% {{ transform: translateX(0); }} 10%, 30%, 50%, 70%, 90% {{ transform: translateX(-5px); }} 20%, 40%, 60%, 80% {{ transform: translateX(5px); }} }} .animate-shake {{ animation: shake 0.5s ease-in-out; }}
        @keyframes dance {{ 0%, 100% {{ transform: translateY(0); }} 50% {{ transform: translateY(-8px) scale(1.03); }} }} .animate-dance {{ animation: dance 0.5s ease-in-out; }}
        @keyframes reveal {{ 0% {{ transform: scale(1); background-color: #eee; }} 50% {{ transform: scale(1.1); background-color: #6aaa64; color: white; }} 100% {{ transform: scale(1); background-color: #6aaa64; }} }} .tile.revealed {{ animation: reveal 0.6s ease-out; background-color: #6aaa64; border-color: #6aaa64; color: white; }}
    </style>
</head>
<body class="bg-gray-100 flex flex-col items-center justify-between min-h-screen p-2 sm:p-4">

    <header class="text-center mb-4">
        <h1 class="text-3xl sm:text-4xl font-bold text-gray-800">Λεξιθήρα</h1>
        <p class="text-sm text-gray-600">{GREEK_UI['theme_label']} {{theme_name_placeholder}} - {{word_length}} {GREEK_UI['letters_label']}</p>
    </header>
    <div id="message-container" class="h-8 mb-2 text-center font-semibold text-red-600"><p id="message"></p></div>
    <div id="grid-container" class="grid grid-rows-6 gap-1 mb-4"></div>
    <div id="keyboard" class="mt-auto w-full max-w-xl p-1 bg-gray-200 rounded-md"></div>
    <div class="flex space-x-4 mt-4">
        <button id="reveal-letter" class="action-button px-4 py-2 bg-yellow-500 text-white font-semibold rounded-lg shadow-md hover:bg-yellow-600 focus:outline-none focus:ring-2 focus:ring-yellow-400 focus:ring-opacity-75 disabled:opacity-50 disabled:cursor-not-allowed">
            {GREEK_UI['reveal_button_label']}
        </button>
        <button id="play-again" class="action-button px-6 py-2 bg-blue-600 text-white font-semibold rounded-lg shadow-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-400 focus:ring-opacity-75 hidden">
            {GREEK_UI['play_again_button_label']}
        </button>
    </div>

    <script>
        const WORD_LENGTH = {{word_length}};
        const MAX_GUESSES = 6;
        const targetWord = {{target_word_placeholder}};
        const GREEK_WORDS = {{word_list_placeholder}};
        const themeName = "{{theme_name_placeholder}}";

        const MSG_NOT_ENOUGH_LETTERS = {GREEK_UI['not_enough_letters']};
        const MSG_NOT_IN_WORD_LIST = {GREEK_UI['not_in_word_list']};
        const MSG_EXCELLENT = {GREEK_UI['excellent']};
        const MSG_REVEAL_USED = {GREEK_UI['reveal_used']};
        const MSG_NO_MORE_REVEAL = {GREEK_UI['no_more_reveal']};
        const MSG_REVEALED = {GREEK_UI['revealed']};
        const MSG_CANNOT_REVEAL_FULL = {GREEK_UI['cannot_reveal_full']};
        const MSG_ERROR_INIT = {GREEK_UI['error_init']};
        const LABEL_WORD_WAS = "{GREEK_UI['word_was_label']}";

        const gridContainer = document.getElementById('grid-container');
        const keyboardContainer = document.getElementById('keyboard');
        const messageElement = document.getElementById('message');
        const playAgainButton = document.getElementById('play-again');
        const revealLetterButton = document.getElementById('reveal-letter');

        let currentRowIndex = 0; let currentColIndex = 0;
        let guesses = Array(MAX_GUESSES).fill(null).map(() => Array(WORD_LENGTH).fill(''));
        let isGameOver = false; let isProcessing = false;
        let keyStates = {{}}; let revealUsed = false;

        const keyboardLayout = [
            ['ε', 'ρ', 'τ', 'υ', 'θ', 'ι', 'ο', 'π'],
            ['α', 'σ', 'δ', 'φ', 'γ', 'η', 'ξ', 'κ', 'λ'],
            ['Enter', 'ζ', 'χ', 'ψ', 'ω', 'β', 'ν', 'μ', 'Backspace']
        ];

        function initializeGame() {{
            currentRowIndex = 0; currentColIndex = 0;
            guesses = Array(MAX_GUESSES).fill(null).map(() => Array(WORD_LENGTH).fill(''));
            isGameOver = false; isProcessing = false; keyStates = {{}}; revealUsed = false;
            messageElement.textContent = '';
            playAgainButton.classList.add('hidden');
            revealLetterButton.disabled = false;
            revealLetterButton.classList.remove('opacity-50', 'cursor-not-allowed');
            console.log(`Theme: ${{themeName}}, Length: ${{WORD_LENGTH}}, Target: ${{targetWord}}`);
            createGrid(); createKeyboard(); addEventListeners();
        }}

        function createGrid() {{
            gridContainer.innerHTML = ''; gridContainer.style.maxWidth = `${{WORD_LENGTH * 65}}px`;
            for (let r = 0; r < MAX_GUESSES; r++) {{
                const row = document.createElement('div'); row.classList.add('grid', `grid-cols-${{WORD_LENGTH}}`, 'gap-1'); row.dataset.row = r;
                for (let c = 0; c < WORD_LENGTH; c++) {{
                    const tile = document.createElement('div'); tile.classList.add('tile'); tile.dataset.row = r; tile.dataset.col = c; row.appendChild(tile);
                }} gridContainer.appendChild(row);
            }}
        }}

        function createKeyboard() {{
            keyboardContainer.innerHTML = '';
            keyboardLayout.forEach(rowKeys => {{
                const rowDiv = document.createElement('div'); rowDiv.classList.add('flex', 'justify-center', 'flex-wrap', 'mb-1');
                rowKeys.forEach(key => {{
                    const button = document.createElement('button'); button.classList.add('key');
                    if (key === 'Enter') {{ button.textContent = '✔'; }} else if (key === 'Backspace') {{ button.textContent = '⌫'; }} else {{ button.textContent = key; }}
                    button.dataset.key = key.toLowerCase();
                    if (key === 'Enter' || key === 'Backspace') {{ button.classList.add('wide'); }}
                    const state = keyStates[key.toLowerCase()]; if (state) {{ button.classList.add(state); }}
                    button.addEventListener('click', () => handleKeyPress(key.toLowerCase())); rowDiv.appendChild(button);
                }}); keyboardContainer.appendChild(rowDiv);
            }});
        }}

        function addEventListeners() {{
            document.removeEventListener('keydown', handlePhysicalKeyboard); document.addEventListener('keydown', handlePhysicalKeyboard);
            playAgainButton.removeEventListener('click', initializeGame); playAgainButton.addEventListener('click', initializeGame);
            revealLetterButton.removeEventListener('click', handleRevealLetter); revealLetterButton.addEventListener('click', handleRevealLetter);
        }}

        function handlePhysicalKeyboard(event) {{
                    if (isGameOver || isProcessing) {{ return; }}
                    const key = event.key.toLowerCase();

                    const virtualKeyElement = keyboardContainer.querySelector(`[data-key="${{key}}"]`);
                    if (virtualKeyElement && virtualKeyElement.disabled) {{
                        return;
                    }}

                    if (key === 'enter') {{
                        handleKeyPress('enter');
                    }} else if (key === 'backspace') {{
                        handleKeyPress('backspace');
                    }} else if (key.length === 1 && 'αβγδεζηθικλμνξοπρστυφχψω'.includes(key)) {{
                        handleKeyPress(key);
                    }}
                }}

        function handleKeyPress(key) {{
            if (isGameOver || isProcessing) return;
            if (key === 'enter') {{ submitGuess(); }} else if (key === 'backspace') {{ deleteLetter(); }} else if ('αβγδεζηθικλμνξοπρστυφχψω'.includes(key)) {{ addLetter(key); }}
        }}

        function handleRevealLetter() {{ // Doubled braces
            if (isGameOver || isProcessing || revealUsed) {{ // Doubled braces
                if (revealUsed) {{ showMessage(MSG_REVEAL_USED, 1500); }} // Doubled braces
                return;
            }} // Doubled braces

            // --- Simplified Selection Logic ---
            let possibleHints = [];
            const targetLetters = targetWord.split(''); // Target word (e.g., ['ε', 'π', 'ο', 'ς'])

            for (let i = 0; i < WORD_LENGTH; i++) {{ // Iterate through each position
                const targetLetter = targetLetters[i]; // Target letter for this position (e.g., 'ς' at index 3)
                const isEmptyInCurrentGuess = !guesses[currentRowIndex][i]; // Is this slot empty now?

                // Check if this position 'i' was already correctly guessed in a previous row
                let previouslyCorrect = false;
                for (let r = 0; r < currentRowIndex; r++) {{ // Doubled braces
                    const prevTile = getTileElement(r, i);
                    if (prevTile && prevTile.classList.contains('correct')) {{ // Doubled braces
                        // Normalize comparison in case previous row showed σ for target ς
                        if (normalizeSigma(prevTile.textContent.toLowerCase()) === normalizeSigma(targetLetter)) {{ // Doubled braces
                           previouslyCorrect = true;
                           break;
                        }} // Doubled braces
                    }} // Doubled braces
                }} // Doubled braces

                // If the slot is empty in the current guess AND wasn't correct previously at this position...
                if (isEmptyInCurrentGuess && !previouslyCorrect) {{ // Doubled braces
                    // ...then this is a potential hint. Store the letter and its correct index.
                    possibleHints.push({{ letter: targetLetter, index: i }});
                }} // Doubled braces
            }} // Doubled braces
            // --- End Simplified Selection Logic ---


            if (possibleHints.length === 0) {{ // Doubled braces
                // No suitable empty slots for letters that haven't been correctly placed yet.
                showMessage(MSG_NO_MORE_REVEAL, 1500); 
                return;
            }} // Doubled braces

            // Choose a random hint from the valid possibilities
            const {{ letter, index }} = possibleHints[Math.floor(Math.random() * possibleHints.length)];

            // --- Placement Logic (with else block fixed) ---
            const targetTile = getTileElement(currentRowIndex, index); 
            
            // Check if the target tile exists (it should) and is still empty 
            // (redundant check based on selection logic, but safe)
            if (targetTile && !guesses[currentRowIndex][index]) {{ // Doubled braces
                const letterToDisplay = letter.toUpperCase(); // Display revealed letter as uppercase
                guesses[currentRowIndex][index] = letter; // Store internal state as lowercase (might be 'ς')
                targetTile.textContent = letterToDisplay;
                targetTile.classList.add('filled', 'revealed'); // Mark as filled and add reveal animation class
                
                // Update keyboard state for the revealed letter (use normalized σ) to 'correct'
                updateKeyboard(normalizeSigma(letter), ['correct']); 

                revealUsed = true;
                revealLetterButton.disabled = true;
                revealLetterButton.classList.add('opacity-50', 'cursor-not-allowed');
                
                // Use JS concatenation for safety with Python f-strings
                showMessage(MSG_REVEALED + ' ' + letterToDisplay, 2000); 

                // Remove the visual animation class after it plays
                setTimeout(() => {{ // Doubled braces
                    const revealedTiles = gridContainer.querySelectorAll('.tile.revealed');
                    revealedTiles.forEach(t => t.classList.remove('revealed'));
                }}, 600); // Doubled braces
            }} else {{ // Doubled braces
                 // This block now runs if something unexpected happened 
                 // (e.g., the slot chosen was somehow filled between selection and placement).
                 // Avoid recursion. Just inform the user the hint failed this time.
                 showMessage(MSG_CANNOT_REVEAL_FULL, 1500); // Or a more specific error message
            }} // Doubled braces
            // --- End Placement Logic ---

        }} // Doubled braces

        function addLetter(letter) {{
            if (currentColIndex < WORD_LENGTH && !isGameOver && !isProcessing) {{
                guesses[currentRowIndex][currentColIndex] = letter; const tile = getTileElement(currentRowIndex, currentColIndex);
                if(tile) {{ tile.textContent = letter; tile.classList.add('filled'); }} currentColIndex++;
            }}
        }}
        function deleteLetter() {{
            if (currentColIndex > 0 && !isGameOver && !isProcessing) {{
                currentColIndex--; guesses[currentRowIndex][currentColIndex] = ''; const tile = getTileElement(currentRowIndex, currentColIndex);
                 if(tile) {{ tile.textContent = ''; tile.classList.remove('filled'); }}
            }}
        }}
       async function submitGuess() {{
            if (currentColIndex !== WORD_LENGTH) {{ showMessage(MSG_NOT_ENOUGH_LETTERS); shakeRow(currentRowIndex); return; }}
            const currentGuess = guesses[currentRowIndex].join('');
            isProcessing = true; revealLetterButton.disabled = true;
            const result = checkGuess(currentGuess, targetWord);
            await animateGuessResult(currentRowIndex, result); updateKeyboard(currentGuess, result);
            if (currentGuess === targetWord) {{
                showMessage(MSG_EXCELLENT); isGameOver = true; playAgainButton.classList.remove('hidden'); revealLetterButton.disabled = true; danceRow(currentRowIndex);
            }} else if (currentRowIndex === MAX_GUESSES - 1) {{
                showMessage(`${{LABEL_WORD_WAS}} ${{targetWord.toUpperCase()}}`); isGameOver = true; playAgainButton.classList.remove('hidden'); revealLetterButton.disabled = true;
            }} else {{
                currentRowIndex++; currentColIndex = 0; if (!revealUsed) {{ revealLetterButton.disabled = false; }}
            }}
            isProcessing = false; if (isGameOver || revealUsed) {{ revealLetterButton.disabled = true; revealLetterButton.classList.add('opacity-50', 'cursor-not-allowed'); }}
        }}
        function normalizeSigma(word) {{ // Doubled braces
        // Replace all final sigma (ς) with medial sigma (σ)
        return word.replace(/ς/g, 'σ'); 
        }} 
        
function checkGuess(guess, target) {{ // Doubled braces
        // Normalize both guess and target to use only medial sigma (σ)
        const normalizedGuess = normalizeSigma(guess);
        const normalizedTarget = normalizeSigma(target);

        const result = Array(WORD_LENGTH).fill('absent');
        // Perform comparisons using the normalized versions
        const targetLetters = normalizedTarget.split('');
        const guessLetters = normalizedGuess.split('');
        const letterCount = {{}}; // Doubled braces for JS object literal

        // Count letters in the normalized target
        targetLetters.forEach(letter => {{ // Doubled braces
            letterCount[letter] = (letterCount[letter] || 0) + 1;
        }}); // Doubled braces

        // First pass: Check for correct letters (Green) using normalized versions
        for (let i = 0; i < WORD_LENGTH; i++) {{ // Doubled braces
            // Comparison is now σ vs σ (if original was σ or ς)
            if (guessLetters[i] === targetLetters[i]) {{ // Doubled braces
                result[i] = 'correct';
                // Decrement count using the normalized letter
                if (letterCount[guessLetters[i]]) {{ // Doubled braces
                    letterCount[guessLetters[i]]--;
                }} // Doubled braces
            }} // Doubled braces
        }} // Doubled braces

        // Second pass: Check for present letters (Yellow) using normalized versions
        for (let i = 0; i < WORD_LENGTH; i++) {{ // Doubled braces
            if (result[i] !== 'correct') {{ // Doubled braces
                const currentLetter = guessLetters[i];
                // Check against remaining counts in letterCount (already reflects normalized target)
                if (targetLetters.includes(currentLetter) && letterCount[currentLetter] > 0) {{ // Doubled braces
                    result[i] = 'present';
                    letterCount[currentLetter]--; // Decrement count
                }} // Doubled braces
            }} // Doubled braces
        }} // Doubled braces
        return result;
        }} // Doubled braces

        function getTileElement(row, col) {{ return gridContainer.querySelector(`[data-row="${{row}}"][data-col="${{col}}"]`); }}
        function getRowElement(row) {{ return gridContainer.querySelector(`[data-row="${{row}}"]`); }}
        function showMessage(msg, duration = 2000) {{ messageElement.textContent = msg; if (duration > 0) {{ setTimeout(() => {{ if (messageElement.textContent === msg) {{ messageElement.textContent = ''; }} }}, duration); }} }}

        async function animateGuessResult(rowIndex, result) {{ // Doubled braces
                    // Using standard JS concatenation to avoid potential f-string/JS literal conflict
                    const rowTiles = gridContainer.querySelectorAll('[data-row="' + rowIndex + '"] .tile'); 
                    
                    if (!rowTiles) return;
                    for (let i = 0; i < WORD_LENGTH; i++) {{ // Doubled braces
                        const tile = rowTiles[i];
                        if (!tile) continue;
                        const state = result[i]; 

                        // Apply the flip animation ONLY if the state is 'absent'
                        if (state === 'absent') {{ // Doubled braces
                            tile.classList.add('flip');
                        }} // Doubled braces
                        
                        // Wait for the first half of the potential flip animation (or just a delay)
                        await new Promise(resolve => setTimeout(resolve, 150));
                        
                        // Apply the state class (correct, present, absent) to change color/style
                        tile.classList.add(state);
                        
                        // Wait for the second half of the flip ONLY if it was actually flipping (state was 'absent')
                        if (state === 'absent') {{ // Doubled braces
                            await new Promise(resolve => setTimeout(resolve, 150));
                        }} // Doubled braces
                    }} // Doubled braces
                }} // Doubled braces

        function updateKeyboard(guessOrLetter, resultOrState) {{ if (typeof guessOrLetter === 'string' && guessOrLetter.length === 1 && Array.isArray(resultOrState)) {{ const letter = guessOrLetter; const newState = resultOrState[0]; const currentKeyState = keyStates[letter]; let finalState = newState; if (currentKeyState === 'correct') {{ finalState = 'correct'; }} else if (currentKeyState === 'present' && newState === 'absent') {{ finalState = 'present'; }} keyStates[letter] = finalState; const keyElement = keyboardContainer.querySelector(`[data-key="${{letter}}"]`); if (keyElement) {{ keyElement.classList.remove('correct', 'present', 'absent'); keyElement.classList.add(finalState); }} }} else if (typeof guessOrLetter === 'string' && Array.isArray(resultOrState)) {{ const guessLetters = guessOrLetter.split(''); const result = resultOrState; for (let i = 0; i < WORD_LENGTH; i++) {{ const letter = guessLetters[i]; if (!letter) continue; const newState = result[i]; const currentKeyState = keyStates[letter]; let finalState = newState; if (currentKeyState === 'correct') {{ finalState = 'correct'; }} else if (currentKeyState === 'present' && newState === 'absent') {{ finalState = 'present'; }} keyStates[letter] = finalState; const keyElement = keyboardContainer.querySelector(`[data-key="${{letter}}"]`); if (keyElement) {{ keyElement.classList.remove('correct', 'present', 'absent'); keyElement.classList.add(finalState); }} }} }} }}
        // Slightly condensed updateKeyboard function (still multi-line for clarity)
 function updateKeyboard(guessOrLetter, resultOrState) {{
            const processLetter = (letter, newState) => {{
                const normalizedLetter = normalizeSigma(letter);
                const keyElement = keyboardContainer.querySelector(`[data-key="${{normalizedLetter}}"]`);
                if (!keyElement || keyElement.classList.contains('correct')) {{ return; }}

                const currentKeyState = keyStates[normalizedLetter];
                let finalState = newState;

                if (currentKeyState === 'correct') {{
                    finalState = 'correct';
                }} else if (currentKeyState === 'present' && newState === 'absent') {{
                    finalState = 'present';
                }}

                if (finalState === 'absent' && currentKeyState !== 'correct' && currentKeyState !== 'present') {{
                    keyElement.classList.add('disabled-key');
                    keyElement.disabled = true;
                }}

                if (finalState !== 'absent' || currentKeyState !== 'present') {{
                     keyElement.className = 'key' + (keyElement.classList.contains('wide') ? ' wide' : '') + ' ' + finalState + (keyElement.disabled ? ' disabled-key' : '');
                }}

                keyStates[normalizedLetter] = finalState;
            }};

            if (typeof guessOrLetter === 'string' && guessOrLetter.length === 1 && Array.isArray(resultOrState)) {{
                processLetter(guessOrLetter, resultOrState[0]);
            }} else if (typeof guessOrLetter === 'string' && Array.isArray(resultOrState)) {{
                const guessLetters = guessOrLetter.split('');
                const result = resultOrState;
                for (let i = 0; i < WORD_LENGTH; i++) {{
                    if (guessLetters[i]) {{ processLetter(guessLetters[i], result[i]); }}
                }}
            }}
        }}
        function shakeRow(rowIndex) {{ const rowElement = getRowElement(rowIndex); if (rowElement) {{ rowElement.classList.add('animate-shake'); setTimeout(() => {{ rowElement.classList.remove('animate-shake'); }}, 500); }} }}
        function danceRow(rowIndex) {{ const rowTiles = gridContainer.querySelectorAll(`[data-row="${{rowIndex}}"] .tile`); if (!rowTiles) return; rowTiles.forEach((tile, index) => {{ if (!tile) return; setTimeout(() => {{ tile.classList.add('animate-dance'); }}, index * 100); }}); }}

        if (typeof WORD_LENGTH === 'number' && typeof targetWord === 'string' && Array.isArray(GREEK_WORDS) && typeof themeName === 'string') {{ initializeGame(); }}
        else {{ console.error("Game constants not properly defined."); showMessage(MSG_ERROR_INIT, 0); }}
    </script>

</body>
</html>
"""

def load_words_from_file(filename):
    """Loads words from a file, assuming they are Base64 encoded."""
    words = []
    print(f"Loading and decoding 'encrypted' words from: {filename}") 
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            for line in f:
                encoded_word = line.strip() # Strips whitespace from the base64 line
                
                # Skip empty lines or comments
                if not encoded_word or encoded_word.startswith('#'): 
                    continue
                    
                try:
                    # Decode from Base64
                    decoded_bytes = base64.b64decode(encoded_word)
                    # Decode bytes to string using UTF-8
                    word = decoded_bytes.decode('utf-8').lower() 
                    
                    # ***** FIX: Strip whitespace AGAIN after decoding *****
                    word = word.strip() 
                    # *****************************************************

                    # Validation: Ensure it's alphabetic AND not empty after stripping
                    if word and word.isalpha(): 
                        words.append(word)
                    # Optional: Keep this warning for debugging if needed
                    # else:
                    #    print(f"Warning: Skipped invalid/non-alpha decoded word '{word}' from line '{encoded_word}' in {filename}")
                        
                except (base64.binascii.Error, UnicodeDecodeError) as decode_error:
                    print(f"Warning: Could not decode line '{encoded_word}' in {filename}. Error: {decode_error}")
                    
        if not words: 
            print(f"Warning: No valid words found/decoded in {filename}.")
        else:
            print(f"Successfully decoded {len(words)} words.") 
        return words
        
    except FileNotFoundError:
        print(f"Error: Word file '{filename}' not found.")
        return None
    except Exception as e:
        print(f"An error occurred while reading {filename}: {e}")
        return []
    
def filter_words_by_length(word_list, length):
    return [word for word in word_list if len(word) == length]

def choose_theme_and_length(themes_dict, possible_lengths):
    available_themes = list(themes_dict.keys())
    if not available_themes:
        print("Error: No themes defined.")
        return None, None, None, None

    try:
        sys_random = random.SystemRandom()
        chosen_theme_name = sys_random.choice(available_themes)
    except NotImplementedError:
        chosen_theme_name = random.choice(available_themes)

    word_file = themes_dict[chosen_theme_name]
    print(f"Selected theme: {chosen_theme_name} (using file: {word_file})")

    all_words = load_words_from_file(word_file)
    if all_words is None:
        print(f"Cannot proceed without words for theme '{chosen_theme_name}'.")
        return None, None, None, None

    valid_lengths = []
    words_by_length = {}
    for length in possible_lengths:
        filtered = filter_words_by_length(all_words, length)
        if filtered:
            valid_lengths.append(length)
            words_by_length[length] = filtered

    if not valid_lengths:
        print(f"Error: No words of lengths {possible_lengths} found in {word_file}.")
        return None, None, None, None

    try:
        chosen_length = sys_random.choice(valid_lengths)
    except NameError:
         chosen_length = random.choice(valid_lengths)

    print(f"Selected word length: {chosen_length}")
    filtered_word_list = words_by_length[chosen_length]
    return chosen_theme_name, chosen_length, filtered_word_list, word_file

def choose_target_word(word_list):
    if not word_list: return None
    try:
        sys_random = random.SystemRandom()
        return sys_random.choice(word_list)
    except NotImplementedError:
         return random.choice(word_list)


def generate_html_file(output_filename, theme_name, word_length, target_word, word_list):
    theme_name_for_js = theme_name
    word_length_js = str(word_length)
    target_word_js = json.dumps(target_word)
    word_list_js = json.dumps(word_list)

    html_content = HTML_TEMPLATE
    html_content = html_content.replace("{theme_name_placeholder}", theme_name_for_js)
    html_content = html_content.replace("{word_length}", word_length_js)
    html_content = html_content.replace("{target_word_placeholder}", target_word_js)
    html_content = html_content.replace("{word_list_placeholder}", word_list_js)

    placeholders_found = []
    if "{theme_name_placeholder}" in html_content: placeholders_found.append("{theme_name_placeholder}")
    if "{word_length}" in html_content: placeholders_found.append("{word_length}")
    if "{target_word_placeholder}" in html_content: placeholders_found.append("{target_word_placeholder}")
    if "{word_list_placeholder}" in html_content: placeholders_found.append("{word_list_placeholder}")
    if placeholders_found:
        print("\n--- WARNING: Placeholders NOT replaced ---")
        for p in placeholders_found: print(f"- {p}")
        print("Check the .replace() calls in generate_html_file.")
        print("------------------------------------------\n")

    try:
        with open(output_filename, 'w', encoding='utf-8') as f: f.write(html_content)
        print(f"Successfully generated game file: '{output_filename}'")
        print(f"Theme: {theme_name}, Length: {word_length}, Target Word: {target_word.upper()}")
        if not placeholders_found: print(f"Open '{output_filename}' in your web browser to play.")
    except IOError as e: print(f"Error writing file '{output_filename}': {e}")
    except Exception as e: print(f"Unexpected error writing file: {e}")

if __name__ == "__main__":
    print(f"--- Generating Attic Greek Wordle HTML Game ---")
    theme, length, words_for_length, source_file = choose_theme_and_length(THEMES, POSSIBLE_LENGTHS)

    if theme and length and words_for_length and source_file:
        print(f"Found {len(words_for_length)} words of length {length} in {source_file}.")
        target = choose_target_word(words_for_length)

        if target:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_theme_name_for_file = os.path.splitext(os.path.basename(source_file))[0]
            output_filename = f"greek_wordle_{safe_theme_name_for_file}_{length}_{timestamp}.html"
            print(f"Generating HTML file '{output_filename}'...")
            generate_html_file(output_filename, theme, length, target, words_for_length)
        else:
            print("Error: Could not choose target word.")
    else:
        print("Could not prepare game data. Halting.")

    print("------------------------------------------------------------------")
