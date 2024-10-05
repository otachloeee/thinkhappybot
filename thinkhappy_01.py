import random
import time
import schedule
from textblob import TextBlob
from telegram import Update, Bot, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ConversationHandler

# Your bot token
bot_token = 'token'  # Replace with your actual bot token

# Initialize the bot application
application = Application.builder().token(bot_token).build()

# List of affirmations
affirmations = [
    "You are capable of achieving your goals, believe in yourself!",
    "You are strong, and you got this.",
    "You are confident, today is your day!",
    "You are brave, look at how far you have come.",
    "I belong in this world; there are people that care about me and my worth.",
    "I promise myself love, patience, and kindness for this week.",
    "You are enough just the way you are.",
    "My future will be positive.",
    "I deserve self-compassion and self-care.",
    "I am resilient and can overcome life’s challenges."
]

# List to hold all subscribed users' chat IDs
subscribed_users = []

# Conversation states
ASK_DAY = 1

# Function to send a random affirmation with "Affirm Yes" button
async def send_affirmation(chat_id):
    affirmation = random.choice(affirmations)
    message = f"{affirmation}"

    # Create an "Affirm Yes" button
    keyboard = [[InlineKeyboardButton("Affirm Yes", callback_data='affirm_yes')]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Send the message with the inline keyboard
    await application.bot.send_message(chat_id=chat_id, text=message, reply_markup=reply_markup)

# Command handler for /start to subscribe the user
async def start(update: Update, context):
    user_id = update.message.chat_id
    if user_id not in subscribed_users:
        subscribed_users.append(user_id)
        await update.message.reply_text(
            "You have subscribed to daily affirmations! You'll receive your first one tomorrow at 9 AM.\n\n"
            "If you ever want to stop receiving affirmations, just type /unsubscribe."
        )
    else:
        await update.message.reply_text("You're already subscribed.")

# Command handler for /unsubscribe
async def unsubscribe(update: Update, context):
    user_id = update.message.chat_id
    if user_id in subscribed_users:
        subscribed_users.remove(user_id)
        await update.message.reply_text("You have unsubscribed from daily affirmations.")
    else:
        await update.message.reply_text("You are not subscribed.")

# Callback function for handling button press
async def button(update: Update, context):
    query = update.callback_query
    if query.data == 'affirm_yes':
        # Acknowledge the "Affirm Yes" button press
        await query.answer()
        
        # Get the original affirmation message text from the query
        original_text = query.message.text
        
        # Edit the message to keep the affirmation text and add a response
        await query.edit_message_text(
            text=f"{original_text}\n\nYou affirmed: Yes! Keep being awesome! 😊"
        )


# Command handler for /affirmation to send an affirmation on request
async def request_affirmation(update: Update, context):
    user_id = update.message.chat_id
    await send_affirmation(user_id)

# Function to ask "How's your day?"
async def ask_day(update: Update, context):
    await update.message.reply_text("How's your day going? 😊")
    return ASK_DAY

# Function to handle user reply to "How's your day?"
#async def handle_day_reply(update: Update, context):
    user_response = update.message.text.lower()
    if "good" in user_response or "great" in user_response:
        await update.message.reply_text("That's awesome! Keep up the positive energy! 🌟")
    elif "bad" in user_response or "not good" in user_response:
        await update.message.reply_text("I'm sorry to hear that. Remember, you're strong and capable of overcoming challenges. 💪")
    else:
        await update.message.reply_text("Got it! I hope things get better; you're doing great! 🌼")
    
    return ConversationHandler.END

# Function to handle user reply to "How's your day?"
async def handle_day_reply(update: Update, context):
    user_response = update.message.text.lower()
    
    # Check for specific keywords first
    if "good" in user_response or "great" in user_response or "pretty good" in user_response or "gd" in user_response:
        await update.message.reply_text("That's awesome! Keep up the positive energy! 🌟")
    elif "bad" in user_response or "not good" in user_response or "ok" in user_response:
        await update.message.reply_text("I'm sorry to hear that. Remember, you're strong and capable of overcoming challenges. 💪")
    else:
        # Basic sentiment analysis as a fallback
        analysis = TextBlob(user_response)
        
        # Check sentiment polarity
        if analysis.sentiment.polarity > 0.5:
            await update.message.reply_text("That's awesome! Keep up the positive energy! 🌟")
        elif analysis.sentiment.polarity < -0.5:
            await update.message.reply_text("I'm sorry to hear that. Remember, you're strong and capable of overcoming challenges. 💪")
        else:
            await update.message.reply_text("That's understandable! Sometimes small things can make a big difference. What's one little thing that could improve your day? ☀️")

    return ConversationHandler.END



# Conversation handler to reset the conversation
async def cancel(update: Update, context):
    await update.message.reply_text("Okay! Let me know how you're doing next time! 😊")
    return ConversationHandler.END

# Schedule the affirmation to be sent daily at 9 AM
async def send_daily_affirmations():
    for chat_id in subscribed_users:
        await send_affirmation(chat_id)

schedule.every().day.at("09:00").do(lambda: application.create_task(send_daily_affirmations()))

# Function to keep the scheduler running
def run_scheduler():
    while True:
        schedule.run_pending()
        time.sleep(1)

# Main function to set up the bot commands and run the application
def main():
    # Set up command handlers
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('unsubscribe', unsubscribe))
    application.add_handler(CommandHandler('affirmation', request_affirmation))
    application.add_handler(CallbackQueryHandler(button))

    # Conversation handler for asking about the day
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('howisyourday', ask_day)],
        states={
            ASK_DAY: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_day_reply)]
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    application.add_handler(conv_handler)

    # Start polling to receive updates
    application.run_polling()

# Start the bot and the scheduler
if __name__ == '__main__':
    import threading

    # Start the scheduler in a separate thread
    scheduler_thread = threading.Thread(target=run_scheduler)
    scheduler_thread.start()

    # Start the Telegram bot application
    main()
