from urlextract import URLExtract
from wordcloud import WordCloud
import pandas as pd
from collections import Counter
import numpy as np
from PIL import Image
import emoji as emt
import re
from googletrans import Translator


extract = URLExtract()

def start_end(df):
    def get_day_with_suffix(day):
        if 4 <= day <= 20 or 24 <= day <= 30:
            suffix = "th"
        else:
            suffix = ["st", "nd", "rd"][day % 10 - 1]

        return str(day) + suffix

    day_number = df['day'].iloc[0]
    day_with_suffix = get_day_with_suffix(day_number)

    start_day = df['day_name'].iloc[0] + ', ' + str(df['month'].iloc[0]) + ' ' + day_with_suffix + ' ' + str(df['year'].iloc[0])
    
    day_number = df['day'].iloc[-1]
    day_with_suffix = get_day_with_suffix(day_number)

    end_day = df['day_name'].iloc[-1] + ', ' + str(df['month'].iloc[-1]) + ' ' + day_with_suffix + ' ' + str(df['year'].iloc[-1])

    return start_day,end_day
    

def fetch_stats(selected_user,df):

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    # fetch the number of messages
    num_messages = df.shape[0]

    # fetch the total number of words
    words = []
    for message in df['message']:
        words.extend(message.split())

    # fetch number of media messages
    num_media_messages = df[df['message'] == '<Media omitted>\n'].shape[0]

    # fetch number of links shared
    links = []
    for message in df['message']:
        links.extend(extract.find_urls(message))

    return num_messages,len(words),num_media_messages,len(links)

def dictionary(df):
    dicto = {}
    for i in range(24):
        dicto[i] = 0
    x = df['hour'].value_counts()
    labels = x.index.tolist()
    values = x.values.tolist()
    for i in range(len(labels)):
        dicto[labels[i]] = values[i]
    return dicto

def most_busy_users(df, num_users):
    x = df['user'].value_counts()
    top_users = x.head(num_users).index.tolist()
    other_users = x.tail(len(x) - num_users).index.tolist()
    return top_users, other_users

def most_busy_users_by_emoji(df, num_users):
    user_emoji_counts = {}
    for user, messages in df.groupby('user')['message']:
        emojis = []
        for message in messages:
            emojis.extend([c for c in message if emt.emoji_count(c) > 0])
        emoji_counter = Counter(emojis)
        user_emoji_counts[user] = sum(emoji_counter.values())

    sorted_users = sorted(user_emoji_counts.items(), key=lambda x: x[1], reverse=True)
    top_users_dict = {user[0]: user[1] for user in sorted_users[:num_users]}
    other_users_dict = {user[0]: user[1] for user in sorted_users[num_users:]}
    return top_users_dict, other_users_dict


def create_wordcloud(selected_user, df, frequency, num_words):
    f = open('stop_hinglish.txt', 'r')
    stop_words = f.read()

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    temp = df[df['user'] != 'group_notification']
    temp = temp[temp['message'] != '<Media omitted>\n']

    def remove_stop_words(message):
        y = []
        for word in message.lower().split():
            if word not in stop_words:
                y.append(word)
        return " ".join(y)

    # Load your custom shape image
    mask = np.array(Image.open("comment.png"))

    wc = WordCloud(width=500, height=500, min_font_size=10, background_color='white', max_words=num_words, max_font_size=frequency, mask=mask, contour_color='steelblue', contour_width=1)
    temp['message'] = temp['message'].apply(remove_stop_words)
    # Generate the word cloud image
    wordcloud = wc.generate(temp['message'].str.cat(sep=" "))
    return wordcloud

def most_common_words(selected_user,df):

    f = open('stop_hinglish.txt','r')
    stop_words = f.read()

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    temp = df[df['user'] != 'group_notification']
    temp = temp[temp['message'] != '<Media omitted>\n']

    words = []

    for message in temp['message']:
        for word in message.lower().split():
            if word not in stop_words:
                words.append(word)

    most_common_df = pd.DataFrame(Counter(words).most_common(20))
    return most_common_df

