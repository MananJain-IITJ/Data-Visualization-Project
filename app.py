import streamlit as st
import preprocessor
import helper
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

@st.cache_data
def preprocess_data(data):
    bytes_data = data.getvalue()
    data = bytes_data.decode("utf-8")
    return preprocessor.preprocess(data)

st.set_page_config(page_title="WhatsApp Chat Analyzer", page_icon=":speech_balloon:")
st.sidebar.title("Whatsapp Chat Analyzer")

uploaded_file = st.sidebar.file_uploader("Choose a file")


if uploaded_file is not None:
    df = preprocess_data(uploaded_file)

    user_list = df['user'].unique().tolist()
    if 'group_notification' in user_list:
        user_list.remove('group_notification')
    user_list.sort()
    user_list.insert(0,"Overall")

    selected_user = st.sidebar.selectbox("Show analysis wrt",user_list)

    # if st.sidebar.button("Show Analysis"):

    option1=st.sidebar.checkbox("Show Analysis")

    if option1:

        st_st,end_st=helper.start_end(df)
        message_box = f"""
        <div style="display: flex; flex-direction: row; justify-content: space-between; border: 2px solid black; border-radius: 10px; padding: 20px; background-color: #f0f0f0;">
            <div style="flex-grow: 1;">
                <h2 style="margin-bottom: 0; color: #333; font-size: 20px;">First Message</h2>
                <p style="margin-top: 0; color: #666; font-size: 35px;">{st_st}</p>
            </div>
            <div style="flex-grow: 2; text-align: right;">
                <p style="margin-top: 0; color: #666; font-size: 35px;">{end_st}</p>
                <h2 style="margin-top: 0; color: #333; font-size: 20px;">Last Message</h2>
            </div>
        </div>
        """

        # Display the custom message box
        st.markdown(message_box, unsafe_allow_html=True)

        # Stats Area
        st.markdown("<h1 style='text-align: center;'>Statistics</h1>", unsafe_allow_html=True)
        # Stats Area
        stats_col1, stats_col2, stats_col3, stats_col4, stats_col5 = st.columns(5)

        # Custom CSS for styling
        st.markdown(
            """
            <style>
            /* Style for statistics columns */
            .stats-column {
                padding: 20px;
                border-radius: 10px;
                box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
                background-color: #f9f9f9;
                text-align: center;
            }

            /* Style for metric value */
            .metric-value {
                font-size: 24px;
                font-weight: bold;
                color: #333;
            }

            /* Style for metric label */
            .metric-label {
                font-size: 16px;
                color: #666;
            }
            </style>
            """,
            unsafe_allow_html=True,
        )

        # Statistic 1: Total Messages
        with stats_col1:
            st.markdown(
                "<div class='stats-column'><div class='metric-value'>{}</div><div class='metric-label'>Total Messages</div></div>".format(
                    helper.fetch_stats(selected_user, df)[0]
                ),
                unsafe_allow_html=True,
            )

        # Statistic 2: Total Words
        with stats_col2:
            st.markdown(
                "<div class='stats-column'><div class='metric-value'>{}</div><div class='metric-label'>Total Words</div></div>".format(
                    helper.fetch_stats(selected_user, df)[1]
                ),
                unsafe_allow_html=True,
            )

        # Statistic 3: Media Shared
        with stats_col3:
            st.markdown(
                "<div class='stats-column'><div class='metric-value'>{}</div><div class='metric-label'>Media Shared</div></div>".format(
                    helper.fetch_stats(selected_user, df)[2]
                ),
                unsafe_allow_html=True,
            )

        # Statistic 4: Links Shared
        with stats_col4:
            st.markdown(
                "<div class='stats-column'><div class='metric-value'>{}</div><div class='metric-label'>Links Shared</div></div>".format(
                    helper.fetch_stats(selected_user, df)[3]
                ),
                unsafe_allow_html=True,
            )
        with stats_col5:
            st.markdown(
                "<div class='stats-column'><div class='metric-value'>{}</div><div class='metric-label'>Most Used Emoji</div></div>".format(
                    helper.emoji_helper(selected_user, df)
                ),
                unsafe_allow_html=True,
            )

        st.markdown("<h1 style='text-align: center;'>Chat Timeline</h1>", unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        # Monthly timeline
        with col1:
            timeline = helper.monthly_timeline(selected_user, df)
            fig = go.Figure(go.Scatter(x=timeline['time'], y=timeline['message'], mode='lines', line=dict(color='green')))
            fig.update_layout(title_text="Monthly Timeline", xaxis_tickangle=-45, yaxis_title="Message", plot_bgcolor='white')
            st.plotly_chart(fig, use_container_width=True)  # Adjust width to fit container

        # Daily timeline
        with col2:
            daily_timeline = helper.daily_timeline(selected_user, df)
            fig = go.Figure(go.Scatter(x=daily_timeline['only_date'], y=daily_timeline['message'], mode='lines', line=dict(color='black')))
            fig.update_layout(title_text="Daily Timeline", xaxis_tickangle=-45, yaxis_title="Message", plot_bgcolor='white')
            st.plotly_chart(fig, use_container_width=True)  # Adjust width to fit container

        # activity map
        st.markdown("<h1 style='text-align: center;'>Activity</h1>", unsafe_allow_html=True)
        col1,col2 = st.columns(2)

        with col1:
            busy_day = helper.week_activity_map(selected_user,df)
            fig,ax = plt.subplots()
            ax.bar(busy_day.index,busy_day.values,color='green')
            plt.xticks(rotation=45)
            plt.title("Day")
            st.pyplot(fig)

        with col2:
            busy_month = helper.month_activity_map(selected_user, df)
            fig, ax = plt.subplots()
            ax.bar(busy_month.index, busy_month.values,color='green')
            plt.xticks(rotation=45)
            plt.title("Month")
            st.pyplot(fig)

        st.markdown("<h1 style='text-align: center;'>Message Distribution</h1>", unsafe_allow_html=True)
        num_users = st.slider("Choose number of users", min_value=1, max_value=len(df['user'].unique()), value=2)

        top_users, other_users = helper.most_busy_users(df, num_users)

        col1, col2 = st.columns(2)
        with col1:
            x = df['user'].value_counts()
            labels = top_users + ['Other']
            if num_users!=len(df['user'].unique()):
                values = x[top_users].tolist() + [x[other_users].sum()]
            else:
                values = x[top_users].tolist()

            fig1 = go.Figure(data=[go.Pie(labels=labels, values=values, hole=0.3)])
            fig1.update_layout(title_text="Person", title_x=0.27, title_font_size=20)
            st.plotly_chart(fig1, use_container_width=True)

        with col2:
            fig2 = px.bar()
            for user in top_users:
                df_user = df[df['user'] == user]
                user_dict = helper.dictionary(df_user)
                fig2.add_bar(x=list(user_dict.keys()), y=list(user_dict.values()), name=user)

            if len(other_users) > 0:
                other_dict = helper.dictionary(df[df['user'].isin(other_users)])
                fig2.add_bar(x=list(other_dict.keys()), y=list(other_dict.values()), name='Other')

            fig2.update_layout(xaxis_title='Hour', yaxis_title='Message', title='Hourly Distribution of Users',title_x=0.27)
            st.plotly_chart(fig2, use_container_width=True)



        st.markdown("<h1 style='text-align: center;'>Word Cloud</h1>", unsafe_allow_html=True)

        frequency = st.slider("Frequency", min_value=10, max_value=200, value=100)
        num_words = st.slider("Number of Words", min_value=1, max_value=100, value=20)

        # Generate Wordcloud
        wordcloud = helper.create_wordcloud(selected_user, df, frequency, num_words)

        # Display the word cloud
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.imshow(wordcloud, interpolation='bilinear')
        ax.axis("off")
        st.pyplot(fig)


        st.markdown("<h1 style='text-align: center;'>Message Heatmap</h1>", unsafe_allow_html=True)
        st.markdown("<h1 style='text-align: center;'></h1>", unsafe_allow_html=True)
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.heatmap(helper.activity_heatmap(selected_user,df), cmap='viridis', annot=True, fmt='d', linewidths=.5, ax=ax)
        plt.xlabel('Hour of the Day')
        plt.ylabel('Day of the Week')
        plt.yticks(rotation=0)  
        st.pyplot(fig)


        st.markdown("<h1 style='text-align: center;'>Emoji Analysis</h1>", unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            num_users = st.slider("Choose number of users", min_value=1, max_value=len(df['user'].unique()), value=2, key="num_users_slider")
            a, b = helper.most_busy_users_by_emoji(df, num_users)
            values = list(a.values())
            labels = list(a.keys())
            if num_users != len(df['user'].unique()):
                values.append(sum(list(b.values())))
                labels.append("Others")
            fig1 = go.Figure(data=[go.Pie(labels=labels, values=values, hole=0.3)])
            fig1.update_layout(title_text="Person", title_x=0.27, title_font_size=20)
            st.plotly_chart(fig1, use_container_width=True)

        with col2:
            st.header("Emoji DataFrame")
            st.dataframe(helper.emoji_occurrences(selected_user, df))

        st.markdown("<h1 style='text-align: center;'>Chat Symmary</h1>", unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        min_date = pd.to_datetime("2000-01-01")
        max_date = pd.to_datetime("2025-01-31")
        with col1:
            start_date = st.date_input("Start Date", min_value=min_date, max_value=max_date, value=min_date)
        with col2:    
            end_date = st.date_input("End Date", min_value=min_date, max_value=max_date, value=max_date)

        summary = helper.chat_summarizer(df, start_date, end_date)
        st.write("### Chat Summary between", start_date, "and", end_date)
        st.write(summary)

        


if uploaded_file is not None:
    st.sidebar.title("Chat History With Filters")
    option2 = st.sidebar.checkbox("Show Chat")
    if option2:
        st.empty()
        whatsapp_style = """
        <style>
        /* Chat container */
        .chat-container {
            display: flex;
            flex-direction: column;
            padding-right: 20px;
        }

        /* Chat bubble for Anshu (sender) */
        .sender {
            background-color: #dcf8c6; /* Light green background */
            color: #000; /* Black text color */
            border-radius: 10px;
            padding: 10px;
            margin: 5px 0;
            max-width: 70%;
            display: inline-block;
            word-wrap: break-word;
            align-self: flex-end;
            margin-left: 30%; /* Adjust as needed */
        }

        /* Chat bubble for other users (receiver) */
        .receiver {
            background-color: white;
            color: #000; /* Black text color */
            border-radius: 10px;
            padding: 10px;
            margin: 5px 0;
            max-width: 70%;
            display: inline-block;
            word-wrap: break-word;
            align-self: flex-start;
            margin-right: 30%; /* Adjust as needed */
        }
        /* Chat bubble for center-aligned messages */
        .center {
            background-color: white;
            color: #000; /* Black text color */
            border-radius: 10px;
            padding: 10px;
            margin: 5px 0;
            max-width: 70%;
            display: inline-block;
            word-wrap: break-word;
            align-self: center; /* Center align */
        }

        /* Sender name */
        .sender-name {
            color: #128C7E;
            font-weight: bold;
        }

        /* Message timestamp */
        .timestamp {
            color: #767676;
            font-size: 0.8em;
            margin-left: 10px;
        }
        </style>
        """

        st.markdown(whatsapp_style, unsafe_allow_html=True)

        st.title("WhatsApp Chat Viewer")


        st.write("### Filter Chat by Date Range:")
        min_date = pd.to_datetime("2000-01-01")
        max_date = pd.to_datetime("2025-01-31")
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("Start Date", min_value=min_date, max_value=max_date, value=min_date)
        with col2:    
            end_date = st.date_input("End Date", min_value=min_date, max_value=max_date, value=max_date)
        col1, col2,col3 = st.columns(3)
        with col1:
            user_input = st.text_input("Type your WhatsApp name:", "")
        with col2:
            target_lang = st.selectbox("Select Target Language:", ["en", "fr", "es", "de","hi","bn"]) 
        with col3:    
            search_query = st.text_input("Enter Search Keyword:")

    
        st.write("### Chat Preview:")
        data = uploaded_file.getvalue().decode("utf-8")
        df = helper.read_whatsapp_chat(data)
        filtered_df = df[(df['Date'] >= pd.Timestamp(start_date)) & (df['Date'] <= pd.Timestamp(end_date))]

        if search_query:
            filtered_df = filtered_df[filtered_df['message'].str.contains(search_query, case=False)]

    
        for index, row in filtered_df.iterrows():
            formatted_message = helper.format_message(row['user'], row['message'], row['Date'], user_input, target_lang)
            st.markdown(f'<div class="chat-container">{formatted_message}</div>', unsafe_allow_html=True)


if uploaded_file is not None:
    st.sidebar.title("Chat sentiment")
    option3 = st.sidebar.checkbox("Show sentiment")
    if option3:
        st.markdown("<h1 style='text-align: center;'>Sentiment Analysis</h1>", unsafe_allow_html=True)
        selected_user1 = st.sidebar.selectbox("Show Sentiment wrt",user_list)
        col1, col2 = st.columns(2)
        with col1:
            sentiment_distribution = helper.senti(selected_user1,df)
            fig_sentiment_distribution = go.Figure(data=[go.Pie(labels=sentiment_distribution.index, values=sentiment_distribution.values)])
            fig_sentiment_distribution.update_layout(title_text="Sentiment Distribution")
            fig_sentiment_distribution.update_traces(marker=dict(colors=['blue','green','red']))
            st.plotly_chart(fig_sentiment_distribution, use_container_width=True)

        with col2:
            sentiment_over_time = helper.senti2(selected_user1,df)
            fig_sentiment_over_time = go.Figure()
            for sentiment in sentiment_over_time.columns:
                fig_sentiment_over_time.add_trace(go.Scatter(x=sentiment_over_time.index, y=sentiment_over_time[sentiment], mode='lines', name=sentiment))
            
            fig_sentiment_over_time.update_layout(title_text="Sentiment Variation Over Time", xaxis_title="Date", yaxis_title="Count")
            st.plotly_chart(fig_sentiment_over_time, use_container_width=True)

        selected_sentiment = st.selectbox("Select Sentiment", ["Overall", "Positive", "Negative", "Neutral"])

        df1=helper.loveu(selected_user1,df)

        filtered_df=df1.copy(deep=True)
        # Filter DataFrame based on selected sentiment
        if selected_sentiment != "Overall":
            filtered_df = df1[df1["sentiment"] == selected_sentiment.lower()]

        # Apply row highlighting based on sentiment
        def highlight_row(row):
            color = ""
            if selected_sentiment == "Overall":
                if row["sentiment"] == "positive":
                    color = "green"
                elif row["sentiment"] == "negative":
                    color = "red"
                elif row["sentiment"] == "neutral":
                    color = "blue"
            else:
                if row["sentiment"] == "positive":
                    color = "green"
                elif row["sentiment"] == "negative":
                    color = "red"
                elif row["sentiment"] == "neutral":
                    color = "blue"
            return [f"background-color: {color}"] * len(row)

        # Apply row highlighting to DataFrame
        styled_df = filtered_df.style.apply(highlight_row, axis=1)

        # Display the styled DataFrame
        st.dataframe(styled_df)







    


if uploaded_file is None or ( not option1 and not option2 and not option3):
    whatsapp_intro = (
        "Welcome to the WhatsApp Chat Analyzer! This project is aimed at providing insights "
        "and visualizations from WhatsApp chat data. It allows users to upload their chat "
        "data and gain insights into their communication patterns."
    )

    # Introduction texts for Anshu, Yash, and Manan
    anshu_intro = (
        "Hi, I'm Anshu Raj. I'm passionate about data analysis and visualization. "
        "Excited to be part of this WhatsApp chat analysis project!"
    )

    yash_intro = (
        "Hi, I'm Yash. I'm enthusiastic about data science and machine learning. "
        "Looking forward to analyzing WhatsApp chat data with this app!"
    )

    manan_intro = (
        "Hey, I'm Manan. I have a passion for coding and exploring new technologies. "
        "Excited to contribute to this WhatsApp chat analysis project!"
    )

    # Column 1: WhatsApp logo
    st.image("watsapp_logo.png", width=200)

    # Column 2: WhatsApp intro
    st.markdown(
        f"<h2 style='text-align: left; color: #0066CC;'>About the WhatsApp Chat Analyzer</h2>", 
        unsafe_allow_html=True
    )
    st.markdown(whatsapp_intro)

    # Display individual photos and intros in a vertical layout
    for name, img, intro in [("Anshu Raj", "Anshu.png", anshu_intro), ("Yash Mangal", "Yash.jpeg.jpg", yash_intro), ("Manan Jain", "Manan.jpeg.jpg", manan_intro)]:
        st.image(img, width=300)
        st.markdown(f"<h3 style='text-align: left; color: #0066CC;'>{name}</h3>", 
                    unsafe_allow_html=True)
        st.markdown(intro)
        st.markdown("---")  # Add a horizontal line for separation

    # Add a button for user interaction
    if st.button("Learn More"):
        st.write("To be Updated soon.......")

