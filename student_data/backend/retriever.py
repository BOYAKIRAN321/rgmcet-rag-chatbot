import os
import re
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings

_db = None

def get_vectorstore():
    global _db
    if _db is not None:
        return _db
    possible_paths = [
        "student_data/DATA/faiss_index",
        "DATA/faiss_index",
        "faiss_index",
        "student_data/faiss_index",
        "./student_data/DATA/faiss_index"
    ]
    for path in possible_paths:
        if os.path.exists(os.path.join(path, "index.faiss")):
            try:
                embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
                db = FAISS.load_local(path, embeddings, allow_dangerous_deserialization=True)
                _db = db
                return db
            except:
                continue
    return None

def extract_student_id(query):
    patterns = [
        r'\b\d{2}9[1,5]A[A-Z0-9]{4}\b',
        r'\b\d{5}A\d{4}\b',
        r'\b22\d{2,3}A\d{4}\b',
        r'\b23\d{2,3}A\d{4}\b',
    ]
    qu = query.upper()
    for pat in patterns:
        m = re.search(pat, qu)
        if m:
            return m.group(0).upper()
    return None

def extract_semester(query):
    m = re.search(r'sem(?:ester)?\s*(\d+)', query.lower())
    return int(m.group(1)) if m else None

def detect_intent(query):
    q = query.lower()
    if "fail" in q or "backlog" in q:
        return "failed_subjects"
    if "topper" in q or "highest cgpa" in q:
        return "topper"
    if "total" in q and "student" in q:
        return "total_students"
    if "max" in q and "backlog" in q:
        return "max_backlogs"
    if "father" in q:
        return "father_name"
    if "branch" in q:
        return "branch"
    if "college" in q:
        return "college"
    if "name" in q:
        return "student_name"
    if "detail" in q:
        return "student_details"
    return "general"

def count_total_students():
    try:
        for d in ["student_data/DATA/chunks", "DATA/chunks"]:
            if os.path.exists(d):
                files = os.listdir(d)
                ids = set([f.split('_')[0].upper() for f in files])
                return len(ids)
    except:
        pass
    return "N/A"

def get_topper():
    try:
        from cgpa_calculator import get_all_cgpas
        ranking = get_all_cgpas()
        if not ranking:
            return "No data"
        ranking.sort(key=lambda x: x['cgpa'], reverse=True)
        top = ranking[0]
        msg = f"🏆 Topper: {top['name']} ({top['id']}) - CGPA: {top['cgpa']}\nTop 5:\n"
        for i, r in enumerate(ranking[:5], 1):
            msg += f"{i}. {r['name']} ({r['id']}) - {r['cgpa']}\n"
        return msg
    except Exception as e:
        return f"Error: {e}"

def get_max_backlogs():
    try:
        from cgpa_calculator import get_all_cgpas
        ranking = get_all_cgpas()
        if not ranking:
            return "No data"
        ranking.sort(key=lambda x: x['fails'], reverse=True)
        top = ranking[0]
        return f"Highest Backlogs: {top['name']} ({top['id']}) - {top['fails']}"
    except Exception as e:
        return f"Error: {e}"

def retrieve_docs(query, k=50):
    student_id = extract_student_id(query)
    intent = detect_intent(query)
    db = get_vectorstore()
    all_docs = db.similarity_search(query, k=50) if db else []
    student_docs = []
    sid = None
    if student_id:
        sid = student_id.upper()
        student_docs = [d for d in all_docs if sid in d.page_content.upper() or str(d.metadata.get("student_id","")).upper() == sid]
        if not student_docs:
            for fpath in [f"student_data/DATA/extracted_text/{sid}.txt", f"DATA/extracted_text/{sid}.txt", f"student_data/DATA/text/{sid}.txt"]:
                if os.path.exists(fpath):
                    with open(fpath, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    from langchain_core.documents import Document
                    student_docs = [Document(page_content=content, metadata={"student_id": sid})]
                    break
        if not student_docs:
            chunks_dir = "student_data/DATA/chunks"
            if os.path.exists(chunks_dir):
                for fname in os.listdir(chunks_dir):
                    if fname.upper().startswith(sid):
                        with open(os.path.join(chunks_dir, fname), 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                        from langchain_core.documents import Document
                        student_docs.append(Document(page_content=content, metadata={"student_id": sid}))

    if "fail" in query.lower() or "backlog" in query.lower():
        if not student_id:
            return "❌ Please provide Roll Number"
        if not student_docs:
            return f"❌ {sid} not found"
        fails = []
        for doc in student_docs:
            for line in doc.page_content.split("\n"):
                up = line.upper()
                if "GRADE: F" in up or "GRADE - F" in up or up.strip().endswith(" F") or " FAIL" in up:
                    if len(line.strip()) > 5:
                        fails.append(line.strip())
        if fails:
            uniq = list(dict.fromkeys(fails))
            msg = f"📚 Failed Subjects for {sid}:\n"
            for i, s in enumerate(uniq, 1):
                msg += f"{i}. {s}\n"
            return msg
        else:
            preview = student_docs[0].page_content[:2000]
            return f"Found {sid} but no F tag. Preview:\n{preview}"

    if intent == "topper":
        return get_topper()
    if intent == "total_students":
        return f"Total Students: {count_total_students()}"
    if intent == "max_backlogs":
        return get_max_backlogs()

    if student_docs:
        target = student_docs[0]
        for d in student_docs:
            if "Student Name:" in d.page_content:
                target = d
                break
        content = target.page_content
        name = re.search(r"Student Name:\s*(.*)", content)
        father = re.search(r"Father Name:\s*(.*)", content)
        branch = re.search(r"Branch:\s*(.*)", content)
        college = re.search(r"College:\s*(.*)", content)
        n = name.group(1).strip() if name else "N/A"
        f = father.group(1).strip() if father else "N/A"
        b = branch.group(1).strip() if branch else "N/A"
        c = college.group(1).strip() if college else "N/A"
        if intent == "student_details":
            return f"🆔 ID: {sid}\n👤 Name: {n}\n👨 Father: {f}\n🏫 Branch: {b}\n🎓 College: {c}"
        return target.page_content[:1500]

    return "No data"
