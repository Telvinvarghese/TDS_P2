
import pytz
from datetime import datetime
import requests
import time
import subprocess
import hashlib
import re
import json
import csv
import numpy as np
from datetime import datetime, timedelta
import os
import zipfile
import shutil
import pandas as pd  # type: ignore
import requests
from bs4 import BeautifulSoup  # type: ignore

def extract_zip_file(source: str, extract_folder: str) -> str:
    """Extracts a ZIP file from a URL or local path."""

    zip_path = "temp.zip" if source.startswith("http") else source

    if source.startswith("http"):  # Download ZIP if source is a URL
        try:
            with requests.get(source, stream=True) as r:
                r.raise_for_status()
                with open(zip_path, "wb") as f:
                    f.write(r.content)
        except requests.RequestException as e:
            raise ValueError(f"Error downloading ZIP file: {e}")

    if os.path.isfile(extract_folder):  # Prevent extracting into a file
        raise ValueError(f"'{extract_folder}' is a file, not a directory.")

    os.makedirs(extract_folder, exist_ok=True)  # Ensure directory exists

    try:
        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(extract_folder)
    except zipfile.BadZipFile:
        raise ValueError(
            f"Failed to extract ZIP file: {zip_path} is not a valid ZIP archive.")

    if source.startswith("http"):
        os.remove(zip_path)  # Cleanup downloaded ZIP

    return extract_folder

def GA1_2(question):
    email_pattern = r"email set to ([\w.%+-]+@[\w.-]+\.\w+)"
    match = re.search(email_pattern, question)

    if match:
        email = match.group(1)
        url = "https://httpbin.org/get"

        # Construct the HTTPie command
        command = ["http", "GET", url, f"email=={email}"]

        # Execute the command and capture output
        result = subprocess.run(command, capture_output=True, text=True)
        return result.stdout  # Returns the JSON response

    return {"error": "Email not found in the input text"}


def GA1_3(file_path):
    try:
        # Run Prettier and capture output
        prettier_cmd = ["npx", "-y", "prettier@3.4.2", file_path]
        formatted_output = subprocess.run(
            prettier_cmd, capture_output=True, text=True, check=True).stdout

        # Compute SHA-256 hash
        hash_value = hashlib.sha256(formatted_output.encode()).hexdigest()

        return hash_value
    except subprocess.CalledProcessError as e:
        return f"Error: {e}"


def GA1_4(question):
    sum_seq_pattern = r"SUM\(ARRAY_CONSTRAIN\(SEQUENCE\((\d+),\s*(\d+),\s*(\d+),\s*(\d+)\),\s*(\d+),\s*(\d+)\)\)"
    if match := re.search(sum_seq_pattern, question):
        rows, cols, start, step, begin, end = map(int, match.groups())
    if begin > 0:
        begin = begin-1
    answer = int(
        np.sum(np.arange(start, start + cols * step, step)[begin:end]))
    return answer


def GA1_4_old():
    sheet_url = "https://docs.google.com/spreadsheets/d/1-A4hSDwAyJWD848AAKi2S178W2HU7klu7JozwclE8kQ/edit"
    sheet_id = "1-A4hSDwAyJWD848AAKi2S178W2HU7klu7JozwclE8kQ"
    sheet_name = "Sheet1"
    cell = "A1"
    formula = "=SUM(ARRAY_CONSTRAIN(SEQUENCE(100, 100, 6, 10), 1, 10))"
    return True


def GA1_5(question):
    sum_take_sortby_pattern = r"SUM\(TAKE\(SORTBY\(\{([\d,]+)\},\s*\{([\d,]+)\}\),\s*(\d+),\s*(\d+)\)\)"
    if match := re.search(sum_take_sortby_pattern, question):
        numbers = list(map(int, match.group(1).split(',')))
        sort_order = list(map(int, match.group(2).split(',')))
        begin, end = map(int, [match.group(3), match.group(4)])
    if begin > 0:
        begin = begin-1
    sorted_numbers = [x for _, x in sorted(zip(sort_order, numbers))]
    answer = sum(sorted_numbers[begin:end])
    return answer


