from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, scoped_session
import pymysql

# Database Configuration
MYSQL_USERNAME = "root"        
MYSQL_PASSWORD = "ServBay.dev" 
MYSQL_HOST = "localhost"        
MYSQL_PORT = 3306               
MYSQL_DATABASE = "db_globalcity" 

# Connect to MySQL Server (without specifying a database) to create the database if it doesn't exist
try:
    root_engine = create_engine(f"mysql+pymysql://{MYSQL_USERNAME}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/")
    with root_engine.connect() as conn:
        try:
            conn.execute(text(f"CREATE DATABASE IF NOT EXISTS {MYSQL_DATABASE}"))
            print(f"Database '{MYSQL_DATABASE}' checked/created successfully.")
        except Exception as db_create_error:
            print(f"Error creating database: {db_create_error}")
            raise
except Exception as connection_error:
    print(f"Error connecting to MySQL server: {connection_error}")
    raise

# Now, connect to the specific database
try:
    DATABASE_URL = f"mysql+pymysql://{MYSQL_USERNAME}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}"
    engine = create_engine(DATABASE_URL, echo=True)
    session_factory = sessionmaker(bind=engine)
    Session = scoped_session(session_factory)
except Exception as engine_error:
    print(f"Error creating database engine: {engine_error}")
    raise

# Declarative Base
from models.base import Base

# Import all models to ensure they are registered with Base
def import_all_models():
    """Import all models to register them with Base"""
    try:
        # Core models
        from models.user import User
        from models.user_role import UserRole
        from models.shop_profile import ShopProfile
        from models.shop_renter_profile import ShopRenterProfile
        from models.shop_allocation import ShopAllocation
        from models.shop_owner_profile import ShopOwnerProfile
        
        # Additional models
        from models.BankAccount import BankAccount
        from models.JournalVoucher import JournalVoucher
        from models.UtilitySetting import UtilitySetting
        
        print("All models imported successfully.")
    except ImportError as e:
        print(f"Error importing models: {e}")
        raise

# DO NOT call import_all_models() here to prevent circular imports

def setup_database():
    """Initialize the database with all tables"""
    # Create all tables
    Base.metadata.create_all(engine)
    print("All tables created successfully.")

    # Insert Initial Data
    session = Session()
    try:
        # Create Admin Role
        admin_role = session.query(UserRole).filter_by(name="Admin").first()
        if not admin_role:
            admin_role = UserRole(name="Admin")
            session.add(admin_role)
            session.flush()  # Assigns ID

        # Create Admin User
        admin_user = session.query(User).filter_by(login_id="admin").first()
        if not admin_user:
            from werkzeug.security import generate_password_hash
            admin_user = User(
                login_id="admin",
                password=generate_password_hash("admin123"),
                name="Admin User",
                user_role_id=admin_role.id,
                is_active=True
            )
            session.add(admin_user)

        # Create User Role
        user_role = session.query(UserRole).filter_by(name="User").first()
        if not user_role:
            user_role = UserRole(name="User")
            session.add(user_role)

        session.commit()
        print("Initial data inserted successfully.")
    except Exception as e:
        session.rollback()
        print(f"Error creating initial data: {e}")
    finally:
        session.close()
