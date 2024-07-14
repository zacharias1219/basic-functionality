import requests

# Define the base URL for the Ollama API
OLLAMA_API_BASE_URL = "https://api.ollama.com/v1"

# Function to generate a response from the Ollama model
def generate_response(model, prompt, context):
    """
    Generates a response from the specified Ollama model.

    :param model: The model to use (e.g., 'llama3', 'mistral', 'gemma7b', 'starling').
    :param prompt: The user query or prompt.
    :param context: The context to use for generating the response.
    :return: The generated response.
    """
    # Construct the API endpoint
    url = f"{OLLAMA_API_BASE_URL}/generate"
    
    # Construct the payload for the API request
    payload = {
        "model": model,
        "prompt": prompt,
        "context": context
    }
    
    # Make the API request
    response = requests.post(url, json=payload)
    
    # Raise an exception if the request was not successful
    response.raise_for_status()
    
    # Parse the response JSON and return the generated text
    return response.json().get("text", "")
