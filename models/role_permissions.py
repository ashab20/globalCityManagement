from sqlalchemy import Column, Integer, String, JSON
from sqlalchemy.ext.declarative import declarative_base

from .base import Base

class RolePermission(Base):
    """
    Model to manage role-based permissions
    Permissions are stored as a JSON dictionary with keys representing 
    different menu items and values representing allowed actions
    """
    __tablename__ = 'role_permissions'

    id = Column(Integer, primary_key=True)
    role_name = Column(String(50), unique=True, nullable=False)
    permissions = Column(JSON, nullable=False)

    @classmethod
    def get_default_permissions(cls):
        """
        Default permission templates for different roles
        """
        return {
            'admin': {
                'user_management': ['create', 'read', 'update', 'delete'],
                'shop_management': ['create', 'read', 'update', 'delete'],
                'shop_owner_management': ['create', 'read', 'update', 'delete'],
                'shop_renter_management': ['create', 'read', 'update', 'delete'],
                'shop_allocation_management': ['create', 'read', 'update', 'delete']
            },
            'manager': {
                'user_management': ['read'],
                'shop_management': ['create', 'read', 'update'],
                'shop_owner_management': ['create', 'read', 'update'],
                'shop_renter_management': ['create', 'read', 'update'],
                'shop_allocation_management': ['read']
            },
            'staff': {
                'user_management': [],
                'shop_management': ['read'],
                'shop_owner_management': ['read'],
                'shop_renter_management': ['read'],
                'shop_allocation_management': ['read']
            }
        }

    def has_permission(self, module, action):
        """
        Check if the role has permission for a specific module and action
        
        :param module: Module name (e.g., 'user_management')
        :param action: Action to check (e.g., 'create', 'read')
        :return: Boolean indicating permission
        """
        if not self.permissions:
            return False
        
        module_permissions = self.permissions.get(module, [])
        return action in module_permissions
