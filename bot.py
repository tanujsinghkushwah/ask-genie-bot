import os
import time
import argparse
import random
import base64
import io
from datetime import datetime
import requests
import firebase_admin
from firebase_admin import credentials, remote_config
import asyncio # Required for template.load()
import tweepy
import google.generativeai as genai
import schedule
from PIL import Image, ImageDraw, ImageFont
import textwrap

# Hardcoded ultimate fallbacks, used if Remote Config is entirely unavailable
# and get_config_value isn't called with a specific default.
# These are passed to init_server_template's default_config.
ULTIMATE_FALLBACK_DEFAULTS = {
    'API_KEY': 'YOUR_FALLBACK_API_KEY_IN_CODE',
    'API_KEY_SECRET': 'YOUR_FALLBACK_API_KEY_SECRET_IN_CODE',
    'ACCESS_TOKEN': 'YOUR_FALLBACK_ACCESS_TOKEN_IN_CODE',
    'ACCESS_TOKEN_SECRET': 'YOUR_FALLBACK_ACCESS_TOKEN_SECRET_IN_CODE',
    'GEMINI_API_KEY': 'YOUR_FALLBACK_GEMINI_API_KEY_IN_CODE',
    'BEARER_TOKEN': '',
    'IMAGE_ROUTER_API': '',
    'STABLE_HORDE_KEY': ''
}

def initialize_firebase_and_load_config():
    """Initializes Firebase app and loads Remote Config template."""
    try:
        firebase_admin.get_app()
    except ValueError:
        cred = credentials.Certificate('serviceAccountKey.json')
        firebase_admin.initialize_app(cred)
    
    print("Initializing Remote Config server template...")
    # Initialize with ultimate fallbacks. Remote values will override these.
    template = remote_config.init_server_template(default_config=ULTIMATE_FALLBACK_DEFAULTS)
    
    print("Loading Remote Config template from Firebase backend...")
    try:
        asyncio.run(template.load()) # Fetches the template and merges with defaults
        print("Remote Config template loaded successfully.")
    except Exception as e:
        print(f"ERROR loading Remote Config template from backend: {e}")
        print("Proceeding with ULTIMATE_FALLBACK_DEFAULTS or specific get_config_value defaults.")
        # If load fails, template still contains ULTIMATE_FALLBACK_DEFAULTS

    print("Evaluating Remote Config template...")
    return template.evaluate() # Returns a firebase_admin.remote_config.Config object

def get_config_value(evaluated_config, key, default_value=""):
    """Gets a config value from the evaluated Remote Config object."""
    try:
        # Attempt to get the value as a string, common for env vars
        value = evaluated_config.get_string(key)
        source = evaluated_config.get_value_source(key)
        # print(f"Retrieved '{key}' from Remote Config: '{value}' (Source: {source})") # Optional: verbose logging
        return value
    except ValueError:
        # This can happen if the key exists but is not a string (e.g., boolean, number)
        # or, more commonly, if the key is not found (neither remote nor in init_server_template's defaults)
        # In this case, we rely on the default_value passed to this function.
        # print(f"Key '{key}' not found as string or not string type in evaluated_config. Using function default: '{default_value}'.") # Optional: verbose logging
        return default_value
    except Exception as e:
        print(f"Error fetching '{key}' from evaluated_config: {e}. Using function default: '{default_value}'.")
        return default_value

# --- Initialize Firebase and Load Remote Config ONCE at startup ---
evaluated_remote_config = initialize_firebase_and_load_config()
# ------------------------------------------------------------------

# Twitter API credentials
API_KEY = get_config_value(evaluated_remote_config, 'API_KEY', ULTIMATE_FALLBACK_DEFAULTS['API_KEY'])
API_KEY_SECRET = get_config_value(evaluated_remote_config, 'API_KEY_SECRET', ULTIMATE_FALLBACK_DEFAULTS['API_KEY_SECRET'])
ACCESS_TOKEN = get_config_value(evaluated_remote_config, 'ACCESS_TOKEN', ULTIMATE_FALLBACK_DEFAULTS['ACCESS_TOKEN'])
ACCESS_TOKEN_SECRET = get_config_value(evaluated_remote_config, 'ACCESS_TOKEN_SECRET', ULTIMATE_FALLBACK_DEFAULTS['ACCESS_TOKEN_SECRET'])
BEARER_TOKEN = get_config_value(evaluated_remote_config, 'BEARER_TOKEN', ULTIMATE_FALLBACK_DEFAULTS['BEARER_TOKEN'])

