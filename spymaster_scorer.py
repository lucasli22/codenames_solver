import os
import numpy as np
from sentence_transformers import SentenceTransformer
from models import Card, Hint, Identity
from nltk.corpus import wordnet as wn
from operative_scorer import top_k_by_similarity

CORPUS_CACHE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "corpus_cache.npz")

SAFETY_THRESHOLD = 0.5

# Logistic transform: maps cosine similarity -> probability the operative would pick that word.
SIGMOID_A = 12
SIGMOID_B = 4.8

# Blanton's weight scheme (per-word contributions to utility)
ALLY_WEIGHT     =   1.0
ENEMY_WEIGHT    =  -1.0
NEUTRAL_WEIGHT  =  -0.04
ASSASSIN_WEIGHT =  -5.0

# A board word is "covered" by a clue if its probability exceeds this threshold.
COVERAGE_THRESHOLD = 0.5

# Number of top hints to display
TOP_N = 15

model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

TEST_WORDS = [
    Card(word="canada",     identity=Identity.RED_AGENT,  is_revealed=False),
    Card(word="trip",       identity=Identity.RED_AGENT,  is_revealed=False),
    Card(word="beat",       identity=Identity.RED_AGENT,  is_revealed=False),
    Card(word="jam",        identity=Identity.RED_AGENT,  is_revealed=False),
    Card(word="triangle",   identity=Identity.RED_AGENT,  is_revealed=False),
    Card(word="root",       identity=Identity.RED_AGENT,  is_revealed=False),
    Card(word="forest",     identity=Identity.RED_AGENT,  is_revealed=False),
    Card(word="ray",        identity=Identity.RED_AGENT,  is_revealed=False),
    Card(word="sock",       identity=Identity.RED_AGENT,  is_revealed=False),
    Card(word="genius",     identity=Identity.BLUE_AGENT, is_revealed=False),
    Card(word="skyscraper", identity=Identity.BLUE_AGENT, is_revealed=False),
    Card(word="mail",       identity=Identity.BLUE_AGENT, is_revealed=False),
    Card(word="lawyer",     identity=Identity.BLUE_AGENT, is_revealed=False),
    Card(word="stream",     identity=Identity.BLUE_AGENT, is_revealed=False),
    Card(word="flute",      identity=Identity.BLUE_AGENT, is_revealed=False),
    Card(word="worm",       identity=Identity.BLUE_AGENT, is_revealed=False),
    Card(word="mars",       identity=Identity.BLUE_AGENT, is_revealed=False),
    Card(word="witch",      identity=Identity.NEUTRAL,    is_revealed=False),
    Card(word="torch",      identity=Identity.NEUTRAL,    is_revealed=False),
    Card(word="jack",       identity=Identity.NEUTRAL,    is_revealed=False),
    Card(word="printer",    identity=Identity.NEUTRAL,    is_revealed=False),
    Card(word="smuggler",   identity=Identity.NEUTRAL,    is_revealed=False),
    Card(word="kid",        identity=Identity.NEUTRAL,    is_revealed=False),
    Card(word="vacuum",     identity=Identity.NEUTRAL,    is_revealed=False),
    Card(word="cloak",      identity=Identity.ASSASSIN,   is_revealed=False),
]

TEST_PAST_HINTS = [
    Hint(clue="physics", num=3, guesses=[]),
]

def _build_corpus_cache():
    print(f"Building corpus cache at {CORPUS_CACHE_PATH} (one-time, may take a few minutes)...")
    corpus = set()
    for synset in wn.all_eng_synsets():
        for lemma in synset.lemmas():
            word = lemma.name()
            word_lower = word.lower()
            if "_" not in word and lemma.count() > 1:
                corpus.add(word_lower)

    words = sorted(corpus)
    embeddings = model.encode(words, show_progress_bar=True)
    np.savez_compressed(CORPUS_CACHE_PATH, words=np.array(words), embeddings=embeddings)
    print(f"Cached {len(words)} words.")


def init_corpus(word_list: list[str]):
    """Return (corpus_words, corpus_embeddings) with board words and their morphy roots removed."""
    if not os.path.exists(CORPUS_CACHE_PATH):
        _build_corpus_cache()

    data = np.load(CORPUS_CACHE_PATH, allow_pickle=True)
    cached_words = data["words"]
    cached_embeddings = data["embeddings"]

    word_set = set(word_list)
    root_set = {wn.morphy(w) or w for w in word_set}

    mask = np.array([
        w not in word_set and (wn.morphy(w) or w) not in root_set
        for w in cached_words
    ])

    filtered_words = [str(w) for w, keep in zip(cached_words, mask) if keep]
    filtered_embeddings = cached_embeddings[mask]
    return filtered_words, filtered_embeddings

