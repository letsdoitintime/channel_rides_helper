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
- **🎨 Configurable Buttons**: Customize button visibility, text, and behavior
  - Hide/show any button (join, maybe, decline, voters, refresh)
  - Custom button text or use translations
  - Add additional URL buttons
  - Restrict voters list to participants only
- **🌐 Multi-Language Support**: English and Ukrainian translations built-in
  - Easy to add new languages via YAML files
  - Optional YAML configuration for buttons and translations
  - Falls back to environment variables if YAML not used

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

### Core Settings

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
| `LANGUAGE` | No | `en` | Language: `en` (English) or `ua` (Ukrainian) |

### Button Configuration

The bot provides a flexible button configuration system allowing you to customize the registration interface.

#### Button Visibility

| Variable | Default | Description |
| --- | --- | --- |
| `BUTTON_SHOW_JOIN` | `true` | Show the "Join" vote button |
| `BUTTON_SHOW_MAYBE` | `true` | Show the "Maybe" vote button |
| `BUTTON_SHOW_DECLINE` | `true` | Show the "Decline" vote button |
| `BUTTON_SHOW_VOTERS` | `true` | Show the "Voters" list button |
| `BUTTON_SHOW_REFRESH` | `true` | Show the "Refresh" button |

**Note:** At least one vote button (Join, Maybe, or Decline) must be visible.

#### Custom Button Text

Override default button text (otherwise uses language translations):

| Variable | Description | Example |
| --- | --- | --- |
| `BUTTON_CUSTOM_JOIN_TEXT` | Custom text for Join button | `✅ I'm In` |
| `BUTTON_CUSTOM_MAYBE_TEXT` | Custom text for Maybe button | `❔ Not Sure` |
| `BUTTON_CUSTOM_DECLINE_TEXT` | Custom text for Decline button | `❌ Can't Make It` |
| `BUTTON_CUSTOM_VOTERS_TEXT` | Custom text for Voters button | `👥 Show List` |
| `BUTTON_CUSTOM_REFRESH_TEXT` | Custom text for Refresh button | `🔄 Update` |

#### Additional Buttons

Add extra buttons with URLs (e.g., rules, maps, external links):

```env
# Format: Button Text|URL,Another Button|URL
BUTTON_ADDITIONAL=Rules|https://example.com/rules,Map|https://example.com/map
```

#### Voter Access Control

| Variable | Default | Description |
| --- | --- | --- |
| `BUTTON_REQUIRE_VOTE_FOR_VOTERS` | `false` | If `true`, users must vote before viewing the voters list |

### Configuration Examples

#### Example 1: Hide "Maybe" button and refresh button

```env
BUTTON_SHOW_MAYBE=false
BUTTON_SHOW_REFRESH=false
```

#### Example 2: Custom button names in your style

```env
BUTTON_CUSTOM_JOIN_TEXT=🚴 Count Me In!
BUTTON_CUSTOM_MAYBE_TEXT=🤔 Thinking...
BUTTON_CUSTOM_DECLINE_TEXT=😢 Can't Join
```

#### Example 3: Ukrainian language with additional info button

```env
LANGUAGE=ua
BUTTON_ADDITIONAL=Правила|https://example.com/rules
```

#### Example 4: Restrict voters list to participants only

```env
BUTTON_REQUIRE_VOTE_FOR_VOTERS=true
```

This prevents users who haven't voted from seeing who voted.

## YAML Configuration (Optional)

The bot supports optional YAML-based configuration for translations and buttons, which makes it easier to manage and add new languages. **This is completely optional** - the bot works perfectly with environment variables alone.

### Why Use YAML Configuration?

- ✅ **Easier to add new languages** - Just add a new section to the YAML file
- ✅ **Better organization** - All translations in one place
- ✅ **No code changes needed** - Add/edit translations without touching Python
- ✅ **Backward compatible** - Falls back to environment variables if YAML not used
- ✅ **Version control friendly** - Easy to track changes in git

### Translations YAML

Create `config/translations.yaml` to define translations for all languages:

