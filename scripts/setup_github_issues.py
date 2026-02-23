import os
import json
import requests

GITHUB_OWNER = "Narandan"
REPO_NAME = "msrp-platform"
CONFIG_FILE = "msrp_plan.json"

TOKEN = os.getenv("GITHUB_TOKEN")
if not TOKEN:
    raise SystemExit("Error: Set GITHUB_TOKEN environment variable first.")

BASE_URL = f"https://api.github.com/repos/{GITHUB_OWNER}/{REPO_NAME}"

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Accept": "application/vnd.github+json"
}

def create_milestones(config):
    milestone_map = {}

    for m in config["milestones"]:
        payload = {
            "title": m["title"],
            "state": m["state"],
            "description": m["description"]
        }

        print(f"Creating milestone: {m['title']}")
        resp = requests.post(f"{BASE_URL}/milestones", headers=headers, json=payload)

        if resp.status_code == 201:
            # Created successfully
            data = resp.json()
            milestone_map[m["title"]] = data["number"]
        elif resp.status_code == 422:
            # Probably already exists – fetch existing milestones and match by title
            print(f"Milestone '{m['title']}' may already exist. Fetching existing milestones...")
            existing_resp = requests.get(f"{BASE_URL}/milestones", headers=headers)
            print(f"Existing milestones status: {existing_resp.status_code}")
            if existing_resp.status_code == 200:
                existing_list = existing_resp.json()
                if isinstance(existing_list, list):
                    for ex in existing_list:
                        if ex.get("title") == m["title"]:
                            milestone_map[m["title"]] = ex["number"]
                            break
            else:
                print(f"Error fetching existing milestones: {existing_resp.status_code} - {existing_resp.text}")
        else:
            # Some other error (auth, repo not found, etc.)
            print(f"Failed to create milestone '{m['title']}': {resp.status_code} - {resp.text}")

    return milestone_map


def create_issues(config, milestone_map):
    for issue in config["issues"]:
        payload = {
            "title": issue["title"],
            "body": issue["body"],
            "labels": issue.get("labels", [])
        }

        m_title = issue.get("milestone_title")
        if m_title:
            payload["milestone"] = milestone_map[m_title]

        print(f"Creating issue: {issue['title']}")
        requests.post(f"{BASE_URL}/issues", headers=headers, json=payload)

def main():
    with open(CONFIG_FILE, "r") as f:
        config = json.load(f)

    milestone_map = create_milestones(config)
    create_issues(config, milestone_map)
    print("Done.")

if __name__ == "__main__":
    main()
