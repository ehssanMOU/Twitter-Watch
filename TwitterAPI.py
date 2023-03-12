import tweepy
import json
import datetime
import openai
from textblob import TextBlob
import re
import string
import nltk
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
import configparser
from Conversation import Conversation
from Tweet import Tweet
from TwitterAccount import TwitterAccount

nltk.download('stopwords')
stop_words = stopwords.words('english')


class TwitterAPI:

    def __init__(self):

        config = configparser.ConfigParser()
        config.read('config.ini')

        self.api_key = config['twitter']['api_key']
        self.api_secret = config['twitter']['api_secret']

        self.access_key = config['twitter']['access_key']
        self.access_secret = config['twitter']['access_secret']

        self.openai_key = config['twitter']['openai_key']

        self.auth = tweepy.OAuthHandler(self.api_key, self.api_secret)

        self.auth.set_access_token(self.access_key, self.access_secret)

        self.api = tweepy.API(self.auth)

        self.conversations = {}

        self.json_data = {}

    def get_json_data(self):

        return self.json_data

    def get_openai_key(self):

        return self.openai_key

    def get_conversations(self):

        return self.conversations

    def set_conversations(self, author, conversations):

        self.conversations[author] = conversations

    def getAPI(self):

        return self.api

    def track(self):

        startDate = datetime.datetime(2023, 2, 1, 00, 00, 00, tzinfo=datetime.timezone.utc)

        api = self.getAPI()

        accounts = [TwitterAccount('@ylecun', Conversation()), TwitterAccount('@elonmusk', Conversation()),
                    TwitterAccount('@BarackObama', Conversation())]

        results = {}

        for account in accounts:

            tweets = api.user_timeline(screen_name=account.get_name())

            for tweet in tweets:

                tweetData, replies = self.get_tweets(api, account, tweet, startDate)

                if tweetData is None or replies is None:

                    continue

                tweetData.set_positivity(self.calculate_sentiment_score(tweetData.get_tweet_text()))

                for reply in replies:


                    reply_data = self.get_replies(reply, tweetData.get_tweet_id())

                    if reply_data is None:

                        continue

                    reply_data['positivity'] = self.calculate_sentiment_score(reply_data['tweet'])

                    account.set_audience(reply_data['author'])

                    tweetData.add_reply(reply_data)

                account.get_conversation().add_tweet(tweetData)

            results[account] = account.get_conversation()

            self.calculate_account_score(account)

        return results

    def extract_data(self):

        data = self.track()

        for account in data:

            self.json_data[account.get_name()] = {}
            self.json_data[account.get_name()]['tweetDetails'] = []
            self.json_data[account.get_name()]['audiences'] = account.get_audiences()
            self.json_data[account.get_name()]['Account Positivity'] = account.get_account_positivity()

            conversation = data[account]

            for tweet in conversation.get_tweets():

                tweet_data = {'ID': tweet.get_tweet_id(), 'tweet': tweet.get_tweet_text(),
                              'time of tweet': tweet.get_tweet_date(), 'replies': tweet.get_replies(),
                              'score': tweet.get_positivity()}

                self.json_data[account.get_name()]['tweetDetails'].append(tweet_data)

    def accountDescription(self, screenName):

        openai.api_key = self.get_openai_key()

        message = [{"role": "user", "content": f'Please generate 2 paragraphs summarization about twitter account of {screenName}.'
                                              f' First paragraph should summarize the general info on {screenName} '
                                              f'twitter account '
                                              f'and it should be around 200 words. Second paragraph should give a '
                                              f'summarization about tweets posted by'
                                              f'{screenName} and this part should be around 200 words.'}]

        response = openai.ChatCompletion.create(
            model='gpt-3.5-turbo',
            messages=message,
            max_tokens=800,
            n=1,
            stop=None,
            temperature=0.5,
        )

        reply = response.choices[0].message.content

        return reply





    def calculate_account_score(self, account):

        sentiments = []

        for tweet in account.get_conversation().get_tweets():

            text = self.clean_text(tweet.get_tweet_text())

            sentiments.append(self.calculate_sentiment_score(text))

        if len(sentiments) == 0:

            account.set_score(0)

        else:

            account.set_score(sum(sentiments) / len(sentiments))

    def calculate_sentiment_score(self, text):

        blob = TextBlob(text)

        sentiment_score = blob.sentiment.polarity

        return sentiment_score

    def clean_text(self, tweet):

        # Remove URLs
        text = re.sub(r'http\S+', '', tweet)

        # Remove mentions and hashtags
        text = re.sub(r'@\w+|\#', '', text)

        # Remove punctuation
        text = text.translate(str.maketrans("", "", string.punctuation))

        # Convert to lowercase
        text = text.lower()

        ps = PorterStemmer()

        # Remove stop words and stemming
        tokens = nltk.word_tokenize(text)
        tokens = [ps.stem(word) for word in tokens if not word in stop_words]

        # Remove words with only one character
        tokens = [word for word in tokens if len(word) > 1]

        return ' '.join(tokens)



    def get_replies(self, reply,tweetId):

        replyData = {}

        if reply.in_reply_to_status_id == tweetId:

            replyData['author'] = reply.user.screen_name

            replyData['tweet'] = self.remove_non_ascii(reply.full_text)

            replyData['timeOfReply'] = json.dumps(reply.created_at, default=str)

            print(replyData['author'])

            return replyData
        return None

    def remove_non_ascii(self, text):

        return ''.join(c for c in text if ord(c) < 128)

    def get_tweets(self, api,account,tweet, startDate):

        if tweet.created_at > startDate:
            time = json.dumps(tweet._json['created_at'], default=str)

            text = self.remove_non_ascii(tweet._json['text'])

            tweetId = tweet.id

            tweetData = Tweet(tweetId, time, text)

            replies = tweepy.Cursor(api.search_tweets, q='to:' + account.get_name(),
                                    since_id=tweetId,
                                    tweet_mode='extended').items(5)

            return tweetData, replies

        return None, None
