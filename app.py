import os
import vertexai
from vertexai.generative_models import GenerativeModel
from flask import Flask, request, render_template, send_file, redirect, url_for
from werkzeug.utils import secure_filename
from bs4 import BeautifulSoup
from markdown import markdown

# Initialize Flask app
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'  # Upload folder where uploaded files will be saved.
app.config['ALLOWED_EXTENSIONS'] = {'sh'}  # File extensions that you are uploading.

# Initialize Vertex AI
project_id = "sandhata"
vertexai.init(project=project_id, location="us-central1")
model = GenerativeModel(model_name="gemini-1.5-flash-001")  # API or model that we are using to predict or generate the text.

# Ensure upload folder exists
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])  # Create the folder if it does not exist.

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']  # Check for allowed extensions.

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':  # Because you want to upload data to the server.
        if 'file' not in request.files:
            return redirect(request.url)
        file = request.files['file']  # Extract the file.
        if file.filename == '':
            return redirect(request.url)  # Redirect back to main page.
        if file and allowed_file(file.filename):  # Check for the file and allowed extension.
            filename = secure_filename(file.filename)  # Get a secure version of the file.
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)  # Save the file to the upload folder.
            return redirect(url_for('generate_documentation', filename=filename))  # Redirect to generate documentation method.
    return render_template('upload.html')

@app.route('/generate/<filename>', methods=['GET'])
def generate_documentation(filename):
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    with open(filepath, 'r') as file:  # Read the contents of the file.
        bash_script = file.read()

    prompt = f"Documentation of the following bash script:\n\n{bash_script}"  # Provide the prompt.
    response = model.generate_content(prompt)  # Generate the response.

    documentation = response.text
    html = markdown(documentation)
    text = ''.join(BeautifulSoup(html, features="html.parser").findAll(text=True))
    doc_file = os.path.join(app.config['UPLOAD_FOLDER'], f"{filename}_documentation.txt")
    with open(doc_file, 'w') as doc:
        doc.write(text)  # Write the response to a txt file.

    return render_template('documentation.html', documentation=text, doc_file=f"{filename}_documentation.txt")  # Call the documentation.html file.

@app.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    return send_file(filepath, as_attachment=True)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
