from utils.database import Session, setup_database
from models.user_role import UserRole
from models.user import User
from models.shop_profile import ShopProfile
from models.category import Category
from models.unit import Unit
from models.url_top_menu import UrlTopMenu
from models.url_sub_menu import UrlSubMenu
from werkzeug.security import generate_password_hash
import random
from datetime import datetime


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


def seed_users():
    """Seed users and roles"""
    session = Session()
    
    try:
        # Create roles if they don't exist
        admin_role = session.query(UserRole).filter_by(name='admin').first()
        if not admin_role:
            admin_role = UserRole(name='admin')
            session.add(admin_role)
            session.flush()  # Get the ID
        
        manager_role = session.query(UserRole).filter_by(name='manager').first()
        if not manager_role:
            manager_role = UserRole(name='manager')
            session.add(manager_role)
            session.flush()
        
        staff_role = session.query(UserRole).filter_by(name='staff').first()
        if not staff_role:
            staff_role = UserRole(name='staff')
            session.add(staff_role)
            session.flush()
        
        # Create admin user if it doesn't exist
        admin_user = session.query(User).filter_by(login_id='admin').first()
        if not admin_user:
            admin_user = User(
                login_id='admin',
                usr_full_name='Administrator',
                email='admin@example.com',
                phone='1234567890',
                password=generate_password_hash('admin123'),
                role_id=admin_role.id,
                active_status=1,
                is_active=True
            )
            session.add(admin_user)
        
        session.commit()
        print("Users and roles seeded successfully!")
        
    except Exception as e:
        print(f"Error seeding users: {e}")
        session.rollback()
    finally:
        session.close()


def seed_categories():
    """Seed product categories"""
    session = Session()
    
    try:
        categories = [
            {'name': 'Electronics', 'status': 1},
            {'name': 'Clothing', 'status': 1},
            {'name': 'Food & Beverages', 'status': 1},
            {'name': 'Books', 'status': 1},
            {'name': 'Home & Garden', 'status': 1}
        ]
        
        for cat_data in categories:
            existing = session.query(Category).filter_by(name=cat_data['name']).first()
            if not existing:
                category = Category(**cat_data)
                session.add(category)
        
        session.commit()
        print("Categories seeded successfully!")
        
    except Exception as e:
        print(f"Error seeding categories: {e}")
        session.rollback()
    finally:
        session.close()


def seed_units():
    """Seed product units"""
    session = Session()
    
    try:
        units = [
            {'unit_name': 'Kg', 'status': 1},
            {'unit_name': 'Pieces', 'status': 1},
            {'unit_name': 'Liters', 'status': 1},
            {'unit_name': 'Meters', 'status': 1},
            {'unit_name': 'Boxes', 'status': 1}
        ]
        
        for unit_data in units:
            existing = session.query(Unit).filter_by(unit_name=unit_data['unit_name']).first()
            if not existing:
                unit = Unit(**unit_data)
                session.add(unit)
        
        session.commit()
        print("Units seeded successfully!")
        
    except Exception as e:
        print(f"Error seeding units: {e}")
        session.rollback()
    finally:
        session.close()


