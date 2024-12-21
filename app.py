import streamlit as st
import openai
import requests
from datetime import datetime
from dotenv import load_dotenv
import os
import schedule
import time

# Load environment variables from .env file
load_dotenv()

# Initialize OpenAI API with environment variable (ensure you set the key in .env)
# openai.api_key = os.getenv("OPENAI_API_KEY")  # Fetch the OpenAI API key from .env file
openai.api_key = ""  # Replace with your actual OpenAI API key

# Telegram Bot Token and Channel Chat ID (replace with your actual values)
TELEGRAM_BOT_TOKEN = "7845194271:AAHd07FXO4UB4aAw24xlXmMFnGkV6Q4v1JQ"  # Replace with your actual Telegram bot token
TELEGRAM_CHAT_ID = "-1002496992612"  # Your Telegram channel username (e.g., @newsdilak)

# Function to send messages to Telegram
def send_to_telegram(message):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": message,
            "parse_mode": "HTML"  # Ensures that HTML is parsed and links are clickable
        }
        response = requests.post(url, data=payload)
        response.raise_for_status()  # Will raise an error for bad responses
        return response.ok
    except requests.exceptions.RequestException as e:
        st.error(f"Error sending message to Telegram: {e}")
        return False

# Function to fetch scholarship news using NewsAPI
def fetch_scholarship_news():
    API_KEY = ""  # Fetch the NewsAPI key from environment variables

    try:
        url = f'https://newsapi.org/v2/everything?q=student+scholarship+deadline&apiKey={API_KEY}'
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for HTTP errors
        news_data = response.json()

        articles = []
        for article in news_data.get('articles', []):
            articles.append({
                'title': article['title'],
                'url': article['url'],
                'category': 'scholarship'
            })

        return articles
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching news: {e}")
        return []

# Function to generate and summarize news with emojis
def generate_and_send_news(news_data):
    if not news_data:
        return "No news articles to summarize."

    prompt = f"Today is {datetime.now().strftime('%B %d, %Y')}. Below are the generated scholarship news articles with clickable links and emojis:\n\n"

    emoji_map = {
        "scholarship": "🎓",
        "technology": "💻",
        "international": "🌎",
        "women": "👩‍💻",
        "general": "📰"
    }

    # Add clickable links and emojis to the prompt
    for news in news_data:
        title = news.get('title', 'No Title')
        link = news.get('url', '#')
        category = news.get('category', 'general')
        emoji = emoji_map.get(category, "📰")
        prompt += f"- {emoji} <a href='{link}'>{title}</a>\n"

    prompt += (
        "\nSummarize these articles with concise, attractive points, and use emojis to make them engaging."
    )

    try:
        # Generate summary using GPT-4
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=300
        )

        summary = response['choices'][0]['message']['content'].strip()

        # Format message for Telegram and send
        telegram_message = f"<b>Scholarship News Updates</b>\n\n" + summary
        send_to_telegram(telegram_message)

        return summary
    except openai.error.OpenAIError as e:
        st.error(f"Error with OpenAI API: {e}")
        return "Error generating summary."

# Function to run the job and fetch/send news
def job():
    # Fetch scholarship news
    scholarship_news = fetch_scholarship_news()

    # Display the scholarship news articles with clickable links in Streamlit
    if scholarship_news:
        st.subheader("Latest Scholarship News Articles")
        for news in scholarship_news:
            title = news.get('title', 'No Title')
            link = news.get('url', '#')
            st.markdown(f"🎓 [{title}]({link})")  # This makes the link clickable in Streamlit
    else:
        st.write("No scholarship news available at the moment.")

    # Generate and display news summary
    st.subheader("Generated Summary for Today's News")
    summary_today = generate_and_send_news(scholarship_news)
    st.write(summary_today)

# Streamlit app layout
st.title("🎓 Scholarship News Updates")
st.markdown("Get AI-generated scholarship news updates, categorized and enhanced with engaging emojis!")

# Schedule the job to run at 8 AM, 1 PM, and 6 PM every day
schedule.every().day.at("03:30").do(job)
schedule.every().day.at("03:35").do(job)
schedule.every().day.at("03:40").do(job)

# Streamlit app loop (to run the job continuously)
while True:
    schedule.run_pending()
    time.sleep(60)  # Wait for one minute before checking again
