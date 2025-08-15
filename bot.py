import logging
import json
import os
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
import asyncio
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# File to store deadlines
DEADLINES_FILE = 'deadlines.json'

# Categories for deadlines
CATEGORIES = [
    'university',
    'academic', 
    'personal',
    'ia',  # Internal Assessment
    'ee',  # Extended Essay
    'work',
    'other'
]

def load_deadlines():
    """Load deadlines from JSON file"""
    if os.path.exists(DEADLINES_FILE):
        try:
            with open(DEADLINES_FILE, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return {}
    return {}

def save_deadlines(deadlines):
    """Save deadlines to JSON file"""
    with open(DEADLINES_FILE, 'w') as f:
        json.dump(deadlines, f, indent=2)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a message when the command /start is issued."""
    welcome_message = """
🗓️ **Deadline Bot** 🗓️

Welcome! I can help you manage your deadlines.

**Available Commands:**
• `/add` - Add a new deadline
• `/view` - View deadlines by category
• `/help` - Show this help message

**Categories available:**
• university
• academic
• personal
• ia (Internal Assessment)
• ee (Extended Essay)
• work
• other

Get started by adding your first deadline with `/add`!
    """
    await update.message.reply_text(welcome_message, parse_mode='Markdown')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send help message"""
    help_text = """
🗓️ **How to use Deadline Bot:**

**Adding Deadlines:**
Use `/add` and I'll guide you through:
1. Enter the deadline title
2. Enter the due date (YYYY-MM-DD format)
3. Select a category

**Viewing Deadlines:**
Use `/view` followed by a category:
• `/view university` - Show university deadlines
• `/view academic` - Show academic deadlines
• `/view personal` - Show personal deadlines
• `/view ia` - Show IA deadlines
• `/view ee` - Show EE deadlines
• `/view work` - Show work deadlines
• `/view other` - Show other deadlines
• `/view all` - Show all deadlines

**Examples:**
• `/add` - Start adding a deadline
• `/view university` - View university deadlines
• `/view all` - View all deadlines
    """
    await update.message.reply_text(help_text, parse_mode='Markdown')

async def add_deadline(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start the process of adding a deadline"""
    await update.message.reply_text(
        "📝 Let's add a new deadline!\n\n"
        "Please enter the title/description of your deadline:"
    )
    context.user_data['adding_deadline'] = True
    context.user_data['step'] = 'title'

async def view_deadlines(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """View deadlines by category"""
    args = context.args
    
    if not args:
        # Show category selection buttons
        keyboard = []
        for i in range(0, len(CATEGORIES), 2):
            row = []
            row.append(InlineKeyboardButton(CATEGORIES[i].upper(), callback_data=f"view_{CATEGORIES[i]}"))
            if i + 1 < len(CATEGORIES):
                row.append(InlineKeyboardButton(CATEGORIES[i + 1].upper(), callback_data=f"view_{CATEGORIES[i + 1]}"))
            keyboard.append(row)
        
        keyboard.append([InlineKeyboardButton("ALL DEADLINES", callback_data="view_all")])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            "📋 Select a category to view deadlines:",
            reply_markup=reply_markup
        )
        return
    
    category = args[0].lower()
    await show_deadlines_by_category(update, category)

async def show_deadlines_by_category(update, category):
    """Show deadlines for a specific category"""
    deadlines = load_deadlines()
    
    if category == 'all':
        filtered_deadlines = []
        for cat in deadlines:
            for deadline in deadlines[cat]:
                deadline['category'] = cat
                filtered_deadlines.append(deadline)
    else:
        if category not in CATEGORIES:
            await update.message.reply_text(
                f"❌ Invalid category '{category}'. Available categories:\n" +
                ", ".join(CATEGORIES) + ", all"
            )
            return
        
        filtered_deadlines = deadlines.get(category, [])
    
    if not filtered_deadlines:
        category_text = "any category" if category == 'all' else f"'{category}' category"
        await update.message.reply_text(f"📭 No deadlines found in {category_text}.")
        return
    
    # Sort deadlines by date
    try:
        filtered_deadlines.sort(key=lambda x: datetime.strptime(x['date'], '%Y-%m-%d'))
    except:
        pass  # If date parsing fails, show unsorted
    
    message = f"📋 **Deadlines" + (f" - {category.upper()}" if category != 'all' else "") + ":**\n\n"
    
    for deadline in filtered_deadlines:
        try:
            due_date = datetime.strptime(deadline['date'], '%Y-%m-%d')
            days_left = (due_date - datetime.now()).days
            
            if days_left < 0:
                status = f"⚠️ OVERDUE ({abs(days_left)} days ago)"
            elif days_left == 0:
                status = "🔥 DUE TODAY"
            elif days_left <= 3:
                status = f"🚨 {days_left} days left"
            elif days_left <= 7:
                status = f"⏰ {days_left} days left"
            else:
                status = f"📅 {days_left} days left"
                
        except:
            status = "📅"
        
        category_tag = f" [{deadline.get('category', '').upper()}]" if category == 'all' else ""
        message += f"• **{deadline['title']}**{category_tag}\n"
        message += f"  📅 {deadline['date']} - {status}\n\n"
    
    await update.message.reply_text(message, parse_mode='Markdown')

async def handle_callback_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle callback queries from inline keyboards"""
    query = update.callback_query
    await query.answer()
    
    if query.data.startswith('view_'):
        category = query.data.replace('view_', '')
        await show_deadlines_by_category(query, category)
    elif query.data.startswith('category_'):
        # Handle category selection for adding deadline
        category = query.data.replace('category_', '')
        
        # Save the deadline
        deadlines = load_deadlines()
        if category not in deadlines:
            deadlines[category] = []
        
        new_deadline = {
            'title': context.user_data['deadline_title'],
            'date': context.user_data['deadline_date'],
            'added_on': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        deadlines[category].append(new_deadline)
        save_deadlines(deadlines)
        
        # Clear user data
        context.user_data.clear()
        
        await query.edit_message_text(
            f"✅ Deadline added successfully!\n\n"
            f"**Title:** {new_deadline['title']}\n"
            f"**Due Date:** {new_deadline['date']}\n"
            f"**Category:** {category.upper()}"
        )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle text messages during deadline addition"""
    if not context.user_data.get('adding_deadline'):
        await update.message.reply_text(
            "Use /add to add a deadline or /view to see your deadlines. Type /help for more information."
        )
        return
    
    step = context.user_data.get('step')
    
    if step == 'title':
        context.user_data['deadline_title'] = update.message.text
        context.user_data['step'] = 'date'
        await update.message.reply_text(
            "📅 Great! Now enter the due date in YYYY-MM-DD format (e.g., 2024-12-25):"
        )
    
    elif step == 'date':
        date_text = update.message.text.strip()
        
        # Validate date format
        try:
            datetime.strptime(date_text, '%Y-%m-%d')
        except ValueError:
            await update.message.reply_text(
                "❌ Invalid date format. Please use YYYY-MM-DD format (e.g., 2024-12-25):"
            )
            return
        
        context.user_data['deadline_date'] = date_text
        context.user_data['step'] = 'category'
        
        # Show category selection
        keyboard = []
        for i in range(0, len(CATEGORIES), 2):
            row = []
            row.append(InlineKeyboardButton(CATEGORIES[i].upper(), callback_data=f"category_{CATEGORIES[i]}"))
            if i + 1 < len(CATEGORIES):
                row.append(InlineKeyboardButton(CATEGORIES[i + 1].upper(), callback_data=f"category_{CATEGORIES[i + 1]}"))
            keyboard.append(row)
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            "🏷️ Finally, select a category for this deadline:",
            reply_markup=reply_markup
        )

def main():
    """Start the bot."""
    # Get bot token from environment variable
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    
    if not token:
        print("❌ Error: TELEGRAM_BOT_TOKEN environment variable not set!")
        print("Please set your bot token: export TELEGRAM_BOT_TOKEN='your_token_here'")
        return
    
    # Create the Application
    application = Application.builder().token(token).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("add", add_deadline))
    application.add_handler(CommandHandler("view", view_deadlines))
    application.add_handler(CallbackQueryHandler(handle_callback_query))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Run the bot
    print("🤖 Deadline Bot is starting...")
    application.run_polling()

if __name__ == '__main__':
    main()
