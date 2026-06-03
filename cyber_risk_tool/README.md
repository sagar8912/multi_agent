# Agentic AI Cyber Risk Underwriting Intelligence Tool

## 1. Project Overview
This tool is an Agentic AI-based backend built to assist cyber insurance underwriters. It autonomously researches target companies, evaluates predefined risk modifiers, verifies facts, and compiles a comprehensive Cyber Risk Report.

## 2. Why this tool is being built
Manual underwriting research is time-consuming and inconsistent. This tool accelerates the process, standardizes the scoring based on verifiable evidence, and produces underwriter-friendly summaries.

## 3. Agentic Workflow
Company Input -> Supervisor Agent -> Research Agents -> Fact Checker Agent -> Underwriter Agent -> Scoring Engine -> JSON Report.

## 4. MVP Modifiers
- Domain Encryption
- Privacy Regulation
- E-Commerce Presence
- Customer Type
- Geographic Spread

## 5. Folder Structure
```text
cyber_risk_tool/
├── api/          # FastAPI routes and main app
├── agents/       # AI agents (Supervisor, Research, FactChecker, Underwriter)
├── core/         # Config and Scoring logic
├── schemas/      # Pydantic models for Input/Output
├── rules/        # YAML configuration for modifiers
├── utils/        # Web scraping and text processing utilities
├── tests/        # API tests
├── outputs/      # Saved JSON reports
└── ...
```

## 6. Setup Commands
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## 7. Demo Steps
1. **Start server:** `python run.py` (or `uvicorn api.main:app --reload`)
2. **Open Swagger UI:** Navigate to [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
3. **Run /health:** Test if the API is up.
4. **Run /modifiers:** Ensure the rules engine is correctly loaded.
5. **Run /analyze-company:** Submit a company profile to generate a full cyber risk report.
6. **View saved reports:** Use the `GET /reports` endpoint to view dynamically saved JSON reports.

## 8. Sample Commands
**Curl:**
```bash
curl -X 'POST' \
  'http://127.0.0.1:8000/analyze-company' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "company_name": "Microsoft",
  "domain": "microsoft.com",
  "country": "USA",
  "revenue_band": "> $1B",
  "industry": "Technology"
}'
```

**PowerShell:**
```powershell
$body = @{
    company_name = "Microsoft"
    domain = "microsoft.com"
    country = "USA"
    revenue_band = "> `$1B"
    industry = "Technology"
} | ConvertTo-Json
Invoke-RestMethod -Uri "http://127.0.0.1:8000/analyze-company" -Method Post -ContentType "application/json" -Body $body
```

## 9. How to test
```bash
python -m tests.test_sample_requests
```

## 10. Future enhancements
- Azure OpenAI integration for Underwriter summaries
- LangGraph orchestration
- Dark Web checks and paid API integrations

## 11. Troubleshooting
- If website parsing fails, ensure you have an active internet connection.
- Timeout errors can be resolved by increasing httpx timeout in `utils/scraper.py`.
