"""Main entry point for the AskMeGenie Twitter Bot."""

import argparse
from .config import load_config
from .bot import GenieTweetBot


def run_bot(task=None):
    """Run the bot with specified task or all tasks."""
    config = load_config()
    bot = GenieTweetBot(config)
    
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


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the AskMeGenie Twitter Bot")
    parser.add_argument('--task', type=str, choices=['keyword', 'mentions', 'post', 'all'], 
                        default='all', help='Specific task to run')
    
    args = parser.parse_args()
    print(f"Running bot with task: {args.task}")
    run_bot(args.task)

