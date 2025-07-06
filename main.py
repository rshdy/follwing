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

async def main():
    """Main function to run the bot"""
    logger.info("Starting Telegram Bot...")
    
    # Initialize database
    db = Database()
    await db.initialize()
    
    # Create application
    application = Application.builder().token(Config.BOT_TOKEN).build()
    
    # Initialize handlers
    handlers = Handlers(db)
    admin_handlers = AdminHandlers(db)
    
    # Add handlers
    application.add_handler(CommandHandler("start", handlers.start))
    application.add_handler(CommandHandler("help", handlers.help))
    application.add_handler(CommandHandler("earn", handlers.earn))
    application.add_handler(CommandHandler("order", handlers.order))
    application.add_handler(CommandHandler("balance", handlers.balance))
    application.add_handler(CommandHandler("profile", handlers.profile))
    application.add_handler(CommandHandler("leaderboard", handlers.leaderboard))
    application.add_handler(CommandHandler("support", handlers.support))
    
    # Admin handlers
    application.add_handler(CommandHandler("admin", admin_handlers.admin_panel))
    application.add_handler(CommandHandler("stats", admin_handlers.stats))
    application.add_handler(CommandHandler("broadcast", admin_handlers.broadcast))
    application.add_handler(CommandHandler("addpoints", admin_handlers.add_points))
    application.add_handler(CommandHandler("removepoints", admin_handlers.remove_points))
    application.add_handler(CommandHandler("ban", admin_handlers.ban_user))
    application.add_handler(CommandHandler("unban", admin_handlers.unban_user))
    application.add_handler(CommandHandler("setprice", admin_handlers.set_price))
    application.add_handler(CommandHandler("users", admin_handlers.list_users))
    
    # Callback query handlers
    application.add_handler(CallbackQueryHandler(handlers.button_callback))
    application.add_handler(CallbackQueryHandler(admin_handlers.admin_callback))
    
    # Message handlers
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.handle_message))
    application.add_handler(MessageHandler(filters.CONTACT, handlers.handle_contact))
    application.add_handler(MessageHandler(filters.PHOTO, handlers.handle_photo))
    application.add_handler(MessageHandler(filters.DOCUMENT, handlers.handle_document))
    
    # Add error handler
    application.add_error_handler(error_handler)
    
    # Run the bot
    logger.info("Bot started successfully!")
    await application.initialize()
    await application.start()
    await application.updater.start_polling(drop_pending_updates=True)
    
    try:
        await application.updater.idle()
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    finally:
        await application.updater.stop()
        await application.stop()
        await application.shutdown()

async def error_handler(update, context):
    """Handle errors"""
    logger.error(f"Update {update} caused error {context.error}")
    
    if update and update.effective_message:
        await update.effective_message.reply_text(
            "❌ حدث خطأ في معالجة طلبك. يرجى المحاولة مرة أخرى."
        )

if __name__ == "__main__":
    asyncio.run(main())
