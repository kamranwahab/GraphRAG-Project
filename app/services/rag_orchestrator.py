import re
from openai import OpenAI
from app.services.graph_service import KnowledgeGraphService
from app.services.vector_service import VectorService

class RAGOrchestrator:
    def __init__(self):
        self.kg = KnowledgeGraphService()
        self.vs = VectorService()

    def ingest(self, pdf_path):
        graph_status = self.kg.build_graph(pdf_path)
        raw_text = self.kg.full_text
        if raw_text: 
            self.vs.ingest_text(raw_text)
        return f"{graph_status} | Vectors Built."

    def extract_search_intent(self, user_query):
        """
        Smartly extracts the core 'Topic' or 'Degree'.
        1. Looks for formal degrees (M.Sc. X)
        2. Looks for topics (Safety programs, Mining degree)
        """
        # Strategy A: Formal Degree
        match = re.search(r"(M\.Sc\.|B\.Sc\.|Ph\.D\.|MS|Bachelors?|Masters?)\s+([A-Za-z\s&]+)", user_query, re.IGNORECASE)
        if match:
            raw = match.group(0).strip()
            # Clean stop words
            words = raw.split()
            clean = []
            stop_words = ["should", "can", "does", "is", "department", "in", "at", "select", "offered"]
            for w in words:
                if re.sub(r'[^\w\s]', '', w).lower() in stop_words: break
                clean.append(w)
            return " ".join(clean)

        # Strategy B: Topic Search (e.g. "Safety related programs")
        # specific keywords + "program"/"degree"
        topic_match = re.search(r"(\w+)\s+(related\s+)?(program|degree|master)", user_query, re.IGNORECASE)
        if topic_match:
            # Returns "Safety" from "Safety related programs"
            return topic_match.group(1)

        return None

    def clean_noise(self, user_query):
        """
        Removes conversational filler ("I live near UET", "Can I apply").
        """
        stop_words = [
            "i", "live", "near", "uet", "campus", "want", "to", "apply", "have", "a", "degree", "in",
            "can", "does", "do", "is", "are", "should", "please", "tell", "me", "the", "of", "for"
        ]
        words = user_query.split()
        keywords = [w for w in words if re.sub(r'[^\w\s]', '', w).lower() not in stop_words]
        return " ".join(keywords)

    def query(self, user_query, api_url):
        # 1. Guardrails
        forbidden = ["fee", "tuition", "hostel", "transport", "cost", "bus", "dues"]
        if any(w in user_query.lower() for w in forbidden):
            return "I only answer department/academic information."

        # 2. Retrieval Strategy
        topic = self.extract_search_intent(user_query)
        
        if topic:
            # Targeted Search
            search_query = f"{topic} Offered Programs Eligibility"
            print(f"🎯 Targeted Search: '{search_query}'")
        else:
            # Clean Broad Search
            cleaned = self.clean_noise(user_query)
            search_query = f"{cleaned} Offered Programs"
            print(f"🔍 Broad Search: '{search_query}'")
        
        # Fetch 50 chunks
        context_vector_string = self.vs.search(search_query, top_k=50)
        chunks = context_vector_string.split("\n\n") if context_vector_string else []

        # 3. Smart Filtering
        # If we have a specific topic (e.g. "Safety", "Polymer"), filter for it.
        if topic and chunks:
            print(f"🧹 Filtering for topic: '{topic}'")
            filtered_chunks = [c for c in chunks if topic.lower() in c.lower()]
            context_vector = "\n\n".join(filtered_chunks) if filtered_chunks else context_vector_string
        else:
            context_vector = context_vector_string

        # 4. Context Assembly
        context_graph = self.kg.get_context(user_query)
        full_context = f"""
        --- OFFICIAL DATA ---
        {context_vector}
        """
        if len(full_context) > 20000: full_context = full_context[:20000]

        # 5. Generation
        client = OpenAI(base_url=api_url, api_key="EMPTY")
        
        # CHAIN OF THOUGHT PROMPT
        prompt = f"""
        You are a logical academic assistant. Answer using ONLY the text provided.

        Context:
        {full_context}

        Question: {user_query}

        INSTRUCTIONS (Step-by-Step Thinking):
        
        1. **IF checking Eligibility:**
           - Step A: Find the list of eligible degrees in the text.
           - Step B: Check if the user's degree (e.g., Physics) is IN that list.
           - Step C: If it is in the list, answer YES. If not, answer NO.
           - *Warning:* Do not hallucinate a "No" if the word is clearly in the list.

        2. **IF checking Offered Programs:**
           - Step A: Locate the "Offered Programs" header under the requested Department.
           - Step B: Scan for the specific keyword (e.g., "Safety").
           - Step C: If found, state the exact program name.

        Answer:
        """
        
        try:
            response = client.chat.completions.create(
                model="Qwen/Qwen2.5-3B-Instruct",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=600,
                temperature=0.1
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error: {e}"