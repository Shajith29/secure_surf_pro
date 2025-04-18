from flask import Flask, request, jsonify
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import requests
import torch
from dotenv import load_dotenv
import os

app = Flask(__name__)

# Load SecureBERT model for phishing detection
securebert_model_name = "AventIQ-AI/Securebert-website-phishing-prediction"
tokenizer = AutoTokenizer.from_pretrained(securebert_model_name)
model = AutoModelForSequenceClassification.from_pretrained(securebert_model_name)

# Function to classify URL
def check_url(url):
    inputs = tokenizer(url, return_tensors="pt", truncation=True, padding=True)
    with torch.no_grad():
        outputs = model(**inputs)
        logits = outputs.logits
        prediction = torch.argmax(logits, dim=1).item()
    return "phishing" if prediction == 1 else "safe"

import requests

import requests

def get_gemini_explanation(url):
    load_dotenv()
    # Gemini API key and endpoint
    gemini_api_key = os.getenv("GEMINI_API_KEY")  # Ensure this is correct
    endpoint = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={gemini_api_key}"

    # Prepare the payload
    payload = {
        "contents": [{
            "parts": [{
                "text": f"Explain why {url} is considered a phishing URL"
            }]
        }]
    }

    # Send the request to Gemini
    response = requests.post(endpoint, json=payload)

    # Check the response
    if response.status_code == 200:
        response_data = response.json()
        # Extract the explanation text from the response
        gemini_explanation = response_data['candidates'][0]['content']['parts'][0]['text']
    else:
        # If error, print status code and response text for debugging
        print(f"Error: {response.status_code}")
        print(f"Response: {response.text}")
        gemini_explanation = "No explanation available due to an error"

    return gemini_explanation



# Function to generate a human-readable explanation
def generate_explanation(url, classification):
    explanation_parts = []

    # Suspicious Keywords
    suspicious_keywords = ["login", "verify", "account", "secure", "update"]
    if any(keyword in url.lower() for keyword in suspicious_keywords):
        explanation_parts.append("The URL contains suspicious keywords like 'login', 'verify', 'account', and 'update'. These are often used in phishing attempts to make users think they are on a legitimate site.")

    # Too many subdomains
    try:
        domain = url.split("//")[-1].split("/")[0]
        subdomains = domain.split(".")
        if len(subdomains) >= 4:
            explanation_parts.append("The URL contains an unusually high number of subdomains, which is commonly seen in phishing websites.")
    except:
        explanation_parts.append("The URL structure is suspicious and might be hiding the true destination.")

    # Misleading domain name (Impersonation)
    trusted_brands = ["paypal", "google", "apple", "facebook", "microsoft"]
    if any(brand in url.lower() for brand in trusted_brands):
        explanation_parts.append(f"The URL attempts to impersonate a trusted brand like 'PayPal' or 'Google' in order to deceive users.")

    # Suspicious TLD (Top Level Domain)
    suspicious_tlds = [".ru", ".cc", ".tk", ".ml", ".gq"]
    if any(url.lower().endswith(tld) for tld in suspicious_tlds):
        explanation_parts.append(f"The URL ends with a suspicious top-level domain (TLD), such as {', '.join(suspicious_tlds)}. Phishing websites often use unusual TLDs to appear legitimate.")

    # Lack of HTTPS
    if "https://" not in url:
        explanation_parts.append("The URL does not use HTTPS, making it less secure. Legitimate websites use HTTPS to ensure secure communication.")

    # Generate final explanation for classification
    if classification == "phishing":
        final_explanation = "This URL is classified as phishing because it contains elements commonly found in phishing websites designed to deceive users into revealing sensitive information."
    else:
        final_explanation = "This URL appears safe based on common phishing indicators, although other methods may still be necessary to fully verify its authenticity."

    explanation = "\n".join(explanation_parts)
    return f"{final_explanation}\n\nExplanation:\n{explanation}"

@app.route('/predict', methods=['POST'])
def predict():
    data = request.get_json()
    url = data.get("url")

    if not url:
        return jsonify({"error": "URL not provided"}), 400

    # Classify the URL
    label = check_url(url)
    
    # Generate human-readable explanation
    explanation = generate_explanation(url, label)
    
    # Get Gemini explanation (wait until it's available)
    gemini_explanation = get_gemini_explanation(url)

    return jsonify({
        "result": label,
        "explanation": explanation,
        "gemini_explanation": gemini_explanation
    })

if __name__ == '__main__':
    app.run(debug=True)
