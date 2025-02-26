# AI Rap Battle

An AI-powered application that creates rap battles between famous historical figures, celebrities, or fictional characters. Leverage the power of AI to generate entertaining, rhyming rap verses that capture each character's unique style and personality.

## Features

- Create rap battles between any two famous figures
- Watch as each rapper takes turns delivering AI-generated verses
- Verses maintain the unique voice and style of each character
- Content is relevant to each character's background, achievements, and personality
- Configure up to 10 rounds of back-and-forth rapping
- Real-time streaming of verse generation

## Project Structure

```
ai-rap-battle/
├── src/
│   ├── app/
│   │   ├── api/
│   │   │   └── routes/
│   │   │       └── battle.py
│   │   ├── models/
│   │   │   └── battle.py
│   │   ├── services/
│   │   │   └── battlebot/
│   │   │       ├── graph.py
│   │   │       ├── prompts.py
│   │   │       └── utils.py
│   │   ├── static/
│   │   │   ├── index.html
│   │   │   ├── battle-ui.html
│   │   │   ├── scripts.js
│   │   │   └── styles.css
│   │   ├── utils/
│   │   │   └── logger.py
│   │   └── main.py
├── .env.example
├── .gitignore
└── pyproject.toml
```

## Technology Stack

- **Backend**: FastAPI
- **AI Framework**: LangGraph for orchestrating the rap battle flow
- **Language Model**: OpenAI GPT models via LangChain
- **Frontend**: HTML, CSS, and vanilla JavaScript

## Setup Instructions

1. Clone the repository:
   ```bash
   git clone https://github.com/oksmith/ai-rap-battle.git
   cd ai-rap-battle
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies with Poetry:
   ```bash
   pip install poetry
   poetry install
   ```

4. Set up environment variables:
   - Copy `.env.example` to `.env`
   - Add your OpenAI API key to the `.env` file

5. Run the application:
   ```bash
   poetry run uvicorn src.app.main:app --reload
   ```

6. Open your browser and navigate to [http://localhost:8000](http://localhost:8000)

## Usage

1. On the main page, enter the names of two famous figures you want to battle
2. Select the number of rounds (1-10)
3. Click "Start Battle" to begin
4. Watch as the AI generates rap verses for each character in turn
5. When the battle is complete, you can start a new battle

## Example Matchups

- Albert Einstein vs. Stephen Hawking
- William Shakespeare vs. Dr. Seuss
- Nikola Tesla vs. Thomas Edison
- Aristotle vs. Friedrich Nietzsche
- Leonardo da Vinci vs. Pablo Picasso
- Marie Curie vs. Ada Lovelace
- Cleopatra vs. Queen Elizabeth I
- Abraham Lincoln vs. Winston Churchill

## Development

This project uses LangGraph to manage the flow of the rap battle. The main components are:

- `BattleGraph`: Manages the state and flow of the rap battle
- `battle.py` routes: Handle API requests for creating and streaming battles
- Frontend UI: Provides an interface for setting up and viewing battles

## Next Steps

Ways to extend the project:
* Audio Generation: Add text-to-speech to have the verses read aloud in character-appropriate voices(!)
* Character Profiles: Allow access to the internet e.g. Wikipedia, to gather context about each rapper to improve the AI's understanding(!)
* Voting System: Allow users to vote on who won each round or the overall battle(?)
* Custom Themes: Allow users to specify themes or topics for the battle(?)
* Multi-lingual Support: Enable battles in different languages(?)
