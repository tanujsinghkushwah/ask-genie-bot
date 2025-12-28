"""Entry point for the AskMeGenie Twitter Bot - imports from src package."""

import argparse
from src.main import run_bot
from src.rate_limiter import TwitterRateLimiter

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the AskMeGenie Twitter Bot")
    parser.add_argument('--task', type=str, choices=['keyword', 'mentions', 'post', 'usage', 'clear-lockout', 'all'], 
                        default='all', help='Specific task to run (use "usage" to check rate limits, "clear-lockout" to clear rate limit lockout)')
    
    args = parser.parse_args()
    
    # Handle utility tasks separately
    if args.task == 'usage':
        rate_limiter = TwitterRateLimiter()
        print(rate_limiter.get_usage_report())
        can_post, message = rate_limiter.can_post()
        print(message)
    elif args.task == 'clear-lockout':
        rate_limiter = TwitterRateLimiter()
        is_locked, lockout_until = rate_limiter.is_locked_out()
        if is_locked:
            print(f"Current lockout expires at: {lockout_until}")
            rate_limiter.clear_lockout()
            print("Lockout cleared. You can now attempt to post again.")
        else:
            print("No active lockout found.")
    else:
        print(f"Running bot with task: {args.task}")
        run_bot(args.task)
