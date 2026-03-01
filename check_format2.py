import fitz

def check_format(filepath, file_out):
    file_out.write(f"Checking: {filepath}\n")
    doc = fitz.open(filepath)
    page = doc.load_page(0)
    
    annots = page.annots()
    file_out.write("Annotations: " + str([a.type for a in annots] if annots else "None") + "\n")
    
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

    file_out.write("Sample Normal Text:\n")
    for s in normal_spans:
        file_out.write(f"Text: {s['text'].strip()} | Font: {s['font']} | Color: {hex(s['color'])} | Flags: {s['flags']}\n")
        
    file_out.write("\nSpecial Text found (first 10):\n")
    for s in special_spans[:10]:
        file_out.write(f"Text: {s['text'].strip()} | Font: {s['font']} | Color: {hex(s['color'])} | Flags: {s['flags']}\n")
    file_out.write("\n")

if __name__ == '__main__':
    with open('format_output.txt', 'w', encoding='utf-8') as f:
        check_format('Clinical engineering I.pdf', f)
        f.write("--------------------------------------------------\n")
        check_format('Medical equipment Measurement and Instrumentation.pdf', f)
        f.write("--------------------------------------------------\n")
        check_format('RAHPC EXAMIN PREP.pdf', f)
