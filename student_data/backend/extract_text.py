import fitz  # PyMuPDF
import os
import re

RAW_PDF_PATH = "../DATA/raw_pdfs"
OUTPUT_TEXT_PATH = "../DATA/extracted_text"

os.makedirs(OUTPUT_TEXT_PATH, exist_ok=True)

def extract_text_from_pdf(pdf_path):
    text = ""
    try:
        doc = fitz.open(pdf_path)
        for page_num, page in enumerate(doc, start=1):
            text += f"\n--- Page {page_num} ---\n"
            text += page.get_text("text")
        doc.close()
    except Exception as e:
        print(f"❌ Error reading {pdf_path}: {e}")
    return text

def clean_basic_text(text):
    noise_keywords = ["Student CMM", "RGMCET", "Developed by", "Copyright", "http", "Go"]
    cleaned_lines = []
    for line in text.split("\n"):
        line = line.strip()
        if not line:
            continue
        if any(keyword in line for keyword in noise_keywords):
            continue
        if re.search(r"\d+/\d+/\d+", line):
            continue
        cleaned_lines.append(line)
    return "\n".join(cleaned_lines)

def process_all_pdfs():
    pdf_files = [f for f in os.listdir(RAW_PDF_PATH) if f.lower().endswith(".pdf")]
    if not pdf_files:
        print("⚠ No PDF files found in DATA/raw_pdfs")
        return
    for pdf_file in pdf_files:
        pdf_path = os.path.join(RAW_PDF_PATH, pdf_file)
        print(f"📄 Processing: {pdf_file}")
        raw_text = extract_text_from_pdf(pdf_path)
        cleaned_text = clean_basic_text(raw_text)
        output_filename = pdf_file.replace(".pdf", ".txt")
        output_path = os.path.join(OUTPUT_TEXT_PATH, output_filename)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(cleaned_text)
        print(f"✅ Saved cleaned text to {output_filename}")
    print("\n🎉 All PDFs processed successfully!")

if __name__ == "__main__":
    process_all_pdfs()
