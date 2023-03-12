

class Tweet:

    def __init__(self, tweetId, tweetDate, tweetText):
        self.tweet_id = tweetId

        self.tweet_date = tweetDate

        self.tweet_text = tweetText

        self.replies = []

        self.positivity = 0

    def get_positivity(self):

        return self.positivity

    def set_positivity(self, positivity):

        self.positivity = positivity

    def get_tweet_id(self):
        return self.tweet_id

    def get_tweet_date(self):
        return self.tweet_date

    def get_tweet_text(self):
        return self.tweet_text

    def get_replies(self):

        return self.replies

    def add_reply(self, reply):

        self.replies.append(reply)
