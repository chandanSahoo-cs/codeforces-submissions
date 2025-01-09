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
    # Check if the 'program' key exists
    code = submission.get("program")
    if not code:
        print(f"Skipping submission {submission.get('id')} due to missing 'program'")
        return

    # Extract details
    contest_id = submission["contestId"]
    index = submission["problem"]["index"]
    submission_id = submission["id"]
    extension = get_extension(submission["programmingLanguage"])

    # Create directory and save the file
    folder = os.path.join(base_dir, f"Contest-{contest_id}")
    os.makedirs(folder, exist_ok=True)
    file_path = os.path.join(folder, f"{index}_{submission_id}.{extension}")
    with open(file_path, "w") as f:
        f.write(code)


def main():
    base_dir = Path(".")
    submissions = fetch_submissions(USERNAME)
    for submission in submissions:
        if submission["verdict"] == "OK":  # Only save accepted solutions
            save_submission(submission, base_dir)

if __name__ == "__main__":
    main()
