export type Identity = "red_agent" | "blue_agent" | "neutral" | "assassin"

export type GameState = "red_spymaster" | "blue_spymaster" | "red_operative" | 
"blue_operative"

export interface Card { 
    word: string; 
    identity: Identity | null;
    is_revealed: boolean
}

export interface Hint {
    clue: string;
    num: number;
    guesses: string[]
}

export interface Game {
    board: Card[][];
    game_state: GameState;
    red_hints: Hint[];
    blue_hints: Hint[]
}
