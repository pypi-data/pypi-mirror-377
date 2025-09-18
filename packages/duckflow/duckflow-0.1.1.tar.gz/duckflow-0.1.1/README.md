# DuckFlow 🦆

**Have your ducks in a row, and watch them go.**  
A playful pipeline framework for chaining AI and logic tasks, built around the metaphor of ducks and flocks.

---

## 🐥 Core Concepts

- **Duck** → A modular unit (task handler). Example: query DuckDuckGo, call OpenAI, format CSV.
- **Flock** → A pipeline definition, chaining ducks together into a workflow.
- **Pond** → Your environment/configuration where ducks swim (e.g. knowledge base files, `.env`).

---

## 📦 Install from PyPI

Once published, DuckFlow can be installed directly:

```bash
pip install duckflow
```

Or inside a virtual environment:

```bash
python -m venv venv
source venv/bin/activate
pip install duckflow
```

---

## 🔑 Environment Variables

DuckFlow requires API keys for certain ducks (e.g., OpenAI). Create a `.env` file in your project root:

```bash
OPENAI_API_KEY=sk-your-key-here
# Optional other services:
# BRAVE_API_KEY=your-key-here
# SERPAPI_KEY=your-key-here
```

---

## 🦆 Example: Quack Test

A toy demo duck that simply quacks back your input.

```bash
duckflow quack_test "Hello DuckFlow"   --ducks-dir ./examples/ducks   --flock-file ./examples/flock.json
```

Output:
```
Running flock: quack_test
Duck quack (type=quack_node) produced output: Quack! You said: Hello DuckFlow
Final flock result: Quack! You said: Hello DuckFlow
```

---

## 🌊 Example: Duck Pond Research

A flock where one duck does research and another summarizes with OpenAI, augmented by a local knowledge base.

```bash
duckflow duckpond_summary "Why do ducks love ponds?"   --ducks-dir ./examples/ducks   --flock-file ./examples/flock.json
```

Possible output:
```
Running flock: duckpond_summary
Duck duckpond_researcher (type=duckduckgo_research) produced output: Related info: Ducks are aquatic birds...; Ponds support ecosystems...
Duck duckpond_summarizer (type=openai_chat) produced output:
- Ducks love ponds because they provide food, safety, and social space.
- Ponds support ecosystems that ducks thrive on.
- Ducklings learn foraging in ponds.
Final flock result: - Ducks love ponds because they provide food, safety, and social space. ...
```

---

## 📂 Project Structure

```
duckflow/            # Core library
  core/              # Runner, duck, flock, registry, settings
  handlers/          # Duck handler implementations
examples/            # Example ducks, flocks, and KBs
```

---

## 📜 License

MIT
