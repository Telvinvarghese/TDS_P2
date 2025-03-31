
from tempfile import NamedTemporaryFile
import os
import io
import re
import json
import csv
import time
import shutil
import zipfile
import hashlib
import tempfile
import asyncio
import subprocess
import requests
import numpy as np
import pandas as pd  # type: ignore
import pytz
from datetime import datetime, timedelta
from bs4 import BeautifulSoup  # type: ignore
from fastapi import UploadFile  # type: ignore
import aiofiles


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

# Install and run Visual Studio Code. In your Terminal ( or Command Prompt), type code - s and press Enter. Copy and paste the entire output below.
# What is the output of code - s?

# def GA1_1(question):

# Running uv run - -with httpie - - https[URL] installs the Python package httpie and sends a HTTPS request to the URL.
# Send a HTTPS request to https: // httpbin.org/get with the URL encoded parameter email set to 22f2001640@ds.study.iitm.ac. in
# What is the JSON output of the command? (Paste only the JSON body, not the headers)


def GA1_2_old(question):
    pattern = r"Send a HTTPS request to (https?://[^\s]+) with the URL encoded parameter email set to ([\w.%+-]+@[\w.-]+\.\w+)"
    match = re.search(pattern, question)

    if match:
        # url = "https://httpbin.org/get"
        url, email = match.groups()
        print("URL:", url)
        print("Email:", email)

        # Construct the HTTPie command
        command = ["http", "GET", url, f"email=={email}"]

        # Execute the command and capture output
        result = subprocess.run(command, capture_output=True, text=True)
        result = json.loads(result.stdout) if result.stdout else result.stdout
        print(result["headers"]["User-Agent"])
        return result

    return {"error": "Url and Email not found in the input text"}


def GA1_2(question):
    pattern = r"Send a HTTPS request to (https?://[^\s]+) with the URL encoded parameter email set to ([\w.%+-]+@[\w.-]+\.\w+)"
    match = re.search(pattern, question)

    if match:
        url, email = match.groups()
        print("URL:", url)
        print("Email:", email)

        # Make a GET request with email as a query parameter
        response = requests.get(url, params={"email": email})
        result = response.json()
        result["headers"]["User-Agent"] = "HTTPie/3.2.4"
        return result

    return {"error": "Url and Email not found in the input text"}

# Let's make sure you know how to use npx and prettier.
# Download . In the directory where you downloaded it, make sure it is called README.md, and run npx - y prettier@3.4.2 README.md | sha256sum.
# What is the output of the command?


EXT_TO_PARSER = {".js": "babel", ".ts": "typescript", ".json": "json", ".css": "css",
                 ".html": "html", ".md": "markdown", ".yaml": "yaml", ".yml": "yaml"}


async def GA1_3(file: UploadFile):
    try:
        process = await asyncio.create_subprocess_exec(
            "npx", "-y", "prettier@3.4.2", "--parser", "markdown",
            stdin=asyncio.subprocess.PIPE, stdout=asyncio.subprocess.PIPE
        )
        formatted_output, _ = await process.communicate(await file.read())
        if not formatted_output:
            {"error": "Prettier failed"}
        return hashlib.sha256(formatted_output).hexdigest()

    except Exception as e:
        return {"error": str(e)}

# Let's make sure you can write formulas in Google Sheets. Type this formula into Google Sheets.
# (It won't work in Excel)= SUM(ARRAY_CONSTRAIN(SEQUENCE(100, 100, 6, 10), 1, 10))
#     What is the result?


def GA1_4(question):
    sum_seq_pattern = r"SUM\(ARRAY_CONSTRAIN\(SEQUENCE\((\d+),\s*(\d+),\s*(\d+),\s*(\d+)\),\s*(\d+),\s*(\d+)\)\)"
    if match := re.search(sum_seq_pattern, question):
        rows, cols, start, step, begin, end = map(int, match.groups())
        if begin > 0:
            begin = begin-1
        if step == 0:
            answer = start*10
        else:
            arr = np.arange(start, start + (cols * step), step)
        answer = int(
            np.sum(arr[begin:end]))
        return answer

