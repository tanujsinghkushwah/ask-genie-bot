from src.config import load_config
import tweepy
import sys

def test_auth():
    config = load_config()
    print(f"Testing with User: {config.get('API_KEY')[:5]}...")
    
    client = tweepy.Client(
        consumer_key=config['API_KEY'],
        consumer_secret=config['API_KEY_SECRET'],
        access_token=config['ACCESS_TOKEN'],
        access_token_secret=config['ACCESS_TOKEN_SECRET']
    )
    
    try:
        me = client.get_me()
        print(f"Auth Success! User: {me.data.username} (ID: {me.data.id})")
        
        print("Attempting media upload...")
        auth = tweepy.OAuth1UserHandler(
            config['API_KEY'], config['API_KEY_SECRET'], 
            config['ACCESS_TOKEN'], config['ACCESS_TOKEN_SECRET']
        )
        api_v1 = tweepy.API(auth)
        
        import os
        img_path = "generated_image.jpg"
        if os.path.exists(img_path):
            media = api_v1.media_upload(filename=img_path)
            media_id = media.media_id_string
            print(f"Media uploaded! ID: {media_id}")
            
            # Use a shorter test text
            test_text = """Everyone chases automation but ignores the real bottleneck.

Learn more at interviewgenie.net"""
            
            print(f"Test text ({len(test_text)} chars):")
            print(test_text)
            print("---")
            
            print("Attempting media post...")
            response = client.create_tweet(
                text=test_text,
                media_ids=[media_id]
            )
            print(f"Post Success! Tweet ID: {response.data['id']}")
        else:
            print("No generated_image.jpg found, skipping media test.")
        
    except Exception as e:
        print(f"Error: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Detail: {e.response.text}")

if __name__ == "__main__":
    test_auth()
