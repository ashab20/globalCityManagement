import os
import sys
import traceback

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

from utils.database import setup_database, Session, Base, engine
from models.user_role import UserRole
from models.user import User
from models.shop_profile import ShopProfile
from models.shop_renter_profile import ShopRenterProfile
from models.shop_allocation import ShopAllocation
from models.shop_owner_profile import ShopOwnerProfile
from models.BankAccount import BankAccount
from models.JournalVoucher import JournalVoucher
from models.UtilitySetting import UtilitySetting
from models.teanant_trans_history import TeanantTransHistory
from werkzeug.security import generate_password_hash

def create_initial_data():
    session = Session()
    try:
        # Create admin role if it doesn't exist
        admin_role = session.query(UserRole).filter_by(name="Admin").first()
        if not admin_role:
            admin_role = UserRole(name="Admin")
            session.add(admin_role)
            session.flush()  # This will assign the id to admin_role
            
            # Create admin user
            admin_user = User(
                login_id="admin",
                name="Admin User",
                password=generate_password_hash("admin123"),
                user_role_id=admin_role.id,
                is_active=True
            )
            session.add(admin_user)
        
        # Create additional roles
        roles = [
            UserRole(name="IT Admin"),
            UserRole(name="Executives"),
        ]

        for role in roles:
            existing_role = session.query(UserRole).filter_by(name=role.name).first()
            if not existing_role:
                session.add(role)
        
        session.commit()
        print("Initial data created successfully!")
        
    except Exception as e:
        session.rollback()
        print(f"Error creating initial data: {e}")
        traceback.print_exc()
    finally:
        session.close()

def main():
    try:
        # Explicitly import and register models
        from models.user import User
        from models.user_role import UserRole
        from models.shop_profile import ShopProfile
        from models.shop_renter_profile import ShopRenterProfile
        from models.shop_allocation import ShopAllocation
        from models.shop_owner_profile import ShopOwnerProfile
        from models.BankAccount import BankAccount
        from models.JournalVoucher import JournalVoucher
        from models.UtilitySetting import UtilitySetting
        from models.teanant_trans_history import TeanantTransHistory
        # Explicitly create all tables
        print("Starting database setup...")
        
        # Print all registered models
        print("Registered models:")
        for table_name, table in Base.metadata.tables.items():
            print(f"- {table_name}")
            print(f"  - Columns: {[column.name for column in table.columns]}")
            print(f"  - Primary Key: {[column.name for column in table.primary_key.columns]}")
        
        # Create all tables
        Base.metadata.create_all(engine)
        print("All tables created successfully.")
        
        # Create initial data
        create_initial_data()
        
    except Exception as e:
        print(f"Fatal error during database setup: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    main()
