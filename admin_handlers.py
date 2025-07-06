import logging
from telegram import Update, ChatMember
from telegram.ext import ContextTypes
from database import Database
from config import Config
from keyboards import Keyboards
from utils import Utils

# Initialize database
db = Database()

class AdminHandlers:
    @staticmethod
    async def admin_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show admin menu"""
        user_id = update.effective_user.id
        
        if not Utils.is_admin(user_id):
            await update.message.reply_text("❌ غير مصرح لك بالوصول")
            return
        
        stats = db.get_stats()
        
        text = f"""
👑 لوحة تحكم الأدمن

📊 الإحصائيات:
👥 إجمالي المستخدمين: {Utils.format_number(stats['total_users'])}
📋 إجمالي الطلبات: {Utils.format_number(stats['total_orders'])}
⏳ الطلبات المعلقة: {Utils.format_number(stats['pending_orders'])}
📢 القنوات النشطة: {Utils.format_number(stats['total_channels'])}
        """
        
        await update.message.reply_text(
            text,
            reply_markup=Keyboards.admin_menu()
        )
    
    @staticmethod
    async def handle_admin_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle admin text messages"""
        text = update.message.text
        user_id = update.effective_user.id
        
        if not Utils.is_admin(user_id):
            return
        
        if text == "📊 إحصائيات البوت":
            await AdminHandlers.bot_stats(update, context)
        elif text == "👥 المستخدمين":
            await AdminHandlers.users_list(update, context)
        elif text == "📢 إدارة القنوات":
            await AdminHandlers.channels_management(update, context)
        elif text == "📦 إدارة الطلبات":
            await AdminHandlers.orders_management(update, context)
        elif text == "✉️ رسالة جماعية":
            await AdminHandlers.broadcast_message(update, context)
        elif text == "💎 إرسال نقاط":
            await AdminHandlers.send_points(update, context)
        elif text == "🔙 القائمة الرئيسية":
            await update.message.reply_text(
                "🏠 القائمة الرئيسية",
                reply_markup=Keyboards.main_menu()
            )
    
    @staticmethod
    async def handle_admin_callback(query, context):
        """Handle admin callbacks"""
        data = query.data
        user_id = query.from_user.id
        
        if not Utils.is_admin(user_id):
            await query.answer("❌ غير مصرح لك بالوصول")
            return
        
        if data == "add_channel":
            await query.edit_message_text(
                "📢 إضافة قناة جديدة\n\n"
                "أرسل معلومات القناة بالتنسيق التالي:\n"
                "معرف_القناة|اسم_القناة|نقاط_المكافأة\n\n"
                "مثال:\n"
                "@mychannel|قناتي الرسمية|15"
            )
            context.user_data['admin_waiting_for'] = 'channel_info'
        
        elif data == "remove_channel":
            channels = db.get_all_channels()
            if not channels:
                await query.edit_message_text("❌ لا توجد قنوات لحذفها")
                return
            
            text = "❌ اختر القناة المراد حذفها:\n\n"
            for i, channel in enumerate(channels):
                text += f"{i+1}. {channel[2]} (@{channel[3]})\n"
            
            text += "\nأرسل رقم القناة:"
            await query.edit_message_text(text)
            context.user_data['admin_waiting_for'] = 'remove_channel'
            context.user_data['channels_list'] = channels
        
        elif data == "list_channels":
            await AdminHandlers.list_channels(query, context)
        
        elif data == "all_orders":
            await AdminHandlers.all_orders(query, context)
        
        elif data == "pending_orders":
            await AdminHandlers.pending_orders(query, context)
        
        elif data == "complete_order":
            await query.edit_message_text(
                "✅ إكمال طلب\n\n"
                "أرسل رقم الطلب المراد إكماله:"
            )
            context.user_data['admin_waiting_for'] = 'complete_order'
        
        elif data == "cancel_order_admin":
            await query.edit_message_text(
                "❌ إلغاء طلب\n\n"
                "أرسل رقم الطلب المراد إلغاؤه:"
            )
            context.user_data['admin_waiting_for'] = 'cancel_order'
        
        elif data.startswith("admin_complete_"):
            order_id = int(data.replace("admin_complete_", ""))
            await AdminHandlers.complete_order(query, context, order_id)
        
        elif data.startswith("admin_cancel_"):
            order_id = int(data.replace("admin_cancel_", ""))
            await AdminHandlers.cancel_order(query, context, order_id)
        
        elif data == "back_to_admin":
            await AdminHandlers.admin_menu_callback(query, context)
    
    @staticmethod
    async def handle_admin_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle admin input"""
        text = update.message.text
        user_id = update.effective_user.id
        
        if not Utils.is_admin(user_id):
            return
        
        waiting_for = context.user_data.get('admin_waiting_for')
        
        if waiting_for == 'channel_info':
            await AdminHandlers.process_channel_info(update, context)
        elif waiting_for == 'remove_channel':
            await AdminHandlers.process_remove_channel(update, context)
        elif waiting_for == 'complete_order':
            await AdminHandlers.process_complete_order(update, context)
        elif waiting_for == 'cancel_order':
            await AdminHandlers.process_cancel_order(update, context)
        elif waiting_for == 'broadcast_message':
            await AdminHandlers.process_broadcast(update, context)
        elif waiting_for == 'send_points_user':
            await AdminHandlers.process_send_points_user(update, context)
        elif waiting_for == 'send_points_amount':
            await AdminHandlers.process_send_points_amount(update, context)
    
    @staticmethod
    async def bot_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show bot statistics"""
        stats = db.get_stats()
        
        text = f"""
📊 إحصائيات البوت المفصلة:

👥 المستخدمين: {Utils.format_number(stats['total_users'])}
📋 إجمالي الطلبات: {Utils.format_number(stats['total_orders'])}
⏳ الطلبات المعلقة: {Utils.format_number(stats['pending_orders'])}
✅ الطلبات المكتملة: {Utils.format_number(stats['total_orders'] - stats['pending_orders'])}
📢 القنوات النشطة: {Utils.format_number(stats['total_channels'])}
        """
        
        await update.message.reply_text(text)
    
    @staticmethod
    async def users_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show users list"""
        # Get recent users (last 20)
        with Database().db_name as db_name:
            import sqlite3
            conn = sqlite3.connect(db_name)
            cursor = conn.cursor()
            cursor.execute('''
                SELECT user_id, username, first_name, points, referrals, joined_date 
                FROM users 
                ORDER BY joined_date DESC 
                LIMIT 20
            ''')
            users = cursor.fetchall()
            conn.close()
        
        if not users:
            await update.message.reply_text("❌ لا توجد مستخدمين")
            return
        
        text = "👥 آخر المستخدمين:\n\n"
        
        for user in users:
            user_id, username, first_name, points, referrals, joined_date = user
            text += f"""
