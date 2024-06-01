from PIL import Image
import piexif

# Open the image and get its EXIF data
image = Image.open("images/palm-tree-1.jpg")
exif_data = image.info.get("exif")  # Get existing EXIF data

# Define the new UserComment tag
new_comment = 'my message'.encode()
exif_ifd = {piexif.ExifIFD.UserComment: new_comment}

# Merge the existing EXIF data with the new UserComment tag
if exif_data:
    exif_dict = piexif.load(exif_data)
    exif_dict["Exif"][piexif.ExifIFD.UserComment] = new_comment
    print("reached here!")
else:
    exif_dict = {"0th": {}, "Exif": exif_ifd, "1st": {}, "thumbnail": None, "GPS": {}}

# Dump the updated EXIF data
exif_data_mod = piexif.dump(exif_dict)

# Save the modified image with the updated EXIF data
image.save('image_mod.jpg', exif=exif_data_mod)

# Open the modified image to retrieve its EXIF data
image_with_comment = Image.open("image_mod.jpg")
exif_data_with_comment = image_with_comment.info.get("exif")

# Try to retrieve the UserComment tag from the modified image using get() method
if exif_data_with_comment:
    # Retrieve the UserComment tag from the modified image
    modified_comment = piexif.load(exif_data_with_comment)["Exif"][piexif.ExifIFD.UserComment]
    print("Modified User Comment:", modified_comment.decode())
else:
    print("No EXIF data found in the modified image.")
