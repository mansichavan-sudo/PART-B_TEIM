from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa  # Library to convert HTML to PDF
from crmapp.models import invoice
from io import BytesIO
from PyPDF2 import PdfReader, PdfWriter
from django.templatetags.static import static

def generate_invoice_pdf(request, invoice_id, action='view'):
    try:
        # Fetch the invoice data from the database
        invoice_data = get_object_or_404(invoice, id=invoice_id)
        logo_path = request.build_absolute_uri(static('images/logo.png'))
        
        # Context to pass to the template
        context = {
            'invoice': invoice_data,
            'logo_path': logo_path
        }

        # Render the PDF using the template
        template = get_template('invoice_generation/invoice_pdf_template.html')  # PDF Template location
        html = template.render(context)

        # Generate the PDF in memory using BytesIO
        pdf_stream = BytesIO()
        pisa_status = pisa.CreatePDF(html, dest=pdf_stream)

        # Check if any errors occurred during PDF generation
        if pisa_status.err:
            return HttpResponse('Error occurred while generating PDF', status=400)
        
        # Move the buffer position to the beginning of the stream
        pdf_stream.seek(0)

        # Create a PdfWriter object to modify the PDF
        pdf_writer = PdfWriter()

        # Load the PDF stream into PdfReader
        pdf_reader = PdfReader(pdf_stream)

        # Copy all pages from reader to writer
        for page_num in range(len(pdf_reader.pages)):
            pdf_writer.add_page(pdf_reader.pages[page_num])

        pdf_writer.encrypt(user_password="", owner_password="admin123", permissions_flag=0b0100)

        # Create response with the encrypted PDF
        response = HttpResponse(content_type='application/pdf')
        
        if action == 'download':
            response['Content-Disposition'] = f'attachment; filename="invoice_{invoice_data.id}.pdf"'
        else:
            response['Content-Disposition'] = f'inline; filename="invoice_{invoice_data.id}.pdf"'
        
        # Write the PDF content to the response
        pdf_writer.write(response)
        
        return response

    except invoice.DoesNotExist:
        return HttpResponse('Invoice not found', status=404)