def GA1_7(question):
    weekday_count_pattern = r"How many (\w+)s are there in the date range (\d{4}-\d{2}-\d{2}) to (\d{4}-\d{2}-\d{2})\?"
    if match := re.search(weekday_count_pattern, question):
        weekday_str, start_date, end_date = match.groups()
        weekdays = {"Monday": 0, "Tuesday": 1, "Wednesday": 2,
                    "Thursday": 3, "Friday": 4, "Saturday": 5, "Sunday": 6}
        if weekday_str in weekdays:
            start, end = datetime.strptime(
                start_date, "%Y-%m-%d"), datetime.strptime(end_date, "%Y-%m-%d")
            answer = sum(1 for i in range((end - start).days + 1) if (start +
                         timedelta(days=i)).weekday() == weekdays[weekday_str])
    return answer


def GA1_6(question, file_path=None):
    source = file_path or (m.group(0) if (
        m := re.search(r"https?://[^\s]+", question)) else None)
    if not source:
        return ""

    html_data = requests.get(source).text if source.startswith(
        ("http://", "https://")) else open(source, "r", encoding="utf-8").read()
    soup = BeautifulSoup(html_data, "html.parser")
    hidden_input = soup.find("input", {"type": "hidden"})

    return hidden_input.get("value", "") if hidden_input else ""


def GA1_8(question, zip_file):
    file_download_pattern = r"which has a single (.+\.csv) file inside\."
    if match := re.search(file_download_pattern, question):
        csv_filename = match.group(1)
        extract_folder = extract_zip_file(os.path.join(
            os.getcwd(), 'uploads', zip_file), zip_file[:-4])
        csv_file_path = os.path.join(extract_folder, csv_filename)
        # Read CSV file
        df = pd.read_csv(csv_file_path)
        answer = df["answer"].iloc[0] if "answer" in df.columns else "Column not found"
        # Cleanup extracted files
        shutil.rmtree(extract_folder, ignore_errors=True)
    return answer


def GA1_9(question):
    json_pattern = r"\[.*?\]|\{.*?\}"
    sort_pattern = r"Sort this JSON array of objects by the value of the (\w+) field.*?tie, sort by the (\w+) field"

    json_match = re.search(json_pattern, question, re.DOTALL)
    sort_match = re.search(sort_pattern, question, re.DOTALL)

    if json_match and sort_match:
        try:
            json_data = json.loads(json_match.group())
            sort_keys = [sort_match.group(1), sort_match.group(2)]
            # print(sort_keys)
            if isinstance(json_data, list) and all(isinstance(d, dict) for d in json_data):
                sorted_data = sorted(json_data, key=lambda x: tuple(
                    x.get(k) for k in sort_keys))
                return json.dumps(sorted_data, separators=(",", ":"))
            else:
                return json.dumps(json_data, separators=(",", ":"))

        except json.JSONDecodeError:
            return None

    return None


def GA1_10(file_path):
    data = {}
    # Check if file exists
    if not os.path.isfile(file_path):
        print(f"Error: File '{file_path}' not found.")
        return "File not found"
    # Read and process the file
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            for line in file:
                line = line.strip()
                if '=' in line:
                    key, value = line.split('=', 1)
                    data[key.strip()] = value.strip()
    except Exception as e:
        print(f"Error reading file: {e}")
        return "Error reading file"
    # Convert data to JSON
    json_str = json.dumps(data, separators=(",", ":"), ensure_ascii=False)
    # print(json_str)
    # Calculate the hash of the JSON string
    json_hash = hashlib.sha256(json_str.encode('utf-8')).hexdigest()
    return json_hash


def GA1_11(question, file_path=None):
    source = file_path or (m.group(0) if (
        m := re.search(r"https?://[^\s]+", question)) else None)
    if not source:
        return 0
    html_data = requests.get(source).text if source.startswith(
        ("http://", "https://")) else open(source, "r", encoding="utf-8").read()
    soup = BeautifulSoup(html_data, "html.parser")
    divs = soup.select('div.foo[data-value]')
    return int(sum(float(div['data-value']) for div in divs))


