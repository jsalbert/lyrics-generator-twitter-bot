import json
import tweepy
import datetime
import numpy as np


class TwitterBot:
    def __init__(self, authentication_json_path):
        self.api = self._get_twitter_api(authentication_json_path)

    @staticmethod
    def _get_twitter_api(authentication_json_path):
        with open(authentication_json_path, 'r') as f:
            authentication_params = json.load(f)

        auth = tweepy.OAuthHandler(authentication_params['CONSUMER_KEY'], authentication_params['CONSUMER_SECRET'])
        auth.set_access_token(authentication_params['ACCESS_TOKEN'], authentication_params['ACCESS_TOKEN_SECRET'])

        # Create API object
        api = tweepy.API(auth)

        try:
            api.verify_credentials()
            print("Twitter Bot correctly authenticated")
        except BaseException:
            raise Exception("Error during authentication")

        return api

    @staticmethod
    def _process_page(date_now, page):
        text_tweets = []
        favorites_count = []
        date_exceeded = False
        for tweet in page:
            if tweet.created_at.date() >= date_now:
                if 'RT @' not in tweet.full_text:
                    text_tweets.append(tweet.full_text)
                    favorites_count.append(tweet.favorite_count)
            else:
                date_exceeded = True
                break

        return text_tweets, favorites_count, date_exceeded

    def post_tweet_with_images(self, image_paths, status, in_reply_to_status_id=None):
        media_ids = []
        if not isinstance(image_paths, list):
            image_paths = [image_paths]

        for filename in image_paths:
            res = self.api.media_upload(filename)
            media_ids.append(res.media_id)

        # tweet with multiple images
        self.api.update_status(status=status, media_ids=media_ids, in_reply_to_status_id=in_reply_to_status_id)

    def post_tweet(self, status):
        self.api.update_status(status=status)
