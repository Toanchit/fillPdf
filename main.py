import PyPDF2
import fitz  # PyMuPDF
import tabula
from matplotlib.patches import Rectangle
import matplotlib.pyplot as plt
import numpy as np
from tabula import read_pdf
import camelot


def identify_blocks(page):
    text_blocks = []

    # Get blocks from the page
    blocks = page.get_text("dict")["blocks"]

    for b in blocks:
        if b['type'] == 0:  # Text block
            text_blocks.append((b['bbox'][0], b['bbox'][1], b['bbox'][2], b['bbox'][3]))
    # print("number of table in this page is",len(table_blocks))
    return text_blocks


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
    for block in table_blocks:
        rect = Rectangle((block[0], block[1]), block[2] - block[0], block[3] - block[1], linewidth=1, edgecolor='b', facecolor='none')
        ax.add_patch(rect)

    # Save the plot to a file
    plt.savefig("blocks_plot.png")

    # Show the image with blocks
    plt.show()
def optimizeTable(text_blocks,table_blocks,noEdge):
    tempText_blocks =[]
    for text in text_blocks:
        isOk = True
        for table in table_blocks:
            count =0
            if text[0]>table[0] and text[0]<table[2]:
                count = count+1
            if text[2] > table[0] and text[2]< table[2]:
                count = count + 1
            if text[1]>table[1] and text[1]<table[3]:
                count = count+1
            if text[3]>table[1] and text[3]<table[3]:
                count = count+1
            if count>noEdge:
                isOk=False
                break
        if isOk == True:
            tempText_blocks.append(text)
    return tempText_blocks
def optimize(text_blocks,table_blocks):
    tempText_blocks =[]
    for text in text_blocks:
        isOk = True
        left = text[0]
        top = text[1]
        right = text[2]
        bottom = text[3]
        for table in table_blocks:
            count =0
            if text[0]>(table[0]-2) and text[0]<(table[2]+2): #the number 2 means the text area really is inside the tabel area
                count = count+1
                if text[2] < table[2]:
                    count = count +1
                elif (text[1]>table[1] and text[1] < table[3]) or (text[3]>table[1] and text[3]<table[3]) or (table[1] > text[1] and table[1] < text[3]) or (table[3] > text[1] and table[3] < text[3]):
                    left = table[2]+2

            if text[2] >(table[0]-2) and text[2] < (table[2]+2):
                count = count + 1
                if text[0] > table[0]:
                    count = count +1
                elif (text[1] > table[1]+2 and text[1] < table[3]-2) or (text[3] > table[1]+2 and text[3] < table[3]-2) or (table[1] > text[1]+2 and table[1] < text[3]-2) or (table[3] > text[1]+2 and table[3] < text[3]-2):
                    right = table[0]-2

        if isOk == True:
            tempText_blocks.append((left,top,right,bottom))
    return tempText_blocks


def main(pdf_file):
    # Open the PDF file
    with open(pdf_file, "rb") as file:
        pdf_reader = PyPDF2.PdfReader(file)
        i =0
        # Iterate through each page
        for page_number in range(len(pdf_reader.pages)):
            # if page_number != 8 :
            #     continue
            # Open the PDF page using fitz
            pdf_document = fitz.open(pdf_file)
            page = pdf_document[page_number]
            table_blocks = []

            # Identify text and table blocks
            text_blocks = identify_blocks(page)
            df = read_pdf(pdf_file, pages=page_number+1,multiple_tables=True,output_format='json') #need add 1 in the field pages because the pages start from 1
            print("number of table in this page is ", len(df))
            for tableFrame in df:
                # print(tableFrame)
                top = tableFrame['top']
                left = tableFrame['left']
                right = tableFrame['right']
                bottom = tableFrame['bottom']
                table_blocks.append((left,top,right,bottom))
            # Print the blocks
            # print('text_blocks:', text_blocks)
            # print('table_blocks:', table_blocks)
            table_blocks = optimizeTable(table_blocks,table_blocks,1) #to remove all of area totally inside another area
            text_blocks = optimizeTable(text_blocks, text_blocks, 3) #to remove all of area totally inside another area
            text_blocks= optimizeTable(text_blocks,table_blocks,3)  #to remove all of area totally inside another area
            table_blocks = optimize(table_blocks,text_blocks) #to minimize the table area that is overlapped by a part of the text area
            # Print the blocks
            # print('table_blocks:', table_blocks)
            # print('text_blocks:', text_blocks)
            # # Draw the blocks
            draw_blocks(page, text_blocks, table_blocks)
            i =i+1
            # print('table_blocks:',table_blocks)

if __name__ == "__main__":
    pdf_file = "profit-and-loss-statement.pdf"  # Replace with your PDF file path profit-and-loss-statement.pdf crowe.pdf
    main(pdf_file)
    # df = read_pdf(pdf_file,multiple_tables=True)
    # print("number of table in this page is ",len(df))