```yaml
# English (en)
en:
  buttons:
    join: "✅ Join"
    maybe: "❔ Maybe"
    decline: "❌ No"
    voters: "👥 Voters"
    refresh: "🔄 Refresh"
  messages:
    registration_title: "🚴 Registration"
    vote_recorded: "Your vote has been recorded!"
    refreshed: "✅ Refreshed!"
    voters_list_title: "👥 **Voters List**"
    no_votes_yet: "_No votes yet_"
    vote_required: "You need to vote first to see the voters list"
    join_label: "Join"
    maybe_label: "Maybe"
    decline_label: "Decline"
    changed_mind: "🔁 Changed mind"

# Ukrainian (ua)
ua:
  buttons:
    join: "✅ Їду"
    maybe: "❔ Можливо"
    decline: "❌ Ні"
    voters: "👥 Учасники"
    refresh: "🔄 Оновити"
  messages:
    registration_title: "🚴 Реєстрація"
    vote_recorded: "Ваш голос збережено!"
    refreshed: "✅ Оновлено!"
    voters_list_title: "👥 **Список учасників**"
    no_votes_yet: "_Голосів поки немає_"
    vote_required: "Спочатку проголосуйте, щоб побачити список учасників"
    join_label: "Їду"
    maybe_label: "Можливо"
    decline_label: "Ні"
    changed_mind: "🔁 Змінили думку"

# Add more languages easily!
# de:
#   buttons:
#     join: "✅ Dabei"
#     ...
```

**To use:** Simply create the file at `config/translations.yaml`. The bot will automatically detect and use it. If the file doesn't exist, the bot uses hardcoded translations.

### Button Configuration YAML

Create `config/buttons.yaml` to configure buttons via YAML instead of environment variables:

```yaml
# Button visibility - control which buttons are shown
visibility:
  show_join: true
  show_maybe: true
  show_decline: true
  show_voters: true
  show_refresh: true

# Custom button text (optional)
# If null, uses translations from translations.yaml
custom_text:
  join: null            # or "✅ I'm In"
  maybe: null           # or "❔ Not Sure"
  decline: null         # or "❌ Can't Make It"
  voters: null          # or "👥 Show List"
  refresh: null         # or "🔄 Update"

# Additional buttons with URLs (optional)
additional_buttons:
  - text: "Rules"
    url: "https://example.com/rules"
  - text: "Map"
    url: "https://example.com/map"

# Access control
access_control:
  require_vote_to_see_voters: false
```

**To use:** 
1. Copy `config/buttons.yaml.example` to `config/buttons.yaml`
2. Edit as needed
3. If the file exists, it takes precedence over environment variables
4. If the file doesn't exist, environment variables are used (backward compatible)

### Adding a New Language

To add a new language (e.g., German):

1. Edit `config/translations.yaml` and add a new section:

```yaml
de:
  buttons:
    join: "✅ Dabei"
    maybe: "❔ Vielleicht"
    decline: "❌ Nein"
    voters: "👥 Teilnehmer"
    refresh: "🔄 Aktualisieren"
  messages:
    registration_title: "🚴 Anmeldung"
    vote_recorded: "Ihre Stimme wurde aufgezeichnet!"
    refreshed: "✅ Aktualisiert!"
    voters_list_title: "👥 **Teilnehmerliste**"
    no_votes_yet: "_Noch keine Stimmen_"
    vote_required: "Sie müssen zuerst abstimmen, um die Teilnehmerliste zu sehen"
    join_label: "Dabei"
    maybe_label: "Vielleicht"
    decline_label: "Nein"
    changed_mind: "🔁 Meinung geändert"
```

2. Update the `Language` type in `app/translations.py` to include the new language
3. Add validation in `app/config.py` for the new language code
4. Set `LANGUAGE=de` in your `.env` file

That's it! No other code changes needed.

### Migration from Environment Variables

Already using environment variables? No problem!

- **Keep using env vars**: Everything works as before
- **Mix and match**: Use YAML for translations, env vars for buttons (or vice versa)
- **Gradual migration**: Move to YAML when convenient - both systems work together

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
