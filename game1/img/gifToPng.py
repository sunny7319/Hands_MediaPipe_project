from PIL import Image, ImageSequence
import os

def convert_gif_to_png_with_transparency(gif_path, frame_name, output_folder):
    gif = Image.open(gif_path)

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
        

    frame_number = 0
    for frame in ImageSequence.Iterator(gif):
        frame = frame.convert('RGBA')
        frame_path = os.path.join(output_folder, f"{frame_name}_frame_{frame_number:02d}.png")
        frame.save(frame_path, 'PNG')
        frame_number += 1

# Example usage:
gif_path = './dog_1.gif'
frame_name = "dog"
output_folder = './img_gif_dog'
convert_gif_to_png_with_transparency(gif_path, frame_name, output_folder)