import json
import zipfile

def package_app():
    # Read the extracted questions
    with open('questions.json', 'r', encoding='utf-8') as f:
        data = f.read()

    # Read the current app.js
    with open('app.js', 'r', encoding='utf-8') as f:
        app_js = f.read()

    # Replace the fetch logic with hardcoded data so it works offline locally
    replacement = f"""// Initialize App
async function initApp() {{
    try {{
        let allQuestions = {data};"""

    js_to_replace = """// Initialize App
async function initApp() {
    try {
        const response = await fetch('questions.json');
        if (!response.ok) throw new Error("Failed to load");
        
        let allQuestions = await response.json();"""

    app_js = app_js.replace(js_to_replace, replacement)

    # Write the standalone app.js back
    with open('app.js', 'w', encoding='utf-8') as f:
        f.write(app_js)

    # Create the zip file
    print("Zipping files: index.html, style.css, app.js")
    with zipfile.ZipFile('ExamPrepApp.zip', 'w', zipfile.ZIP_DEFLATED) as zipf:
        zipf.write('index.html')
        zipf.write('style.css')
        zipf.write('app.js')

    print("Successfully created ExamPrepApp.zip")

if __name__ == '__main__':
    package_app()
