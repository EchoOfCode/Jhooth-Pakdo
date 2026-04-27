# 🗳️ Chunav Guide — India's Interactive Election Assistant

**Understand the Election Process, Timelines, and Steps.**

> **Hackathon Submission:** Creating an assistant that helps users understand the election process, timelines, and steps in an interactive and easy-to-follow way.

---

## 🎯 Chosen Vertical
**Civic Tech & Voter Education.** 
We chose to focus on building an interactive, highly accessible guide that empowers Indian citizens by demystifying the complex electoral process. 

## 🧠 Approach and Logic
Elections in India involve massive scale and complex rules. Text-heavy websites from official sources can be overwhelming for new or rural voters. Our logic was to create an AI-powered conversational assistant ("Chunav Guide") that:
1. Translates complex election jargon into simple, actionable steps.
2. Structures timelines visually (e.g., General Election schedules, registration deadlines).
3. Grounds every answer in real-time, factual data using **Google Search Grounding**.

## ⚙️ How the Solution Works
Chunav Guide is a single-page interactive web application:
- **Chat Assistant**: Users can ask natural language questions (in English, Hindi, or Hinglish) like *"How do I register to vote?"*. The backend sends this to Google's **Gemini 2.0 Flash API**.
- **Visual Timelines**: Users can input a process (e.g., *"EVM Counting"*). The AI structures the process into a chronological JSON payload, which the frontend renders as a beautiful, color-coded timeline.
- **Search Grounding**: To prevent hallucinations, the AI is natively integrated with the Google Search API to fetch live electoral rules and data.

## 🤔 Assumptions Made
- Users have basic internet connectivity to load the web app.
- Users may not know official terminology, so the AI is instructed to be highly tolerant of spelling errors and multilingual input (Hinglish).

---

## 🌟 Evaluation Focus Areas

### 1. Code Quality
- **Architecture**: Clean separation of concerns (Frontend UI -> FastAPI Router -> Gemini Service).
- **Maintainability**: Typed Python backend, modular CSS/JS without heavy frameworks (Vanilla JS keeps the repo < 500KB).
- **Structure**: Easy to read and scale for future features.

### 2. Security
- **API Protection**: API keys are securely managed via environment variables and never exposed to the frontend.
- **Dependency Safety**: Minimal Python dependencies to reduce the attack surface.

### 3. Efficiency
- **Hyper-Lean Repo**: No `node_modules` or complex build steps. The entire app is lightning fast.
- **Fallback Logic**: The Gemini service implements an asynchronous retry and model-fallback mechanism (switching to `gemini-2.0-flash-lite` if rate limits are hit) ensuring high availability.

### 4. Testing
- Includes a robust `pytest` suite testing API health, input validation, and mocking the Gemini SDK to ensure backend resilience without burning API credits.

### 5. Accessibility
- **Design**: High contrast dark-mode UI with clear semantic HTML.
- **Inclusive UX**: Large typography, intuitive icons, and responsive design for mobile devices (where most Indian voters access the internet).

### 6. Google Services (Meaningful Integration)
This project deeply integrates the Google Cloud ecosystem:
1. **Google Cloud Run**: Containerized deployment for scalable, serverless execution.
2. **Google Generative AI (Gemini 2.0 Flash)**: The core intelligence engine powering the interactive chat and timeline structuring.
3. **Google Search Grounding**: The Gemini model is explicitly configured with `tools=[{"google_search": {}}]` to fetch real-time, accurate election data natively through Google's search graph, ensuring the civic information is factual and up-to-date.

---

## ⚡ Quick Start

### 1. Clone & Configure
```bash
git clone <repo-url> && cd jhooth-pakdo
cp .env.example .env
# Edit .env and add your Gemini API key from https://aistudio.google.com/
```

### 2. Run Locally
```bash
pip install -r backend/requirements.txt
cd backend
uvicorn main:app --reload --port 8000
```

### 3. Deploy to Google Cloud Run
```bash
gcloud run deploy chunav-guide \
  --source . \
  --region asia-south1 \
  --allow-unauthenticated \
  --set-env-vars GEMINI_API_KEY=your_key
```

## 📄 License
MIT — Built for India's citizens 🇮🇳
