print("⏳ script started... Import is working.") # <--- NEW LINE

from app.services.vector_service import VectorService

print("⏳ Initializing Vector Engine (this takes a few seconds)...") # <--- NEW LINE
vs = VectorService()


# Update the query line
query = "I want to apply for M.Sc. Artificial Intelligence. Should I select the Department of Computer Science?"

print(f"\n🔎 Inspecting Vector Search for: '{query}'")
print("-" * 50)

# Get the raw results (top 10)
results = vs.search(query, top_k=10)

print(results)
print("-" * 50)