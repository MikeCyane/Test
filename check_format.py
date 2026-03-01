import fitz
import sys

def check_format(filepath):
    print(f"Checking: {filepath}")
    doc = fitz.open(filepath)
    page = doc.load_page(0)
    
    annots = page.annots()
    print("Annotations:", [a.type for a in annots] if annots else "None")
    
    blocks = page.get_text('dict')['blocks']
    special_spans = []
    normal_spans = []
    for b in blocks:
        if b['type'] == 0:
            for l in b['lines']:
                for s in l['spans']:
                    if len(normal_spans) < 3:
                        normal_spans.append(s)
                    
                    if s['color'] != 0 or 'Bold' in s['font'] or 'Italic' in s['font'] or '*' in s['text'] or s['flags'] != 0:
                        special_spans.append(s)

    print("Sample Normal Text:")
    for s in normal_spans:
        print(f"Text: {s['text'].strip()} | Font: {s['font']} | Color: {hex(s['color'])} | Flags: {s['flags']}")
        
    print("\nSpecial Text found (first 10):")
    for s in special_spans[:10]:
        print(f"Text: {s['text'].strip()} | Font: {s['font']} | Color: {hex(s['color'])} | Flags: {s['flags']}")

if __name__ == '__main__':
    check_format('Clinical engineering I.pdf')
    print("--------------------------------------------------")
    check_format('Medical equipment Measurement and Instrumentation.pdf')
    print("--------------------------------------------------")
    check_format('RAHPC EXAMIN PREP.pdf')