def get_active_ally_words(words: list[Card], past_hints: list[Hint], identity: Identity,
                          board_words: list[str], board_embeddings) -> list[str]:
    claimed = set() 
    for hint in past_hints or TEST_PAST_HINTS:
        hint_embedding = model.encode([hint.clue])
        board_similarities = model.similarity(board_embeddings, hint_embedding).numpy()[:, 0]
        top_words = top_k_by_similarity(hint.num, board_similarities, board_words)
        claimed.update(word for score, word in top_words if score > SAFETY_THRESHOLD)

    ally_words = [w for w in words or TEST_WORDS if w.identity == identity]
    active_ally_words = [w.word for w in ally_words or TEST_WORDS if w.word not in claimed 
                         and not w.is_revealed]

    return active_ally_words

def get_active_non_ally_words(words: list[Card], identity: Identity) -> tuple[list[str], list[str], list[str]]:
    enemy_identity = Identity.RED_AGENT if identity == Identity.BLUE_AGENT else Identity.BLUE_AGENT
    active = [w for w in words or TEST_WORDS if w.is_revealed == False]

    enemies = [w.word for w in active if w.identity == enemy_identity]
    neutrals = [w.word for w in active if w.identity == Identity.NEUTRAL]
    asassins = [w.word for w in active if w.identity == Identity.ASSASSIN]

    return enemies, neutrals, asassins

def sigmoid(x):
    return 1 / (1 + np.exp(-(SIGMOID_A * x - SIGMOID_B)))


def weighted_prob_sum(corpus_embeddings, target_embeddings, weight: float):
    if target_embeddings is None:
        return np.zeros(corpus_embeddings.shape[0])
    sim_matrix = model.similarity(corpus_embeddings, target_embeddings).numpy()
    return weight * sigmoid(sim_matrix).sum(axis=1)


def spymaster_scorer(words: list[Card], past_hints: list[Hint], identity: Identity):
    board_words = [w.word for w in words or TEST_WORDS]
    corpus_list, corpus_embeddings = init_corpus(board_words)

    used_clues = {h.clue.lower() for h in (past_hints or TEST_PAST_HINTS)}
    if used_clues:
        mask = np.array([w not in used_clues for w in corpus_list])
        corpus_list = [w for w, keep in zip(corpus_list, mask) if keep]
        corpus_embeddings = corpus_embeddings[mask]
    
    board_embeddings = model.encode(board_words)
    active_ally_words = get_active_ally_words(words, past_hints, identity,
                                              board_words, board_embeddings)
    ally_embeddings = model.encode(active_ally_words)

    enemies, neutrals, assassins = get_active_non_ally_words(words, identity)
    enemy_embeddings    = model.encode(enemies)   if enemies   else None
    neutral_embeddings  = model.encode(neutrals)  if neutrals  else None
    assassin_embeddings = model.encode(assassins) if assassins else None

    # Utility = Σ weight(c) * sigmoid(sim(candidate, c)) for every board word c.
    # No top-k slicing: the math itself decides which words contribute meaningfully.
    ally_score     = weighted_prob_sum(corpus_embeddings, ally_embeddings,     ALLY_WEIGHT)
    enemy_score    = weighted_prob_sum(corpus_embeddings, enemy_embeddings,    ENEMY_WEIGHT)
    neutral_score  = weighted_prob_sum(corpus_embeddings, neutral_embeddings,  NEUTRAL_WEIGHT)
    assassin_score = weighted_prob_sum(corpus_embeddings, assassin_embeddings, ASSASSIN_WEIGHT)

    utilities = ally_score + enemy_score + neutral_score + assassin_score

    # Implicit k per candidate: count of ally words above the coverage threshold.
    ally_sim_matrix = model.similarity(corpus_embeddings, ally_embeddings).numpy()
    ally_probs = sigmoid(ally_sim_matrix)
    implicit_k = (ally_probs > COVERAGE_THRESHOLD).sum(axis=1)

    order = np.argsort(-utilities)
    results = []
    for idx in order[:TOP_N]:
        if utilities[idx] <= 0:
            break
        results.append((float(utilities[idx]), corpus_list[idx], int(implicit_k[idx])))

    return results


def print_results(results: list, identity: Identity):
    print(f"\n=== Spymaster Hints ({identity.value}) ===")
    print(f"  {'hint':<15} {'k':>3}   utility")
    for utility, hint, k in results:
        print(f"  {hint:<15} {k:>3}   {utility:.4f}")


if __name__ == "__main__":
    results = spymaster_scorer([], [], Identity.RED_AGENT)
    print_results(results, Identity.RED_AGENT)