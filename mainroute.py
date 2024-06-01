from flask import Flask, request, redirect, url_for, render_template, send_from_directory, flash
import os
from stegano import lsb
from PIL import Image
import piexif

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}  # Allowed file extensions

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def embed_message(image_path, message):

    # add exif data into image
    image = Image.open(image_path)
    exif_data = image.info.get("exif")  # Get existing EXIF data

    # Define the new UserComment tag
    new_comment = message.encode()
    exif_ifd = {piexif.ExifIFD.UserComment: new_comment}

    # Merge the existing EXIF data with the new UserComment tag
    if exif_data:
        exif_dict = piexif.load(exif_data)
        exif_dict["Exif"][piexif.ExifIFD.UserComment] = new_comment
    else:
        exif_dict = {"0th": {}, "Exif": exif_ifd, "1st": {}, "thumbnail": None, "GPS": {}}
    # Dump the updated EXIF data
    exif_data_mod = piexif.dump(exif_dict)
    # Save the modified image with the updated EXIF data
    image.save(image_path, exif=exif_data_mod)
    # change the last bit of the red pixel in image
    def modify_image(image_path, comment):
        # Open the image
        image = Image.open(image_path)
        # Split the image into its RGB components
        r, g, b = image.split()
        # Convert comment to binary
        comment_binary = ''.join(format(ord(c), '08b') for c in comment)
        # Ensure the length of comment binary is less than or equal to the number of pixels in the red channel
        comment_binary = comment_binary[:(len(r.getdata()))]
        # Modify the red channel pixels based on the comment binary
        modified_r_pixels = []
        rvalue = r.getdata()
        for i in range(len(rvalue)):
            modified_pixel = rvalue[i] & 0b11111110  # Zero out the last bit
            modified_pixel |= int(comment_binary[i%len(comment_binary)])  # Set the last bit based on the comment binary
            modified_pixel |= 0x00000001 if comment_binary == 1 else 0x0000000
            modified_r_pixels.append(modified_pixel)
        # Create a new red channel image with the modified pixel values
        modified_r = Image.new('L', r.size)
        modified_r.putdata(modified_r_pixels)
        # modified_r.putdata(list(convert(modified_r_pixels,r.size)))
        print(modified_r.getpixel)
        # Recombine the modified red channel with the original green and blue channels into a new image
        modified_image = Image.merge('RGB', (modified_r, g, b))

        return modified_image
    DELIMITER = "@"
    comment = message + DELIMITER
    modified_image = modify_image(image_path, message)
    modified_image.save(image_path)
    # use stegano
    secret = lsb.hide(image_path, message)
    secret.save(image_path)  # Overwrite the original file with hidden message

def detect_message(image_path):
    try:
        message = lsb.reveal(image_path)
        return message
    except Exception as e:
        print(f"Error detecting message: {str(e)}")
        # return None
    else:
        pass
    try:
        image_with_comment = Image.open(image_path)
        exif_data_with_comment = image_with_comment.info.get("exif")
        if exif_data_with_comment:
    # Retrieve the UserComment tag from the modified image
            modified_comment = piexif.load(exif_data_with_comment)["Exif"][piexif.ExifIFD.UserComment]
            # print("Modified User Comment:", modified_comment.decode())
            return modified_comment.decode()
        else:
            print("No EXIF data found in the modified image.")
    except:
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
