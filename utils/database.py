from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# SQLAlchemy Base and Session
Base = declarative_base()

MYSQL_USERNAME = "root"        
MYSQL_PASSWORD = "ServBay.dev" 
MYSQL_HOST = "localhost"        
MYSQL_PORT = 3306               
MYSQL_DATABASE = "baliarchide" 

# Use pymysql as the driver (or mysqlclient if preferred)
DATABASE_URL = f"mysql+pymysql://{MYSQL_USERNAME}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}"

# Initialize Engine and Session
engine = create_engine(DATABASE_URL, echo=True)
Session = sessionmaker(bind=engine)


def setup_database():
    """Initialize the database with all tables"""
    # Import all models to ensure they are registered with Base
    from models.user import User
    from models.role import Role
    from models.shop import Shop
    from models.renter import Renter

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

    print("Creating database tables...")
    # Create all tables
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    print("Database tables created successfully!")
