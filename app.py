from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
import os
# Fix the imports to use the services package
from app.services.video_generator import VideoGenerator
from app.services.propmt_generator import generate_random_prompt

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'temp'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Ensure temp directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate-prompt', methods=['POST'])
def get_random_prompt():
    try:
        prompt = generate_random_prompt()
        return jsonify({'prompt': prompt})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/generate-video', methods=['POST'])
def generate_video():
    try:
        if 'image1' not in request.files or 'image2' not in request.files:
            return jsonify({'error': 'Both images are required'}), 400
        
        image1 = request.files['image1']
        image2 = request.files['image2']
        prompt = request.form.get('prompt', '')
        
        if not prompt:
            return jsonify({'error': 'Prompt is required'}), 400
        
        # Save uploaded images
        image1_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(image1.filename))
        image2_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(image2.filename))
        
        image1.save(image1_path)
        image2.save(image2_path)
        
        # Process video generation
        video_generator = VideoGenerator()
        status, video_url = video_generator.process_images(image1_path, image2_path, prompt)
        
        # Clean up temporary files
        os.remove(image1_path)
        os.remove(image2_path)
        
        return jsonify({
            'status': status,
            'video_url': video_url
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)