// copyright 2025--DO NOT EDIT THE CODE IN THIS PAGE

const WORD_LENGTH = gameConfig.WORD_LENGTH;
const MAX_GUESSES = gameConfig.MAX_GUESSES;
const targetWord = gameConfig.targetWord;
const targetExplanation = gameConfig.targetExplanation; // New: Store the explanation
const GREEK_WORDS = gameConfig.GREEK_WORDS;
const themeName = gameConfig.themeName;

// UI message constants from Python
const MSG_NOT_ENOUGH_LETTERS = gameConfig.MSG_NOT_ENOUGH_LETTERS;
const MSG_NOT_IN_WORD_LIST = gameConfig.MSG_NOT_IN_WORD_LIST;
const MSG_EXCELLENT = gameConfig.MSG_EXCELLENT;
const MSG_REVEAL_USED = gameConfig.MSG_REVEAL_USED;
const MSG_NO_MORE_REVEAL = gameConfig.MSG_NO_MORE_REVEAL;
const MSG_REVEALED = gameConfig.MSG_REVEALED;
const MSG_CANNOT_REVEAL_FULL = gameConfig.MSG_CANNOT_REVEAL_FULL;
const MSG_ERROR_INIT = gameConfig.MSG_ERROR_INIT;
const LABEL_WORD_WAS = gameConfig.LABEL_WORD_WAS;
const LABEL_WORD_EXPLANATION = gameConfig.LABEL_WORD_EXPLANATION || "Επεξήγηση:"; // New: Label for explanation

// DOM Elements
const gridContainer = document.getElementById('grid-container');
const keyboardContainer = document.getElementById('keyboard');
const messageElement = document.getElementById('message');
const playAgainButton = document.getElementById('play-again');
const revealLetterButton = document.getElementById('reveal-letter');
const explanationElement = document.getElementById('explanation'); // New: Element for explanation

// Game state variables - Define these BEFORE any function definitions
let currentRowIndex = 0;
let currentColIndex = 0;
let guesses = Array(MAX_GUESSES).fill(null).map(() => Array(WORD_LENGTH).fill(''));
let isGameOver = false;
let isProcessing = false;
let keyStates = {};
let revealUsed = false;

// Keyboard layout for Greek
const keyboardLayout = [
    ['ε', 'ρ', 'τ', 'υ', 'θ', 'ι', 'ο', 'π'],
    ['α', 'σ', 'δ', 'φ', 'γ', 'η', 'ξ', 'κ', 'λ'],
    ['Enter', 'ζ', 'χ', 'ψ', 'ω', 'β', 'ν', 'μ', 'Backspace']
];

// Add event listeners
function addEventListeners() {
    document.removeEventListener('keydown', handlePhysicalKeyboard);
    document.addEventListener('keydown', handlePhysicalKeyboard);
    playAgainButton.removeEventListener('click', initializeGame);
    playAgainButton.addEventListener('click', initializeGame);
    revealLetterButton.removeEventListener('click', handleRevealLetter);
    revealLetterButton.addEventListener('click', handleRevealLetter);
}

// Handle physical keyboard input
function handlePhysicalKeyboard(event) {
    if (isGameOver || isProcessing) { return; }
    const key = event.key.toLowerCase();

    const virtualKeyElement = keyboardContainer.querySelector(`[data-key="${key}"]`);
    if (virtualKeyElement && virtualKeyElement.disabled) {
        return;
    }

    if (key === 'enter') {
        handleKeyPress('enter');
    } else if (key === 'backspace') {
        handleKeyPress('backspace');
    } else if (key.length === 1 && 'αβγδεζηθικλμνξοπρστυφχψω'.includes(key)) {
        handleKeyPress(key);
    }
}

// Handle key press
function handleKeyPress(key) {
    if (isGameOver || isProcessing) return;
    if (key === 'enter') { submitGuess(); }
    else if (key === 'backspace') { deleteLetter(); }
    else if ('αβγδεζηθικλμνξοπρστυφχψω'.includes(key)) { addLetter(key); }
}

