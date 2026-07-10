print("HYBRID AI CHAT AGENT STARTED")
import json
import re
from sqlalchemy import text
from agents.db import SessionLocal
from agents.ingestion import check_data_freshness
from agents.ai_client import call_ai_with_fallback
from pipeline.competitors.embedding_service import create_embedding

def answer_question(question):
    q = question.lower()
    
    # --- 1. Fast Path: Health/Status ---
    if any(x in q for x in ["products tracked", "data fresh", "status", "health"]):
        res = check_data_freshness()
        status_msg = (f"Data Freshness Report: \n"
                      f"- Status: {res.get('status').upper()}\n"
                      f"- Last Updated: {res.get('last_updated', 'unknown')}\n"
                      f"- Total Products: {res.get('products_tracked', 0)}\n"
                      f"Data is synchronized with Amazon and Flipkart scrapers.")
        return status_msg

    # --- 2. RAG Context Retrieval ---
    session = SessionLocal()
    context_data = ""
    try:
        # Embed the question for vector search
        question_emb = create_embedding(question)
        emb_str = "[" + ",".join(str(x) for x in question_emb) + "]"
        
        # Query DB for top 3 matching products using cosine distance
        sql = f"""
            SELECT p.asin, p.brand, p.title, p.is_own_product,
                   (SELECT price FROM price_snapshots ps WHERE ps.asin = p.asin ORDER BY scraped_at DESC LIMIT 1) as latest_price,
                   (SELECT rating FROM rating_snapshots rs WHERE rs.asin = p.asin ORDER BY scraped_at DESC LIMIT 1) as latest_rating
            FROM products p
            WHERE p.embedding IS NOT NULL
            ORDER BY p.embedding <=> '{emb_str}'::vector
            LIMIT 4
        """
        rows = session.execute(text(sql)).fetchall()
        
        context_data = "Retrieved Database Context containing the most relevant products:\n"
        for r in rows:
            own_label = "(User's Own Product)" if r[3] == 1 else "(Competitor Product)"
            context_data += f"- ASIN: {r[0]}, Brand: {r[1]} {own_label}\n  Title: {r[2]}\n  Latest Price: INR {r[4] or 'N/A'}, Rating: {r[5] or 'N/A'} stars\n"
            
        # Also grab a few recent reviews to add sentiment context
        rev_sql = """
            SELECT p.brand, r.rating, r.body 
            FROM reviews r 
            JOIN products p ON r.asin = p.asin 
            ORDER BY r.scraped_at DESC 
            LIMIT 5
        """
        rev_rows = session.execute(text(rev_sql)).fetchall()
        context_data += "\nRecent Customer Reviews context:\n"
        for rr in rev_rows:
            context_data += f"- Brand {rr[0]} (Rating {rr[1]}): {rr[2]}\n"
            
    except Exception as e:
        print(f"[CHAT] RAG Context extraction failed: {e}")
        context_data = "No database context could be retrieved."
    finally:
        session.close()

    # --- 3. Call Together AI for Reasoning ---
    together_system_prompt = (
        "You are Marketlens, an intelligent e-commerce AI assistant for analyzing competitor intelligence. "
        "Use the retrieved database context to accurately answer the user's question. "
        "IMPORTANT RULES:\n"
        "1. DO NOT include ``` blocks or internal reasoning.\n"
        "2. DO NOT use any markdown formatting (no asterisks *, no hashes #, no bold texts).\n"
        "3. Output PLAIN TEXT ONLY. You may use simple dash (-) for lists.\n"
        "4. Be concise and directly answer the question based on the context provided.\n"
        "5. DO NOT show step-by-step reasoning, analysis, or methodology. Provide only the final conclusion."
    )
    
    full_user_prompt = f"Context Data:\n{context_data}\n\nUser Question: {question}"
    
    print("[CHAT] Requesting AI response with fallback...")
    ai_res = call_ai_with_fallback(together_system_prompt, full_user_prompt)
    
    if "error" in ai_res or not ai_res.get("message"):
        return f"Error: AI providers failed -> {ai_res.get('error', 'No message')}"
        
    # Direct return from unified AI client
    raw_msg = ai_res["message"]
    # Scrub residual markdown to be absolutely certain
    clean_msg = raw_msg.replace("*", "").replace("#", "")
    return clean_msg
