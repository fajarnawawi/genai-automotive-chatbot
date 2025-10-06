import vertexai
from vertexai.generative_models import GenerativeModel

vertexai.init(project="sql-ai-474116", location="us-central1")

models = [
    "gemini-1.5-flash",
    "gemini-1.5-pro", 
    "gemini-2.0-flash",
    "gemini-2.0-flash-lite-001",
    "gemini-pro"
]

for model_name in models:
    try:
        model = GenerativeModel(model_name)
        response = model.generate_content("test")
        print(f"✅ {model_name} - AVAILABLE")
    except Exception as e:
        print(f"❌ {model_name} - {str(e)[:80]}")
