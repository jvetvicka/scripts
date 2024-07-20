import os
import random
from PIL import Image, ImageDraw, ImageFont, ImageColor
import uuid

def wrap_text(text, font, max_width):
    lines = []
    words = text.split()
    while words:
        line = ''
        while words and font.getbbox(line + ' ' + words[0])[2] <= max_width:  # Add space before words[0]
            line = f'{line} {words.pop(0)}' if line else words.pop(0)
        lines.append(line)
    return lines

def add_text_to_image(image, text, font_path, font_size, text_color, y_start=None):
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype(font_path, font_size)
    lines = wrap_text(text, font, image.width - 150)

    line_spacing = 1  # Add this line for custom line spacing
    total_text_height = sum(draw.textbbox((0, 0), line, font=font)[3] * line_spacing for line in lines)

    if y_start is None:
        y_start = (image.height - total_text_height) // 2

    for line in lines:
        text_width, text_height = draw.textbbox((0, 0), line, font=font)[2:]
        text_position = ((image.width - text_width) // 2, y_start)
        draw.text(text_position, line, font=font, fill=text_color)
        y_start += text_height * line_spacing

    return y_start  # Return the ending y position

def add_side_by_side_text(image, left_text, right_text, keyword, font_path, font_size, left_text_color, right_text_color, keyword_color, y_start):
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype(font_path, font_size)

    # Text před keyword
    text_before_keyword = f"{left_text} - {right_text} - "
    # Text s keyword
    combined_text = f"{text_before_keyword}{keyword}"
    
    # Vykreslit text před keyword
    text_before_keyword_width, text_height = draw.textbbox((0, 0), text_before_keyword, font=font)[2:]
    x_start = (image.width - draw.textbbox((0, 0), combined_text, font=font)[2]) // 2
    text_position = (x_start, y_start)
    draw.text(text_position, text_before_keyword, font=font, fill=left_text_color)

    # Vykreslit keyword
    keyword_position = (text_position[0] + text_before_keyword_width, y_start)
    draw.text(keyword_position, keyword, font=font, fill=keyword_color)
    
    # Vykreslit text po keyword
    text_after_keyword = ""
    draw.text((keyword_position[0] + draw.textbbox((0, 0), keyword, font=font)[2], y_start), text_after_keyword, font=font, fill=right_text_color)

    return y_start + text_height

def add_logo_and_text(image, logo_path, text, font_path, font_size, text_color):
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype(font_path, font_size)

    logo_image = Image.open(logo_path).convert("RGBA")  # Convert to RGBA for transparency

    logo_height = 30
    aspect_ratio = logo_image.width / logo_image.height
    logo_image = logo_image.resize((int(logo_height * aspect_ratio), logo_height))

    text_width, text_height = draw.textbbox((0, 0), text, font=font)[2:]
    total_width = logo_image.width + text_width - 5  # 5 pixels spacing between logo and text
    x_start = (image.width - total_width) // 2
    y_start = image.height - logo_image.height - 40  # 40 pixels from the bottom

    image.paste(logo_image, (x_start, y_start), logo_image.split()[3])  # Use the alpha channel as the mask

    text_position = (x_start + logo_image.width - 5, y_start + (logo_image.height - text_height) // 2)
    draw.text(text_position, text, font=font, fill=text_color)

    return image

def create_image_with_text(text1, text2, date_text, source_text, logo_text, width=1024, height=1024, overlay_color=(4, 4, 2, 204), font_path1="PTSansNarrow-Bold.ttf", font_path2="OpenSans-Regular.ttf", font_size1=40, font_size2=80, font_size3=10, font_size_logo=50, keyword=None):
    if len(text2) > 500:
        text2 = text2[:500] + "..."
    if keyword == "podvod":
        image_files = [f for f in os.listdir("random") if f.startswith("podvod")]
    elif keyword == "dezinformace":
        image_files = [f for f in os.listdir("random") if f.startswith("dezinformace")]
    else:
        image_files = ['default.jpg']

    if not image_files:
        image_files = ['default.jpg']  # Use default image
        # Ensure the default image is in the directory
        if 'default.jpg' not in image_files:
            raise FileNotFoundError("Default image 'default.jpg' not found in the 'random' directory.")
    
    random_image_path = random.choice(image_files)
    base_image = Image.open(os.path.join("random", random_image_path)).resize((width, height))


    overlay = Image.new('RGBA', base_image.size, overlay_color)
    img = Image.alpha_composite(base_image.convert('RGBA'), overlay)

    colors = [ImageColor.getrgb("#65ff00"), ImageColor.getrgb("#ff0000"), ImageColor.getrgb("#0000ff")]

    draw = ImageDraw.Draw(img)
    font1 = ImageFont.truetype(font_path1, font_size1)
    font2 = ImageFont.truetype(font_path2, font_size2)
    font3 = ImageFont.truetype(font_path2, font_size3)

    lines1 = wrap_text(text1, font1, img.width - 150)
    lines2 = wrap_text(text2, font2, img.width - 100)

    total_text_height = (
        sum(draw.textbbox((0, 0), line, font=font1)[3] for line in lines1) +
        sum(draw.textbbox((0, 0), line, font=font2)[3] for line in lines2) +
        draw.textbbox((0, 0), f"{date_text} - {source_text}", font=font3)[3] +
        40 + 40 + 40
    )

    y_start = (img.height - total_text_height) // 2

    y_end = add_text_to_image(img, text1, font_path1, font_size1, "#04F3F3", y_start)
    y_end = add_text_to_image(img, text2, font_path2, font_size2, "#ffffff", y_end + 40)
    y_end = add_side_by_side_text(img, date_text, source_text, keyword, font_path2, font_size3, "#ffffff", "#ffffff", "#04F3F3", y_end + 20)
    img_with_logo = add_logo_and_text(img, "kyberzpravy-logo.png", "yberzpravy.cz", font_path1, font_size_logo, "#ffffff")

    return img_with_logo

text1 = "Před dovolenou si zálohujte telefon a fotkami se pochlubte raději až po návratu, radí kyberexpert"
text2 = "Akcie americké kybernetické společnosti CrowdStrike dnes prudce oslabují, v jednu chvíli odepisovaly až téměř 15 procent, než ztráty zmírnily. Firma je považována za hlavního viníka výpadku globálních počítačových systémů, který způsobila aktualizace jejího softwaru na systémech Windows od společnosti Microsoft. Agentura Reuters uvedla, že dnešní událost by mohla zákazníky a investory přimět k tomu, aby se poohlédli po jiných dodavatelích Další text aby to bylo delší a uvidí se, co to udělá. Ted - u toho ted to uz ma 500 znaků, na který je nastavený trimování."
date_text = "6. července 2024"
source_text = "www.seznam.cz"
logo_text = "yberzpravy.cz"
width = 1024
height = 1024
overlay_color = (6, 5, 37, 245)
font_path1 = "Barlow-Bold.ttf"
font_path2 = "Inter-Regular.ttf"
font_size1 = 48
font_size2 = 28
font_size3 = 18
font_size_logo = 30
keyword = "dezinformace"

try:
    image = create_image_with_text(text1, text2, date_text, source_text, logo_text, width, height, overlay_color, font_path1, font_path2, font_size1, font_size2, font_size3, font_size_logo, keyword)

    output_filename = f"output_image_{uuid.uuid4()}.png"
    image.save(output_filename)
    print(f"Image saved as {output_filename}")
    image.show()

except ValueError as e:
    print(e)
