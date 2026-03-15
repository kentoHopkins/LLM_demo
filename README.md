# LLM Demo — Setup & Run Guide
**MCP Demo | RAG Demo | Hackathon Edition — March 2026**

---

## Folder Structure
```
LLM_demo/
  MCP_demo/
    client.py
    server.py
  RAG_demo/
    documents/
      company.txt
      product.txt
      faq.pdf
    loader.py
    retriever.py
    main.py
  .env
```

---

## Environment Setup

### 1. Create your .env file
Place this inside `LLM_demo/` (not in any subfolder):
```
OPENAI_API_KEY=your_openai_key_here
```
Get your key at: https://platform.openai.com/api-keys

### 2. Install all dependencies
```bash
pip install fastmcp openai chromadb pdfplumber python-dotenv
```

---

## MCP Demo

### What it does
Demonstrates how an LLM can call custom tools via the Model Context Protocol (MCP). The server exposes 5 math and text tools. OpenAI automatically decides which tools to call based on your message.

**Tools available:**
- `add(a, b)` — adds two numbers
- `multiply(a, b)` — multiplies two numbers
- `power(base, exponent)` — raises base to a power
- `reverse_text(text)` — reverses a string
- `word_count(text)` — counts words in a string

### How to run
```bash
cd LLM_demo/MCP_demo
python client.py
```
Type `quit` or `exit` to stop.

### Demo Chat Script

**Exchange 1 — Simple greeting (no tools called)**
> **You:** Hi, what can you help me with?
> 
> **AI:** Hi! I have access to tools that can add and multiply numbers, raise numbers to a power, reverse text, and count words. Feel free to ask me anything involving these!

**Exchange 2 — Single tool call**
> **You:** What is 2 to the power of 10?
> 
> **AI:** [calling tool: power({'base': 2.0, 'exponent': 10})]
> 
> 2 to the power of 10 is 1024.

**Exchange 3 — Multiple tool calls chained**
> **You:** Calculate 6 to the power of 5, then multiply that result by 3.
> 
> **AI:** [calling tool: power({'base': 6.0, 'exponent': 5})]
> [calling tool: multiply({'a': 7776.0, 'b': 3.0})]
> 
> 6 to the power of 5 is 7776. Multiplied by 3, the result is 23328.

**Exchange 4 — Text tool**
> **You:** How many words are in the phrase 'artificial intelligence is changing the world'?
> 
> **AI:** [calling tool: word_count({'text': 'artificial intelligence is changing the world'})]
> 
> The phrase contains 6 words.

**Exchange 5 — Closing**
> **You:** quit

---

## RAG Demo

### What it does
Demonstrates Retrieval-Augmented Generation (RAG). The system loads company and product documents, embeds them using OpenAI, stores them in a ChromaDB vector database, and retrieves the most relevant chunks to answer questions. The LLM cannot answer these questions without the documents.

**Documents included:**
- `company.txt` — NovaMind AI company overview, team, values
- `product.txt` — FlowMind product specs and pricing
- `faq.pdf` — Frequently asked questions about FlowMind

### How to run
```bash
cd LLM_demo/RAG_demo
python main.py
```
The first run takes a few extra seconds to build the vector store. Type `quit` or `exit` to stop.

### Demo Chat Script

**Exchange 1 — Company info**
> **You:** Who is the CEO of NovaMind AI and what is her background?
> 
> **AI:** [retrieved 3 chunks: company.txt]
> 
> The CEO of NovaMind AI is Dr. Priya Anand. She is a former ML researcher at Stanford and previously served as VP of Product at DataRobot.

**Exchange 2 — Pricing question**
> **You:** How much does the Growth plan cost and what does it include?
> 
> **AI:** [retrieved 3 chunks: product.txt]
> 
> The Growth Plan costs $99 per month. It includes up to 25 active workflows, 50,000 workflow runs per month, priority support, and an onboarding call.

**Exchange 3 — FAQ question (from PDF)**
> **You:** What happens if I go over my monthly workflow run limit?
> 
> **AI:** [retrieved 3 chunks: faq.pdf]
> 
> On the Starter and Growth plans, your workflows will pause until the next billing cycle. You will receive an email warning at 80% and again at 100% of your limit. You can upgrade your plan at any time to restore access immediately.

**Exchange 4 — Follow-up (tests conversation memory)**
> **You:** Does that plan also support Claude AI models?
> 
> **AI:** [retrieved 3 chunks: product.txt]
> 
> Yes. FlowMind's AI Step block supports GPT-4o, GPT-4o-mini, Claude 3.5 Sonnet, and Gemini 1.5 Flash. You can use your own API key or NovaMind AI's shared key.

**Exchange 5 — Out-of-scope question (shows honesty)**
> **You:** What is the capital of France?
> 
> **AI:** I don't have information about that in the provided documents. I can only answer questions based on the NovaMind AI and FlowMind documentation I have access to.

**Exchange 6 — Closing**
> **You:** quit

---

## Demo Tips

- Run both demos once before presenting to warm up the vector store and confirm API keys work.
- For RAG, point out the `[retrieved N chunks: filename]` line — it shows exactly which document was used to answer each question.
- The out-of-scope question in RAG Exchange 5 is powerful — it shows the model won't hallucinate when the answer isn't in the docs.
- For MCP Exchange 3, pause and highlight that two tools were called automatically in sequence — the LLM planned this itself.
- Students can add new tools to `server.py` or new documents to `RAG_demo/documents/` without changing any other code.