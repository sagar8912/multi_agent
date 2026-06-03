# Implementation Plan: Agentic AI Cyber Risk Underwriting Intelligence Tool

## 1. Executive Summary
- **What we are building:** An Agentic AI-based Cyber Risk Underwriting Intelligence Tool that automates the assessment of cyber risks for target companies.
- **Why we are building it:** To improve the speed, consistency, and accuracy of cyber underwriting by replacing manual research with automated, evidence-backed AI workflows.
- **Who will use it:** Cyber insurance underwriters, risk analysts, and portfolio managers.

## 2. Problem Statement
- **Manual Effort:** Current underwriting research is highly manual, time-consuming, and prone to human error.
- **Scattered Data:** Risk data is scattered across multiple public and proprietary sources.
- **Inconsistent Scoring:** Risk scoring lacks consistent application of evidence, making pricing and risk accumulation difficult to standardize.

## 3. Proposed Solution
- **Agentic AI Tool:** A co-pilot for underwriters that autonomously gathers and evaluates company risk data.
- **Multi-Agent Workflow:** Specialized agents (e.g., Domain, Privacy, E-Commerce) handle specific research and scoring tasks concurrently.
- **Modifier-Based Scoring:** Systematically applies cyber underwriting modifier rules to adjust a baseline risk profile.
- **Evidence-Backed Report:** Generates a cyber risk score and underwriter summary backed by verifiable URLs and confidence scores.

## 4. MVP Scope
The MVP will focus on fast-to-build, high-impact components:
- **Domain Encryption Agent**
- **Privacy Regulation Agent**
- **E-Commerce Agent**
- **Customer Type Agent**
- **Geographic Spread Agent**
- **Fact Checker**
- **Scoring Engine**
- **JSON Risk Report Generation**

## 5. Out of Scope for MVP
- Premium calculation
- Dynamic pricing
- Dark web data analysis
- Paid D&B integration
- Full portfolio accumulation risk
- Climate/geopolitical risk modules

## 6. High-Level Workflow

```text
[Company Input]
       |
       v
[Supervisor Agent] ----------------------------------+
       |                                             |
       +--> [Research Agents]                        |
       |      |- Domain Encryption Agent             |
       |      |- Privacy Regulation Agent            |
       |      |- E-Commerce Agent                    |
       |      |- Customer Type Agent                 |
       |      |- Geographic Spread Agent             |
       v                                             |
[Fact Checker] <-------------------------------------+
       |
       v
[Underwriter Agent]
       |
       v
[Scoring Engine]
       |
       v
[Cyber Risk Report (JSON)]
```

## 7. Agent Design
- **Supervisor Agent:** 
  - **Purpose:** Orchestrate the workflow. 
  - **Input:** Company details (Name, Domain, etc.). 
  - **Output:** Task assignments. 
  - **Logic:** Distributes sub-tasks to Research Agents.
- **Research Agents (Domain, Privacy, E-Commerce, Customer, Geo):** 
  - **Purpose:** Gather specific modifier data. 
  - **Input:** Company URLs and search queries. 
  - **Output:** Raw evidence and modifier assessments. 
  - **Logic:** Web scraping, search integration, and data parsing.
- **Fact Checker Agent:** 
  - **Purpose:** Verify agent findings. 
  - **Input:** Agent assessments and evidence URLs. 
  - **Output:** Verified facts and confidence scores. 
  - **Logic:** Cross-references findings against sources; flags hallucinations.
- **Underwriter Agent:** 
  - **Purpose:** Synthesize findings. 
  - **Input:** Verified facts and scores. 
  - **Output:** Underwriter summary narrative. 
  - **Logic:** Uses LLM to generate a human-readable risk narrative based on the collected evidence.

## 8. Modifier Design
- **Domain Encryption:**
  - **Data needed:** Protocol of company domains, SSL certificate validity.
  - **Collection:** HTTP requests, SSL inspection tools.
  - **Calculation:** -1 if HTTPS valid, +2 if HTTP or invalid cert.
  - **Example output:** `{"modifier": "Domain Encryption", "score": -1, "evidence": "Valid SSL cert from Let's Encrypt"}`
- **Privacy Regulation:**
  - **Data needed:** Presence of privacy policy, mentions of GDPR/CCPA.
  - **Collection:** Scraping homepage footer, privacy policy page.
  - **Calculation:** 0 if clear policy, +1 if missing or inadequate.
- **E-Commerce Presence:**
  - **Data needed:** Shopping cart presence, payment gateways.
  - **Collection:** Web scraping for keywords (cart, checkout, buy now).
  - **Calculation:** +1 if active e-commerce, 0 if purely informational.
- **Customer Type (B2B/B2C):**
  - **Data needed:** B2B vs. B2C focus.
  - **Collection:** Analyzing homepage copy, client testimonials, products.
  - **Calculation:** +1 for B2C (higher data risk), 0 for B2B.
- **Geographic Spread:**
  - **Data needed:** Countries of operation or office locations.
  - **Collection:** "Contact Us" or "Locations" pages.
  - **Calculation:** +1 if >3 regions or high-risk jurisdictions, 0 otherwise.

