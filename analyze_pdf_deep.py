import fitz
import json

def analyze_page(filepath, outpath):
    doc = fitz.open(filepath)
    page = doc.load_page(0)
    
    data = {"text_blocks": []}
    
    # get text blocks with span info (font, color, etc.)
    blocks = page.get_text("dict")["blocks"]
    for b in blocks:
        if b['type'] == 0:  # text block
            block_info = {"bbox": b["bbox"], "lines": []}
            for l in b["lines"]:
                line_info = {"bbox": l["bbox"], "spans": []}
                for s in l["spans"]:
                    # color is an integer representing RGB
                    line_info["spans"].append({
                        "text": s["text"],
                        "bbox": s["bbox"],
                        "color": hex(s["color"]),
                        "flags": s["flags"]
                    })
                block_info["lines"].append(line_info)
            data["text_blocks"].append(block_info)
            
    # get drawings (lines, rectangles, etc.)
    data["drawings"] = []
    drawings = page.get_drawings()
    for d in drawings:
        data["drawings"].append({
            "items": [item[0] for item in d["items"]],  # type of drawing (e.g. 're' for rect, 'l' for line)
            "color": d.get("color"),
            "fill": d.get("fill")
        })
        
    with open(outpath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)

if __name__ == '__main__':
    analyze_page('exammmm.pdf', 'exammmm_analysis.json')
    analyze_page('Clinical engineering I.pdf', 'clinical_analysis.json')
