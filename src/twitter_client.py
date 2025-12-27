"""Twitter API client for posting tweets and interacting with Twitter."""

from typing import Optional
import time
import tweepy


class TwitterClient:
    """Client for Twitter API operations."""
    
    def __init__(self, api_key: str, api_key_secret: str, access_token: str, 
                 access_token_secret: str, bearer_token: str = None):
        """Initialize Twitter client with credentials."""
        # Initialize Twitter client
        self.client = tweepy.Client(
            bearer_token=bearer_token if bearer_token else None,  # Make bearer token optional
            consumer_key=api_key,
            consumer_secret=api_key_secret,
            access_token=access_token,
            access_token_secret=access_token_secret
        )
        
        # Initialize Twitter API v1.1 for media uploads
        auth = tweepy.OAuth1UserHandler(
            api_key, api_key_secret, access_token, access_token_secret
        )
        self.api = tweepy.API(auth)
        
        # Get own user ID
        try:
            self.me = self.client.get_me()
            self.user_id = self.me.data.id
            print(f"Twitter client initialized for user: {self.me.data.username}")
        except Exception as e:
            print(f"Warning: Could not get user information: {e}")
            print("Some features like mention tracking may not work properly.")
            self.user_id = None
    
    def search_tweets(self, query: str, max_results: int = 10):
        """Search for tweets based on keywords."""
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
    
    def get_mentions(self, since_id: Optional[int] = None):
        """Get mentions directed at the bot."""
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
    
    def post_tweet(self, text: str, media_ids: list = None, max_retries: int = 3, retry_delay: int = 10):
        """Post a tweet with optional media."""
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                if media_ids:
                    response = self.client.create_tweet(
                        text=text,
                        media_ids=media_ids
                    )
                else:
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
    
    def reply_to_tweet(self, tweet_id: int, text: str, max_retries: int = 3, retry_delay: int = 10):
        """Reply to a specific tweet."""
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
    
    def upload_media(self, image_buffer, filename: str = 'image.jpg'):
        """Upload media to Twitter."""
        try:
            media = self.api.media_upload(filename=filename, file=image_buffer)
            return media.media_id
        except Exception as e:
            print(f"Error uploading media: {e}")
            return None
    
    def get_tweet(self, tweet_id: int):
        """Get a tweet by ID."""
        try:
            tweet = self.client.get_tweet(tweet_id).data
            return tweet
        except Exception as e:
            print(f"Error getting tweet: {e}")
            return None




