import os
import requests
from pathlib import Path

# Configuration
USERNAME = "Realmchan"
LANGUAGE_EXTENSIONS = {
    "GNU C++17": ".cpp",
    "Python 3": ".py",
    "Java 11": ".java",
    "Kotlin 1.4": ".kt",
    # Add more languages and extensions as needed
}

def fetch_submissions(username):
    url = f"https://codeforces.com/api/user.status?handle={username}"
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception(f"Error fetching submissions: {response.json().get('comment', 'Unknown error')}")
    return response.json()["result"]

def save_submission(submission, base_dir):
    contest_id = submission["contestId"]
    problem_id = submission["problem"]["index"]
    language = submission["programmingLanguage"]
    extension = LANGUAGE_EXTENSIONS.get(language, ".txt")
    submission_id = submission["id"]  # Unique ID for each submission

    code = submission["program"]
    if not code.strip():
        return  # Skip empty submissions

    # Directory for the contest
    contest_dir = base_dir / f"Contest-{contest_id}"
    contest_dir.mkdir(parents=True, exist_ok=True)

    # Save the file with a unique name (submission ID)
    file_name = f"{problem_id}_{submission_id}{extension}"
    file_path = contest_dir / file_name

    with open(file_path, "w", encoding="utf-8") as file:
        file.write(code)

    print(f"Saved: {file_path}")

def main():
    base_dir = Path(".")
    submissions = fetch_submissions(USERNAME)
    for submission in submissions:
        if submission["verdict"] == "OK":  # Only save accepted solutions
            save_submission(submission, base_dir)

if __name__ == "__main__":
    main()
