from ga1 import GA1_2, GA1_3, GA1_4, GA1_5, GA1_6, GA1_7, GA1_8, GA1_9, GA1_10, GA1_11, GA1_12, GA1_14, GA1_15, GA1_16, GA1_17, GA1_18
from ga2 import GA2_2, GA2_4, GA2_5, GA2_9_old
from ga5 import GA5_1, GA5_2, GA5_3, GA5_4, GA5_5, GA5_6, GA5_7, GA5_8, GA5_10
from ga2_9 import read_student_data, get_students
import asyncio
import subprocess

async def fetch_answer(task_id, question, file_path):
    # if task_id == 'GA1.1': extract from excel
    if task_id == 'GA1.2':
        answer = GA1_2(question)
    if task_id == 'GA1.3':
        answer = await GA1_3(file_path)
    if task_id == 'GA1.4':
        answer = GA1_4(question)
    if task_id == 'GA1.5':
        answer = GA1_5(question)
    if task_id == 'GA1.6':
        answer = GA1_6(question, file_path)
    if task_id == 'GA1.7':
        answer = GA1_7(question)
    if task_id == 'GA1.8':
        answer = GA1_8(question, file_path)
    if task_id == 'GA1.9':
        answer = GA1_9(question)
    if task_id == 'GA1.10':
        answer = await GA1_10(file_path)
    if task_id == 'GA1.11':
        answer = GA1_11(question, file_path)
    if task_id == 'GA1.12':
        answer = await GA1_12(question, file_path)
    # if task_id == 'GA1.13': extract from excel
    if task_id == 'GA1.14':
        answer = await GA1_14(question, file_path)
    if task_id == 'GA1.15':
        answer = await GA1_15(question, file_path)
    if task_id == 'GA1.16':
        answer = await GA1_16(file_path)
    if task_id == 'GA1.17':
        answer = await GA1_17(question, file_path)
    if task_id == 'GA1.18':
        answer = GA1_18(question)
    # if task_id == 'GA2.1': extract from excel
    if task_id == 'GA2.2':
        answer = await GA2_2(file_path)
    # if task_id == 'GA2.3': extract from excel
    if task_id == 'GA2.4':
        answer = await GA2_4(question)
    if task_id == 'GA2.5':
        answer = await GA2_5(file_path)
    # if task_id == 'GA2.6': extract from excel
    # if task_id == 'GA2.7': extract from excel
    # if task_id == 'GA2.8': extract from excel
    if task_id == 'GA2.9':
        port = 10000
        subprocess.Popen(["uvicorn", "ga2_9:app", "--host","0.0.0.0", "--port", str(port)])
        # GA2_9_old(file_path,port)
        # process.terminate()
        answer = f"http://127.0.0.1:{port}/api"
    # if task_id == 'GA2.10': extract from excel
    if task_id == 'GA5.1':
        answer = GA5_1(question, file_path)
    if task_id == 'GA5.2':
        answer = GA5_2(question, file_path)
    if task_id == 'GA5.3':
        answer = GA5_3(question, file_path)
    if task_id == 'GA5.4':
        answer = GA5_4(question, file_path)
    if task_id == 'GA5.5':
        answer = GA5_5(question, file_path)
    if task_id == 'GA5.6':
        answer = GA5_6(question, file_path)
    if task_id == 'GA5.7':
        answer = GA5_7(question, file_path)
    if task_id == 'GA5.8':
        answer = GA5_8(question)
    # if task_id == 'GA5.9': extract from excel
    if task_id == 'GA5.10':
        answer = GA5_10(question, file_path)
    return answer
