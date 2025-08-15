# 🗓️ Deadline Bot

A Telegram bot to help you manage and track your deadlines across different categories.

## Features

- **Add Deadlines**: Easily add deadlines with title, date, and category
- **View Deadlines**: Filter deadlines by specific categories
- **Smart Status**: Shows days remaining, overdue warnings, and urgency indicators
- **Multiple Categories**: Support for university, academic, personal, IA, EE, work, and other deadlines
- **Interactive Interface**: User-friendly buttons and guided workflows

## Categories

- `university` - University-related deadlines
- `academic` - General academic deadlines
- `personal` - Personal deadlines
- `ia` - Internal Assessment deadlines
- `ee` - Extended Essay deadlines
- `work` - Work-related deadlines
- `other` - Other miscellaneous deadlines

## Setup

### 1. Create a Telegram Bot

1. Message [@BotFather](https://t.me/BotFather) on Telegram
2. Send `/newbot` and follow the instructions
3. Choose a name and username for your bot
4. Copy the bot token provided by BotFather

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Set Environment Variable

Set your bot token as an environment variable:

```bash
export TELEGRAM_BOT_TOKEN="your_bot_token_here"
```

Or on Windows:
```cmd
set TELEGRAM_BOT_TOKEN=your_bot_token_here
```

### 4. Run the Bot

```bash
python bot.py
```

## Usage

### Commands

- `/start` - Welcome message and overview
- `/help` - Detailed help and usage instructions
- `/add` - Add a new deadline (interactive process)
- `/view` - View deadlines (shows category selection or use with category)
- `/view <category>` - View deadlines for a specific category
- `/view all` - View all deadlines

### Examples

```
/add
# Bot will guide you through:
# 1. Enter deadline title
# 2. Enter date (YYYY-MM-DD)
# 3. Select category

/view university
# Shows all university deadlines

/view
# Shows category selection buttons

/view all
# Shows all deadlines from all categories
```

### Status Indicators

- 🔥 **DUE TODAY** - Deadline is today
- 🚨 **X days left** - 1-3 days remaining (urgent)
- ⏰ **X days left** - 4-7 days remaining (soon)
- 📅 **X days left** - More than 7 days remaining
- ⚠️ **OVERDUE** - Past due date

## Data Storage

Deadlines are stored in `deadlines.json` in the same directory as the bot. The file is created automatically when you add your first deadline.

## File Structure

```
DeadelinesBot/
├── bot.py              # Main bot code
├── requirements.txt    # Python dependencies
├── README.md          # This file
└── deadlines.json     # Data storage (created automatically)
```

## Troubleshooting

1. **Bot not responding**: Check if the bot token is correctly set
2. **Permission errors**: Make sure the bot has permission to write files in the directory
3. **Date format errors**: Use YYYY-MM-DD format (e.g., 2024-12-25)

## Contributing

Feel free to submit issues and enhancement requests!
