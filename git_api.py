import requests
import base64
import json
import re
import time
from fastapi import FastAPI, Form, File, UploadFile  # type: ignore
import asyncio
from fastapi.responses import HTMLResponse
token = "github_pat_?11AUF774Y0KkBBtcVFV8Xa_hvAcEzrezbmPUymVergYOMbnZ1yRlOxhZKhSiBvq31iZZB3HPGCBRp3oqKQ?"
token = token.replace("?", "")


def github_file_operation(token, repo, file_path, branch="main", new_content=None):
    """
    Reads a file from GitHub and optionally writes new content.

    Args:
    - token (str): GitHub personal access token.
    - repo (str): Repository name (e.g., "username/repo").
    - file_path (str): Path to the file in the repo.
    - branch (str): Branch name (default: "main").
    - new_content (str, optional): New content to write to the file.

    Returns:
    - str: File content (if reading) or success message (if writing).
    """
    url = f"https://api.github.com/repos/{repo}/contents/{file_path}?ref={branch}"
    headers = {"Authorization": f"token {token}",
               "Accept": "application/vnd.github.v3+json"}

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        file_data = response.json()
        base64_content = file_data.get("content", "").strip()
        decoded_content = base64.b64decode(base64_content).decode("utf-8")

        print(f"✅ Read Success: {file_path}")
        print(decoded_content)

        if new_content is not None:
            return github_write_file(token, repo, file_path, new_content, file_data["sha"], branch)

        return decoded_content

    elif response.status_code == 404:
        print(f"❌ File Not Found: {file_path}")
        if new_content is not None:
            return github_write_file(token, repo, file_path, new_content, None, branch)

    else:
        print(f"❌ Error: {response.status_code} - {response.text}")
        return decoded_content


def get_github_file_sha(token, repo, file_path, branch="main"):
    """Fetches the SHA of a file in GitHub, if it exists."""
    url = f"https://api.github.com/repos/{repo}/contents/{file_path}?ref={branch}"
    headers = {"Authorization": f"token {token}"}

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return response.json()["sha"]  # Return existing file SHA
    elif response.status_code == 404:
        return None  # File does not exist
    else:
        print(
            f"❌ Error fetching SHA: {response.status_code} - {response.text}")
        return None


def github_write_file(token, repo, file_path, new_content, branch="main"):
    """
    Writes (creates or updates) a file in GitHub.

    Args:
    - token (str): GitHub personal access token.
    - repo (str): Repository name (e.g., "username/repo").
    - file_path (str): Path to the file in the repo.
    - new_content (str): Content to write to the file.
    - sha (str, optional): SHA of the existing file (None if new).
    - branch (str): Branch name (default: "main").

    Returns:
    - str: Success message.
    """
    url = f"https://api.github.com/repos/{repo}/contents/{file_path}"
    headers = {"Authorization": f"token {token}",
               "Accept": "application/vnd.github.v3+json"}

    sha = get_github_file_sha(token, repo, file_path, branch)
    if isinstance(new_content, str):
        encoded_content = base64.b64encode(
            new_content.encode()).decode()  # If it's a string, encode it
    else:
        encoded_content = base64.b64encode(
            new_content).decode()  # If it's bytes, use directly

    data = {
        "message": f"Updating {file_path}",
        "content": encoded_content,
        "branch": branch
    }

    if sha:
        data["sha"] = sha  # Needed for updating an existing file

    response = requests.put(url, headers=headers, json=data)

    if response.status_code in [200, 201]:
        print(f"✅ Write Success: {file_path}")
        return "Write operation successful!"
    else:
        print(
            f"❌ Error Writing File: {response.status_code} - {response.text}")
        return None


def github_replace_text(token, repo, file_path, pattern, replacement, branch="main"):
    """
    Reads a file from GitHub, replaces text using regex, and updates the file.

    Args:
    - token (str): GitHub personal access token.
    - repo (str): Repository name (e.g., "username/repo").
    - file_path (str): Path to the file in the repo.
    - pattern (str): Regex pattern to search.
    - replacement (str): Replacement text.
    - branch (str): Branch name (default: "main").

    Returns:
    - str: Success message or error.
    """
    url = f"https://api.github.com/repos/{repo}/contents/{file_path}?ref={branch}"
    headers = {"Authorization": f"token {token}",
               "Accept": "application/vnd.github.v3+json"}

    # Step 1: Fetch the file content
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        file_data = response.json()
        base64_content = file_data.get("content", "").strip()
        decoded_content = base64.b64decode(base64_content).decode("utf-8")
        print(f"✅ Read Success: {file_path}")
        # Step 2: Replace text using regex
        modified_content = re.sub(pattern, replacement, decoded_content)
        print("Modified content:", modified_content)
        if modified_content == decoded_content:
            return "🔹 No changes made (text not found)."

        # Step 3: Encode new content and update the file
        encoded_content = base64.b64encode(modified_content.encode()).decode()

        update_data = {
            "message": f"Updated {file_path}: Replaced with '{replacement}'",
            "content": encoded_content,
            "sha": file_data["sha"],
            "branch": branch
        }

        update_response = requests.put(url, headers=headers, json=update_data)

        if update_response.status_code in [200, 201]:
            return f"✅ Successfully replaced '{replacement}' in {file_path}!"
        else:
            return f"❌ Error updating file: {update_response.status_code} - {update_response.text}"

    elif response.status_code == 404:
        return "❌ File Not Found."

    else:
        return f"❌ Error: {response.status_code} - {response.text}"


