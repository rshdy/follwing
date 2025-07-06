import re
from datetime import datetime
from config import Config

class Utils:
    @staticmethod
    def is_valid_instagram_url(url):
        """Check if URL is valid Instagram URL"""
        patterns = [
            r'^https?://(www\.)?instagram\.com/p/[A-Za-z0-9_-]+/?$',
            r'^https?://(www\.)?instagram\.com/[A-Za-z0-9_.]+/?$',
            r'^https?://(www\.)?instagram\.com/reel/[A-Za-z0-9_-]+/?$'
        ]
        return any(re.match(pattern, url) for pattern in patterns)
    
    @staticmethod
    def is_valid_tiktok_url(url):
        """Check if URL is valid TikTok URL"""
        patterns = [
            r'^https?://(www\.)?tiktok\.com/@[A-Za-z0-9_.]+/video/\d+$',
            r'^https?://vm\.tiktok\.com/[A-Za-z0-9]+/?$',
            r'^https?://www\.tiktok\.com/t/[A-Za-z0-9]+/?$'
        ]
        return any(re.match(pattern, url) for pattern in patterns)
    
    @staticmethod
    def is_valid_youtube_url(url):
        """Check if URL is valid YouTube URL"""
        patterns = [
            r'^https?://(www\.)?youtube\.com/watch\?v=[A-Za-z0-9_-]+',
            r'^https?://(www\.)?youtu\.be/[A-Za-z0-9_-]+',
            r'^https?://(www\.)?youtube\.com/shorts/[A-Za-z0-9_-]+'
        ]
        return any(re.match(pattern, url) for pattern in patterns)
    
    @staticmethod
    def is_valid_telegram_url(url):
        """Check if URL is valid Telegram URL"""
        patterns = [
            r'^https?://t\.me/[A-Za-z0-9_]+/\d+$',
            r'^https?://telegram\.me/[A-Za-z0-9_]+/\d+$'
        ]
        return any(re.match(pattern, url) for pattern in patterns)
    
    @staticmethod
    def validate_service_url(service_type, url):
        """Validate URL based on service type"""
        if service_type == 'instagram':
            return Utils.is_valid_instagram_url(url)
        elif service_type == 'tiktok':
            return Utils.is_valid_tiktok_url(url)
        elif service_type == 'youtube':
            return Utils.is_valid_youtube_url(url)
        elif service_type == 'telegram':
            return Utils.is_valid_telegram_url(url)
        return False
    
    @staticmethod
    def calculate_points_cost(service_type, quantity):
        """Calculate points cost for service"""
        if service_type == 'followers':
            return max(1, (quantity * Config.FOLLOWERS_COST) // 1000)
        elif service_type == 'likes':
            return max(1, (quantity * Config.LIKES_COST) // 1000)
        elif service_type == 'views':
            return max(1, (quantity * Config.VIEWS_COST) // 1000)
        return 1
    
    @staticmethod
    def calculate_cost(service_type, quantity):
        """Alternative method name for backwards compatibility"""
        return Utils.calculate_points_cost(service_type, quantity)
    
    @staticmethod
    def format_service_name(service_type):
        """Format service name in Arabic"""
        names = {
            'followers': 'متابعين',
            'likes': 'إعجابات',
            'views': 'مشاهدات',
            'comments': 'تعليقات',
            'shares': 'مشاركات',
            'instagram_followers': 'متابعين انستقرام',
            'instagram_likes': 'إعجابات انستقرام',
            'instagram_views': 'مشاهدات انستقرام',
            'youtube_subscribers': 'مشتركين يوتيوب',
            'youtube_views': 'مشاهدات يوتيوب',
            'tiktok_followers': 'متابعين تيك توك',
            'tiktok_likes': 'إعجابات تيك توك'
        }
        return names.get(service_type, service_type)
    
    @staticmethod
    def format_number(number):
        """Format number with thousands separator"""
        return f"{number:,}"
    
    @staticmethod
    def format_date(date_str):
        """Format date string"""
        if isinstance(date_str, str):
            try:
                date_obj = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
                return date_obj.strftime('%Y/%m/%d %H:%M')
            except:
                return date_str
        return str(date_str)
    
    @staticmethod
    def get_service_emoji(service_type):
        """Get emoji for service type"""
        emojis = {
            'followers': '👥',
            'likes': '❤️',
            'views': '👀',
            'comments': '💬',
            'shares': '🔄'
        }
        return emojis.get(service_type, '🔧')
    
    @staticmethod
    def get_platform_emoji(platform):
        """Get emoji for platform"""
        emojis = {
            'instagram': '📸',
            'tiktok': '🎵',
            'youtube': '📺',
            'telegram': '✈️',
            'twitter': '🐦',
            'facebook': '📘'
        }
        return emojis.get(platform, '🌐')
    
    @staticmethod
    def truncate_text(text, max_length=100):
        """Truncate text if too long"""
        if len(text) <= max_length:
            return text
        return text[:max_length-3] + "..."
    
    @staticmethod
    def is_valid_quantity(quantity, min_qty=100, max_qty=10000):
        """Check if quantity is valid"""
        try:
            qty = int(quantity)
            return min_qty <= qty <= max_qty
        except:
            return False
    
    @staticmethod
    def format_order_status(status):
        """Format order status with emoji"""
        status_map = {
            'pending': '⏳ معلق',
            'processing': '🔄 قيد التنفيذ',
            'completed': '✅ مكتمل',
            'cancelled': '❌ ملغى',
            'failed': '🔴 فشل'
        }
        return status_map.get(status, status)
    
    @staticmethod
    def create_progress_bar(current, total, length=10):
        """Create progress bar"""
        if total == 0:
            return "□" * length
        
        progress = min(current / total, 1.0)
        filled = int(progress * length)
        empty = length - filled
        
        return "■" * filled + "□" * empty
    
    @staticmethod
    def format_order_details(order):
        """Format order details for display"""
        order_id, user_id, service_type, target_url, quantity, points_cost, status, created_date, completed_date = order
        
        text = f"""
📋 **تفاصيل الطلب #{order_id}**

🔧 الخدمة: {Utils.get_service_emoji(service_type)} {service_type}
🎯 الرابط: {Utils.truncate_text(target_url)}
📊 الكمية: {Utils.format_number(quantity)}
💰 التكلفة: {Utils.format_number(points_cost)} نقطة
📅 تاريخ الطلب: {Utils.format_date(created_date)}
📈 الحالة: {Utils.format_order_status(status)}
        """
        
        if completed_date:
            text += f"\n🏁 تاريخ الإكمال: {Utils.format_date(completed_date)}"
        
        return text
    
    @staticmethod
    def generate_referral_link(user_id, bot_username):
        """Generate referral link for user"""
        return f"https://t.me/{bot_username}?start=ref_{user_id}"
    
    @staticmethod
    def extract_referral_id(start_param):
        """Extract referral ID from start parameter"""
        if start_param and start_param.startswith('ref_'):
            try:
                return int(start_param.split('_')[1])
            except:
                return None
        return None
    
    @staticmethod
    def validate_channel_id(channel_id):
        """Validate channel ID format"""
        if not channel_id:
            return False
        
        # Should start with @ or -100
        if channel_id.startswith('@'):
            return len(channel_id) > 1 and channel_id[1:].replace('_', '').isalnum()
        elif channel_id.startswith('-100'):
            return channel_id[1:].isdigit()
        
        return False
    
    @staticmethod
    def clean_channel_id(channel_id):
        """Clean channel ID"""
        if not channel_id:
            return None
        
        channel_id = channel_id.strip()
        
        # Remove https://t.me/ prefix if present
        if channel_id.startswith('https://t.me/'):
            channel_id = '@' + channel_id.replace('https://t.me/', '')
        
        # Add @ prefix if missing
        if not channel_id.startswith('@') and not channel_id.startswith('-'):
            channel_id = '@' + channel_id
        
        return channel_id
    
    @staticmethod
    def time_ago(date_str):
        """Get time ago string"""
        try:
            if isinstance(date_str, str):
                date_obj = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
            else:
                date_obj = date_str
            
            now = datetime.now()
            diff = now - date_obj
            
            if diff.days > 0:
                return f"{diff.days} يوم مضى"
            elif diff.seconds > 3600:
                hours = diff.seconds // 3600
                return f"{hours} ساعة مضت"
            elif diff.seconds > 60:
                minutes = diff.seconds // 60
                return f"{minutes} دقيقة مضت"
            else:
                return "الآن"
        except:
            return "غير معروف"
    
    @staticmethod
    def is_maintenance_mode():
        """Check if bot is in maintenance mode"""
        return Config.MAINTENANCE_MODE
    
    @staticmethod
    def get_maintenance_message():
        """Get maintenance message"""
        return """
🔧 البوت قيد الصيانة حالياً

نعتذر عن الإزعاج، البوت قيد الصيانة والتحديث.
سيعود للعمل قريباً إن شاء الله.

⏰ المدة المتوقعة: 30 دقيقة
        """