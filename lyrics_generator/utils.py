import re
import os
import json
import numpy as np

from PIL import Image, ImageDraw, ImageFont


def mkdir(path):
    """
    Args:
        path: Path where directory will be created
    Returns: Nothing. Creates directory with the path specified
    """
    if not os.path.exists(path):
        os.makedirs(path)


def is_valid_prefix(string, pattern=r'[^a-z0-9A-Z.!?,\n\'\" ]'):
    """
    Args:
        string: String to perform search
        pattern: Pattern of characters to search for
    Returns: False if the string contains any character outside the pattern specified
    """
    return not bool(re.compile(pattern).search(string))


def generate_random_parametres():
    """

    Returns: Random length, temperature and top_k parameters from a predefined range of values.

    """
    length = np.random.randint(256, 481)
    temperature = [0.7, 0.8, 0.9][np.random.randint(0, 3)]
    top_k = np.random.randint(0, 41)

    return length, temperature, top_k


def limit_sentence_len(sentence, max_len):
    count, initial_index = 0, 0
    new_sentences = []
    # Separate by words
    sentence_split = sentence.split(' ')
    for i, s in enumerate(sentence_split):
        # +1 to count the spaces
        count += len(s) + 1
        if count >= max_len:
            new_sentences.append(' '.join(sentence_split[initial_index:i]) + '\n')
            initial_index = i
            count = len(s)
    new_sentences.append(' '.join(sentence_split[initial_index:i + 1]) + '\n')
    return new_sentences


def process_lyrics(lyrics, max_len_sentence):
    new_lyrics = []
    sentences = lyrics[0].split('\n')
    for sentence in sentences:
        if len(sentence) > max_len_sentence:
            new_lyrics += limit_sentence_len(sentence, max_len_sentence)
        else:
            new_lyrics += [sentence + '\n']

    if new_lyrics[:-1] == '\n':
        new_lyrics = new_lyrics[:-1]
    return new_lyrics


def pick_random_font():
    # Get a font randomly
    font_name = ['Allura-Regular.otf', 'Bilbo-Regular.otf'][np.random.randint(0, 2)]
    return os.path.join('/'.join(os.path.dirname(os.path.realpath(__file__)).split('/')[:-2]), 'fonts', font_name)


def print_text_in_image(text, font_path='Pillow/Tests/fonts/FreeMono.ttf', image_color=(245, 235, 225)):
    # Create a blank image
    # image = np.uint8(np.ones((1100, 1000, 3)) * 255)
    image = np.ones((1100, 1000, 3))

    # Give some colour to the base image
    image[:, :, 0] *= image_color[0]
    image[:, :, 1] *= image_color[1]
    image[:, :, 2] *= image_color[2]
    image = np.uint8(image)

    # Create a PIL Image
    pil_image = Image.fromarray(image, 'RGB')

    font = ImageFont.truetype(font_path, 40)

    # Get a drawing context
    d = ImageDraw.Draw(pil_image)

    # Margins
    vertical_coord = 50
    horizontal_margin = 50

    # Draw text, full opacity
    for sentence in text:
        d.text((horizontal_margin, vertical_coord), sentence, font=font, fill=(0, 0, 0, 255))
        vertical_coord += 40
    return pil_image


def load_since_id(path):
    with open(path, 'r') as f:
        file = json.load(f)
    return file['since_id']


def write_since_id_json(path, since_id):
    with open(path, 'w') as f:
        json.dump({'since_id': since_id}, f, indent=4)
