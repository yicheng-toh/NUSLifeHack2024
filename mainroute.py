from flask import Flask, request, redirect, url_for, render_template, send_from_directory, flash
import os
from stegano import lsb

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}  # Allowed file extensions

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def embed_message(image_path, message):
    secret = lsb.hide(image_path, message)
    secret.save(image_path)  # Overwrite the original file with hidden message

def detect_message(image_path):
    try:
        message = lsb.reveal(image_path)
        return message
    except Exception as e:
        print(f"Error detecting message: {str(e)}")
        return None

@app.route('/<username>', methods=['GET', 'POST'])
def upload_file(username):
    user_folder = os.path.join(app.config['UPLOAD_FOLDER'], username)
    
    if request.method == 'POST':
        # Check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        
        file = request.files['file']
        
        # If user does not select file, browser also submits an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        
        if file and allowed_file(file.filename):
            filename = file.filename
            file_path = os.path.join(user_folder, filename)
            
            # Ensure user_folder exists before saving the file
            os.makedirs(user_folder, exist_ok=True)
            
            file.save(file_path)
            
            # Attempt to detect existing message
            existing_message = detect_message(file_path)
            
            if existing_message:
                flash(f"Existing message detected: {existing_message}")
            else:
                # Embed a default message if no message detected
                default_message = f"Author: {username}"
                embed_message(file_path, default_message)
                flash(f"No existing message detected. Added default message for {username}.")
            
            return redirect(url_for('upload_file', username=username))

    # Display uploaded images
    if os.path.exists(user_folder):
        files = os.listdir(user_folder)
    else:
        files = []

    return render_template('index.html', username=username, files=files)

@app.route('/uploads/<username>/<filename>')
def uploaded_file(username, filename):
    user_folder = os.path.join(app.config['UPLOAD_FOLDER'], username)
    return send_from_directory(user_folder, filename)

if __name__ == '__main__':
    app.run(debug=True)
