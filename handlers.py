import logging
from telegram import Update, ChatMember
from telegram.ext import ContextTypes
from telegram.error import BadRequest
from database import Database
from config import Config
from keyboards import Keyboards
from utils import Utils

# Initialize database
db = Database()

class Handlers:
    @staticmethod
    async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        user = update.effective_user
        
        # Add user to database
        db.add_user(user.id, user.username, user.first_name)
        
        # Check for referral
        if context.args:
            referral_id = Utils.extract_referral_id(context.args[0])
            if referral_id and referral_id != user.id:
                # Check if referral already exists
                existing_user = db.get_user(user.id)
                if existing_user and existing_user[5] == 0:  # Not referred before
                    db.add_referral(referral_id, user.id, Config.POINTS_PER_REFERRAL)
                    await context.bot.send_message(
                        referral_id,
                        f"🎉 تم إحضار صديق جديد!\n💎 حصلت على {Config.POINTS_PER_REFERRAL} نقطة"
                    )
        
        await update.message.reply_text(
            Config.WELCOME_MESSAGE,
            reply_markup=Keyboards.main_menu()
        )
    
    @staticmethod
    async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        user_id = update.effective_user.id
        
        if Utils.is_admin(user_id):
            await update.message.reply_text(
                Config.HELP_MESSAGE + "\n\n" + Config.ADMIN_HELP
            )
        else:
            await update.message.reply_text(Config.HELP_MESSAGE)
    
    @staticmethod
    async def profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle profile command"""
        user_id = update.effective_user.id
        user_data = db.get_user(user_id)
        
        if not user_data:
            await update.message.reply_text("❌ المستخدم غير موجود في قاعدة البيانات")
            return
        
        user_id, username, first_name, points, referrals, joined_date, is_banned = user_data
        
        profile_text = f"""
👤 الملف الشخصي:

