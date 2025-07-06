import os

class Config:
    # Bot Configuration
    BOT_TOKEN = os.getenv('BOT_TOKEN', 'YOUR_BOT_TOKEN_HERE')
    ADMIN_ID = int(os.getenv('ADMIN_ID', '123456789'))
    
    # Database
    DB_NAME = os.getenv('DB_NAME', 'bot_database.db')
    
    # Points System
    POINTS_PER_CHANNEL_JOIN = int(os.getenv('POINTS_PER_CHANNEL_JOIN', '10'))
    POINTS_PER_LIKE = int(os.getenv('POINTS_PER_LIKE', '5'))
    POINTS_PER_VIEW = int(os.getenv('POINTS_PER_VIEW', '3'))
    POINTS_PER_REFERRAL = int(os.getenv('POINTS_PER_REFERRAL', '20'))
    
    # Service Costs (points per 1000)
    FOLLOWERS_COST = int(os.getenv('FOLLOWERS_COST', '50'))
    LIKES_COST = int(os.getenv('LIKES_COST', '30'))
    VIEWS_COST = int(os.getenv('VIEWS_COST', '20'))
    
    # Additional Settings
    DAILY_ORDER_LIMIT = int(os.getenv('DAILY_ORDER_LIMIT', '5'))
    MAX_POINTS_PER_USER = int(os.getenv('MAX_POINTS_PER_USER', '100000'))
    ORDER_COOLDOWN = int(os.getenv('ORDER_COOLDOWN', '300'))
    MAINTENANCE_MODE = os.getenv('MAINTENANCE_MODE', 'false').lower() == 'true'
    
    # Messages
    WELCOME_MESSAGE = """
🎉 أهلاً بك في بوت الرشق المتقدم! 🎉

🔥 احصل على نقاط مجانية من خلال:
• الاشتراك في القنوات (+{} نقطة)
• مشاهدة المنشورات (+{} نقطة)
• الإعجابات (+{} نقطة)
• دعوة الأصدقاء (+{} نقطة)

💎 استخدم النقاط لشراء:
• متابعين ({} نقطة لكل 1000)
• إعجابات ({} نقطة لكل 1000)
• مشاهدات ({} نقطة لكل 1000)

استخدم /start للبدء أو /help للمساعدة
    """.format(
        POINTS_PER_CHANNEL_JOIN, POINTS_PER_VIEW, POINTS_PER_LIKE, 
        POINTS_PER_REFERRAL, FOLLOWERS_COST, LIKES_COST, VIEWS_COST
    )
    
    HELP_MESSAGE = """
📚 مساعدة البوت:

👤 للمستخدمين:
/start - بدء استخدام البوت
/balance - عرض رصيد النقاط
/earn - كسب نقاط مجانية
/order - طلب خدمة
/orders - عرض طلباتي
/referral - رابط الإحالة

🔧 للأدمن:
/admin - لوحة الإدارة
/stats - إحصائيات البوت
/broadcast - إرسال رسالة جماعية
/add_channel - إضافة قناة
/remove_channel - إزالة قناة
/orders_admin - إدارة الطلبات
    """
    
    ADMIN_HELP_MESSAGE = """
🛠️ أوامر الأدمن:

📊 الإحصائيات:
/stats - عرض إحصائيات البوت
/users - قائمة المستخدمين

📢 الرسائل:
/broadcast - إرسال رسالة جماعية
/send_message - إرسال رسالة لمستخدم

📺 إدارة القنوات:
/add_channel - إضافة قناة جديدة
/remove_channel - إزالة قناة
/channels - عرض جميع القنوات

🛠️ إدارة الطلبات:
/orders_admin - عرض جميع الطلبات
/complete_order - إكمال طلب
/cancel_order - إلغاء طلب
    """