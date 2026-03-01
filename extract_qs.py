import fitz
import re
import json

def extract_from_pdf(pdf_path):
    print(f"Extracting: {pdf_path}")
    try:
        doc = fitz.open(pdf_path)
    except:
        return []
        
    questions = []
    current_q = None
    red_colors = {0xc00000, 0xff0000, 0xed1c24, 0xff3333}

    raw_lines = []
    for page in doc:
        blocks = page.get_text("dict")["blocks"]
        for b in blocks:
            if b['type'] == 0:
                for l in b['lines']:
                    txt = ""
                    red = False
                    for s in l['spans']:
                        if s['text'].strip():
                            txt += s['text']
                            if s['color'] in red_colors: red = True
                    if txt.strip(): raw_lines.append((txt.strip(), red))

    # Pattern for splitting: "Option Text 10.Question"
    # We look for: (any char) (space) (digits) (dot/paren) (space optional) (Capital Letter)
    split_regex = re.compile(r'(.+?)\s+(\d+[.)]\s*[A-Z].*)')

    lines = []
    for txt, red in raw_lines:
        match = split_regex.search(txt)
        if match:
            lines.append((match.group(1).strip(), red))
            lines.append((match.group(2).strip(), False))
        else:
            lines.append((txt, red))

    q_pattern = re.compile(r'^(?:Q|q)?\s*(\d+)[.)]\s*(.*)$', re.IGNORECASE)
    opt_pattern = re.compile(r'^([a-eA-ExX1-9])[.)]\s*(.*)$')

    for txt, red in lines:
        q_m = q_pattern.match(txt)
        o_m = opt_pattern.match(txt)
        
        # 1. New Question?
        # A question usually has a clear number. 
        # In these PDFs, questions often start with Q. or are in a specific sequence.
        # If it's just a number like "1.", it might be an option.
        is_q = False
        if q_m:
            if txt.lower().startswith('q'): is_q = True
            elif not current_q: is_q = True # First one
            elif current_q and current_q['options']: is_q = True # Already have options for prev
            
        if is_q:
            if current_q and current_q['options']: questions.append(current_q)
            current_q = {"question": txt, "options": [], "source": pdf_path}
        elif o_m and current_q:
            current_q['options'].append({"text": txt, "isCorrect": red})
        elif current_q:
            if current_q['options']:
                current_q['options'][-1]['text'] += " " + txt
                if red: current_q['options'][-1]['isCorrect'] = True
            else:
                current_q['question'] += " " + txt

    if current_q and current_q['options']: questions.append(current_q)
    return questions

def main():
    all_qs = []
    files = ["OGs/exammmm.pdf", "OGs/ECMG.pdf", "OGs/ICs.pdf", "OGs/DIODES.pdf", 
             "OGs/MEASUREMENTS.pdf", "OGs/CAPACITORS.pdf", "OGs/TRANSISTOR.pdf"]
    for f in files:
        all_qs.extend(extract_from_pdf(f))
    
    # Filter only real questions (at least 2 options)
    valid = [q for q in all_qs if len(q['options']) > 1]
    
    with open("questions_data.js", "w", encoding="utf-8") as f:
        f.write(f"const RAW_QUESTIONS = {json.dumps(valid, indent=2)};")
    print(f"Extraction complete. Total questions: {len(valid)}")

main()
