from sentence_transformers import SentenceTransformer
from models import Card, Hint, Identity
from nltk.corpus import wordnet as wn
from operative_scorer import top_k_by_similarity

SAFETY_THRESHOLD = 0.5
ENEMY_WEIGHT = 1.0
NEUTRAL_WEIGHT = 0.5
ASSASSIN_WEIGHT = 3.0

model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
corpus = set()

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

def init_corpus(word_list: list[str]) -> list[str]:
    word_set = set(word_list)
    root_set = {wn.morphy(w) or w for w in word_set}

    for synset in wn.all_eng_synsets():
        for lemma in synset.lemmas():
            word = lemma.name()
            word_lower = word.lower()
            root = wn.morphy(word_lower) or word_lower
            if ("_" not in word
                    and word_lower not in word_set
                    and root not in root_set
                    and lemma.count() > 1):
                corpus.add(word_lower)

    return list(corpus)
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

def top_k_hints(k: int, ally_sim: list[float], enemy_sim: list[float], 
                neutral_sim: list[float], assassin_sim: list[float], 
                corpus_list: list[str]):
    scores = []

    for i in range(len(ally_sim)):
        top_k_sims = sorted(ally_sim[i], reverse=True)[:k]
        penalty_per_word = (
            (ENEMY_WEIGHT    * max(enemy_sim[i])    if enemy_sim    is not None else 0) +
            (NEUTRAL_WEIGHT  * max(neutral_sim[i])  if neutral_sim  is not None else 0) +
            (ASSASSIN_WEIGHT * max(assassin_sim[i]) if assassin_sim is not None else 0)
        )
        scores.append(sum(top_k_sims) - k * penalty_per_word)


    paired = [(score, word) for score, word in zip(scores, corpus_list)]
    return max(paired)
    
def spymaster_scorer(words: list[Card], past_hints: list[Hint], identity: Identity):
    board_words = [w.word for w in words or TEST_WORDS]
    corpus_list = init_corpus(board_words)
    corpus_embeddings = model.encode(corpus_list)

    board_embeddings = model.encode(board_words)
    active_ally_words = get_active_ally_words(words, past_hints, identity, 
                                              board_words, board_embeddings)
    ally_embeddings = model.encode(active_ally_words)

    enemy_words, neutral_words, asassin_words = get_active_non_ally_words(words, identity)
    enemy_embeddings = model.encode(enemy_words) if enemy_words else None
    neutral_embeddings = model.encode(neutral_words) if neutral_words else None
    asassin_embeddings = model.encode(asassin_words) if asassin_words else None
    
    ally_sim_matrix     = model.similarity(corpus_embeddings, ally_embeddings).numpy()
    enemy_sim_matrix    = model.similarity(corpus_embeddings, enemy_embeddings).numpy()    if enemy_embeddings   is not None else None
    neutral_sim_matrix  = model.similarity(corpus_embeddings, neutral_embeddings).numpy()  if neutral_embeddings is not None else None
    assassin_sim_matrix = model.similarity(corpus_embeddings, asassin_embeddings).numpy()  if asassin_embeddings is not None else None


    results = {}
    for k in range(1, len(active_ally_words) + 1):
        best = top_k_hints(k, ally_sim_matrix, enemy_sim_matrix, neutral_sim_matrix, assassin_sim_matrix, corpus_list)
        if best and best[0] > 0:
            results[k] = best

    return results


def print_results(results: dict, identity: Identity):
    print(f"\n=== Spymaster Hints ({identity.value}) ===")
    for k, (score, hint) in results.items():
        print(f"  {hint:<15} {k}  (score: {float(score):.4f})")


if __name__ == "__main__":
    results = spymaster_scorer([], [], Identity.RED_AGENT)
    print_results(results, Identity.RED_AGENT)