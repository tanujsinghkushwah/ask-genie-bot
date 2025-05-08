import os
import time
import argparse
import random
import base64
import io
from datetime import datetime
import requests
from dotenv import load_dotenv
import tweepy
import google.generativeai as genai
import schedule
from PIL import Image

# Load environment variables
load_dotenv()

# Twitter API credentials
API_KEY = os.getenv('API_KEY')
API_KEY_SECRET = os.getenv('API_KEY_SECRET')
ACCESS_TOKEN = os.getenv('ACCESS_TOKEN')
ACCESS_TOKEN_SECRET = os.getenv('ACCESS_TOKEN_SECRET')
BEARER_TOKEN = os.getenv('BEARER_TOKEN', '')  # Make bearer token optional

# Gemini API credentials
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
genai.configure(api_key=GEMINI_API_KEY)

# Conversation history for each interaction
conversation_history = {}

# Keywords to search for
KEYWORDS = [
    "Interview", "Software Engineer", "Leetcode", 
    "System Design", "High Level Design", "Low Level Design", 
    "AI", "Blockchain", "Crypto"
]

class GenieTweetBot:
    def __init__(self):
        # Initialize Twitter client
        self.client = tweepy.Client(
            bearer_token=BEARER_TOKEN if BEARER_TOKEN else None,  # Make bearer token optional
            consumer_key=API_KEY,
            consumer_secret=API_KEY_SECRET,
            access_token=ACCESS_TOKEN,
            access_token_secret=ACCESS_TOKEN_SECRET
        )
        
        # Initialize Twitter API v1.1 for media uploads
        auth = tweepy.OAuth1UserHandler(
            API_KEY, API_KEY_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET
        )
        self.api = tweepy.API(auth)
        
        # Initialize Gemini model
        self.model = genai.GenerativeModel('gemini-2.0-flash')
        self.image_model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Get own user ID
        try:
            self.me = self.client.get_me()
            self.user_id = self.me.data.id
            print(f"Bot initialized for user: {self.me.data.username}")
        except Exception as e:
            print(f"Warning: Could not get user information: {e}")
            print("Some features like mention tracking may not work properly.")
            self.user_id = None
    
    def generate_ai_response(self, prompt, conversation_id=None):
        """Generate an AI response using Gemini API"""
        try:
            # If this is part of a conversation, use history
            if conversation_id and conversation_id in conversation_history:
                history = conversation_history[conversation_id]
                history.append({"role": "user", "parts": [prompt]})
                chat = self.model.start_chat(history=history)
                response = chat.send_message(prompt)
            else:
                # New conversation
                response = self.model.generate_content(prompt)
                
                if conversation_id:
                    conversation_history[conversation_id] = [
                        {"role": "user", "parts": [prompt]},
                        {"role": "model", "parts": [response.text]}
                    ]
            
            return response.text
        except Exception as e:
            print(f"Error generating AI response: {e}")
            return None
    
    def generate_image_prompt(self, topic):
        """Generate a prompt for image creation based on the topic"""
        prompt = f"""
        Create a detailed image description for a tech-related image about '{topic}'. 
        The image should be visually appealing and informative. 
        Keep the description under 100 words and focus on visual elements.
        """
        
        response = self.model.generate_content(prompt)
        return response.text
    
    def create_image_from_dalle(self, prompt):
        """Generate an image using DALL-E API (placeholder for future implementation)"""
        # This is a placeholder function for future integration with DALL-E or similar
        # For now, we'll return a placeholder image
        try:
            # Generate a simple gradient image as a placeholder
            width, height = 1024, 1024
            image = Image.new('RGB', (width, height), color='white')
            
            # Save image to a buffer
            img_buffer = io.BytesIO()
            image.save(img_buffer, format='JPEG')
            img_buffer.seek(0)
            
            return img_buffer
        except Exception as e:
            print(f"Error creating image: {e}")
            return None
    
    def search_tweets(self, query, max_results=10):
        """Search for tweets based on keywords"""
        try:
            # Exclude retweets and replies for better results
            formatted_query = f"{query} -is:retweet -is:reply"
            
            # Search for recent tweets
            tweets = self.client.search_recent_tweets(
                query=formatted_query,
                max_results=max_results,
                tweet_fields=['created_at', 'author_id', 'conversation_id']
            )
            
            if not tweets.data:
                print(f"No tweets found for query: {query}")
                return []
                
            return tweets.data
        except Exception as e:
            print(f"Error searching tweets: {e}")
            return []
    
    def get_mentions(self, since_id=None):
        """Get mentions directed at the bot"""
        try:
            # Get mentions
            mentions = self.client.get_users_mentions(
                id=self.user_id,
                since_id=since_id,
                tweet_fields=['created_at', 'author_id', 'conversation_id']
            )
            
            if not mentions.data:
                print("No new mentions found")
                return []
                
            return mentions.data
        except Exception as e:
            print(f"Error getting mentions: {e}")
            return []
    
    def post_tweet(self, text, with_image=False, image_topic=None):
        """Post a tweet with optional image"""
        try:
            if with_image and image_topic:
                # Generate image prompt
                image_prompt = self.generate_image_prompt(image_topic)
                
                # Generate image
                img_buffer = self.create_image_from_dalle(image_prompt)
                
                if img_buffer:
                    # Upload media
                    media = self.api.media_upload(filename='image.jpg', file=img_buffer)
                    
                    # Post tweet with media
                    response = self.client.create_tweet(
                        text=text,
                        media_ids=[media.media_id]
                    )
                else:
                    # Fallback to text-only tweet
                    response = self.client.create_tweet(text=text)
            else:
                # Text-only tweet
                response = self.client.create_tweet(text=text)
                
            print(f"Tweet posted successfully: {response.data['id']}")
            return response.data['id']
        except Exception as e:
            print(f"Error posting tweet: {e}")
            return None
    
    def reply_to_tweet(self, tweet_id, text):
        """Reply to a specific tweet"""
        try:
            response = self.client.create_tweet(
                text=text,
                in_reply_to_tweet_id=tweet_id
            )
            print(f"Reply posted successfully: {response.data['id']}")
            return response.data['id']
        except Exception as e:
            print(f"Error replying to tweet: {e}")
            return None
    
    def interact_with_keyword_tweets(self):
        """Find and interact with tweets containing keywords"""
        print(f"Searching for tweets with keywords...")
        
        # Select random keyword to search for
        keyword = random.choice(KEYWORDS)
        
        # Get tweets containing the keyword
        tweets = self.search_tweets(keyword, max_results=5)
        
        if not tweets:
            return
        
        # Select a random tweet to interact with
        tweet = random.choice(tweets)
        
        # Generate a response
        original_tweet = self.client.get_tweet(tweet.id).data
        tweet_text = original_tweet.text
        
        prompt = f"""
        You are AskMeGenie, a helpful AI assistant specializing in software engineering, tech trends, and career advice.
        
        Here's a tweet: "{tweet_text}"
        
        Craft a thoughtful, informative reply that demonstrates expertise while being humble and curious. 
        Keep it under 240 characters and make it engaging without using hashtags.
        """
        
        response = self.generate_ai_response(prompt, conversation_id=str(tweet.id))
        
        if response:
            # Reply to the tweet
            self.reply_to_tweet(tweet.id, response)
            print(f"Interacted with tweet: {tweet.id}")
    
    def respond_to_mentions(self, since_id=None):
        """Respond to mentions of the bot"""
        print("Checking for mentions...")
        
        # Get mentions
        mentions = self.get_mentions(since_id=since_id)
        
        if not mentions:
            return since_id
        
        newest_id = since_id
        
        for mention in mentions:
            if newest_id is None or mention.id > newest_id:
                newest_id = mention.id
            
            # Get the tweet text
            tweet = self.client.get_tweet(mention.id).data
            tweet_text = tweet.text
            
            # Generate response
            prompt = f"""
            You are AskMeGenie, a helpful AI assistant specializing in software engineering, tech trends, and career advice.
            
            A user has mentioned you in this tweet: "{tweet_text}"
            
            Respond helpfully and concisely (under 240 characters). If they're asking a question, provide a clear answer.
            If unclear, ask for clarification. Maintain a helpful, humble tone.
            """
            
            response = self.generate_ai_response(prompt, conversation_id=str(mention.id))
            
            if response:
                # Reply to the mention
                self.reply_to_tweet(mention.id, response)
                print(f"Responded to mention: {mention.id}")
        
        return newest_id
    
    def generate_tech_post(self):
        """Generate and post content about latest tech trends"""
        print("Generating tech post...")
        
        # Randomly decide if post should include an image
        with_image = random.choice([True, False])
        
        # Generate post content
        prompt = """
        You are AskMeGenie, a tech thought leader.
        
        Generate a viral, insightful tweet about a current tech trend, software engineering best practice, 
        or career advice that would be valuable to developers and tech professionals.
        
        The tweet should be under 240 characters, thought-provoking, and valuable without using hashtags.
        Make it sound authentic and conversational, not promotional.
        """
        
        post_content = self.generate_ai_response(prompt)
        
        if post_content:
            # If with image, we need a topic for the image
            image_topic = None
            if with_image:
                # Extract main topic from post content
                topic_prompt = f"""
                Extract the main tech topic from this tweet in 2-3 words only: "{post_content}"
                Just respond with those 2-3 words, nothing else.
                """
                image_topic = self.generate_ai_response(topic_prompt)
            
            # Post the tweet
            self.post_tweet(post_content, with_image=with_image, image_topic=image_topic)
            print("Tech post generated and posted")

