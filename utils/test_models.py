import google.generativeai as genai
import os

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

print("🔍 Listing available models...\n")
for model in genai.list_models():
    print(model.name, " | ", model.supported_generation_methods)