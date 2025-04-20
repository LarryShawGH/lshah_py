import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    raise Exception("GEMINI_API_KEY not set in .env")

# Configure the API key
genai.configure(api_key=api_key)

#  List available models
print("Available Models:")
models = genai.list_models()
#for m in models:
    #print(f"- {m.name}")

#  Try generating a simple response
model = genai.GenerativeModel("models/gemini-1.5-flash")

user_prompt = input("How can I help you? ")

response = model.generate_content(user_prompt)
print("\n Gemini Response:")
print(response.text)