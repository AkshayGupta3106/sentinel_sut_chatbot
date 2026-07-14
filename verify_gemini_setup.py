"""
Standalone sanity check for a real GEMINI_API_KEY -- run this BEFORE
booting the full Streamlit app, so a bad/missing key shows up as one
clear error instead of a vague fallback string buried in a chat reply.

Run:
    export GEMINI_API_KEY=your_real_key_here
    python verify_gemini_setup.py
"""

import os
import sys
from dotenv import load_dotenv

# Ensure we load environment variables from the .env file
load_dotenv()

# Prevent Windows console encoding issues when printing emojis
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


def main():
    key = os.getenv("GEMINI_API_KEY")
    if not key:
        print("❌ GEMINI_API_KEY is not set in the environment or .env file.")
        print("   Please add GEMINI_API_KEY=your_key_here to your .env file.")
        print("   (Get a Gemini key at https://aistudio.google.com/apikey)")
        sys.exit(1)

    print(f"✓ GEMINI_API_KEY is set ({key[:6]}...{key[-4:]})")

    groq_key = os.getenv("GROQ_API_KEY")
    if groq_key:
        print(f"✓ GROQ_API_KEY is set ({groq_key[:6]}...{groq_key[-4:]})")
    else:
        print("ℹ GROQ_API_KEY is not set (optional)")

    # --- Step 1: plain generation call ---
    print("\n[1/2] Testing plain generation (rag/generator.py)...")
    from rag.generator import generate_answer
    answer = generate_answer("Reply with exactly the word: PONG")
    if answer.startswith("[FALLBACK") or "PONG" not in answer.upper():
        print(f"❌ Unexpected response: {answer[:200]}")
        sys.exit(1)
    print(f"✓ Got a real response: {answer.strip()[:100]}")

    # --- Step 2: LLM-judge structured JSON call ---
    print("\n[2/2] Testing LLM-as-judge (sentinel/evaluation/llm_judge.py)...")
    from sentinel.evaluation.llm_judge import judge_faithfulness, USE_GROQ, JUDGE_MODEL
    if USE_GROQ:
        print(f"  (Using Groq provider with model: {JUDGE_MODEL})")
    else:
        print(f"  (Using Gemini provider with model: {JUDGE_MODEL})")

    result = judge_faithfulness(
        context="The sky appears blue due to Rayleigh scattering of sunlight in the atmosphere.",
        answer="The sky is blue because of Rayleigh scattering.",
    )
    if result["skipped"] or result["score"] is None:
        print(f"❌ Judge call failed or was skipped: {result['reasoning']}")
        sys.exit(1)
    print(f"✓ Judge returned a real structured score: {result['score']} — {result['reasoning']}")

    print("\n✅ All checks passed. Real Gemini calls are working end to end.")
    print("   You can now run: streamlit run streamlit_app.py")


if __name__ == "__main__":
    main()
