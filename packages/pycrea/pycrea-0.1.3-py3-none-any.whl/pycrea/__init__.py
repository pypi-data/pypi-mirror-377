import os 
import json
from .crea import CREA

# Automatically load JSON file if needed
PACKAGE_DIR = os.path.dirname(__file__)
JSON_FILE = os.path.join(PACKAGE_DIR, "data", "data.json")

if os.path.exists(JSON_FILE):
    with open(JSON_FILE, "r") as f:
        word_vectors = json.load(f)  # Load JSON data
else:
    word_vectors = {}  # Fallback to empty dict if file is missing

# Initialize CREA with preloaded word vectors or fallback to URL
crea_instance = CREA(word_vectors if word_vectors else None)

# Expose functions for easier use
get_vector = crea_instance.get_vector
get_all_vectors = crea_instance.get_all_vectors
get_vectors = crea_instance.get_vectors
top_n_similar = crea_instance.top_n_similar

# Define what gets imported when using `from crea import *`
__all__ = ["CREA", "get_vector", "get_all_vectors", "get_vectors", "top_n_similar"]
