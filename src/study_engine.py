import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity


class StudyEngine:

    def __init__(self):
        self.documents = []
        self.embeddings = np.empty((0, 0), dtype=float)
        self.model = SentenceTransformer(
            "all-MiniLM-L6-v2",
            cache_folder="./model_cache",
            local_files_only=True
        )

    def index(self, docs):

        self.documents = docs

        texts = [str(d) for d in docs]

        if not texts:
            self.embeddings = np.empty((0, 0), dtype=float)
            return

        # Force a 2D numpy array so sklearn cosine_similarity always receives valid input.
        self.embeddings = np.atleast_2d(
            np.asarray(self.model.encode(texts, convert_to_numpy=True))
        )

    def search(self, query, top_k=3):

        if len(self.documents) == 0 or self.embeddings.size == 0:
            return []

        query_vec = np.atleast_2d(
            np.asarray(self.model.encode([str(query)], convert_to_numpy=True))
        )

        scores = cosine_similarity(query_vec, self.embeddings)[0]

        top_k = max(1, min(int(top_k), len(scores)))
        idx = np.argsort(scores)[-top_k:][::-1]

        return [self.documents[i] for i in idx]
