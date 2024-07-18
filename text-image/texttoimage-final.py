import os
import random
from PIL import Image, ImageDraw, ImageFont, ImageColor
import uuid

def wrap_text(text, font, max_width):
    lines = []
    words = text.split()
    while words:
        line = ''
        while words and font.getsize(line + words[0])[0] <= max_width:
            line = f'{line} {words.pop(0)}' if line else words.pop(0)
        lines.append(line)
    return lines

def add_text_to_image(image, text, font_path, font_size, text_color, y_start=None):
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype(font_path, font_size)
    lines = wrap_text(text, font, image.width - 150)

    # Calculate vertical centering if y_start is not provided
    line_spacing = 1  # Add this line for custom line spacing

    total_text_height = sum(draw.textsize(line, font=font)[1] * line_spacing for line in lines)

    if y_start is None:
        y_start = (image.height - total_text_height) // 2

    for line in lines:
        text_width, text_height = draw.textsize(line, font=font)
        text_position = ((image.width - text_width) // 2, y_start)
        draw.text(text_position, line, font=font, fill=text_color)
        y_start += text_height * line_spacing

    return y_start  # Return the ending y position

def add_side_by_side_text(image, left_text, right_text, font_path, font_size, left_text_color, right_text_color, y_start):
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype(font_path, font_size)

    combined_text = f"{left_text} - {right_text}"
    text_width, text_height = draw.textsize(combined_text, font=font)

    x_start = (image.width - text_width) // 2
    text_position = (x_start, y_start)

    draw.text(text_position, combined_text, font=font, fill=left_text_color)

    return y_start + text_height

def add_logo_and_text(image, logo_path, text, font_path, font_size, text_color):
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype(font_path, font_size)

    # Load the logo image
    logo_image = Image.open(logo_path).convert("RGBA")  # Convert to RGBA for transparency

    # Calculate the new size while maintaining aspect ratio
    logo_height = 30
    aspect_ratio = logo_image.width / logo_image.height
    logo_image = logo_image.resize((int(logo_height * aspect_ratio), logo_height))

    # Calculate positions
    text_width, text_height = draw.textsize(text, font=font)
    total_width = logo_image.width + text_width - 5  # 5 pixels spacing between logo and text
    x_start = (image.width - total_width) // 2
    y_start = image.height - logo_image.height - 40  # 40 pixels from the bottom

    # Paste the logo image
    image.paste(logo_image, (x_start, y_start), logo_image.split()[3])  # Use the alpha channel as the mask

    # Draw the text
    text_position = (x_start + logo_image.width - 5, y_start + (logo_image.height - text_height) // 2)
    draw.text(text_position, text, font=font, fill=text_color)

    return image

def create_image_with_text(text1, text2, date_text, source_text, logo_text, width=1024, height=1024, overlay_color=(4, 4, 2, 204), font_path1="PTSansNarrow-Bold.ttf", font_path2="OpenSans-Regular.ttf", font_size1=40, font_size2=80, font_size3=10, font_size_logo=50, keyword=None):
    if keyword == "podvod":
        image_files = [f for f in os.listdir("random") if f.startswith("podvod")]
    elif keyword == "umela inteligence":
        image_files = [f for f in os.listdir("random") if f.startswith("umelainteligence")]
    else:
        image_files = os.listdir("random")

    if not image_files:
        raise ValueError("No images found in the 'random' directory.")

    random_image_path = random.choice(image_files)
    base_image = Image.open(os.path.join("random", random_image_path)).resize((width, height))

    overlay = Image.new('RGBA', base_image.size, overlay_color)
    img = Image.alpha_composite(base_image.convert('RGBA'), overlay)

    colors = [ImageColor.getrgb("#65ff00"), ImageColor.getrgb("#ff0000"), ImageColor.getrgb("#0000ff")]

    # Calculate the total height of all texts plus the spacing
    draw = ImageDraw.Draw(img)
    font1 = ImageFont.truetype(font_path1, font_size1)
    font2 = ImageFont.truetype(font_path2, font_size2)
    font3 = ImageFont.truetype(font_path2, font_size3)  # Font for date_text and source_text

    lines1 = wrap_text(text1, font1, img.width - 150)
    lines2 = wrap_text(text2, font2, img.width - 100)

    total_text_height = (
        sum(draw.textsize(line, font=font1)[1] for line in lines1) +
        sum(draw.textsize(line, font=font2)[1] for line in lines2) +
        draw.textsize(f"{date_text} - {source_text}", font=font3)[1] +  # Single line height for date_text and source_text combined
        40 + 40 + 40
    )

    # Calculate vertical centering
    y_start = (img.height - total_text_height) // 2

    # Add the first text
    y_end = add_text_to_image(img, text1, font_path1, font_size1, "#04F3F3", y_start)
    # Add the second text with 40px spacing
    y_end = add_text_to_image(img, text2, font_path2, font_size2, "#ffffff", y_end + 40)
    # Add the date and source text side by side with 40px spacing
    y_end = add_side_by_side_text(img, date_text, source_text, font_path2, font_size3, "#ffffff", "#ffffff", y_end + 20)
    # Add the logo text at the bottom
    img_with_logo = add_logo_and_text(img, "kyberzpravy-logo.png", "yberzpravy.cz", font_path1, font_size_logo, "#ffffff")

    return img_with_logo

text1 = "Před dovolenou si zálohujte telefon a fotkami se pochlubte raději až po návratu, radí kyberexpert"
text2 = "Ztráta kufru nebo zpožděný let není to nejhorší, co vás může na dovolené potkat. Na okamžik, kdy „přepnete“ do dovolenkového módu, totiž čekají kyberútočníci. Pro ně je období letních prázdnin ideální příležitostí, jak z lidí vylákat citlivé údaje, jako jsou třeba hesla k internetovému bankovnictví. Jak jim nenaletět, popsal pro Radiožurnál a iROZHLAS.cz Roman Pačka z Národního úřadu pro kybernetickou a informační bezpečnost (NÚKIB)"
date_text = "6. července 2024"
source_text = "www.seznam.cz"
logo_text = "yberzpravy.cz"  # Updated text without the 'K'
width = 1024
height = 1024
overlay_color = (6, 5, 37, 245) # Solid background color with transparency (0-255)
font_path1 = "Barlow-Bold.ttf"
font_path2 = "Inter-Regular.ttf"
font_size1 = 48
font_size2 = 28
font_size3 = 18
font_size_logo = 30  # Add this parameter for logo text size
keyword = "podvod"  # Change this to "umela inteligence" if needed

try:
    image = create_image_with_text(text1, text2, date_text, source_text, logo_text, width, height, overlay_color, font_path1, font_path2, font_size1, font_size2, font_size3, font_size_logo, keyword)

    output_filename = f"output_image_{uuid.uuid4()}.png"
    image.save(output_filename)
    print(f"Image saved as {output_filename}")
    image.show()  # To display

except ValueError as e:
    print(e)
