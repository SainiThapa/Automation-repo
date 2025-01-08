from PIL import Image, ImageDraw, ImageFont
import textwrap

def crop_to_square(image):
    width, height = image.size
    if width > height:
        # Crop the excess width
        left = (width - height) // 2
        right = left + height
        image = image.crop((left, 0, right, height))
    elif height > width:
        # Crop the excess height
        top = (height - width) // 2
        bottom = top + width
        image = image.crop((0, top, width, bottom))
    return image

def overlay_image(base_image, overlay_image_path, position, overlay_size, output_path):
    # Check if the base_image is a file path or an Image object
    if isinstance(base_image, str):
        base_image = Image.open(base_image)

    overlay_image = Image.open(overlay_image_path)
    overlay_image = overlay_image.resize(overlay_size)
    base_image.paste(overlay_image, position, overlay_image.convert('RGBA'))

    # Save the resulting image
    base_image.save(output_path, format="PNG")

def add_text_to_image(image, text, font_path, font_size, output_path,line_spacing=1.5):
    # Create a drawing context
    draw = ImageDraw.Draw(image)
    width, height = image.size
    # Load font
    try:
        font = ImageFont.truetype(font_path, font_size)
    except IOError:
        print("Font file not found. Using default font.")
        font = ImageFont.load_default()
    
    max_width = int(width)  # Use 80% of the image width for text
    wrapped_lines = []
    for line in text.split('\n'):
        wrapped_lines.extend(textwrap.wrap(line, width=max_width // draw.textlength('A',font=font)))

    # Calculate the total height of the wrapped text
    line_height = draw.textbbox((0, 0), 'A', font=font)[3] - draw.textbbox((0, 0), 'A', font=font)[1]
    total_text_height = int(len(wrapped_lines) * line_height * line_spacing)

    # Start text block vertically centered
    start_y = (height - total_text_height) // 1.2

    # Draw each line with stroke for better visibility
    for line in wrapped_lines:
        text_width = draw.textlength(line,font=font)
        text_x = (width - text_width) // 2  # Center each line
        text_y = start_y
        start_y += int(line_height*line_spacing)

        # Draw stroke (outline)
        for offset in [(-1, -1), (-1, 1), (1, -1), (1, 1)]:
            draw.text((text_x + offset[0], text_y + offset[1]), line, font=font, fill=(0, 0, 0, 255))

        # Draw main text
        draw.text((text_x, text_y), line, font=font, fill=(255, 255, 255, 255))

        # Brand Name goes here
    # Load the font for the brand name
    try:
        brand_font = ImageFont.truetype("DMSerifText.ttf", font_size // 2)  # Smaller font size for the brand name
    except IOError:
        print("Font file not found. Using default font.")
        brand_font = ImageFont.load_default()

    # Brand Name goes here
    brand = "TIMES BERWICK"

    # Calculate position for central alignment at the bottom of the image
    brand_text_width = draw.textlength(brand, font=brand_font)
    brand_x = (width - brand_text_width) // 2  # Center horizontally
    brand_y = height - (font_size // 2) - 75  # Place near the bottom with some padding

    # Draw the brand name on the image
    draw.text((brand_x, brand_y), brand, font=brand_font, fill=(255, 255, 255, 255))

    # Save the resulting image
    image.save(output_path, format="PNG")


def add_black_layer_with_opacity(base_image_path, overlay_image_path, output_path, caption, opacity=128, font_path="DMSerifText.ttf", font_size=300):
    base_image = Image.open(base_image_path).convert("RGBA")

    # Crop the image to a square 
    base_image = crop_to_square(base_image)

    # Create a black overlay with the same size as the base image
    black_overlay = Image.new("RGBA", base_image.size, (0, 0, 0, opacity))
    # Composite the overlay onto the base image
    combined_image = Image.alpha_composite(base_image, black_overlay)
    # Determine overlay size and position
    base_width, base_height = base_image.size
    overlay_width = int(base_width * 0.3)
    overlay_height = int(base_height * 0.25)
    position_x = int(base_width * 0.5 - overlay_width / 2)  # Center horizontally
    position_y = int(base_height)//20  # 10% from the top
    
    overlay_image_path = "times.png"
    overlay_size = (overlay_width, overlay_height)
    position = (position_x, position_y)
    
    # Call the overlay_image function
    overlay_image(combined_image, overlay_image_path, position, overlay_size, output_path)

    final_image = Image.open(output_path).convert("RGBA")
    add_text_to_image(final_image, caption, font_path, font_size, output_path)


if __name__=="__main__":
    base_image_path = 'Scallops.jpg'
    output_path = 'output_image1.png'
    overlay_image_path='times.png'
    caption=input("Enter caption: ")

    add_black_layer_with_opacity(base_image_path,overlay_image_path,output_path,caption.upper())
