import json
import re
from pathlib import Path

import faiss
import numpy as np

from sentence_transformers import SentenceTransformer
from sklearn.feature_extraction.text import TfidfVectorizer


# =========================================================
# Configuration
# =========================================================

MODEL_NAME = "all-MiniLM-L6-v2"

CHUNKS_FILE = "data/processed/chunks.json"
EMBEDDINGS_FILE = "data/processed/embeddings.npy"
INDEX_FILE = "vectorstore/ifrs.index"

DEFAULT_TOP_K = 5

SEMANTIC_WEIGHT = 0.40
LEXICAL_WEIGHT = 0.30
PHRASE_WEIGHT = 0.15
DOMAIN_WEIGHT = 0.15

FAISS_CANDIDATES = 60
TFIDF_CANDIDATES = 60


# =========================================================
# Load data
# =========================================================

print("Loading embedding model...")

model = SentenceTransformer(MODEL_NAME)

print("Loading FAISS index...")

index = faiss.read_index(INDEX_FILE)

print("Loading chunks...")

with open(CHUNKS_FILE, "r", encoding="utf-8") as file:
    chunks = json.load(file)

print("Building TF-IDF index...")

tfidf_vectorizer = TfidfVectorizer(
    lowercase=True,
    strip_accents="unicode",
    ngram_range=(1, 2),
    min_df=1,
    sublinear_tf=True,
    max_features=100000
)

chunk_texts = [
    (
        f"{chunk.get('standard', '')} "
        f"{chunk.get('section', '')} "
        f"{chunk.get('paragraph', '')} "
        f"{chunk.get('text', '')}"
    )
    for chunk in chunks
]

tfidf_matrix = tfidf_vectorizer.fit_transform(
    chunk_texts
)

print(
    f"Search index loaded: {len(chunks)} chunks"
)


# =========================================================
# Standard detection
# =========================================================

def detect_standard(query):

    if not query:
        return None

    match = re.search(
        r"\b(IFRS|IAS)[\s\-_]*(\d{1,3})\b",
        query,
        flags=re.IGNORECASE
    )

    if not match:
        return None

    return (
        f"{match.group(1).upper()} "
        f"{match.group(2)}"
    )


# =========================================================
# Query cleaning
# =========================================================

def clean_query(query):

    return re.sub(
        r"\b(IFRS|IAS)[\s\-_]*\d{1,3}\b",
        "",
        query,
        flags=re.IGNORECASE
    ).strip()


# =========================================================
# Query expansion
# =========================================================

QUERY_EXPANSIONS = {

    "recognition criteria": [
        "criteria are met",
        "contract with a customer",
        "identify the contract",
        "enforceable rights",
        "payment terms",
        "commercial substance",
        "probable collectability"
    ],

    "five steps": [
        "five-step model",
        "identify the contract",
        "identify performance obligations",
        "determine transaction price",
        "allocate transaction price",
        "recognise revenue",
        "recognize revenue"
    ],

    "revenue recognition": [
        "recognise revenue",
        "recognize revenue",
        "performance obligation",
        "transfer of control",
        "transaction price"
    ],

    "depreciation policy": [
        "depreciation method",
        "depreciable amount",
        "useful life",
        "residual value",
        "systematic basis",
        "pattern of consumption"
    ],

    "depreciation": [
        "depreciation method",
        "depreciable amount",
        "useful life",
        "residual value",
        "systematic basis",
        "pattern of consumption"
    ],

    "impairment": [
        "impairment loss",
        "recoverable amount",
        "value in use",
        "fair value less costs of disposal",
        "cash-generating unit"
    ],

    "expected credit loss": [
        "loss allowance",
        "12-month ECL",
        "lifetime ECL",
        "credit risk",
        "significant increase in credit risk"
    ],

    "lease": [
        "right-of-use asset",
        "lease liability",
        "lessee",
        "lease term",
        "discount rate"
    ],

    "fair value": [
        "fair value measurement",
        "exit price",
        "market participant",
        "principal market",
        "most advantageous market"
    ],

    "provision": [
        "present obligation",
        "past event",
        "probable outflow",
        "reliable estimate",
        "recognition criteria",
        "contingent liability"
    ],

    "contingent liability": [
        "possible obligation",
        "present obligation",
        "not probable",
        "reliable estimate",
        "disclose",
        "provision"
    ]
}


# =========================================================
# Intent profiles
# =========================================================