// Handle reveal letter functionality
function handleRevealLetter() {
    if (isGameOver || isProcessing || revealUsed) {
        if (revealUsed) { showMessage(MSG_REVEAL_USED, 1500); }
        return;
    }

    // --- Simplified Selection Logic ---
    let possibleHints = [];
    const targetLetters = targetWord.split(''); // Target word (e.g., ['ε', 'π', 'ο', 'ς'])

    for (let i = 0; i < WORD_LENGTH; i++) { // Iterate through each position
        const targetLetter = targetLetters[i]; // Target letter for this position (e.g., 'ς' at index 3)
        const isEmptyInCurrentGuess = !guesses[currentRowIndex][i]; // Is this slot empty now?

        // Check if this position 'i' was already correctly guessed in a previous row
        let previouslyCorrect = false;
        for (let r = 0; r < currentRowIndex; r++) {
            const prevTile = getTileElement(r, i);
            if (prevTile && prevTile.classList.contains('correct')) {
                // Normalize comparison in case previous row showed σ for target ς
                if (normalizeSigma(prevTile.textContent.toLowerCase()) === normalizeSigma(targetLetter)) {
                    previouslyCorrect = true;
                    break;
                }
            }
        }

        // If the slot is empty in the current guess AND wasn't correct previously at this position...
        if (isEmptyInCurrentGuess && !previouslyCorrect) {
            // ...then this is a potential hint. Store the letter and its correct index.
            possibleHints.push({ letter: targetLetter, index: i });
        }
    }
    // --- End Simplified Selection Logic ---

    if (possibleHints.length === 0) {
        // No suitable empty slots for letters that haven't been correctly placed yet.
        showMessage(MSG_NO_MORE_REVEAL, 1500); 
        return;
    }

    // Choose a random hint from the valid possibilities
    const { letter, index } = possibleHints[Math.floor(Math.random() * possibleHints.length)];

    // --- Placement Logic (with else block fixed) ---
    const targetTile = getTileElement(currentRowIndex, index); 
    
    // Check if the target tile exists (it should) and is still empty 
    // (redundant check based on selection logic, but safe)
    if (targetTile && !guesses[currentRowIndex][index]) {
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
        setTimeout(() => {
            const revealedTiles = gridContainer.querySelectorAll('.tile.revealed');
            revealedTiles.forEach(t => t.classList.remove('revealed'));
        }, 600);
    } else {
        // This block now runs if something unexpected happened 
        // (e.g., the slot chosen was somehow filled between selection and placement).
        // Avoid recursion. Just inform the user the hint failed this time.
        showMessage(MSG_CANNOT_REVEAL_FULL, 1500); // Or a more specific error message
    }
    // --- End Placement Logic ---
}

// Add a letter to the current tile
function addLetter(letter) {
    if (currentColIndex < WORD_LENGTH && !isGameOver && !isProcessing) {
        guesses[currentRowIndex][currentColIndex] = letter;
        const tile = getTileElement(currentRowIndex, currentColIndex);
        if(tile) {
            tile.textContent = letter;
            tile.classList.add('filled');
        }
        currentColIndex++;
    }
}

// Delete the last letter
function deleteLetter() {
    if (currentColIndex > 0 && !isGameOver && !isProcessing) {
        currentColIndex--;
        guesses[currentRowIndex][currentColIndex] = '';
        const tile = getTileElement(currentRowIndex, currentColIndex);
        if(tile) {
            tile.textContent = '';
            tile.classList.remove('filled');
        }
    }
}

// Submit the current guess
async function submitGuess() {
    // Check if all tiles are filled (either by user input or by hint)
    const allTilesFilled = guesses[currentRowIndex].every(letter => letter !== '');
    
    if (!allTilesFilled) {
        showMessage(MSG_NOT_ENOUGH_LETTERS);
        shakeRow(currentRowIndex);
        return;
    }
    
    const currentGuess = guesses[currentRowIndex].join('');
    isProcessing = true;
    revealLetterButton.disabled = true;
    
    const result = checkGuess(currentGuess, targetWord);
    await animateGuessResult(currentRowIndex, result);
    updateKeyboard(currentGuess, result);
    forceKeyboardColors();
    
    // More lenient equality check for the win condition
    // Normalize both words to lowercase with no accents
    // In submitGuess()
    const normalizedGuess = normalizeSigma(currentGuess).normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLowerCase();
    const normalizedTarget = normalizeSigma(targetWord).normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLowerCase();

    const isCorrect = normalizedGuess === normalizedTarget;
    
    if (isCorrect) {
        showMessage(MSG_EXCELLENT);
        isGameOver = true;
        playAgainButton.classList.remove('hidden');
        revealLetterButton.disabled = true;
        danceRow(currentRowIndex);
        
        // New: Show explanation after a win
        setTimeout(() => {
            revealExplanation();
        }, 1500);
    } else if (currentRowIndex === MAX_GUESSES - 1) {
        // showMessage(`${LABEL_WORD_WAS} ${targetWord.toUpperCase()}`);
        isGameOver = true;
        playAgainButton.classList.remove('hidden');
        revealLetterButton.disabled = true;
        
        // New: Show explanation after losing
        setTimeout(() => {
            revealExplanation();
        }, 1500);
    } else {
        currentRowIndex++;
        currentColIndex = 0;
        if (!revealUsed) {
            revealLetterButton.disabled = false;
        }
    }
    
    isProcessing = false;
    if (isGameOver || revealUsed) {
        revealLetterButton.disabled = true;
        revealLetterButton.classList.add('opacity-50', 'cursor-not-allowed');
    }
}

