import os
import re
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FAISS_PATH = os.path.join(BASE_DIR, "DATA", "faiss_index")

def load_vectorstore():
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )
    return FAISS.load_local(
        FAISS_PATH,
        embeddings,
        allow_dangerous_deserialization=True
    )

try:
    db = load_vectorstore()
    all_docs = list(db.docstore._dict.values())
except Exception as e:
    print(f"⚠️ FAISS load failed: {e}")
    db = None
    all_docs = []

def count_total_students():
    student_ids = set()
    for doc in all_docs:
        sid = doc.metadata.get("student_id")
        if sid:
            student_ids.add(str(sid).upper())
    return len(student_ids)

def extract_student_id(query):
    query = query.upper().replace(" ", "")
    match = re.search(r'(22|23)\d{3}[A-Z]\d{4}', query)
    return match.group(0) if match else None

def extract_student_name(query):
    q = query.lower()
    for doc in all_docs:
        if doc.metadata.get("type") == "student_info":
            lines = doc.page_content.split("\n")
            name_line = [l for l in lines if "Student Name:" in l]
            if not name_line:
                continue
            full_name = name_line[0].split("Student Name:")[-1].strip().lower()
            name_parts = full_name.split()
            for part in name_parts:
                if len(part) > 3 and part in q:
                    return doc.metadata.get("student_id")
    return None

def extract_semester(query):
    q = query.lower().replace(" ", "").replace("-", "")
    mapping = {
        "1-1": "I Year I Sem", "1-2": "I Year II Sem",
        "2-1": "II Year I Sem", "2-2": "II Year II Sem",
        "3-1": "III Year I Sem", "3-2": "III Year II Sem",
        "firstyearfirstsem": "I Year I Sem",
        "secondyearfirstsem": "II Year I Sem",
        "secondyearsecondsem": "II Year II Sem",
        "thirdyearfirstsem": "III Year I Sem",
        "thirdyearsecondsem": "III Year II Sem",
    }
    for key, val in mapping.items():
        if key in q:
            return val
    return None

def detect_intent(query):
    q = query.lower()
    if "father" in q:
        return "father_name"
    if ("student" in q and "name" in q) or "details" in q:
        return "student_details"
    if "branch" in q:
        return "branch"
    if "college" in q:
        return "college"
    if "subject" in q or "course" in q:
        return "subjects"
    if "total students" in q or "how many students" in q:
        return "total_students"
    if "ranking" in q or "rank" in q:
        return "ranks"
    if "topper" in q or "top rank" in q or "highest cgpa" in q:
        return "topper"
    if "maximum backlog" in q or "most backlogs" in q or "more backlogs" in q:
        return "max_backlogs"
    if "how many backlogs" in q:
        return "backlog_count"
    if "cgpa" in q:
        return "cgpa"
    if "performance" in q or "analysis" in q:
        return "performance"
    marks_keywords = ["marks", "grade", "result", "score", "academic"]
    if any(word in q for word in marks_keywords):
        return "all_marks"
    return "general"

def get_topper():
    """Calculate topper from all docs - NO similarity search"""
    try:
        from cgpa_calculator import get_all_cgpas
        ranking = get_all_cgpas(all_docs)
        if not ranking:
            return "❌ No CGPA data found. Check if chunks have Grade/Credits format."
        
        top = ranking[0]
        msg = f"🏆 Topper of the class: {top['name']} ({top['id']}) - CGPA: {top['cgpa']}\n"
        msg += f"   Credits: {top['credits']}, Backlogs: {top['fails']}\n\n"
        msg += "📊 Top 5 Ranking:\n"
        for i, r in enumerate(ranking[:5], 1):
            msg += f"{i}. {r['name']} ({r['id']}) - CGPA: {r['cgpa']}\n"
        msg += f"\nTotal Students: {len(ranking)}"
        return msg
    except Exception as e:
        import traceback
        traceback.print_exc()
        return f"Error in get_topper: {e}"

