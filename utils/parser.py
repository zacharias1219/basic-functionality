import requests
from bs4 import BeautifulSoup
import pdfplumber
from docx import Document
from PIL import Image
import pytesseract
from io import BytesIO

def parse_pdf(file):
    with pdfplumber.open(file) as pdf:
        text = ''
        for page in pdf.pages:
            text += page.extract_text()
    return text

def parse_word(file):
    doc = Document(file)
    text = ''
    for para in doc.paragraphs:
        text += para.text + '\n'
    return text

def parse_image(file):
    image = Image.open(file)
    text = pytesseract.image_to_string(image)
    return text

def parse_website(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    text = soup.get_text()
    return text
