import logging
import asyncio
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters
from config import Config
from handlers import Handlers
from admin_handlers import AdminHandlers
from database import Database

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Initialize database
db = Database()

def main():
    """Main function to run the bot"""
    # Check if bot token is provided
    if not Config.BOT_TOKEN:
        logger.error("Bot token not provided. Please set BOT_TOKEN in .env file")
        return
    
    # Create application
    application = Application.builder().token(Config.BOT_TOKEN).build()
    
    # Add handlers
    
    # Command handlers
    application.add_handler(CommandHandler("start", Handlers.start))
    application.add_handler(CommandHandler("help", Handlers.help_command))
    application.add_handler(CommandHandler("profile", Handlers.profile))
    application.add_handler(CommandHandler("balance", Handlers.balance))
    application.add_handler(CommandHandler("channels", Handlers.channels))
    application.add_handler(CommandHandler("referral", Handlers.referral))
    application.add_handler(CommandHandler("services", Handlers.services))
    application.add_handler(CommandHandler("orders", Handlers.orders))
    application.add_handler(CommandHandler("stats", Handlers.stats))
    
    # Admin command handlers
    application.add_handler(CommandHandler("admin", AdminHandlers.admin_menu))
    application.add_handler(CommandHandler("admin_stats", AdminHandlers.bot_stats))
    application.add_handler(CommandHandler("users", AdminHandlers.users_list))
    application.add_handler(CommandHandler("broadcast", AdminHandlers.broadcast_message))
    application.add_handler(CommandHandler("send_points", AdminHandlers.send_points))
    
    # Callback query handler
    application.add_handler(CallbackQueryHandler(handle_callback_query))
    
    # Message handlers
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_message))
    
    # Error handler
    application.add_error_handler(error_handler)
    
    # Start the bot
    logger.info("Starting bot...")
    application.run_polling(allowed_updates=["message", "callback_query"])

async def handle_callback_query(update, context):
    """Handle callback queries"""
    query = update.callback_query
    user_id = query.from_user.id
    
    # Admin callbacks
    if query.data.startswith(('add_channel', 'remove_channel', 'list_channels', 'all_orders', 
                              'pending_orders', 'complete_order', 'cancel_order_admin', 
                              'admin_complete_', 'admin_cancel_', 'back_to_admin')):
        await AdminHandlers.handle_admin_callback(query, context)
    else:
        await Handlers.button_callback(update, context)

async def handle_text_message(update, context):
    """Handle text messages"""
    user_id = update.effective_user.id
    
    # Admin text messages
    if update.message.text in ["📊 إحصائيات البوت", "👥 المستخدمين", "📢 إدارة القنوات", 
                               "📦 إدارة الطلبات", "✉️ رسالة جماعية", "💎 إرسال نقاط", 
                               "🔙 القائمة الرئيسية"]:
        await AdminHandlers.handle_admin_text(update, context)
    
    # Admin input handling
    elif context.user_data.get('admin_waiting_for'):
        await AdminHandlers.handle_admin_input(update, context)
    
    # Regular user messages
    else:
        await Handlers.handle_text_message(update, context)

async def error_handler(update, context):
    """Handle errors"""
    logger.error(f"Update {update} caused error {context.error}")
    
    if update and update.effective_message:
        await update.effective_message.reply_text(
            "❌ حدث خطأ في معالجة طلبك. يرجى المحاولة مرة أخرى."
        )

if __name__ == "__main__":
    main()import logging
import asyncio
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters
from config import Config
from handlers import Handlers
from admin_handlers import AdminHandlers
from database import Database

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Initialize database
db = Database()

def main():
    """Main function to run the bot"""
    # Check if bot token is provided
    if not Config.BOT_TOKEN:
        logger.error("Bot token not provided. Please set BOT_TOKEN in .env file")
        return
    
    # Create application
    application = Application.builder().token(Config.BOT_TOKEN).build()
    
    # Add handlers
    
    # Command handlers
    application.add_handler(CommandHandler("start", Handlers.start))
    application.add_handler(CommandHandler("help", Handlers.help_command))
    application.add_handler(CommandHandler("profile", Handlers.profile))
    application.add_handler(CommandHandler("balance", Handlers.balance))
    application.add_handler(CommandHandler("channels", Handlers.channels))
    application.add_handler(CommandHandler("referral", Handlers.referral))
    application.add_handler(CommandHandler("services", Handlers.services))
    application.add_handler(CommandHandler("orders", Handlers.orders))
    application.add_handler(CommandHandler("stats", Handlers.stats))
    
    # Admin command handlers
    application.add_handler(CommandHandler("admin", AdminHandlers.admin_menu))
    application.add_handler(CommandHandler("admin_stats", AdminHandlers.bot_stats))
    application.add_handler(CommandHandler("users", AdminHandlers.users_list))
    application.add_handler(CommandHandler("broadcast", AdminHandlers.broadcast_message))
    application.add_handler(CommandHandler("send_points", AdminHandlers.send_points))
    
    # Callback query handler
    application.add_handler(CallbackQueryHandler(handle_callback_query))
    
    # Message handlers
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_message))
    
    # Error handler
    application.add_error_handler(error_handler)
    
    # Start the bot
    logger.info("Starting bot...")
    application.run_polling(allowed_updates=["message", "callback_query"])