// New function: Reveal the explanation for the word
function revealExplanation() {
    // Ensure gridContainer and targetExplanation are available
    if (!gridContainer || (typeof targetExplanation === 'undefined' && !targetWord)) { // Allow if targetWord exists (for win message)
         // If no explanation and no word (for win message), nothing to show.
        if(!targetExplanation && !targetWord) return;
    }


    const allTiles = gridContainer.querySelectorAll('.tile');
    allTiles.forEach(tile => {
        tile.classList.add('fade-out'); // Assumes .fade-out makes opacity 0
        // Optionally ensure tiles are not interactive during/after fade
        // tile.style.pointerEvents = 'none'; // If fade-out class doesn't handle this
    });

    // Wait for tiles to fade out (adjust duration to match your CSS animation)
    setTimeout(() => {
        // Store current height before clearing, to maintain the space
        const gridHeight = gridContainer.offsetHeight;
        gridContainer.style.minHeight = `${gridHeight}px`; // Maintain height

        // Clear the grid content (tiles)
        gridContainer.innerHTML = ''; 

        // Change gridContainer display style to center the new explanation content
        gridContainer.style.display = 'flex';
        gridContainer.style.alignItems = 'center';
        gridContainer.style.justifyContent = 'center';
        gridContainer.style.padding = '10px'; // Add some padding for the new content

        // Prepare the explanation content HTML
        // This uses the simplified version where the word isn't explicitly revealed in the explanation
        // LABEL_WORD_EXPLANATION itself is "Λόγος σημαίνει:"
        let explanationContentHTML = '';
        if (targetExplanation) {
            explanationContentHTML = `
                <div class="explanation-popup-content" style="background: #f8f9fa; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); text-align: left; max-width: 95%; opacity: 0;">
                    ${LABEL_WORD_EXPLANATION} ${targetExplanation}
                </div>
            `;
        } else {
             // Fallback if there's no explanation text, perhaps for a win without explanation
             // Or you might have different logic here based on the isWin flag if you reintroduce it
             explanationContentHTML = `<div class="explanation-popup-content" style="opacity: 0;">No explanation available.</div>`
        }

        gridContainer.innerHTML = explanationContentHTML;

        // Fade in the new explanation content
        const popupContent = gridContainer.querySelector('.explanation-popup-content');
        if (popupContent) {
            // Force reflow to ensure transition is applied
            void popupContent.offsetWidth; 
            popupContent.style.transition = 'opacity 0.5s ease-in';
            popupContent.style.opacity = '1';
        }

        // If you were using a separate #explanation element, ensure it's hidden
        if (explanationElement) {
            explanationElement.classList.add('hidden');
        }

    }, 500); // This duration should match your .fade-out animation time
}

