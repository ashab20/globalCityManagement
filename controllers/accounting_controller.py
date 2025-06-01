from sqlalchemy.orm import Session
from datetime import date
from models.BankAccount import BankAccount
from sqlalchemy import text
import traceback
from models.account_journal import AccountJournal
from models.ledger_current import LedgerCurrent
from models.ledger_history import LedgerHistory
from decimal import Decimal
from datetime import datetime
from data.common_head_data import common_head_data as commonHeadData

class AccountingController:

    @staticmethod
    def manage_ledger_current(session: Session, head_id: int, amount: float, drcr_type: str):
        try:
            ledger = session.query(LedgerCurrent).filter_by(head_id=head_id).first()
            print("ledger",ledger)
            if not ledger:
                ledger = LedgerCurrent(head_id=head_id, amount=Decimal(str(amount)), drcr_type=drcr_type)
                session.add(ledger)
            else:
                if ledger.drcr_type == drcr_type:
                    ledger.amount += Decimal(str(amount))
                else:
                    ledger.amount -= Decimal(str(amount))

            session.flush()

            # Clear today's ledger history
            session.query(LedgerHistory).filter(LedgerHistory.ledger_date == date.today()).delete()

            # Re-insert all from ledger_current into ledger_history
            # all_ledgers = session.query(LedgerHistory).all()
            # print("all_ledgers",all_ledgers)
            # if all_ledgers:
            #     for entry in all_ledgers:
            #         history = LedgerHistory(
            #             head_id=entry.head_id,
            #             amount=entry.amount,
            #             drcr_type=entry.drcr_type,
            #             ledger_date=date.today()
            #         )
            #     session.add(history)
            #     session.commit()
        except Exception as e:
            traceback.print_exc()
            print(f"Error saving ledger current: {str(e)}")
            return 1

    @staticmethod
    def manage_transaction(session: Session, transaction_info: list):
        print("From controller",transaction_info)
        (
            operation_type, action_type, head_id, trans_ref_id, trans_date, amount,
            account_id, user, prev_jour_id, col_name, ref_number, drcr_type, remarks
        ) = transaction_info
        print("transaction_info",transaction_info)
        try:
            rtn = 0
            print("head_id from model", head_id,trans_ref_id)

            if action_type == "insert":
                if trans_ref_id != 0:
                    # check the col_name wise AccountJournal insertation
                    if col_name == "bill_info_id":
                        new_journal = AccountJournal(
                            head_id= head_id,
                            trans_date=trans_date,
                            amount=amount,
                            entry_by=user,
                            transaction_ref=ref_number,
                            drcr_type=drcr_type,
                            remarks=remarks,
                            bill_info_id=trans_ref_id
                        )
                    elif col_name == "bill_colct_id":
                        new_journal = AccountJournal(
                            head_id= head_id,
                            trans_date=trans_date,
                            amount=amount,
                            entry_by=user,
                            transaction_ref=ref_number,
                            drcr_type=drcr_type,
                            remarks=remarks,
                            bill_colct_id=trans_ref_id
                        )

                    elif col_name == "jrnlVocr_ref_id":
                        new_journal = AccountJournal(
                            head_id= head_id,
                            trans_date=trans_date,
                            amount=amount,
                            entry_by=user,
                            transaction_ref=ref_number,
                            drcr_type=drcr_type,
                            remarks=remarks,
                            jrnlVocr_ref_id=trans_ref_id
                        )
                    else:
                        new_journal = AccountJournal(
                            head_id= head_id,
                            trans_date=trans_date,
                            amount=amount,
                            entry_by=user,
                            transaction_ref=ref_number,
                            drcr_type=drcr_type,
                            remarks=remarks
                        )


                    setattr(new_journal, col_name, trans_ref_id)
                    session.add(new_journal)
                    session.flush()

                    AccountingController.manage_ledger_current(session, head_id, amount, drcr_type)

            return rtn
        except Exception as e:
            # get stack trace
            
            traceback.print_exc()

            print(f"Error saving transaction: {str(e)}")
            return 1
            
    
    @staticmethod
    def get_head_balance(session: Session, head_id: int):
        head_balance = session.query(LedgerCurrent).filter_by(head_id=head_id).first()
        return head_balance.amount
    
    @staticmethod
    def get_bank_head_id(session: Session, bank_name: str):
        bank_head = session.query(BankAccount).filter_by(bank_name=bank_name).first()
        return bank_head.head_id
    
    @staticmethod
    def getTransRefNumber(session: Session):
        sql = text('select IFNULL(MAX(transaction_ref),0)+1 AS rtnValue FROM account_journal')
        refNumber = session.execute(sql).scalar()
        return refNumber
    
    @staticmethod
    def get_trial_balance(session: Session, tb_date: str = None):
        trial_balance = []
        print("tb_date",tb_date)
        if not tb_date:
            # No date provided — use `ledger_current`
            sql = text("""
                SELECT acc_head_of_accounts.head_name, acc_head_of_accounts.id as ref_id,
                       ledger_current.amount, ledger_current.drcr_type, CURDATE() as ledger_date
                FROM ledger_current
                INNER JOIN acc_head_of_accounts ON acc_head_of_accounts.id = ledger_current.head_id
                ORDER BY acc_head_of_accounts.id
            """)
            result = session.execute(sql)
            print("result all",result.fetchall())
            trial_balance = result.fetchall()
        
        else:
            # A date was posted
            search_date = datetime.strptime(tb_date, "%Y-%m-%d").date()

            # Try to fetch from ledger_history for exact date
            sql = text("""
                SELECT acc_head_of_accounts.head_name, acc_head_of_accounts.id as ref_id,
                        ledger_history.amount, ledger_history.drcr_type, ledger_history.ledger_date
                FROM ledger_history
                INNER JOIN acc_head_of_accounts ON acc_head_of_accounts.id = ledger_history.head_id
                WHERE ledger_history.ledger_date = :search_date
                ORDER BY acc_head_of_accounts.id
            """)
            result = session.execute(sql, {"search_date": search_date})
            trial_balance = result.fetchall()

            # If no records found, fallback to last available ledger_dt
            if not trial_balance:
                last_date_sql = text("""
                    SELECT ledger_date FROM ledger_history
                    WHERE ledger_date < :search_date
                    GROUP BY ledger_date
                    ORDER BY ledger_date DESC
                    LIMIT 1
                """)
                last_date_result = session.execute(last_date_sql, {"search_date": search_date}).fetchone()
                if last_date_result:
                    last_ledger_date = last_date_result[0]
                    fallback_sql = text("""
                        SELECT acc_head_of_accounts.head_name, acc_head_of_accounts.id as ref_id,
                               ledger_history.amount, ledger_history.drcr_type, ledger_history.ledger_date
                        FROM ledger_history
                        INNER JOIN acc_head_of_accounts ON acc_head_of_accounts.id = ledger_history.head_id
                        WHERE ledger_history.ledger_date = :last_ledger_date
                        ORDER BY acc_head_of_accounts.id
                    """)
                    result = session.execute(fallback_sql, {"last_ledger_date": last_ledger_date})
                    trial_balance = result.fetchall()

        return trial_balance
	
    @staticmethod
    def get_ledger_balance(session: Session, head_id: int, frm_dt: str, to_dt: str):

        # check all arg is not null
        # print("frm_dt",frm_dt)
        # print("to_dt",to_dt)
        # print("head_id",head_id)
        try:
            sql = text("""SELECT CONCAT(DAY(trans_date),'/',MONTH(trans_date),'/',RIGHT(YEAR(trans_date),2)) AS trans_date,
			account_journal.remarks AS particulars,
			account_journal.transaction_ref,account_journal.amount,account_journal.drcr_type
			FROM account_journal 
			WHERE (trans_date between :frm_dt AND :to_dt) AND head_id=:head_id
            """)
            result = session.execute(sql, {"frm_dt": frm_dt, "to_dt": to_dt, "head_id": head_id})
            ledger_balance = result.fetchall()

            sqlPrevAmount = text("""select amount,drcr_type from ledger_history 
			where head_id=:head_id and ledger_date < :frm_dt order by ledger_date desc limit 1""")
            
            prev_amount_data = session.execute(sqlPrevAmount, {"frm_dt": frm_dt, "head_id": head_id}).fetchone()
            prev_amount = prev_amount_data[0] if prev_amount_data else 0
            prev_drcr_type = prev_amount_data[1] if prev_amount_data else ''

            for row in ledger_balance:
                if prev_drcr_type == 'dr':
                    prev_amount += row[3]
                else:
                    prev_amount -= row[3]

            return ledger_balance, prev_amount, prev_drcr_type
        except Exception as e:
            traceback.print_exc()
            print(f"Error getting ledger balance: {str(e)}")
            return 0

    @staticmethod
    def get_common_head_name_by_id(head_id: int):
        for head in commonHeadData:
            if head["head_id"] == head_id:
                return head["name"]
        return None
    
    @staticmethod
    def get_common_head_name(name: str):
        # search from commonHeadData and get all the cd type as array
        cd_type = []
        for head in commonHeadData:
            if head["name"] == name:
                cd_type.append(head)
        return cd_type

        