📛 الاسم: {first_name}
🏷️ المعرف: @{username if username else 'غير محدد'}
💎 النقاط: {Utils.format_number(points)}
👥 الإحالات: {referrals}
📅 تاريخ الانضمام: {Utils.format_date(joined_date)}
        """
        
        await update.message.reply_text(profile_text)
    
    @staticmethod
    async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle balance command"""
        user_id = update.effective_user.id
        user_data = db.get_user(user_id)
        
        if not user_data:
            await update.message.reply_text("❌ المستخدم غير موجود في قاعدة البيانات")
            return
        
        points = user_data[3]
        await update.message.reply_text(f"💎 رصيدك الحالي: {Utils.format_number(points)} نقطة")
    
    @staticmethod
    async def channels(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle channels command"""
        channels = db.get_all_channels()
        
        if not channels:
            await update.message.reply_text("📢 لا توجد قنوات متاحة حالياً")
            return
        
        text = "📢 اشترك في القنوات التالية للحصول على نقاط:\n\n"
        
        await update.message.reply_text(
            text,
            reply_markup=Keyboards.channels_keyboard(channels)
        )
    
    @staticmethod
    async def referral(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle referral command"""
        user_id = update.effective_user.id
        bot_username = context.bot.username
        
        referral_link = Utils.generate_referral_link(user_id, bot_username)
        
        text = f"""
🎯 رابط الإحالة الخاص بك:

{referral_link}

💎 احصل على {Config.POINTS_PER_REFERRAL} نقطة عن كل صديق تدعوه!

📝 كيفية الاستخدام:
1. انسخ الرابط أعلاه
2. أرسله لأصدقائك
3. عندما يبدأون البوت ستحصل على نقاط فوراً!
        """
        
        await update.message.reply_text(text)
    
    @staticmethod
    async def services(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle services command"""
        text = """
🚀 الخدمات المتاحة:

👥 متابعين انستغرام - {} نقطة
❤️ إعجابات انستغرام - {} نقطة  
👀 مشاهدات انستغرام - {} نقطة
👥 متابعين تيكتوك - {} نقطة
❤️ إعجابات تيكتوك - {} نقطة
👀 مشاهدات تيكتوك - {} نقطة

اختر الخدمة التي تريدها:
        """.format(
            Config.FOLLOWERS_COST, Config.LIKES_COST, Config.VIEWS_COST,
            Config.FOLLOWERS_COST, Config.LIKES_COST, Config.VIEWS_COST
        )
        
        await update.message.reply_text(
            text,
            reply_markup=Keyboards.services_menu()
        )
    
    @staticmethod
    async def orders(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle orders command"""
        user_id = update.effective_user.id
        orders = db.get_user_orders(user_id)
        
        if not orders:
            await update.message.reply_text("📋 لا توجد لديك طلبات")
            return
        
        text = "📋 طلباتك:\n\n"
        
        for order in orders[-10:]:  # Show last 10 orders
            order_id, _, service_type, target_url, quantity, points_cost, status, created_date, _ = order
            text += f"""
🔸 طلب #{order_id}
🚀 {Utils.format_service_name(service_type)}
📊 {Utils.format_number(quantity)}
📈 {Utils.format_order_status(status)}
📅 {Utils.format_date(created_date)}
────────────────
            """
        
        await update.message.reply_text(text)
    
    @staticmethod
    async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle stats command"""
        user_id = update.effective_user.id
        user_data = db.get_user(user_id)
        user_orders = db.get_user_orders(user_id)
        
        if not user_data:
            await update.message.reply_text("❌ المستخدم غير موجود")
            return
        
        completed_orders = len([o for o in user_orders if o[6] == 'completed'])
        pending_orders = len([o for o in user_orders if o[6] == 'pending'])
        
        text = f"""
📊 إحصائياتك:

💎 النقاط: {Utils.format_number(user_data[3])}
👥 الإحالات: {user_data[4]}
📋 إجمالي الطلبات: {len(user_orders)}
✅ الطلبات المكتملة: {completed_orders}
⏳ الطلبات المعلقة: {pending_orders}
📅 عضو منذ: {Utils.format_date(user_data[5])}
        """
        
        await update.message.reply_text(text)
    
    @staticmethod
    async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle button callbacks"""
        query = update.callback_query
        await query.answer()
        
        data = query.data
        user_id = query.from_user.id
        
        if data == "back_to_main":
            await query.edit_message_text(
                "🏠 القائمة الرئيسية",
                reply_markup=Keyboards.main_menu()
            )
        
        elif data == "back_to_services":
            await query.edit_message_text(
                "🚀 اختر الخدمة:",
                reply_markup=Keyboards.services_menu()
            )
        
        elif data.startswith("service_"):
            service_type = data.replace("service_", "")
            context.user_data['service_type'] = service_type
            
            await query.edit_message_text(
                f"📊 اختر الكمية لـ {Utils.format_service_name(service_type)}:",
                reply_markup=Keyboards.quantity_keyboard(service_type)
            )
        
        elif data.startswith("quantity_"):
            parts = data.split("_")
            service_type = parts[1] + "_" + parts[2]
            quantity = parts[3]
            
            if quantity == "custom":
                await query.edit_message_text(
                    "📝 أرسل الكمية المطلوبة (رقم فقط):"
                )
                context.user_data['waiting_for_quantity'] = True
                context.user_data['service_type'] = service_type
                return
            
            quantity = int(quantity)
            context.user_data['quantity'] = quantity
            
            await query.edit_message_text(
                f"🎯 أرسل الرابط المراد رشقه:\n\n"
                f"🚀 الخدمة: {Utils.format_service_name(service_type)}\n"
                f"📊 الكمية: {Utils.format_number(quantity)}"
            )
            context.user_data['waiting_for_url'] = True
        
        elif data == "check_subscriptions":
            await Handlers.check_subscriptions(query, context)
        
        elif data.startswith("confirm_order_"):
            order_id = int(data.replace("confirm_order_", ""))
            await Handlers.confirm_order(query, context, order_id)
        
        elif data == "cancel_order":
            await query.edit_message_text("❌ تم إلغاء الطلب")
        
        # Admin callbacks
        elif Utils.is_admin(user_id):
            await Handlers.handle_admin_callback(query, context)
    
    @staticmethod
    async def check_subscriptions(query, context):
        """Check user subscriptions to channels"""
        user_id = query.from_user.id
        channels = db.get_all_channels()
        
        if not channels:
            await query.edit_message_text("📢 لا توجد قنوات متاحة")
            return
        
        earned_points = 0
        subscribed_channels = []
        
        for channel in channels:
            channel_id, channel_name, channel_username, points_reward = channel[1], channel[2], channel[3], channel[4]
            
            # Check if user already got points for this channel
            if db.check_user_subscription(user_id, channel_id):
                continue
            
            try:
                # Check if user is subscribed
                member = await context.bot.get_chat_member(channel_id, user_id)
                if member.status in [ChatMember.MEMBER, ChatMember.ADMINISTRATOR, ChatMember.OWNER]:
                    # Award points
                    db.update_user_points(user_id, points_reward)
                    db.add_user_subscription(user_id, channel_id)
                    earned_points += points_reward
                    subscribed_channels.append(channel_name)
            except BadRequest:
                continue
        
        if earned_points > 0:
            text = f"""
🎉 تم منحك {earned_points} نقطة!

📢 القنوات المشترك بها:
{chr(10).join(f"• {ch}" for ch in subscribed_channels)}

💎 رصيدك الحالي: {db.get_user(user_id)[3]} نقطة
            """
        else:
            text = "❌ لم تشترك في أي قناة جديدة أو حصلت على النقاط مسبقاً"
        
        await query.edit_message_text(text)
    
    @staticmethod
    async def confirm_order(query, context, order_id):
        """Confirm order creation"""
        user_id = query.from_user.id
        
        # Get order details from user_data
        service_type = context.user_data.get('service_type')
        target_url = context.user_data.get('target_url')
        quantity = context.user_data.get('quantity')
        
        if not all([service_type, target_url, quantity]):
            await query.edit_message_text("❌ بيانات الطلب غير مكتملة")
            return
        
        # Calculate cost
        cost = Utils.calculate_cost(service_type, quantity)
        
        # Check if user has enough points
        user_data = db.get_user(user_id)
        if user_data[3] < cost:
            await query.edit_message_text(
                f"❌ رصيدك غير كافي!\n"
                f"💎 المطلوب: {Utils.format_number(cost)} نقطة\n"
                f"💰 رصيدك: {Utils.format_number(user_data[3])} نقطة"
            )
            return
        
        # Deduct points and create order
        if db.deduct_points(user_id, cost):
            order_id = db.create_order(user_id, service_type, target_url, quantity, cost)
            
            await query.edit_message_text(
                f"✅ تم إنشاء طلبك بنجاح!\n\n"
                f"🔖 رقم الطلب: #{order_id}\n"
                f"📈 الحالة: {Utils.format_order_status('pending')}\n"
                f"💎 رصيدك المتبقي: {Utils.format_number(user_data[3] - cost)} نقطة\n\n"
                f"⏰ سيتم معالجة طلبك خلال 24 ساعة"
            )
            
            # Clear user data
            context.user_data.clear()
        else:
            await query.edit_message_text("❌ حدث خطأ في خصم النقاط")
    
    @staticmethod
    async def handle_text_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle text messages"""
        text = update.message.text
        user_id = update.effective_user.id
        
        # Handle button text
        if text == "💎 رصيد النقاط":
            await Handlers.balance(update, context)
        elif text == "👤 الملف الشخصي":
            await Handlers.profile(update, context)
        elif text == "🚀 طلب خدمة":
            await Handlers.services(update, context)
        elif text == "📋 طلباتي":
            await Handlers.orders(update, context)
        elif text == "📢 القنوات":
            await Handlers.channels(update, context)
        elif text == "🎯 رابط الإحالة":
            await Handlers.referral(update, context)
        elif text == "📊 الإحصائيات":
            await Handlers.stats(update, context)
        elif text == "ℹ️ المساعدة":
            await Handlers.help_command(update, context)
        
        # Handle admin menu
        elif Utils.is_admin(user_id):
            await Handlers.handle_admin_text(update, context)
        
        # Handle waiting states
        elif context.user_data.get('waiting_for_quantity'):
            try:
                quantity = int(text)
                if quantity <= 0 or quantity > 100000:
                    await update.message.reply_text("❌ الكمية يجب أن تكون بين 1 و 100,000")
                    return
                
                context.user_data['quantity'] = quantity
                context.user_data['waiting_for_quantity'] = False
                context.user_data['waiting_for_url'] = True
                
                service_type = context.user_data.get('service_type')
                await update.message.reply_text(
                    f"🎯 أرسل الرابط المراد رشقه:\n\n"
                    f"🚀 الخدمة: {Utils.format_service_name(service_type)}\n"
                    f"📊 الكمية: {Utils.format_number(quantity)}"
                )
            except ValueError:
                await update.message.reply_text("❌ يرجى إرسال رقم صحيح")
        
        elif context.user_data.get('waiting_for_url'):
            await Handlers.handle_url_input(update, context)
        
        # Handle admin waiting states
        elif Utils.is_admin(user_id):
            await Handlers.handle_admin_input(update, context)
    
    @staticmethod
    async def handle_url_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle URL input"""
        url = update.message.text.strip()
        service_type = context.user_data.get('service_type')
        quantity = context.user_data.get('quantity')
        
        if not service_type or not quantity:
            await update.message.reply_text("❌ بيانات الطلب غير مكتملة")
            return
        
        # Validate URL
        errors = Utils.validate_order_data(service_type, url, quantity)
        if errors:
            await update.message.reply_text(f"❌ خطأ في البيانات:\n" + "\n".join(errors))
            return
        
        context.user_data['target_url'] = url
        context.user_data['waiting_for_url'] = False
        
        # Calculate cost
        cost = Utils.calculate_cost(service_type, quantity)
        
        # Create order summary
        summary = Utils.create_order_summary(service_type, url, quantity, cost)
        
        await update.message.reply_text(
            summary,
            reply_markup=Keyboards.confirm_order_keyboard(0)
        )
    
    @staticmethod
    async def handle_admin_callback(query, context):
        """Handle admin callbacks"""
        from admin_handlers import AdminHandlers
        await AdminHandlers.handle_admin_callback(query, context)
    
    @staticmethod
    async def handle_admin_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle admin text messages"""
        from admin_handlers import AdminHandlers
        await AdminHandlers.handle_admin_text(update, context)
    
    @staticmethod
    async def handle_admin_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle admin input"""
        from admin_handlers import AdminHandlers
        await AdminHandlers.handle_admin_input(update, context)import logging
from telegram import Update, ChatMember
from telegram.ext import ContextTypes
from telegram.error import BadRequest
from database import Database
from config import Config
from keyboards import Keyboards
from utils import Utils

# Initialize database
db = Database()

class Handlers:
    @staticmethod
    async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        user = update.effective_user
        
        # Add user to database
        db.add_user(user.id, user.username, user.first_name)
        
        # Check for referral
        if context.args:
            referral_id = Utils.extract_referral_id(context.args[0])
            if referral_id and referral_id != user.id:
                # Check if referral already exists
                existing_user = db.get_user(user.id)
                if existing_user and existing_user[5] == 0:  # Not referred before
                    db.add_referral(referral_id, user.id, Config.POINTS_PER_REFERRAL)
                    await context.bot.send_message(
                        referral_id,
                        f"🎉 تم إحضار صديق جديد!\n💎 حصلت على {Config.POINTS_PER_REFERRAL} نقطة"
                    )
        
        await update.message.reply_text(
            Config.WELCOME_MESSAGE,
            reply_markup=Keyboards.main_menu()
        )
    
    @staticmethod
    async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        user_id = update.effective_user.id
        
        if Utils.is_admin(user_id):
            await update.message.reply_text(
                Config.HELP_MESSAGE + "\n\n" + Config.ADMIN_HELP
            )
        else:
            await update.message.reply_text(Config.HELP_MESSAGE)
    
    @staticmethod
    async def profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle profile command"""
        user_id = update.effective_user.id
        user_data = db.get_user(user_id)
        
        if not user_data:
            await update.message.reply_text("❌ المستخدم غير موجود في قاعدة البيانات")
            return
        
        user_id, username, first_name, points, referrals, joined_date, is_banned = user_data
        
        profile_text = f"""
👤 الملف الشخصي:

📛 الاسم: {first_name}
🏷️ المعرف: @{username if username else 'غير محدد'}
💎 النقاط: {Utils.format_number(points)}
👥 الإحالات: {referrals}
📅 تاريخ الانضمام: {Utils.format_date(joined_date)}
        """
        
        await update.message.reply_text(profile_text)
    
    @staticmethod
    async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle balance command"""
        user_id = update.effective_user.id
        user_data = db.get_user(user_id)
        
        if not user_data:
            await update.message.reply_text("❌ المستخدم غير موجود في قاعدة البيانات")
            return
        
        points = user_data[3]
        await update.message.reply_text(f"💎 رصيدك الحالي: {Utils.format_number(points)} نقطة")
    
    @staticmethod
    async def channels(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle channels command"""
        channels = db.get_all_channels()
        
        if not channels:
            await update.message.reply_text("📢 لا توجد قنوات متاحة حالياً")
            return
        
        text = "📢 اشترك في القنوات التالية للحصول على نقاط:\n\n"
        
        await update.message.reply_text(
            text,
            reply_markup=Keyboards.channels_keyboard(channels)
        )
    
    @staticmethod
    async def referral(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle referral command"""
        user_id = update.effective_user.id
        bot_username = context.bot.username
        
        referral_link = Utils.generate_referral_link(user_id, bot_username)
        
        text = f"""
🎯 رابط الإحالة الخاص بك:

{referral_link}

💎 احصل على {Config.POINTS_PER_REFERRAL} نقطة عن كل صديق تدعوه!

📝 كيفية الاستخدام:
1. انسخ الرابط أعلاه
2. أرسله لأصدقائك
3. عندما يبدأون البوت ستحصل على نقاط فوراً!
        """
        
        await update.message.reply_text(text)
    
    @staticmethod
    async def services(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle services command"""
        text = """
🚀 الخدمات المتاحة:

👥 متابعين انستغرام - {} نقطة
❤️ إعجابات انستغرام - {} نقطة  
👀 مشاهدات انستغرام - {} نقطة
👥 متابعين تيكتوك - {} نقطة
❤️ إعجابات تيكتوك - {} نقطة
👀 مشاهدات تيكتوك - {} نقطة

اختر الخدمة التي تريدها:
        """.format(
            Config.FOLLOWERS_COST, Config.LIKES_COST, Config.VIEWS_COST,
            Config.FOLLOWERS_COST, Config.LIKES_COST, Config.VIEWS_COST
        )
        
        await update.message.reply_text(
            text,
            reply_markup=Keyboards.services_menu()
        )
    
    @staticmethod
    async def orders(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle orders command"""
        user_id = update.effective_user.id
        orders = db.get_user_orders(user_id)
        
        if not orders:
            await update.message.reply_text("📋 لا توجد لديك طلبات")
            return
        
        text = "📋 طلباتك:\n\n"
        
        for order in orders[-10:]:  # Show last 10 orders
            order_id, _, service_type, target_url, quantity, points_cost, status, created_date, _ = order
            text += f"""
🔸 طلب #{order_id}
🚀 {Utils.format_service_name(service_type)}
📊 {Utils.format_number(quantity)}
📈 {Utils.format_order_status(status)}
📅 {Utils.format_date(created_date)}
────────────────
            """
        
        await update.message.reply_text(text)
    
    @staticmethod
    async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle stats command"""
        user_id = update.effective_user.id
        user_data = db.get_user(user_id)
        user_orders = db.get_user_orders(user_id)
        
        if not user_data:
            await update.message.reply_text("❌ المستخدم غير موجود")
            return
        
        completed_orders = len([o for o in user_orders if o[6] == 'completed'])
        pending_orders = len([o for o in user_orders if o[6] == 'pending'])
        
        text = f"""
📊 إحصائياتك:

💎 النقاط: {Utils.format_number(user_data[3])}
👥 الإحالات: {user_data[4]}
📋 إجمالي الطلبات: {len(user_orders)}
✅ الطلبات المكتملة: {completed_orders}
⏳ الطلبات المعلقة: {pending_orders}
📅 عضو منذ: {Utils.format_date(user_data[5])}
        """
        
        await update.message.reply_text(text)
    
    @staticmethod
    async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle button callbacks"""
        query = update.callback_query
        await query.answer()
        
        data = query.data
        user_id = query.from_user.id
        
        if data == "back_to_main":
            await query.edit_message_text(
                "🏠 القائمة الرئيسية",
                reply_markup=Keyboards.main_menu()
            )
        
        elif data == "back_to_services":
            await query.edit_message_text(
                "🚀 اختر الخدمة:",
                reply_markup=Keyboards.services_menu()
            )
        
        elif data.startswith("service_"):
            service_type = data.replace("service_", "")
            context.user_data['service_type'] = service_type
            
            await query.edit_message_text(
                f"📊 اختر الكمية لـ {Utils.format_service_name(service_type)}:",
                reply_markup=Keyboards.quantity_keyboard(service_type)
            )
        
        elif data.startswith("quantity_"):
            parts = data.split("_")
            service_type = parts[1] + "_" + parts[2]
            quantity = parts[3]
            
            if quantity == "custom":
                await query.edit_message_text(
                    "📝 أرسل الكمية المطلوبة (رقم فقط):"
                )
                context.user_data['waiting_for_quantity'] = True
                context.user_data['service_type'] = service_type
                return
            
            quantity = int(quantity)
            context.user_data['quantity'] = quantity
            
            await query.edit_message_text(
                f"🎯 أرسل الرابط المراد رشقه:\n\n"
                f"🚀 الخدمة: {Utils.format_service_name(service_type)}\n"
                f"📊 الكمية: {Utils.format_number(quantity)}"
            )
            context.user_data['waiting_for_url'] = True
        
        elif data == "check_subscriptions":
            await Handlers.check_subscriptions(query, context)
        
        elif data.startswith("confirm_order_"):
            order_id = int(data.replace("confirm_order_", ""))
            await Handlers.confirm_order(query, context, order_id)
        
        elif data == "cancel_order":
            await query.edit_message_text("❌ تم إلغاء الطلب")
        
        # Admin callbacks
        elif Utils.is_admin(user_id):
            await Handlers.handle_admin_callback(query, context)
    
    @staticmethod
    async def check_subscriptions(query, context):
        """Check user subscriptions to channels"""
        user_id = query.from_user.id
        channels = db.get_all_channels()
        
        if not channels:
            await query.edit_message_text("📢 لا توجد قنوات متاحة")
            return
        
        earned_points = 0
        subscribed_channels = []
        
        for channel in channels:
            channel_id, channel_name, channel_username, points_reward = channel[1], channel[2], channel[3], channel[4]
            
            # Check if user already got points for this channel
            if db.check_user_subscription(user_id, channel_id):
                continue
            
            try:
                # Check if user is subscribed
                member = await context.bot.get_chat_member(channel_id, user_id)
                if member.status in [ChatMember.MEMBER, ChatMember.ADMINISTRATOR, ChatMember.OWNER]:
                    # Award points
                    db.update_user_points(user_id, points_reward)
                    db.add_user_subscription(user_id, channel_id)
                    earned_points += points_reward
                    subscribed_channels.append(channel_name)
            except BadRequest:
                continue
        
        if earned_points > 0:
            text = f"""
🎉 تم منحك {earned_points} نقطة!

📢 القنوات المشترك بها:
{chr(10).join(f"• {ch}" for ch in subscribed_channels)}

💎 رصيدك الحالي: {db.get_user(user_id)[3]} نقطة
            """
        else:
            text = "❌ لم تشترك في أي قناة جديدة أو حصلت على النقاط مسبقاً"
        
        await query.edit_message_text(text)
    
    @staticmethod
    async def confirm_order(query, context, order_id):
        """Confirm order creation"""
        user_id = query.from_user.id
        
        # Get order details from user_data
        service_type = context.user_data.get('service_type')
        target_url = context.user_data.get('target_url')
        quantity = context.user_data.get('quantity')
        
        if not all([service_type, target_url, quantity]):
            await query.edit_message_text("❌ بيانات الطلب غير مكتملة")
            return
        
        # Calculate cost
        cost = Utils.calculate_cost(service_type, quantity)
        
        # Check if user has enough points
        user_data = db.get_user(user_id)
        if user_data[3] < cost:
            await query.edit_message_text(
                f"❌ رصيدك غير كافي!\n"
                f"💎 المطلوب: {Utils.format_number(cost)} نقطة\n"
                f"💰 رصيدك: {Utils.format_number(user_data[3])} نقطة"
            )
            return
        
        # Deduct points and create order
        if db.deduct_points(user_id, cost):
            order_id = db.create_order(user_id, service_type, target_url, quantity, cost)
            
            await query.edit_message_text(
                f"✅ تم إنشاء طلبك بنجاح!\n\n"
                f"🔖 رقم الطلب: #{order_id}\n"
                f"📈 الحالة: {Utils.format_order_status('pending')}\n"
                f"💎 رصيدك المتبقي: {Utils.format_number(user_data[3] - cost)} نقطة\n\n"
                f"⏰ سيتم معالجة طلبك خلال 24 ساعة"
            )
            
            # Clear user data
            context.user_data.clear()
        else:
            await query.edit_message_text("❌ حدث خطأ في خصم النقاط")
    
    @staticmethod
    async def handle_text_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle text messages"""
        text = update.message.text
        user_id = update.effective_user.id
        
        # Handle button text
        if text == "💎 رصيد النقاط":
            await Handlers.balance(update, context)
        elif text == "👤 الملف الشخصي":
            await Handlers.profile(update, context)
        elif text == "🚀 طلب خدمة":
            await Handlers.services(update, context)
        elif text == "📋 طلباتي":
            await Handlers.orders(update, context)
        elif text == "📢 القنوات":
            await Handlers.channels(update, context)
        elif text == "🎯 رابط الإحالة":
            await Handlers.referral(update, context)
        elif text == "📊 الإحصائيات":
            await Handlers.stats(update, context)
        elif text == "ℹ️ المساعدة":
            await Handlers.help_command(update, context)
        
        # Handle admin menu
        elif Utils.is_admin(user_id):
            await Handlers.handle_admin_text(update, context)
        
        # Handle waiting states
        elif context.user_data.get('waiting_for_quantity'):
            try:
                quantity = int(text)
                if quantity <= 0 or quantity > 100000:
                    await update.message.reply_text("❌ الكمية يجب أن تكون بين 1 و 100,000")
                    return
                
                context.user_data['quantity'] = quantity
                context.user_data['waiting_for_quantity'] = False
                context.user_data['waiting_for_url'] = True
                
                service_type = context.user_data.get('service_type')
                await update.message.reply_text(
                    f"🎯 أرسل الرابط المراد رشقه:\n\n"
                    f"🚀 الخدمة: {Utils.format_service_name(service_type)}\n"
                    f"📊 الكمية: {Utils.format_number(quantity)}"
                )
            except ValueError:
                await update.message.reply_text("❌ يرجى إرسال رقم صحيح")
        
        elif context.user_data.get('waiting_for_url'):
            await Handlers.handle_url_input(update, context)
        
        # Handle admin waiting states
        elif Utils.is_admin(user_id):
            await Handlers.handle_admin_input(update, context)
    
    @staticmethod
    async def handle_url_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle URL input"""
        url = update.message.text.strip()
        service_type = context.user_data.get('service_type')
        quantity = context.user_data.get('quantity')
        
        if not service_type or not quantity:
            await update.message.reply_text("❌ بيانات الطلب غير مكتملة")
            return
        
        # Validate URL
        errors = Utils.validate_order_data(service_type, url, quantity)
        if errors:
            await update.message.reply_text(f"❌ خطأ في البيانات:\n" + "\n".join(errors))
            return
        
        context.user_data['target_url'] = url
        context.user_data['waiting_for_url'] = False
        
        # Calculate cost
        cost = Utils.calculate_cost(service_type, quantity)
        
        # Create order summary
        summary = Utils.create_order_summary(service_type, url, quantity, cost)
        
        await update.message.reply_text(
            summary,
            reply_markup=Keyboards.confirm_order_keyboard(0)
        )
    
    @staticmethod
    async def handle_admin_callback(query, context):
        """Handle admin callbacks"""
        from admin_handlers import AdminHandlers
        await AdminHandlers.handle_admin_callback(query, context)
    
    @staticmethod
    async def handle_admin_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle admin text messages"""
        from admin_handlers import AdminHandlers
        await AdminHandlers.handle_admin_text(update, context)
    
    @staticmethod
    async def handle_admin_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle admin input"""
        from admin_handlers import AdminHandlers
        await AdminHandlers.handle_admin_input(update, context)import logging
from telegram import Update, ChatMember
from telegram.ext import ContextTypes
from telegram.error import BadRequest
from database import Database
from config import Config
from keyboards import Keyboards
from utils import Utils

# Initialize database
db = Database()

class Handlers:
    @staticmethod
    async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        user = update.effective_user
        
        # Add user to database
        db.add_user(user.id, user.username, user.first_name)
        
        # Check for referral
        if context.args:
            referral_id = Utils.extract_referral_id(context.args[0])
            if referral_id and referral_id != user.id:
                # Check if referral already exists
                existing_user = db.get_user(user.id)
                if existing_user and existing_user[5] == 0:  # Not referred before
                    db.add_referral(referral_id, user.id, Config.POINTS_PER_REFERRAL)
                    await context.bot.send_message(
                        referral_id,
                        f"🎉 تم إحضار صديق جديد!\n💎 حصلت على {Config.POINTS_PER_REFERRAL} نقطة"
                    )
        
        await update.message.reply_text(
            Config.WELCOME_MESSAGE,
            reply_markup=Keyboards.main_menu()
        )
    
    @staticmethod
    async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        user_id = update.effective_user.id
        
        if Utils.is_admin(user_id):
            await update.message.reply_text(
                Config.HELP_MESSAGE + "\n\n" + Config.ADMIN_HELP
            )
        else:
            await update.message.reply_text(Config.HELP_MESSAGE)
    
    @staticmethod
    async def profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle profile command"""
        user_id = update.effective_user.id
        user_data = db.get_user(user_id)
        
        if not user_data:
            await update.message.reply_text("❌ المستخدم غير موجود في قاعدة البيانات")
            return
        
        user_id, username, first_name, points, referrals, joined_date, is_banned = user_data
        
        profile_text = f"""
👤 الملف الشخصي:

📛 الاسم: {first_name}
🏷️ المعرف: @{username if username else 'غير محدد'}
💎 النقاط: {Utils.format_number(points)}
👥 الإحالات: {referrals}
📅 تاريخ الانضمام: {Utils.format_date(joined_date)}
        """
        
        await update.message.reply_text(profile_text)
    
    @staticmethod
    async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle balance command"""
        user_id = update.effective_user.id
        user_data = db.get_user(user_id)
        
        if not user_data:
            await update.message.reply_text("❌ المستخدم غير موجود في قاعدة البيانات")
            return
        
        points = user_data[3]
        await update.message.reply_text(f"💎 رصيدك الحالي: {Utils.format_number(points)} نقطة")
    
    @staticmethod
    async def channels(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle channels command"""
        channels = db.get_all_channels()
        
        if not channels:
            await update.message.reply_text("📢 لا توجد قنوات متاحة حالياً")
            return
        
        text = "📢 اشترك في القنوات التالية للحصول على نقاط:\n\n"
        
        await update.message.reply_text(
            text,
            reply_markup=Keyboards.channels_keyboard(channels)
        )
    
    @staticmethod
    async def referral(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle referral command"""
        user_id = update.effective_user.id
        bot_username = context.bot.username
        
        referral_link = Utils.generate_referral_link(user_id, bot_username)
        
        text = f"""
🎯 رابط الإحالة الخاص بك:

{referral_link}

💎 احصل على {Config.POINTS_PER_REFERRAL} نقطة عن كل صديق تدعوه!

📝 كيفية الاستخدام:
1. انسخ الرابط أعلاه
2. أرسله لأصدقائك
3. عندما يبدأون البوت ستحصل على نقاط فوراً!
        """
        
        await update.message.reply_text(text)
    
    @staticmethod
    async def services(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle services command"""
        text = """
🚀 الخدمات المتاحة:

👥 متابعين انستغرام - {} نقطة
❤️ إعجابات انستغرام - {} نقطة  
👀 مشاهدات انستغرام - {} نقطة
👥 متابعين تيكتوك - {} نقطة
❤️ إعجابات تيكتوك - {} نقطة
👀 مشاهدات تيكتوك - {} نقطة

اختر الخدمة التي تريدها:
        """.format(
            Config.FOLLOWERS_COST, Config.LIKES_COST, Config.VIEWS_COST,
            Config.FOLLOWERS_COST, Config.LIKES_COST, Config.VIEWS_COST
        )
        
        await update.message.reply_text(
            text,
            reply_markup=Keyboards.services_menu()
        )
    
    @staticmethod
    async def orders(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle orders command"""
        user_id = update.effective_user.id
        orders = db.get_user_orders(user_id)
        
        if not orders:
            await update.message.reply_text("📋 لا توجد لديك طلبات")
            return
        
        text = "📋 طلباتك:\n\n"
        
        for order in orders[-10:]:  # Show last 10 orders
            order_id, _, service_type, target_url, quantity, points_cost, status, created_date, _ = order
            text += f"""
🔸 طلب #{order_id}
🚀 {Utils.format_service_name(service_type)}
📊 {Utils.format_number(quantity)}
📈 {Utils.format_order_status(status)}
📅 {Utils.format_date(created_date)}
────────────────
            """
        
        await update.message.reply_text(text)
    
    @staticmethod
    async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle stats command"""
        user_id = update.effective_user.id
        user_data = db.get_user(user_id)
        user_orders = db.get_user_orders(user_id)
        
        if not user_data:
            await update.message.reply_text("❌ المستخدم غير موجود")
            return
        
        completed_orders = len([o for o in user_orders if o[6] == 'completed'])
        pending_orders = len([o for o in user_orders if o[6] == 'pending'])
        
        text = f"""
📊 إحصائياتك:

💎 النقاط: {Utils.format_number(user_data[3])}
👥 الإحالات: {user_data[4]}
📋 إجمالي الطلبات: {len(user_orders)}
✅ الطلبات المكتملة: {completed_orders}
⏳ الطلبات المعلقة: {pending_orders}
📅 عضو منذ: {Utils.format_date(user_data[5])}
        """
        
        await update.message.reply_text(text)
    
    @staticmethod
    async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle button callbacks"""
        query = update.callback_query
        await query.answer()
        
        data = query.data
        user_id = query.from_user.id
        
        if data == "back_to_main":
            await query.edit_message_text(
                "🏠 القائمة الرئيسية",
                reply_markup=Keyboards.main_menu()
            )
        
        elif data == "back_to_services":
            await query.edit_message_text(
                "🚀 اختر الخدمة:",
                reply_markup=Keyboards.services_menu()
            )
        
        elif data.startswith("service_"):
            service_type = data.replace("service_", "")
            context.user_data['service_type'] = service_type
            
            await query.edit_message_text(
                f"📊 اختر الكمية لـ {Utils.format_service_name(service_type)}:",
                reply_markup=Keyboards.quantity_keyboard(service_type)
            )
        
        elif data.startswith("quantity_"):
            parts = data.split("_")
            service_type = parts[1] + "_" + parts[2]
            quantity = parts[3]
            
            if quantity == "custom":
                await query.edit_message_text(
                    "📝 أرسل الكمية المطلوبة (رقم فقط):"
                )
                context.user_data['waiting_for_quantity'] = True
                context.user_data['service_type'] = service_type
                return
            
            quantity = int(quantity)
            context.user_data['quantity'] = quantity
            
            await query.edit_message_text(
                f"🎯 أرسل الرابط المراد رشقه:\n\n"
                f"🚀 الخدمة: {Utils.format_service_name(service_type)}\n"
                f"📊 الكمية: {Utils.format_number(quantity)}"
            )
            context.user_data['waiting_for_url'] = True
        
        elif data == "check_subscriptions":
            await Handlers.check_subscriptions(query, context)
        
        elif data.startswith("confirm_order_"):
            order_id = int(data.replace("confirm_order_", ""))
            await Handlers.confirm_order(query, context, order_id)
        
        elif data == "cancel_order":
            await query.edit_message_text("❌ تم إلغاء الطلب")
        
        # Admin callbacks
        elif Utils.is_admin(user_id):
            await Handlers.handle_admin_callback(query, context)
    
    @staticmethod
    async def check_subscriptions(query, context):
        """Check user subscriptions to channels"""
        user_id = query.from_user.id
        channels = db.get_all_channels()
        
        if not channels:
            await query.edit_message_text("📢 لا توجد قنوات متاحة")
            return
        
        earned_points = 0
        subscribed_channels = []
        
        for channel in channels:
            channel_id, channel_name, channel_username, points_reward = channel[1], channel[2], channel[3], channel[4]
            
            # Check if user already got points for this channel
            if db.check_user_subscription(user_id, channel_id):
                continue
            
            try:
                # Check if user is subscribed
                member = await context.bot.get_chat_member(channel_id, user_id)
                if member.status in [ChatMember.MEMBER, ChatMember.ADMINISTRATOR, ChatMember.OWNER]:
                    # Award points
                    db.update_user_points(user_id, points_reward)
                    db.add_user_subscription(user_id, channel_id)
                    earned_points += points_reward
                    subscribed_channels.append(channel_name)
            except BadRequest:
                continue
        
        if earned_points > 0:
            text = f"""
🎉 تم منحك {earned_points} نقطة!

📢 القنوات المشترك بها:
{chr(10).join(f"• {ch}" for ch in subscribed_channels)}

💎 رصيدك الحالي: {db.get_user(user_id)[3]} نقطة
            """
        else:
            text = "❌ لم تشترك في أي قناة جديدة أو حصلت على النقاط مسبقاً"
        
        await query.edit_message_text(text)
    
    @staticmethod
    async def confirm_order(query, context, order_id):
        """Confirm order creation"""
        user_id = query.from_user.id
        
        # Get order details from user_data
        service_type = context.user_data.get('service_type')
        target_url = context.user_data.get('target_url')
        quantity = context.user_data.get('quantity')
        
        if not all([service_type, target_url, quantity]):
            await query.edit_message_text("❌ بيانات الطلب غير مكتملة")
            return
        
        # Calculate cost
        cost = Utils.calculate_cost(service_type, quantity)
        
        # Check if user has enough points
        user_data = db.get_user(user_id)
        if user_data[3] < cost:
            await query.edit_message_text(
                f"❌ رصيدك غير كافي!\n"
                f"💎 المطلوب: {Utils.format_number(cost)} نقطة\n"
                f"💰 رصيدك: {Utils.format_number(user_data[3])} نقطة"
            )
            return
        
        # Deduct points and create order
        if db.deduct_points(user_id, cost):
            order_id = db.create_order(user_id, service_type, target_url, quantity, cost)
            
            await query.edit_message_text(
                f"✅ تم إنشاء طلبك بنجاح!\n\n"
                f"🔖 رقم الطلب: #{order_id}\n"
                f"📈 الحالة: {Utils.format_order_status('pending')}\n"
                f"💎 رصيدك المتبقي: {Utils.format_number(user_data[3] - cost)} نقطة\n\n"
                f"⏰ سيتم معالجة طلبك خلال 24 ساعة"
            )
            
            # Clear user data
            context.user_data.clear()
        else:
            await query.edit_message_text("❌ حدث خطأ في خصم النقاط")
    
    @staticmethod
    async def handle_text_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle text messages"""
        text = update.message.text
        user_id = update.effective_user.id
        
        # Handle button text
        if text == "💎 رصيد النقاط":
            await Handlers.balance(update, context)
        elif text == "👤 الملف الشخصي":
            await Handlers.profile(update, context)
        elif text == "🚀 طلب خدمة":
            await Handlers.services(update, context)
        elif text == "📋 طلباتي":
            await Handlers.orders(update, context)
        elif text == "📢 القنوات":
            await Handlers.channels(update, context)
        elif text == "🎯 رابط الإحالة":
            await Handlers.referral(update, context)
        elif text == "📊 الإحصائيات":
            await Handlers.stats(update, context)
        elif text == "ℹ️ المساعدة":
            await Handlers.help_command(update, context)
        
        # Handle admin menu
        elif Utils.is_admin(user_id):
            await Handlers.handle_admin_text(update, context)
        
        # Handle waiting states
        elif context.user_data.get('waiting_for_quantity'):
            try:
                quantity = int(text)
                if quantity <= 0 or quantity > 100000:
                    await update.message.reply_text("❌ الكمية يجب أن تكون بين 1 و 100,000")
                    return
                
                context.user_data['quantity'] = quantity
                context.user_data['waiting_for_quantity'] = False
                context.user_data['waiting_for_url'] = True
                
                service_type = context.user_data.get('service_type')
                await update.message.reply_text(
                    f"🎯 أرسل الرابط المراد رشقه:\n\n"
                    f"🚀 الخدمة: {Utils.format_service_name(service_type)}\n"
                    f"📊 الكمية: {Utils.format_number(quantity)}"
                )
            except ValueError:
                await update.message.reply_text("❌ يرجى إرسال رقم صحيح")
        
        elif context.user_data.get('waiting_for_url'):
            await Handlers.handle_url_input(update, context)
        
        # Handle admin waiting states
        elif Utils.is_admin(user_id):
            await Handlers.handle_admin_input(update, context)
    
    @staticmethod
    async def handle_url_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle URL input"""
        url = update.message.text.strip()
        service_type = context.user_data.get('service_type')
        quantity = context.user_data.get('quantity')
        
        if not service_type or not quantity:
            await update.message.reply_text("❌ بيانات الطلب غير مكتملة")
            return
        
        # Validate URL
        errors = Utils.validate_order_data(service_type, url, quantity)
        if errors:
            await update.message.reply_text(f"❌ خطأ في البيانات:\n" + "\n".join(errors))
            return
        
        context.user_data['target_url'] = url
        context.user_data['waiting_for_url'] = False
        
        # Calculate cost
        cost = Utils.calculate_cost(service_type, quantity)
        
        # Create order summary
        summary = Utils.create_order_summary(service_type, url, quantity, cost)
        
        await update.message.reply_text(
            summary,
            reply_markup=Keyboards.confirm_order_keyboard(0)
        )
    
    @staticmethod
    async def handle_admin_callback(query, context):
        """Handle admin callbacks"""
        from admin_handlers import AdminHandlers
        await AdminHandlers.handle_admin_callback(query, context)
    
    @staticmethod
    async def handle_admin_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle admin text messages"""
        from admin_handlers import AdminHandlers
        await AdminHandlers.handle_admin_text(update, context)
    
    @staticmethod
    async def handle_admin_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle admin input"""
        from admin_handlers import AdminHandlers
        await AdminHandlers.handle_admin_input(update, context)