// Check the guess against the target word
function checkGuess(guess, target) {
    // Normalize both guess and target to use only medial sigma (σ)
    const normalizedGuess = normalizeSigma(guess);
    const normalizedTarget = normalizeSigma(target);

    const result = Array(WORD_LENGTH).fill('absent');
    // Perform comparisons using the normalized versions
    const targetLetters = normalizedTarget.split('');
    const guessLetters = normalizedGuess.split('');
    const letterCount = {};

    // Count letters in the normalized target
    targetLetters.forEach(letter => {
        letterCount[letter] = (letterCount[letter] || 0) + 1;
    });

    // First pass: Check for correct letters (Green) using normalized versions
    for (let i = 0; i < WORD_LENGTH; i++) {
        // Comparison is now σ vs σ (if original was σ or ς)
        if (guessLetters[i] === targetLetters[i]) {
            result[i] = 'correct';
            // Decrement count using the normalized letter
            if (letterCount[guessLetters[i]]) {
                letterCount[guessLetters[i]]--;
            }
        }
    }

    // Second pass: Check for present letters (Yellow) using normalized versions
    for (let i = 0; i < WORD_LENGTH; i++) {
        if (result[i] !== 'correct') {
            const currentLetter = guessLetters[i];
            // Check against remaining counts in letterCount (already reflects normalized target)
            if (targetLetters.includes(currentLetter) && letterCount[currentLetter] > 0) {
                result[i] = 'present';
                letterCount[currentLetter]--; // Decrement count
            }
        }
    }
    return result;
}

// Helper function to get a tile element
function getTileElement(row, col) {
    return gridContainer.querySelector(`[data-row="${row}"][data-col="${col}"]`);
}

// Helper function to get a row element
function getRowElement(row) {
    return gridContainer.querySelector(`[data-row="${row}"]`);
}

// Show a message to the user
function showMessage(msg, duration = 2000) {
    messageElement.textContent = msg;
    if (duration > 0) {
        setTimeout(() => {
            if (messageElement.textContent === msg) {
                messageElement.textContent = '';
            }
        }, duration);
    }
}

// Animate the guess result
async function animateGuessResult(rowIndex, result) { 
    // Using standard JS concatenation to avoid potential f-string/JS literal conflict
    const rowTiles = gridContainer.querySelectorAll('[data-row="' + rowIndex + '"] .tile'); 
    
    if (!rowTiles) return;
    for (let i = 0; i < WORD_LENGTH; i++) { 
        const tile = rowTiles[i];
        if (!tile) continue;
        const state = result[i]; 

        // Apply the flip animation ONLY if the state is 'absent'
        if (state === 'absent') { 
            tile.classList.add('flip');
        } 
        
        // Wait for the first half of the potential flip animation (or just a delay)
        await new Promise(resolve => setTimeout(resolve, 150));
        
        // Apply the state class (correct, present, absent) to change color/style
        tile.classList.add(state);
        
        // Wait for the second half of the flip ONLY if it was actually flipping (state was 'absent')
        if (state === 'absent') { 
            await new Promise(resolve => setTimeout(resolve, 150));
        } 
    }

    // Force keyboard colors to update after animation is complete
    forceKeyboardColors();
}

// Update the keyboard
function updateKeyboard(guessOrLetter, resultOrState) {
    const processLetter = (letter, newState) => {
        const normalizedLetter = normalizeSigma(letter);
        const keyElement = keyboardContainer.querySelector(`[data-key="${normalizedLetter}"]`);
        if (!keyElement || keyElement.classList.contains('correct')) { return; }

        const currentKeyState = keyStates[normalizedLetter];
        let finalState = newState;

        if (currentKeyState === 'correct') {
            finalState = 'correct';
        } else if (currentKeyState === 'present' && newState === 'absent') {
            finalState = 'present';
        }

        // Remove all state classes first
        keyElement.classList.remove('correct', 'present', 'absent');
        
        // Then add the appropriate state class
        keyElement.classList.add(finalState);
        
        // Handle disabled state separately
        if (finalState === 'absent' && currentKeyState !== 'correct' && currentKeyState !== 'present') {
            keyElement.classList.add('disabled-key');
            keyElement.disabled = true;
        }

        keyStates[normalizedLetter] = finalState;
    };

    // Process a single letter with a state
    if (typeof guessOrLetter === 'string' && guessOrLetter.length === 1) {
        processLetter(guessOrLetter, resultOrState);
        return;
    }
    
    // Process a guess string with an array of states
    if (typeof guessOrLetter === 'string' && Array.isArray(resultOrState)) {
        const letters = guessOrLetter.split('');
        letters.forEach((letter, index) => {
            processLetter(letter, resultOrState[index]);
        });
        return;
    }
}

// Shake a row for invalid guesses
function shakeRow(rowIndex) {
    const rowElement = getRowElement(rowIndex);
    if (rowElement) {
        rowElement.classList.add('animate-shake');
        setTimeout(() => {
            rowElement.classList.remove('animate-shake');
        }, 500);
    }
}

