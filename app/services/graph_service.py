import networkx as nx
import pickle
import os
import re
from pypdf import PdfReader

class KnowledgeGraphService:
    def __init__(self, data_path="data/processed/graph.pkl"):
        self.data_path = data_path
        self.graph = nx.DiGraph()
        self.full_text = "" 
        
        os.makedirs(os.path.dirname(self.data_path), exist_ok=True)
        if os.path.exists(self.data_path):
            with open(self.data_path, "rb") as f: self.graph = pickle.load(f)

    def build_graph(self, pdf_path):
        print("⚙️  Starting Ingestion (Debug Mode)...")
        if not os.path.exists(pdf_path): return "Error: PDF not found."

        reader = PdfReader(pdf_path)
        total_pages = len(reader.pages)
        print(f"📄 PDF Detected: {total_pages} pages.")
        
        raw_text_list = []
        for i, page in enumerate(reader.pages):
            text = page.extract_text()
            if text:
                # Clean up header/footer noise (optional, but helps)
                cleaned = text.replace('\n', ' ').strip()
                if len(cleaned) > 50: # Ignore empty/tiny pages
                    raw_text_list.append(cleaned)
                else:
                    print(f"   ⚠️ Page {i+1} skipped (Too little text).")
            else:
                print(f"   ❌ Page {i+1} skipped (No text found / Image).")

        self.full_text = " ".join(raw_text_list)
        print(f"✅ Total Extracted Characters: {len(self.full_text)}")
        
        # STOP if text is too short (Major PDF Issue)
        if len(self.full_text) < 10000:
            print("🚨 CRITICAL WARNING: Extracted text is suspicious (< 10k chars). The PDF might be images.")

        # --- GRAPH BUILDING (Standard) ---
        pattern = r"((?:Faculty|Department|Institute|Center|School)\s+of\s+[A-Za-z\s&]+?)(?=\s(?:Faculty|Department|Institute|Center|School|\d+\.))"
        matches = list(re.finditer(pattern, self.full_text, re.IGNORECASE))
        
        for m in matches:
            node_name = re.sub(r"^\d+\.\s*", "", m.group(1).strip())
            if len(node_name) < 100:
                self.graph.add_node(node_name, type="Department")
                start = m.end()
                content = self.full_text[start : start + 1500]
                leaders = re.findall(r"(Dean|Chairman|Director|Head)\s*(?:[:\-])?\s*((?:Prof|Dr|Engr|Mr|Ms)\.?\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)", content)
                for role, name in leaders:
                    self.graph.add_edge(node_name, name.strip(), relation=f"HAS_{role.upper()}")

        with open(self.data_path, "wb") as f: pickle.dump(self.graph, f)
        return f"Graph: {self.graph.number_of_nodes()} nodes."

    def get_context(self, query):
        context = []
        query_lower = query.lower()
        for node in self.graph.nodes:
            if node.lower() in query_lower:
                context.append(f"Entity: {node}")
                for n in self.graph.neighbors(node):
                    rel = self.graph[node][n].get('relation', 'related')
                    context.append(f" - {rel}: {n}")
        return "\n".join(context)