def GA1_12(question, zip_path):
    # Regex patterns
    file_pattern = r"(\w+\.\w+):\s*(?:CSV file|Tab-separated file) encoded in ([\w-]+)"
    symbol_pattern = r"where the symbol matches ((?:[\w\d]+|\W)(?:\s*OR\s*(?:[\w\d]+|\W))*)"

    # Extract file encodings
    files = {match.group(1): match.group(2)
             for match in re.finditer(file_pattern, question)}

    # Extract symbols
    symbols_match = re.search(symbol_pattern, question)
    target_symbols = set(symbols_match.group(
        1).split(" OR ")) if symbols_match else set()

    total_sum = 0
    # Extract ZIP
    extract_folder = extract_zip_file(zip_path, zip_path[:-4])
    print(extract_folder)
    # Process extracted files
    for file_name, encoding in files.items():
        encoding = encoding.lower()
        if 'cp-' in encoding:
            encoding = encoding.replace('cp-', 'cp')
        target_symbols = list(target_symbols)
        print(file_name, encoding, target_symbols)
        file_path = os.path.join(extract_folder, file_name)
        if file_name.endswith(".csv"):
            with open(file_path, mode='r', encoding=encoding) as file:
                reader = csv.reader(file)
                for row in reader:
                    symbol, value = row
                    if symbol in target_symbols:
                        total_sum += float(value)
        elif file_name.endswith(".txt"):
            with open(file_path, mode='r', encoding=encoding) as file:
                for line in file:
                    symbol, value = line.strip().split('\t')
                    if symbol in target_symbols:
                        total_sum += float(value)
    return total_sum


def GA1_14(question, zip_path):
    # Step 1: Extract words to replace and the replacement word from the question
    pattern = r'replace\s+all\s+"([^"]+)"\s+\(.*\)\s+with\s+"([^"]+)"'
    match = re.search(pattern, question, re.IGNORECASE)
    if match:
        word_to_replace = match.group(1)  # The word to replace
        replacement_word = match.group(2)  # The replacement word
    else:
        raise ValueError("Invalid question format: Unable to extract words.")

    folder_path = zip_path[:-4]
    # Step 2: Unzip files into the target folder
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(folder_path)
        print(f"Unzipped files to {folder_path}")
    # Step 3: Replace words in all files
    for filename in os.listdir(folder_path):
        filepath = os.path.join(folder_path, filename)

        if os.path.isfile(filepath):
            with open(filepath, 'r', encoding='utf-8') as file:
                content = file.read()
            # Replace the word (case insensitive)
            updated_content = re.sub(
                re.escape(word_to_replace), replacement_word, content, flags=re.IGNORECASE)
            # Write the modified content back to the file (keeping the original line endings)
            with open(filepath, 'w', encoding='utf-8') as file:
                file.write(updated_content)
    # Step 4: Calculate the SHA-256 hash of the concatenated files
    sha256_hash = hashlib.sha256()
    # Sort files to ensure the same order
    files = sorted(os.listdir(folder_path))
    for filename in files:
        filepath = os.path.join(folder_path, filename)

        if os.path.isfile(filepath):
            with open(filepath, 'rb') as file:
                while chunk := file.read(4096):
                    sha256_hash.update(chunk)
    # Return the final SHA-256 hash value
    return sha256_hash.hexdigest()


