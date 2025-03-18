# Diskolos: Attic Greek Story Generator

Diskolos is an automated tool that generates, corrects, and publishes authentic Attic Greek stories to a static website.

## Overview

This project uses the Anthropic Claude API to create a two-agent workflow:

1. **AtticGreekWriter**: Generates original stories written in classical Attic Greek
2. **DiskolosEditor**: Reviews and corrects the stories for grammatical accuracy

The resulting stories are automatically published to a static website with an index and individual story pages.

## Features

- Automated story generation with authentic Attic Greek vocabulary and grammar
- Professional editing/correction by an Attic Greek grammar specialist
- HTML publication with proper formatting and navigation
- Static website generation with featured stories and archives

## Requirements

- Python 3.8+
- Anthropic API key (for Claude 3.7 Sonnet model)

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/diskolos.git
   cd diskolos
   ```

2. Install dependencies:
   ```
   pip install anthropic
   ```

3. Set up your Anthropic API key as an environment variable:
   ```
   export ANTHROPIC_API_KEY=your_api_key_here
   ```

## Usage

Run the main script to generate and publish a new story:

```
python scripts/diskolos.py
```

The script will:
1. Generate a new Attic Greek story with title
2. Have it corrected by the Diskolos editor
3. Publish it to the website in the `docs` directory

## Website Structure

The generated website is stored in the `docs` directory with the following structure:

```
docs/
├── index.html                 # Main page with featured story and archive
├── assets/                    # CSS and image files
└── stories/                   # Individual story pages
    └── YYYYMMDD-title.html    # Date-prefixed story files
```

## Customization

- Edit the system prompts in `AtticGreekWriter` and `DiskolosEditor` classes to adjust the style and focus of the stories
- Modify the HTML templates in the `save_to_website` function to change the website appearance

## Cost Estimation

The script provides an estimated cost based on token usage with Claude 3.7 Sonnet pricing:
- Input tokens: $3.00 per million tokens
- Output tokens: $15.00 per million tokens

## License

MIT

## Credits

Created using the Anthropic Claude API.