// Dance animation for correct guesses
function danceRow(rowIndex) {
    const rowTiles = gridContainer.querySelectorAll(`[data-row="${rowIndex}"] .tile`);
    if (!rowTiles) return;
    rowTiles.forEach((tile, index) => {
        if (!tile) return;
        setTimeout(() => {
            tile.classList.add('animate-dance');
        }, index * 100);
    });
}

// Helper function to normalize sigma characters
function normalizeSigma(word) {
    // Return the word if it's not a string or is empty
    if (typeof word !== 'string' || !word) {
        return word;
    }
    // Replace all final sigma (ς) with medial sigma (σ)
    return word.replace(/ς/g, 'σ');
}

// Initialize keyboard with case insensitivity
function initializeKeyboardWithCaseInsensitivity() {
    // Add event listeners to all keyboard buttons with case insensitivity
    document.querySelectorAll('.key').forEach(key => {
        const keyChar = key.dataset.key; // This gets the lowercase data-key
        if (keyChar && keyChar.length === 1 && 'αβγδεζηθικλμνξοπρστυφχψω'.includes(keyChar.toLowerCase())) {
            // Store both lowercase and uppercase versions for comparison
            key.dataset.keyNormalized = normalizeSigma(keyChar.toLowerCase());
            
            // Also add the uppercase version for easier lookup
            key.dataset.keyUpper = keyChar.toUpperCase();
        }
    });
}

// Initialize the game
function initializeGame() {
    currentRowIndex = 0;
    currentColIndex = 0;
    guesses = Array(MAX_GUESSES).fill(null).map(() => Array(WORD_LENGTH).fill(''));
    isGameOver = false;
    isProcessing = false;
    keyStates = {};
    revealUsed = false;
    messageElement.textContent = '';
    playAgainButton.classList.add('hidden');
    revealLetterButton.disabled = false;
    revealLetterButton.classList.remove('opacity-50', 'cursor-not-allowed');
    
    // Reset explanation container if it exists
    if (explanationElement) {
        explanationElement.classList.add('hidden');
        explanationElement.innerHTML = '';
        explanationElement.classList.remove('fade-in');
    }
    
    if (gridContainer) {
        gridContainer.style.display = '';                                     
    }
    
    // Reset any faded tiles
    const allTiles = document.querySelectorAll('.tile');
    allTiles.forEach(tile => {
        tile.classList.remove('fade-out');
    });
    
    console.log(`Theme: ${themeName}, Length: ${WORD_LENGTH}, Target: ${targetWord}`);
    console.log(`Target explanation available: ${targetExplanation ? 'Yes' : 'No'}`);
    
    createGrid();
    createKeyboard();
    addEventListeners();
}

// Create the game grid
function createGrid() {
    gridContainer.innerHTML = '';
    gridContainer.style.maxWidth = `${WORD_LENGTH * 65}px`;
    for (let r = 0; r < MAX_GUESSES; r++) {
        const row = document.createElement('div');
        row.classList.add('grid', `grid-cols-${WORD_LENGTH}`, 'gap-1');
        row.dataset.row = r;
        for (let c = 0; c < WORD_LENGTH; c++) {
            const tile = document.createElement('div');
            tile.classList.add('tile');
            tile.dataset.row = r;
            tile.dataset.col = c;
            row.appendChild(tile);
        }
        gridContainer.appendChild(row);
    }
}

// Create the keyboard
function createKeyboard() {
    keyboardContainer.innerHTML = '';
    keyboardLayout.forEach(rowKeys => {
        const rowDiv = document.createElement('div'); 
        rowDiv.classList.add('flex', 'justify-center', 'flex-wrap', 'mb-1');
        rowKeys.forEach(key => {
            const button = document.createElement('button'); 
            button.classList.add('key');
            if (key === 'Enter') { 
                button.textContent = '✔'; 
            } else if (key === 'Backspace') { 
                button.textContent = '⌫'; 
            } else { 
                button.textContent = key;
            }
            
            // Always store lowercase in data-key attribute for consistency
            button.dataset.key = key.toLowerCase();
            
            // Add normalized and uppercase versions for easier matching
            if (key.length === 1 && 'αβγδεζηθικλμνξοπρστυφχψω'.includes(key.toLowerCase())) {
                button.dataset.keyNormalized = normalizeSigma(key.toLowerCase());
                button.dataset.keyUpper = key.toUpperCase();
            }
            
            if (key === 'Enter' || key === 'Backspace') { 
                button.classList.add('wide'); 
            }
            
            const state = keyStates[key.toLowerCase()]; 
            if (state) { button.classList.add(state); }
            
            button.addEventListener('click', () => handleKeyPress(key.toLowerCase())); 
            rowDiv.appendChild(button);
        }); 
        keyboardContainer.appendChild(rowDiv);
    });
}