def GA1_15(question, zip_path):
    # Extract file size and modification date from the question
    size_pattern = r"at least (\d+) bytes"
    date_pattern = r"modified on or after (.*) IST"

    # Extract file size
    size_match = re.search(size_pattern, question)
    if size_match:
        min_size = int(size_match.group(1))
    else:
        raise ValueError("No file size criterion found in the question.")

    # Extract modification date
    date_match = re.search(date_pattern, question)
    if date_match:
        date_str = date_match.group(1).replace(' IST', '').strip()
        try:
            target_timestamp = datetime.strptime(
                date_str, "%a, %d %b, %Y, %I:%M %p")
            target_timestamp = pytz.timezone(
                "Asia/Kolkata").localize(target_timestamp)
        except ValueError as e:
            raise ValueError(f"Date format error: {e}")
    else:
        raise ValueError(
            "No modification date criterion found in the question.")

    # Determine folder path from the zip file
    folder_path, _ = os.path.splitext(zip_path)

    # Extract files preserving timestamps
    if os.name == 'nt':  # Windows
        try:
            subprocess.run(
                ["7z", "x", zip_path, f"-o{folder_path}"], check=True)
        except FileNotFoundError:
            raise RuntimeError(
                "7-Zip not found. Please install or add it to the system PATH.")
        except subprocess.CalledProcessError:
            raise RuntimeError("7-Zip extraction failed.")
    else:  # Linux or macOS
        try:
            subprocess.run(
                ["unzip", "-o", zip_path, "-d", folder_path], check=True)
        except FileNotFoundError:
            raise RuntimeError(
                "unzip not found. Please install unzip utility.")
        except subprocess.CalledProcessError:
            raise RuntimeError("unzip extraction failed.")

    # Initialize total size
    total_size = 0

    # List files and check if they meet the criteria
    for filename in os.listdir(folder_path):
        filepath = os.path.join(folder_path, filename)

        if os.path.isfile(filepath):
            file_size = os.path.getsize(filepath)
            file_mtime = datetime.fromtimestamp(os.path.getmtime(
                filepath), tz=pytz.timezone("Asia/Kolkata"))

            if file_size >= min_size and file_mtime >= target_timestamp:
                total_size += file_size

    return total_size


def GA1_16(zip_path):
    folder_path, _ = os.path.splitext(zip_path)
    target_folder = os.path.join(folder_path, "renamed_files")
    os.makedirs(target_folder, exist_ok=True)

    # Extract ZIP
    if os.name == 'nt':  # Windows
        subprocess.run(["7z", "x", zip_path, f"-o{folder_path}"], check=True)
    else:  # Linux/macOS
        subprocess.run(
            ["unzip", "-o", zip_path, "-d", folder_path], check=True)

    # Move files to target folder
    for root, _, files in os.walk(folder_path):
        for file in files:
            shutil.move(os.path.join(root, file),
                        os.path.join(target_folder, file))

    # Rename files: replace digits with the next digit
    def rename_file(file_name):
        return ''.join([str((int(ch) + 1) % 10) if ch.isdigit() else ch for ch in file_name])

    for filename in os.listdir(target_folder):
        old_path = os.path.join(target_folder, filename)
        new_filename = rename_file(filename)
        new_path = os.path.join(target_folder, new_filename)
        os.rename(old_path, new_path)

    # Move into the renamed_files folder
    os.chdir(os.path.join(folder_path, "renamed_files"))
    # Run the bash command
    bash_command = "grep . * | LC_ALL=C sort | sha256sum"
    result = subprocess.run(bash_command, shell=True,
                            capture_output=True, text=True)
    sha256_value = result.stdout.strip()
    print(f"\nSHA256 hash result: {sha256_value}")

    os.chdir("..")
    del_folder = os.path.join(os.getcwd())
    print(del_folder)
    os.chdir("..")
    os.chdir("..")
    print(os.getcwd())
    shutil.rmtree(del_folder)
    return sha256_value


def GA1_17(question: str, zip_path: str) -> int:
    extract_folder = extract_zip_file(zip_path, zip_path[:-4])
    # Matches any two filenames with extensions
    files = re.findall(r'\b([^\/\\\s]+?\.[a-zA-Z0-9]+)\b', question)[:2]
    with open(os.path.join(extract_folder, files[0])) as f1, open(os.path.join(extract_folder, files[1])) as f2:
        return sum(l1.strip() != l2.strip() for l1, l2 in zip(f1, f2))


def GA1_18(question: str) -> str:
    """Extracts ticket type from the question and returns the corresponding SQL query dynamically."""
    match = re.search(
        r'in the\s+"([\w\s-]+)"\s+ticket type', question, re.IGNORECASE)
    ticket_type = match.group(1).strip().lower() if match else None
    return f"SELECT SUM(units * price) AS total_sales FROM tickets WHERE type like '%{ticket_type}%';" if ticket_type else None
