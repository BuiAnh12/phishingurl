import re
from tensorflow.keras.models import load_model
from gensim.utils import simple_preprocess
import pandas as pd
import sys
import os
from processer.preprocess import URLProcessor 
from processer.nlp_convert import NLP_Converter
import pandas as pd
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'  # Suppress TensorFlow logs

# Load the model
loaded_model = load_model('./model/cnn_binary_classification_model_final.keras')

# Initialize the URLProcessor
print("Load the df")
input_csv = './dataset/v1/base_url.csv'

df = pd.read_csv(input_csv)
df['preprocess_url'] = df['url'].apply(simple_preprocess)
print("Load the classes")

processor = URLProcessor()
nlp_convert = NLP_Converter(300,5,1,4,df['preprocess_url'])
def predict_phishing(url):
    # Logic for CNN prediction
    try:
        # Preprocess the URL to extract features
        url_features = processor.process_url(url)
        if 'error' in url_features:
            return {"error": url_features['error']}

        # Convert the extracted features into a DataFrame for model input
        feature_columns = [
            'use_of_ip','abnormal_url','google_index', 'count.', 'count-www', 
            'count@', 'count_dir', 'count_embed_domian', 'short_url', 'count%', 
            'count?', 'count-', 'count=', 'url_length', 'hostname_length', 'sus_url', 
            'count-digits', 'count-letters'
        ]

        features_df = pd.DataFrame([url_features], columns=feature_columns)

        # Process the URL for NLP features
        nlp_feature = nlp_convert.process_url(url)
        
        # Convert the NLP feature dictionary into a DataFrame
        nlp_features_df = pd.DataFrame([nlp_feature])
        print(nlp_features_df)
        # Combine the extracted features and NLP features
        combined_df = pd.concat([features_df, nlp_features_df], axis=1)

        # Make predictions
        predictions = loaded_model.predict(combined_df, verbose=0)
        prediction_score = predictions[0][0]

        # Determine label based on the threshold
        threshold = 0.5
        result = 1 if prediction_score > threshold else 0
        print(f"prediction_score: {prediction_score} - tag: {result} - url: {url} ")

        return result

    except Exception as e:
        return {"error": str(e)}


# if __name__ == "__main__":
#     # Read the URL from command-line arguments
#     if len(sys.argv) > 1:
#         url = sys.argv[1]
#         result = predict_phishing(url)  # Make prediction
#         print(result.strip())  # Print the result
#     else:
#         print("Invalid URL")




def test_model(input_csv):
    """
    Test the phishing detection model using a dataset.

    Args:
        input_csv (str): Path to the CSV file containing 'url' and 'label' columns.

    Returns:
        None
    """
    # Load the dataset
    print("Loading test dataset...")
    df = pd.read_csv(input_csv)
    df = df.head(1000)
    # Ensure the DataFrame contains the required columns
    if 'url' not in df.columns or 'label' not in df.columns:
        raise ValueError("The input CSV must contain 'url' and 'label' columns.")

    # Initialize lists to store results
    true_labels = []
    predicted_labels = []

    print("Starting model predictions...")
    for index, row in df.iterrows():
        url = row['url']
        true_label = row['label']
        
        try:
            # Make a prediction
            prediction = predict_phishing(url)

            # Append the true and predicted labels
            true_labels.append(true_label)
            predicted_labels.append(prediction)
        except Exception as e:
            print(f"Error processing URL at index {index}: {e}")
            continue

    # Evaluate the model
    print("Evaluating model performance...")
    accuracy = accuracy_score(true_labels, predicted_labels)
    print(f"Accuracy: {accuracy * 100:.2f}%\n")

    print("Confusion Matrix:")
    print(confusion_matrix(true_labels, predicted_labels))

    print("\nClassification Report:")
    print(classification_report(true_labels, predicted_labels, target_names=["Not Phishing", "Phishing"]))

if __name__ == "__main__":
    # Path to the test dataset
    test_csv_path = './dataset/v1/eval_df.csv'  # Update with your test file path

    # Call the testing function
    test_model(test_csv_path)
    # prediction = predict_phishing("https://www.google.com")
