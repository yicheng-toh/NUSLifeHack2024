from flask import Flask, request, redirect, url_for, render_template, send_from_directory, flash
import os
from stegano import lsb
from send_telegram_msg import send_message
import cv2
from scipy.fftpack import dct, idct
import numpy as np

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
# def embed_message(image_path, message):
#     # Load the image
#     image = cv2.imread(image_path)
#     h, w, channels = image.shape
    
#     # Convert image to float32
#     image = np.float32(image)
    
#     # Process each channel separately
#     for channel in range(channels):
#         # Apply DCT to the channel
#         dct_channel = dct(dct(image[:,:,channel].T, norm='ortho').T, norm='ortho')
        
#         # Flatten the DCT coefficients
#         dct_flat = dct_channel.flatten()
        
#         # Convert the message to binary representation
#         data_bits = ''.join(format(byte, '08b') for byte in message.encode('utf-8'))
        
#         # Embed the data bits into the DCT coefficients
#         for i, bit in enumerate(data_bits):
#             if bit == '1':
#                 dct_flat[i] = dct_flat[i] + 0.01  # Modify coefficient slightly to embed bit '1'
#             else:
#                 dct_flat[i] = dct_flat[i] - 0.01  # Modify coefficient slightly to embed bit '0'
        
#         # Reshape the modified coefficients back to the original shape
#         dct_channel = dct_flat.reshape((h, w))
        
#         # Apply inverse DCT to get the modified channel
#         idct_channel = idct(idct(dct_channel.T, norm='ortho').T, norm='ortho')
        
#         # Clip and convert the channel back to uint8
#         idct_channel = np.uint8(np.clip(idct_channel, 0, 255))
        
#         # Update the image with the modified channel
#         image[:,:,channel] = idct_channel
    
#     # Convert the entire image back to uint8
#     image = np.uint8(np.clip(image, 0, 255))
    
#     # Save the modified image
#     cv2.imwrite(image_path, image)

# def detect_message(image_path, message_length):
#     try:
#         # Load the image
#         image = cv2.imread(image_path)
#         h, w, channels = image.shape
        
#         # Convert image to float32
#         image = np.float32(image)
        
#         # Initialize an empty message
#         extracted_message = ''
        
#         # Process each channel separately
#         for channel in range(channels):
#             # Apply DCT to the channel
#             dct_channel = dct(dct(image[:,:,channel].T, norm='ortho').T, norm='ortho')
            
#             # Flatten the DCT coefficients
#             dct_flat = dct_channel.flatten()
            
#             # Extract the data bits from the DCT coefficients
#             extracted_bits = []
#             for i in range(message_length * 8):  # 8 bits per byte
#                 if dct_flat[i] > 0:
#                     extracted_bits.append('1')
#                 else:
#                     extracted_bits.append('0')
            
#             # Convert the extracted bits back to bytes
#             extracted_bytes = [int(''.join(extracted_bits[i:i+8]), 2) for i in range(0, len(extracted_bits), 8)]
            
#             # Convert bytes to string
#             extracted_message += bytes(extracted_bytes).decode('utf-8')
        
#         return extracted_message
    
#     except Exception as e:
#         print(f"Error detecting message: {str(e)}")
#         return None
    

@app.route('/<username>', methods=['GET', 'POST'])
async def upload_file(username):
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
                additional_message = f"{username} is trying to upload this image"
                await send_message(file_path, existing_message + "\n" + additional_message)
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
