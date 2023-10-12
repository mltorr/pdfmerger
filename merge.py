import streamlit as st
from io import BytesIO
import zipfile
import fitz
import os

# Setting page title and header
st.set_page_config(
    page_title="PDF Merger",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded",
)
st.title("PDF Merger")

# Function to get reference number from a PDF filename
def get_ref_num(pdf_file):
    return int(pdf_file.split(".")[0])

# Function to process and modify the PDFs
def process_pdfs(zip_file):
    temp_dir = "temp_pdfs"
    os.makedirs(temp_dir, exist_ok=True)

    with zipfile.ZipFile(zip_file, "r") as zip_ref:
        zip_ref.extractall(temp_dir)

    pdf_files = [f for f in os.listdir(temp_dir) if f.lower().endswith(".pdf")]
    pdf_files.sort(key=get_ref_num)  # Sort by reference number

    result = fitz.open()
    total_files = len(pdf_files)

    progress_bar = st.progress(0)
    progress_text = st.empty()

    for i, pdf_file in enumerate(pdf_files):
        doc = fitz.open(os.path.join(temp_dir, pdf_file))
        ref_num = get_ref_num(pdf_file)

        for page in doc:
            page.clean_contents(False)
            rect = fitz.Rect(5, 5, 150, 22)  # Rectangle (left, top, right, bottom) in pixels
            text = f"BTG Reference: {ref_num}"
            page.draw_rect(rect, color=(0, 0, 1))
            rc = page.insert_textbox(rect, text, color=(0, 0, 1))

        result.insert_pdf(doc)

        # Update progress bar
        progress = (i + 1) / total_files
        progress_bar.progress(progress)
        progress_text.text(f"Processing PDF {i+1}/{total_files}")

    if result.page_count > 0:
        result_file = "consolidated.pdf"
        result.save(result_file)
        st.success(f"Processing complete! Click below to download the consolidated PDF.")
        return result_file
    else:
        st.error("No valid PDF pages to save.")
        return None

# Main part of the app
uploaded_file = st.file_uploader("Upload a ZIP file containing PDFs", type=["zip"])
if uploaded_file:
    if st.button("Process PDFs"):
        result_file = process_pdfs(uploaded_file)
        if result_file:
            with open(result_file, "rb") as pdf_file:
                PDFbyte = pdf_file.read()
            st.download_button(
                label="Download Consolidated PDF",
                data=PDFbyte,
                file_name="Consolidated.pdf",
                mime="application/octet-stream",
            )

# Clean up temporary directory
if os.path.exists("temp_pdfs"):
    for file in os.listdir("temp_pdfs"):
        os.remove(os.path.join("temp_pdfs", file))
    os.rmdir("temp_pdfs")
