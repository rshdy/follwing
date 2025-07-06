from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton

class Keyboards:
    @staticmethod
    def main_menu():
        """Main menu keyboard"""
        keyboard = [
            [KeyboardButton("💎 رصيد النقاط"), KeyboardButton("👤 الملف الشخصي")],
            [KeyboardButton("🚀 طلب خدمة"), KeyboardButton("📋 طلباتي")],
            [KeyboardButton("📢 القنوات"), KeyboardButton("🎯 رابط الإحالة")],
            [KeyboardButton("📊 الإحصائيات"), KeyboardButton("ℹ️ المساعدة")]
        ]
        return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    @staticmethod
    def admin_menu():
        """Admin menu keyboard"""
        keyboard = [
            [KeyboardButton("📊 إحصائيات البوت"), KeyboardButton("👥 المستخدمين")],
            [KeyboardButton("📢 إدارة القنوات"), KeyboardButton("📦 إدارة الطلبات")],
            [KeyboardButton("✉️ رسالة جماعية"), KeyboardButton("💎 إرسال نقاط")],
            [KeyboardButton("🔙 القائمة الرئيسية")]
        ]
        return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    @staticmethod
    def services_menu():
        """Services selection keyboard"""
        keyboard = [
            [
                InlineKeyboardButton("👥 متابعين انستغرام", callback_data="service_instagram_followers"),
                InlineKeyboardButton("❤️ إعجابات انستغرام", callback_data="service_instagram_likes")
            ],
            [
                InlineKeyboardButton("👀 مشاهدات انستغرام", callback_data="service_instagram_views"),
                InlineKeyboardButton("👥 متابعين تيكتوك", callback_data="service_tiktok_followers")
            ],
            [
                InlineKeyboardButton("❤️ إعجابات تيكتوك", callback_data="service_tiktok_likes"),
                InlineKeyboardButton("👀 مشاهدات تيكتوك", callback_data="service_tiktok_views")
            ],
            [InlineKeyboardButton("🔙 العودة", callback_data="back_to_main")]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def quantity_keyboard(service_type):
        """Quantity selection keyboard"""
        keyboard = [
            [
                InlineKeyboardButton("100", callback_data=f"quantity_{service_type}_100"),
                InlineKeyboardButton("500", callback_data=f"quantity_{service_type}_500")
            ],
            [
                InlineKeyboardButton("1000", callback_data=f"quantity_{service_type}_1000"),
                InlineKeyboardButton("5000", callback_data=f"quantity_{service_type}_5000")
            ],
            [
                InlineKeyboardButton("10000", callback_data=f"quantity_{service_type}_10000"),
                InlineKeyboardButton("مخصص", callback_data=f"quantity_{service_type}_custom")
            ],
            [InlineKeyboardButton("🔙 العودة", callback_data="back_to_services")]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def confirm_order_keyboard(order_id):
        """Confirm order keyboard"""
        keyboard = [
            [
                InlineKeyboardButton("✅ تأكيد الطلب", callback_data=f"confirm_order_{order_id}"),
                InlineKeyboardButton("❌ إلغاء", callback_data="cancel_order")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def channels_keyboard(channels):
        """Channels subscription keyboard"""
        keyboard = []
        for channel in channels:
            channel_id, channel_name, channel_username, points_reward = channel[1], channel[2], channel[3], channel[4]
            if channel_username:
                keyboard.append([
                    InlineKeyboardButton(
                        f"📢 {channel_name} (+{points_reward} نقطة)",
                        url=f"https://t.me/{channel_username}"
                    )
                ])
            else:
                keyboard.append([
                    InlineKeyboardButton(
                        f"📢 {channel_name} (+{points_reward} نقطة)",
                        url=f"https://t.me/{channel_id}"
                    )
                ])
        
        keyboard.append([InlineKeyboardButton("✅ تحقق من الاشتراك", callback_data="check_subscriptions")])
        keyboard.append([InlineKeyboardButton("🔙 العودة", callback_data="back_to_main")])
        
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def admin_channels_keyboard():
        """Admin channels management keyboard"""
        keyboard = [
            [
                InlineKeyboardButton("➕ إضافة قناة", callback_data="add_channel"),
                InlineKeyboardButton("➖ حذف قناة", callback_data="remove_channel")
            ],
            [
                InlineKeyboardButton("📋 قائمة القنوات", callback_data="list_channels"),
                InlineKeyboardButton("🔙 العودة", callback_data="back_to_admin")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def admin_orders_keyboard():
        """Admin orders management keyboard"""
        keyboard = [
            [
                InlineKeyboardButton("📋 جميع الطلبات", callback_data="all_orders"),
                InlineKeyboardButton("⏳ الطلبات المعلقة", callback_data="pending_orders")
            ],
            [
                InlineKeyboardButton("✅ إكمال طلب", callback_data="complete_order"),
                InlineKeyboardButton("❌ إلغاء طلب", callback_data="cancel_order_admin")
            ],
            [InlineKeyboardButton("🔙 العودة", callback_data="back_to_admin")]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def order_action_keyboard(order_id):
        """Order action keyboard for admin"""
        keyboard = [
            [
                InlineKeyboardButton("✅ إكمال", callback_data=f"admin_complete_{order_id}"),
                InlineKeyboardButton("❌ إلغاء", callback_data=f"admin_cancel_{order_id}")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def back_keyboard():
        """Simple back keyboard"""
        keyboard = [[InlineKeyboardButton("🔙 العودة", callback_data="back_to_main")]]
        return InlineKeyboardMarkup(keyboard)from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton

class Keyboards:
    @staticmethod
    def main_menu():
        """Main menu keyboard"""
        keyboard = [
            [KeyboardButton("💎 رصيد النقاط"), KeyboardButton("👤 الملف الشخصي")],
            [KeyboardButton("🚀 طلب خدمة"), KeyboardButton("📋 طلباتي")],
            [KeyboardButton("📢 القنوات"), KeyboardButton("🎯 رابط الإحالة")],
            [KeyboardButton("📊 الإحصائيات"), KeyboardButton("ℹ️ المساعدة")]
        ]
        return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    @staticmethod
    def admin_menu():
        """Admin menu keyboard"""
        keyboard = [
            [KeyboardButton("📊 إحصائيات البوت"), KeyboardButton("👥 المستخدمين")],
            [KeyboardButton("📢 إدارة القنوات"), KeyboardButton("📦 إدارة الطلبات")],
            [KeyboardButton("✉️ رسالة جماعية"), KeyboardButton("💎 إرسال نقاط")],
            [KeyboardButton("🔙 القائمة الرئيسية")]
        ]
        return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    @staticmethod
    def services_menu():
        """Services selection keyboard"""
        keyboard = [
            [
                InlineKeyboardButton("👥 متابعين انستغرام", callback_data="service_instagram_followers"),
                InlineKeyboardButton("❤️ إعجابات انستغرام", callback_data="service_instagram_likes")
            ],
            [
                InlineKeyboardButton("👀 مشاهدات انستغرام", callback_data="service_instagram_views"),
                InlineKeyboardButton("👥 متابعين تيكتوك", callback_data="service_tiktok_followers")
            ],
            [
                InlineKeyboardButton("❤️ إعجابات تيكتوك", callback_data="service_tiktok_likes"),
                InlineKeyboardButton("👀 مشاهدات تيكتوك", callback_data="service_tiktok_views")
            ],
            [InlineKeyboardButton("🔙 العودة", callback_data="back_to_main")]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def quantity_keyboard(service_type):
        """Quantity selection keyboard"""
        keyboard = [
            [
                InlineKeyboardButton("100", callback_data=f"quantity_{service_type}_100"),
                InlineKeyboardButton("500", callback_data=f"quantity_{service_type}_500")
            ],
            [
                InlineKeyboardButton("1000", callback_data=f"quantity_{service_type}_1000"),
                InlineKeyboardButton("5000", callback_data=f"quantity_{service_type}_5000")
            ],
            [
                InlineKeyboardButton("10000", callback_data=f"quantity_{service_type}_10000"),
                InlineKeyboardButton("مخصص", callback_data=f"quantity_{service_type}_custom")
            ],
            [InlineKeyboardButton("🔙 العودة", callback_data="back_to_services")]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def confirm_order_keyboard(order_id):
        """Confirm order keyboard"""
        keyboard = [
            [
                InlineKeyboardButton("✅ تأكيد الطلب", callback_data=f"confirm_order_{order_id}"),
                InlineKeyboardButton("❌ إلغاء", callback_data="cancel_order")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def channels_keyboard(channels):
        """Channels subscription keyboard"""
        keyboard = []
        for channel in channels:
            channel_id, channel_name, channel_username, points_reward = channel[1], channel[2], channel[3], channel[4]
            if channel_username:
                keyboard.append([
                    InlineKeyboardButton(
                        f"📢 {channel_name} (+{points_reward} نقطة)",
                        url=f"https://t.me/{channel_username}"
                    )
                ])
            else:
                keyboard.append([
                    InlineKeyboardButton(
                        f"📢 {channel_name} (+{points_reward} نقطة)",
                        url=f"https://t.me/{channel_id}"
                    )
                ])
        
        keyboard.append([InlineKeyboardButton("✅ تحقق من الاشتراك", callback_data="check_subscriptions")])
        keyboard.append([InlineKeyboardButton("🔙 العودة", callback_data="back_to_main")])
        
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def admin_channels_keyboard():
        """Admin channels management keyboard"""
        keyboard = [
            [
                InlineKeyboardButton("➕ إضافة قناة", callback_data="add_channel"),
                InlineKeyboardButton("➖ حذف قناة", callback_data="remove_channel")
            ],
            [
                InlineKeyboardButton("📋 قائمة القنوات", callback_data="list_channels"),
                InlineKeyboardButton("🔙 العودة", callback_data="back_to_admin")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def admin_orders_keyboard():
        """Admin orders management keyboard"""
        keyboard = [
            [
                InlineKeyboardButton("📋 جميع الطلبات", callback_data="all_orders"),
                InlineKeyboardButton("⏳ الطلبات المعلقة", callback_data="pending_orders")
            ],
            [
                InlineKeyboardButton("✅ إكمال طلب", callback_data="complete_order"),
                InlineKeyboardButton("❌ إلغاء طلب", callback_data="cancel_order_admin")
            ],
            [InlineKeyboardButton("🔙 العودة", callback_data="back_to_admin")]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def order_action_keyboard(order_id):
        """Order action keyboard for admin"""
        keyboard = [
            [
                InlineKeyboardButton("✅ إكمال", callback_data=f"admin_complete_{order_id}"),
                InlineKeyboardButton("❌ إلغاء", callback_data=f"admin_cancel_{order_id}")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def back_keyboard():
        """Simple back keyboard"""
        keyboard = [[InlineKeyboardButton("🔙 العودة", callback_data="back_to_main")]]
        return InlineKeyboardMarkup(keyboard)from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton

class Keyboards:
    @staticmethod
    def main_menu():
        """Main menu keyboard"""
        keyboard = [
            [KeyboardButton("💎 رصيد النقاط"), KeyboardButton("👤 الملف الشخصي")],
            [KeyboardButton("🚀 طلب خدمة"), KeyboardButton("📋 طلباتي")],
            [KeyboardButton("📢 القنوات"), KeyboardButton("🎯 رابط الإحالة")],
            [KeyboardButton("📊 الإحصائيات"), KeyboardButton("ℹ️ المساعدة")]
        ]
        return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    @staticmethod
    def admin_menu():
        """Admin menu keyboard"""
        keyboard = [
            [KeyboardButton("📊 إحصائيات البوت"), KeyboardButton("👥 المستخدمين")],
            [KeyboardButton("📢 إدارة القنوات"), KeyboardButton("📦 إدارة الطلبات")],
            [KeyboardButton("✉️ رسالة جماعية"), KeyboardButton("💎 إرسال نقاط")],
            [KeyboardButton("🔙 القائمة الرئيسية")]
        ]
        return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    @staticmethod
    def services_menu():
        """Services selection keyboard"""
        keyboard = [
            [
                InlineKeyboardButton("👥 متابعين انستغرام", callback_data="service_instagram_followers"),
                InlineKeyboardButton("❤️ إعجابات انستغرام", callback_data="service_instagram_likes")
            ],
            [
                InlineKeyboardButton("👀 مشاهدات انستغرام", callback_data="service_instagram_views"),
                InlineKeyboardButton("👥 متابعين تيكتوك", callback_data="service_tiktok_followers")
            ],
            [
                InlineKeyboardButton("❤️ إعجابات تيكتوك", callback_data="service_tiktok_likes"),
                InlineKeyboardButton("👀 مشاهدات تيكتوك", callback_data="service_tiktok_views")
            ],
            [InlineKeyboardButton("🔙 العودة", callback_data="back_to_main")]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def quantity_keyboard(service_type):
        """Quantity selection keyboard"""
        keyboard = [
            [
                InlineKeyboardButton("100", callback_data=f"quantity_{service_type}_100"),
                InlineKeyboardButton("500", callback_data=f"quantity_{service_type}_500")
            ],
            [
                InlineKeyboardButton("1000", callback_data=f"quantity_{service_type}_1000"),
                InlineKeyboardButton("5000", callback_data=f"quantity_{service_type}_5000")
            ],
            [
                InlineKeyboardButton("10000", callback_data=f"quantity_{service_type}_10000"),
                InlineKeyboardButton("مخصص", callback_data=f"quantity_{service_type}_custom")
            ],
            [InlineKeyboardButton("🔙 العودة", callback_data="back_to_services")]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def confirm_order_keyboard(order_id):
        """Confirm order keyboard"""
        keyboard = [
            [
                InlineKeyboardButton("✅ تأكيد الطلب", callback_data=f"confirm_order_{order_id}"),
                InlineKeyboardButton("❌ إلغاء", callback_data="cancel_order")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def channels_keyboard(channels):
        """Channels subscription keyboard"""
        keyboard = []
        for channel in channels:
            channel_id, channel_name, channel_username, points_reward = channel[1], channel[2], channel[3], channel[4]
            if channel_username:
                keyboard.append([
                    InlineKeyboardButton(
                        f"📢 {channel_name} (+{points_reward} نقطة)",
                        url=f"https://t.me/{channel_username}"
                    )
                ])
            else:
                keyboard.append([
                    InlineKeyboardButton(
                        f"📢 {channel_name} (+{points_reward} نقطة)",
                        url=f"https://t.me/{channel_id}"
                    )
                ])
        
        keyboard.append([InlineKeyboardButton("✅ تحقق من الاشتراك", callback_data="check_subscriptions")])
        keyboard.append([InlineKeyboardButton("🔙 العودة", callback_data="back_to_main")])
        
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def admin_channels_keyboard():
        """Admin channels management keyboard"""
        keyboard = [
            [
                InlineKeyboardButton("➕ إضافة قناة", callback_data="add_channel"),
                InlineKeyboardButton("➖ حذف قناة", callback_data="remove_channel")
            ],
            [
                InlineKeyboardButton("📋 قائمة القنوات", callback_data="list_channels"),
                InlineKeyboardButton("🔙 العودة", callback_data="back_to_admin")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def admin_orders_keyboard():
        """Admin orders management keyboard"""
        keyboard = [
            [
                InlineKeyboardButton("📋 جميع الطلبات", callback_data="all_orders"),
                InlineKeyboardButton("⏳ الطلبات المعلقة", callback_data="pending_orders")
            ],
            [
                InlineKeyboardButton("✅ إكمال طلب", callback_data="complete_order"),
                InlineKeyboardButton("❌ إلغاء طلب", callback_data="cancel_order_admin")
            ],
            [InlineKeyboardButton("🔙 العودة", callback_data="back_to_admin")]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def order_action_keyboard(order_id):
        """Order action keyboard for admin"""
        keyboard = [
            [
                InlineKeyboardButton("✅ إكمال", callback_data=f"admin_complete_{order_id}"),
                InlineKeyboardButton("❌ إلغاء", callback_data=f"admin_cancel_{order_id}")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def back_keyboard():
        """Simple back keyboard"""
        keyboard = [[InlineKeyboardButton("🔙 العودة", callback_data="back_to_main")]]
        return InlineKeyboardMarkup(keyboard)