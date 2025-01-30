import os
import sys

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

from utils.database import setup_database, Session
from models.role import Role
from models.user import User
from werkzeug.security import generate_password_hash

def create_initial_data():
    session = Session()
    try:
        # Create admin role if it doesn't exist
        admin_role = session.query(Role).filter_by(name="Admin").first()
        if not admin_role:
            admin_role = Role(name="Admin")
            session.add(admin_role)
            session.flush()  # This will assign the id to admin_role
            
            # Create admin user
            admin_user = User(
                username="admin",
                email="admin@example.com",
                password=generate_password_hash("admin123"),
                ptext="admin123",
                phone="0174444444",
                avatar="admin.png",
                role_id=admin_role.id
            )
            session.add(admin_user)
        
        # Create basic user role if it doesn't exist
        user_role = session.query(Role).filter_by(name="User").first()
        if not user_role:
            user_role = Role(name="User")
            session.add(user_role)
        
        session.commit()
        print("Initial data created successfully!")
        
    except Exception as e:
        session.rollback()
        print(f"Error creating initial data: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    # Create tables
    setup_database()
    
    # Create initial roles and admin user
    create_initial_data()