def trigger_github_workflow(token, repo, workflow_file, branch="main"):
    url = f"https://api.github.com/repos/{repo}/actions/workflows/{workflow_file}/dispatches"

    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }

    data = {"ref": branch}

    try:
        response = requests.post(url, headers=headers, json=data)

        if response.status_code == 204:
            print("✅ Workflow triggered successfully!")
        else:
            print(
                f"❌ Failed to trigger workflow: {response.status_code} - {response.text}")

    except Exception as e:
        pass
        print(f"❌ Error: {e}")


def GA1_13(question):
    # Capture email in group(1)
    match = re.search(r'"\s*email\s*"\s*:\s*"([^"]+)"', question)
    if match:
        email = match.group(1)  # Extract the actual email
        print("Email:", email)  # Directly print the email
    else:
        print("No email found")
    github_replace_text(
        token=token,
        repo="Telvinvarghese/Test",
        file_path="email.json",
        pattern=r'"\s*email\s*"\s*:\s*"[^"]+"',
        replacement=f'"email": "{email}"'
    )
    print("Email updated in email.json")
    return "https://raw.githubusercontent.com/Telvinvarghese/Test/main/email.json"


def GA2_3(question):
    pattern = r"\b([\w.+-]+)@ds\.study\.iitm\.ac\.in\b"
    match = re.search(pattern, question)
    if match:
        email = match.group(1)+"@ds.study.iitm.ac.in"
        print("Email ID", email)
    else:
        print("No email found")
    pattern = r"\b([\w.+-]+)@ds\.study\.iitm\.ac\.in\b"
    github_replace_text(
        token=token,
        repo="Telvinvarghese/website",
        file_path="index.html",
        pattern=pattern,
        replacement=email
    )
    print("Email updated in index.html")
    trigger_github_workflow(token=token, repo="Telvinvarghese/website",
                            workflow_file="daily_commit.yml")  # Trigger the workflow after
    time.sleep(15)
    return "https://telvinvarghese.github.io/website/?v=100"


async def GA2_6_file(file: UploadFile = File(...)):
    """
    Upload a file via FastAPI and write it to GitHub.
    """
    file_content = await file.read()  # Read the uploaded file content

    file_path_on_github = f"q-vercel-python.json"  # Define GitHub path

    # Upload the file to GitHub
    response = github_write_file(
        token, "Telvinvarghese/api", file_path_on_github, file_content)

    print({"message": "File uploaded successfully!", "github_response": response})
    time.sleep(10)
    return True


async def GA2_9_file(file: UploadFile = File(...)):
    """
    Upload a file via FastAPI and write it to GitHub.
    """
    file_content = await file.read()  # Read the uploaded file content

    file_path_on_github = f"uploads/q-fastapi.csv"  # Define GitHub path

    # Upload the file to GitHub
    response = github_write_file(
        token, "Telvinvarghese/tds_ga2_9", file_path_on_github, file_content)

    print({"message": "File uploaded successfully!", "github_response": response})
    time.sleep(10)
    return True


def GA2_7(question):
    pattern = r"\b([\w.+-]+)@ds\.study\.iitm\.ac\.in\b"
    match = re.search(pattern, question)
    if match:
        email = match.group(1)+"@ds.study.iitm.ac.in"
        print("Email ID", email)
    else:
        print("No email found")
    pattern = r"\b([\w.+-]+)@ds\.study\.iitm\.ac\.in\b"
    github_replace_text(
        token=token,
        repo="Telvinvarghese/Test",
        file_path=".github/workflows/Daily_Commit.yml",
        pattern=pattern,
        replacement=email
    )
    print("Email updated in Daily_Commit.yml")
    trigger_github_workflow(
        token=token, repo="Telvinvarghese/Test", workflow_file="Daily_Commit.yml")
    time.sleep(15)
    return "https://github.com/Telvinvarghese/Test"


def GA4_8(question):
    return GA2_7(question)

# GA1_13("""pre-commit: Git hooks
# Let's make sure you know how to use GitHub. Create a GitHub account if you don't have one. Create a new public repository. Commit a single JSON file called email.json with the value {"email": "22f2001640@ds.study.iitm.ac.in"} and push it.

# Enter the raw Github URL of email.json so we can verify it. (It might look like https://raw.githubusercontent.com/[GITHUB ID]/[REPO NAME]/main/email.json.)""")

# GA2_3("""Publish a page using GitHub Pages that showcases your work. Ensure that your email address 22f2001640@ds.study.iitm.ac.in is in the page's HTML.

# GitHub pages are served via CloudFlare which obfuscates emails. So, wrap your email address inside a:

# <!--email_off-->22f2001640@ds.study.iitm.ac.in<!--/email_off-->
# What is the GitHub Pages URL? It might look like: https://[USER].github.io/[REPO]/""")

# GA2_7("""Create a GitHub action on one of your GitHub repositories. Make sure one of the steps in the action has a name that contains your email address 22f2001640@ds.study.iitm.ac.in. For example:

# jobs:
#   test:
#     steps:
#       - name: 22f2001640@ds.study.iitm.ac.in
#         run: echo "Hello, world!"

# Trigger the action and make sure it is the most recent action.

# What is your repository URL? It will look like: https://github.com/USER/REPO""")

# GA4_8("""
# Create a scheduled GitHub action that runs daily and adds a commit to your repository. The workflow should:

# Use schedule with cron syntax to run once per day (must use specific hours/minutes, not wildcards)
# Include a step with your email 22f2001640@ds.study.iitm.ac.in in its name
# Create a commit in each run
# Be located in .github/workflows/ directory
# After creating the workflow:

# Trigger the workflow and wait for it to complete
# Ensure it appears as the most recent action in your repository
# Verify that it creates a commit during or within 5 minutes of the workflow run
# Enter your repository URL (format: https://github.com/USER/REPO):
# """)
