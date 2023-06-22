import os
from PIL import Image

def get_size_format(b, factor=1024, suffix="B"):
    """
    Scale bytes to its proper byte format
    e.g:
        1253656 => '1.20MB'
        1253656678 => '1.17GB'
    """
    for unit in ["", "K", "M", "G", "T", "P", "E", "Z"]:
        if b < factor:
            return f"{b:.2f}{unit}{suffix}"
        b /= factor
    return f"{b:.2f}Y{suffix}"


def compress_img(image_name, quality=75, to_jpg=False, max_size=600000):
    # load the image to memory
    img = Image.open(image_name)
    # get the original image size in bytes
    image_size = os.path.getsize(image_name)
    if image_size > max_size:
        img_width, img_height = img.size
        if img_width > 1920:
            resize_ratio = 1920 / img_width # scale to 1920 width
            img = img.resize((int(img_width * resize_ratio), int(img_height * resize_ratio)), Image.ANTIALIAS)
        # split the filename and extension
        filename, ext = os.path.splitext(image_name)
        # make new filename appending _compressed to the original file name
        extension = ext.lower()
        if to_jpg or extension in (".tif", ".tiff", ".png"):
            # change the extension to JPEG
            new_filename = f"{filename}_compressed.jpg"
        else:
            # retain the same extension of the original image
            new_filename = f"{filename}_compressed{extension}"
        try:
            if new_filename.endswith(".jpg"):
                img.save(new_filename, quality=quality, optimize=True)
            elif new_filename.endswith(".png"):
                img.save(new_filename, compress_level=9)
            else:
                img.save(new_filename)
        except OSError:
            # convert the image to RGB mode first
            img = img.convert("RGB")
            # save the image with the corresponding quality and optimize set to True
            img.save(new_filename, quality=quality, optimize=True)
        # get the new image size in bytes
        new_image_size = os.path.getsize(new_filename)
        if new_image_size > max_size:
            print(f"Image still large!! {get_size_format(new_image_size)}")
            print(new_filename)
        # # calculate the saving bytes
        # saving_diff = new_image_size - image_size
        # # print the saving percentage
        # print(f"[+] Image size change: {saving_diff/image_size*100:.2f}% of the original image size.")
        try:
            os.remove(image_name)
        except OSError as e:
            print(e) # look what it says
            print(e.code)


def compress_directory_recursive(path):
    if path.endswith(".DS_Store"):
        return
    # check if path is file
    if not os.path.isdir(path):
        compress_img(path, max_size=600000)
    else:
        directory = os.fsencode(path)
        for f in os.listdir(directory):
            f_path = os.path.join(directory, f)
            compress_directory_recursive(os.fsdecode(f_path))