# Gemini API credentials
GEMINI_API_KEY = get_config_value(evaluated_remote_config, 'GEMINI_API_KEY', ULTIMATE_FALLBACK_DEFAULTS['GEMINI_API_KEY'])
genai.configure(api_key=GEMINI_API_KEY)

# Image Router API 
IMAGE_ROUTER_API_KEY = get_config_value(evaluated_remote_config, 'IMAGE_ROUTER_API', ULTIMATE_FALLBACK_DEFAULTS['IMAGE_ROUTER_API'])

# Stable Horde API key
STABLE_HORDE_API_KEY = get_config_value(evaluated_remote_config, 'STABLE_HORDE_KEY', ULTIMATE_FALLBACK_DEFAULTS['STABLE_HORDE_KEY'])

# Conversation history for each interaction
conversation_history = {}

# Keywords to search for
KEYWORDS = [
    "Interview", "Software Engineer", "Leetcode", 
    "System Design", "High Level Design", "Low Level Design", 
    "AI", "Blockchain", "Crypto", "Cloud Computing", "DevOps",
    "Microservices", "Database", "Caching", "Operating Systems",
    "Kubernetes", "Docker", "Machine Learning", "Tech News"
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
        """Generate a detailed prompt for image creation based on the topic"""
        prompt = f"""
        Create a detailed image prompt for a visually captivating tech-related image about '{topic}'. 
        
        Your image prompt should:
        - Be very specific and detailed (at least 50 words)
        - Include visual elements that would draw attention on social media
        - Describe lighting, style, mood, and composition
        - Mention vibrant colors and high contrast elements
        - Avoid mentioning text or words in the image
        - Have a modern, professional aesthetic
        
        Format your response as a single paragraph with no introductions or explanations.
        """
        
        response = self.model.generate_content(prompt)
        # Limit to 300 characters for Stable Horde API
        image_prompt = response.text.strip()
        if len(image_prompt) > 500:
            image_prompt = image_prompt[:500]
        
        print(f"Generated image prompt: {image_prompt}")
        return image_prompt
    
    def create_tech_themed_image(self, topic, title):
        """Generate a visually appealing tech-themed image with text"""
        try:
            print(f"Creating tech-themed image for: {topic}")
            width, height = 1200, 630  # Good size for Twitter
            
            # Create a gradient background
            image = Image.new('RGB', (width, height), color='white')
            draw = ImageDraw.Draw(image)
            
            # Draw colorful gradient background - tech-themed colors
            for y in range(height):
                r = int(20 + (50 * (1 - y / height)))  # Dark blue to lighter blue
                g = int(40 + (80 * (y / height)))
                b = int(80 + (120 * (y / height)))
                for x in range(width):
                    # Add some horizontal variation too
                    r_mod = r + int(20 * (x / width))
                    g_mod = g + int(10 * (x / width))
                    draw.point((x, y), fill=(r_mod, g_mod, b))
            
            # Add some tech-themed decorative elements
            # Network nodes and connections
            nodes = []
            for _ in range(20):
                x = random.randint(50, width-50)
                y = random.randint(50, height-50)
                size = random.randint(5, 15)
                nodes.append((x, y, size))
            
            # Draw connections between nodes
            for i in range(len(nodes)):
                for j in range(i+1, min(i+4, len(nodes))):
                    x1, y1, _ = nodes[i]
                    x2, y2, _ = nodes[j]
                    # Calculate distance
                    dist = ((x2-x1)**2 + (y2-y1)**2)**0.5
                    if dist < 300:  # Only connect nearby nodes
                        # Add some curvature for visual interest
                        draw.line((x1, y1, x2, y2), fill=(180, 220, 255, 128), width=1)
            
            # Draw nodes on top of connections
            for x, y, size in nodes:
                draw.ellipse((x-size, y-size, x+size, y+size), 
                             fill=(220, 240, 255), 
                             outline=(255, 255, 255))
            
            # Add some random larger circles for visual interest
            for _ in range(8):
                x = random.randint(0, width)
                y = random.randint(0, height)
                size = random.randint(50, 150)
                # Semi-transparent circles
                for s in range(size, 0, -10):
                    opacity = int(100 * (s/size))
                    draw.ellipse((x-s, y-s, x+s, y+s), 
                                outline=(255, 255, 255, opacity),
                                width=2)
            
            # Add topic text
            try:
                # Try to load a nice font, fall back to default if not available
                try:
                    title_font = ImageFont.truetype("arial.ttf", 60)
                    subtitle_font = ImageFont.truetype("arial.ttf", 30)
                except:
                    # Fallback fonts
                    title_font = ImageFont.load_default()
                    subtitle_font = ImageFont.load_default()
                
                # Add a semi-transparent overlay for text
                overlay = Image.new('RGBA', (width, 200), (0, 0, 0, 150))
                image.paste(overlay, (0, height-200), overlay)
                
                # Wrap title text to fit
                title_wrapped = textwrap.fill(title, width=30)
                
                # Draw title text
                draw.text((width//2, height-120), title_wrapped, 
                         fill=(255, 255, 255), 
                         font=title_font, 
                         anchor="mm", 
                         align="center")
                
                # Draw subtitle/attribution
                draw.text((width//2, height-40), "AskMeGenie", 
                         fill=(200, 200, 255), 
                         font=subtitle_font,
                         anchor="mm")
                
            except Exception as e:
                print(f"Error adding text to image: {e}")
            
            # Save the image for debugging
            image_path = "generated_image.jpg"
            image.save(image_path)
            print(f"Image saved to {image_path}")
            
            # Return the image as a buffer
            img_buffer = io.BytesIO()
            image.save(img_buffer, format='JPEG', quality=95)
            img_buffer.seek(0)
            return img_buffer
            
        except Exception as e:
            print(f"Error creating tech-themed image: {e}")
            # Create an even simpler fallback image
            image = Image.new('RGB', (800, 500), color=(20, 40, 80))
            draw = ImageDraw.Draw(image)
            draw.rectangle((10, 10, 790, 490), outline=(255, 255, 255), width=5)
            
            img_buffer = io.BytesIO()
            image.save(img_buffer, format='JPEG')
            img_buffer.seek(0)
            return img_buffer
    
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
    
    def create_image_with_router_api(self, prompt):
        """Generate an image using the Image Router API"""
        try:
            print(f"Generating image using Image Router API with prompt: {prompt}")
            
            # API endpoint
            url = "https://ir-api.myqa.cc/v1/openai/images/generations"
            
            # Headers
            headers = {
                "Authorization": f"Bearer {IMAGE_ROUTER_API_KEY}",
                "Content-Type": "application/json"
            }
            
            # Request payload
            data = {
                "prompt": prompt,
                "model": "google/gemini-2.0-flash-exp:free",
                "quality": "auto"
            }
            
            # Make the API request
            print("Sending request to Image Router API...")
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()  # Raise exception for non-200 responses
            
            # Parse the response
            response_data = response.json()
            print(f"Response received, status: {response.status_code}")
            
            # Check if we have image data
            if not response_data.get("data") or not response_data["data"][0].get("b64_json"):
                print("No image data found in response")
                # Log the response structure for debugging
                print(f"Response structure: {response_data.keys()}")
                raise Exception("No image data in response")
            
            # Get the base64 image data
            base64_image = response_data["data"][0]["b64_json"]
            print(f"Received base64 image data, length: {len(base64_image)}")
            
            # Decode the base64 image
            image_data = base64.b64decode(base64_image)
            
            # Create an image buffer
            img_buffer = io.BytesIO(image_data)
            
            # Verify the image by opening it
            img = Image.open(img_buffer)
            img.verify()  # Will raise an exception if it's not a valid image
            
            # Save a copy for debugging
            img_buffer.seek(0)
            img = Image.open(img_buffer)
            img.save("router_api_image.jpg")
            print(f"Image saved as 'router_api_image.jpg'")
            
            # Return the image buffer
            img_buffer.seek(0)
            return img_buffer
            
        except Exception as e:
            print(f"Error generating image with Router API: {e}")
            print("Falling back to local image generation...")
            # Fall back to our local image generation if the API fails
            return self.create_tech_themed_image(prompt, prompt)
    
    def post_tweet(self, text, with_image=False, image_topic=None, image_title=None):
        """Post a tweet with optional image"""
        max_retries = 3
        retry_delay = 10
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                if with_image and image_topic:
                    # Generate image
                    print(f"Generating image for topic: {image_topic}")
                    
                    if not image_title:
                        image_title = image_topic
                    
                    # Generate a detailed prompt for the image
                    image_prompt = self.generate_image_prompt(image_topic)
                    
                    # Use the Router API to generate the image
                    img_buffer = self.create_image_with_router_api(image_prompt)
                    
                    if img_buffer:
                        # Upload media
                        print("Uploading image to Twitter...")
                        media = self.api.media_upload(filename='image.jpg', file=img_buffer)
                        
                        # Post tweet with media
                        print("Posting tweet with image...")
                        response = self.client.create_tweet(
                            text=text,
                            media_ids=[media.media_id]
                        )
                    else:
                        # Fallback to text-only tweet
                        print("Image generation failed, posting text-only tweet")
                        response = self.client.create_tweet(text=text)
                else:
                    # Text-only tweet
                    response = self.client.create_tweet(text=text)
                    
                print(f"Tweet posted successfully: {response.data['id']}")
                return response.data['id']
            except Exception as e:
                retry_count += 1
                if retry_count < max_retries:
                    print(f"Error posting tweet: {e}. Retrying in {retry_delay} seconds... (Attempt {retry_count}/{max_retries})")
                    time.sleep(retry_delay)
                else:
                    print(f"Failed to post tweet after {max_retries} attempts: {e}")
                    return None
    
    def reply_to_tweet(self, tweet_id, text):
        """Reply to a specific tweet"""
        max_retries = 3
        retry_delay = 10
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                response = self.client.create_tweet(
                    text=text,
                    in_reply_to_tweet_id=tweet_id
                )
                print(f"Reply posted successfully: {response.data['id']}")
                return response.data['id']
            except Exception as e:
                retry_count += 1
                if retry_count < max_retries:
                    print(f"Error replying to tweet: {e}. Retrying in {retry_delay} seconds... (Attempt {retry_count}/{max_retries})")
                    time.sleep(retry_delay)
                else:
                    print(f"Failed to reply to tweet after {max_retries} attempts: {e}")
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
        Make it conversational and human-like, as if written by a tech professional.
        Add a touch of personality and warmth to it.
        Keep it under 240 characters and make it engaging without using hashtags.
        
        Don't use phrases like "As an AI" or anything that reveals you're an AI.
        Do not use asterisks for emphasis (like *word* or *phrase*) in your response.
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
            
            Respond in a casual, friendly tone like a tech professional would. Be concise (under 240 characters).
            If they're asking a question, provide a clear answer.
            If unclear, ask for clarification.
            
            Don't use phrases like "As an AI" or anything that reveals you're an AI.
            Make it sound natural like a human tech expert's tweet.
            Do not use asterisks for emphasis (like *word* or *phrase*) in your response.
            """
            
            response = self.generate_ai_response(prompt, conversation_id=str(mention.id))
            
            if response:
                # Reply to the mention
                self.reply_to_tweet(mention.id, response)
                print(f"Responded to mention: {mention.id}")
        
        return newest_id
    
    def generate_tech_post(self):
        """Generate and post content about latest tech trends with engaging images"""
        print("Generating tech post...")
        
        # Always include an image for better engagement
        with_image = True
        
        # Select a random tech topic from keywords or generate a novel one
        base_topic = random.choice(KEYWORDS)
        
        # Generate a more specific tech topic based on the base topic
        topic_prompt = f"""
        Based on the general topic '{base_topic}', generate a specific, current tech subtopic 
        that would be interesting to software engineers and tech professionals in 2024.
        Your response should be ONLY the specific topic name in 3-5 words, nothing else.
        """
        
        specific_topic = self.generate_ai_response(topic_prompt)
        if not specific_topic:
            specific_topic = base_topic
            
        # Trim any extra whitespace or punctuation
        specific_topic = specific_topic.strip().strip('"\'.,;:')
        print(f"Selected specific tech topic: {specific_topic}")
        
        # Generate engaging post content
        post_prompt = f"""
        You're a tech thought leader posting on X (Twitter).
        
        Create an insightful, engaging tweet about '{specific_topic}' for software engineers and tech professionals.
        
        Your tweet should:
        - Start with a hook (question, surprising fact, or bold statement)
        - Include a useful insight or tip
        - Sound natural and conversational, not formal
        - End with a thought-provoking point or call to action
        - Be under 240 characters
        - NOT use hashtags
        - NOT mention that you're an AI or bot
        - NOT use asterisks for emphasis (like *word* or *phrase*)
        
        Write it like a real human tech expert would write it - casual, direct, and with personality.
        """
        
        post_content = self.generate_ai_response(post_prompt)
        
        if post_content:
            # Post the tweet with an image
            self.post_tweet(post_content, with_image=with_image, image_topic=specific_topic, image_title=specific_topic)
            print("Tech post generated and posted with image")

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