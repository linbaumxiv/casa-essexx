import tweepy
import os
from dotenv import load_dotenv

# Loads the keys from .env file
load_dotenv()

# Assign the keys
api_key = os.getenv('TWITTER_API_KEY')
api_secret = os.getenv('TWITTER_API_SECRET')
access_token = os.getenv('TWITTER_ACCESS_TOKEN')
access_token_secret = os.getenv('TWITTER_ACCESS_TOKEN_SECRET')

# Set up the Client (V2 API)
client = tweepy.Client(
    consumer_key=api_key,
    consumer_secret=api_secret,
    access_token=access_token,
    access_token_secret=access_token_secret
)

try:
    print("Connecting to X...")
    response = client.create_tweet(text="Hello from my Django eCommerce API! 🚀 #Python #Django")
    print("Success! Tweet ID:", response.data['id'])
except Exception as e:
    print(f"Error: {e}")