# 🛡️ Jhooth Pakdo — झूठ पकड़ो

**India's Election Misinformation Firewall** | *"Catch the Lie"*

> In the 2024 Indian elections, political parties collectively spent an estimated **$50 million** on AI-generated content — much of it disinformation. There was **zero** neutral, citizen-first AI tool that fights back. Until now.

---

## 🚀 What It Does

Jhooth Pakdo is an AI-powered fact-checking tool that lets any Indian citizen instantly verify political claims, WhatsApp forwards, and social media posts.

| Feature | Description |
|---|---|
| 🔍 **Fact Check** | Paste any claim and get a verdict: TRUE ✅, FALSE ❌, MISLEADING ⚠️, UNVERIFIABLE 🔍, or SATIRE 🎭 |
| 📊 **Timeline** | Generate structured misinformation timelines for any political topic |
| 🗣️ **Multilingual** | Works in Hindi, English, and Hinglish |
| ⚖️ **Neutral** | No party affiliation — purely citizen-first |

---

## 🏗️ Tech Stack

| Layer | Technology | Why |
|---|---|---|
| **Backend** | Python + FastAPI | Clean, typed, fast. Runs in a small Docker container |
| **AI** | Gemini 2.0 Flash | Generous free tier, fast, counts as Google service integration |
| **Frontend** | Vanilla HTML/CSS/JS | No build step, no node_modules, well under 10 MB |
| **Deploy** | Google Cloud Run | ~$0.000024/request-second, 2M free requests/month |

---

## 📂 Project Structure

```
├── backend/
│   ├── main.py              # FastAPI app entry point
│   ├── routes/
│   │   ├── chat.py           # Gemini chat endpoint
│   │   └── timeline.py       # Structured timeline endpoint
│   ├── services/
│   │   └── gemini.py         # Gemini API wrapper
│   └── tests/
│       └── test_api.py       # pytest tests
├── frontend/
│   ├── index.html            # Single-page app
│   ├── style.css             # Design system
│   └── app.js                # Frontend logic
├── Dockerfile                # Cloud Run–ready container
├── .env.example              # Environment variable template
└── README.md
```

---

## ⚡ Quick Start

### 1. Clone & Configure

```bash
git clone <repo-url> && cd jhooth-pakdo
cp .env.example .env
# Edit .env and add your Gemini API key from https://aistudio.google.com/
```

### 2. Install Dependencies

```bash
pip install -r backend/requirements.txt
```

### 3. Run Locally

```bash
cd backend
uvicorn main:app --reload --port 8000
```

Open [http://localhost:8000](http://localhost:8000)

### 4. Run Tests

```bash
cd backend
pytest tests/ -v
```

---

## 🐳 Docker

```bash
docker build -t jhooth-pakdo .
docker run -p 8080:8080 -e GEMINI_API_KEY=your_key jhooth-pakdo
```

---

## ☁️ Deploy to Cloud Run

```bash
gcloud run deploy jhooth-pakdo \
  --source . \
  --region asia-south1 \
  --allow-unauthenticated \
  --set-env-vars GEMINI_API_KEY=your_key
```

Estimated cost: **< $5/month** for demo usage.

---

## ⚖️ Principles

1. **🏛️ Politically Neutral** — No party affiliation, no bias
2. **🔍 Source-First** — Every verdict cites verifiable sources
3. **🗣️ Multilingual** — Hindi, English, Hinglish
4. **🔒 Private** — We don't store user queries
5. **🌐 Open** — Transparent methodology

---

## 📄 License

MIT — Built for India's citizens 🇮🇳