def seed_menus():
    """Seed menu structure"""
    session = Session()
    
    try:
        # Create top menus
        top_menus = [
            {'menu_name': 'User Management', 'menu_order': 1, 'icon': 'users.png'},
            {'menu_name': 'Shop Management', 'menu_order': 2, 'icon': 'shop.png'},
            {'menu_name': 'Inventory', 'menu_order': 3, 'icon': 'inventory.png'},
            {'menu_name': 'Accounting', 'menu_order': 4, 'icon': 'accounting.png'},
            {'menu_name': 'Reports', 'menu_order': 5, 'icon': 'reports.png'}
        ]
        
        for menu_data in top_menus:
            existing = session.query(UrlTopMenu).filter_by(menu_name=menu_data['menu_name']).first()
            if not existing:
                top_menu = UrlTopMenu(**menu_data)
                session.add(top_menu)
                session.flush()  # Get the ID
                
                # Add submenus based on top menu
                if menu_data['menu_name'] == 'User Management':
                    submenus = [
                        {'top_menu_id': top_menu.id, 'sub_menu_order': 1, 'sub_menu_name': 'Create User', 'command_name': 'create_user'},
                        {'top_menu_id': top_menu.id, 'sub_menu_order': 2, 'sub_menu_name': 'User List', 'command_name': 'list_users'},
                        {'top_menu_id': top_menu.id, 'sub_menu_order': 3, 'sub_menu_name': 'Create Role', 'command_name': 'create_role'},
                        {'top_menu_id': top_menu.id, 'sub_menu_order': 4, 'sub_menu_name': 'Role List', 'command_name': 'role_list'}
                    ]
                elif menu_data['menu_name'] == 'Shop Management':
                    submenus = [
                        {'top_menu_id': top_menu.id, 'sub_menu_order': 1, 'sub_menu_name': 'Create Shop', 'command_name': 'create_shop'},
                        {'top_menu_id': top_menu.id, 'sub_menu_order': 2, 'sub_menu_name': 'Shop List', 'command_name': 'list_shops'},
                        {'top_menu_id': top_menu.id, 'sub_menu_order': 3, 'sub_menu_name': 'Create Shop Owner', 'command_name': 'create_shop_owner'},
                        {'top_menu_id': top_menu.id, 'sub_menu_order': 4, 'sub_menu_name': 'Shop Owner List', 'command_name': 'list_shop_owners'}
                    ]
                elif menu_data['menu_name'] == 'Inventory':
                    submenus = [
                        {'top_menu_id': top_menu.id, 'sub_menu_order': 1, 'sub_menu_name': 'Product Category', 'command_name': 'product_category'},
                        {'top_menu_id': top_menu.id, 'sub_menu_order': 2, 'sub_menu_name': 'Category List', 'command_name': 'product_category_list'},
                        {'top_menu_id': top_menu.id, 'sub_menu_order': 3, 'sub_menu_name': 'Create Product', 'command_name': 'create_product'},
                        {'top_menu_id': top_menu.id, 'sub_menu_order': 4, 'sub_menu_name': 'Product List', 'command_name': 'product_details_list'},
                        {'top_menu_id': top_menu.id, 'sub_menu_order': 5, 'sub_menu_name': 'Create Unit', 'command_name': 'create_unit'},
                        {'top_menu_id': top_menu.id, 'sub_menu_order': 6, 'sub_menu_name': 'Unit List', 'command_name': 'unit_list'}
                    ]
                elif menu_data['menu_name'] == 'Accounting':
                    submenus = [
                        {'top_menu_id': top_menu.id, 'sub_menu_order': 1, 'sub_menu_name': 'Trial Balance', 'command_name': 'trial_balance'},
                        {'top_menu_id': top_menu.id, 'sub_menu_order': 2, 'sub_menu_name': 'Ledger Balance', 'command_name': 'ledger_balance'},
                        {'top_menu_id': top_menu.id, 'sub_menu_order': 3, 'sub_menu_name': 'Balance Sheet', 'command_name': 'balance_sheet'},
                        {'top_menu_id': top_menu.id, 'sub_menu_order': 4, 'sub_menu_name': 'Profit Loss', 'command_name': 'profit_loss'}
                    ]
                elif menu_data['menu_name'] == 'Reports':
                    submenus = [
                        {'top_menu_id': top_menu.id, 'sub_menu_order': 1, 'sub_menu_name': 'Shop Owner Due Report', 'command_name': 'shop_owner_due_report'},
                        {'top_menu_id': top_menu.id, 'sub_menu_order': 2, 'sub_menu_name': 'Shop Renter Due Report', 'command_name': 'shop_renter_due_report'}
                    ]
                else:
                    submenus = []
                
                for submenu_data in submenus:
                    existing_sub = session.query(UrlSubMenu).filter_by(
                        top_menu_id=submenu_data['top_menu_id'],
                        sub_menu_name=submenu_data['sub_menu_name']
                    ).first()
                    if not existing_sub:
                        submenu = UrlSubMenu(**submenu_data)
                        session.add(submenu)
        
        session.commit()
        print("Menus seeded successfully!")
        
    except Exception as e:
        print(f"Error seeding menus: {e}")
        session.rollback()
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
    
    seed_users()
    seed_categories()
    seed_units()
    seed_menus()
    
    print("Database seeding completed!")


if __name__ == "__main__":
    run_all_seeders()
