from flask import Flask, request, jsonify
import re
from tensorflow.keras.models import load_model
from gensim.utils import simple_preprocess
import pandas as pd
import os
from processer.preprocess import URLProcessor 
from processer.nlp_convert import NLP_Converter
from flask_cors import CORS 

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'  # Suppress TensorFlow logs

# Initialize the Flask app
app = Flask(__name__)

CORS(app)

# Load the pre-trained model
cnn_model = load_model('./model/cnn_binary_classification_model_final.keras')
ltsm_model = load_model('./model/ltsm_binary_classification_model_final.keras')
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

def predict_phishing(url, model):
    # Based on the model, process the URL and return a result
    if model == "cnn":
        # Call the CNN model prediction logic here
        print("CNN")
        result = cnn_predict(url)
    elif model == "ltsm":
        # Call the LSTM model prediction logic here
        print("LTSM")
        result = lstm_predict(url)
    else:
        result = {"error": "Invalid model."}
    
    return result


# Example CNN prediction function
def cnn_predict(url):
    # Logic for CNN prediction
    try:
        # Preprocess the URL to extract features
        url_features = processor.process_url(url)
        if 'error' in url_features:
            return {"error": url_features['error']}

        # Convert the extracted features into a DataFrame for model input
        feature_columns = [
            "use_of_ip", "abnormal_url", "google_index", "count_dot", "count_www", "count_at",
            "count_dir", "count_embed_domian", "short_url", "count_percent", "count_question",
            "count_hyphen", "count_equals", "url_length", "hostname_length", "sus_url",
            "count_digits", "count_letters"
        ]

        features_df = pd.DataFrame([url_features], columns=feature_columns)

        # Process the URL for NLP features
        nlp_feature = nlp_convert.process_url(url)
        
        # Convert the NLP feature dictionary into a DataFrame
        nlp_features_df = pd.DataFrame([nlp_feature])

        # Combine the extracted features and NLP features
        combined_df = pd.concat([features_df, nlp_features_df], axis=1)

        # Make predictions
        predictions = cnn_model.predict(combined_df, verbose=0)
        prediction_score = predictions[0][0]

        # Determine label based on the threshold
        threshold = 0.5
        result = 0 if prediction_score > threshold else 1
        print(f"CNN prediction_score: {prediction_score} - tag: {result} - url: {url} ")

        return {"is_phishing": result, "model": "CNN"}

    except Exception as e:
        return {"error": str(e)}

# Example LSTM prediction function
def lstm_predict(url):
    # Logic for CNN prediction
    try:
        # Preprocess the URL to extract features
        url_features = processor.process_url(url)
        if 'error' in url_features:
            return {"error": url_features['error']}

        # Convert the extracted features into a DataFrame for model input
        feature_columns = [
            "use_of_ip", "abnormal_url", "google_index", "count_dot", "count_www", "count_at",
            "count_dir", "count_embed_domian", "short_url", "count_percent", "count_question",
            "count_hyphen", "count_equals", "url_length", "hostname_length", "sus_url",
            "count_digits", "count_letters"
        ]

        features_df = pd.DataFrame([url_features], columns=feature_columns)

        # Process the URL for NLP features
        nlp_feature = nlp_convert.process_url(url)
        
        # Convert the NLP feature dictionary into a DataFrame
        nlp_features_df = pd.DataFrame([nlp_feature])

        # Combine the extracted features and NLP features
        combined_df = pd.concat([features_df, nlp_features_df], axis=1)

        # Make predictions
        predictions = ltsm_model.predict(combined_df, verbose=0)
        prediction_score = predictions[0][0]

        # Determine label based on the threshold
        threshold = 0.5
        result = 0 if prediction_score > threshold else 1
        print(f"LTSM prediction_score: {prediction_score} - tag: {result} - url: {url} ")

        return {"is_phishing": result, "model": "LTSM"}

    except Exception as e:
        return {"error": str(e)}



# Define the prediction endpoint
@app.route('/predict', methods=['POST'])
def predict():
    # Parse the incoming JSON request
    data = request.get_json()
    
    # Validate input data
    if not data or 'url' not in data or 'model' not in data:
        return jsonify({"error": "Invalid input. Please provide a URL and model."}), 400

    url = data['url']
    model = data['model']
    print(url, model)
    # Perform the prediction based on the selected model
    result = predict_phishing(url, model)
    
    # Return the result as a JSON response
    return jsonify(result)

# Run the API
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)