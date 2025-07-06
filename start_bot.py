#!/usr/bin/env python3
"""
بوت تلغرام للرشق المتقدم
Script لبدء تشغيل البوت - Railway Version
"""

import sys
import os
import asyncio
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def check_requirements():
    """Check if all requirements are met"""
    errors = []
    
    # Check Python version
    if sys.version_info < (3, 8):
        errors.append("Python 3.8+ مطلوب")
    
    # Check required packages
    required_packages = [
        'telegram',
        'requests',
        'aiofiles'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        errors.append(f"المكتبات المطلوبة غير مثبتة: {', '.join(missing_packages)}")
    
    return errors

def main():
    """Main function"""
    print("🚀 بدء تشغيل بوت الرشق المتقدم...")
    
    # Check requirements
    errors = check_requirements()
    if errors:
        print("\n❌ أخطاء في المتطلبات:")
        for error in errors:
            print(f"• {error}")
        print("\n🔧 يرجى حل هذه المشاكل أولاً")
        sys.exit(1)
    
    # Check config
    try:
        from config import Config
        if Config.BOT_TOKEN == 'YOUR_BOT_TOKEN_HERE':
            print("❌ يرجى تحديث BOT_TOKEN في متغيرات البيئة")
            sys.exit(1)
    except ImportError:
        print("❌ ملف config.py غير موجود")
        sys.exit(1)
    
    # Run the bot
    try:
        print("✅ جميع المتطلبات متوفرة")
        print("🔄 بدء تشغيل البوت...")
        
        # Import and run the bot
        from main import main as bot_main
        asyncio.run(bot_main())
        
    except KeyboardInterrupt:
        print("\n⏹️ تم إيقاف البوت بواسطة المستخدم")
    except Exception as e:
        print(f"\n❌ خطأ في تشغيل البوت: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()