import requests
import json

def test_ollama_connection():
    """Test if Ollama is running and accessible."""
    try:
        # Test if Ollama is running
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        
        if response.status_code == 200:
            models = response.json()
            print("Ollama is running!")
            print("Available models:")
            for model in models.get('models', []):
                print(f"  - {model.get('name', 'Unknown')}")
            
            # Test if mistral is available
            model_names = [model.get('name', '') for model in models.get('models', [])]
            if any('mistral' in name.lower() for name in model_names):
                print("Mistral model is available!")
            else:
                print("Mistral model not found. You may need to pull it:")
                print("   Run: ollama pull mistral")
            
            return True
        else:
            print(f"Ollama responded with status code: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("Cannot connect to Ollama. Make sure it's running on localhost:11434")
        print("   Start Ollama and try again.")
        return False
    except Exception as e:
        print(f"Error testing Ollama: {e}")
        return False

def test_mistral_generation():
    """Test a simple generation with Mistral."""
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "mistral",
                "prompt": "Generate a simple course title for a mathematics class:",
                "stream": False
            },
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            generated_text = result.get('response', '')
            print(f"Test generation successful: {generated_text.strip()}")
            return True
        else:
            print(f"Generation failed with status: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"Error testing generation: {e}")
        return False

if __name__ == "__main__":
    print("Testing Ollama connection...")
    
    if test_ollama_connection():
        print("\nTesting Mistral generation...")
        test_mistral_generation()
    
    print("\nIf Ollama is not running, start it with: ollama serve")
    print("If Mistral is not available, install it with: ollama pull mistral")
