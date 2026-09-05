import os
import re

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_FOLDER = os.path.join(BASE_DIR, "DATA")
TEXT_FOLDER = os.path.join(DATA_FOLDER, "text")
CHUNK_FOLDER = os.path.join(DATA_FOLDER, "chunks")
STUDENT_INFO_FOLDER = os.path.join(DATA_FOLDER, "chunks")

os.makedirs(CHUNK_FOLDER, exist_ok=True)


def clean_line(line):
    line = line.replace("11 ", "II ")
    line = line.replace("I1 ", "II ")
    line = line.replace("Il ", "II ")
    line = line.replace("Ill ", "III ")
    line = line.replace("B-Tech", "B.Tech")
    line = line.replace("|", "I")
    return line.strip()


for filename in os.listdir(TEXT_FOLDER):

    if filename.endswith(".txt"):

        path = os.path.join(TEXT_FOLDER, filename)

        with open(path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        roll_no = filename.replace(".txt", "")
        semesters = []
        total_backlogs = 0
        total_credits = 0
        final_cgpa = "Not Found"

        # =====================================================
        # 🔥 STEP 1: READ STUDENT INFO FILE
        # =====================================================

        info_path = os.path.join(STUDENT_INFO_FOLDER, f"{roll_no}_student_info.txt")

        student_name = "Not Found"
        father_name = "Not Found"
        branch = "Not Found"
        college = "Not Found"

        if os.path.exists(info_path):
            with open(info_path, "r", encoding="utf-8") as info_file:
                info_content = info_file.read()

                name_match = re.search(r"Student Name:\s*(.*)", info_content)
                father_match = re.search(r"Father Name:\s*(.*)", info_content)
                branch_match = re.search(r"Branch:\s*(.*)", info_content)
                college_match = re.search(r"College:\s*(.*)", info_content)

                if name_match:
                    student_name = name_match.group(1).strip()

                if father_match:
                    father_name = father_match.group(1).strip()

                if branch_match:
                    branch = branch_match.group(1).strip()

                if college_match:
                    college = college_match.group(1).strip()

        # =====================================================
        # 🔥 STEP 2: READ CGPA / SEMESTER DATA
        # =====================================================

        for raw_line in lines:

            line = clean_line(raw_line)

            # Detect semester row
            if "B.Tech" in line and "R20" in line:

                parts = line.split()

                if len(parts) >= 4:
                    try:
                        backlog = int(parts[-1])
                        sgpa = parts[-2]
                        credits = float(parts[-3])

                        if re.match(r"\d+\.\d+", sgpa):

                            sem_name = " ".join(parts[:-3])
                            semesters.append((sem_name, credits, sgpa, backlog))

                            total_backlogs += backlog
                            total_credits += credits

                    except:
                        pass

            # Detect Total row
            if line.startswith("Total"):
                parts = line.split()
                if len(parts) >= 4:
                    total_credits = int(parts[1])
                    final_cgpa = parts[2]
                    total_backlogs = int(parts[3])

        # =====================================================
        # 🔥 STEP 3: CREATE OUTPUT FILE
        # =====================================================

        output = f"Student ID: {roll_no}\n"
        output += f"Student Name: {student_name}\n"
        output += f"Father Name: {father_name}\n"
        output += f"Branch: {branch}\n"
        output += f"College: {college}\n\n"

        output += "Semester-wise:\n"
        output += "---------------------------------\n"

        for sem, credits, sgpa, backlog in semesters:
            output += f"{sem:<30} → Credits: {credits}  CGPA: {sgpa}  Backlogs: {backlog}\n"

        output += "\n"
        output += f"Final CGPA → {final_cgpa}\n"
        output += f"Total Credits → {total_credits}\n"
        output += f"Total Backlogs → {total_backlogs}\n"

        chunk_path = os.path.join(CHUNK_FOLDER, f"{roll_no}_cgpa.txt")

        with open(chunk_path, "w", encoding="utf-8") as f:
            f.write(output)

        print(f"✅ Created {roll_no}_cgpa.txt")

print("\n🔥 CGPA files created successfully with Student Name included!")