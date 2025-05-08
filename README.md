# AskMeGenie Twitter Bot

A perplexity-style Twitter bot for tech content that:
- Searches for posts based on tech/programming keywords
- Interacts with posts using AI responses
- Generates tech content posts (text + images)
- Responds to mentions automatically

## Features

- **Keyword Monitoring**: Automatically searches for tweets containing specific keywords (Interview, Software Engineer, Leetcode, System Design, etc.)
- **AI-Powered Interactions**: Uses Gemini 2.0 Flash model for generating thoughtful, informative responses
- **Content Generation**: Creates high-quality tech posts with optional images
- **Mention Responses**: Automatically responds to any mentions of your account
- **Flexible Scheduling**: Run manually or schedule automated posting and interactions

## Setup

1. Clone this repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Create a `.env` file in the project root with the following variables:
   ```
   # Twitter API credentials
   API_KEY=your_twitter_api_key
   API_KEY_SECRET=your_twitter_api_key_secret
   ACCESS_TOKEN=your_twitter_access_token
   ACCESS_TOKEN_SECRET=your_twitter_access_token_secret
   BEARER_TOKEN=your_twitter_bearer_token

   # Gemini API credentials
   GEMINI_API_KEY=your_gemini_api_key
   ```
4. Obtain Twitter API credentials from the [Twitter Developer Portal](https://developer.twitter.com/)
5. Get a Gemini API key from [Google AI Studio](https://makersuite.google.com/app/apikey)

## Usage

### Running Manually

Run specific tasks:
```
# Post a new tech tweet
python bot.py --task post

# Respond to mentions
python bot.py --task mentions

# Interact with keyword tweets
python bot.py --task keyword

# Run all tasks
python bot.py --task all
```

### Running with Scheduling

To run the bot with predefined schedules:
```
python bot.py --schedule
```

This will:
- Post tech content at 9 AM and 5 PM
- Check and respond to mentions every 2 hours
- Interact with keyword tweets at 11 AM, 3 PM and 7 PM

## Scheduling with GitHub Actions

You can automate this bot using GitHub Actions. Create a file `.github/workflows/bot.yml` with:

```yaml
name: Run Twitter Bot

on:
  schedule:
    - cron: '0 */4 * * *'  # Run every 4 hours
  workflow_dispatch:  # Allow manual triggers

jobs:
  run-bot:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.10'
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
      - name: Run bot
        env:
          API_KEY: ${{ secrets.API_KEY }}
          API_KEY_SECRET: ${{ secrets.API_KEY_SECRET }}
          ACCESS_TOKEN: ${{ secrets.ACCESS_TOKEN }}
          ACCESS_TOKEN_SECRET: ${{ secrets.ACCESS_TOKEN_SECRET }}
          BEARER_TOKEN: ${{ secrets.BEARER_TOKEN }}
          GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}
        run: |
          python bot.py --task all
```

Don't forget to add your API keys as secrets in your GitHub repository.

## Customization

You can modify the following in `bot.py`:
- Keywords to search for in the `KEYWORDS` list
- Scheduled times in the `setup_schedule()` function
- AI prompts in each respective function to change the bot's tone and responses

## License

MIT 