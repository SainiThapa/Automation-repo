import os
import zipfile
from django.shortcuts import redirect, render
from django.http import HttpResponse, FileResponse
from .forms import ImageTextForm
from .models import UploadedImage
from PIL import Image, ImageDraw, ImageFont
from PIL import Image, ImageDraw, ImageFont
import textwrap


LOGOS = {
    "berwick": "static/img/berwick.png",
    "cranbourne": "static/img/cranbourne.png"
}

def onboarding(request):
    if request.method == "POST":
        restaurant = request.POST.get("restaurant")
        if restaurant in ["berwick", "cranbourne"]:
            request.session["restaurant"] = restaurant
            return redirect(f"/upload")
    return render(request, "overlay_app/onboarding.html")
    

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

def overlay_image(base_image, overlay_image_path, position, overlay_size):
    overlay_image = Image.open(overlay_image_path)
    overlay_image = overlay_image.resize(overlay_size)
    base_image.paste(overlay_image, position, overlay_image.convert('RGBA'))

def add_text_to_image(image, text, font_path, font_size, restaurant_name, output_path, line_spacing=1.5):
    draw = ImageDraw.Draw(image)
    width, height = image.size
    
    # Load font
    try:
        font = ImageFont.truetype(font_path, font_size)
    except IOError:
        print("Font file not found. Using default font.")
        font = ImageFont.load_default()
    
    # Wrap text
    max_width = int(width)
    wrapped_lines = []
    for line in text.split('\n'):
        wrapped_lines.extend(textwrap.wrap(line, width=max_width // draw.textlength('A', font=font)))

    # Calculate text height
    line_height = draw.textbbox((0, 0), 'A', font=font)[3] - draw.textbbox((0, 0), 'A', font=font)[1]
    total_text_height = int(len(wrapped_lines) * line_height * line_spacing)
    start_y = (height - total_text_height) // 1.2

    # Draw text
    for line in wrapped_lines:
        text_width = draw.textlength(line, font=font)
        text_x = (width - text_width) // 2
        text_y = start_y
        start_y += int(line_height * line_spacing)

        for offset in [(-1, -1), (-1, 1), (1, -1), (1, 1)]:
            draw.text((text_x + offset[0], text_y + offset[1]), line, font=font, fill=(0, 0, 0, 255))
        draw.text((text_x, text_y), line, font=font, fill=(255, 255, 255, 255))

    # Add restaurant name
    try:
        brand_font = ImageFont.truetype(font_path, 150)
    except IOError:
        print("Font file not found. Using default font.")
        brand_font = ImageFont.load_default()

    brand_text_width = draw.textlength(restaurant_name, font=brand_font)
    brand_x = (width - brand_text_width) // 2
    brand_y = height - (font_size // 2) - 75
    draw.text((brand_x, brand_y), restaurant_name, font=brand_font, fill=(255, 255, 255, 255))

    image.save(output_path, format="PNG")

def add_black_layer_with_opacity(base_image_path, overlay_image_path, output_path, caption, logo_path, restaurant_name, opacity=128, font_path="DMSerifText.ttf", font_size=300):
    base_image = Image.open(base_image_path).convert("RGBA")

    # Crop image
    base_image = crop_to_square(base_image)

    # Add black overlay
    black_overlay = Image.new("RGBA", base_image.size, (0, 0, 0, opacity))
    combined_image = Image.alpha_composite(base_image, black_overlay)

    # Add logo
    base_width, base_height = base_image.size
    overlay_width = int(base_width * 0.3)
    overlay_height = int(base_height * 0.25)
    position_x = int(base_width * 0.5 - overlay_width / 2)
    position_y = int(base_height // 20)
    overlay_image(combined_image, logo_path, (position_x, position_y), (overlay_width, overlay_height))

    # Add text
    final_image = combined_image.convert("RGBA")
    add_text_to_image(final_image, caption, font_path, font_size, restaurant_name, output_path)

def process_image(image, text, logo_path, restaurant_name):
    output_path = f"{image.name}"
    add_black_layer_with_opacity(
        base_image_path=image,
        overlay_image_path=logo_path,
        output_path=output_path,
        caption=text.upper(),
        logo_path=logo_path,
        restaurant_name=restaurant_name,
        opacity=128,
        font_path="static/font/DMSerifText.ttf",
        font_size=300
    )
    return output_path

# Main view
def upload_images(request):
    if request.method == "POST":
        restaurant = request.session.get("restaurant")
        if not restaurant:
            return render(request, "overlay_app/onboarding.html", {"error": "Please select a restaurant."})
        
        restaurant_name = "TIMES BERWICK" if restaurant == "berwick" else "TIMES CRANBOURNE"
        logo_path = LOGOS.get(restaurant)
        if not os.path.exists(logo_path):
            return render(request, "overlay_app/upload.html", {"error": f"Logo for {restaurant_name} not found."})

        images = request.FILES.getlist('image')
        texts = request.POST.getlist('text')

        if len(images) != len(texts):
            return render(request, 'overlay_app/upload.html', {"error": "Image and text count mismatch."})

        output_files = []
        for image, text in zip(images, texts):
            try:
                processed_path = process_image(image, text, logo_path, restaurant_name)
                output_files.append(processed_path)
            except Exception as e:
                print(f"Error processing image {image.name}: {e}")
                return render(request, 'overlay_app/upload.html', {"error": f"Error processing image {image.name}: {e}"})
        # Handle bulk download
        if "bulk_download" in request.POST:
            zip_path = "processed_images.zip"
            try:
                with zipfile.ZipFile(zip_path, "w") as zipf:
                    for file_path in output_files:
                        zipf.write(file_path, os.path.basename(file_path))
                return FileResponse(open(zip_path, "rb"), as_attachment=True)
            except Exception as e:
                return render(request, 'overlay_app/upload.html', {"error": f"Error creating zip file: {e}"})
        return render(request, 'overlay_app/upload.html', {
            "output_files": output_files,
            "restaurant_name": restaurant_name
        })

    return render(request, 'overlay_app/upload.html')
