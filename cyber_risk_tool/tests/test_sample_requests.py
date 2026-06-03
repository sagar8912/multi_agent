import httpx
import time

def test_api():
    base_url = "http://127.0.0.1:8000"
    
    print("Testing GET /health...")
    try:
        resp = httpx.get(f"{base_url}/health")
        print(f"Health check: {resp.json()}")
    except Exception as e:
        print(f"API not running or unreachable: {e}. Please start it using 'python run.py'.")
        return

    print("\nTesting GET /modifiers...")
    try:
        resp = httpx.get(f"{base_url}/modifiers")
        print(f"Modifiers: {resp.json()}")
    except Exception as e:
        print(f"Failed to get modifiers: {e}")

    domains = ["microsoft.com", "apple.com", "example.com"]
    for domain in domains:
        print(f"\nTesting POST /analyze-company for {domain}...")
        payload = {
            "company_name": domain.split('.')[0].capitalize(),
            "domain": domain,
            "country": "USA",
            "revenue_band": "> $1B",
            "industry": "Technology"
        }
        resp = httpx.post(f"{base_url}/analyze-company", json=payload, timeout=60)
        if resp.status_code == 200:
            data = resp.json()
            print(f"Result for {domain}:")
            print(f"  Overall Score: {data['overall_score']:.2f}")
            print(f"  Risk Category: {data['overall_risk_category']}")
            print(f"  Confidence: {data['overall_confidence']:.2f}")
            print("  Summary:")
            print(data['underwriter_summary'])
            for mod in data['modifiers']:
                print(f"    - {mod['modifier_name']}: {mod['score']} ({mod['risk_category']}) [Verified: {mod['verification_status']}] -> {mod.get('recommendation', '')}")
        else:
            print(f"Error {resp.status_code}: {resp.text}")

    print("\nTesting GET /reports...")
    try:
        resp = httpx.get(f"{base_url}/reports")
        if resp.status_code == 200:
            reports = resp.json().get("saved_reports", [])
            print(f"Found {len(reports)} saved reports:")
            for r in reports:
                print(f"  - {r}")
        else:
            print(f"Failed to get reports. Status: {resp.status_code}")
    except Exception as e:
        print(f"Failed to get reports: {e}")

if __name__ == "__main__":
    test_api()
