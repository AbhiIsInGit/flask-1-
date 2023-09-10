from flask import Flask, request, jsonify, render_template_string
from spleeter.separator import Separator
import os

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['OUTPUT_FOLDER'] = 'output'

# Initialize Spleeter
separator = Separator('spleeter:2stems')

# HTML template with embedded CSS
html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Vocal Remover ML</title>
    <style>
        /* CSS styles here */
        body {
            background-color: #20232a;
            color: #61dafb;
            font-family: Arial, sans-serif;
        }

        h1 {
            text-align: center;
            margin: 20px 0;
        }

        form {
            text-align: center;
        }

        input[type="file"] {
            display: none;
        }

        label {
            background-color: #61dafb;
            color: #20232a;
            padding: 10px 20px;
            cursor: pointer;
            border-radius: 5px;
            transition: background-color 0.3s;
        }

        label:hover {
            background-color: #1e90ff;
        }

        input[type="submit"] {
            display: none;
        }

        #upload-label::before {
            content: "Select an audio file";
        }

        #upload-label:hover::before {
            content: "Click to select";
        }

        #upload-label::after {
            content: "No file chosen";
        }

        input[type="file"]:focus + label {
            outline: 2px dotted #61dafb;
            outline-offset: -5px;
        }

        #upload-label.has-file::after {
            content: attr(data-filename);
        }

        #waveform-container {
            text-align: center;
            margin-top: 20px;
        }

        #waveform {
            width: 80%;
            max-width: 600px;
            height: 100px;
            background-color: #20232a;
            position: relative;
            overflow: hidden;
        }

        #waveform-bar {
            width: 100%;
            height: 100%;
            background: linear-gradient(to right, rgba(97, 218, 251, 0.5), rgba(97, 218, 251, 0.8));
            position: absolute;
            animation: wave-animation 2s linear infinite;
        }

        @keyframes wave-animation {
            0% {
                left: -100%;
            }
            100% {
                left: 100%;
            }
        }
    </style>
</head>
<body>
    <h1>Vocal Remover ML</h1>
    <form method="POST" action="/upload" enctype="multipart/form-data">
        <input type="file" name="audio_file" accept=".mp3,.wav">
        <label id="upload-label" for="audio_file">Select an audio file</label>
        <input type="submit" value="Upload and Process">
    </form>
    <div id="waveform-container">
        <h2>Audio Wave Animation</h2>
        <div id="waveform">
            <div id="waveform-bar"></div>
        </div>
    </div>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(html_template)

@app.route('/upload', methods=['POST'])
def upload():
    if 'audio_file' not in request.files:
        return jsonify({"error": "No file part"})

    file = request.files['audio_file']
    if file.filename == '':
        return jsonify({"error": "No selected file"})

    if file:
        # Save the uploaded file
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(file_path)

        # Separate vocals and accompaniment
        output_path = app.config['OUTPUT_FOLDER']
        separator.separate_to_file(file_path, output_path)

        # Send the accompaniment to the user
        accompaniment_path = os.path.join(output_path, f'{file.stem}_accompaniment.wav')

        return jsonify({"message": "Processing complete", "accompaniment_path": accompaniment_path})

if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)
    app.run(debug=True, port=os.getenv("PORT", default=5000))
