import PyPDF2
import fitz  # PyMuPDF
import tabula
from matplotlib.patches import Rectangle
import matplotlib.pyplot as plt
import numpy as np

def identify_blocks(page):
    text_blocks = []
    table_blocks = []

    # Get blocks from the page
    blocks = page.get_text("dict")["blocks"]

    for b in blocks:
        if b['type'] == 0:  # Text block
            text_blocks.append((b['bbox'][0], b['bbox'][1], b['bbox'][2], b['bbox'][3]))
        elif b['type'] == 1:  # Table block
            table_blocks.append((b['bbox'][0], b['bbox'][1], b['bbox'][2], b['bbox'][3]))

    return text_blocks, table_blocks


def draw_blocks(page, text_blocks, table_blocks):
    # Load the page image
    pix = page.get_pixmap()

    # Convert pixmap to numpy array
    img_data = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, pix.n)

    # Create figure and axes
    fig, ax = plt.subplots(figsize=(8, 8))

    # Draw the image
    ax.imshow(img_data)

    # Draw text blocks
    for block in text_blocks:
        rect = Rectangle((block[0], block[1]), block[2] - block[0], block[3] - block[1], linewidth=1, edgecolor='r', facecolor='none')
        ax.add_patch(rect)

    # Draw table blocks
    # for block in table_blocks:
    #     rect = Rectangle((block[0], block[1]), block[2] - block[0], block[3] - block[1], linewidth=1, edgecolor='b', facecolor='none')
    #     ax.add_patch(rect)

    # Save the plot to a file
    plt.savefig("blocks_plot.png")

    # Show the image with blocks
    plt.show()


def main(pdf_file):
    # Open the PDF file
    i=0
    with open(pdf_file, "rb") as file:
        pdf_reader = PyPDF2.PdfReader(file)

        # Iterate through each page
        for page_number in range(len(pdf_reader.pages)):
            if i ==15:
                break
            i=i+1
            # Open the PDF page using fitz
            pdf_document = fitz.open(pdf_file)
            page = pdf_document[page_number]

            # Identify text and table blocks
            text_blocks, table_blocks = identify_blocks(page)

            # Print the blocks
            print('text_blocks:', text_blocks)
            print('table_blocks:', table_blocks)

            # Draw the blocks
            draw_blocks(page, text_blocks, table_blocks)
            print('table_blocks:',table_blocks)

if __name__ == "__main__":
    pdf_file = "crowe.pdf"  # Replace with your PDF file path
    main(pdf_file)
