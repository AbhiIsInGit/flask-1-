from flask import Flask, request, jsonify, render_template_string
import os
import torchaudio
import torchaudio.transforms as T

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['OUTPUT_FOLDER'] = 'output'

# HTML template with embedded CSS (same as before)
html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Vocal Remover ML</title>
    <!-- CSS styles here -->
    <!-- ... (same as previous CSS) ... -->
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

        # Load the audio
        waveform, sample_rate = torchaudio.load(file_path)

        # Your Open-Unmix code here to separate vocals
        # Example code (replace this with your Open-Unmix code):
        transform = T.Resample(orig_freq=sample_rate, new_freq=44100)
        waveform = transform(waveform)
        
        # Save the separated vocals (replace this with your Open-Unmix code)
        vocals_path = os.path.join(app.config['OUTPUT_FOLDER'], f'{file.stem}_vocals.wav')
        torchaudio.save(vocals_path, waveform, 44100)

        return jsonify({"message": "Processing complete", "vocals_path": vocals_path})

if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)
    app.run(debug=True, port=os.getenv("PORT", default=5000))