def emoji_helper(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    emojis = []
    for message in df['message']:
        emojis.extend([c for c in message if emt.emoji_count(c) > 0])

    emoji_counter = Counter(emojis)
    top_3_emojis = emoji_counter.most_common(3)
    top_3_emoji_string = ''.join([emoji for emoji, _ in top_3_emojis])

    return top_3_emoji_string


def emoji_occurrences(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    emojis = []
    for message in df['message']:
        emojis.extend([c for c in message if emt.emoji_count(c) > 0])

    emoji_counter = Counter(emojis)
    emoji_data = {'Emoji': [], 'Occurrences': []}

    for emoji, count in emoji_counter.items():
        emoji_data['Emoji'].append(emoji)
        emoji_data['Occurrences'].append(count)

    emoji_df = pd.DataFrame(emoji_data)
    emoji_df = emoji_df.sort_values(by='Occurrences', ascending=False)
    emoji_df = emoji_df.reset_index(drop=True) 
    return emoji_df


def monthly_timeline(selected_user,df):

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    timeline = df.groupby(['year', 'month_num', 'month']).count()['message'].reset_index()

    time = []
    for i in range(timeline.shape[0]):
        time.append(timeline['month'][i] + "-" + str(timeline['year'][i]))

    timeline['time'] = time

    return timeline

def daily_timeline(selected_user,df):

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    daily_timeline = df.groupby('only_date').count()['message'].reset_index()

    return daily_timeline

def week_activity_map(selected_user,df):

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    return df['day_name'].value_counts()

def month_activity_map(selected_user,df):

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    return df['month'].value_counts()

def activity_heatmap(selected_user,df):

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    heatmap_data = df.groupby(['day_name', 'hour']).size().unstack(fill_value=0)

    return heatmap_data


def read_whatsapp_chat(data):    
    pattern = r'\d{1,2}/\d{1,2}/\d{2},\s\d{1,2}:\d{1,2}\s(?:am|pm)\s-\s'
    message = re.split(pattern, data)[1:]
    dates = re.findall(pattern, data)
    dates = [date.replace('\u202f', '') for date in dates]

    df = pd.DataFrame({'Date': dates, 'Message': message})
    df['Date'] = pd.to_datetime(df['Date'], format='%d/%m/%y, %I:%M%p - ')

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

    return df

def format_message(sender, message, date, user_name, target_lang='en'):
    translator = Translator()
    translated_message = translator.translate(message, dest=target_lang).text
    timestamp = date.strftime("%d/%m/%Y %I:%M %p")
    if sender.strip() == user_name:
        return f'<div class="chat-bubble sender"><span class="sender-name">{sender}:</span> {translated_message}<br><span class="timestamp">{timestamp}</span></div>'
    elif sender.strip() == "group_notification":
        return f'<div class="chat-bubble center">{translated_message}<br><span class="timestamp">{timestamp}</span></div>'
    else:
        return f'<div class="chat-bubble receiver"><span class="sender-name">{sender}:</span> {translated_message}<br><span class="timestamp">{timestamp}</span></div>'


def chat_summarizer(df, start_date, end_date):
    start_date = pd.Timestamp(start_date)
    end_date = pd.Timestamp(end_date)
    
    filtered_df = df[(df['Date'] >= start_date) & (df['Date'] <= end_date)]
    
    # Calculate message length for each message
    filtered_df['Message Length'] = filtered_df['message'].apply(lambda x: len(x.split()))
    
    # Calculate average message length per user
    avg_msg_length_per_user = filtered_df.groupby('user')['Message Length'].mean().to_dict()
    
    total_emojis_per_user = filtered_df.groupby('user')['message'].apply(lambda x: sum([emt.emoji_count(c) for c in x])).to_dict()
    
    avg_messages = filtered_df.groupby('user').size().mean()

    summary = {
        'Total Messages': filtered_df.shape[0],
        'Users': filtered_df['user'].nunique(),
        'Top 5 Active Users': filtered_df['user'].value_counts().head().to_dict(),
        'Average Messages per User': filtered_df.groupby('user').size().mean(),
        'Average Message length per User':  dict(sorted(avg_msg_length_per_user.items(), key=lambda item: item[1])[::-1]),
        'Total Emojis per Person': dict(sorted(total_emojis_per_user.items(), key=lambda item: item[1])[::-1])
    }
    return summary


def senti(selected_user,df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    return df['sentiment'].value_counts()

def senti2(selected_user,df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    sentiment_over_time = df.groupby([pd.Grouper(key='Date', freq='D'), 'sentiment']).size().unstack(fill_value=0)

    return sentiment_over_time

def loveu(selected_user,df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    return df









    