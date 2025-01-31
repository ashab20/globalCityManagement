from utils.database import Session, setup_database
from models.user_role import UserRole
from models.user import User
from models.shop_profile import ShopProfile
from werkzeug.security import generate_password_hash
import random


def create_roles():
    """Create roles"""
    session = Session()
    roles = [
        "Admin",
        "Manager",
        "Shopkeeper",
        "Staff",
        "User"
    ]
    
    created_roles = []
    try:
        for role_name in roles:
            role = session.query(UserRole).filter_by(name=role_name).first()
            if not role:
                role = UserRole(name=role_name)
                session.add(role)
                session.flush()
            created_roles.append(role)
        session.commit()
        print("Roles created successfully!")
        return created_roles
    except Exception as e:
        session.rollback()
        print(f"Error creating roles: {e}")
        return []
    finally:
        session.close()


def create_users(roles):
    """Create sample users"""
    session = Session()
    users = [
        {
            "username": "admin",
            "email": "admin@example.com",
            "password": generate_password_hash("admin123"),
            "phone": "0174444444",
            "role": "Admin"
        },
        {
            "username": "john_manager",
            "email": "john@example.com",
            "password": generate_password_hash("john123"),
            "phone": "0171111111",
            "role": "Manager"
        },
        {
            "username": "sarah_shop",
            "email": "sarah@example.com",
            "password": generate_password_hash("sarah123"),
            "phone": "0172222222",
            "role": "Shopkeeper"
        },
        {
            "username": "mike_staff",
            "email": "mike@example.com",
            "password": generate_password_hash("mike123"),
            "phone": "0173333333",
            "role": "Staff"
        },
        {
            "username": "lisa_user",
            "email": "lisa@example.com",
            "password": generate_password_hash("lisa123"),
            "phone": "0175555555",
            "role": "User"
        }
    ]
    
    created_users = []
    try:
        for user_data in users:
            user = session.query(User).filter_by(email=user_data["email"]).first()
            if not user:
                # Find role
                role = session.query(UserRole).filter_by(name=user_data["role"]).first()
                if role:
                    user = User(
                        username=user_data["username"],
                        email=user_data["email"],
                        password=generate_password_hash(user_data["password"]),
                        ptext=user_data["password"],
                        phone=user_data["phone"],
                        role_id=role.id
                    )
                    session.add(user)
                    session.flush()
                    created_users.append(user)
        
        session.commit()
        print("Users created successfully!")
        return created_users
    except Exception as e:
        session.rollback()
        print(f"Error creating users: {e}")
        return []
    finally:
        session.close()


def create_shops(users):
    """Create sample shops"""
    session = Session()
    
    # Sample shop names and locations
    shop_types = ["Clothing", "Electronics", "Food", "Books", "Jewelry", "Sports", "Toys"]
    shop_names = [f"{type} Shop" for type in shop_types]
    
    try:
        # Get shopkeeper users
        shopkeeper_role = session.query(UserRole).filter_by(name="Shopkeeper").first()
        if not shopkeeper_role:
            print("Shopkeeper role not found!")
            return
            
        shopkeepers = session.query(User).filter_by(role_id=shopkeeper_role.id).all()
        if not shopkeepers:
            shopkeepers = [users[0]]  # Use admin if no shopkeepers
        
        # Create shops
        for i, name in enumerate(shop_names):
            owner = random.choice(shopkeepers)
            floor = random.randint(1, 5)
            shop = ShopProfile(
                shopName=name,
                floorNo=str(floor),
                shopNo=f"{floor}0{random.randint(1, 9)}",
                address=f"Floor {floor}, Shop {random.randint(1, 20)}",
                owner_id=owner.id
            )
            session.add(shop)
        
        session.commit()
        print("Shops created successfully!")
    except Exception as e:
        session.rollback()
        print(f"Error creating shops: {e}")
    finally:
        session.close()


def run_all_seeders():
    """Run all seeders in the correct order"""
    print("Starting database seeding...")
    
    # First setup database
    setup_database()
    
    # Create roles
    roles = create_roles()
    if not roles:
        print("Failed to create roles. Stopping seeding process.")
        return
        
    # Create users
    users = create_users(roles)
    if not users:
        print("Failed to create users. Stopping seeding process.")
        return
        
    # Create shops
    create_shops(users)
    
    print("Database seeding completed!")
