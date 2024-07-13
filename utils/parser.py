# utils/parser.py
import pdfplumber
from docx import Document
from PIL import Image
import pytesseract
import requests
from bs4 import BeautifulSoup

def parse_pdf(file):
    with pdfplumber.open(file) as pdf:
        text = ''.join(page.extract_text() for page in pdf.pages)
    return text

def parse_word(file):
    doc = Document(file)
    text = ''.join(para.text for para in doc.paragraphs)
    return text

def parse_image(file):
    image = Image.open(file)
    text = pytesseract.image_to_string(image)
    return text

def parse_website(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    return soup.get_text()
