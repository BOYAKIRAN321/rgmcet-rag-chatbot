import os
import fitz
import pytesseract
from PIL import Image

# ==============================
# SET TESSERACT PATH (Windows)
# ==============================
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# ==============================
# FIX FOLDER STRUCTURE
# ==============================

# extract.py is inside BACKEND
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DATA_FOLDER = os.path.join(BASE_DIR, "DATA")
MARKS_FOLDER = os.path.join(DATA_FOLDER, "marks")
TEXT_FOLDER = os.path.join(DATA_FOLDER, "text")

os.makedirs(TEXT_FOLDER, exist_ok=True)

print("Reading PDFs from:", MARKS_FOLDER)
print("Saving text files to:", TEXT_FOLDER)

# ==============================
# PROCESS ALL PDFs
# ==============================

for filename in os.listdir(MARKS_FOLDER):

    if filename.lower().endswith(".pdf"):

        pdf_path = os.path.join(MARKS_FOLDER, filename)
        output_file = os.path.join(TEXT_FOLDER, os.path.splitext(filename)[0] + ".txt")

        print(f"\nProcessing: {filename}")

        try:
            doc = fitz.open(pdf_path)
            full_text = ""

            for page_number in range(len(doc)):

                page = doc[page_number]

                # Convert page to high quality image
                pix = page.get_pixmap(dpi=400)
                img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

                # OCR
                text = pytesseract.image_to_string(img, config="--psm 4")

                full_text += f"\n\n===== PAGE {page_number+1} =====\n\n"
                full_text += text

            # Save text file
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(full_text)

            print(f"✅ Saved: {os.path.basename(output_file)}")

        except Exception as e:
            print(f"❌ Error processing {filename}")
            print("Error:", e)

print("\n🎉 All PDFs converted to text successfully!")