import type { Card, Game } from "./types";

const BASE_URL = "http://localhost:8000";

export interface SpymasterHint {
  hint: string;
  k: number;
  utility: number;
}

export interface OperativeRanking {
  word: string;
  score: number;
}

export interface OperativeScoreResponse {
  rankings: OperativeRanking[];
  per_hint: Record<string, OperativeRanking[]>;
}

async function request<T>(path: string, body: unknown): Promise<T> {
  const res = await fetch(`${BASE_URL}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail ?? `Request failed: ${res.status}`);
  }
  return res.json();
}

export const api = {
  createSpymasterGame: (words: Card[]) =>
    request<Game>("/game/spymaster", { words }),

  createOperativeGame: (words: string[], first_team: "red_spymaster" | "blue_spymaster") =>
    request<Game>("/game/operative", { words, first_team }),

  scoreSpymaster: (game: Game) =>
    request<{ identity: string; clue: SpymasterHint[] }>("/game/score/spymaster", game),

  scoreOperative: (game: Game) =>
    request<OperativeScoreResponse>("/game/score/operative", game),
};