# Let's make sure you can write formulas in Excel. Type this formula into Excel.
# Note: This will ONLY work in Office 365.
# =SUM(TAKE(SORTBY({11,14,12,9,5,4,13,0,1,6,7,12,10,12,0,11}, {10,9,13,2,11,8,16,14,7,15,5,4,6,1,3,12}), 1, 10))
# What is the result?


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

# Just above this paragraph, there's a hidden input with a secret value.
# What is the value in the hidden input?


def GA1_6(question, file_path=None):
    try:
        html_data = None

        # Check for URL in the question
        url_match = re.search(r"https?://[^\s]+", question)
        if url_match:
            source = url_match.group(0)
            try:
                response = requests.get(source, timeout=5)
                response.raise_for_status()
                html_data = response.text
            except requests.RequestException as e:
                print(f"Error fetching URL: {e}")
                return ""

        elif file_path:  # If a file is provided
            try:
                with open(file_path, "r", encoding="utf-8") as file:
                    html_data = file.read()
            except (FileNotFoundError, IOError) as e:
                print(f"Error reading file: {e}")
                return ""

        else:  # No URL or file, extract from the question itself
            html_data = question

        # Parse the HTML and extract the first hidden input value
        soup = BeautifulSoup(html_data, "html.parser")
        hidden_input = soup.find("input", {"type": "hidden"})

        return hidden_input.get("value", "") if hidden_input else ""

    except Exception as e:
        print(f"Unexpected error: {e}")
        return ""


# How many Wednesdays are there in the date range 1980-01-25 to 2012-07-28?

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

# Download and unzip file  which has a single extract.csv file inside.
# What is the value in the "answer" column of the CSV file?


def GA1_8(question: str, zip_file: UploadFile):
    file_download_pattern = r"which has a single (.+\.csv) file inside\."
    match = re.search(file_download_pattern, question)

    if not match:
        return "CSV filename not found in question"

    csv_filename = match.group(1)

    # Read ZIP file as bytes
    zip_bytes = zip_file.file.read()

    # Open ZIP file in memory
    with zipfile.ZipFile(io.BytesIO(zip_bytes), "r") as zf:
        if csv_filename not in zf.namelist():
            return f"{csv_filename} not found in ZIP"

        with zf.open(csv_filename) as csv_file:
            df = pd.read_csv(csv_file)
            return df["answer"].iloc[0] if "answer" in df.columns else "Column not found"

    return "Failed to process ZIP file"

# Let's make sure you know how to use JSON. Sort this JSON array of objects by the value of the age field. In case of a tie, sort by the name field. Paste the resulting JSON below without any spaces or newlines.

# [{"name":"Alice","age":74},{"name":"Bob","age":87},{"name":"Charlie","age":92},{"name":"David","age":50},{"name":"Emma","age":47},{"name":"Frank","age":29},{"name":"Grace","age":44},{"name":"Henry","age":38},{"name":"Ivy","age":91},{"name":"Jack","age":62},{"name":"Karen","age":4},{"name":"Liam","age":91},{"name":"Mary","age":42},{"name":"Nora","age":82},{"name":"Oscar","age":50},{"name":"Paul","age":62}]
# Sorted JSON:


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

# Download and use multi-cursors and convert it into a single JSON object, where key = value pairs are converted into {key: value, key: value, ...}.
# What's the result when you paste the JSON at tools-in -data-science.pages.dev/jsonhash and click the Hash button?


