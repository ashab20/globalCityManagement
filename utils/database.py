from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base

# SQLAlchemy Base and Session
Base = declarative_base()

MYSQL_USERNAME = "root"        
MYSQL_PASSWORD = "ServBay.dev" 
MYSQL_HOST = "localhost"        
MYSQL_PORT = 3306               
MYSQL_DATABASE = "global_city_management" 

# Use pymysql as the driver (or mysqlclient if preferred)
DATABASE_URL = f"mysql+pymysql://{MYSQL_USERNAME}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}"

# Initialize Engine and Session
engine = create_engine(DATABASE_URL, echo=True)
Session = sessionmaker(bind=engine)


def setup_database():
    """Initialize the database with all tables"""
    # Import all models to ensure they are registered with Base
    from models.user import User
    from models.user_role import UserRole
    from models.shop_profile import ShopProfile

    # Use a connection to execute raw SQL
    with engine.connect() as connection:
        connection.execute(text("SET FOREIGN_KEY_CHECKS = 0"))
        
        # Drop all tables
        Base.metadata.drop_all(engine)

        # Recreate all tables
        Base.metadata.create_all(engine)

        connection.execute(text("SET FOREIGN_KEY_CHECKS = 1"))
        connection.commit()

    session = Session()
    try:
        # Create admin role if it doesn't exist
        admin_role = session.query(UserRole).filter_by(name="Admin").first()
        if not admin_role:
            admin_role = UserRole(name="Admin")
            session.add(admin_role)
            session.flush()  # This will assign the id to admin_role
            
        # Create admin user
        admin_user = session.query(User).filter_by(login_id="admin").first()
        if not admin_user:
            from werkzeug.security import generate_password_hash
            admin_user = User(
                role_id=admin_role.id,
                login_id="admin",
                usr_full_name="Administrator",
                email="admin@example.com",
                phone="1234567890",
                password=generate_password_hash("admin123"),
                active_status=1
            )
            session.add(admin_user)
        
        # Create basic user role if it doesn't exist
        user_role = session.query(UserRole).filter_by(name="User").first()
        if not user_role:
            user_role = UserRole(name="User")
            session.add(user_role)
        
        session.commit()
    except Exception as e:
        session.rollback()
        print(f"Error creating initial data: {e}")
    finally:
        session.close()
