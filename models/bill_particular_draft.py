from sqlalchemy import Column, Integer, String, DateTime, DECIMAL, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .base import Base
from utils.database import Session

class BillParticularDraft(Base):
    __tablename__ = 'bill_particular_draft'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    shop_id = Column(Integer, nullable=True)
    head_id = Column(Integer, nullable=True)
    bill_particular = Column(String(200), nullable=True)
    bill_qty = Column(DECIMAL(10,2), nullable=True)
    bill_unit = Column(String(20), nullable=True)
    bill_rate = Column(DECIMAL(10,2), nullable=True)
    sub_amount = Column(DECIMAL(10,2), nullable=True)
    bill_month = Column(Integer, nullable=True)
    bill_year = Column(Integer, nullable=True)
    vat = Column(DECIMAL(10,2), nullable=True,default=0)
    demand_charge = Column(DECIMAL(10,2), nullable=True,default=0)
    bill_type = Column(String(20), nullable=True,default="Bill",comment="Bill, Collection") # Bill, Collection
    
    
    @staticmethod
    def get_all_bill_particular_draft():
        session = Session()
        try:
            return session.query(BillParticularDraft).all()
        finally:
            session.close()
    
    @staticmethod
    def get_bill_particular_draft_by_id(id):
        session = Session()
        try:
            return session.query(BillParticularDraft).get(id)
        finally:
            session.close()

    @staticmethod
    def get_bill_particular_draft_by_shop_id(shop_id, bill_month, bill_year, session):
        # session = Session()
        try:
            return (
                session.query(BillParticularDraft)
                .filter_by(shop_id=shop_id, bill_month=bill_month, bill_year=bill_year)
                .all()
            )
        finally:
            print("Inserted")
            # session.close()

    @staticmethod
    def get_total_draft_amount(shop_id, bill_month, bill_year):
        session = Session()
        try:
            total = session.query(func.coalesce(func.sum(BillParticularDraft.sub_amount), 0)).filter_by(
                shop_id=shop_id,
                bill_month=bill_month,
                bill_year=bill_year
            ).scalar()
            return total
        finally:
            session.close()
                
                
    @staticmethod
    def add_bill_particular_draft(shop_id, head_id, bill_particular, bill_qty, bill_unit, bill_rate, sub_amount,bill_month,bill_year, vat=0, demand_charge=0):
        session = Session()
        try:
            draft = BillParticularDraft(
                shop_id=shop_id,
                head_id=head_id,
                bill_particular=bill_particular,
                bill_qty=bill_qty,
                bill_unit=bill_unit,
                bill_rate=bill_rate,
                sub_amount=sub_amount,
                bill_month=bill_month,
                bill_year=bill_year,
                vat=vat,
                demand_charge=demand_charge,
            )
            session.add(draft)
            session.commit()
            return draft
        except Exception as e:
            session.rollback()
            print(f"Error adding bill particular draft: {str(e)}")
            raise e
        finally:
            session.close()

    @staticmethod
    def clear_drafts(shop_id, bill_month, bill_year):
        session = Session()
        try:
            session.query(BillParticularDraft).filter_by(shop_id=shop_id, bill_month=bill_month, bill_year=bill_year).delete()
            session.commit()
        finally:
            session.close()
            
    @staticmethod
    def update_draft_by_field(id, field,value):
        session = Session()
        try:
            session.query(BillParticularDraft).filter_by(shop_id=shop_id).delete()
            session.commit()
        finally:
            session.close()
    
    # @staticmethod
    # def delete_bill_particular_draft_by_id(id):
    #     session = Session()
    #         try:
    #             draft = session.query(BillParticularDraft).filter_by(id=id).first()
    #             if draft:
    #                 session.delete(shop)
    #                 session.commit()
    #                 print("Particular draft deleted successfully.")
    #             else:
    #                 print("draft with ID not found.")
    #         finally:
    #             session.close()
    
    @staticmethod
    def delete_bill_particular_draft_by_id(id):
        session = Session()
        draft = session.query(BillParticularDraft).filter_by(id=id).first()
        if draft:
            session.delete(draft)
            session.commit()
            print(f"Draft deleted successfully.")
        else:
            print(f"Draft  not found.")
            
    @staticmethod
    def get_bill_particular_draft_by_bill_draft_id(bill_draft_id):
        session = Session()
        try:
            return session.query(BillParticularDraft).filter_by(bill_draft_id=bill_draft_id).all()
        finally:
            session.close()

    @staticmethod
    def delete_bill_particular_draft_by_bill_draft_id(bill_draft_id):
        session = Session()
        try:
            session.query(BillParticularDraft).filter_by(bill_draft_id=bill_draft_id).delete()
            session.commit()
        except Exception as e:
            session.rollback()
            print(f"Error deleting bill particular draft: {str(e)}")
            raise e
        finally:
            session.close()
            