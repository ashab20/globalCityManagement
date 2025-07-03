#!/usr/bin/env python3

from utils.database import Session, setup_database
from models.url_top_menu import UrlTopMenu
from models.url_sub_menu import UrlSubMenu
from models.user import User
from models.user_role import UserRole

def check_database():
    """Check database tables and data"""
    print("Checking database...")
    
    try:
        # Setup database
        setup_database()
        
        session = Session()
        
        # Check top menus
        print("\n=== Top Menus ===")
        top_menus = session.query(UrlTopMenu).all()
        print(f"Found {len(top_menus)} top menus:")
        for menu in top_menus:
            print(f"  - {menu.menu_name} (ID: {menu.id}, Order: {menu.menu_order})")
        
        # Check sub menus
        print("\n=== Sub Menus ===")
        sub_menus = session.query(UrlSubMenu).all()
        print(f"Found {len(sub_menus)} sub menus:")
        for submenu in sub_menus:
            print(f"  - {submenu.sub_menu_name} (Top Menu ID: {submenu.top_menu_id}, Command: {submenu.command_name})")
        
        # Check users
        print("\n=== Users ===")
        users = session.query(User).all()
        print(f"Found {len(users)} users:")
        for user in users:
            print(f"  - {user.login_id} ({user.usr_full_name})")
        
        # Check roles
        print("\n=== Roles ===")
        roles = session.query(UserRole).all()
        print(f"Found {len(roles)} roles:")
        for role in roles:
            print(f"  - {role.name} (ID: {role.id})")
        
        session.close()
        
    except Exception as e:
        print(f"Error checking database: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_database() 