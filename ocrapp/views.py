import pytesseract
from PIL import Image
import re
from django.shortcuts import render, redirect
from django.http import JsonResponse
from .models import VisitingCard
from .forms import VisitingCardForm
from pdf2image import convert_from_bytes
import os
from io import BytesIO
from django.contrib import messages
from crmapp import views

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def extract_text_from_image(image_path):
    # Extract text from image using Tesseract.
    image = Image.open(image_path)
    text = pytesseract.image_to_string(image)
    return text

def extract_text_from_pdf_bytes(pdf_file_bytes):
    # Convert PDF (as bytes) to images and extract text
    images = convert_from_bytes(pdf_file_bytes)
    extracted_text = ''
    
    for image in images:
        extracted_text += pytesseract.image_to_string(image)
    
    return extracted_text

def scan_visiting_card(request):
    if request.method == 'POST':
        form = VisitingCardForm(request.POST, request.FILES)
        if form.is_valid():
            # Save uploaded file temporarily without committing
            card = form.save(commit=False)
            uploaded_file = request.FILES['file']

            file_extension = os.path.splitext(uploaded_file.name)[1].lower()

            # Initialize extracted_text as None
            extracted_text = None

            # Check if the file is an image or PDF
            if file_extension in ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']:
                # Save the image to the card_image field
                card.card_image = uploaded_file
                card.save()  # Save the instance first to get a valid file path
                extracted_text = extract_text_from_image(card.card_image.path)

            elif file_extension == '.pdf':
                # For PDFs, read the file as bytes and convert it
                pdf_file_bytes = uploaded_file.read()
                extracted_text = extract_text_from_pdf_bytes(pdf_file_bytes)

            else:
                # If unsupported file type, return error response
                return JsonResponse({'success': False, 'error': 'Unsupported file format'}, status=400)

            if extracted_text:
                # Extract details from the text
                name = extract_name(extracted_text)
                email = extract_email(extracted_text)
                phone = extract_phone(extracted_text)
                company = extract_company(extracted_text)
                address = extract_address(extracted_text)

                # Update the VisitingCard model with the extracted data
                card.name = name
                card.email = email
                card.phone = phone
                card.company = company
                card.address = address
                card.save()  # Final save after filling in all fields

                # If everything was successful, send the success message
                messages.success(request, 'Visiting card uploaded and processed successfully!')

                # Render the index.html template and pass the success message
                return redirect('/index')

            else:
                # If text extraction failed, send an error response
                return JsonResponse({'success': False, 'error': 'Failed to extract text from the file'}, status=400)

    else:
        form = VisitingCardForm()

    return render(request, 'ocrapp/scan.html', {'form': form})



def extract_company(text):
    # Using a pattern to extract the company name. Assuming it appears in all caps.
    company_pattern = r'(?<=\n)([A-Z\s&]+)(?=\n)'
    matches = re.findall(company_pattern, text)
    
    if matches:
        return matches[0].strip()  # Return the first match and strip any extra spaces
    return None

def extract_email(text):
    email_pattern = r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+'
    email_match = re.search(email_pattern, text)
    return email_match.group(0) if email_match else None

def extract_phone(text):
    phone_pattern = r'(\+91\s?\d{5}\s?\d{5})'
    phone_match = re.search(phone_pattern, text)
    return phone_match.group(0) if phone_match else None

def extract_name(text):
    lines = text.splitlines()

    for line in lines:
        # Check for a line with exactly two words in uppercase
        if line.isupper() and len(line.split()) == 2:
            if "CEO" not in line and "FOUNDER" not in line:
                return line.strip()
    
    return "Name not found"


def extract_address(text):
    match = re.search(r'@([\s\S]*?)(?=©|\Z)', text)
    if match:
        # Clean up whitespace and extra characters
        address = match.group(1).strip().replace("\n", " ")
        return address
    return None