def run_bot(task=None):
    """Run the bot with specified task or all tasks"""
    bot = GenieTweetBot()
    
    # Last mention ID to track new mentions
    last_mention_id = None
    
    if task == 'keyword':
        bot.interact_with_keyword_tweets()
    elif task == 'mentions':
        last_mention_id = bot.respond_to_mentions(last_mention_id)
    elif task == 'post':
        bot.generate_tech_post()
    else:
        # Run all tasks
        bot.generate_tech_post()
        bot.interact_with_keyword_tweets()
        last_mention_id = bot.respond_to_mentions(last_mention_id)

def setup_schedule():
    """Set up scheduled tasks"""
    # Post at 9 AM and 5 PM
    schedule.every().day.at("09:00").do(run_bot, task='post')
    schedule.every().day.at("17:00").do(run_bot, task='post')
    
    # Check mentions every 2 hours
    schedule.every(2).hours.do(run_bot, task='mentions')
    
    # Interact with keyword tweets 3 times a day
    schedule.every().day.at("11:00").do(run_bot, task='keyword')
    schedule.every().day.at("15:00").do(run_bot, task='keyword')
    schedule.every().day.at("19:00").do(run_bot, task='keyword')
    
    print("Schedule set up")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the AskMeGenie Twitter Bot")
    parser.add_argument('--task', type=str, choices=['keyword', 'mentions', 'post', 'all'], 
                        default='all', help='Specific task to run')
    parser.add_argument('--schedule', action='store_true', help='Run with scheduling')
    
    args = parser.parse_args()
    
    if args.schedule:
        setup_schedule()
        print("Bot started with scheduling. Press Ctrl+C to exit.")
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)
        except KeyboardInterrupt:
            print("Bot stopped")
    else:
        print(f"Running bot with task: {args.task}")
        run_bot(args.task) 