def get_max_backlogs():
    try:
        from cgpa_calculator import get_all_cgpas
        ranking = get_all_cgpas(all_docs)
        if not ranking:
            return "No data"
        ranking.sort(key=lambda x: x['fails'], reverse=True)
        top = ranking[0]
        msg = f"📉 Highest Backlogs: {top['name']} ({top['id']}) - {top['fails']} backlogs\n\n"
        for i, r in enumerate(ranking[:5], 1):
            msg += f"{i}. {r['name']} ({r['id']}) - {r['fails']} backlogs\n"
        return msg
    except Exception as e:
        return f"Error: {e}"

def get_class_ranking(top_n=None):
    return get_topper()

def retrieve_docs(query, k=10):
    student_id = extract_student_id(query)
    semester = extract_semester(query)
    intent = detect_intent(query)
    if not student_id:
        student_id = extract_student_name(query)
    
    print(f"student id, semester, intent: {student_id}, {semester}, {intent}")
    
    # Handle global intents FIRST
    if intent == "topper":
        return get_topper()
    if intent == "total_students":
        return f"📊 Total Students in database: {count_total_students()}"
    if intent == "max_backlogs":
        return get_max_backlogs()
    if intent == "ranks":
        return get_class_ranking()
    
    if student_id:
        sid = student_id.upper()
        student_docs = [doc for doc in all_docs if str(doc.metadata.get("student_id", "")).upper() == sid]

        if intent in ["student_details", "branch", "college", "student_name", "father_name"]:
            for doc in all_docs:
                if str(doc.metadata.get("student_id", "")).upper() == sid and doc.metadata.get("type") == "student_info":
                    content = doc.page_content
                    name_match = re.search(r"Student Name:\s*(.*)", content)
                    father_match = re.search(r"Father Name:\s*(.*)", content)
                    branch_match = re.search(r"Branch:\s*(.*)", content)
                    college_match = re.search(r"College:\s*(.*)", content)
                    student_name = name_match.group(1).strip() if name_match else "Not available"
                    father_name = father_match.group(1).strip() if father_match else "Not available"
                    branch = branch_match.group(1).strip() if branch_match else "Not available"
                    college = college_match.group(1).strip() if college_match else "Not available"

                    if intent == "student_details":
                        return f"🎓 Student ID: {sid}\n👤 Name: {student_name}\n👨 Father: {father_name}\n🏫 Branch: {branch}\n🏛 College: {college}"
                    if intent == "student_name":
                        return f"👤 Name: {student_name}"
                    if intent == "father_name":
                        return f"👨 Father Name: {father_name}"
                    if intent == "branch":
                        return f"🏫 Branch: {branch}"
                    if intent == "college":
                        return f"🏛 College: {college}"
            return "❌ Student details not found."

        if intent == "all_marks":
            semester_docs = [d for d in student_docs if d.metadata.get("semester")]
            if not semester_docs:
                return "❌ No semester data found."
            output = f"📘 All Semester Marks for {sid}:\n"
            for d in semester_docs:
                sem = d.metadata.get("semester")
                subjects = d.page_content.split("\n")[1:]
                output += f"\n🎓 {sem}\n"
                for i, sub in enumerate(subjects, 1):
                    output += f"{i}. {sub}\n"
            return output

        if intent == "subjects":
            if semester:
                return [doc for doc in student_docs if doc.metadata.get("semester") == semester]
            return [doc for doc in student_docs if doc.metadata.get("semester")]

        if student_docs:
            return student_docs
        return "❌ Student data not found."

    if semester:
        return [doc for doc in all_docs if doc.metadata.get("semester") == semester][:1]

    if intent in ["college", "branch"]:
        for doc in all_docs:
            if doc.metadata.get("type") == "student_info":
                return doc.page_content
        return "Student information not found."

    if db is None:
        return "general"
    
    return db.similarity_search(query, k=k)