async def GA1_10(file: UploadFile):
    try:
        content = await file.read()
        data = dict(
            line.strip().split("=", 1)
            for line in io.StringIO(content.decode("utf-8"))
            if "=" in line
        )
    except Exception:
        return {"error": "Error reading file"}
    return hashlib.sha256(json.dumps(data, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()

# Let's make sure you know how to select elements using CSS selectors. Find all <div>s having a foo class in the hidden element below.
# What's the sum of their data-value attributes?
# Sum of data-value attributes:


def GA1_11(question, file_path=None):
    try:
        html_data = None

        # Check for URL in the question
        url_match = re.search(r"https?://[^\s]+", question)
        if url_match:
            source = url_match.group(0)
            try:
                response = requests.get(source, timeout=5)
                response.raise_for_status()
                html_data = response.text
            except requests.RequestException as e:
                print(f"Error fetching URL: {e}")
                return ""

        elif file_path:  # If a file is provided
            try:
                with open(file_path, "r", encoding="utf-8") as file:
                    html_data = file.read()
            except (FileNotFoundError, IOError) as e:
                print(f"Error reading file: {e}")
                return ""

        else:  # No URL or file, extract from the question itself
            html_data = question
        soup = BeautifulSoup(html_data, "html.parser")

        # Extract divs with class "foo" and data-value attribute
        divs = soup.select('div.foo[data-value]')

        # Convert data-value attributes to float and sum them as an integer
        values = [float(div['data-value'])
                  for div in divs if div['data-value'].replace('.', '', 1).isdigit()]
        return int(sum(values))
    except Exception as e:
        print(f"Unexpected error: {e}")
        return 0


# Download and process the files in which contains three files with different encodings:
# data1.csv: CSV file encoded in CP-1252
# data2.csv: CSV file encoded in UTF-8
# data3.txt: Tab-separated file encoded in UTF-16
# Each file has 2 columns: symbol and value. Sum up all the values where the symbol matches Œ OR ™ OR † across all three files.
# What is the sum of all values associated with these symbols?


async def GA1_12(question: str, zip_file: UploadFile):
    # Regex patterns
    file_pattern = r"(\w+\.\w+):\s*(?:CSV file|Tab-separated file) encoded in ([\w-]+)"
    symbol_pattern = r"where the symbol matches ((?:[\w\d]+|\W)(?:\s*OR\s*(?:[\w\d]+|\W))*)"

    # Extract file encodings
    files = {match.group(1): match.group(2).lower().replace('cp-', 'cp')
             for match in re.finditer(file_pattern, question)}

    # Extract symbols
    symbols_match = re.search(symbol_pattern, question)
    target_symbols = set(symbols_match.group(
        1).split(" OR ")) if symbols_match else set()

    total_sum = 0

    # Read ZIP file in-memory
    zip_bytes = await zip_file.read()
    with zipfile.ZipFile(io.BytesIO(zip_bytes), "r") as zip_ref:
        for file_name in files:
            encoding = files[file_name]
            if file_name not in zip_ref.namelist():
                continue

            with zip_ref.open(file_name) as file:
                decoded_content = io.TextIOWrapper(file, encoding=encoding)

                if file_name.endswith(".csv"):
                    reader = csv.reader(decoded_content)
                    for row in reader:
                        if len(row) >= 2 and row[0] in target_symbols:
                            total_sum += int(row[1])

                elif file_name.endswith(".txt"):
                    for line in decoded_content:
                        parts = line.strip().split("\t")
                        if len(parts) >= 2 and parts[0] in target_symbols:
                            total_sum += int(parts[1])

    return total_sum

# Let's make sure you know how to use GitHub. Create a GitHub account if you don't have one. Create a new public repository. Commit a single JSON file called email.json with the value {"email": "22f2001640@ds.study.iitm.ac.in"} and push it.
# Enter the raw Github URL of email.json so we can verify it. (It might look like https://raw.githubusercontent.com/[GITHUB ID]/[REPO NAME]/main/email.json.)

# def GA1_13(question):

# Download  and unzip it into a new folder, then replace all "IITM" ( in upper, lower, or mixed case) with "IIT Madras" in all files. Leave everything as- is - don't change the line endings.
# What does running cat * | sha256sum in that folder show in bash?


async def GA1_14(question: str, zip_file: UploadFile):
    # Step 1: Extract words to replace and the replacement word from the question
    pattern = r'replace all "([^"]+)" \(in upper, lower, or mixed case\) with "([^"]+)" in all files'
    match = re.search(pattern, question, re.IGNORECASE)
    if not match:
        raise ValueError("Invalid question format: Unable to extract words.")

    word_to_replace = match.group(1)  # The word to replace
    replacement_word = match.group(2)  # The replacement word

    print("Word to replace:", word_to_replace)
    print("Replacement word:", replacement_word)

    # Step 2: Read ZIP file in-memory
    zip_bytes = await zip_file.read()
    sha256_hash = hashlib.sha256()

    with zipfile.ZipFile(io.BytesIO(zip_bytes), "r") as zip_ref:
        file_contents = {}

        # Read and modify file contents
        for filename in sorted(zip_ref.namelist()):  # Ensure consistent order
            with zip_ref.open(filename) as file:
                content = file.read().decode("utf-8")  # Decode file content
                updated_content = re.sub(
                    re.escape(word_to_replace), replacement_word, content, flags=re.IGNORECASE)
                file_contents[filename] = updated_content.encode(
                    "utf-8")  # Store modified content

        # Compute hash from modified contents
        for filename in sorted(file_contents.keys()):
            sha256_hash.update(file_contents[filename])

    # Return the final SHA-256 hash value
    return sha256_hash.hexdigest()

# Download and extract it. Use ls with options to list all files in the folder along with their date and file size.
# What's the total size of all files at least 3352 bytes large and modified on or after Fri, 17 Aug, 2018, 4: 06 am IST?'


async def GA1_15(question: str, zip_file: UploadFile):
    # Extract file size and modification date from the question
    size_pattern = r"at least (\d+) bytes"
    date_pattern = r"modified on or after (.*) IST"

    # Extract file size
    size_match = re.search(size_pattern, question)
    if not size_match:
        raise ValueError("No file size criterion found in the question.")
    min_size = int(size_match.group(1))

    # Extract modification date
    date_match = re.search(date_pattern, question)
    if not date_match:
        raise ValueError(
            "No modification date criterion found in the question.")

    date_str = date_match.group(1).replace(' IST', '').strip()
    try:
        target_timestamp = datetime.strptime(
            date_str, "%a, %d %b, %Y, %I:%M %p")
        target_timestamp = pytz.timezone(
            "Asia/Kolkata").localize(target_timestamp)
    except ValueError as e:
        raise ValueError(f"Date format error: {e}")

    # Read ZIP file in-memory
    zip_bytes = await zip_file.read()
    total_size = 0

    with zipfile.ZipFile(io.BytesIO(zip_bytes), "r") as zip_ref:
        for zip_info in zip_ref.infolist():
            # Convert ZIP modification time to datetime with IST timezone
            file_mtime = datetime(*zip_info.date_time)
            file_mtime = pytz.timezone("Asia/Kolkata").localize(file_mtime)

            # Check if file meets size and modification date criteria
            if zip_info.file_size >= min_size and file_mtime >= target_timestamp:
                total_size += zip_info.file_size

    return total_size

# Download and extract it. Use mv to move all files under folders into an empty folder. Then rename all files replacing each digit with the next. 1 becomes 2, 9 becomes 0, a1b9c.txt becomes a2b0c.txt.
# What does running grep . * | LC_ALL=C sort | sha256sum in bash on that folder show?


async def GA1_16_LINX(zip_file: UploadFile):
    extract_folder = "extracted"
    merged_folder = "merged_folder"

    # Ensure clean directories
    shutil.rmtree(extract_folder, ignore_errors=True)
    shutil.rmtree(merged_folder, ignore_errors=True)
    os.makedirs(extract_folder, exist_ok=True)
    os.makedirs(merged_folder, exist_ok=True)

    # Save uploaded file temporarily
    with NamedTemporaryFile(delete=False) as temp_zip:
        temp_zip.write(await zip_file.read())
        temp_zip_path = temp_zip.name

    # Extract ZIP file
    with zipfile.ZipFile(temp_zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_folder)

    # Move all files from subdirectories into merged_folder
    subprocess.run(
        f'find "{extract_folder}" -type f -exec mv {{}} "{merged_folder}" \\;', shell=True, check=True)

    # Rename files (Shift digits: 1 → 2, 9 → 0)
    os.chdir(merged_folder)
    for file in os.listdir():
        newname = file.translate(str.maketrans("0123456789", "1234567890"))
        if file != newname:
            os.rename(file, newname)

    # Run checksum command
    result = subprocess.run('grep . * | LC_ALL=C sort | sha256sum',
                            shell=True, text=True, capture_output=True)

    # Cleanup temp files
    os.remove(temp_zip_path)

    # Return checksum result
    return result.stdout.strip()


async def GA1_16(zip_file: UploadFile):
    # Use "/tmp/" for Vercel, or local paths when running locally
    print(os.getenv("VERCEL"))
    if not os.getenv("VERCEL"):
        return await GA1_16_LINX(zip_file)
    else:
        return await GA1_16_Vercel("/tmp", zip_file)


async def GA1_16_Vercel(BASE_DIR, zip_file: UploadFile):
    # Use "/tmp/" for Vercel, or local paths when running locally
    extract_folder = os.path.join(BASE_DIR, "extracted")
    merged_folder = os.path.join(BASE_DIR, "merged_folder")

    # Ensure clean directories
    shutil.rmtree(extract_folder, ignore_errors=True)
    shutil.rmtree(merged_folder, ignore_errors=True)
    os.makedirs(extract_folder, exist_ok=True)
    os.makedirs(merged_folder, exist_ok=True)

    # Save uploaded file temporarily
    with NamedTemporaryFile(delete=False, dir=BASE_DIR) as temp_zip:
        temp_zip_path = temp_zip.name

    async with aiofiles.open(temp_zip_path, 'wb') as temp_zip_writer:
        while chunk := await zip_file.read(1024):  # Read in chunks
            await temp_zip_writer.write(chunk)

    # Extract ZIP file
    with zipfile.ZipFile(temp_zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_folder)

    # Move all files from subdirectories into merged_folder
    for root, _, files in os.walk(extract_folder):
        for file in files:
            src_path = os.path.join(root, file)
            dest_path = os.path.join(merged_folder, file)
            shutil.move(src_path, dest_path)

    # Rename files (Shift digits: 1 → 2, 9 → 0)
    for file in os.listdir(merged_folder):
        newname = file.translate(str.maketrans("0123456789", "1234567890"))
        if file != newname:
            shutil.move(os.path.join(merged_folder, file),
                        os.path.join(merged_folder, newname))

    # Change to merged folder for hashing
    os.chdir(merged_folder)

    # Mimic `grep . * | LC_ALL=C sort | sha256sum`
    sorted_lines = []
    for file in sorted(os.listdir(), key=lambda f: f.encode("utf-8")):  # Byte-wise sorting
        async with aiofiles.open(file, 'r', encoding='utf-8', errors='ignore') as f:
            lines = await f.readlines()
            for line in lines:
                if line.strip():  # Ignore empty lines like `grep . *`
                    sorted_lines.append(f"{file}:{line.strip()}")

    sorted_lines.sort(key=lambda x: x.encode("utf-8"))  # Mimic `LC_ALL=C sort`

    # Compute SHA-256 checksum on sorted content
    hash_obj = hashlib.sha256()
    for line in sorted_lines:
        hash_obj.update(line.encode("utf-8"))

    checksum_result = hash_obj.hexdigest()

    # Cleanup temp files
    os.remove(temp_zip_path)

    return checksum_result

# Download and extract it. It has 2 nearly identical files, a.txt and b.txt, with the same number of lines.
# How many lines are different between a.txt and b.txt?


async def GA1_17(question: str, zip_file: UploadFile) -> int:
    files = re.findall(r'\b([^\/\\\s]+?\.[a-zA-Z0-9]+)\b', question)[:2]
    with zipfile.ZipFile(io.BytesIO(await zip_file.read())) as z:
        extracted = {f: z.read(f).decode(errors="ignore").splitlines()
                     for f in files if f in z.namelist()}
    return sum(l1.strip() != l2.strip() for l1, l2 in zip(*extracted.values())) if len(extracted) == 2 else -1

# There is a tickets table in a SQLite database that has columns type, units, and price. Each row is a customer bid for a concert ticket.

# type	units	price
# SILVER	591	1.69
# Bronze	537	1.53
# Gold	771	1.21
# gold	565	1.42
# Bronze	303	0.8
# ...
# What is the total sales of all the items in the "Gold" ticket type? Write SQL to calculate it.


def GA1_18(question: str) -> str:
    """Extracts ticket type from the question and returns the corresponding SQL query dynamically."""
    match = re.search(
        r'What is the total sales of all the items in the\s+"([\w\s-]+)"\s+ticket type', question, re.IGNORECASE)
    ticket_type = match.group(1).strip().lower() if match else None
    return f"SELECT SUM(units * price) AS total_sales FROM tickets WHERE type like '%{ticket_type}%';" if ticket_type else None
