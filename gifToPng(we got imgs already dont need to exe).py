from PIL import Image, ImageSequence
import os

def convert_gif_to_png_with_transparency(gif_path, output_folder):
    gif = Image.open(gif_path)

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
        

    frame_number = 0
    for frame in ImageSequence.Iterator(gif):
        frame = frame.convert('RGBA')
        frame_path = os.path.join(output_folder, f"butterfly_frame_{frame_number:02d}.png")
        frame.save(frame_path, 'PNG')
        frame_number += 1

# Example usage:
gif_path = './butterfly_3.gif'
output_folder = './img'
convert_gif_to_png_with_transparency(gif_path, output_folder)