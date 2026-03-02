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

    # Pattern for splitting: "Option/Question 1.Next" or "Option (a) Next"
    # We look for: (any char) (space) (digits/letters) (dot/paren) (space optional) (any char)
    # Using re.IGNORECASE for [a-e] and Q
    # Allowing leading (
    split_regex = re.compile(r'(.+?)\s+([(]?(?:(?:Q|q)?\d+|[a-eA-ExX])[.)]\s*.*)', re.IGNORECASE)

    lines = []
    for txt, red in raw_lines:
        match = split_regex.search(txt)
        if match:
            # We might have multiple things on one line, so let's try to split until no more matches
            temp_txt = txt
            while True:
                m = split_regex.search(temp_txt)
                if m:
                    lines.append((m.group(1).strip(), red))
                    temp_txt = m.group(2).strip()
                else:
                    lines.append((temp_txt, red))
                    break
        else:
            lines.append((txt, red))

    q_pattern = re.compile(r'^[(]?(?:Q|q)?\s*(\d+)[.)]\s*(.*)$', re.IGNORECASE)
    opt_pattern = re.compile(r'^[(]?([a-eA-ExX]|(?:\d+))[.)]\s*(.*)$', re.IGNORECASE)

    for txt, red in lines:
        q_m = q_pattern.match(txt)
        o_m = opt_pattern.match(txt)
        
        is_q = False
        if q_m:
            if txt.lower().startswith('q'): 
                is_q = True
            elif not current_q: 
                is_q = True
            else:
                # Overlap case: number-only prefix
                # If current_q starts with Q, then numbers are options
                if current_q['question'].lower().startswith('q'):
                    is_q = False
                # If current_q already has options, we might be seeing a new question
                elif current_q['options']:
                    # If the current options are letters, a new number is definitely a new question
                    # If current options are also numbers, this is tricky. 
                    # But if we see '2.' after '1.', it's an option.
                    # Let's assume numbers are questions if no 'Q' is present in the file style.
                    # EXCEPT if it follows an option.
                    is_q = True
                else:
                    # No options yet. So "1." after a "Question" is likely an option.
                    is_q = False
            
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
        qs = extract_from_pdf(f)
        all_qs.extend(qs)
        print(f"Extracted: {len(qs)} from {f}")
    
    # Filter only real questions (at least 2 options)
    valid = [q for q in all_qs if len(q['options']) > 1]
    
    with open("questions_data.js", "w", encoding="utf-8") as f:
        f.write(f"const RAW_QUESTIONS = {json.dumps(valid, indent=2)};")
    print(f"Extraction complete. Total questions: {len(valid)}")

main()
