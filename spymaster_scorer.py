from sentence_transformers import SentenceTransformer
from models import Card, Hint, Identity
from nltk.corpus import wordnet as wn
from operative_scorer import top_k_by_similarity

SAFETY_THRESHOLD = 0.5
model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
corpus = set()

TEST_WORDS = [
    Card(word=w, identity=None, is_revealed=False) for w in [
        "canada", "trip", "beat", "jam", "triangle", "root",
        "forest", "ray", "sock", "genius", "skyscraper", "mail",
        "lawyer", "stream", "flute", "worm", "mars", "witch",
        "torch", "jack", "printer", "smuggler", "kid", "vacuum",
        "cloak"
    ]
]

TEST_PAST_HINTS = [
    Hint(clue="physics", num=3, guesses=[]),
]

def init_corpus(word_list: list[str]) -> list[str]:
    word_set = set(word_list)
    for synset in wn.all_eng_synsets():
        for lemma in synset.lemmas():
            word = lemma.name()
            if "_" not in word and word not in word_set and lemma.count() > 1:
                corpus.add(word.lower())
    print(len(corpus))

    return list(corpus)
def get_active_ally_words(words: list[Card], past_hints: list[Hint], identity: Identity,
                          board_words: list[str], board_embeddings) -> list[str]:
    claimed = set() 
    for hint in past_hints or TEST_PAST_HINTS:
        hint_embedding = model.encode([hint.clue])
        board_similarities = model.similarity(board_embeddings, hint_embedding).numpy()[:, 0]
        top_words = top_k_by_similarity(hint.num, board_similarities, board_words)
        claimed.update(word for score, word in top_words if score > SAFETY_THRESHOLD)

    ally_words = [w.word for w in words or TEST_WORDS if w.identity == identity]
    active_ally_words = [w for w in ally_words or TEST_WORDS if w not in claimed 
                         and not w.is_revealed]

    return active_ally_words

def get_active_enemy_words(words: list[Card], identity: Identity) -> list[str]:
    active_enemy_words = [w.word for w in words or TEST_WORDS if not w.is_revealed 
                          and w.identity != identity]
    return active_enemy_words

def spymaster_scorer(words: list[Card], past_hints: list[Hint], identity: Identity):
    board_words = [w.word for w in words or TEST_WORDS]
    corpus_list = init_corpus(board_words)
    corpus_embeddings = model.encode(corpus_list)

    board_embeddings = model.encode(board_words)
    active_ally_words = get_active_ally_words(words, past_hints, identity, 
                                              board_words, board_embeddings)
    ally_embeddings = model.encode(active_ally_words)
    active_enemy_words = get_active_enemy_words(words, identity)
    enemy_embeddings = model.encode(active_enemy_words)

    ally_sim_matrix = model.similarity(ally_embeddings, corpus_embeddings)
    enemy_sim_matrix = model.similarity(enemy_embeddings, corpus_embeddings)

        

    

if __name__ == "__main__":
    spymaster_scorer([], [], Identity.RED_AGENT)