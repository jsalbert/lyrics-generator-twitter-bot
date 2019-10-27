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

    def search_most_popular_tweets_of_day(self, query, n_tweets=2):
        """
        Will search for the most popular n_tweets of the day
        Args:
            query: Tweepy search query
            n_tweets: Number of tweets we want to gather

        Returns: A list with the tweets full text and a list with the favourites count for that tweets.

        """
        # Current date
        date_now = datetime.datetime.now().date()

        text_tweets = []
        favorites_count = []

        for page in tweepy.Cursor(self.api.search, q=query, count=100, tweet_mode='extended').pages(5):
            text_tweets_page, favorites_counts_page, date_exceeded = self._process_page(date_now, page)
            text_tweets += text_tweets_page
            favorites_count += favorites_counts_page
            if date_exceeded:
                break
        text_tweets, favorites_count = np.array(text_tweets), np.array(favorites_count)
        filter_indices = np.argsort(np.array(favorites_count))[::-1][0:n_tweets]

        return text_tweets[filter_indices].tolist(), favorites_count[filter_indices].tolist()

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
