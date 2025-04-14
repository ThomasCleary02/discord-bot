# Grumpy Discord Bot

A deliberately irritated Discord chatbot that responds with sarcastic, short, and blunt replies when mentioned. Built with Discord.py and Claude AI.

## Features

- Responds only when directly mentioned
- Provides short, sarcastic responses
- Deploys easily to fly.io
- Customizable personality through prompt engineering

## Setup

### Prerequisites

- Python 3.12+
- Discord Bot Token
- Anthropic API Key (Claude)
- Discord Server with appropriate permissions

### Installation

1. Clone this repository
   ```bash
   git clone https://github.com/yourusername/grumpy-discord-bot.git
   cd grumpy-discord-bot
   ```

2. Create a virtual environment
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. Install dependencies
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file with your credentials
   ```
   DISCORD_TOKEN=your_discord_bot_token
   DISCORD_GUILD=your_server_name
   ANTHROPIC_API_KEY=your_anthropic_api_key
   ```

### Running Locally

```bash
python main.py
```

## Deployment

This bot is configured for deployment on fly.io.

1. Install the Fly CLI
   ```bash
   curl -L https://fly.io/install.sh | sh
   ```

2. Login to Fly
   ```bash
   fly auth login
   ```

3. Create the app (if not already created)
   ```bash
   fly apps create your-app-name
   ```

4. Set your secrets
   ```bash
   fly secrets set DISCORD_TOKEN=your_discord_token
   fly secrets set DISCORD_GUILD=your_guild_name 
   fly secrets set ANTHROPIC_API_KEY=your_anthropic_api_key
   ```

5. Deploy your app
   ```bash
   fly deploy
   ```

## Project Structure

```
├── main.py                 # Discord bot main script
├── utils/
│   └── llm_client.py       # Claude AI integration
├── Dockerfile              # Container configuration
├── fly.toml                # Fly.io configuration
├── requirements.txt        # Python dependencies
└── .env                    # Environment variables (not committed)
```

## Customization

You can customize the bot's personality by editing the prompt template in `utils/llm_client.py`. Adjust the temperature value to control response randomness (higher = more random).

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.