## 9. Data Sources
- Company website (Home, About, Contact, Footer)
- Privacy policy pages
- Product and Pricing pages
- Investor relations / SEC filings (where available)
- Public web search
- **Future:** D&B, CyberWrite, Cyrus, Profound references.

## 10. Output Format
```json
{
  "company_name": "Example Corp",
  "modifiers": [
    {
      "name": "Domain Encryption",
      "score": -1,
      "evidence_urls": ["https://example.com"],
      "confidence": 0.99
    },
    {
      "name": "Privacy Regulation",
      "score": 0,
      "evidence_urls": ["https://example.com/privacy"],
      "confidence": 0.95
    }
  ],
  "total_modifier_score": -1,
  "risk_category": "Low",
  "underwriter_summary": "Example Corp maintains strong basic hygiene with valid domain encryption and a clearly defined privacy policy adhering to standard regulations. They operate primarily B2B with no direct e-commerce exposure."
}
```

## 11. Technical Architecture
- **Language:** Python
- **Framework:** FastAPI (API endpoints), Pydantic (data validation)
- **Scraping:** BeautifulSoup, httpx / requests
- **Configuration:** JSON/YAML for rule config and modifier logic
- **Optional/Future:** Azure OpenAI (LLM models), LangGraph (Agent orchestration), MLflow (Prompt tracking), Docker (Containerization)

## 12. Folder Structure
```text
cyber_risk_tool/
├── api/
│   ├── main.py
│   ├── routes.py
│   └── dependencies.py
├── agents/
│   ├── supervisor.py
│   ├── research/
│   │   ├── domain_agent.py
│   │   ├── privacy_agent.py
│   │   ├── ecommerce_agent.py
│   │   ├── customer_type_agent.py
│   │   └── geo_agent.py
│   ├── fact_checker.py
│   └── underwriter.py
├── core/
│   ├── config.py
│   ├── scoring_engine.py
│   └── llm_client.py
├── schemas/
│   ├── input_models.py
│   └── output_models.py
├── rules/
│   └── modifiers.yaml
├── utils/
│   ├── scraper.py
│   └── logger.py
├── requirements.txt
└── Dockerfile
```

## 13. 4-Day Planning Timeline
- **Day 1:** Understand PPT, modifier Excel, and reference documents; Finalize MVP scope; Identify priority modifiers.
- **Day 2:** Create architecture diagram; Define agents and data flow; Define input/output schema.
- **Day 3:** Prepare scoring framework; Define modifier rules; Prepare API design and folder structure.
- **Day 4:** Finalize implementation plan; Prepare presentation; Prepare questions/blockers for manager.

## 14. Development Roadmap After Planning
- **Week 1:** Setup + basic FastAPI + Domain Encryption
- **Week 2:** Privacy + E-Commerce + Customer Type
- **Week 3:** Geographic Spread + Fact Checker + Scoring
- **Week 4:** Report generation + testing + demo

## 15. Task Allocation
- **Sagar:** Web scraping utilities, Domain Encryption Agent, Privacy Regulation Agent.
- **Shivam:** FastAPI setup, E-Commerce Agent, Customer Type Agent, Geographic Spread Agent.
- **Lead/Architect:** System Architecture, Supervisor Agent, Fact Checker, Scoring Engine, Prompts.
- **Manager/Reviewer:** Requirement validation, modifier logic review, final report approval.

## 16. Risks and Dependencies
- **Azure/LLM Access Delay:** Dependency on IT for API keys and rate limits.
- **Website Scraping Restrictions:** Cloudflare, CAPTCHAs, or IP bans.
- **Modifier Rule Ambiguity:** Need clear scoring thresholds from the underwriting team.
- **Data Source Limitations:** Private companies may lack public information.
- **Accuracy and Hallucination Risk:** LLM inventing evidence or misinterpreting text.

## 17. Questions for Manager
1. Are there specific regional regulations (e.g., EU vs. US) we should prioritize for the Privacy Agent?
2. How should we handle companies that completely block automated web scraping?
3. What is the expected turnaround time for a single company's risk report in production?
4. Do we have a budget allocated for specific paid APIs if public scraping proves insufficient for MVP?
5. Who will provide the final sign-off on the accuracy of the Scoring Engine's modifier weights?
6. Should the MVP integrate with any existing internal databases, or operate completely standalone?
7. What format do the underwriters currently use to consume this data (e.g., PDF, Excel, Dashboard)?
8. How will we measure the business value of this MVP to justify Phase 2 funding?

## 18. MVP Success Criteria
- The system successfully intakes a company name and domain.
- All 5 MVP agents run without fatal crashes on 80% of test cases.
- The Fact Checker successfully validates evidence and flags missing URLs.
- The Scoring Engine produces a valid JSON report containing modifier scores and an underwriter summary.
- The end-to-end execution time per company is under 2 minutes.

## 19. Final Recommendation
- **Recommend starting development with Domain Encryption, Privacy Regulation, and E-Commerce Presence.** 
  These modifiers are the fastest to build and require fewer paid data sources. They rely on relatively structured or easily accessible public web data, allowing for quick wins and immediate demonstration of the multi-agent orchestration framework.
