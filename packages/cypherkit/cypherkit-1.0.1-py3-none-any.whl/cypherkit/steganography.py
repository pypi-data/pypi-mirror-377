from PIL import Image

def encode_message(image_path: str, message: str, output_path: str):
    image = Image.open(image_path)
    encoded_image = image.copy()
    width, height = image.size
    message += chr(0)  # Null-terminator to indicate end of message
    message_bits = ''.join([format(ord(char), '08b') for char in message])
    data_index = 0

    for y in range(height):
        for x in range(width):
            pixel = list(image.getpixel((x, y)))
            for i in range(3):  # R, G, B
                if data_index < len(message_bits):
                    pixel[i] = pixel[i] & ~1 | int(message_bits[data_index])
                    data_index += 1
            encoded_image.putpixel((x, y), tuple(pixel))
            if data_index >= len(message_bits):
                encoded_image.save(output_path)
                return

def decode_message(image_path: str) -> str:
    image = Image.open(image_path)
    width, height = image.size
    message_bits = []
    for y in range(height):
        for x in range(width):
            pixel = list(image.getpixel((x, y)))
            for i in range(3):  # R, G, B
                message_bits.append(pixel[i] & 1)
    message_bytes = [message_bits[i:i + 8] for i in range(0, len(message_bits), 8)]
    message = ''.join([chr(int(''.join(map(str, byte)), 2)) for byte in message_bytes])
    return message.split(chr(0))[0]  # Split at null-terminator and return the message
