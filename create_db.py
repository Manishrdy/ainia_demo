# create_db.py

from app import app
from models import db, User

def setup_database():
    with app.app_context():
        print("Dropping all database tables...")
        db.drop_all()
        print("Creating all database tables...")
        db.create_all()

        print("Adding a test user to the database...")
        test_user = User(
            email='test.parent@example.com',
            name='Test Parent',
            parent_choice='seed'
        )

        # Add the new user object to the database session
        db.session.add(test_user)

        # Commit the changes to write them to the database file
        db.session.commit()
        print("Test user 'Test Parent' added successfully.")
        print("Database setup is complete!")

# This makes the script runnable from the command line
if __name__ == '__main__':
    setup_database()