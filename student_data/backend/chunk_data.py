import os
import re
import json

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEXT_PATH = os.path.join(BASE_DIR, "DATA", "extracted_text")
CHUNK_PATH = os.path.join(BASE_DIR, "DATA", "chunks")
META_PATH = os.path.join(BASE_DIR, "DATA", "metadata")

os.makedirs(CHUNK_PATH, exist_ok=True)
os.makedirs(META_PATH, exist_ok=True)

def is_noise(line):
    noise_keywords = ["Student CMM", "Regd. No.", "Go", "Developed by", "Copyright", "http", "RGMCET", "--- Page"]
    return any(word in line for word in noise_keywords)

def extract_student_info(text):
    name = re.search(r"Name\s*:?\s*(.+)", text)
    father = re.search(r"Father Name\s*:?\s*(.+)", text)
    regd = re.search(r"Regd\.?\s*No\.?\s*:?\s*(\w+)", text)
    return {
        "name": name.group(1).strip() if name else "Unknown",
        "father": father.group(1).strip() if father else "Unknown",
        "regd_no": regd.group(1).strip() if regd else ""
    }

def clean_lines(text):
    return [line.strip() for line in text.split("\n") if line.strip()]

def is_year(line):
    return line in ["I Year", "II Year", "III Year"]

def parse_subjects(lines, start_index):
    subjects = []
    i = start_index
    while i < len(lines):
        line = lines[i]
        if is_year(line):
            break
        if is_noise(line):
            i += 1
            continue
        if re.match(r"[A-Z]", line) and not re.match(r"^\d+$", line):
            subject = line
            j = i + 1
            while j < len(lines) and not re.match(r"^0", lines[j]):
                subject += " " + lines[j]
                j += 1
            try:
                parts = lines[j].split()
                if len(parts) == 2:
                    grade = parts[1]
                    credits = lines[j + 2]
                    step = 3
                else:
                    grade = lines[j + 1]
                    credits = lines[j + 3]
                    step = 4
                if re.match(r"\d+(\.\d+)?", credits):
                    subjects.append({"subject": subject.title(), "grade": grade, "credits": credits})
                    i = j + step
                    continue
            except:
                pass
        i += 1
    return subjects, i

def split_two_column_subjects(subjects, year):
    sem1, sem2 = [], []
    for idx, sub in enumerate(subjects):
        (sem1 if idx % 2 == 0 else sem2).append(sub)
    return {f"{year} I Sem": sem1, f"{year} II Sem": sem2}

def process_student_file(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        raw_text = f.read()
    student_info = extract_student_info(raw_text)
    lines = clean_lines(raw_text)
    student_id = student_info["regd_no"] or os.path.basename(filepath).replace(".txt", "")
    semester_data = {}
    i = 0
    while i < len(lines):
        if is_year(lines[i]):
            year = lines[i]
            i += 1
            while i < len(lines) and not re.match(r"[A-Z]", lines[i]):
                i += 1
            subjects, i = parse_subjects(lines, i)
            semester_data.update(split_two_column_subjects(subjects, year))
        else:
            i += 1
    info_content = f"""Student Information
-------------------
Student ID: {student_id}
Student Name: {student_info['name']}
Father Name: {student_info['father']}
Branch: CSE & Business Systems
College: Rajeev Gandhi Memorial College of Engineering and Technology"""
    info_filename = f"{student_id}_student_info.txt"
    with open(os.path.join(CHUNK_PATH, info_filename), "w", encoding="utf-8") as f:
        f.write(info_content)
    with open(os.path.join(META_PATH, info_filename.replace(".txt", ".json")), "w") as mf:
        json.dump({"student_id": student_id, "type": "student_info", "branch": "CSE & Business Systems", "college": "RGMCET"}, mf)
    for sem, subjects in semester_data.items():
        if not subjects:
            continue
        subject_lines = "\n".join(f"{idx+1}. {s['subject']} — Grade: {s['grade']} — Credits: {s['credits']}" for idx, s in enumerate(subjects))
        content = f"""Student ID: {student_id}
Student Name: {student_info['name']}
Semester: {sem}

Subjects:
{subject_lines}
"""
        filename = f"{student_id}_{sem.replace(' ', '_')}.txt"
        with open(os.path.join(CHUNK_PATH, filename), "w", encoding="utf-8") as f:
            f.write(content)
        with open(os.path.join(META_PATH, filename.replace(".txt", ".json")), "w") as mf:
            json.dump({"student_id": student_id, "semester": sem, "branch": "CSE & Business Systems", "college": "RGMCET"}, mf)

def process_all_students():
    files = [f for f in os.listdir(TEXT_PATH) if f.endswith(".txt")]
    if not files:
        print("⚠ No extracted text files found.")
        return
    for file in files:
        print(f"📄 Processing {file}")
        process_student_file(os.path.join(TEXT_PATH, file))
    print("\n🎉 Smart chunking completed successfully!")

if __name__ == "__main__":
    process_all_students()
