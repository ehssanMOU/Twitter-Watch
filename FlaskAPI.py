from flask import Flask, request, jsonify
from flask_restful import Resource, Api
import nltk
from nltk.corpus import stopwords
from TwitterAPI import TwitterAPI

nltk.download('stopwords')
stop_words = stopwords.words('english')

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False
api = Api(app)

twitter_api = TwitterAPI()


@app.route('/accounts')
def threads():
    try:
        twitter_api.extract_data()

        return twitter_api.get_json_data()

    except:

        return "please retry again. Something went wrong"


@app.route('/sentiment')
def sentimentAnal():
    sentiment_data = {}

    try:

        json_data = twitter_api.get_json_data()

        for account in json_data:

            print(account)

            sentiment_data[account] = {}
            sentiment_data[account]['tweet'] = []

            sentiment_data[account]['score'] = json_data[account]['Account Positivity']

            for data in json_data[account]['tweetDetails']:

                tweet_and_tweet_score = {'tweet': data['tweet'], 'score': data['score'], 'replies': []}

                for reply in data['replies']:
                    reply_and_reply_score = {'reply': reply['tweet'], 'score': reply['positivity']}

                    tweet_and_tweet_score['replies'].append(reply_and_reply_score)

                sentiment_data[account]['tweet'].append(tweet_and_tweet_score)

        return sentiment_data

    except:

        return "please make sure the name you provided is correct or make sure to first got to accounts page"


@app.route('/accountDescription/<username>')
def getDescription(username):
    author = '@' + username


    try:
        return twitter_api.accountDescription(author)

    except:

        return "please make sure the name you provided is correct or make sure to first got to accounts page"



@app.route('/audience/<twitterhandle>')
def getActiveAudience(twitterhandle):
    author = '@' + twitterhandle

    try:

        return twitter_api.get_json_data()[author]['audiences']

    except:

        return "please make sure the name you provided is correct or make sure to first got to accounts page"


if __name__ == '__main__':
    app.run(debug=True, port=8000)
