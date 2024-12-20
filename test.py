import re
import tensorflow as tf
from tensorflow.keras.models import load_model
from gensim.utils import simple_preprocess
import pandas as pd
import sys
import os
from processer.preprocess import URLProcessor 
from processer.nlp_convert import NLP_Converter
import pandas as pd
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report, f1_score
from sklearn.preprocessing import StandardScaler
import numpy as np
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'  # Suppress TensorFlow logs

# Load the model
detect_model = load_model('./model/ltsm_binary_classification_model_v2.keras')

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
        # Combine the extracted features and NLP features
        combined_df = pd.concat([features_df, nlp_features_df], axis=1)

        # # Step 4: Optional - Normalize the data using StandardScaler (recommended if feature ranges vary)
        # scaler = StandardScaler()
        # scaled_data = scaler.fit_transform(combined_df)

        # # Step 5: Convert to NumPy arrays (if necessary for Keras model)
        # # If your data is already a NumPy array, this step can be skipped
        # # final_data = scaled_data.astype('float32')

        # final_processed_df = pd.DataFrame(final_data, columns=combined_df.columns)
        # combined_df.to_csv("./google.csv")
        # Make predictions
        predictions = detect_model.predict(combined_df, verbose=0)

        y_pred_classes = (predictions < 0.5).astype(int)
        # print(f"prediction_score: {prediction_score} - tag: {result} - url: {url} ")

        return y_pred_classes[0][0]

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


def test_model_x_y(x_csv, y_csv):
    
    x_test = pd.read_csv(x_csv)
    y_test = pd.read_csv(y_csv)

    # Step 4: Normalize the data using StandardScaler
    scaler = StandardScaler()

    # Fit the scaler on the test data and transform it
    x_test_scaled = scaler.fit_transform(x_test)  # Use 'fit_transform' instead of 'transform'

    # Step 5: Convert to NumPy arrays
    x_test = x_test_scaled.astype('float32')


    # Evaluate the model
    test_loss, test_accuracy, test_precision = detect_model.evaluate(x_test, y_test, verbose=1)
    print(f"Test Precision: {test_precision}")
    print(f"Test Loss: {test_loss}")
    print(f"Test Accuracy: {test_accuracy}")

    # Make predictions
    y_pred = detect_model.predict(x_test)
    y_pred_classes = (y_pred > 0.5).astype(int).flatten()  # Threshold at 0.5

    # Convert y_test to NumPy array and flatten
    y_true_classes = y_test.to_numpy().flatten()

    # Confusion Matrix
    conf_matrix = confusion_matrix(y_true_classes, y_pred_classes)
    print("Confusion Matrix:")
    print(conf_matrix)

    # F1 Score
    f1 = f1_score(y_true_classes, y_pred_classes)
    print(f"F1 Score: {f1}")

    # Classification Report
    class_report = classification_report(y_true_classes, y_pred_classes)
    print("Classification Report:")
    print(class_report)

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
    df = pd.read_csv(input_csv).head(10000)
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


import pandas as pd
from sklearn.preprocessing import StandardScaler

# Assume processor, nlp_convert, and detect_model are already defined

def feature_extraction(url):
    """
    Predict whether URLs in a DataFrame are phishing or not and return the final processed data.

    Args:
        url_df (pd.DataFrame): DataFrame containing a column 'url' with URLs to process.

    Returns:
        pd.DataFrame: DataFrame containing the final processed features for all URLs in the input DataFrame.
    """
    try:
        # Initialize lists to store features and errors
        extracted_features_list = []
        nlp_features_list = []

        # Preprocess the URL to extract features
        url_features = processor.process_url(url)
        # Extract NLP features
        nlp_feature = nlp_convert.process_url(url)        # Append features for processing
        extracted_features_list.append(url_features)
        nlp_features_list.append(nlp_feature)

        # Convert extracted features and NLP features to DataFrames
        feature_columns = [
            'use_of_ip', 'abnormal_url', 'google_index', 'count.', 'count-www',
            'count@', 'count_dir', 'count_embed_domian', 'short_url', 'count%',
            'count?', 'count-', 'count=', 'url_length', 'hostname_length', 'sus_url',
            'count-digits', 'count-letters'
        ]

        features_df = pd.DataFrame(extracted_features_list, columns=feature_columns)
        nlp_features_df = pd.DataFrame(nlp_features_list)

        # Combine the extracted features and NLP features
        combined_df = pd.concat([features_df, nlp_features_df], axis=1)
        print(combined_df)


        # Return the final processed DataFrame
        final_processed_df = pd.DataFrame(final_data, columns=combined_df.columns)
        final_processed_df['url'] = url

        return final_processed_df

    except Exception as e:
        return pd.DataFrame({'error': [str(e)]})



if __name__ == "__main__":
    # Path to the test dataset
    test_csv_path = './dataset/v1/eval_df.csv'  # Update with your test file path

    # # Call the testing function
    test_model(test_csv_path)
    # prediction = feature_extraction("https://www.google.com")
    # print(prediction)

    # test_model_x_y(x_csv="./x_test.csv", y_csv="./y_test.csv")
    # print(tf.__version__)