INTENT_PROFILES = {

    "ifrs15_five_steps": {

        "keywords": [
            "five steps",
            "5 steps",
            "five-step",
            "five step",
            "revenue recognition model"
        ],

        "anchors": [
            "identify the contract",
            "performance obligation",
            "transaction price",
            "allocate transaction price",
            "recognise revenue",
            "recognize revenue"
        ],

        "sections": [
            "identifying the contract",
            "performance obligations",
            "transaction price",
            "allocating the transaction price",
            "recognition"
        ]
    },

    "ifrs15_contract": {

        "keywords": [
            "recognition criteria",
            "contract criteria",
            "criteria for a contract",
            "identify the contract",
            "contract with a customer"
        ],

        "anchors": [
            "approved the contract",
            "commercial substance",
            "rights regarding the goods",
            "payment terms",
            "probable that the entity will collect"
        ],

        "sections": [
            "identifying the contract"
        ]
    },

    "ias16_depreciation": {

        "keywords": [
            "depreciation",
            "depreciation policy",
            "depreciation method",
            "useful life",
            "residual value",
            "depreciable amount"
        ],

        "anchors": [
            "systematic basis",
            "pattern in which the asset's future economic benefits",
            "depreciable amount",
            "useful life",
            "residual value",
            "depreciation method"
        ],

        "sections": [
            "depreciation",
            "depreciable amount",
            "useful life"
        ]
    },

    "ias37_provision_contingent": {

        "keywords": [
            "provision",
            "contingent liability",
            "difference between a provision",
            "provision and contingent",
            "provision versus contingent"
        ],

        "anchors": [
            "present obligation",
            "past event",
            "possible obligation",
            "probable outflow",
            "reliable estimate"
        ],

        "sections": [
            "provisions",
            "contingent liabilities",
            "recognition"
        ]
    }
}


# =========================================================
# Detect intent
# =========================================================

def detect_intent(query):

    query_lower = query.lower()

    best_intent = None
    best_score = 0

    for intent_name, profile in INTENT_PROFILES.items():

        score = 0

        for keyword in profile["keywords"]:

            if keyword in query_lower:
                score += 3

        for anchor in profile["anchors"]:

            if anchor in query_lower:
                score += 1

        if score > best_score:

            best_score = score
            best_intent = intent_name

    return best_intent


# =========================================================
# Expand query
# =========================================================

def expand_query(query):

    query_lower = query.lower()

    expansion_terms = []

    for trigger, terms in QUERY_EXPANSIONS.items():

        if trigger in query_lower:

            expansion_terms.extend(terms)

    if expansion_terms:

        return (
            query
            + " "
            + " ".join(expansion_terms)
        )

    return query


# =========================================================
# Parse paragraph number
# =========================================================

def paragraph_number(value):

    if value is None:
        return None

    match = re.match(
        r"^\s*(\d+)",
        str(value)
    )

    if not match:
        return None

    return int(match.group(1))


# =========================================================
# Phrase matching
# =========================================================

def phrase_match_score(query, chunk):

    query_lower = query.lower()

    text = (
        f"{chunk.get('section', '')} "
        f"{chunk.get('text', '')}"
    ).lower()

    score = 0

    # Full query phrase
    if len(query_lower.split()) >= 3:

        if query_lower in text:
            score += 1.0

    # Important query phrases
    phrases = [
        phrase.strip()
        for phrase in re.split(
            r"\band\b|\bunder\b|\bfor\b",
            query_lower
        )
        if len(phrase.strip()) > 3
    ]

    for phrase in phrases:

        if phrase in text:
            score += 0.25

    return min(score, 1.0)


# =========================================================
# Keyword overlap
# =========================================================

def keyword_overlap(query, chunk):

    query_words = set(
        re.findall(
            r"\b[a-zA-Z]{3,}\b",
            query.lower()
        )
    )

    text = (
        f"{chunk.get('section', '')} "
        f"{chunk.get('text', '')}"
    ).lower()

    text_words = set(
        re.findall(
            r"\b[a-zA-Z]{3,}\b",
            text
        )
    )

    if not query_words:
        return 0.0

    overlap = (
        len(query_words.intersection(text_words))
        / len(query_words)
    )

    return min(overlap, 1.0)


# =========================================================
# Domain-aware scoring
# =========================================================

def domain_score(query, chunk, intent):

    if not intent:
        return 0.0

    profile = INTENT_PROFILES[intent]

    text = (
        f"{chunk.get('section', '')} "
        f"{chunk.get('text', '')}"
    ).lower()

    section = chunk.get(
        "section",
        ""
    ).lower()

    score = 0.0

    # Section match is very strong evidence
    for section_name in profile["sections"]:

        if section_name in section:
            score += 0.45

    # Anchor phrase match
    for anchor in profile["anchors"]:

        if anchor in text:
            score += 0.20

    # Keyword match
    query_lower = query.lower()

    for keyword in profile["keywords"]:

        if keyword in text:
            score += 0.10

    return min(score, 1.0)


# =========================================================
# Intent paragraph preference
# =========================================================