async def handle_callback_query(update, context):
    """Handle callback queries"""
    query = update.callback_query
    user_id = query.from_user.id
    
    # Admin callbacks
    if query.data.startswith(('add_channel', 'remove_channel', 'list_channels', 'all_orders', 
                              'pending_orders', 'complete_order', 'cancel_order_admin', 
                              'admin_complete_', 'admin_cancel_', 'back_to_admin')):
        await AdminHandlers.handle_admin_callback(query, context)
    else:
        await Handlers.button_callback(update, context)

async def handle_text_message(update, context):
    """Handle text messages"""
    user_id = update.effective_user.id
    
    # Admin text messages
    if update.message.text in ["📊 إحصائيات البوت", "👥 المستخدمين", "📢 إدارة القنوات", 
                               "📦 إدارة الطلبات", "✉️ رسالة جماعية", "💎 إرسال نقاط", 
                               "🔙 القائمة الرئيسية"]:
        await AdminHandlers.handle_admin_text(update, context)
    
    # Admin input handling
    elif context.user_data.get('admin_waiting_for'):
        await AdminHandlers.handle_admin_input(update, context)
    
    # Regular user messages
    else:
        await Handlers.handle_text_message(update, context)

async def error_handler(update, context):
    """Handle errors"""
    logger.error(f"Update {update} caused error {context.error}")
    
    if update and update.effective_message:
        await update.effective_message.reply_text(
            "❌ حدث خطأ في معالجة طلبك. يرجى المحاولة مرة أخرى."
        )

if __name__ == "__main__":
    main()import logging
import asyncio
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters
from config import Config
from handlers import Handlers
from admin_handlers import AdminHandlers
from database import Database

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Initialize database
db = Database()

def main():
    """Main function to run the bot"""
    # Check if bot token is provided
    if not Config.BOT_TOKEN:
        logger.error("Bot token not provided. Please set BOT_TOKEN in .env file")
        return
    
    # Create application
    application = Application.builder().token(Config.BOT_TOKEN).build()
    
    # Add handlers
    
    # Command handlers
    application.add_handler(CommandHandler("start", Handlers.start))
    application.add_handler(CommandHandler("help", Handlers.help_command))
    application.add_handler(CommandHandler("profile", Handlers.profile))
    application.add_handler(CommandHandler("balance", Handlers.balance))
    application.add_handler(CommandHandler("channels", Handlers.channels))
    application.add_handler(CommandHandler("referral", Handlers.referral))
    application.add_handler(CommandHandler("services", Handlers.services))
    application.add_handler(CommandHandler("orders", Handlers.orders))
    application.add_handler(CommandHandler("stats", Handlers.stats))
    
    # Admin command handlers
    application.add_handler(CommandHandler("admin", AdminHandlers.admin_menu))
    application.add_handler(CommandHandler("admin_stats", AdminHandlers.bot_stats))
    application.add_handler(CommandHandler("users", AdminHandlers.users_list))
    application.add_handler(CommandHandler("broadcast", AdminHandlers.broadcast_message))
    application.add_handler(CommandHandler("send_points", AdminHandlers.send_points))
    
    # Callback query handler
    application.add_handler(CallbackQueryHandler(handle_callback_query))
    
    # Message handlers
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_message))
    
    # Error handler
    application.add_error_handler(error_handler)
    
    # Start the bot
    logger.info("Starting bot...")
    application.run_polling(allowed_updates=["message", "callback_query"])

async def handle_callback_query(update, context):
    """Handle callback queries"""
    query = update.callback_query
    user_id = query.from_user.id
    
    # Admin callbacks
    if query.data.startswith(('add_channel', 'remove_channel', 'list_channels', 'all_orders', 
                              'pending_orders', 'complete_order', 'cancel_order_admin', 
                              'admin_complete_', 'admin_cancel_', 'back_to_admin')):
        await AdminHandlers.handle_admin_callback(query, context)
    else:
        await Handlers.button_callback(update, context)

async def handle_text_message(update, context):
    """Handle text messages"""
    user_id = update.effective_user.id
    
    # Admin text messages
    if update.message.text in ["📊 إحصائيات البوت", "👥 المستخدمين", "📢 إدارة القنوات", 
                               "📦 إدارة الطلبات", "✉️ رسالة جماعية", "💎 إرسال نقاط", 
                               "🔙 القائمة الرئيسية"]:
        await AdminHandlers.handle_admin_text(update, context)
    
    # Admin input handling
    elif context.user_data.get('admin_waiting_for'):
        await AdminHandlers.handle_admin_input(update, context)
    
    # Regular user messages
    else:
        await Handlers.handle_text_message(update, context)

async def error_handler(update, context):
    """Handle errors"""
    logger.error(f"Update {update} caused error {context.error}")
    
    if update and update.effective_message:
        await update.effective_message.reply_text(
            "❌ حدث خطأ في معالجة طلبك. يرجى المحاولة مرة أخرى."
        )

if __name__ == "__main__":
    main()