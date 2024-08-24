from flask import Flask, render_template, request, jsonify, send_file, Response
import google.generativeai as genai
import re
import os
import json
import zipfile

app = Flask(__name__)

# Configuration for Generative AI
genai.configure(api_key="AIzaSyCQR3E3kru000LRka7RRjR0mD2Q9pmWEcc")
model = genai.GenerativeModel('gemini-1.5-flash')

# Initialization function
def initialize_chat():
    chat = model.start_chat(history=[])
    with open('iterations/init.txt', 'r') as m:
        init = m.read()
    chat.send_message(init)
    return chat

# Regex pattern for extracting JSON from response
def extract_json(text):
    pattern = r'```json\s+(.*?)\s+```'
    match = re.search(pattern, text, re.DOTALL)
    if match:
        return match.group(1)
    return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate_website():
    query = request.form['query']
    chat = initialize_chat()  # Initialize the chat session

    def generate():
        accumulated_files = []
        
        # Iteration 1 - HTML
        progress = {"step": 1, "message": "Processing HTML file..."}
        yield f"data:{json.dumps(progress)}\n\n"
        with open('iterations/it1.txt', 'r') as m:
            first = m.read()
        response = chat.send_message(first + query)
        website_name = response.text

        # Iteration 2 - CSS
        progress = {"step": 2, "message": "Processing CSS file..."}
        yield f"data:{json.dumps(progress)}\n\n"
        with open('iterations/it2.txt', 'r') as m:
            file_query = m.read()
        response = chat.send_message(file_query)
        extracted_json = extract_json(response.text)
        if extracted_json:
            accumulated_files.extend(json.loads(extracted_json))

        # Iteration 3 - JavaScript
        progress = {"step": 3, "message": "Processing JavaScript file..."}
        yield f"data:{json.dumps(progress)}\n\n"
        with open('iterations/it3.txt', 'r') as m:
            file_query = m.read()
        response = chat.send_message(file_query)
        extracted_json = extract_json(response.text)
        if extracted_json:
            accumulated_files.extend(json.loads(extracted_json))

        # Iteration 4 - Additional Assets
        progress = {"step": 4, "message": "Processing additional assets..."}
        yield f"data:{json.dumps(progress)}\n\n"
        with open('iterations/it4.txt', 'r') as m:
            file_query = m.read()
        response = chat.send_message(file_query)
        extracted_json = extract_json(response.text)
        if extracted_json:
            accumulated_files.extend(json.loads(extracted_json))

        # Final Iteration - Description
        progress = {"step": 5, "message": "Finalizing..."}
        yield f"data:{json.dumps(progress)}\n\n"
        with open('iterations/it5.txt', 'r') as m:
            file_query = m.read()
        response = chat.send_message(file_query)
        description = response.text

        # Generate ZIP
        zip_filename = 'output.zip'
        with zipfile.ZipFile(zip_filename, 'w') as zipf:
            for file in accumulated_files:
                zipf.writestr(file['dir'], file['content'])

            images_folder = 'images'
            target_folder = 'project-root/assets/images'
            for root, dirs, files in os.walk(images_folder):
                for file in files:
                    image_path = os.path.join(root, file)
                    relative_path_in_zip = os.path.join(target_folder, os.path.relpath(image_path, start=images_folder))
                    zipf.write(image_path, relative_path_in_zip)

        result = {"website_name": website_name, "description": description}
        yield f"data:{json.dumps(result)}\n\n"

    return Response(generate(), content_type='text/event-stream')

@app.route('/download')
def download_file():
    path = "output.zip"
    return send_file(path, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
