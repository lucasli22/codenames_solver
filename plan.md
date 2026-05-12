# Codenames Solver Plan

## Goal
Codenames solver for players playing codenames that need assistance, whether 
for spymasters or operatives.
For spymasters, it gives the best possible hints for operatives using NLP's.
For the operatives, it gives the safest words to choose given the current context.

## User Stories 
- The user should be able to put the current grid of words into the software 
- The user should pick what role they are currently playing as
- If the uer is a spymaster, they should be able to put down the agent identities
- The program should give the spymaster a word followed by a number 
- Operatives should be able to enter the spymaster's guesses from both teams 
- The program should give operatives a list of words in the current grid
ranked by its likelyhood of being an agent of the same colour, opposing colour, 
neutral, and the assasssin that adds to 100%
- Operatives should also be able to enter cards that are being revealed after each
round


