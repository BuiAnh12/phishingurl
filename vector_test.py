from flask import Flask, request, jsonify
import re
from tensorflow.keras.models import load_model
from gensim.utils import simple_preprocess
import pandas as pd
import os
from processer.preprocess import URLProcessor 
from processer.nlp_convert import NLP_Converter
from flask_cors import CORS 


loaded_model = load_model('./model/cnn_binary_classification_model.keras')


# Initialize auxiliary components
def init_processors():
    print("Loading the dataset and initializing processors...")
    input_csv = './dataset/v1/base_url.csv'
    df = pd.read_csv(input_csv)
    df['preprocess_url'] = df['url'].apply(simple_preprocess)
    
    processor = URLProcessor()
    nlp_convert = NLP_Converter(300, 5, 1, 4, df['preprocess_url'])
    
    return processor, nlp_convert

processor, nlp_convert = init_processors()


url = "https://www.google.com"


vector1 = nlp_convert.process_url(url)
print(vector1)
# # Compare if the two vectors are the same
# if (vector1 == vector2):
#     print("The vectors are the same!")
# else:
#     print("The vectors are different!")



