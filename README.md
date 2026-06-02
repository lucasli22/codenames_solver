# Codenames Solver

An AI-powered assistant for the board game Codenames. Supports both spymaster and operative roles with NLP-based hint generation and word ranking.

## Features

- **Spymaster mode** — generates optimal clue words using expected utility maximisation over a filtered WordNet corpus, scored with logistic-transformed sentence embeddings
- **Operative mode** — ranks board words by safety given the current clues from both teams, accounting for ally hints, enemy hints, and assassin risk
- **Interactive board** — 5×5 grid with color-coded card identities and revealed state
- **Results panel** — slide-in panel showing ranked suggestions with scores

## Tech Stack

- **Frontend**: React, TypeScript, Vite
- **Backend**: FastAPI, Python
- **NLP**: [Sentence Transformers](https://www.sbert.net/) (`all-MiniLM-L6-v2`), [Princeton WordNet](https://www.nltk.org/howto/wordnet.html) via NLTK

## Getting Started

### Backend

```bash
cd backend
pip install fastapi uvicorn sentence-transformers nltk numpy
python3 -m uvicorn main:app --reload
```

The first run will build a WordNet corpus cache (`corpus_cache.npz`) which may take a few minutes. Subsequent runs load from cache.

### Frontend

```bash
cd frontend
npm install
npm run dev
```

The app will be available at `http://localhost:5173`.

## Usage

1. Select your **role** (Spymaster or Operative) and **team colour**
2. Enter all 25 words on the board
3. **Spymaster**: assign identities to each card, then click *Find Clue*
4. **Operative**: select which team goes first, enter each team's hints as they are given, then click *Find Best Guess*
5. Results appear in the side panel ranked by utility or safety score

## Algorithm

The spymaster scorer uses **expected utility maximization** with a logistic-transformed cosine similarity model:

```
U(clue) = Σ sigmoid(sim(clue, ally))
        − Σ sigmoid(sim(clue, enemy))
        − 0.04 · Σ sigmoid(sim(clue, neutral))
        − 5.0  · Σ sigmoid(sim(clue, assassin))
```

Where `sigmoid(x) = 1 / (1 + e^−(12x − 4.8))` maps cosine similarity to an operative pick probability.

The operative scorer ranks board words by adjusted similarity across all active ally clues, penalised by enemy clue proximity and assassin risk.
