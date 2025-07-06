import base64

def encode_image_base64(image_path) -> str:
    with open(image_path, "rb") as image_file:
        buffer = image_file.read()
        encoded_image = base64.b64encode(buffer).decode("utf-8")

        return encoded_image