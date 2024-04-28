# def preprocess(data):
#     import re
#     import pandas as pd

#     pattern = r'\d{1,2}/\d{1,2}/\d{2},\s\d{1,2}:\d{1,2}\s(?:am|pm)\s-\s'
#     message=re.split(pattern,data)[1:]
#     dates = re.findall(pattern, data)
#     dates = [date.replace('\u202f', '') for date in dates]

#     df=pd.DataFrame({'Date':dates,'Message':message})
#     df['Date'] = pd.to_datetime(df['Date'], format='%d/%m/%y, %I:%M%p - ')

#     users = []
#     messages = []
#     for message in df['Message']:
#         entry = re.split('([\w\W]+?):\s', message)
#         if entry[1:]:
#             users.append(entry[1])
#             messages.append(" ".join(entry[2:]))
#         else:
#             users.append('group_notification')
#             messages.append(entry[0])
#     df['user'] = users
#     df['message'] = messages
#     df.drop(columns=['Message'], inplace=True)

#     df['only_date'] = df['Date'].dt.date
#     df['year'] = df['Date'].dt.year
#     df['month_num'] = df['Date'].dt.month
#     df['month'] = df['Date'].dt.month_name()
#     df['day'] = df['Date'].dt.day
#     df['day_name'] = df['Date'].dt.day_name()
#     df['hour'] = df['Date'].dt.hour
#     df['minute'] = df['Date'].dt.minute


#     df=df[df['user'] != 'group_notification']
#     return df



import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import re
import pandas as pd


def preprocess(data):
    # pattern = r'\d{1,2}/\d{1,2}/\d{2},\s\d{1,2}:\d{1,2}\s(?:am|pm)\s-\s'
    # message=re.split(pattern,data)[1:]
    # dates = re.findall(pattern, data)
    # dates = [date.replace('\u202f', '') for date in dates]

    # df=pd.DataFrame({'Date':dates,'Message':message})
    # df['Date'] = pd.to_datetime(df['Date'], format='%d/%m/%y, %I:%M%p - ')

    pattern = '\d{1,2}/\d{1,2}/\d{2,4},\s\d{1,2}:\d{2}\s-\s'

    messages = re.split(pattern, data)[1:]
    dates = re.findall(pattern, data)

    df = pd.DataFrame({'user_message': messages, 'message_date': dates})
    # convert message_date type
    df['message_date'] = pd.to_datetime(df['message_date'], format='%d/%m/%Y, %H:%M - ')

    df.rename(columns={'Message': 'Date'}, inplace=True)


    users = []
    messages = []
    for message in df['Message']:
        entry = re.split('([\w\W]+?):\s', message)
        if entry[1:]:
            users.append(entry[1])
            messages.append(" ".join(entry[2:]))
        else:
            users.append('group_notification')
            messages.append(entry[0])
    df['user'] = users
    df['message'] = messages
    df.drop(columns=['Message'], inplace=True)

    df['only_date'] = df['Date'].dt.date
    df['year'] = df['Date'].dt.year
    df['month_num'] = df['Date'].dt.month
    df['month'] = df['Date'].dt.month_name()
    df['day'] = df['Date'].dt.day
    df['day_name'] = df['Date'].dt.day_name()
    df['hour'] = df['Date'].dt.hour
    df['minute'] = df['Date'].dt.minute
    
    def analyze_sentiment(message):
        sid = SentimentIntensityAnalyzer()
        sentiment_scores = sid.polarity_scores(message)
        
        if sentiment_scores['compound'] >= 0.05:
            sentiment_label = 'positive'
        elif sentiment_scores['compound'] <= -0.05:
            sentiment_label = 'negative'
        else:
            sentiment_label = 'neutral'
        
        return sentiment_label, sentiment_scores

    sentiment_labels = []

    for index, row in df.iterrows():
        sentiment_label, _ = analyze_sentiment(row['message'])
        sentiment_labels.append(sentiment_label)
    df['sentiment'] = sentiment_labels

    df=df[df['user'] != 'group_notification']
    return df

