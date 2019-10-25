# Lyrics Generator Twitter Bot
The repository will contain code to load a GPT-2 model, perform text generation and create a Twitter Bot

## Examples

I fine-tuned 2 small GPT-2 models (124MB) and they both are running live on Twitter. The following samples correspond to the outputs of suchs models. 

**Eminem Bot Lyrics** ([@rap_god_bot](https://twitter.com/rap_god_bot))

<p align="center">
  <img width="500" height="600" src="https://github.com/jsalbert/lyrics-generator-twitter-bot/blob/master/samples/eminem_sample.png">
</p>

**Music Storytelling Bot Lyrics** ([@musicstorytell](https://twitter.com/musicstorytell))

<p align="center">
  <img width="500" height="600" src=https://github.com/jsalbert/lyrics-generator-twitter-bot/blob/master/samples/musicstorytell_sample.png>
</p>

## Cool Stuff that I Used/Learned Doing the Project

### GPT-2 and Transformer Models

### LyricsGenious Package 

In order to download all the song lyrics that I used to fine-tune the GPT-2 model, I used a great library called [LyricsGenious](https://github.com/johnwmillr/LyricsGenius). This package offers a really clean interface that interactuates with the [Genious API](https://genius.com/signup_or_login) and makes easy the download of lyrics. 

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

I used the Free Tier of [Amazon EC2 instances](https://aws.amazon.com/ec2/) to deploy the models. Even though they were the smallest GPT-2 models, they weren't fitting on RAM memory. The solution I opted to was creating a Swap file in the system. 

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
def print_text_in_image(text, font_path='Pillow/Tests/fonts/FreeMono.ttf', image_color=(245, 235, 225)):
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