👤 {first_name} (@{username or 'N/A'})
🆔 {user_id}
💎 النقاط: {Utils.format_number(points)}
👥 الإحالات: {referrals}
📅 {Utils.format_date(joined_date)}
────────────────
            """
        
        await update.message.reply_text(text)
    
    @staticmethod
    async def channels_management(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show channels management"""
        await update.message.reply_text(
            "📢 إدارة القنوات",
            reply_markup=Keyboards.admin_channels_keyboard()
        )
    
    @staticmethod
    async def orders_management(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show orders management"""
        await update.message.reply_text(
            "📦 إدارة الطلبات",
            reply_markup=Keyboards.admin_orders_keyboard()
        )
    
    @staticmethod
    async def broadcast_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Broadcast message to all users"""
        await update.message.reply_text(
            "✉️ إرسال رسالة جماعية\n\n"
            "أرسل الرسالة التي تريد إرسالها لجميع المستخدمين:"
        )
        context.user_data['admin_waiting_for'] = 'broadcast_message'
    
    @staticmethod
    async def send_points(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Send points to user"""
        await update.message.reply_text(
            "💎 إرسال نقاط\n\n"
            "أرسل معرف المستخدم:"
        )
        context.user_data['admin_waiting_for'] = 'send_points_user'
    
    @staticmethod
    async def process_channel_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Process channel information"""
        text = update.message.text
        
        try:
            parts = text.split('|')
            if len(parts) != 3:
                await update.message.reply_text("❌ تنسيق خاطئ. استخدم: معرف_القناة|اسم_القناة|نقاط_المكافأة")
                return
            
            channel_id = parts[0].strip()
            channel_name = parts[1].strip()
            points_reward = int(parts[2].strip())
            
            # Remove @ if present
            channel_username = channel_id.replace('@', '') if channel_id.startswith('@') else None
            
            if db.add_channel(channel_id, channel_name, channel_username, points_reward):
                await update.message.reply_text(
                    f"✅ تم إضافة القناة بنجاح!\n\n"
                    f"📢 القناة: {channel_name}\n"
                    f"🆔 المعرف: {channel_id}\n"
                    f"💎 المكافأة: {points_reward} نقطة"
                )
                db.log_admin_action(update.effective_user.id, "add_channel", f"{channel_name} - {channel_id}")
            else:
                await update.message.reply_text("❌ القناة موجودة مسبقاً")
        
        except ValueError:
            await update.message.reply_text("❌ نقاط المكافأة يجب أن تكون رقماً")
        except Exception as e:
            await update.message.reply_text(f"❌ حدث خطأ: {str(e)}")
        
        context.user_data.pop('admin_waiting_for', None)
    
    @staticmethod
    async def process_remove_channel(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Process channel removal"""
        text = update.message.text
        
        try:
            channel_index = int(text) - 1
            channels = context.user_data.get('channels_list', [])
            
            if 0 <= channel_index < len(channels):
                channel = channels[channel_index]
                channel_id = channel[1]
                channel_name = channel[2]
                
                if db.remove_channel(channel_id):
                    await update.message.reply_text(f"✅ تم حذف القناة: {channel_name}")
                    db.log_admin_action(update.effective_user.id, "remove_channel", f"{channel_name} - {channel_id}")
                else:
                    await update.message.reply_text("❌ فشل في حذف القناة")
            else:
                await update.message.reply_text("❌ رقم القناة غير صحيح")
        
        except ValueError:
            await update.message.reply_text("❌ يرجى إرسال رقم صحيح")
        
        context.user_data.pop('admin_waiting_for', None)
        context.user_data.pop('channels_list', None)
    
    @staticmethod
    async def process_complete_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Process order completion"""
        text = update.message.text
        
        try:
            order_id = int(text)
            db.update_order_status(order_id, 'completed')
            
            await update.message.reply_text(f"✅ تم إكمال الطلب #{order_id}")
            db.log_admin_action(update.effective_user.id, "complete_order", f"Order #{order_id}")
            
            # Notify user
            # Get order details to notify user
            orders = db.get_all_orders()
            order = next((o for o in orders if o[0] == order_id), None)
            if order:
                user_id = order[1]
                await context.bot.send_message(
                    user_id,
                    f"✅ تم إكمال طلبك #{order_id} بنجاح!\n"
                    f"شكراً لاستخدام البوت 🎉"
                )
        
        except ValueError:
            await update.message.reply_text("❌ يرجى إرسال رقم الطلب")
        except Exception as e:
            await update.message.reply_text(f"❌ حدث خطأ: {str(e)}")
        
        context.user_data.pop('admin_waiting_for', None)
    
    @staticmethod
    async def process_cancel_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Process order cancellation"""
        text = update.message.text
        
        try:
            order_id = int(text)
            
            # Get order details first
            orders = db.get_all_orders()
            order = next((o for o in orders if o[0] == order_id), None)
            
            if not order:
                await update.message.reply_text("❌ الطلب غير موجود")
                return
            
            user_id = order[1]
            points_cost = order[5]
            
            # Refund points
            db.update_user_points(user_id, points_cost)
            db.update_order_status(order_id, 'cancelled')
            
            await update.message.reply_text(f"✅ تم إلغاء الطلب #{order_id} واسترداد النقاط")
            db.log_admin_action(update.effective_user.id, "cancel_order", f"Order #{order_id}")
            
            # Notify user
            await context.bot.send_message(
                user_id,
                f"❌ تم إلغاء طلبك #{order_id}\n"
                f"💎 تم استرداد {Utils.format_number(points_cost)} نقطة"
            )
        
        except ValueError:
            await update.message.reply_text("❌ يرجى إرسال رقم الطلب")
        except Exception as e:
            await update.message.reply_text(f"❌ حدث خطأ: {str(e)}")
        
        context.user_data.pop('admin_waiting_for', None)
    
    @staticmethod
    async def process_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Process broadcast message"""
        message = update.message.text
        
        # Get all users
        with Database().db_name as db_name:
            import sqlite3
            conn = sqlite3.connect(db_name)
            cursor = conn.cursor()
            cursor.execute('SELECT user_id FROM users WHERE is_banned = 0')
            users = cursor.fetchall()
            conn.close()
        
        sent_count = 0
        failed_count = 0
        
        await update.message.reply_text(f"📤 بدء إرسال الرسالة لـ {len(users)} مستخدم...")
        
        for user in users:
            user_id = user[0]
            try:
                await context.bot.send_message(user_id, message)
                sent_count += 1
            except Exception:
                failed_count += 1
        
        await update.message.reply_text(
            f"📊 تم إرسال الرسالة:\n"
            f"✅ نجح: {sent_count}\n"
            f"❌ فشل: {failed_count}"
        )
        
        db.log_admin_action(
            update.effective_user.id, 
            "broadcast", 
            f"Sent to {sent_count} users, failed {failed_count}"
        )
        
        context.user_data.pop('admin_waiting_for', None)
    
    @staticmethod
    async def process_send_points_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Process send points user selection"""
        text = update.message.text
        
        try:
            user_id = int(text)
            user_data = db.get_user(user_id)
            
            if not user_data:
                await update.message.reply_text("❌ المستخدم غير موجود")
                return
            
            context.user_data['target_user_id'] = user_id
            context.user_data['admin_waiting_for'] = 'send_points_amount'
            
            await update.message.reply_text(
                f"👤 المستخدم: {user_data[2]} (@{user_data[1] or 'N/A'})\n"
                f"💎 النقاط الحالية: {Utils.format_number(user_data[3])}\n\n"
                f"أرسل كمية النقاط المراد إرسالها:"
            )
        
        except ValueError:
            await update.message.reply_text("❌ يرجى إرسال معرف المستخدم (رقم)")
    
    @staticmethod
    async def process_send_points_amount(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Process send points amount"""
        text = update.message.text
        
        try:
            points = int(text)
            user_id = context.user_data.get('target_user_id')
            
            if not user_id:
                await update.message.reply_text("❌ خطأ في بيانات المستخدم")
                return
            
            db.update_user_points(user_id, points)
            
            await update.message.reply_text(
                f"✅ تم إرسال {Utils.format_number(points)} نقطة بنجاح!"
            )
            
            # Notify user
            await context.bot.send_message(
                user_id,
                f"🎉 تم منحك {Utils.format_number(points)} نقطة من الإدارة!\n"
                f"💎 رصيدك الحالي: {Utils.format_number(db.get_user(user_id)[3])} نقطة"
            )
            
            db.log_admin_action(
                update.effective_user.id,
                "send_points",
                f"Sent {points} points to user {user_id}"
            )
        
        except ValueError:
            await update.message.reply_text("❌ يرجى إرسال رقم صحيح")
        
        context.user_data.pop('admin_waiting_for', None)
        context.user_data.pop('target_user_id', None)
    
    @staticmethod
    async def list_channels(query, context):
        """List all channels"""
        channels = db.get_all_channels()
        
        if not channels:
            await query.edit_message_text("❌ لا توجد قنوات")
            return
        
        text = "📢 قائمة القنوات:\n\n"
        
        for channel in channels:
            channel_id, channel_name, channel_username, points_reward = channel[1], channel[2], channel[3], channel[4]
            text += f"""
📢 {channel_name}
🆔 {channel_id}
💎 المكافأة: {points_reward} نقطة
📅 {Utils.format_date(channel[6])}
────────────────
            """
        
        await query.edit_message_text(text)
    
    @staticmethod
    async def all_orders(query, context):
        """Show all orders"""
        orders = db.get_all_orders()
        
        if not orders:
            await query.edit_message_text("❌ لا توجد طلبات")
            return
        
        text = "📋 جميع الطلبات (آخر 20):\n\n"
        
        for order in orders[-20:]:
            order_id, user_id, service_type, target_url, quantity, points_cost, status, created_date, completed_date, username = order
            text += f"""
🔸 طلب #{order_id}
👤 @{username or 'N/A'}
🚀 {Utils.format_service_name(service_type)}
📊 {Utils.format_number(quantity)}
💎 {Utils.format_number(points_cost)} نقطة
📈 {Utils.format_order_status(status)}
📅 {Utils.format_date(created_date)}
────────────────
            """
        
        await query.edit_message_text(text)
    
    @staticmethod
    async def pending_orders(query, context):
        """Show pending orders"""
        orders = db.get_all_orders()
        pending_orders = [o for o in orders if o[6] == 'pending']
        
        if not pending_orders:
            await query.edit_message_text("✅ لا توجد طلبات معلقة")
            return
        
        text = "⏳ الطلبات المعلقة:\n\n"
        
        for order in pending_orders:
            order_id, user_id, service_type, target_url, quantity, points_cost, status, created_date, completed_date, username = order
            text += f"""
🔸 طلب #{order_id}
👤 @{username or 'N/A'}
🚀 {Utils.format_service_name(service_type)}
🎯 {target_url}
📊 {Utils.format_number(quantity)}
💎 {Utils.format_number(points_cost)} نقطة
📅 {Utils.format_date(created_date)}
────────────────
            """
        
        await query.edit_message_text(
            text,
            reply_markup=None
        )
    
    @staticmethod
    async def complete_order(query, context, order_id):
        """Complete specific order"""
        db.update_order_status(order_id, 'completed')
        
        await query.edit_message_text(f"✅ تم إكمال الطلب #{order_id}")
        db.log_admin_action(query.from_user.id, "complete_order", f"Order #{order_id}")
        
        # Get order details to notify user
        orders = db.get_all_orders()
        order = next((o for o in orders if o[0] == order_id), None)
        if order:
            user_id = order[1]
            await context.bot.send_message(
                user_id,
                f"✅ تم إكمال طلبك #{order_id} بنجاح!\n"
                f"شكراً لاستخدام البوت 🎉"
            )
    
    @staticmethod
    async def cancel_order(query, context, order_id):
        """Cancel specific order"""
        # Get order details first
        orders = db.get_all_orders()
        order = next((o for o in orders if o[0] == order_id), None)
        
        if not order:
            await query.edit_message_text("❌ الطلب غير موجود")
            return
        
        user_id = order[1]
        points_cost = order[5]
        
        # Refund points
        db.update_user_points(user_id, points_cost)
        db.update_order_status(order_id, 'cancelled')
        
        await query.edit_message_text(f"✅ تم إلغاء الطلب #{order_id} واسترداد النقاط")
        db.log_admin_action(query.from_user.id, "cancel_order", f"Order #{order_id}")
        
        # Notify user
        await context.bot.send_message(
            user_id,
            f"❌ تم إلغاء طلبك #{order_id}\n"
            f"💎 تم استرداد {Utils.format_number(points_cost)} نقطة"
        )
    
    @staticmethod
    async def admin_menu_callback(query, context):
        """Show admin menu callback"""
        stats = db.get_stats()
        
        text = f"""
👑 لوحة تحكم الأدمن

📊 الإحصائيات:
👥 إجمالي المستخدمين: {Utils.format_number(stats['total_users'])}
📋 إجمالي الطلبات: {Utils.format_number(stats['total_orders'])}
⏳ الطلبات المعلقة: {Utils.format_number(stats['pending_orders'])}
📢 القنوات النشطة: {Utils.format_number(stats['total_channels'])}
        """
        
        await query.edit_message_text(text)import logging
from telegram import Update, ChatMember
from telegram.ext import ContextTypes
from database import Database
from config import Config
from keyboards import Keyboards
from utils import Utils

# Initialize database
db = Database()

class AdminHandlers:
    @staticmethod
    async def admin_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show admin menu"""
        user_id = update.effective_user.id
        
        if not Utils.is_admin(user_id):
            await update.message.reply_text("❌ غير مصرح لك بالوصول")
            return
        
        stats = db.get_stats()
        
        text = f"""
👑 لوحة تحكم الأدمن

📊 الإحصائيات:
👥 إجمالي المستخدمين: {Utils.format_number(stats['total_users'])}
📋 إجمالي الطلبات: {Utils.format_number(stats['total_orders'])}
⏳ الطلبات المعلقة: {Utils.format_number(stats['pending_orders'])}
📢 القنوات النشطة: {Utils.format_number(stats['total_channels'])}
        """
        
        await update.message.reply_text(
            text,
            reply_markup=Keyboards.admin_menu()
        )
    
    @staticmethod
    async def handle_admin_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle admin text messages"""
        text = update.message.text
        user_id = update.effective_user.id
        
        if not Utils.is_admin(user_id):
            return
        
        if text == "📊 إحصائيات البوت":
            await AdminHandlers.bot_stats(update, context)
        elif text == "👥 المستخدمين":
            await AdminHandlers.users_list(update, context)
        elif text == "📢 إدارة القنوات":
            await AdminHandlers.channels_management(update, context)
        elif text == "📦 إدارة الطلبات":
            await AdminHandlers.orders_management(update, context)
        elif text == "✉️ رسالة جماعية":
            await AdminHandlers.broadcast_message(update, context)
        elif text == "💎 إرسال نقاط":
            await AdminHandlers.send_points(update, context)
        elif text == "🔙 القائمة الرئيسية":
            await update.message.reply_text(
                "🏠 القائمة الرئيسية",
                reply_markup=Keyboards.main_menu()
            )
    
    @staticmethod
    async def handle_admin_callback(query, context):
        """Handle admin callbacks"""
        data = query.data
        user_id = query.from_user.id
        
        if not Utils.is_admin(user_id):
            await query.answer("❌ غير مصرح لك بالوصول")
            return
        
        if data == "add_channel":
            await query.edit_message_text(
                "📢 إضافة قناة جديدة\n\n"
                "أرسل معلومات القناة بالتنسيق التالي:\n"
                "معرف_القناة|اسم_القناة|نقاط_المكافأة\n\n"
                "مثال:\n"
                "@mychannel|قناتي الرسمية|15"
            )
            context.user_data['admin_waiting_for'] = 'channel_info'
        
        elif data == "remove_channel":
            channels = db.get_all_channels()
            if not channels:
                await query.edit_message_text("❌ لا توجد قنوات لحذفها")
                return
            
            text = "❌ اختر القناة المراد حذفها:\n\n"
            for i, channel in enumerate(channels):
                text += f"{i+1}. {channel[2]} (@{channel[3]})\n"
            
            text += "\nأرسل رقم القناة:"
            await query.edit_message_text(text)
            context.user_data['admin_waiting_for'] = 'remove_channel'
            context.user_data['channels_list'] = channels
        
        elif data == "list_channels":
            await AdminHandlers.list_channels(query, context)
        
        elif data == "all_orders":
            await AdminHandlers.all_orders(query, context)
        
        elif data == "pending_orders":
            await AdminHandlers.pending_orders(query, context)
        
        elif data == "complete_order":
            await query.edit_message_text(
                "✅ إكمال طلب\n\n"
                "أرسل رقم الطلب المراد إكماله:"
            )
            context.user_data['admin_waiting_for'] = 'complete_order'
        
        elif data == "cancel_order_admin":
            await query.edit_message_text(
                "❌ إلغاء طلب\n\n"
                "أرسل رقم الطلب المراد إلغاؤه:"
            )
            context.user_data['admin_waiting_for'] = 'cancel_order'
        
        elif data.startswith("admin_complete_"):
            order_id = int(data.replace("admin_complete_", ""))
            await AdminHandlers.complete_order(query, context, order_id)
        
        elif data.startswith("admin_cancel_"):
            order_id = int(data.replace("admin_cancel_", ""))
            await AdminHandlers.cancel_order(query, context, order_id)
        
        elif data == "back_to_admin":
            await AdminHandlers.admin_menu_callback(query, context)
    
    @staticmethod
    async def handle_admin_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle admin input"""
        text = update.message.text
        user_id = update.effective_user.id
        
        if not Utils.is_admin(user_id):
            return
        
        waiting_for = context.user_data.get('admin_waiting_for')
        
        if waiting_for == 'channel_info':
            await AdminHandlers.process_channel_info(update, context)
        elif waiting_for == 'remove_channel':
            await AdminHandlers.process_remove_channel(update, context)
        elif waiting_for == 'complete_order':
            await AdminHandlers.process_complete_order(update, context)
        elif waiting_for == 'cancel_order':
            await AdminHandlers.process_cancel_order(update, context)
        elif waiting_for == 'broadcast_message':
            await AdminHandlers.process_broadcast(update, context)
        elif waiting_for == 'send_points_user':
            await AdminHandlers.process_send_points_user(update, context)
        elif waiting_for == 'send_points_amount':
            await AdminHandlers.process_send_points_amount(update, context)
    
    @staticmethod
    async def bot_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show bot statistics"""
        stats = db.get_stats()
        
        text = f"""
📊 إحصائيات البوت المفصلة:

👥 المستخدمين: {Utils.format_number(stats['total_users'])}
📋 إجمالي الطلبات: {Utils.format_number(stats['total_orders'])}
⏳ الطلبات المعلقة: {Utils.format_number(stats['pending_orders'])}
✅ الطلبات المكتملة: {Utils.format_number(stats['total_orders'] - stats['pending_orders'])}
📢 القنوات النشطة: {Utils.format_number(stats['total_channels'])}
        """
        
        await update.message.reply_text(text)
    
    @staticmethod
    async def users_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show users list"""
        # Get recent users (last 20)
        with Database().db_name as db_name:
            import sqlite3
            conn = sqlite3.connect(db_name)
            cursor = conn.cursor()
            cursor.execute('''
                SELECT user_id, username, first_name, points, referrals, joined_date 
                FROM users 
                ORDER BY joined_date DESC 
                LIMIT 20
            ''')
            users = cursor.fetchall()
            conn.close()
        
        if not users:
            await update.message.reply_text("❌ لا توجد مستخدمين")
            return
        
        text = "👥 آخر المستخدمين:\n\n"
        
        for user in users:
            user_id, username, first_name, points, referrals, joined_date = user
            text += f"""
👤 {first_name} (@{username or 'N/A'})
🆔 {user_id}
💎 النقاط: {Utils.format_number(points)}
👥 الإحالات: {referrals}
📅 {Utils.format_date(joined_date)}
────────────────
            """
        
        await update.message.reply_text(text)
    
    @staticmethod
    async def channels_management(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show channels management"""
        await update.message.reply_text(
            "📢 إدارة القنوات",
            reply_markup=Keyboards.admin_channels_keyboard()
        )
    
    @staticmethod
    async def orders_management(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show orders management"""
        await update.message.reply_text(
            "📦 إدارة الطلبات",
            reply_markup=Keyboards.admin_orders_keyboard()
        )
    
    @staticmethod
    async def broadcast_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Broadcast message to all users"""
        await update.message.reply_text(
            "✉️ إرسال رسالة جماعية\n\n"
            "أرسل الرسالة التي تريد إرسالها لجميع المستخدمين:"
        )
        context.user_data['admin_waiting_for'] = 'broadcast_message'
    
    @staticmethod
    async def send_points(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Send points to user"""
        await update.message.reply_text(
            "💎 إرسال نقاط\n\n"
            "أرسل معرف المستخدم:"
        )
        context.user_data['admin_waiting_for'] = 'send_points_user'
    
    @staticmethod
    async def process_channel_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Process channel information"""
        text = update.message.text
        
        try:
            parts = text.split('|')
            if len(parts) != 3:
                await update.message.reply_text("❌ تنسيق خاطئ. استخدم: معرف_القناة|اسم_القناة|نقاط_المكافأة")
                return
            
            channel_id = parts[0].strip()
            channel_name = parts[1].strip()
            points_reward = int(parts[2].strip())
            
            # Remove @ if present
            channel_username = channel_id.replace('@', '') if channel_id.startswith('@') else None
            
            if db.add_channel(channel_id, channel_name, channel_username, points_reward):
                await update.message.reply_text(
                    f"✅ تم إضافة القناة بنجاح!\n\n"
                    f"📢 القناة: {channel_name}\n"
                    f"🆔 المعرف: {channel_id}\n"
                    f"💎 المكافأة: {points_reward} نقطة"
                )
                db.log_admin_action(update.effective_user.id, "add_channel", f"{channel_name} - {channel_id}")
            else:
                await update.message.reply_text("❌ القناة موجودة مسبقاً")
        
        except ValueError:
            await update.message.reply_text("❌ نقاط المكافأة يجب أن تكون رقماً")
        except Exception as e:
            await update.message.reply_text(f"❌ حدث خطأ: {str(e)}")
        
        context.user_data.pop('admin_waiting_for', None)
    
    @staticmethod
    async def process_remove_channel(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Process channel removal"""
        text = update.message.text
        
        try:
            channel_index = int(text) - 1
            channels = context.user_data.get('channels_list', [])
            
            if 0 <= channel_index < len(channels):
                channel = channels[channel_index]
                channel_id = channel[1]
                channel_name = channel[2]
                
                if db.remove_channel(channel_id):
                    await update.message.reply_text(f"✅ تم حذف القناة: {channel_name}")
                    db.log_admin_action(update.effective_user.id, "remove_channel", f"{channel_name} - {channel_id}")
                else:
                    await update.message.reply_text("❌ فشل في حذف القناة")
            else:
                await update.message.reply_text("❌ رقم القناة غير صحيح")
        
        except ValueError:
            await update.message.reply_text("❌ يرجى إرسال رقم صحيح")
        
        context.user_data.pop('admin_waiting_for', None)
        context.user_data.pop('channels_list', None)
    
    @staticmethod
    async def process_complete_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Process order completion"""
        text = update.message.text
        
        try:
            order_id = int(text)
            db.update_order_status(order_id, 'completed')
            
            await update.message.reply_text(f"✅ تم إكمال الطلب #{order_id}")
            db.log_admin_action(update.effective_user.id, "complete_order", f"Order #{order_id}")
            
            # Notify user
            # Get order details to notify user
            orders = db.get_all_orders()
            order = next((o for o in orders if o[0] == order_id), None)
            if order:
                user_id = order[1]
                await context.bot.send_message(
                    user_id,
                    f"✅ تم إكمال طلبك #{order_id} بنجاح!\n"
                    f"شكراً لاستخدام البوت 🎉"
                )
        
        except ValueError:
            await update.message.reply_text("❌ يرجى إرسال رقم الطلب")
        except Exception as e:
            await update.message.reply_text(f"❌ حدث خطأ: {str(e)}")
        
        context.user_data.pop('admin_waiting_for', None)
    
    @staticmethod
    async def process_cancel_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Process order cancellation"""
        text = update.message.text
        
        try:
            order_id = int(text)
            
            # Get order details first
            orders = db.get_all_orders()
            order = next((o for o in orders if o[0] == order_id), None)
            
            if not order:
                await update.message.reply_text("❌ الطلب غير موجود")
                return
            
            user_id = order[1]
            points_cost = order[5]
            
            # Refund points
            db.update_user_points(user_id, points_cost)
            db.update_order_status(order_id, 'cancelled')
            
            await update.message.reply_text(f"✅ تم إلغاء الطلب #{order_id} واسترداد النقاط")
            db.log_admin_action(update.effective_user.id, "cancel_order", f"Order #{order_id}")
            
            # Notify user
            await context.bot.send_message(
                user_id,
                f"❌ تم إلغاء طلبك #{order_id}\n"
                f"💎 تم استرداد {Utils.format_number(points_cost)} نقطة"
            )
        
        except ValueError:
            await update.message.reply_text("❌ يرجى إرسال رقم الطلب")
        except Exception as e:
            await update.message.reply_text(f"❌ حدث خطأ: {str(e)}")
        
        context.user_data.pop('admin_waiting_for', None)
    
    @staticmethod
    async def process_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Process broadcast message"""
        message = update.message.text
        
        # Get all users
        with Database().db_name as db_name:
            import sqlite3
            conn = sqlite3.connect(db_name)
            cursor = conn.cursor()
            cursor.execute('SELECT user_id FROM users WHERE is_banned = 0')
            users = cursor.fetchall()
            conn.close()
        
        sent_count = 0
        failed_count = 0
        
        await update.message.reply_text(f"📤 بدء إرسال الرسالة لـ {len(users)} مستخدم...")
        
        for user in users:
            user_id = user[0]
            try:
                await context.bot.send_message(user_id, message)
                sent_count += 1
            except Exception:
                failed_count += 1
        
        await update.message.reply_text(
            f"📊 تم إرسال الرسالة:\n"
            f"✅ نجح: {sent_count}\n"
            f"❌ فشل: {failed_count}"
        )
        
        db.log_admin_action(
            update.effective_user.id, 
            "broadcast", 
            f"Sent to {sent_count} users, failed {failed_count}"
        )
        
        context.user_data.pop('admin_waiting_for', None)
    
    @staticmethod
    async def process_send_points_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Process send points user selection"""
        text = update.message.text
        
        try:
            user_id = int(text)
            user_data = db.get_user(user_id)
            
            if not user_data:
                await update.message.reply_text("❌ المستخدم غير موجود")
                return
            
            context.user_data['target_user_id'] = user_id
            context.user_data['admin_waiting_for'] = 'send_points_amount'
            
            await update.message.reply_text(
                f"👤 المستخدم: {user_data[2]} (@{user_data[1] or 'N/A'})\n"
                f"💎 النقاط الحالية: {Utils.format_number(user_data[3])}\n\n"
                f"أرسل كمية النقاط المراد إرسالها:"
            )
        
        except ValueError:
            await update.message.reply_text("❌ يرجى إرسال معرف المستخدم (رقم)")
    
    @staticmethod
    async def process_send_points_amount(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Process send points amount"""
        text = update.message.text
        
        try:
            points = int(text)
            user_id = context.user_data.get('target_user_id')
            
            if not user_id:
                await update.message.reply_text("❌ خطأ في بيانات المستخدم")
                return
            
            db.update_user_points(user_id, points)
            
            await update.message.reply_text(
                f"✅ تم إرسال {Utils.format_number(points)} نقطة بنجاح!"
            )
            
            # Notify user
            await context.bot.send_message(
                user_id,
                f"🎉 تم منحك {Utils.format_number(points)} نقطة من الإدارة!\n"
                f"💎 رصيدك الحالي: {Utils.format_number(db.get_user(user_id)[3])} نقطة"
            )
            
            db.log_admin_action(
                update.effective_user.id,
                "send_points",
                f"Sent {points} points to user {user_id}"
            )
        
        except ValueError:
            await update.message.reply_text("❌ يرجى إرسال رقم صحيح")
        
        context.user_data.pop('admin_waiting_for', None)
        context.user_data.pop('target_user_id', None)
    
    @staticmethod
    async def list_channels(query, context):
        """List all channels"""
        channels = db.get_all_channels()
        
        if not channels:
            await query.edit_message_text("❌ لا توجد قنوات")
            return
        
        text = "📢 قائمة القنوات:\n\n"
        
        for channel in channels:
            channel_id, channel_name, channel_username, points_reward = channel[1], channel[2], channel[3], channel[4]
            text += f"""
📢 {channel_name}
🆔 {channel_id}
💎 المكافأة: {points_reward} نقطة
📅 {Utils.format_date(channel[6])}
────────────────
            """
        
        await query.edit_message_text(text)
    
    @staticmethod
    async def all_orders(query, context):
        """Show all orders"""
        orders = db.get_all_orders()
        
        if not orders:
            await query.edit_message_text("❌ لا توجد طلبات")
            return
        
        text = "📋 جميع الطلبات (آخر 20):\n\n"
        
        for order in orders[-20:]:
            order_id, user_id, service_type, target_url, quantity, points_cost, status, created_date, completed_date, username = order
            text += f"""
🔸 طلب #{order_id}
👤 @{username or 'N/A'}
🚀 {Utils.format_service_name(service_type)}
📊 {Utils.format_number(quantity)}
💎 {Utils.format_number(points_cost)} نقطة
📈 {Utils.format_order_status(status)}
📅 {Utils.format_date(created_date)}
────────────────
            """
        
        await query.edit_message_text(text)
    
    @staticmethod
    async def pending_orders(query, context):
        """Show pending orders"""
        orders = db.get_all_orders()
        pending_orders = [o for o in orders if o[6] == 'pending']
        
        if not pending_orders:
            await query.edit_message_text("✅ لا توجد طلبات معلقة")
            return
        
        text = "⏳ الطلبات المعلقة:\n\n"
        
        for order in pending_orders:
            order_id, user_id, service_type, target_url, quantity, points_cost, status, created_date, completed_date, username = order
            text += f"""
🔸 طلب #{order_id}
👤 @{username or 'N/A'}
🚀 {Utils.format_service_name(service_type)}
🎯 {target_url}
📊 {Utils.format_number(quantity)}
💎 {Utils.format_number(points_cost)} نقطة
📅 {Utils.format_date(created_date)}
────────────────
            """
        
        await query.edit_message_text(
            text,
            reply_markup=None
        )
    
    @staticmethod
    async def complete_order(query, context, order_id):
        """Complete specific order"""
        db.update_order_status(order_id, 'completed')
        
        await query.edit_message_text(f"✅ تم إكمال الطلب #{order_id}")
        db.log_admin_action(query.from_user.id, "complete_order", f"Order #{order_id}")
        
        # Get order details to notify user
        orders = db.get_all_orders()
        order = next((o for o in orders if o[0] == order_id), None)
        if order:
            user_id = order[1]
            await context.bot.send_message(
                user_id,
                f"✅ تم إكمال طلبك #{order_id} بنجاح!\n"
                f"شكراً لاستخدام البوت 🎉"
            )
    
    @staticmethod
    async def cancel_order(query, context, order_id):
        """Cancel specific order"""
        # Get order details first
        orders = db.get_all_orders()
        order = next((o for o in orders if o[0] == order_id), None)
        
        if not order:
            await query.edit_message_text("❌ الطلب غير موجود")
            return
        
        user_id = order[1]
        points_cost = order[5]
        
        # Refund points
        db.update_user_points(user_id, points_cost)
        db.update_order_status(order_id, 'cancelled')
        
        await query.edit_message_text(f"✅ تم إلغاء الطلب #{order_id} واسترداد النقاط")
        db.log_admin_action(query.from_user.id, "cancel_order", f"Order #{order_id}")
        
        # Notify user
        await context.bot.send_message(
            user_id,
            f"❌ تم إلغاء طلبك #{order_id}\n"
            f"💎 تم استرداد {Utils.format_number(points_cost)} نقطة"
        )
    
    @staticmethod
    async def admin_menu_callback(query, context):
        """Show admin menu callback"""
        stats = db.get_stats()
        
        text = f"""
👑 لوحة تحكم الأدمن

📊 الإحصائيات:
👥 إجمالي المستخدمين: {Utils.format_number(stats['total_users'])}
📋 إجمالي الطلبات: {Utils.format_number(stats['total_orders'])}
⏳ الطلبات المعلقة: {Utils.format_number(stats['pending_orders'])}
📢 القنوات النشطة: {Utils.format_number(stats['total_channels'])}
        """
        
        await query.edit_message_text(text)import logging
from telegram import Update, ChatMember
from telegram.ext import ContextTypes
from database import Database
from config import Config
from keyboards import Keyboards
from utils import Utils

# Initialize database
db = Database()

class AdminHandlers:
    @staticmethod
    async def admin_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show admin menu"""
        user_id = update.effective_user.id
        
        if not Utils.is_admin(user_id):
            await update.message.reply_text("❌ غير مصرح لك بالوصول")
            return
        
        stats = db.get_stats()
        
        text = f"""
👑 لوحة تحكم الأدمن

📊 الإحصائيات:
👥 إجمالي المستخدمين: {Utils.format_number(stats['total_users'])}
📋 إجمالي الطلبات: {Utils.format_number(stats['total_orders'])}
⏳ الطلبات المعلقة: {Utils.format_number(stats['pending_orders'])}
📢 القنوات النشطة: {Utils.format_number(stats['total_channels'])}
        """
        
        await update.message.reply_text(
            text,
            reply_markup=Keyboards.admin_menu()
        )
    
    @staticmethod
    async def handle_admin_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle admin text messages"""
        text = update.message.text
        user_id = update.effective_user.id
        
        if not Utils.is_admin(user_id):
            return
        
        if text == "📊 إحصائيات البوت":
            await AdminHandlers.bot_stats(update, context)
        elif text == "👥 المستخدمين":
            await AdminHandlers.users_list(update, context)
        elif text == "📢 إدارة القنوات":
            await AdminHandlers.channels_management(update, context)
        elif text == "📦 إدارة الطلبات":
            await AdminHandlers.orders_management(update, context)
        elif text == "✉️ رسالة جماعية":
            await AdminHandlers.broadcast_message(update, context)
        elif text == "💎 إرسال نقاط":
            await AdminHandlers.send_points(update, context)
        elif text == "🔙 القائمة الرئيسية":
            await update.message.reply_text(
                "🏠 القائمة الرئيسية",
                reply_markup=Keyboards.main_menu()
            )
    
    @staticmethod
    async def handle_admin_callback(query, context):
        """Handle admin callbacks"""
        data = query.data
        user_id = query.from_user.id
        
        if not Utils.is_admin(user_id):
            await query.answer("❌ غير مصرح لك بالوصول")
            return
        
        if data == "add_channel":
            await query.edit_message_text(
                "📢 إضافة قناة جديدة\n\n"
                "أرسل معلومات القناة بالتنسيق التالي:\n"
                "معرف_القناة|اسم_القناة|نقاط_المكافأة\n\n"
                "مثال:\n"
                "@mychannel|قناتي الرسمية|15"
            )
            context.user_data['admin_waiting_for'] = 'channel_info'
        
        elif data == "remove_channel":
            channels = db.get_all_channels()
            if not channels:
                await query.edit_message_text("❌ لا توجد قنوات لحذفها")
                return
            
            text = "❌ اختر القناة المراد حذفها:\n\n"
            for i, channel in enumerate(channels):
                text += f"{i+1}. {channel[2]} (@{channel[3]})\n"
            
            text += "\nأرسل رقم القناة:"
            await query.edit_message_text(text)
            context.user_data['admin_waiting_for'] = 'remove_channel'
            context.user_data['channels_list'] = channels
        
        elif data == "list_channels":
            await AdminHandlers.list_channels(query, context)
        
        elif data == "all_orders":
            await AdminHandlers.all_orders(query, context)
        
        elif data == "pending_orders":
            await AdminHandlers.pending_orders(query, context)
        
        elif data == "complete_order":
            await query.edit_message_text(
                "✅ إكمال طلب\n\n"
                "أرسل رقم الطلب المراد إكماله:"
            )
            context.user_data['admin_waiting_for'] = 'complete_order'
        
        elif data == "cancel_order_admin":
            await query.edit_message_text(
                "❌ إلغاء طلب\n\n"
                "أرسل رقم الطلب المراد إلغاؤه:"
            )
            context.user_data['admin_waiting_for'] = 'cancel_order'
        
        elif data.startswith("admin_complete_"):
            order_id = int(data.replace("admin_complete_", ""))
            await AdminHandlers.complete_order(query, context, order_id)
        
        elif data.startswith("admin_cancel_"):
            order_id = int(data.replace("admin_cancel_", ""))
            await AdminHandlers.cancel_order(query, context, order_id)
        
        elif data == "back_to_admin":
            await AdminHandlers.admin_menu_callback(query, context)
    
    @staticmethod
    async def handle_admin_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle admin input"""
        text = update.message.text
        user_id = update.effective_user.id
        
        if not Utils.is_admin(user_id):
            return
        
        waiting_for = context.user_data.get('admin_waiting_for')
        
        if waiting_for == 'channel_info':
            await AdminHandlers.process_channel_info(update, context)
        elif waiting_for == 'remove_channel':
            await AdminHandlers.process_remove_channel(update, context)
        elif waiting_for == 'complete_order':
            await AdminHandlers.process_complete_order(update, context)
        elif waiting_for == 'cancel_order':
            await AdminHandlers.process_cancel_order(update, context)
        elif waiting_for == 'broadcast_message':
            await AdminHandlers.process_broadcast(update, context)
        elif waiting_for == 'send_points_user':
            await AdminHandlers.process_send_points_user(update, context)
        elif waiting_for == 'send_points_amount':
            await AdminHandlers.process_send_points_amount(update, context)
    
    @staticmethod
    async def bot_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show bot statistics"""
        stats = db.get_stats()
        
        text = f"""
📊 إحصائيات البوت المفصلة:

👥 المستخدمين: {Utils.format_number(stats['total_users'])}
📋 إجمالي الطلبات: {Utils.format_number(stats['total_orders'])}
⏳ الطلبات المعلقة: {Utils.format_number(stats['pending_orders'])}
✅ الطلبات المكتملة: {Utils.format_number(stats['total_orders'] - stats['pending_orders'])}
📢 القنوات النشطة: {Utils.format_number(stats['total_channels'])}
        """
        
        await update.message.reply_text(text)
    
    @staticmethod
    async def users_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show users list"""
        # Get recent users (last 20)
        with Database().db_name as db_name:
            import sqlite3
            conn = sqlite3.connect(db_name)
            cursor = conn.cursor()
            cursor.execute('''
                SELECT user_id, username, first_name, points, referrals, joined_date 
                FROM users 
                ORDER BY joined_date DESC 
                LIMIT 20
            ''')
            users = cursor.fetchall()
            conn.close()
        
        if not users:
            await update.message.reply_text("❌ لا توجد مستخدمين")
            return
        
        text = "👥 آخر المستخدمين:\n\n"
        
        for user in users:
            user_id, username, first_name, points, referrals, joined_date = user
            text += f"""
👤 {first_name} (@{username or 'N/A'})
🆔 {user_id}
💎 النقاط: {Utils.format_number(points)}
👥 الإحالات: {referrals}
📅 {Utils.format_date(joined_date)}
────────────────
            """
        
        await update.message.reply_text(text)
    
    @staticmethod
    async def channels_management(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show channels management"""
        await update.message.reply_text(
            "📢 إدارة القنوات",
            reply_markup=Keyboards.admin_channels_keyboard()
        )
    
    @staticmethod
    async def orders_management(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show orders management"""
        await update.message.reply_text(
            "📦 إدارة الطلبات",
            reply_markup=Keyboards.admin_orders_keyboard()
        )
    
    @staticmethod
    async def broadcast_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Broadcast message to all users"""
        await update.message.reply_text(
            "✉️ إرسال رسالة جماعية\n\n"
            "أرسل الرسالة التي تريد إرسالها لجميع المستخدمين:"
        )
        context.user_data['admin_waiting_for'] = 'broadcast_message'
    
    @staticmethod
    async def send_points(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Send points to user"""
        await update.message.reply_text(
            "💎 إرسال نقاط\n\n"
            "أرسل معرف المستخدم:"
        )
        context.user_data['admin_waiting_for'] = 'send_points_user'
    
    @staticmethod
    async def process_channel_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Process channel information"""
        text = update.message.text
        
        try:
            parts = text.split('|')
            if len(parts) != 3:
                await update.message.reply_text("❌ تنسيق خاطئ. استخدم: معرف_القناة|اسم_القناة|نقاط_المكافأة")
                return
            
            channel_id = parts[0].strip()
            channel_name = parts[1].strip()
            points_reward = int(parts[2].strip())
            
            # Remove @ if present
            channel_username = channel_id.replace('@', '') if channel_id.startswith('@') else None
            
            if db.add_channel(channel_id, channel_name, channel_username, points_reward):
                await update.message.reply_text(
                    f"✅ تم إضافة القناة بنجاح!\n\n"
                    f"📢 القناة: {channel_name}\n"
                    f"🆔 المعرف: {channel_id}\n"
                    f"💎 المكافأة: {points_reward} نقطة"
                )
                db.log_admin_action(update.effective_user.id, "add_channel", f"{channel_name} - {channel_id}")
            else:
                await update.message.reply_text("❌ القناة موجودة مسبقاً")
        
        except ValueError:
            await update.message.reply_text("❌ نقاط المكافأة يجب أن تكون رقماً")
        except Exception as e:
            await update.message.reply_text(f"❌ حدث خطأ: {str(e)}")
        
        context.user_data.pop('admin_waiting_for', None)
    
    @staticmethod
    async def process_remove_channel(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Process channel removal"""
        text = update.message.text
        
        try:
            channel_index = int(text) - 1
            channels = context.user_data.get('channels_list', [])
            
            if 0 <= channel_index < len(channels):
                channel = channels[channel_index]
                channel_id = channel[1]
                channel_name = channel[2]
                
                if db.remove_channel(channel_id):
                    await update.message.reply_text(f"✅ تم حذف القناة: {channel_name}")
                    db.log_admin_action(update.effective_user.id, "remove_channel", f"{channel_name} - {channel_id}")
                else:
                    await update.message.reply_text("❌ فشل في حذف القناة")
            else:
                await update.message.reply_text("❌ رقم القناة غير صحيح")
        
        except ValueError:
            await update.message.reply_text("❌ يرجى إرسال رقم صحيح")
        
        context.user_data.pop('admin_waiting_for', None)
        context.user_data.pop('channels_list', None)
    
    @staticmethod
    async def process_complete_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Process order completion"""
        text = update.message.text
        
        try:
            order_id = int(text)
            db.update_order_status(order_id, 'completed')
            
            await update.message.reply_text(f"✅ تم إكمال الطلب #{order_id}")
            db.log_admin_action(update.effective_user.id, "complete_order", f"Order #{order_id}")
            
            # Notify user
            # Get order details to notify user
            orders = db.get_all_orders()
            order = next((o for o in orders if o[0] == order_id), None)
            if order:
                user_id = order[1]
                await context.bot.send_message(
                    user_id,
                    f"✅ تم إكمال طلبك #{order_id} بنجاح!\n"
                    f"شكراً لاستخدام البوت 🎉"
                )
        
        except ValueError:
            await update.message.reply_text("❌ يرجى إرسال رقم الطلب")
        except Exception as e:
            await update.message.reply_text(f"❌ حدث خطأ: {str(e)}")
        
        context.user_data.pop('admin_waiting_for', None)
    
    @staticmethod
    async def process_cancel_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Process order cancellation"""
        text = update.message.text
        
        try:
            order_id = int(text)
            
            # Get order details first
            orders = db.get_all_orders()
            order = next((o for o in orders if o[0] == order_id), None)
            
            if not order:
                await update.message.reply_text("❌ الطلب غير موجود")
                return
            
            user_id = order[1]
            points_cost = order[5]
            
            # Refund points
            db.update_user_points(user_id, points_cost)
            db.update_order_status(order_id, 'cancelled')
            
            await update.message.reply_text(f"✅ تم إلغاء الطلب #{order_id} واسترداد النقاط")
            db.log_admin_action(update.effective_user.id, "cancel_order", f"Order #{order_id}")
            
            # Notify user
            await context.bot.send_message(
                user_id,
                f"❌ تم إلغاء طلبك #{order_id}\n"
                f"💎 تم استرداد {Utils.format_number(points_cost)} نقطة"
            )
        
        except ValueError:
            await update.message.reply_text("❌ يرجى إرسال رقم الطلب")
        except Exception as e:
            await update.message.reply_text(f"❌ حدث خطأ: {str(e)}")
        
        context.user_data.pop('admin_waiting_for', None)
    
    @staticmethod
    async def process_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Process broadcast message"""
        message = update.message.text
        
        # Get all users
        with Database().db_name as db_name:
            import sqlite3
            conn = sqlite3.connect(db_name)
            cursor = conn.cursor()
            cursor.execute('SELECT user_id FROM users WHERE is_banned = 0')
            users = cursor.fetchall()
            conn.close()
        
        sent_count = 0
        failed_count = 0
        
        await update.message.reply_text(f"📤 بدء إرسال الرسالة لـ {len(users)} مستخدم...")
        
        for user in users:
            user_id = user[0]
            try:
                await context.bot.send_message(user_id, message)
                sent_count += 1
            except Exception:
                failed_count += 1
        
        await update.message.reply_text(
            f"📊 تم إرسال الرسالة:\n"
            f"✅ نجح: {sent_count}\n"
            f"❌ فشل: {failed_count}"
        )
        
        db.log_admin_action(
            update.effective_user.id, 
            "broadcast", 
            f"Sent to {sent_count} users, failed {failed_count}"
        )
        
        context.user_data.pop('admin_waiting_for', None)
    
    @staticmethod
    async def process_send_points_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Process send points user selection"""
        text = update.message.text
        
        try:
            user_id = int(text)
            user_data = db.get_user(user_id)
            
            if not user_data:
                await update.message.reply_text("❌ المستخدم غير موجود")
                return
            
            context.user_data['target_user_id'] = user_id
            context.user_data['admin_waiting_for'] = 'send_points_amount'
            
            await update.message.reply_text(
                f"👤 المستخدم: {user_data[2]} (@{user_data[1] or 'N/A'})\n"
                f"💎 النقاط الحالية: {Utils.format_number(user_data[3])}\n\n"
                f"أرسل كمية النقاط المراد إرسالها:"
            )
        
        except ValueError:
            await update.message.reply_text("❌ يرجى إرسال معرف المستخدم (رقم)")
    
    @staticmethod
    async def process_send_points_amount(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Process send points amount"""
        text = update.message.text
        
        try:
            points = int(text)
            user_id = context.user_data.get('target_user_id')
            
            if not user_id:
                await update.message.reply_text("❌ خطأ في بيانات المستخدم")
                return
            
            db.update_user_points(user_id, points)
            
            await update.message.reply_text(
                f"✅ تم إرسال {Utils.format_number(points)} نقطة بنجاح!"
            )
            
            # Notify user
            await context.bot.send_message(
                user_id,
                f"🎉 تم منحك {Utils.format_number(points)} نقطة من الإدارة!\n"
                f"💎 رصيدك الحالي: {Utils.format_number(db.get_user(user_id)[3])} نقطة"
            )
            
            db.log_admin_action(
                update.effective_user.id,
                "send_points",
                f"Sent {points} points to user {user_id}"
            )
        
        except ValueError:
            await update.message.reply_text("❌ يرجى إرسال رقم صحيح")
        
        context.user_data.pop('admin_waiting_for', None)
        context.user_data.pop('target_user_id', None)
    
    @staticmethod
    async def list_channels(query, context):
        """List all channels"""
        channels = db.get_all_channels()
        
        if not channels:
            await query.edit_message_text("❌ لا توجد قنوات")
            return
        
        text = "📢 قائمة القنوات:\n\n"
        
        for channel in channels:
            channel_id, channel_name, channel_username, points_reward = channel[1], channel[2], channel[3], channel[4]
            text += f"""
📢 {channel_name}
🆔 {channel_id}
💎 المكافأة: {points_reward} نقطة
📅 {Utils.format_date(channel[6])}
────────────────
            """
        
        await query.edit_message_text(text)
    
    @staticmethod
    async def all_orders(query, context):
        """Show all orders"""
        orders = db.get_all_orders()
        
        if not orders:
            await query.edit_message_text("❌ لا توجد طلبات")
            return
        
        text = "📋 جميع الطلبات (آخر 20):\n\n"
        
        for order in orders[-20:]:
            order_id, user_id, service_type, target_url, quantity, points_cost, status, created_date, completed_date, username = order
            text += f"""
🔸 طلب #{order_id}
👤 @{username or 'N/A'}
🚀 {Utils.format_service_name(service_type)}
📊 {Utils.format_number(quantity)}
💎 {Utils.format_number(points_cost)} نقطة
📈 {Utils.format_order_status(status)}
📅 {Utils.format_date(created_date)}
────────────────
            """
        
        await query.edit_message_text(text)
    
    @staticmethod
    async def pending_orders(query, context):
        """Show pending orders"""
        orders = db.get_all_orders()
        pending_orders = [o for o in orders if o[6] == 'pending']
        
        if not pending_orders:
            await query.edit_message_text("✅ لا توجد طلبات معلقة")
            return
        
        text = "⏳ الطلبات المعلقة:\n\n"
        
        for order in pending_orders:
            order_id, user_id, service_type, target_url, quantity, points_cost, status, created_date, completed_date, username = order
            text += f"""
🔸 طلب #{order_id}
👤 @{username or 'N/A'}
🚀 {Utils.format_service_name(service_type)}
🎯 {target_url}
📊 {Utils.format_number(quantity)}
💎 {Utils.format_number(points_cost)} نقطة
📅 {Utils.format_date(created_date)}
────────────────
            """
        
        await query.edit_message_text(
            text,
            reply_markup=None
        )
    
    @staticmethod
    async def complete_order(query, context, order_id):
        """Complete specific order"""
        db.update_order_status(order_id, 'completed')
        
        await query.edit_message_text(f"✅ تم إكمال الطلب #{order_id}")
        db.log_admin_action(query.from_user.id, "complete_order", f"Order #{order_id}")
        
        # Get order details to notify user
        orders = db.get_all_orders()
        order = next((o for o in orders if o[0] == order_id), None)
        if order:
            user_id = order[1]
            await context.bot.send_message(
                user_id,
                f"✅ تم إكمال طلبك #{order_id} بنجاح!\n"
                f"شكراً لاستخدام البوت 🎉"
            )
    
    @staticmethod
    async def cancel_order(query, context, order_id):
        """Cancel specific order"""
        # Get order details first
        orders = db.get_all_orders()
        order = next((o for o in orders if o[0] == order_id), None)
        
        if not order:
            await query.edit_message_text("❌ الطلب غير موجود")
            return
        
        user_id = order[1]
        points_cost = order[5]
        
        # Refund points
        db.update_user_points(user_id, points_cost)
        db.update_order_status(order_id, 'cancelled')
        
        await query.edit_message_text(f"✅ تم إلغاء الطلب #{order_id} واسترداد النقاط")
        db.log_admin_action(query.from_user.id, "cancel_order", f"Order #{order_id}")
        
        # Notify user
        await context.bot.send_message(
            user_id,
            f"❌ تم إلغاء طلبك #{order_id}\n"
            f"💎 تم استرداد {Utils.format_number(points_cost)} نقطة"
        )
    
    @staticmethod
    async def admin_menu_callback(query, context):
        """Show admin menu callback"""
        stats = db.get_stats()
        
        text = f"""
👑 لوحة تحكم الأدمن

📊 الإحصائيات:
👥 إجمالي المستخدمين: {Utils.format_number(stats['total_users'])}
📋 إجمالي الطلبات: {Utils.format_number(stats['total_orders'])}
⏳ الطلبات المعلقة: {Utils.format_number(stats['pending_orders'])}
📢 القنوات النشطة: {Utils.format_number(stats['total_channels'])}
        """
        
        await query.edit_message_text(text)