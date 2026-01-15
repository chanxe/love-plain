from app import app, db, Anniversary, User, Moment
from datetime import date, timedelta, datetime
import os

def seed_data():
    with app.app_context():
        # Drop all tables to reset schema
        db.drop_all()
        # Create Tables if not exist
        db.create_all()

        # Seed Users
        if User.query.count() == 0:
            print("Seeding Users...")
            boy = User(name='Boy', avatar='https://cdn-icons-png.flaticon.com/512/4140/4140048.png') # External placeholder
            girl = User(name='Girl', avatar='https://cdn-icons-png.flaticon.com/512/4140/4140047.png') # External placeholder
            db.session.add(boy)
            db.session.add(girl)
            db.session.commit()
            print("Users seeded.")

        # Seed Anniversaries
        count = Anniversary.query.count()
        if count <= 5:
            needed = 8 - count
            print(f"Adding {needed} test anniversaries...")
            for i in range(needed):
                d = date.today() - timedelta(days=i*30 + 10)
                a = Anniversary(title=f"测试纪念日 {count + i + 1}", date=d)
                db.session.add(a)
            db.session.commit()

        # Seed Moments
        if Moment.query.count() == 0:
            print("Seeding Moments...")
            user_ids = [u.id for u in User.query.all()]
            for i in range(10):
                m = Moment(
                    content=f"这是第 {i+1} 条动态，今天心情不错！",
                    user_id=user_ids[i % len(user_ids)],
                    timestamp=datetime.utcnow() - timedelta(hours=i*5)
                )
                db.session.add(m)
            db.session.commit()
            print("Moments seeded.")
            
        print("Seed complete!")

if __name__ == "__main__":
    seed_data()
