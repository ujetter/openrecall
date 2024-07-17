from sentence_transformers import SentenceTransformer
import numpy as np
import logging
from openrecall.utils import timeit_decorator
logger = logging.getLogger(__name__)
logger.debug(f"initializing {__name__}")


@timeit_decorator
def get_embedding(text):
    model = SentenceTransformer("all-MiniLM-L6-v2")
    sentences = text.split("\n")
    sentence_embeddings = model.encode(sentences)
    mean = np.mean(sentence_embeddings, axis=0)
    mean = mean.astype(np.float64)
    return mean


@timeit_decorator
def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
