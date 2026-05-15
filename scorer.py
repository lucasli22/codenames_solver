from sentence_transformers import SentenceTransformer
from models import Card, Hint
model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

ENEMY_WEIGHTING = 1
ASSASSIN_WEIGHTING = 2

TEST_WORDS = [
    Card(word=w, identity=None, is_revealed=False) for w in [
        "ocean", "lantern", "velocity", "forest", "quantum", "harmony",
        "puzzle", "crystal", "volcano", "compass", "galaxy", "shadow",
        "avalanche", "phoenix", "library", "whisper", "meteor", "canyon",
        "spectrum", "pirate", "castle", "nebula", "thunder", "voyage",
        "paradox"
    ]
]

TEST_ALLY_HINTS = [
    Hint(clue="physics", num=3, guesses=[]),
    Hint(clue="books", num=2, guesses=[]),
]

TEST_ENEMY_HINTS = [
    Hint(clue="sea", num=3, guesses=[]),
    Hint(clue="voice", num=2, guesses=[]),
]


def top_k_by_similarity(k: int, scores: list[float], words: list[str]) -> list[tuple[float, str]]:
    paired = [(score, word) for score, word in zip(scores, words)]
    return sorted(paired, reverse=True)[:k]

def get_similarity_matrix(board_embeddings, hints: list[str]) -> list[float]:
    hint_embeddings = model.encode(hints)
    return model.similarity(board_embeddings, hint_embeddings).numpy()

def adjust_similarity(ally_sim_matrix: list[float], enemy_sim_matrix: list[tuple],
                      word_list: list[str]) -> list[float]:
    n_words = len(ally_sim_matrix)
    adjusted_matrix = []

    for i in range(n_words):
        danger = max(enemy_sim_matrix[i]) - max(ally_sim_matrix[i])
        score = (max(ally_sim_matrix[i]) - ENEMY_WEIGHTING * max(enemy_sim_matrix[i]) - 
                 ASSASSIN_WEIGHTING * danger)
        adjusted_matrix.append((score, word_list[i]))
    adjusted_matrix.sort(reverse=True)

    return adjusted_matrix

def operative_scorer(words: list[Card], ally_hints: list[Hint], enemy_hints: list[Hint]):
    word_list = [card.word for card in (words or TEST_WORDS)]
    board_embeddings = model.encode(word_list)

    ally_clue_list = [hint.clue for hint in ally_hints or TEST_ALLY_HINTS]
    ally_sim_matrix = get_similarity_matrix(board_embeddings, ally_clue_list)

    enemy_clue_list = [hint.clue for hint in enemy_hints or TEST_ENEMY_HINTS]
    enemy_sim_matrix = get_similarity_matrix(board_embeddings, enemy_clue_list)

    adjusted_matrix = adjust_similarity(ally_sim_matrix, enemy_sim_matrix, word_list)

    results = {}
    for i, hint in enumerate(ally_hints or TEST_ALLY_HINTS):
        top_words = top_k_by_similarity(hint.num, ally_sim_matrix[:, i], word_list)
        results[hint.clue] = top_words

    return adjusted_matrix, results


def print_results(adjusted_matrix: list[tuple], results: dict):
    print("\n=== Overall Word Rankings (safest to riskiest) ===")
    for rank, (score, word) in enumerate(adjusted_matrix, 1):
        print(f"  {rank:2}. {word:<12} {score:.4f}")

    print("\n=== Top Words Per Hint ===")
    for clue, matches in results.items():
        print(f"\n  Clue: '{clue}'")
        for rank, (score, word) in enumerate(matches, 1):
            print(f"    {rank}. {word:<12} {score:.4f}")


if __name__ == "__main__":
    adjusted_matrix, results = operative_scorer([], [], [])
    print_results(adjusted_matrix, results)
