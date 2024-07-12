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
    lines = wrap_text(text, font, image.width - 40)

    # Calculate vertical centering if y_start is not provided
    total_text_height = sum(draw.textsize(line, font=font)[1] for line in lines)
    if y_start is None:
        y_start = (image.height - total_text_height) // 2

    for line in lines:
        text_width, text_height = draw.textsize(line, font=font)
        text_position = ((image.width - text_width) // 2, y_start)
        draw.text(text_position, line, font=font, fill=text_color)
        y_start += text_height

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

def add_logo_text_to_image(image, logo_text, font_path, font_size, colors):
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype(font_path, font_size)
    parts = logo_text.split()

    # Calculate the total width of the logo text
    total_text_width = sum(draw.textsize(part, font=font)[0] for part in parts) + (len(parts) - 1) * 5
    x_offset = (image.width - total_text_width) // 2
    y_offset = image.height - font_size - 40  # 20 pixels from the bottom

    for part, color in zip(parts, colors):
        text_width, text_height = draw.textsize(part, font=font)
        text_position = (x_offset, y_offset)
        draw.text(text_position, part, font=font, fill=color)
        x_offset += text_width + 5

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

    lines1 = wrap_text(text1, font1, img.width - 40)
    lines2 = wrap_text(text2, font2, img.width - 40)

    total_text_height = (
        sum(draw.textsize(line, font=font1)[1] for line in lines1) +
        sum(draw.textsize(line, font=font2)[1] for line in lines2) +
        draw.textsize(f"{date_text} - {source_text}", font=font3)[1] +  # Single line height for date_text and source_text combined
        40 + 40 + 40
    )

    # Calculate vertical centering
    y_start = (img.height - total_text_height) // 2

    # Add the first text
    y_end = add_text_to_image(img, text1, font_path1, font_size1, "#00ffc9", y_start)
    # Add the second text with 40px spacing
    y_end = add_text_to_image(img, text2, font_path2, font_size2, "#ffffff", y_end + 20)
    # Add the date and source text side by side with 40px spacing
    y_end = add_side_by_side_text(img, date_text, source_text, font_path2, font_size3, "#ffffff", "#ffffff", y_end + 20)
    # Add the logo text at the bottom
    img_with_logo = add_logo_text_to_image(img, logo_text, font_path1, font_size_logo, colors)

    return img_with_logo

text1 = "Před dovolenou si zálohujte telefon a fotkami se pochlubte raději až po návratu, radí kyberexpert"
text2 = "Ztráta kufru nebo zpožděný let není to nejhorší, co vás může na dovolené potkat. Na okamžik, kdy „přepnete“ do dovolenkového módu, totiž čekají kyberútočníci. Pro ně je období letních prázdnin ideální příležitostí, jak z lidí vylákat citlivé údaje, jako jsou třeba hesla k internetovému bankovnictví. Jak jim nenaletět, popsal pro Radiožurnál a iROZHLAS.cz Roman Pačka z Národního úřadu pro kybernetickou a informační bezpečnost (NÚKIB)"
date_text = "6. července 2024"
source_text = "www.seznam.cz"
logo_text = "KyberZpravy.cz"
width = 1024
height = 1024
overlay_color = (4, 4, 2, 204)  # Solid background color with transparency (0-255)
font_path1 = "PTSansNarrow-Bold.ttf"
font_path2 = "OpenSans-Regular.ttf"
font_size1 = 55
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
