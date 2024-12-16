import re
import os
from gensim.models import Word2Vec
from sklearn.preprocessing import normalize
from gensim.utils import simple_preprocess

class NLP_Converter:
    def __init__(self, vector_size, window, min_count, workers, sentences):
        # Define the model save path
        model_save_path = './model/word2vec_model.model'
        model_dir = os.path.dirname(model_save_path)
        
        try:
            self.model = Word2Vec.load('./model/word2vec_model.model')
        except:
            # # Initialize the Word2Vec model
            # self.model = Word2Vec(
            #     sentences=sentences,
            #     vector_size=vector_size,
            #     window=window,
            #     min_count=min_count,
            #     workers=workers
            # )
            # Save the model to a file
            # self.model.save(model_save_path)
            # print(f"Model saved to {model_save_path}")
            pass

        vocab = set(self.model.wv.index_to_key)
        print(len(vocab))

    def url_to_vector(self,tokens):
        # Get vectors for each token in the URL
        vectors = [self.model.wv[word] for word in tokens if word in self.model.wv]
        # Average the vectors to get a single vector representation for the URL
        if vectors:
            return sum(vectors) / len(vectors)
        else:
            # Return a zero vector if no tokens exist in the Word2Vec vocabulary
            return [0] * self.model.vector_size

    def process_url(self, url):
        """Process a single URL and extract its NLP features."""
        # Tokenize using the same logic as training
        tokens = simple_preprocess(url)
        print("Tokens in process_url:", tokens)  # Debug

        # Generate vector
        vector = self.url_to_vector(tokens)

        if not any(vector):
            print("Warning: All-zero vector returned for URL")

        # Normalize vector
        # normalized_vector = normalize([vector])[0]

        # return {f'vector_{i+1}': value for i, value in enumerate(normalized_vector)}
        return {f'vector_{i+1}': value for i, value in enumerate(vector)}