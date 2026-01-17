import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db, LoveOneDayReport

def clear_love_one_day_cache():
    """清除爱的一天缓存"""
    with app.app_context():
        print("=" * 60)
        print("清除爱的一天缓存")
        print("=" * 60)
        
        try:
            count = LoveOneDayReport.query.count()
            print(f"\n当前缓存记录数: {count}")
            
            if count > 0:
                LoveOneDayReport.query.delete()
                db.session.commit()
                print(f"✅ 已清除 {count} 条缓存记录")
            else:
                print("⚠️  当前没有缓存记录")
            
            print(f"\n{'='*60}")
            print("缓存清除完成")
            print(f"{'='*60}")
            
        except Exception as e:
            db.session.rollback()
            print(f"\n❌ 清除缓存时发生错误: {e}")
            import traceback
            traceback.print_exc()
            return False
        
        return True

if __name__ == '__main__':
    success = clear_love_one_day_cache()
    sys.exit(0 if success else 1)