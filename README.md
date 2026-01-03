# 🚴 Velo Ride Registration Bot

A production-ready Telegram bot for managing ride registrations from a channel. Built with aiogram v3 and SQLite.

## Features

- **📢 Channel Monitoring**: Automatically detects new ride posts in your channel
- **🎯 Smart Filtering**: Configurable hashtag filtering (e.g., #ride) or process all posts
- **📸 Album Support**: Single registration for media groups (photo albums)
- **✅ Vote Tracking**: Join/Maybe/Decline buttons with real-time updates
- **🔁 Changed Mind Analytics**: Track users who registered but changed their minds
- **📊 Voter Lists**: View detailed voter lists grouped by status
- **🔄 Three Registration Modes**:
  - `edit_channel` - Edit original post (if bot is author)
  - `discussion_thread` - Post in linked discussion group
  - `channel_reply_post` - Create reply post in channel
- **🛡️ Rate Limiting**: Prevent spam clicking on vote buttons
- **👑 Admin Commands**: `/ping` and `/voters` for administrators

## Requirements

- Python 3.11+
- Telegram Bot Token
- Channel/Group permissions

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/letsdoitintime/channel_rides_helper.git
cd channel_rides_helper
```

### 2. Create virtual environment

```bash
python -m venv venv
# Activate (macOS / Linux)
source venv/bin/activate

# Activate (Windows - CMD)
venv\Scripts\activate

# Activate (Windows - PowerShell)
.\venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment

Copy the example environment file and edit it:

```bash
cp .env.example .env
```

Edit `.env` with your settings:

```env
# Get from @BotFather
BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz

# Your channel ID (negative number)
RIDES_CHANNEL_ID=-1001234567890

# Discussion group ID (optional)
DISCUSSION_GROUP_ID=-1009876543210

# Registration mode: edit_channel | discussion_thread | channel_reply_post
REGISTRATION_MODE=edit_channel

# Filter: hashtag | all
RIDE_FILTER=hashtag

# Hashtags to detect (comma-separated)
RIDE_HASHTAGS=#ride,#велопокатушка

# Admin user IDs (comma-separated)
ADMIN_USER_IDS=123456789,987654321
```

### 5. Run the bot

```bash
python -m app.bot
```

Or for production with systemd:

```bash
sudo cp channel_rides_bot.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable channel_rides_bot
sudo systemctl start channel_rides_bot
```

## Getting Channel/Group IDs

### Method 1: Forward a message

1. Forward any message from your channel/group to @userinfobot
2. It will show you the channel/group ID

### Method 2: Using the bot

1. Add your bot to the channel/group as admin
2. Send a message to the channel/group
3. Check bot logs - the ID will appear

### Method 3: Web Telegram

1. Open [Web Telegram](https://web.telegram.org)
2. Navigate to your channel/group
3. Look at the URL: `https://web.telegram.org/z/#-1001234567890`

## Bot Setup

### 1. Create the bot

1. Message @BotFather on Telegram
2. Send `/newbot`
3. Choose a name and username
4. Copy the bot token

### 2. Add bot to channel

1. Add the bot to your channel as **Administrator**
2. Give it these permissions:
   - ✅ Post messages
   - ✅ Edit messages
   - ✅ Delete messages (optional)

### 3. Setup discussion group (optional)

1. Link a discussion group to your channel
2. Add the bot to the discussion group
3. Get the discussion group ID

## Configuration Options

| Variable | Required | Default | Description |
| --- | --- | --- | --- |
| `BOT_TOKEN` | Yes | - | Telegram bot token from @BotFather |
| `RIDES_CHANNEL_ID` | Yes | - | Channel ID to monitor |
| `DISCUSSION_GROUP_ID` | No | - | Linked discussion group ID |
| `REGISTRATION_MODE` | No | `edit_channel` | Registration mode (see below) |
| `RIDE_FILTER` | No | `hashtag` | Filter type: `hashtag` or `all` |
| `RIDE_HASHTAGS` | No | `#ride` | Comma-separated hashtags |
| `ADMIN_USER_IDS` | No | - | Comma-separated admin user IDs |
| `DATABASE_PATH` | No | `./data/bot.db` | SQLite database path |
| `LOG_LEVEL` | No | `INFO` | Logging level |
| `LOG_FILE` | No | `./logs/bot.log` | Log file path |
| `VOTE_COOLDOWN` | No | `1` | Seconds between votes per user |
| `SHOW_CHANGED_MIND_STATS` | No | `true` | Show changed mind count |

### Registration Modes

#### edit_channel (Recommended)

- Edits the original channel post to add buttons
- Only works if the bot posted the message
- Most integrated experience

#### discussion_thread

- Posts registration card in linked discussion group
- Good for channels with active discussions
- Requires `DISCUSSION_GROUP_ID`

#### channel_reply_post

- Creates a new post in the channel as a reply
- Falls back to a new post with link button if reply fails
- Works in all scenarios

Fallback chain: The bot tries modes in order. If your configured mode fails, it automatically tries the next one.

## Usage

### For Channel Members

When a ride post appears in the channel:

1. Click one of the buttons:
   - ✅ **Join** - You're coming!
   - ❔ **Maybe** - You might come
   - ❌ **No** - You're not coming

2. View voters:
   - Click 👥 **Voters** to see who's coming

3. Refresh stats:
   - Click 🔄 **Refresh** to update the count

### For Admins

#### Check bot status

```text
/ping
```

#### View voters for a post

```text
/voters 123                          # Using message ID
/voters https://t.me/c/1234567890/123  # Using message link
```

## Database Schema

### posts table

Stores registration card information:

- `channel_id` - Channel where post was made
- `channel_message_id` - Original message ID
- `mode` - Registration mode used
- `registration_chat_id` - Where registration card is posted
- `registration_message_id` - Registration card message ID
- `media_group_id` - Album ID (if part of album)
- `created_at` - Timestamp

### votes table

Stores user votes:

- `channel_id` - Channel ID
- `channel_message_id` - Message ID
- `user_id` - Telegram user ID
- `status` - Current status (join/maybe/decline)
- `first_status` - Initial vote
- `ever_joined` - 1 if user ever clicked Join
- `updated_at` - Last update timestamp

## Development

### Running tests

```bash
# Install test dependencies
pip install -r requirements.txt

# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_db.py
```

### Project Structure

```text
channel_rides_helper/
├── app/
│   ├── __init__.py
│   ├── bot.py                    # Main entry point
│   ├── config.py                 # Configuration management
│   ├── db.py                     # Database layer
│   ├── handlers/
│   │   ├── __init__.py
│   │   ├── channel_watcher.py   # Channel post monitoring
│   │   ├── callbacks.py         # Button handlers
│   │   └── admin.py             # Admin commands
│   └── services/
│       ├── __init__.py
│       └── registration.py      # Registration card logic
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_config.py
│   ├── test_db.py
│   └── test_admin.py
├── data/                         # SQLite database (created automatically)
├── logs/                         # Log files (created automatically)
├── .env                          # Your configuration (create from .env.example)
├── .env.example                  # Environment template
├── .gitignore
├── requirements.txt
└── README.md
```

## Troubleshooting

### Bot doesn't respond

- Check bot token is correct
- Verify bot is admin in the channel
- Check logs: `tail -f logs/bot.log`

### Registration cards not appearing

- Verify `REGISTRATION_MODE` is correct
- Check bot has permission to post/edit messages
- Try changing to `channel_reply_post` mode

### Hashtag filtering not working

- Ensure hashtags in `.env` match exactly (including #)
- Check `RIDE_FILTER=hashtag` is set
- Hashtags are case-insensitive

### Database errors

- Ensure `data/` directory exists and is writable
- Check SQLite is installed: `python -c "import sqlite3"`

### Permission errors

- Bot needs to be admin in channel
- For `edit_channel` mode, bot must be the author
- For `discussion_thread`, bot needs to be in discussion group

## Security Notes

- Never commit `.env` file
- Keep bot token secret
- Restrict admin commands to trusted users only
- Use rate limiting to prevent abuse
- Review logs regularly for suspicious activity

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Add tests for new features
4. Ensure all tests pass
5. Submit a pull request

## License

MIT License - feel free to use this bot for your cycling community!

## Support

For issues and questions:

- Create an issue on GitHub
- Check logs in `logs/bot.log`
- Review configuration in `.env`

## Acknowledgments

Built with:

- [aiogram](https://github.com/aiogram/aiogram) - Telegram Bot framework
- [aiosqlite](https://github.com/omnilib/aiosqlite) - Async SQLite
- [loguru](https://github.com/Delgan/loguru) - Logging made simple

---

Happy cycling! 🚴‍♂️🚴‍♀️
