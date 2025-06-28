import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from models.bill_info import BillInfo
from sqlalchemy import text
from models.bill_particular import BillParticular
from utils.database import Session
from ttkbootstrap.dialogs import Messagebox
from datetime import datetime, date
from models.shop_profile import ShopProfile
from models.UtilitySetting import UtilitySetting
from models.bill_particular_draft import BillParticularDraft
from models.shop_allocation import ShopAllocation
from functools import partial
import traceback
from controllers.accounting_controller import AccountingController
from utils.session_scope import session_scope
from decimal import Decimal

class CreateBillInfoView(ttk.Frame):
    def __init__(self, parent, existing_bill_info=None):
        super().__init__(parent, padding=10)
        self.parent = parent
        self.existing_bill_info = existing_bill_info
        self.bill_particulars = []
        
        # Month mapping
        self.month_names = [
            "January", "February", "March", "April", "May", "June",
            "July", "August", "September", "October", "November", "December"
        ]
        self.month_to_number = {name: i+1 for i, name in enumerate(self.month_names)}
        self.number_to_month = {i+1: name for i, name in enumerate(self.month_names)}
        
        # Configure styles
        style = ttk.Style()
        style.configure("TFrame", background="white")
        style.configure("TLabel", background="white")
        style.configure("TButton", font=("Helvetica", 10))
        
        # Create main container
        self.main_container = ttk.Frame(self)
        self.main_container.pack(fill="both", expand=True)
        
        # Create canvas and scrollbar
        self.canvas = ttk.Canvas(self.main_container)
        self.scrollbar = ttk.Scrollbar(self.main_container, orient="vertical", command=self.canvas.yview)
        
        # Create scrollable frame
        self.scrollable_frame = ttk.Frame(self.canvas)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas_frame = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        self.scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        
        self.canvas.bind('<Configure>', self._configure_canvas)
        self.bind_mouse_wheel()
        self.create_form()

    def _configure_canvas(self, event):
        self.canvas.itemconfig(self.canvas_frame, width=event.width)
        required_height = self.scrollable_frame.winfo_reqheight()
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        self.canvas.configure(width=event.width, height=min(required_height, 600))

    def bind_mouse_wheel(self):
        def _on_mousewheel(event):
            self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        self.canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        def _bound_to_mousewheel(event):
            self.canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        def _unbound_to_mousewheel(event):
            self.canvas.unbind_all("<MouseWheel>")
        
        self.scrollable_frame.bind("<Enter>", _bound_to_mousewheel)
        self.scrollable_frame.bind("<Leave>", _unbound_to_mousewheel)

    def load_shops(self):
        try:
            session = Session()
            shops = session.query(ShopProfile).filter_by(active_status=1).all()
            shop_items = [f"{shop.shop_name} - {shop.shop_no}" for shop in shops]
            self.shop_combobox['values'] = shop_items
            self.shops_dict = {f"{shop.shop_name} - {shop.shop_no}": shop.id for shop in shops}
            session.close()
        except Exception as e:
            Messagebox.show_error(message=f"Error loading shops: {str(e)}", title="Error", parent=self)

    def create_form(self):
        form_frame = ttk.Frame(self.scrollable_frame, padding=(20, 10))
        form_frame.pack(fill="both", expand=True)

        title_label = ttk.Label(
            form_frame, 
            text="Create Bill", 
            font=("Helvetica", 16, "bold"), 
            bootstyle="primary"
        )
        title_label.pack(pady=(0, 20), anchor="center")

        columns_frame = ttk.Frame(form_frame)
        columns_frame.pack(fill="x", expand=True)
        
        left_frame = ttk.Frame(columns_frame)
        left_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        right_frame = ttk.Frame(columns_frame)
        right_frame.pack(side="left", fill="both", expand=True, padx=(10, 0))

        label_style = {"bootstyle": "primary", "font": ("Helvetica", 10)}
        entry_style = {"font": ("Helvetica", 10)}

        # Left Column
        ttk.Label(left_frame, text="Shop:", **label_style).pack(anchor="w")
        self.shop_combobox = ttk.Combobox(left_frame, state="readonly", **entry_style)
        self.shop_combobox.pack(fill="x", pady=(0, 10))
        self.shop_combobox.bind('<<ComboboxSelected>>', self.on_shop_change)
        self.load_shops()

        # previus bill dues
        ttk.Label(left_frame, text="Previous Bill Dues:", **label_style).pack(anchor="w")
        self.prev_bill_dues_entry = ttk.Entry(left_frame, **entry_style)
        self.prev_bill_dues_entry.pack(fill="x", pady=(0, 10))

        ttk.Label(left_frame, text="Bill Year:", **label_style).pack(anchor="w")
        self.bill_year_entry = ttk.Entry(left_frame, **entry_style)
        self.bill_year_entry.pack(fill="x", pady=(0, 10))
        self.bill_year_entry.insert(0, datetime.now().year)

        ttk.Label(left_frame, text="Bill Month:", **label_style).pack(anchor="w")
        self.bill_month_combobox = ttk.Combobox(
            left_frame,
            values=[
                "January", "February", "March", "April", "May", "June",
                "July", "August", "September", "October", "November", "December"
            ],
            state="readonly",
            **entry_style
        )
        self.bill_month_combobox.bind('<<ComboboxSelected>>', self.on_bill_month_change)
        self.bill_month_combobox.pack(fill="x", pady=(0, 10))
        
        # Set current month as default
        current_month = datetime.now().month
        self.bill_month_combobox.set([
            "January", "February", "March", "April", "May", "June",
            "July", "August", "September", "October", "November", "December"
        ][current_month - 1])

        ttk.Label(left_frame, text="Bill Date:", **label_style).pack(anchor="w")
        self.bill_date_entry = ttk.DateEntry(left_frame, dateformat="%Y-%m-%d")
        self.bill_date_entry.entry.configure(font=("Helvetica", 10))
        self.bill_date_entry.pack(fill="x", pady=(0, 10))

        ttk.Label(left_frame, text="Last Pay Date:", **label_style).pack(anchor="w")
        self.last_pay_date_entry = ttk.DateEntry(left_frame, dateformat="%Y-%m-%d")
        self.last_pay_date_entry.entry.configure(font=("Helvetica", 10))
        self.last_pay_date_entry.pack(fill="x", pady=(0, 10))

        # Right Column
        ttk.Label(right_frame, text="Electricity Opening Unit:", **label_style).pack(anchor="w")
        self.elect_op_unit_entry = ttk.Entry(right_frame, **entry_style)
        self.elect_op_unit_entry.pack(fill="x", pady=(0, 10))

        ttk.Label(right_frame, text="Electricity Closing Unit:", **label_style).pack(anchor="w")
        self.elect_closing_unit_entry = ttk.Entry(right_frame, **entry_style)
        self.elect_closing_unit_entry.pack(fill="x", pady=(0, 10))

        ttk.Label(right_frame, text="Gas Opening Unit:", **label_style).pack(anchor="w")
        self.gas_op_unit_entry = ttk.Entry(right_frame, **entry_style)
        self.gas_op_unit_entry.pack(fill="x", pady=(0, 10))

        ttk.Label(right_frame, text="Gas Closing Unit:", **label_style).pack(anchor="w")
        self.gas_closing_unit_entry = ttk.Entry(right_frame, **entry_style)
        self.gas_closing_unit_entry.pack(fill="x", pady=(0, 10))

        ttk.Label(right_frame, text="WASA Opening Unit:", **label_style).pack(anchor="w")
        self.wasa_op_unit_entry = ttk.Entry(right_frame, **entry_style)
        self.wasa_op_unit_entry.pack(fill="x", pady=(0, 10))

        ttk.Label(right_frame, text="WASA Closing Unit:", **label_style).pack(anchor="w")
        self.wasa_closing_unit_entry = ttk.Entry(right_frame, **entry_style)
        self.wasa_closing_unit_entry.pack(fill="x", pady=(0, 10))
        
        # self.wasa_closing_unit_entry.bind("<FocusOut>", print("wasa closing:"))
        
        if self.existing_bill_info:
            # Get shop name from related ShopProfile
            shop = self.existing_bill_info.shop  # Assuming relationship exists
            self.shop_combobox.set(f"{shop.shop_name} - {shop.shop_no}")
            
            
            self.bill_year_entry.insert(0, self.existing_bill_info.bill_year)
            self.bill_month_combobox.set(self.existing_bill_info.bill_month)
            self.bill_date_entry.set_date(self.existing_bill_info.bill_date)
            self.last_pay_date_entry.set_date(self.existing_bill_info.last_pay_date)
            
            self.elect_op_unit_entry.insert(0, self.existing_bill_info.elect_op_unit)
            self.elect_closing_unit_entry.insert(0, self.existing_bill_info.elect_closing_unit)
            self.gas_op_unit_entry.insert(0, self.existing_bill_info.gas_op_unit)
            self.gas_closing_unit_entry.insert(0, self.existing_bill_info.gas_closing_unit)
            self.wasa_op_unit_entry.insert(0, self.existing_bill_info.wasa_op_unit)
            self.wasa_closing_unit_entry.insert(0, self.existing_bill_info.wasa_closing_unit)
            
            
             # Load existing bill particulars
            if self.existing_bill_info:
                index = 0
            # Directly use the already-loaded particulars
                for particular in self.existing_bill_info.particulars:
                    self.add_particular_row(
                        draft_id=particular.id,
                        particular=particular.bill_particular,
                        qty=str(particular.bill_qty),
                        unit=particular.bill_unit,
                        rate=str(particular.bill_rate)
                    )


        self.show_shop_info_button = ttk.Button(
            form_frame,
            text="Show Bill Information",
            command=self.show_shop_info,
            bootstyle="info",
            width=20
        )
        self.show_shop_info_button.pack(pady=20)

        particulars_frame = ttk.LabelFrame(form_frame, text="Bill Particulars", padding=10)
        particulars_frame.pack(fill="x", expand=True, pady=20)

        headers_frame = ttk.Frame(particulars_frame)
        headers_frame.pack(fill="x", pady=(0, 5))

        headers = ["Particular", "Qty", "Unit", "Rate", "Amount", "Action"]
        column_weights = [3, 1, 1, 1, 1, 0]

        headers_frame.columnconfigure(0, weight=3)
        headers_frame.columnconfigure(1, weight=1)
        headers_frame.columnconfigure(2, weight=1)
        headers_frame.columnconfigure(3, weight=1)
        headers_frame.columnconfigure(4, weight=1)
        headers_frame.columnconfigure(5, weight=0)

        for col, (header, weight) in enumerate(zip(headers, column_weights)):
            ttk.Label(
                headers_frame,
                text=header,
                font=("Helvetica", 10, "bold"),
                bootstyle="primary"
            ).grid(row=0, column=col, sticky="ew", padx=2)

        self.particulars_container = ttk.Frame(particulars_frame)
        self.particulars_container.pack(fill="x", expand=True)

        ttk.Button(
            particulars_frame,
            text="Add Particular",
            command=self.add_particular_row,
            bootstyle="primary-outline"
        ).pack(pady=10)

        total_frame = ttk.Frame(form_frame)
        total_frame.pack(fill="x", pady=10)
        
        ttk.Label(
            total_frame,
            text="Total Amount:",
            font=("Helvetica", 12, "bold"),
            bootstyle="primary"
        ).pack(side="left")
        
 
        self.total_amount_var = ttk.StringVar(value="0.00")
        ttk.Label(
            total_frame,
            textvariable=self.total_amount_var,
            font=("Helvetica", 12, "bold"),
            bootstyle="primary"
        ).pack(side="right")

        self.save_button = ttk.Button(
            form_frame,
            text="Generate Bill",
            command=self.save_bill_info,
            bootstyle="warning",
            width=20
        )
        self.save_button.pack(pady=20)

    def get_month_number(self, month_name):
        """Convert month name to number (1-12)"""
        return self.month_to_number.get(month_name, 1)

    def get_month_name(self, month_number):
        """Convert month number (1-12) to name"""
        return self.number_to_month.get(month_number, "January")

    def on_bill_month_change(self, event=None):
        """Handle bill month selection change"""
        try:
            # Get selected shop
            shop_selection = self.shop_combobox.get()
            if not shop_selection:
                return

            shop_id = self.shops_dict.get(shop_selection)
            if not shop_id:
                return

            # Get current month and year
            current_month = self.get_month_number(self.bill_month_combobox.get())
            current_year = int(self.bill_year_entry.get())

            # Get last bill info if exists
            session = Session()
            last_bill = session.query(BillInfo).filter_by(
                shop_id=shop_id,
                bill_year=current_year,
                bill_month=current_month-1 if current_month > 1 else 12
            ).first()

            if last_bill:
                # Set closing units as opening units for current bill
                self.elect_op_unit_entry.delete(0, 'end')
                self.elect_op_unit_entry.insert(0, str(last_bill.elect_closing_unit or 0))
                
                self.gas_op_unit_entry.delete(0, 'end')
                self.gas_op_unit_entry.insert(0, str(last_bill.gas_closing_unit or 0))
                
                self.wasa_op_unit_entry.delete(0, 'end')
                self.wasa_op_unit_entry.insert(0, str(last_bill.wasa_closing_unit or 0))

            # Clear any existing particulars
            for child in self.particulars_container.winfo_children():
                child.destroy()
            self.total_amount_var.set("0.00")

            # Load any existing drafts for this shop and month/year
            # self.display_draft_particulars(shop_id)

        except Exception as e:
            print(f"Error updating month info: {str(e)}")
            Messagebox.show_error(f"Error updating month info: {str(e)}", "Error", parent=self)
        finally:
            session.close()

    def on_shop_change(self, event=None):
        try:
            # Get selected shop
            shop_selection = self.shop_combobox.get()
            if not shop_selection:
                return

            shop_id = self.shops_dict.get(shop_selection)
            if not shop_id:
                Messagebox.show_error("Invalid shop selection", "Error", parent=self)
                return

            # Get shop info
            session = Session()
            shop_info = session.query(ShopProfile).filter_by(id=shop_id).first()
            # print(f"shop_info: {shop_info}")
            
            if shop_info:
                # Update form fields with shop data

                # check preform data
                print(f"bill_year: {self.bill_year_entry.get()}")
                print(f"bill_month: {self.bill_month_combobox.get()}")
                # collect previus data from bill info
                sql = text("""SELECT * FROM bill_info
                WHERE shop_id=:shop_id
                ORDER BY id DESC LIMIT 1
                """)
                result = session.execute(sql, {"shop_id": shop_id})
                prev_bill_info = result.fetchone()
                
                if prev_bill_info:
                    # Set closing units as opening units for current bill
                    self.elect_op_unit_entry.delete(0, 'end')
                    self.elect_op_unit_entry.insert(0, str(prev_bill_info.elect_closing_unit or 0))

                    self.gas_op_unit_entry.delete(0, 'end')
                    self.gas_op_unit_entry.insert(0, str(prev_bill_info.gas_closing_unit or 0))

                    self.wasa_op_unit_entry.delete(0, 'end')
                    self.wasa_op_unit_entry.insert(0, str(prev_bill_info.wasa_closing_unit or 0))

                    bill_year = prev_bill_info.bill_year + 1 if prev_bill_info.bill_month == 12 else prev_bill_info.bill_year
                    bill_month = prev_bill_info.bill_month + 1  if prev_bill_info.bill_month < 12 else 1

                    # set bill month and year
                    self.bill_month_combobox.set(self.get_month_name(bill_month))
                    self.bill_year_entry.delete(0, 'end')
                    self.bill_year_entry.insert(0, bill_year)
                    # print(f"prev_bill_info.bill_date: {datetime.strptime(prev_bill_info.bill_date, "%Y-%m-%d")}")
                    # if prev_bill_info.bill_date:
                    #     self.last_pay_date_entry.setvar(datetime.strptime(prev_bill_info.bill_date, "%Y-%m-%d"))



                # clear previus bill dues
                self.prev_bill_dues_entry.delete(0, 'end')
                # previus bill dues

                sql = text("""SELECT IFNULL(SUM(prev_due),0)  as due  FROM bill_info
                WHERE bill_info.shop_id=:shop_id
                """)
                result = session.execute(sql, {"shop_id": shop_id})
                prev_bill_dues = result.fetchone()
                if prev_bill_dues:
                    self.prev_bill_dues_entry.insert(0, f"{prev_bill_dues.due:.2f}")

                # print(f"prev_bill_info: {prev_bill_info}")
                    

        except Exception as e:
            print(f"Error updating shop info: {str(e)}")
            Messagebox.show_error(f"Error updating shop info: {str(e)}", "Error", parent=self)
        finally:
            session.close()

    def handle_update_particular_draft_raw(self, draft_id="", particular="", qty="", unit="", rate="", subtotal="0.0"):
        if hasattr(draft_id, 'id'):  # Fix if draft_id is a SQLAlchemy object
            draft_id = draft_id.id

        session = Session()
        try:
            particular_draft = session.query(BillParticularDraft).filter_by(id=draft_id).first()
            if not particular_draft:
                print(f"No draft found with ID: {draft_id}")
                return

            particular_draft.bill_particular = particular
            particular_draft.bill_qty = qty
            particular_draft.bill_unit = unit
            particular_draft.bill_rate = rate
            particular_draft.sub_amount = subtotal

            session.commit()
            print(f"Draft {draft_id} updated successfully.")
        except Exception as err:
            print(f"ERROR while updating draft {draft_id}: {err}")
            session.rollback()
        finally:
            session.close()

    def add_particular_row(self, draft_id="", particular="", qty="", unit="", rate=""):
        # Preelauch
        # get shop id
        shop_selection = self.shop_combobox.get()
        if not shop_selection:
            Messagebox.show_warning("Please select a shop first", "No Shop Selected", parent=self)
            return

        shop_id = self.shops_dict.get(shop_selection)
        if not shop_id:
            Messagebox.show_error("Invalid shop selection", "Error", parent=self)
            return
        
        shop_info = ShopProfile.get_shop_info(shop_id)
        if not shop_info:
            Messagebox.show_error("Shop information not found", "Error", parent=self)
            return
        
        # Get date info
        bill_month = self.bill_month_combobox.get()
        bill_year = int(self.bill_year_entry.get())
        row_frame = ttk.Frame(self.particulars_container)
        row_frame.pack(fill="x", pady=2, expand=True)

        row_frame.columnconfigure(0, weight=3)
        row_frame.columnconfigure(1, weight=1)
        row_frame.columnconfigure(2, weight=1)
        row_frame.columnconfigure(3, weight=1)
        row_frame.columnconfigure(4, weight=1)
        row_frame.columnconfigure(5, weight=0)

        particular_entry = ttk.Entry(row_frame)
        particular_entry.grid(row=0, column=0, sticky="ew", padx=2)
        particular_entry.insert(0, particular)

        qty_entry = ttk.Entry(row_frame, width=8)
        qty_entry.grid(row=0, column=1, sticky="ew", padx=2)
        qty_entry.insert(0, qty)

        unit_cb = ttk.Combobox(
            row_frame,
            values=["PCS", "KG", "LITRE", "METER", "UNIT", "KW", "%", "Month", "YEAR"],
            width=8,
            state="readonly"
        )
        unit_cb.grid(row=0, column=2, sticky="ew", padx=2)
        unit_cb.set(unit)

        rate_entry = ttk.Entry(row_frame, width=8)
        rate_entry.grid(row=0, column=3, sticky="ew", padx=2)
        rate_entry.insert(0, rate)

        amount_var = ttk.StringVar(value="0.00")
        amount_entry = ttk.Entry(row_frame, width=8, textvariable=amount_var, state="readonly")
        amount_entry.grid(row=0, column=4, sticky="ew", padx=2)

        delete_btn = ttk.Button(
            row_frame,
            text="X",
            bootstyle="danger-outline",
            width=3
        )
        delete_btn.grid(row=0, column=5, padx=2)

        def calculate_and_update_row(event=None):
            try:
                q = float(qty_entry.get().strip() or 0)
                r = float(rate_entry.get().strip() or 0)
                amt = q * r
            except ValueError:
                amt = 0.0

            amount_var.set(f"{amt:.2f}")
            self.update_total_amount()

            if draft_id:
                # Update existing
                self.handle_update_particular_draft_raw(
                    draft_id,
                    particular_entry.get(),
                    qty_entry.get(),
                    unit_cb.get(),
                    rate_entry.get(),
                    amt
                )
            else:
                # Save new
                new_id = BillParticularDraft.add_bill_particular_draft(
                    shop_id=shop_id,
                    head_id=None,
                    bill_particular=particular_entry.get(),
                    bill_qty=qty_entry.get(),
                    bill_unit=unit_cb.get(),
                    bill_rate=rate_entry.get(),
                    sub_amount=amt,
                    bill_month=bill_month,
                    bill_year=bill_year
                )



                # Update delete button to work with new id
                delete_btn.config(command=lambda rf=row_frame, did=new_id: self.delete_particular_row(rf, did))

                # Attach update events like in display_draft_particulars
                qty_entry.bind(
                    '<FocusOut>',
                    partial(
                        self.handle_update_particular_draft_raw_event,
                        new_id,
                        particular_entry,
                        qty_entry,
                        unit_cb,
                        rate_entry,
                        amount_entry
                    )
                )
                rate_entry.bind(
                    '<FocusOut>',
                    partial(
                        self.handle_update_particular_draft_raw_event,
                        new_id,
                        particular_entry,
                        qty_entry,
                        unit_cb,
                        rate_entry,
                        amount_entry
                    )
                )

        # Initial bindings for unsaved row
        qty_entry.bind('<FocusOut>', calculate_and_update_row)
        rate_entry.bind('<FocusOut>', calculate_and_update_row)
        particular_entry.bind('<FocusOut>', calculate_and_update_row)
        unit_cb.bind("<<ComboboxSelected>>", calculate_and_update_row)

        # Default delete behavior (no id yet)
        delete_btn.config(command=lambda: row_frame.destroy())

        # Initial calculation
        calculate_and_update_row()
    
    def delete_particular_row(self, row_frame, id):
        if id:
            # Only delete from DB if there's a valid ID
            BillParticularDraft.delete_bill_particular_draft_by_id(id)
            shop_selection = self.shop_combobox.get()
            shop_id = self.shops_dict.get(shop_selection)
            self.display_draft_particulars(shop_id)
        else:
            # Just remove the row from UI
            row_frame.destroy()
            self.update_total_amount()

    def update_total_amount(self):
        print("Updating total amount...")
        total = 0.0
        for child in self.particulars_container.winfo_children():
            try:
                amount_entry = child.winfo_children()[4]  # amount column
                amt = float(amount_entry.get() or 0)
                total += amt
            except (ValueError, IndexError):
                continue
        self.total_amount_var.set(f"{total:.2f}")

    def show_shop_info(self):
        try:
            # selected shop
            shop_selection = self.shop_combobox.get()
            if not shop_selection:
                Messagebox.show_warning("Please select a shop first", "No Shop Selected", parent=self)
                return

            shop_id = self.shops_dict.get(shop_selection)
            if not shop_id:
                Messagebox.show_error("Invalid shop selection", "Error", parent=self)
                return
            

            
            shop_info = ShopProfile.get_shop_info(shop_id)
            if not shop_info:
                Messagebox.show_error("Shop information not found", "Error", parent=self)
                return
            # print(f"shop_info: {shop_info.rent_type}")
            # print(f"shop_info: {shop_info.shop_size}")
            rental_type =shop_info.rent_type
            rental_amount=0.0
            shop_size=shop_info.shop_size
            per_sqr_fit_amt=shop_info.per_sqr_fit_amt
            if rental_type=='Contractual':
                rental_amount=shop_info.rent_amount
            else:
                rental_amount=per_sqr_fit_amt*shop_size
                
            # print(f"Amount: {rental_amount}")
            try:
                # Handle empty/NULL values by converting to 0.0
                elect_op = float(self.elect_op_unit_entry.get() or 0)
                elect_cl = float(self.elect_closing_unit_entry.get() or 0)
                electricity_unit = elect_cl - elect_op
                
                gas_op = float(self.gas_op_unit_entry.get() or 0)
                gas_cl = float(self.gas_closing_unit_entry.get() or 0)
                gas_unit = gas_cl - gas_op
                
                wasa_op = float(self.wasa_op_unit_entry.get() or 0)
                wasa_cl = float(self.wasa_closing_unit_entry.get() or 0)
                wasa_unit = wasa_cl - wasa_op
            except ValueError:
                Messagebox.show_error("Invalid unit values", "Calculation Error", parent=self)
                return

            # Handle potential None values from database
            utilities = {
                'electricity': UtilitySetting.get_unit_price(7) or {'unit_price': 0.0, 'unit': 'UNIT'},
                'wasa': UtilitySetting.get_unit_price(8) or {'unit_price': 0.0, 'unit': 'UNIT'},
                'gas': UtilitySetting.get_unit_price(9) or {'unit_price': 0.0, 'unit': 'UNIT'},
                'internet': float(shop_info.internet_bill or 0),
                'house_rent': float(rental_amount or 0),
                'demand_charge': float(shop_info.elect_demand_chrge or 0)
            }

            calculations = {
                'electricity': electricity_unit * utilities['electricity']['unit_price'],
                'wasa': wasa_unit * utilities['wasa']['unit_price'],
                'gas': gas_unit * utilities['gas']['unit_price'],
                'internet': utilities['internet'],
                'rent': float(rental_amount or 0),
                'demand_charge': utilities['demand_charge']
            }

            # Convert all values to float before summing
            total_amount = sum(float(v) for v in calculations.values())
            self.total_amount_var.set(f"৳{total_amount:.2f}")

            self.save_draft_particulars(shop_id, calculations, utilities, total_amount, electricity_unit, gas_unit, wasa_unit)
            # self.toggle_form_visibility(False)
            self.display_draft_particulars(shop_id)

        except Exception as e:
            print(f"Error processing shop info: {str(e)}")
            Messagebox.show_error(f"Error processing shop info: {str(e)}", "Error", parent=self)

    def save_draft_particulars(self, shop_id, calculations, utilities, total_amount, electricity_unit, gas_unit, wasa_unit):
        bill_month = self.get_month_number(self.bill_month_combobox.get())
        bill_year=int(self.bill_year_entry.get())
        BillParticularDraft.clear_drafts(shop_id,bill_month,bill_year)
        
        # print(f"bill month: {bill_month} Bill Year: {bill_year}")
        # print(f"utilities: {utilities}")
        
        particulars = [
            (7, "Electricity", 
         float(calculations['electricity']),
        utilities['electricity']['unit'], 
        float(electricity_unit or 0),
        float(utilities['electricity']['vat'] or 0),
        float(utilities['electricity']['demand_charge'] or 0)
            ),
            (8, "WASA", 
            float(calculations['wasa']),
            utilities['wasa']['unit'], 
            float(wasa_unit or 0),
            0,
            0
            ),
            (9, "Gas", 
            float(calculations['gas']),
            utilities['gas']['unit'], 
            float(gas_unit or 0),
            0,
            0
            ),
            (10, "Internet", 
            float(calculations['internet']), 
            "MONTH", 
            1,
            0,
            0
            ),
            (6, "House Rent", 
            float(utilities['house_rent']), 
            "MONTH", 
            1,
            0,
            0
            )
        ]
        
        for head_id, name, amount, unit, qty, vat, demand_charge in particulars:
            # Prevent division by zero
            rate = amount / qty if qty and qty != 0 else 0.0
            BillParticularDraft.add_bill_particular_draft(
                shop_id=shop_id,
                head_id=head_id,
                bill_particular=name,
                bill_qty=qty,
                bill_unit=unit,
                bill_rate=rate,
                sub_amount=amount,
                bill_month=bill_month,
                bill_year=bill_year,
                vat=vat,
                demand_charge=demand_charge
                
            )
            
            
    def handle_update_particular_draft_raw_event(self, draft_id, part_entry, qty_entry, unit_cb, rate_entry, amt_entry, event=None):
        try:
            self.handle_update_particular_draft_raw(
                draft_id,
                part_entry.get(),
                float(qty_entry.get() or 0),
                unit_cb.get(),
                float(rate_entry.get() or 0),
                float(amt_entry.get() or 0)
            )
        except Exception as e:
            print(f"Error updating draft {draft_id}: {e}")


    def display_draft_particulars(self, shop_id):
        # print("Reapply")
        # Clear existing rows
        session = Session()
        for child in self.particulars_container.winfo_children():
            child.destroy()
        bill_month=self.get_month_number(self.bill_month_combobox.get())
        bill_year=int(self.bill_year_entry.get())
        drafts = BillParticularDraft.get_bill_particular_draft_by_shop_id(shop_id,bill_month,bill_year,session)
        
        # change global total values to 0
        self.total_amount_var.set(f"{0.0:.2f}")
        totalAmount = 0.0
        
        for draft in drafts:
            row_frame = ttk.Frame(self.particulars_container)
            row_frame.pack(fill="x", pady=2, expand=True)
            
            # Configure grid columns (match the header proportions)
            row_frame.columnconfigure(0, weight=3)  # Particular
            row_frame.columnconfigure(1, weight=1)  # Qty
            row_frame.columnconfigure(2, weight=1)  # Unit
            row_frame.columnconfigure(3, weight=1)  # Rate
            row_frame.columnconfigure(4, weight=1)  # Amount
            row_frame.columnconfigure(5, weight=0)  # Action
            
            
            setattr(self, f'particular_entry_{draft.id}', ttk.Entry(row_frame))

            particular_entry = getattr(self, f'particular_entry_{draft.id}')
            particular_entry.grid(row=0, column=0, sticky="ew", padx=2)
            particular_entry.insert(0, draft.bill_particular)

            # Particular Entry
            # particular_entry = ttk.Entry(row_frame)
            # particular_entry.grid(row=0, column=0, sticky="ew", padx=2)
            # particular_entry.insert(0, draft.bill_particular)
            
            setattr(self, f'qty_entry_{draft.id}', ttk.Entry(row_frame,width=8))
            qty_entry = getattr(self, f'qty_entry_{draft.id}')
            qty_entry.grid(row=0, column=1, sticky="ew", padx=2)
            qty_entry.insert(0, draft.bill_qty)

            # Quantity Entry
            # qty_entry = ttk.Entry(row_frame, width=8)
            # qty_entry.grid(row=0, column=1, sticky="ew", padx=2)
            # qty_entry.insert(0, f"{draft.bill_qty:.2f}")

            # Unit Combobox
            unit_cb = ttk.Combobox(
                row_frame,
                values=["PCS", "KG", "LITRE", "METER", "UNIT", "KW", "%", "YEAR"],
                width=8,
                state="readonly"
            )
            unit_cb.grid(row=0, column=2, sticky="ew", padx=2)
            unit_cb.set(draft.bill_unit)

            # Rate Entry
            rate_entry = ttk.Entry(row_frame, width=8)
            rate_entry.grid(row=0, column=3, sticky="ew", padx=2)
            rate_entry.insert(0, f"{draft.bill_rate:.2f}")
            
            # Amount Label (right aligned)
            # amount_var = ttk.StringVar(value=f"{draft.sub_amount:.2f}")
            # amount_entry = ttk.Entry(row_frame, width=8)
            # amount_entry.grid(row=0, column=4, sticky="ew", padx=2)
            # amount_entry.insert(0, f"{draft.sub_amount:.2f}")
            
            amount_var = ttk.StringVar(value=f"{draft.sub_amount:.2f}")
            amount_entry = ttk.Entry(row_frame, width=8, textvariable=amount_var)
            amount_entry.grid(row=0, column=4, sticky="ew", padx=2)
            
            # amount_var = tk.StringVar(value=f"{draft.sub_amount:.2f}")
            totalAmount += float(draft.sub_amount)

            # Delete Button
            delete_btn = ttk.Button(
                row_frame,
                text="X",
                command=lambda rf=row_frame, did=draft.id: self.delete_particular_row(rf, did),
                bootstyle="danger-outline",
                width=3
            )
            delete_btn.grid(row=0, column=5, padx=2)

            # Calculation binding
            def calculate_amount(event=None, qentry=qty_entry, rentry=rate_entry, avar=amount_var):
                try:
                    qty = float(qentry.get() or 0)
                    rate = float(rentry.get() or 0)
                    amount = qty * rate
                    avar.set(f"{amount:.2f}")

                    # Update total by summing all amount fields
                    total = 0.0
                    for child in self.particulars_container.winfo_children():
                        entries = child.winfo_children()
                        if len(entries) >= 5:
                            try:
                                amt = float(entries[4].get())
                                total += amt
                            except ValueError:
                                continue

                    self.total_amount_var.set(f"{total:.2f}")
                except ValueError:
                    avar.set("0.00")

            # --- Bind to both qty and rate ---
            qty_entry.bind('<KeyRelease>', calculate_amount)
            rate_entry.bind('<KeyRelease>', calculate_amount)
            
            # FocusOut bindings for qty and rate entries (save/update)
            qty_entry.bind(
                '<FocusOut>',
                partial(
                    self.handle_update_particular_draft_raw_event,
                    draft.id,
                    particular_entry,
                    qty_entry,
                    unit_cb,
                    rate_entry,
                    amount_entry
                )
            )

            rate_entry.bind(
                '<FocusOut>',
                partial(
                    self.handle_update_particular_draft_raw_event,
                    draft.id,
                    particular_entry,
                    qty_entry,
                    unit_cb,
                    rate_entry,
                    amount_entry
                )
            )
            
        # end Loop
        self.total_amount_var.set(f"{totalAmount:.2f}")
        

    def toggle_form_visibility(self, show_form=True):
        form_elements = [
            self.shop_combobox, self.bill_year_entry,
            self.bill_month_combobox, self.bill_date_entry,
            self.last_pay_date_entry, self.elect_op_unit_entry,
            self.elect_closing_unit_entry, self.gas_op_unit_entry,
            self.gas_closing_unit_entry, self.wasa_op_unit_entry,
            self.wasa_closing_unit_entry, self.show_shop_info_button
        ]

        print(f"form_elements: {self.bill_date_entry}")
        
        for widget in form_elements:
            if show_form:
                widget.pack(fill="x", pady=(0, 10))
            else:
                widget.pack_forget()


    def save_bill_info(self):
        from sqlalchemy.exc import IntegrityError, SQLAlchemyError
        try:
            if not self.shop_combobox.get():
                raise ValueError("Please select a shop")

            shop_selection = self.shop_combobox.get()
            shop_id = self.shops_dict.get(shop_selection)
            if not shop_id:
                raise ValueError("Invalid shop selection")

            # bill_month = self.get_month_number(self.bill_month_combobox.get())
            # bill_year = int(self.bill_year_entry.get())

            bill_month = self.get_month_number(self.bill_month_combobox.get())
            bill_year=int(self.bill_year_entry.get())

            with session_scope() as session:
                total_amount = BillParticularDraft.get_total_draft_amount(shop_id, bill_month, bill_year)
                if total_amount is None:
                    raise ValueError("No draft amount found for the selected shop/month/year.")
                
                # tenant profile by shop_id
                # tenant_profile = session.query(ShopProfile).filter_by(shop_id=data['shop_id']).first()
                print(f"shop_id: {shop_id}, bill_year: {bill_year}, bill_month: {bill_month}")
                shop_allocation = ShopAllocation.get_renter_profile_by_shop_id(session,shop_id, year=bill_year, month=bill_month)
                if not shop_allocation:
                    raise ValueError("No shop allocation found for the selected shop/month/year.")

                bill_info = BillInfo(
                    shop_id=shop_id,
                    bill_year=bill_year,
                    bill_month=bill_month,
                    bill_date=datetime.strptime(self.bill_date_entry.entry.get(), "%Y-%m-%d"),
                    last_pay_date=datetime.strptime(self.last_pay_date_entry.entry.get(), "%Y-%m-%d"),
                    elect_op_unit=float(self.elect_op_unit_entry.get() or 0),
                    elect_closing_unit=float(self.elect_closing_unit_entry.get() or 0),
                    gas_op_unit=float(self.gas_op_unit_entry.get() or 0),
                    gas_closing_unit=float(self.gas_closing_unit_entry.get() or 0),
                    wasa_op_unit=float(self.wasa_op_unit_entry.get() or 0),
                    wasa_closing_unit=float(self.wasa_closing_unit_entry.get() or 0),
                    bill_amount=total_amount,
                    bill_gen_by="1",
                    bill_gen_at=datetime.now(),
                    prev_due=float(self.prev_bill_dues_entry.get() or 0),
                    status=1
                )

                session.add(bill_info)
                session.flush()
                bill_check = session.query(BillInfo).filter_by(id=bill_info.id).first()
                if not bill_check:
                    raise ValueError("BillInfo not flushed correctly.")

                print('shop Id:',shop_id)
                drafts = BillParticularDraft.get_bill_particular_draft_by_shop_id(shop_id, bill_month, bill_year,session=session)
                # print("drafts:",drafts,bill_month, bill_year)
                for draft in drafts:
                    # print("drafts:" , draft.bill_particular)
                    new_particular = BillParticular(
                        bill_id=bill_info.id,
                        bill_particular=draft.bill_particular,
                        bill_qty=draft.bill_qty,
                        bill_unit=draft.bill_unit,
                        bill_rate=draft.bill_rate,
                        sub_amount=draft.sub_amount,
                        paid_amount=0,
                        due_amount=draft.sub_amount,
                        vat=draft.vat,
                        demand_charge=draft.demand_charge,
                        bill_type="Bill"
                    )
                    session.add(new_particular)

                teant_amount = 0
                for draft in drafts:
                    drHeadId = crHeadId = crHeadId2 = 0
                    if draft.bill_particular == "House Rent":
                        drHeadId, crHeadId = 6, 21
                    elif draft.bill_particular == "Common Areal Maintenance":
                        drHeadId, crHeadId = 28, 29
                    elif draft.bill_particular == "Electricity":
                        drHeadId, crHeadId, crHeadId2 = 7, 23, 27
                    elif draft.bill_particular == "Gas":
                        drHeadId, crHeadId = 9, 25
                    elif draft.bill_particular == "WASA":
                        drHeadId, crHeadId = 8, 24
                    elif draft.bill_particular == "Internet":
                        drHeadId, crHeadId = 10, 26

                    try:
                        AccountingController.manage_transaction(session, [
                            "+", "insert", drHeadId, bill_info.id, date.today(), draft.sub_amount,
                            None, '1', None, "bill_info_id", bill_info.id, "cr", f"Bill Bill Generations for {draft.bill_particular}-cr"
                        ])

                        # ? INSERT TO TEANANT TRANS HISTORY
                        teant_amount += draft.sub_amount
                        AccountingController.insert_teanant_trans_history(session, drHeadId, shop_allocation.renter_profile_id, bill_info.id, None, date.today(), draft.sub_amount, "dr", teant_amount, "dr", f"Bill Generations for {draft.bill_particular}-dr", "1")

                        AccountingController.manage_transaction(session, [
                            "+", "insert", crHeadId, bill_info.id, date.today(), draft.sub_amount,
                            None, '1', None, "bill_info_id", bill_info.id, "dr", f"Bill Generations for {draft.bill_particular}-dr"
                        ])
                        # Apply for electrict bill
                        if draft.bill_particular == "Electricity":
                            #  Provisionary for vat charge 15%
                            vat_charge = draft.sub_amount * Decimal("0.15")
                            # print(f"Electricity bill: {draft.vat} & {draft.demand_charge}")
                            AccountingController.manage_transaction(session, [
                                "-", "insert", crHeadId2, bill_info.id, date.today(), vat_charge,
                                None, '1', None, "bill_info_id", bill_info.id, "cr", "Bill Generations Vat Charge"
                            ])
                            #  Provisionary for demand charge 40 BDT
                            demand_charge = Decimal("40.00")
                            AccountingController.manage_transaction(session, [
                                "-", "insert", crHeadId2, bill_info.id, date.today(), demand_charge,
                                None, '1', None, "bill_info_id", bill_info.id, "cr", "Bill Generations Demand Charge"
                            ])
                    except Exception as trans_error:
                        print(f"Transaction failed: {trans_error}")
                        raise trans_error

                session.commit()
                Messagebox.show_info("Bill created successfully!", "Success", parent=self)
                self.clear_form()

        except Exception as e:
            print(f"Error creating bill: {str(e)}")
            # traceback.print_exc()
            # Messagebox.show_error(f"Error creating bill: {str(e)}", "Error", parent=self)


    def clear_form(self):
        self.shop_combobox.set('')
        self.bill_year_entry.delete(0, "end")
        self.bill_year_entry.insert(0, str(datetime.now().year))
        self.bill_month_combobox.set(str(datetime.now().month).zfill(2))
        self.bill_date_entry.entry.delete(0, "end")
        self.bill_date_entry.entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.last_pay_date_entry.entry.delete(0, "end")
        self.elect_op_unit_entry.delete(0, "end")
        self.elect_closing_unit_entry.delete(0, "end")
        self.gas_op_unit_entry.delete(0, "end")
        self.gas_closing_unit_entry.delete(0, "end")
        self.wasa_op_unit_entry.delete(0, "end")
        self.wasa_closing_unit_entry.delete(0, "end")
        for child in self.particulars_container.winfo_children():
            child.destroy()
        self.total_amount_var.set("0.00")
        

    def show_particular_draft_table(self, shop_id):
        drafts = BillParticularDraft.get_bill_particular_draft_by_shop_id(shop_id)
        for draft in drafts:
            row_frame = ttk.Frame(self.particulars_container)
            row_frame.pack(fill="x", pady=2)

            particular_entry = ttk.Entry(row_frame)
            particular_entry.pack(side="left", fill="x", expand=True, padx=2)
            particular_entry.insert(0, draft.bill_particular)

            qty_entry = ttk.Entry(row_frame, width=15)
            qty_entry.pack(side="left", padx=2)
            qty_entry.insert(0, draft.bill_qty)

            unit_cb = ttk.Combobox(
                row_frame,
                values=["PCS", "KG", "LITRE", "METER", "UNIT", "KW", "%", "YEAR"],
                width=10,
                state="readonly"
            )
            unit_cb.pack(side="left", padx=2)
            unit_cb.set(draft.bill_unit)

            rate_entry = ttk.Entry(row_frame, width=15)
            rate_entry.pack(side="left", padx=2)
            rate_entry.insert(0, draft.bill_rate)

            amount_var = ttk.StringVar(value=f"{draft.sub_amount:.2f}")
            amount_label = ttk.Label(row_frame, textvariable=amount_var, width=15)
            amount_label.pack(side="left", padx=2)
            amount_label.insert(0, draft.sub_amount)

            ttk.Button(
                row_frame,
                text="X",
                command=lambda rf=row_frame, did=draft.id: self.delete_particular_row(rf, did),
                bootstyle="danger-outline",
                width=3
            ).pack(side="left", padx=2)

            def calculate_amount(*args):
                try:
                    qty = float(qty_entry.get() or 0)
                    rate = float(rate_entry.get() or 0)
                    amount = qty * rate
                    amount_var.set(f"{amount:.2f}")
                    self.update_total_amount()
                except ValueError:
                    amount_var.set("0.00")

            qty_entry.bind('<KeyRelease>', calculate_amount)
            rate_entry.bind('<KeyRelease>', calculate_amount)
    

    # def show_particular_draft_table(self, shop_id):
    #     drafts = BillParticularDraft.get_bill_particular_draft_by_shop_id(shop_id)
    #     for draft in drafts:
    #         row_frame = ttk.Frame(self.particulars_container)
    #         row_frame.pack(fill="x", pady=2)

    #         particular_entry = ttk.Entry(row_frame)
    #         particular_entry.pack(side="left", fill="x", expand=True, padx=2)
    #         particular_entry.insert(0, draft.bill_particular)

    #         qty_entry = ttk.Entry(row_frame, width=15)
    #         qty_entry.pack(side="left", padx=2)
    #         qty_entry.insert(0, draft.bill_qty)

    #         unit_cb = ttk.Combobox(
    #             row_frame,
    #             values=["PCS", "KG", "LITRE", "METER", "UNIT", "KW", "%", "YEAR"],
    #             width=10,
    #             state="readonly"
    #         )
    #         unit_cb.pack(side="left", padx=2)
    #         unit_cb.set(draft.bill_unit)

    #         rate_entry = ttk.Entry(row_frame, width=15)
    #         rate_entry.pack(side="left", padx=2)
    #         rate_entry.insert(0, draft.bill_rate)

    #         # Corrected: Using tk.StringVar
    #         amount_var = tk.StringVar(value=f"{draft.sub_amount:.2f}")
    #         # amount_label = ttk.Label(row_frame, textvariable=amount_var, width=15)
    #         # amount_label.pack(side="left", padx=2)
            
    #         sub_amount = ttk.Entry(row_frame, width=15)
    #         sub_amount.pack(side="left", padx=2)
    #         sub_amount.insert(0, draft.sub_amount)

    #         ttk.Button(
    #             row_frame,
    #             text="X",
    #             command=lambda: self.delete_particular_row(row_frame, draft.id),
    #             width=3
    #         ).pack(side="left", padx=2)

    #         def calculate_amount(*args, var=amount_var, qentry=qty_entry, rentry=rate_entry):
    #             try:
    #                 qty = float(qentry.get() or 0)
    #                 rate = float(rentry.get() or 0)
    #                 amount = qty * rate
    #                 var.set(f"{amount:.2f}")
    #                 amount_entry.delete(0, tk.END)
    #                 amount_entry.insert(0, f"{amount:.2f}")
    #                 self.update_total_amount()  # Update total
    #             except ValueError:
    #                 var.set("0.00")


    #         qty_entry.bind('<KeyRelease>', calculate_amount)
    #         rate_entry.bind('<KeyRelease>', calculate_amount)
    #         sub_amount.bind('<KeyRelease>', calculate_amount)
            
        