def intent_paragraph_score(chunk, intent):

    if not intent:
        return 0.0

    number = paragraph_number(
        chunk.get("paragraph")
    )

    if number is None:
        return 0.0

    # These are retrieval preferences, NOT accounting rules.
    #
    # They help the search engine prioritize the relevant
    # portion of a standard when the user's question clearly
    # expresses a known research intent.

    if intent == "ifrs15_five_steps":

        if 9 <= number <= 45:
            return 1.0

        if 47 <= number <= 86:
            return 0.90

        return 0.0

    if intent == "ifrs15_contract":

        if 9 <= number <= 21:
            return 1.0

        return 0.0

    if intent == "ias16_depreciation":

        if 50 <= number <= 62:
            return 1.0

        if 43 <= number <= 49:
            return 0.65

        return 0.0

    if intent == "ias37_provision_contingent":

        if 10 <= number <= 30:
            return 1.0

        if 31 <= number <= 35:
            return 0.70

        return 0.0

    return 0.0


# =========================================================
# Search
# =========================================================

def search(
    query,
    top_k=DEFAULT_TOP_K,
    standard=None
):

    if not query or not query.strip():

        return []

    original_query = query.strip()

    if standard is None:
        standard = detect_standard(
            original_query
        )

    cleaned_query = clean_query(
        original_query
    )

    expanded_query = expand_query(
        cleaned_query
    )

    intent = detect_intent(
        original_query
    )

    print(
        f"Detected intent: {intent or 'general'}"
    )

    # -----------------------------------------------------
    # Candidate pool
    # -----------------------------------------------------

    candidate_indices = set()

    # -----------------------------------------------------
    # Semantic search
    # -----------------------------------------------------

    query_embedding = model.encode(
        [expanded_query],
        convert_to_numpy=True
    ).astype("float32")

    faiss.normalize_L2(
        query_embedding
    )

    semantic_scores, semantic_indices = (
        index.search(
            query_embedding,
            min(
                FAISS_CANDIDATES,
                len(chunks)
            )
        )
    )

    for idx in semantic_indices[0]:

        if idx >= 0:
            candidate_indices.add(
                int(idx)
            )

    # -----------------------------------------------------
    # TF-IDF search
    # -----------------------------------------------------

    query_tfidf = tfidf_vectorizer.transform(
        [expanded_query]
    )

    lexical_scores_all = (
        tfidf_matrix @ query_tfidf.T
    ).toarray().ravel()

    tfidf_top_indices = np.argsort(
        lexical_scores_all
    )[
        -min(
            TFIDF_CANDIDATES,
            len(chunks)
        ):
    ]

    for idx in tfidf_top_indices:

        candidate_indices.add(
            int(idx)
        )

    # -----------------------------------------------------
    # Standard filter
    # -----------------------------------------------------

    if standard:

        filtered_candidates = {

            idx
            for idx in candidate_indices

            if chunks[idx].get(
                "standard"
            ) == standard
        }

        # If standard filtering produces results,
        # use those candidates.
        if filtered_candidates:

            candidate_indices = (
                filtered_candidates
            )

    # -----------------------------------------------------
    # Build semantic lookup
    # -----------------------------------------------------

    semantic_lookup = {}

    for idx, score in zip(
        semantic_indices[0],
        semantic_scores[0]
    ):

        if idx >= 0:

            semantic_lookup[
                int(idx)
            ] = float(score)

    # -----------------------------------------------------
    # Score candidates
    # -----------------------------------------------------

    scored_results = []

    for idx in candidate_indices:

        chunk = chunks[idx]

        semantic_score = semantic_lookup.get(
            idx,
            0.0
        )

        lexical_score = float(
            lexical_scores_all[idx]
        )

        # Normalize lexical score approximately
        lexical_score = min(
            max(lexical_score, 0.0),
            1.0
        )

        phrase_score = phrase_match_score(
            cleaned_query,
            chunk
        )

        keyword_score = keyword_overlap(
            cleaned_query,
            chunk
        )

        domain = domain_score(
            original_query,
            chunk,
            intent
        )

        intent_paragraph = (
            intent_paragraph_score(
                chunk,
                intent
            )
        )

        # -------------------------------------------------
        # Final score
        # -------------------------------------------------

        final_score = (
            semantic_score * SEMANTIC_WEIGHT
            +
            lexical_score * LEXICAL_WEIGHT
            +
            phrase_score * PHRASE_WEIGHT
            +
            domain * DOMAIN_WEIGHT
        )

        # Small keyword contribution
        final_score += (
            keyword_score * 0.05
        )

        # Intent paragraph preference
        final_score += (
            intent_paragraph * 0.10
        )

        scored_results.append(
            {
                "index": idx,
                "standard": chunk.get(
                    "standard",
                    "Unknown"
                ),
                "paragraph": chunk.get(
                    "paragraph",
                    ""
                ),
                "section": chunk.get(
                    "section",
                    "General"
                ),
                "text": chunk.get(
                    "text",
                    ""
                ),
                "score": float(
                    final_score
                ),
                "semantic_score": float(
                    semantic_score
                ),
                "lexical_score": float(
                    lexical_score
                ),
                "phrase_score": float(
                    phrase_score
                ),
                "domain_score": float(
                    domain
                ),
                "intent_paragraph_score": float(
                    intent_paragraph
                )
            }
        )

    # -----------------------------------------------------
    # Sort
    # -----------------------------------------------------

    scored_results.sort(
        key=lambda item: item["score"],
        reverse=True
    )

    # -----------------------------------------------------
    # Adjacent paragraph expansion
    # -----------------------------------------------------

    expanded_results = []

    selected_indices = set()

    for result in scored_results:

        if len(expanded_results) >= top_k:
            break

        idx = result["index"]

        if idx in selected_indices:
            continue

        expanded_results.append(
            result
        )

        selected_indices.add(
            idx
        )

        # Find immediate adjacent paragraphs
        # from the same standard.
        #
        # They are considered only as supporting
        # candidates and do not automatically replace
        # stronger results.

        for direction in (-1, 1):

            adjacent_idx = idx + direction

            if adjacent_idx < 0:
                continue

            if adjacent_idx >= len(chunks):
                continue

            adjacent_chunk = chunks[
                adjacent_idx
            ]

            if adjacent_chunk.get(
                "standard"
            ) != result["standard"]:

                continue

            adjacent_result = {
                "index": adjacent_idx,
                "standard": adjacent_chunk.get(
                    "standard",
                    "Unknown"
                ),
                "paragraph": adjacent_chunk.get(
                    "paragraph",
                    ""
                ),
                "section": adjacent_chunk.get(
                    "section",
                    "General"
                ),
                "text": adjacent_chunk.get(
                    "text",
                    ""
                ),
                "score": max(
                    result["score"] * 0.82,
                    0.0
                ),
                "semantic_score": 0.0,
                "lexical_score": 0.0,
                "phrase_score": 0.0,
                "domain_score": 0.0,
                "intent_paragraph_score": 0.0,
                "adjacent": True
            }

            # Do not immediately add it.
            # It enters a secondary pool.
            expanded_results.append(
                adjacent_result
            )

            selected_indices.add(
                adjacent_idx
            )

            if len(expanded_results) >= (
                top_k + 2
            ):
                break

        if len(expanded_results) >= (
            top_k + 2
        ):
            break

    # -----------------------------------------------------
    # Re-rank after adjacent expansion
    # -----------------------------------------------------

    expanded_results.sort(
        key=lambda item: item["score"],
        reverse=True
    )

    # -----------------------------------------------------
    # Remove duplicate paragraphs
    # -----------------------------------------------------

    final_results = []

    seen = set()

    for result in expanded_results:

        key = (
            result["standard"],
            result["paragraph"]
        )

        if key in seen:
            continue

        seen.add(key)

        final_results.append(
            result
        )

        if len(final_results) >= top_k:
            break

    # -----------------------------------------------------
    # Print debugging information
    # -----------------------------------------------------

    print(
        f"Query: {original_query}"
    )

    if standard:
        print(
            f"Standard filter: {standard}"
        )

    print(
        f"Candidates evaluated: "
        f"{len(candidate_indices)}"
    )

    print("\nTop retrieved results:")

    for number, result in enumerate(
        final_results,
        start=1
    ):

        print(
            f"{number}. "
            f"{result['standard']} "
            f"paragraph "
            f"{result['paragraph']} "
            f"| section: "
            f"{result['section']} "
            f"| score: "
            f"{result['score']:.4f}"
        )

    return final_results


# =========================================================
# CLI
# =========================================================

if __name__ == "__main__":

    question = input(
        "\nEnter your accounting question: "
    ).strip()

    detected_standard = detect_standard(
        question
    )

    if detected_standard:

        print(
            f"Detected standard: "
            f"{detected_standard}"
        )

    else:

        print(
            "No specific IAS/IFRS standard detected."
        )

    results = search(
        question,
        top_k=5,
        standard=detected_standard
    )

    print(
        "\n"
        + "=" * 70
    )

    print("RETRIEVED SOURCES")

    print(
        "=" * 70
    )

    for number, result in enumerate(
        results,
        start=1
    ):

        print(
            f"\n{number}. "
            f"{result['standard']} "
            f"paragraph "
            f"{result['paragraph']}"
        )

        print(
            f"Section: "
            f"{result['section']}"
        )

        print(
            f"Score: "
            f"{result['score']:.4f}"
        )

        print(
            result["text"][:500]
        )