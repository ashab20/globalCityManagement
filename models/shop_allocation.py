from sqlalchemy import Column, Integer, DateTime, ForeignKey,and_,text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from models.shop_profile import ShopProfile
from models.shop_renter_profile import ShopRenterProfile
from .base import Base

class ShopAllocation(Base):
    __tablename__ = 'shop_allocation'

    id = Column(Integer, primary_key=True, autoincrement=True)
    shop_profile_id = Column(Integer, ForeignKey('shop_profile.id'), nullable=True)
    renter_profile_id = Column(Integer, ForeignKey('shop_renter_profile.id'), nullable=True)
    from_year = Column(Integer, nullable=True)
    from_month = Column(Integer, nullable=True)
    to_year = Column(Integer, nullable=True)
    to_month = Column(Integer, nullable=True)
    close_status = Column(Integer, default=0, nullable=True)  # 0=active, 1=close
    created_by = Column(Integer, ForeignKey('users.id'), nullable=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=True)
    update_by = Column(Integer, ForeignKey('users.id'), nullable=True)
    update_at = Column(DateTime, onupdate=func.now(), nullable=True)

    # Relationships
    # shop_profile = relationship("ShopProfile", back_populates="allocations")
    # renter_profile = relationship("ShopRenterProfile", back_populates="allocations")
    # creator = relationship("User", foreign_keys=[created_by])
    # updater = relationship("User", foreign_keys=[update_by])

    def __repr__(self):
        return f"<ShopAllocation(id={self.id}, shop_profile_id={self.shop_profile_id}, renter_profile_id={self.renter_profile_id})>"

    @staticmethod
    def get_renter_profile_by_shop_id(session, shop_id: int, year: int, month: int):
        # Convert year and month to a comparable integer (e.g., 202506 for June 2025)
        target = year * 100 + month

        # Convert allocation period to comparable integers for range checking
        from_expr = year * 100 + month
        to_expr = year * 100 + month

        # shop_allocation = (
        #     session.query(ShopAllocation)
        #     .filter(
        #         ShopAllocation.shop_profile_id == shop_id,
        #         ShopAllocation.close_status == 0,
        #         and_(from_expr <= target, to_expr >= target)
        #     )
        #     .join(ShopProfile)
        #     .join(ShopRenterProfile)
        #     .first()
        # )

        print('SHOP PROFILE:',shop_id, year, month)
        query = text("""
            SELECT sa.renter_profile_id
            FROM shop_allocation sa
            LEFT JOIN shop_profile sp ON sa.shop_profile_id = sp.id
            LEFT JOIN shop_renter_profile srp ON sa.renter_profile_id = srp.id
            WHERE sp.id = 5
            AND sa.close_status = 0
            AND (sa.from_year * 100 + sa.from_month <= :target)
            AND (sa.to_year * 100 + sa.to_month >= :target)
        """)

        # SELECT sa.renter_profile_id
        #     FROM shop_allocation sa
        #     JOIN shop_profile sp ON sa.shop_profile_id = sp.id
        #     JOIN shop_renter_profile srp ON sa.renter_profile_id = srp.id
        #     WHERE sp.id = 5
        #     AND sa.close_status = 0
        #     AND (sa.from_year * 100 + sa.from_month <= 202507)
        #     AND (sa.to_year * 100 + sa.to_month >= 202507)

        print('QUERY:',target,from_expr, to_expr)

        result = session.execute(query, {"shop_id": shop_id, "target": target})
        shop_allocations = result.fetchone()
        print('SHOP ALLOCATIONS:',shop_allocations)

        return shop_allocations or None