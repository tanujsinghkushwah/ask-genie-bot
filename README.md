# AskMeGenie Twitter Bot

Twitter: [@AskMeGenie](https://x.com/AskMeGenie)

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
- **Modular Architecture**: Clean, maintainable codebase organized by functionality
- **GitHub Actions Integration**: Automated scheduling via GitHub Actions workflows

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

## Firebase Remote Config Setup

This project uses Firebase Remote Config to manage environment variables. Follow these steps to set it up:

1. Create a Firebase project at [Firebase Console](https://console.firebase.google.com/)
2. Set up Remote Config in your Firebase project
3. Add the following parameters to your Remote Config:
   - `API_KEY` - Twitter API Key
   - `API_KEY_SECRET` - Twitter API Key Secret
   - `ACCESS_TOKEN` - Twitter Access Token
   - `ACCESS_TOKEN_SECRET` - Twitter Access Token Secret
   - `BEARER_TOKEN` - Twitter Bearer Token (optional)
   - `GEMINI_API_KEY` - Google Gemini API Key
   - `IMAGE_ROUTER_API` - Image Router API Key (optional)
   - `STABLE_HORDE_KEY` - Stable Horde API Key (optional)

4. Set up Firebase Admin SDK authentication:
   - For local development:
     - Generate a service account key from Firebase Console → Project Settings → Service Accounts
     - Set the environment variable: `export GOOGLE_APPLICATION_CREDENTIALS="/path/to/serviceAccountKey.json"`
   - For deployment:
     - Configure appropriate credentials based on your hosting environment

5. Install the requirements: `pip install -r requirements.txt`

Note: The bot will fetch config values from Firebase Remote Config first, then fall back to `.env` file if not found in Remote Config.

## Project Structure

The bot is organized into a modular structure for better maintainability:

```
src/
├── __init__.py          # Package initialization
├── constants.py         # Constants (keywords, defaults)
├── config.py            # Configuration management (Firebase, env vars)
├── ai_service.py        # Gemini AI service for responses
├── image_generator.py   # Image generation (Pollinations API, local fallback)
├── twitter_client.py    # Twitter API operations
├── bot.py               # Main bot class orchestrating all services
└── main.py              # Entry point with task execution logic

run_bot.py               # Root-level entry point
```

## Usage

### Running Manually

Run specific tasks:
```bash
# Post a new tech tweet
python run_bot.py --task post

# Respond to mentions
python run_bot.py --task mentions

# Interact with keyword tweets
python run_bot.py --task keyword

# Run all tasks
python run_bot.py --task all
```

## Scheduling with GitHub Actions

The bot uses GitHub Actions for automated scheduling. The workflow file `.github/workflows/bot.yml` is already configured. You just need to:

1. Add your API keys as secrets in your GitHub repository:
   - Go to Settings → Secrets and variables → Actions
   - Add the following secrets:
     - `API_KEY`
     - `API_KEY_SECRET`
     - `ACCESS_TOKEN`
     - `ACCESS_TOKEN_SECRET`
     - `BEARER_TOKEN`
     - `GEMINI_API_KEY`
     - `FIREBASE_SERVICE_ACCOUNT` (JSON content of your Firebase service account key)

2. The workflow will automatically run on the scheduled times defined in the cron expression.

The current workflow configuration:
- Runs on a cron schedule (configurable in `.github/workflows/bot.yml`)
- Supports manual triggers via `workflow_dispatch`
- Executes the bot with the specified task (default: `post`)

You can modify the schedule in `.github/workflows/bot.yml` to adjust when the bot runs.

## Customization

### Keywords
Modify the keywords to search for in `src/constants.py`:
- Edit the `KEYWORDS` list to add or remove keywords

### AI Prompts
Customize the bot's tone and responses:
- **Keyword interactions**: Edit prompts in `src/bot.py` → `interact_with_keyword_tweets()`
- **Mention responses**: Edit prompts in `src/bot.py` → `respond_to_mentions()`
- **Tech posts**: Edit prompts in `src/bot.py` → `generate_tech_post()`
- **Image prompts**: Edit image generation prompts in `src/ai_service.py` → `generate_image_prompt()`

### Model Configuration
- Change the Gemini model in Firebase Remote Config or `.env` file:
  - Set `MODEL_NAME` (default: `gemini-2.5-flash`)

### Scheduling
- Modify the GitHub Actions workflow schedule in `.github/workflows/bot.yml`
- Change the cron expression to adjust when the bot runs
- Modify the `--task` parameter to change which task runs on schedule

## License

MIT 
