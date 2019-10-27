import json
import time
import tweepy


from email_service.email_sender import EmailSender
from lyrics_generator.twitter_bot import TwitterBot
from lyrics_generator.gpt_2 import LyricsGenerator, utils


# Variables to set

# GPT-2 Model files
gpt_2_model_directory = 'models/model_1'

# Twitter files
twitter_user = '@'
authentication_twitter_json_path = 'files/authentication/authentication_twitter.json'
since_id_json_path = 'files/last_since_id.json'

# If you want to receive error messages
authentication_email_json_path = 'files/authentication/authentication_email.json'


def reply_mentions(twitter_bot, lyrics_generator, keyword, since_id):
    new_since_id = since_id
    for tweet in tweepy.Cursor(twitter_bot.api.mentions_timeline, since_id=since_id).items():
        new_since_id = max(tweet.id, new_since_id)
        if keyword in tweet.text.lower():
            prefix = tweet.text.replace(keyword, '')[1:]
            print('Generating Lyrics')
            try:
                lyrics = lyrics_generator.generate_lyrics(prefix=prefix, random_parametres=True)
                image_paths = lyrics_generator.save_lyrics_app_default(lyrics,
                                                                       max_lines=25,
                                                                       font_path='fonts/Bilbo-Regular.otf',
                                                                       image_color=(255, 255, 255))
                status = '@' + tweet.user.screen_name + '\n' + prefix
                print('Posting Status replying to ', '@' + tweet.user.screen_name)
                twitter_bot.post_tweet_with_images(image_paths, status=status[0:280], in_reply_to_status_id=tweet.id)
            except:
                pass

    return new_since_id


if __name__ == '__main__':
    if authentication_email_json_path:
        email_sender = EmailSender(authentication_email_json_path)

    print('Loading Lyrics Generator Model')
    lyrics_gen = LyricsGenerator(gpt_2_model_directory)

    print('Creating Twitter Bot')
    twitter_bot = TwitterBot(authentication_twitter_json_path)

    try:
        since_id = utils.load_since_id(since_id_json_path)
        print('Last tweet replied loaded correctly')
    except:
        print('Error loading last tweet / There was no last tweet')
        since_id = 1

    print('Running...')

    try:
        while True:
            try:
                print('Replying mentions...')
                since_id = reply_mentions(twitter_bot, lyrics_gen, twitter_user, since_id)
            except tweepy.RateLimitError:
                print('Exception reached... sleeping 15 minutes :(')
                time.sleep(900)

            utils.write_since_id_json(since_id_json_path, new_since_id)
            print('Sleeping 3 minutes...')
            time.sleep(180)

    except Exception as e:
        message = 'An error ocurred:\n' + str(e)
        print(message)
        if authentication_email_json_path:
            email_sender.send_email(email_sender.email, message)
