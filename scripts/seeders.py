from utils.database import Session, setup_database
from models.user_role import UserRole
from models.user import User
from models.shop_profile import ShopProfile
from models.category import Category
from models.unit import Unit
from werkzeug.security import generate_password_hash
import random


def create_roles():
    """Create roles"""
    session = Session()
    roles = [
        "Super Admin",
        "IT Admin",
        "Account Manager",
        "Executives",
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


def create_units():
    """Create sample units"""
    session = Session()
    units = [
        "Piece", "Kg", "Gram", "Liter", "Meter", "Centimeter", "Inch", "Foot", 
        "Yard", "Square Meter", "Square Foot", "Cubic Meter", "Dozen", "Pair",
        "Set", "Pack", "Box", "Bottle", "Can", "Bag", "Roll", "Sheet", "Unit"
    ]
    
    created_units = []
    try:
        for unit_name in units:
            unit = session.query(Unit).filter_by(unit_name=unit_name).first()
            if not unit:
                unit = Unit(
                    unit_name=unit_name,
                    status=1
                )
                session.add(unit)
                session.flush()
            created_units.append(unit)
        
        session.commit()
        print("Units created successfully!")
        return created_units
    except Exception as e:
        session.rollback()
        print(f"Error creating units: {e}")
        return []
    finally:
        session.close()


def create_categories():
    """Create sample categories"""
    session = Session()
    categories = [
        {"name": "Electronics", "description": "Electronic devices and gadgets"},
        {"name": "Clothing", "description": "Apparel and fashion items"},
        {"name": "Food & Beverages", "description": "Food and drink products"},
        {"name": "Books", "description": "Books and publications"},
        {"name": "Home & Garden", "description": "Home improvement and garden items"},
        {"name": "Sports & Outdoors", "description": "Sports equipment and outdoor gear"},
        {"name": "Toys & Games", "description": "Toys and entertainment items"},
        {"name": "Health & Beauty", "description": "Health and beauty products"},
        {"name": "Automotive", "description": "Automotive parts and accessories"},
        {"name": "Office Supplies", "description": "Office and stationery items"}
    ]
    
    created_categories = []
    try:
        for cat_data in categories:
            category = session.query(Category).filter_by(name=cat_data["name"]).first()
            if not category:
                category = Category(
                    name=cat_data["name"],
                    description=cat_data["description"],
                    status=1
                )
                session.add(category)
                session.flush()
            created_categories.append(category)
        
        session.commit()
        print("Categories created successfully!")
        return created_categories
    except Exception as e:
        session.rollback()
        print(f"Error creating categories: {e}")
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
        
    # Create units
    units = create_units()
    if not units:
        print("Failed to create units. Stopping seeding process.")
        return
        
    # Create categories
    categories = create_categories()
    if not categories:
        print("Failed to create categories. Stopping seeding process.")
        return
        
    # Create users
    users = create_users(roles)
    if not users:
        print("Failed to create users. Stopping seeding process.")
        return
        
    # Create shops
    create_shops(users)
    
    print("Database seeding completed!")
