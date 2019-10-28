# Lyrics Generator Twitter Bot
The repository contains code to load a GPT-2 model, perform text generation and create a Twitter Bot that interact with Twitter users.

## Examples

I fine-tuned 2 small GPT-2 models (117MB) to generate Eminem lyrics as well as Storytelling lyrics.  The following samples correspond to the outputs of such models:

**Eminem Bot Lyrics** ([@rap_god_bot](https://twitter.com/rap_god_bot))

<p align="center">
  <img width="500" height="600" src="https://github.com/jsalbert/lyrics-generator-twitter-bot/blob/master/samples/eminem_sample.png">
</p>

**Music Storytelling Bot Lyrics** ([@musicstorytell](https://twitter.com/musicstorytell))

<p align="center">
  <img width="500" height="600" src=https://github.com/jsalbert/lyrics-generator-twitter-bot/blob/master/samples/musicstorytell_sample.png>
</p>

## How to run the code

1. Make sure you have python 3, pip installed:

```
$ sudo apt-get update
$ sudo apt-get install python3
$ sudo apt install python3-pip
```

2. Package will be installed if you write:

```
script/setup
```

3. Download the example model (a small 124M pre-trained GPT-2 model) or place yours under `models/` folder:

```
python3 download_example_model.py 
```

4. Open the file [run_twitter_bot.py](https://github.com/jsalbert/lyrics-generator-twitter-bot/blob/master/run_twitter_bot.py) and modify it with your model file path and twitter user information. 

5. Modify the [authentication files](https://github.com/jsalbert/lyrics-generator-twitter-bot/tree/master/files/authentication) to match your user / keys. More info on how to create a Twitter development account in the section below.


## Cool Stuff that I Used/Learned Doing the Project

### GPT-2 and Transformer Models

This year, [OpenAI](https://openai.com/) released a new set of language generation models: [GPT-2](https://openai.com/blog/better-language-models/). These large-scale unsupervised language models were able to generate coherent paragraphs of text while achieving state-of-the-art performance on many language modeling benchmarks.

For storage and memory purposes I decided to fine-tune the smallest one (117MB) though the 335MB was genenerating more diverse outputs. 

These are some resources that I used:

- Understand the Transformer architecture: [[Paper](https://s3-us-west-2.amazonaws.com/openai-assets/research-covers/language-unsupervised/language_understanding_paper.pdf)], [[Blog_1](https://openai.com/blog/language-unsupervised/)], [[Blog_2](http://jalammar.github.io/illustrated-transformer/)]
- Understand GPT-2: [[Paper](https://www.techbooky.com/wp-content/uploads/2019/02/Better-Language-Models-and-Their-Implications.pdf)], [[Blog_1](https://openai.com/blog/better-language-models/)], [[Blog_2](http://jalammar.github.io/illustrated-gpt2/)]
- Understand code, download models and fine-tune them: [[gpt-2-simple](https://github.com/minimaxir/gpt-2-simple)], [[OpenAI](https://github.com/openai/gpt-2)]


### LyricsGenious Package 

In order to download all the song lyrics that I used to fine-tune the GPT-2 model, I used a great library called [LyricsGenious](https://github.com/johnwmillr/LyricsGenius). This package offers a really clean interface that interacts with the [Genious API](https://genius.com/signup_or_login) and makes easy the download of lyrics. 

```
import lyricsgenius
genius = lyricsgenius.Genius("my_client_access_token_here")
artist = genius.search_artist("Eminem", max_songs=10, sort="title")
print(artist.songs)
```

### Twitter API and Tweepy

[Tweepy](https://www.tweepy.org/) is an easy-to-use Python library for accessing and interacting with the Twitter API.
Getting started is as simple as:
```
import tweepy

# Authenticate to Twitter
auth = tweepy.OAuthHandler("CONSUMER_KEY", "CONSUMER_SECRET")
auth.set_access_token("ACCESS_TOKEN", "ACCESS_TOKEN_SECRET")

# Create API object
api = tweepy.API(auth)

# Create a tweet
api.update_status("Hello Tweepy")
```
To use the Twitter API you will need to create a [developer account](https://developer.twitter.com/).
This [post](https://realpython.com/twitter-bot-python-tweepy/) was very useful to understand the API calls, functions and details that I needed to create my own Twitter Bot. 

### Swap files

I used the Free Tier of [Amazon EC2 instances](https://aws.amazon.com/ec2/) to deploy the models. Even though they were the smallest GPT-2 models, they weren't fitting on RAM memory. The solution I opted for was creating a Swap space in the system. 

```
Swap is a space on a disk that is used when the amount of physical RAM memory is full. When a Linux system runs out of RAM, inactive pages are moved from the RAM to the swap space.
```

I used the following code to allocate 2GB of space:

```
# Create a file which will be used for swap
sudo fallocate -l 2G /swapfile

# Set the correct permissions
sudo chmod 600 /swapfile

# Set up a Linux swap area
sudo mkswap /swapfile

# Enable the swap
sudo swapon /swapfile

# Verify the swap status
sudo swapon --show
```

Check this [blogpost](https://linuxize.com/post/create-a-linux-swap-file/) for more information. 

### Using PIL to Print Text in Images

I created a function to create an image and draw text on it using PIL. 

```
def print_text_in_image(text, font_path='Pillow/Tests/fonts/FreeMono.ttf', image_color=(255, 255, 225)):
    # Create a blank image
    # image = np.uint8(np.ones((1100, 1000, 3)) * 255)
    image = np.ones((1100, 1000, 3))

    # Give some color to the base image
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
```

### Sending E-mails with Python

I wanted to set up an automatic e-mail messaging service so every time the bot is down I could get a notification. I ended up using SMTP_SSL and a gmail account: 

```
import ssl
import json
import smtplib


class EmailSender:
    def __init__(self, authentication_json_path):
        with open(authentication_json_path, 'r') as f:
            authentication_params = json.load(f)

        self.password = authentication_params['PASSWORD']
        self.email = authentication_params['EMAIL']

        # Port for SSL
        self.port = 465

        # Create a secure SSL context
        self.context = ssl.create_default_context()

    def send_email(self, email_receiver, message):
        with smtplib.SMTP_SSL("smtp.gmail.com", self.port, context=self.context) as server:
            server.login(self.email, self.password)
            server.sendmail(self.email, email_receiver, message)
```

More information about how to set an e-mail service can be found [here](https://realpython.com/python-send-email/).

