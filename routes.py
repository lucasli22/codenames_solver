from fastapi import APIRouter, HTTPException
from models import Game, Identity, GameState, Card, CreateSpymasterGameRequest, CreateOperativeGameRequest

N_ROWS = 5
N_COLS = 5

router = APIRouter()


@router.get("/")
def read_root():
    return {"Hello": "World"}

@router.post("/game/spymaster")
def create_game_spymaster(request: CreateSpymasterGameRequest):
    words = request.words
    if len(words) != 25:
        raise HTTPException(status_code=400, detail="Must provide exactly 25 words")

    board = []
    index = 0
    n_blue = 0
    n_red = 0 
    for x in range(N_ROWS):
        row = []
        for y in range(N_COLS):
            if words[index].identity == Identity.BLUE_AGENT:
                n_blue += 1
            else:
                n_red += 1

            card = Card(word=words[index].word, identity=words[index].identity, is_revealed=False)
            row.append(card)
            index += 1
        board.append(row)

    return Game(board=board, game_state=GameState.BLUE_SPYMASTER if n_blue > n_red else GameState.RED_SPYMASTER,
        red_hints=[], blue_hints=[])
    
@router.post("/game/operative")
def create_game_operative(request: CreateOperativeGameRequest):
    words = request.words
    if len(words) != 25:
        raise HTTPException(status_code=400, detail="Must provide exactly 25 words")

    if request.first_team not in (GameState.RED_SPYMASTER, GameState.BLUE_SPYMASTER):
        raise HTTPException(status_code=400, detail="first_team must be a spymaster state") 
    
    board = []
    index = 0
    for x in range(N_ROWS):
        row = []
        for y in range(N_COLS):
            card = Card(word=words[index], identity=None, is_revealed=False)
            row.append(card)
            index += 1
        board.append(row)

    return Game(board=board, game_state=request.first_team, red_hints=[], blue_hints=[])
