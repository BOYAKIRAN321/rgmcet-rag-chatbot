# cgpa_calculator.py - FIXED
import re
from collections import defaultdict

GRADE_POINTS = {
    "O": 10, "A+": 9, "A": 8, "B+": 7,
    "B": 6, "C": 5, "D": 4, "F": 0
}

# Handles both em-dash and hyphen
GRADE_REGEX = re.compile(
    r"Grade:\s*(O|A\+|A|B\+|B|C|D|F)\s*[—\-]\s*Credits:\s*([\d.]+)",
    re.IGNORECASE
)

# Fallback for old format "Grade: A - Credits: 3" or "Grade: 3 - Credits: 6" (skip numeric)
GRADE_REGEX_FALLBACK = re.compile(
    r"Grade:\s*([A-Z\+]+)\s*[-—]\s*Credits:\s*([\d.]+)",
    re.IGNORECASE
)

def calculate_cgpa_and_fails(docs, semester=None):
    total_points = 0.0
    total_credits = 0.0
    failed_subjects = 0

    for doc in docs:
        if semester and doc.metadata.get("semester") != semester:
            continue
        # try primary regex
        matches = GRADE_REGEX.findall(doc.page_content)
        if not matches:
            matches = GRADE_REGEX_FALLBACK.findall(doc.page_content)
        
        for grade, credits in matches:
            grade = grade.upper().strip()
            # skip if grade is numeric like "3" (old noisy format)
            if grade not in GRADE_POINTS:
                continue
            try:
                credits = float(credits)
            except:
                continue

            if grade == "F":
                failed_subjects += 1

            total_points += GRADE_POINTS[grade] * credits
            total_credits += credits

    if total_credits == 0:
        return None, failed_subjects, 0

    return round(total_points / total_credits, 2), failed_subjects, total_credits

def calculate_all_semester_gpa(docs):
    semester_map = defaultdict(list)
    for doc in docs:
        sem = doc.metadata.get("semester")
        if sem:
            semester_map[sem].append(doc)

    results = {}
    for sem, sem_docs in semester_map.items():
        gpa, fails, credits = calculate_cgpa_and_fails(sem_docs)
        results[sem] = {"gpa": gpa, "fails": fails, "credits": credits}
    return results

def get_all_cgpas(all_docs):
    """Returns list of dicts: [{'id':..., 'name':..., 'cgpa':...}]"""
    student_ids = set([str(d.metadata.get("student_id","")).upper() for d in all_docs if d.metadata.get("student_id")])
    ranking = []
    for sid in student_ids:
        student_docs = [d for d in all_docs if str(d.metadata.get("student_id","")).upper() == sid]
        # get name
        name = sid
        for d in student_docs:
            if d.metadata.get("type") == "student_info":
                m = re.search(r"Student Name:\s*(.*)", d.page_content)
                if m:
                    name = m.group(1).strip()
                    break
        cgpa, fails, credits = calculate_cgpa_and_fails(student_docs)
        if cgpa is not None:
            ranking.append({"id": sid, "name": name, "cgpa": cgpa, "fails": fails, "credits": credits})
    ranking.sort(key=lambda x: x["cgpa"], reverse=True)
    return ranking
