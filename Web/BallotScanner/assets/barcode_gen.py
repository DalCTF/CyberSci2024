import barcode
from barcode.writer import ImageWriter
import fitz
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import ImageReader
from PIL import Image
import requests

def generate_barcode(data, output_image):
    """
    Generates a Code 128 barcode image file.
    :param data: The alphanumeric data for the barcode
    :param output_image: The filename to save the barcode image (without extension)
    :return: Path to the saved barcode image
    """
    barcode_type = barcode.get_barcode_class('code39')
    barcode_obj = barcode_type(data, writer=ImageWriter())
    return barcode_obj.save(output_image)

pdf_file = "/home/kali/cybersci/temp_document.pdf"
def create_document_as_png(barcode_image, output_png):
    """
    Creates a document with a barcode, title, and checkboxes, and saves it as a PNG file.
    :param barcode_image: The path to the barcode image file
    :param output_png: The name of the output PNG file
    """
    # Create a PDF canvas first
    
    c = canvas.Canvas(pdf_file, pagesize=letter)
    
    # Set font for the title
    c.setFont("Helvetica-Bold", 20)
    c.drawString(100, 700, "Advance Polling")
    c.drawString(100, 675, "Precinct 65916")
    
    # Draw the barcode image
    c.drawImage(barcode_image, 300, 650, width=200, height=50)
    
    # Add barcode data below the barcode
    c.setFont("Helvetica", 12)
    
    # Draw a vertical line to separate sections
    c.line(300, 500, 300, 100)
    
    # Add checkbox items
    items_left = ["Onion", "Carrot", "Potato","Cheese"]
    checked_item_left = ["Peas"]
    items_right = ["Tomato", "Fennel", "Parsnip", "Broccoli", "Turnip"]

    c.setFont("Helvetica-Bold", 14)
    
    # Draw left column
    y = 600
    for item in items_left:
        c.rect(100, y, 15, 15)  # Draw checkbox
        c.drawString(125, y, item)
        y -= 40

    for checked_item in checked_item_left:
        c.rect(100, y, 15, 15, fill=1)  # Draw checkbox
        c.drawString(125, y, checked_item)
        y -= 40
    
    # Draw right column
    y = 600
    for item in items_right:
        c.rect(320, y, 15, 15)  # Draw checkbox
        c.drawString(345, y, item)
        y -= 40
    
    # Save the PDF canvas
    c.save()

def pdf_to_png(pdf_path, output_folder):
    doc = fitz.open(pdf_path)

    for page_index in range(len(doc)):
        page = doc.load_page(page_index)
        pix = page.get_pixmap(dpi=300)  # Adjust DPI as needed
        pix.save(f"{output_folder}/page_{page_index}.png")

def upload_file(file_path, url="http://10.0.2.41/scan"):
    """Uploads a file to the specified URL.

    Args:
        file_path (str): Path to the file to upload.
        url (str, optional): Target URL for the upload. Defaults to "http://10.0.2.41/scan".
    """

    files = {
        'ballotimage': open(file_path, 'rb')
    }

    headers= {
        "Content-Type": "image/png"
    }

    response = requests.post(url, files=files, headers=headers)
    return response

# Example Usage
if __name__ == "__main__":
    # Step 1: Generate the barcode
    barcode_data = "65916-000001"
    barcode_image_file = "barcode_image.png"
    barcode_path = generate_barcode(barcode_data, barcode_image_file)

    # Step 2: Create the PNG document
    png_output_file = "polling_precinct.png"
    create_document_as_png(barcode_path, png_output_file)
    pdf_to_png(pdf_file, "output_images/")
    #resp = upload_file("output_images/page_0.png")
    #print(resp.text)

