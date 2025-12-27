"""Entry point for the AskMeGenie Twitter Bot - imports from src package."""

import argparse
from src.main import run_bot

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the AskMeGenie Twitter Bot")
    parser.add_argument('--task', type=str, choices=['keyword', 'mentions', 'post', 'all'], 
                        default='all', help='Specific task to run')
    
    args = parser.parse_args()
    print(f"Running bot with task: {args.task}")
    run_bot(args.task)

