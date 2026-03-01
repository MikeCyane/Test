import fitz
import sys

def analyze_pdf(filepath):
    print(f"Analyzing {filepath}")
    doc = fitz.open(filepath)
    # Check first 5 pages for highlights
    for page_num in range(min(5, len(doc))):
        page = doc.load_page(page_num)
        
        # Check annotations (highlights)
        annots = page.annots()
        if annots:
            for annot in annots:
                if annot.type[0] == 8: # Highlight
                    rect = annot.rect
                    text = page.get_text("text", clip=rect)
                    print(f"Page {page_num+1} Highlight Annot: {text.strip()}")
        
        # Also let's print a little snippet of text to see question format
        text = page.get_text("text")
        lines = text.split('\n')
        if len(lines) > 5:
            print(f"Page {page_num+1} Sample Text Start:")
            for line in lines[:20]:
                print("  " + line.strip())
            break
            
if __name__ == '__main__':
    analyze_pdf('exammmm.pdf')
