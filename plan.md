# Codenames Solver Plan

## Goal
Codenames solver for players playing codenames that need assistance, whether 
for spymasters or operatives.
For spymasters, it gives the best possible hints for operatives using NLP's.
For the operatives, it gives the safest words to choose given the current context.

## User Stories 
- The user should be able to put the current grid of words into the software 
- The user should pick what role they are currently playing as
- If the user is a spymaster, they should be able to put down the agent identities
- The spymaster should be able to choose the risk level of the generated hints
- The program should give the spymaster a word followed by a number 
- Operatives should be able to enter the spymaster's guesses from both teams 
- The program should give operatives a list of words in the current grid
ranked by its likelyhood of being an agent of the same colour, opposing colour, 
neutral, and the assasssin that adds to 100%
- Operatives should also be able to enter cards that are being revealed after each
round

## Data Models
- 5x5 grid of words
- Each spymaster hints
- Each operative guesses
- Choices for each round 

## Technical components 
- Backend/API - FastAPI, python
- Frontend/UI - React
- Scoring Algorithm - [Sentence Transformers](https://www.sbert.net/docs/sentence_transformer/pretrained_models.html)