// Force keyboard colors based on current game state
function forceKeyboardColors() {
    // For each letter in the target word, directly mark its keyboard key
    const targetLetters = targetWord.split('');
    
    // Track which letters are in correct positions and which are just present
    const correctPositions = new Array(WORD_LENGTH).fill(false);
    const correctLetters = new Set();
    const presentLetters = new Set();
    
    // First, analyze the current grid state to identify correct and present letters
    for (let r = 0; r <= currentRowIndex; r++) {
        const rowGuess = guesses[r];
        if (!rowGuess || !rowGuess.join('')) continue;
        
        // First pass: mark correct positions
        for (let c = 0; c < WORD_LENGTH; c++) {
            const guessLetter = rowGuess[c];
            if (!guessLetter) continue;
            
            const normalizedGuess = normalizeSigma(guessLetter);
            const normalizedTarget = normalizeSigma(targetLetters[c]);
            
            if (normalizedGuess === normalizedTarget) {
                correctPositions[c] = true;
                correctLetters.add(normalizedGuess.toUpperCase());
            }
        }
        
        // Second pass: mark present letters (that aren't already correct)
        for (let c = 0; c < WORD_LENGTH; c++) {
            const guessLetter = rowGuess[c];
            if (!guessLetter) continue;
            
            const normalizedGuess = normalizeSigma(guessLetter);
            const normalizedGuessUpper = normalizedGuess.toUpperCase();
            
            // Skip if this position was correct
            if (correctPositions[c]) continue;
            
            // Check if this letter exists anywhere in the target word
            if (targetLetters.some(targetChar => 
                normalizeSigma(targetChar) === normalizedGuess)) {
                presentLetters.add(normalizedGuessUpper);
            }
        }
    }
    
    // Apply the colors to the keyboard
    // Important: Greek alphabet includes both uppercase and lowercase
    const greekAlphabet = 'αβγδεζηθικλμνξοπρστυφχψωΑΒΓΔΕΖΗΘΙΚΛΜΝΞΟΠΡΣΤΥΦΧΨΩ';
    
    for (let letter of greekAlphabet) {
        // Try both cases - important for keys like Τ vs τ
        const possibleSelectors = [
            `[data-key="${letter.toLowerCase()}"]`,
            `[data-key="${letter.toUpperCase()}"]`,
            `[data-key="${letter}"]`
        ];
        
        for (const selector of possibleSelectors) {
            const keyElement = keyboardContainer.querySelector(selector);
            if (!keyElement) continue;
            
            // Normalize for checking
            const normalizedLetter = normalizeSigma(letter).toUpperCase();
            
            // Clear previous state classes
            keyElement.classList.remove('correct', 'present', 'absent');
            
            // Apply the appropriate class and force the color
            if (correctLetters.has(normalizedLetter)) {
                keyElement.classList.add('correct');
                keyElement.style.backgroundColor = '#6aaa64';
                keyElement.style.borderColor = '#6aaa64';
                keyElement.style.color = 'white';
            } else if (presentLetters.has(normalizedLetter)) {
                keyElement.classList.add('present');
                keyElement.style.backgroundColor = '#c9b458';
                keyElement.style.borderColor = '#c9b458';
                keyElement.style.color = 'white';
            }
        }
    }
}

// Initialize the game if all required variables are defined
if (typeof WORD_LENGTH === 'number' && typeof targetWord === 'string' && Array.isArray(GREEK_WORDS) && typeof themeName === 'string') {
    // Wait for DOM to be fully loaded
    document.addEventListener('DOMContentLoaded', function() {
        initializeGame();
    });
} else {
    console.error("Game constants not properly defined.");
    showMessage(MSG_ERROR_INIT, 0);
}