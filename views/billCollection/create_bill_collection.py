import tkinter as tk
from tkinter import ttk
from ttkbootstrap import Frame, Label, Button, Entry, Combobox
from ttkbootstrap.constants import *
from ttkbootstrap.widgets import DateEntry
from utils.database import Session
from models.acc_head_of_accounts import AccHeadOfAccounts
from models.BankAccount import BankAccount
from models.shop_profile import ShopProfile
from models.bill_info import BillInfo
from models.bill_due import BillDue
from models.bill_particular import BillParticular
import traceback
from models.bill_collection import BillCollection
from models.shop_allocation import ShopAllocation
from ttkbootstrap.dialogs import Messagebox
from controllers.accounting_controller import AccountingController
from decimal import Decimal


class CreateBillCollectionView(Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.pack(fill='both', expand=True)

        self.selected_shop_name = tk.StringVar()
        self.shop_id = tk.StringVar()
        self.selected_bill_no = tk.StringVar()
        self.bill_id = tk.StringVar()
        self.trans_mode = tk.StringVar()
        self.trans_amount = tk.StringVar()
        self.pay_amount = tk.StringVar()
        self.trans_remarks = tk.StringVar()
        self.selected_bank_name = tk.StringVar()
        self.check_no = tk.StringVar()
        self.due_amount = tk.StringVar()
        self.total_paid = tk.StringVar()
        self.total_due = tk.StringVar()

        self.shops_dict = {}
        self.bill_no_dict = {}
        self.bank_dict = {}

        self.load_shops()
        self.load_banks()

        self.create_form()

    def create_form(self):
        container = Frame(self)
        container.place(relx=0.5, rely=0.5, anchor='center')

        Label(container, text="Bill Collection Entry", font=("Segoe UI", 18, "bold")).grid(
            row=0, column=0, columnspan=2, pady=(0, 20)
        )

        row = 1

        # Shop Selection
        Label(container, text="Shop Name").grid(row=row, column=0, padx=10, pady=5, sticky="e")
        shop_cb = Combobox(container, textvariable=self.selected_shop_name, values=list(self.shops_dict.keys()), width=30)
        shop_cb.grid(row=row, column=1, padx=10, pady=5, sticky="w")
        shop_cb.bind("<<ComboboxSelected>>", self.on_shop_select)

        row += 1

        # Due Amount
        Label(container, text="Due Amount").grid(row=row, column=0, padx=10, pady=5, sticky="e")
        Entry(container, textvariable=self.due_amount, width=32, state='readonly').grid(row=row, column=1, padx=10, pady=5, sticky="w")

        row += 1

        # Bill Selection
        Label(container, text="Bill No").grid(row=row, column=0, padx=10, pady=5, sticky="e")
        bill_no_cb = Combobox(container, textvariable=self.selected_bill_no, values=list(self.bill_no_dict.keys()), width=30)
        bill_no_cb.grid(row=row, column=1, padx=10, pady=5, sticky="w")
        bill_no_cb.bind("<<ComboboxSelected>>", self.on_bill_no_select)

        row += 1

        # Transaction Date
        Label(container, text="Transaction Date").grid(row=row, column=0, padx=10, pady=5, sticky="e")
        self.date_picker = DateEntry(container, bootstyle="info", dateformat="%Y-%m-%d", width=28)
        self.date_picker.grid(row=row, column=1, padx=10, pady=5, sticky="w")

        row += 1

        # Transaction Mode
        Label(container, text="Transaction Mode").grid(row=row, column=0, padx=10, pady=5, sticky="e")
        mode_cb = Combobox(container, textvariable=self.trans_mode, values=["Cash", "Bank"], width=30)
        mode_cb.grid(row=row, column=1, padx=10, pady=5, sticky="w")
        mode_cb.bind("<<ComboboxSelected>>", self.on_mode_change)

        row += 1

        # Bank Name (hidden by default)
        self.bank_row = row
        self.bank_label = Label(container, text="Bank Name")
        self.bank_combobox = Combobox(container, textvariable=self.selected_bank_name, values=list(self.bank_dict.keys()), width=30)

        row += 1

        # Check No (hidden by default)
        self.check_row = row
        self.check_label = Label(container, text="Check No")
        self.check_entry = Entry(container, textvariable=self.check_no, width=32)

        row += 1

        # Transaction Amount
        Label(container, text="Transaction Amount").grid(row=row, column=0, padx=10, pady=5, sticky="e")
        Entry(container, textvariable=self.trans_amount, width=32).grid(row=row, column=1, padx=10, pady=5, sticky="w")

        row += 1

        # # Pay Amount
        # Label(container, text="Pay Amount").grid(row=row, column=0, padx=10, pady=5, sticky="e")
        # Entry(container, textvariable=self.pay_amount, width=32).grid(row=row, column=1, padx=10, pady=5, sticky="w")

        # row += 1

        # Remarks
        Label(container, text="Remarks").grid(row=row, column=0, padx=10, pady=5, sticky="e")
        Entry(container, textvariable=self.trans_remarks, width=32).grid(row=row, column=1, padx=10, pady=5, sticky="w")

        row += 1

        # Submit Button
        # Button(container, text="Save Collection", bootstyle="success", command=self.save_data).grid(
        #     row=row, column=0, columnspan=2, pady=20
        # )

        Button(container, text="Show Details", bootstyle="success", command=self.next_form).grid(
            row=row, column=1, columnspan=3, pady=50
        )

    def load_shops(self):
        try:
            session = Session()
            shops = session.query(ShopProfile).all()
            print(f"Shops: {shops}")
            self.shops_dict = {shop.shop_name: shop.id for shop in shops}
            session.close()
        except Exception as e:
            print(f"Error loading shops: {str(e)}")
            self.shops_dict = {}

    def load_banks(self):
        try:
            session = Session()
            banks = BankAccount.get_banks()
            self.bank_dict = {bank.bank_name: bank.id for bank in banks}
            session.close()
        except Exception as e:
            print(f"Error loading banks: {str(e)}")
            self.bank_dict = {}

    def on_shop_select(self, event=None):
        shop_name = self.selected_shop_name.get()
        shop_id = self.shops_dict.get(shop_name, "")
        self.shop_id.set(shop_id)
        print(f"Selected Shop ID: {shop_id}")

        # Load bills for the selected shop
        session = Session()
        bills = session.query(BillInfo).filter_by(shop_id=shop_id).all()
        print(f"Bills: {bills}")

        # Format bill display as "Month Year"
        month_names = {
            1: "January", 2: "February", 3: "March", 4: "April",
            5: "May", 6: "June", 7: "July", 8: "August",
            9: "September", 10: "October", 11: "November", 12: "December"
        }
        self.bill_no_dict = {f"{month_names[bill.bill_month]} {bill.bill_year}": bill.id for bill in bills}
        
        # Update bill combobox values
        for widget in self.winfo_children():
            if isinstance(widget, Frame):
                for child in widget.winfo_children():
                    if isinstance(child, Combobox) and child.cget('textvariable') == str(self.selected_bill_no):
                        child['values'] = list(self.bill_no_dict.keys())
                        break
        
        # Load due amount for the shop
        bill_due = session.query(BillDue).filter_by(shop_id=shop_id).first()
        print(f"Bill Due: {bill_due}", shop_id)
        if bill_due:
            self.due_amount.set(str(bill_due.due_amount))
        else:
            self.due_amount.set("0")
        
        session.close()

    def on_bill_no_select(self, event=None):
        bill_no = self.selected_bill_no.get()
        bill_id = self.bill_no_dict.get(bill_no, "")
        self.bill_id.set(bill_id)
        
        # Load bill amount and set it as transaction amount
        session = Session()
        bill = session.query(BillInfo).filter_by(id=bill_id).first()
        if bill:
            self.trans_amount.set(str(bill.bill_amount))
            # Set the date in the DateEntry widget
            try:
                # For ttk.DateEntry, we need to set the date using the entry widget
                self.date_picker.entry.delete(0, 'end')
                self.date_picker.entry.insert(0, bill.bill_date.strftime('%Y-%m-%d'))
                # For ttk.DateEntry, we need to set the internal date
                self.date_picker._set_date(bill.bill_date)
            except Exception as e:
                print(f"Error setting date: {str(e)}")
        session.close()

    def on_mode_change(self, event=None):
        mode = self.trans_mode.get()
        if mode == "Bank":
            self.bank_label.grid(row=self.bank_row, column=0, padx=10, pady=5, sticky="e")
            self.bank_combobox.grid(row=self.bank_row, column=1, padx=10, pady=5, sticky="w")

            self.check_label.grid(row=self.check_row, column=0, padx=10, pady=5, sticky="e")
            self.check_entry.grid(row=self.check_row, column=1, padx=10, pady=5, sticky="w")
        else:
            self.bank_label.grid_remove()
            self.bank_combobox.grid_remove()
            self.check_label.grid_remove()
            self.check_entry.grid_remove()

    # ! ON NEXT FORM CLICKED
    def next_form(self):
        data = {
            "shop_id": self.shop_id.get(),
            "bill_id": self.bill_id.get(),
            "trans_date": self.date_picker.entry.get(),
            "trans_mode": self.trans_mode.get(),
            "bank_name": self.selected_bank_name.get() if self.trans_mode.get() == "Bank" else None,
            "check_no": self.check_no.get() if self.trans_mode.get() == "Bank" else None,
            "trans_amount": self.trans_amount.get(),
            "pay_amount": self.pay_amount.get(),
            "remarks": self.trans_remarks.get(),
        }

        self.pack_forget()
        
        self.pack_forget()
    
        session = Session()
        try:
            # ? GET BILL PARTICULARS
            bill_particulars = BillParticular.get_bill_particular_by_bill_id(session, self.bill_id.get())
            print(f"Bill Particulars: {bill_particulars}")
            
            # ? CREATE COLLECTION FORM
            self.collection_form = Frame(self.parent)
            self.collection_form.pack(fill='both', expand=True)

            Label(self.collection_form, text="Bill Collection Details", font=("Segoe UI", 16, "bold"))\
                .grid(row=0, column=0, columnspan=6, pady=10)

            # Display some details (as labels)
            details_frame = Frame(self.collection_form)
            details_frame.grid(row=1, column=0, columnspan=6, padx=10, pady=10, sticky='w')

            Label(details_frame, text=f"Shop: {self.selected_shop_name.get()}").grid(row=0, column=0, sticky='w')
            Label(details_frame, text=f"Bill No: {self.selected_bill_no.get()}").grid(row=0, column=1, padx=20, sticky='w')
            Label(details_frame, text=f"Total Amount: {self.trans_amount.get()}").grid(row=0, column=2, padx=20, sticky='w')
            Label(details_frame, text=f"Paid Amount: {self.pay_amount.get()}").grid(row=0, column=3, padx=20, sticky='w')
            Label(details_frame, text=f"Payment Date: {data['trans_date']}").grid(row=0, column=4, sticky='w')

            # Optional: Header row
            header_frame = ttk.Frame(self.collection_form)
            header_frame.grid(row=2, column=0, columnspan=6, sticky="ew", padx=10)
            headers = ['Particulars', 'Qty', 'Rate', 'Subtotal', 'Pay Amount', 'Due']
            for c, h in enumerate(headers):
                lbl = ttk.Label(header_frame, text=h, font=('Segoe UI', 12, 'bold'), width=15 if c==0 else 10, anchor='center')
                lbl.grid(row=0, column=c, padx=2)

            # Container for entry rows
            self.collection_container = ttk.Frame(self.collection_form)
            self.collection_container.grid(row=3, column=0, columnspan=6, sticky='nsew', padx=10)

            self.row_vars = []  # to keep vars per row
            self.total_paid.set(0)
            self.total_due.set(0)

            # Create labels first so they can be referenced in the recalc function
            total_paid_label = ttk.Label(self.collection_form, text=f"Total Paid: {self.total_paid.get()}", font=("Segoe UI", 12, "bold"))
            total_paid_label.grid(row=4, column=0, columnspan=6, pady=5, sticky='e')

            total_due_label = ttk.Label(self.collection_form, text=f"Total Due: {self.total_due.get()}", font=("Segoe UI", 12, "bold"))
            total_due_label.grid(row=5, column=0, columnspan=6, pady=5, sticky='e')

            # TODO CREATE ROWS FOR EACH PARTICULAR
            for idx, particular in enumerate(bill_particulars):
                row_frame = ttk.Frame(self.collection_container)
                row_frame.grid(row=idx, column=0, sticky="ew", pady=2)

                # Particular (readonly Entry)
                particular_var = tk.StringVar(value=particular.bill_particular)
                particular_entry = ttk.Entry(row_frame, textvariable=particular_var, width=16, state='readonly')
                particular_entry.grid(row=0, column=0, padx=2)

                # Qty Entry
                qty_var = tk.StringVar(value=f"{particular.bill_qty:.2f}")
                qty_entry = ttk.Entry(row_frame, textvariable=qty_var, width=6, state='readonly')
                qty_entry.grid(row=0, column=1, padx=2)

                # Rate Entry (readonly)
                rate_var = tk.StringVar(value=f"{particular.bill_rate:.2f}")
                rate_entry = ttk.Entry(row_frame, textvariable=rate_var, width=8, state='readonly')
                rate_entry.grid(row=0, column=2, padx=2)

                # Subtotal Entry (readonly, auto-calculated)
                subtotal_var = tk.StringVar(value=f"{particular.sub_amount:.2f}")
                subtotal_entry = ttk.Entry(row_frame, textvariable=subtotal_var, width=10, state='readonly')
                subtotal_entry.grid(row=0, column=3, padx=2)

                # Pay Now Entry - Initialize with subtotal amount
                pay_now_var = tk.StringVar(value=f"{particular.sub_amount:.2f}")
                pay_now_entry = ttk.Entry(row_frame, textvariable=pay_now_var, width=10)
                pay_now_entry.grid(row=0, column=4, padx=2)

                # Due Entry (readonly, auto-calculated) - Initialize with 0 since full amount is paid
                due_var = tk.StringVar(value="0.00")
                due_entry = ttk.Entry(row_frame, textvariable=due_var, width=8, state='readonly')
                due_entry.grid(row=0, column=5, padx=2)

                # Store vars if needed
                self.row_vars.append({
                    'particular': particular_var,
                    'qty': qty_var,
                    'rate': rate_var,
                    'subtotal': subtotal_var,
                    'pay_now': pay_now_var,
                    'due': due_var,
                })

                # Recalc function
                def recalc(*args, qv=qty_var, rv=rate_var, sv=subtotal_var, pv=pay_now_var, dv=due_var):
                    try:
                        qty = float(qv.get())
                        rate = float(rv.get())
                        subtotal = qty * rate
                        sv.set(f"{subtotal:.2f}")
                        
                        # Get pay amount, default to subtotal if invalid
                        try:
                            pay = float(pv.get())
                        except ValueError:
                            pay = subtotal
                            pv.set(f"{subtotal:.2f}")
                        
                        # Calculate due amount
                        due = subtotal - pay
                        dv.set(f"{due:.2f}")
                        
                        # Recalculate totals
                        self.total_paid = sum(float(row['pay_now'].get() or 0) for row in self.row_vars)
                        self.total_due = sum(float(row['due'].get() or 0) for row in self.row_vars)
                        
                        # Update labels
                        total_paid_label.config(text=f"Total Paid: {self.total_paid.get()}")
                        total_due_label.config(text=f"Total Due: {self.total_due.get()}")
                    except ValueError:
                        pass

                # Bind the recalc function to pay_now_var changes
                pay_now_var.trace_add('write', recalc)

            # Initialize totals with initial values
            self.total_paid.set(sum(float(row['pay_now'].get() or 0) for row in self.row_vars))
            self.total_due.set(sum(float(row['due'].get() or 0) for row in self.row_vars))
            total_paid_label.config(text=f"Total Paid: {self.total_paid.get()}")
            total_due_label.config(text=f"Total Due: {self.total_due.get()}")

            # Buttons frame
            btn_frame = Frame(self.collection_form)
            btn_frame.grid(row=6, column=0, columnspan=6, pady=20)

            Button(btn_frame, text="Back", bootstyle="secondary", command=self.show_previous_form).pack(side='left', padx=10)
            Button(btn_frame, text="Save Collection", bootstyle="success", 
                command=lambda: self.save_collection(data, bill_particulars)).pack(side='left', padx=10)

        finally:
            session.close()

    def on_tree_edit(self, event):
        region = self.tree.identify("region", event.x, event.y)
        if region != "cell":
            return

        row_id = self.tree.identify_row(event.y)
        col = self.tree.identify_column(event.x)
        col_index = int(col[1:]) - 1

        editable_columns = ['qty', 'pay_now']
        column_names = ('particular', 'qty', 'rate', 'subtotal', 'pay_now','due')
        if column_names[col_index] not in editable_columns:
            return

        x, y, width, height = self.tree.bbox(row_id, col)
        value = self.tree.set(row_id, column_names[col_index])

        x, y, width, height = self.tree.bbox(row_id, col)

        self.edit_box = Entry(self.tree, font=("Segoe UI", 12))
        self.edit_box.place(x=x, y=y, width=width + 15, height=height + 6)
        self.edit_box.insert(0, value)
        self.edit_box.focus()



        def save_edit(event):
            new_value = self.edit_box.get()
            try:
                new_decimal = Decimal(new_value)
            except:
                self.edit_box.destroy()
                return

            row_idx = int(row_id)
            self.row_data[row_idx][column_names[col_index]] = new_decimal

            # Recalculate subtotal, due
            if column_names[col_index] == 'qty':
                qty = new_decimal
                rate = self.row_data[row_idx]['rate']
                self.row_data[row_idx]['subtotal'] = qty * rate
                pay_amount = self.row_data[row_idx]['pay_now']
                self.row_data[row_idx]['due'] = (qty * rate) - pay_amount
                self.total_due += self.row_data[row_idx]['due']
                self.total_paid += pay_amount
                self.total_paid_label.config(text=f"Total Paid: {self.total_paid.get()}")
                self.total_due_label.config(text=f"Total Due: {self.total_due.get()}")

            elif column_names[col_index] == 'pay_now':
                due = self.row_data[row_idx]['due']
                if new_decimal > due:
                    new_decimal = due  # clamp to due
                    self.row_data[row_idx]['pay_now'] = due
                self.total_due += self.row_data[row_idx]['due']
                self.total_paid += pay_amount

                self.total_paid_label.config(text=f"Total Paid: {self.total_paid.get()}")
                self.total_due_label.config(text=f"Total Due: {self.total_due.get()}")

            self.tree.item(row_id, values=(
                self.row_data[row_idx]['particular'],
                f"{self.row_data[row_idx]['qty']:.2f}",
                f"{self.row_data[row_idx]['rate']:.2f}",
                f"{self.row_data[row_idx]['subtotal']:.2f}",
                f"{self.row_data[row_idx]['pay_now']:.2f}",
                f"{self.row_data[row_idx]['due']:.2f}",
            ))

            self.edit_box.destroy()

        self.edit_box.bind("<Return>", save_edit)
        self.edit_box.bind("<FocusOut>", lambda e: self.edit_box.destroy())

    def on_pay_now_edit(self, event):
        region = self.tree.identify("region", event.x, event.y)
        if region != "cell":
            return

        column = self.tree.identify_column(event.x)
        if column != '#7':  # Pay Now column
            return

        row_id = self.tree.identify_row(event.y)
        item = self.tree.item(row_id)
        values = item['values']
        x, y, width, height = self.tree.bbox(row_id, column)

        # Get original due from hidden column
        original_due = Decimal(values[7])
        
        # Create entry widget
        entry = Entry(self.tree)
        entry.place(x=x, y=y, width=width, height=height)
        entry.insert(0, values[6])
        entry.select_range(0, tk.END)
        entry.focus_set()

        def save_edit():
            try:
                new_payment = Decimal(entry.get())
            except:
                Messagebox.show_error("Invalid amount entered", "Error")
                entry.destroy()
                return

            # Validate payment
            if new_payment < 0:
                Messagebox.show_error("Payment cannot be negative", "Error")
                entry.destroy()
                return
                
            if new_payment > original_due:
                Messagebox.show_error("Payment exceeds due amount", "Error")
                entry.destroy()
                return

            # Update values
            new_values = list(values)
            new_values[6] = f"{new_payment:.2f}"          # Update Pay Now
            new_values[5] = f"{original_due - new_payment:.2f}"  # Update Due
            
            self.tree.item(row_id, values=new_values)
            entry.destroy()
            
            # Update total paid
            self.update_total_paid()

        entry.bind('<FocusOut>', lambda e: save_edit())
        entry.bind('<Return>', lambda e: save_edit())

    def update_total_paid(self):
        total = Decimal('0')
        for item in self.tree.get_children():
            values = self.tree.item(item)['values']
            total += Decimal(values[6])
        self.total_paid_label.config(text=f"Total Paid: {total:.2f}")


    def on_pay_now_edit(self, event):
        # Handle double-click to edit Pay Now
        region = self.tree.identify("region", event.x, event.y)
        if region == "cell":
            column = self.tree.identify_column(event.x)
            if column == '#7':  # Pay Now column
                row_id = self.tree.identify_row(event.y)
                column_box = self.tree.bbox(row_id, column)
                current_value = self.tree.item(row_id, 'values')[6]

                entry = Entry(self.tree, width=8)
                entry.place(x=column_box[0], y=column_box[1], width=column_box[2], height=column_box[3])
                entry.insert(0, current_value)
                entry.focus_set()

                def save_edit(event):
                    new_value = entry.get()
                    try:
                        # Validate input as a positive number
                        if Decimal(new_value) >= 0:
                            values = list(self.tree.item(row_id, 'values'))
                            values[6] = f"{Decimal(new_value):.2f}"
                            self.tree.item(row_id, values=values)
                    except:
                        pass
                    entry.destroy()

                entry.bind('<FocusOut>', save_edit)
                entry.bind('<Return>', save_edit)

    def save_data(self):
        try:
            trans_amount = Decimal(self.trans_amount.get())
        except Exception:
            Messagebox.show_error("Invalid transaction amount", "Error")
            return

        data = {
            "shop_id": int(self.shop_id.get()),
            "bill_id": int(self.bill_id.get()),
            "trans_date": self.date_picker.entry.get(),
            "trans_mode": self.trans_mode.get(),
            "bank_name": self.selected_bank_name.get() if self.trans_mode.get() == "Bank" else None,
            "check_no": self.check_no.get() if self.trans_mode.get() == "Bank" else None,
            "trans_amount": trans_amount,
            "remarks": self.trans_remarks.get(),
        }
        bank_id = self.bank_dict.get(data['bank_name']) if data['trans_mode'] == 'Bank' else None
        session = Session()
        try:
            collection = BillCollection(
                shop_id=data['shop_id'],
                bill_id=data['bill_id'],
                trans_date=data['trans_date'],
                trans_mode=data['trans_mode'],
                bank_id=bank_id,
                check_no=data['check_no'],
                trans_amount=data['trans_amount'],
                remarks=data['remarks']
            )
            session.add(collection)
            session.commit()
            Messagebox.show_info("Collection saved successfully!", "Success")
        except Exception as e:
            # session.rollback()
            Messagebox.show_error(f"Error saving collection: {str(e)}", "Error")
            traceback.print_exc()
        finally:
            session.close()

    # ! ON SAVE COLLECTION CLICKED
    def save_collection(self, data, bill_particulars):
        session = Session()
        try:
            bank_id = self.bank_dict.get(data['bank_name']) if data['trans_mode'] == 'Bank' else None
            
            # Start transaction
            session.begin()
            print('data before collection',data)
            # check if bill collection already exists
            bill_collection = session.query(BillCollection).filter_by(bill_id=data['bill_id']).first()
            if bill_collection:
                Messagebox.show_error("Bill collection already exists", "Error")
                return
            
            shop_allocation = ShopAllocation.get_renter_profile_by_shop_id(session,data['shop_id'], year=data['bill_year'], month=data['bill_month'])
            # if not shop_allocation:
            #     raise ValueError("No shop allocation found for the selected shop/month/year.")
            
            # Create BillCollection entry
            collection = BillCollection(
                shop_id=int(data['shop_id']),
                bill_id=int(data['bill_id']),
                trans_date=data['trans_date'],
                trans_mode=data['trans_mode'],
                bank_id=bank_id,
                check_no=data['check_no'],
                trans_amount=Decimal(data['trans_amount']),
                pay_amount=Decimal(self.total_paid.get() or 0),
                due_amount=Decimal(self.total_due.get() or 0),
                remarks=data['remarks']
            )
            # ? ADD BILL COLLECTION TO DATABASE
            session.add(collection)
            session.flush()  # Get collection ID

            total_paid = Decimal('0')
            print('len:',len(bill_particulars))

            # tenant profile by shop_id
            # # tenant_profile = session.query(ShopProfile).filter_by(shop_id=data['shop_id']).first()
            shop_allocation = ShopAllocation.get_renter_profile_by_shop_id(data['shop_id'], year=data['trans_date'].year, month=data['trans_date'].month)
            # if shop_allocation:
            #     renter_profile_id = shop_allocation.renter_profile_id
            # else:
            #     renter_profile_id = None
            
            # ? UPDATE BILL PARTICULARS AND CREATE COLLECTION PARTICULARS
            for idx, particular in enumerate(bill_particulars):
                try:
                    row_data = self.row_vars[idx]
                    pay_now_str = row_data['pay_now'].get()
                    if not pay_now_str:
                        pay_now_str = "0"
                    pay_now = Decimal(pay_now_str)
                    
                    if pay_now > 0:
                        particular.paid_amount = (particular.paid_amount or Decimal('0')) + pay_now
                        particular.due_amount = (particular.due_amount or particular.sub_amount) - pay_now
                        
                        # Create collection particular
                        coll_particular = BillParticular(
                            bill_collection_id=collection.id,
                            bill_id=particular.bill_id,
                            bill_particular=particular.bill_particular,
                            bill_qty=particular.bill_qty,
                            bill_rate=particular.bill_rate,
                            sub_amount=pay_now,
                            paid_amount=pay_now,
                            bill_type="Collection"
                        )
                        session.add(coll_particular)
                        total_paid += pay_now
                        # continue

                        # ? INSERT TO ACCOUNTING TABLE
                        drHeadId = crHeadId = crHeadId2 = 0

                        # print('data',int(data['bank_id']))

                        if data['trans_mode'] == 'Cash':
                            drHeadId = 4  # Cash Head ID
                        else:
                            head = session.query(AccHeadOfAccounts).filter_by(bank_id=bank_id).first()
                            drHeadId = head.id if head else 1 

                        if particular.bill_particular == "House Rent":
                            self.insert_house_rent_to_accounting(session, collection, pay_now, data)
                            continue
                        elif particular.bill_particular == "Common Area Maintenance":
                            crHeadId = 28
                        elif particular.bill_particular == "Electricity":
                           crHeadId = 7
                        elif particular.bill_particular == "Gas":
                            crHeadId = 9
                        elif particular.bill_particular == "WASA":
                            crHeadId = 8
                        elif particular.bill_particular == "Internet":
                            crHeadId = 10

                        # Collection Debit Entry
                        AccountingController.manage_transaction(session, [
                            "+", "insert", drHeadId, collection.id,
                            collection.trans_date, pay_now, 
                            bank_id, '1', None,
                            "bill_colct_id", collection.id,
                            "dr", "Bill Collection - Debit"
                        ])

                        # # ? INSERT TO TEANANT TRANS HISTORY
                        AccountingController.insert_teanant_trans_history(
                            session,
                            shop_allocation.renter_profile_id,
                            collection.id, None, 
                            collection.trans_date, 
                            pay_now, "cr", 
                            pay_now, 
                            "dr", 
                            f"Bill Collection - Debit", 
                            "1"
                        )

                        # Rent Income Credit Entry
                        AccountingController.manage_transaction(session, [
                            "-", "insert", crHeadId, collection.id,
                            collection.trans_date, pay_now, 
                            None, '1', None,
                            "bill_colct_id", collection.id,
                            "cr", "Bill Collection - Credit"
                        ])
                        
                except (ValueError, TypeError, AttributeError) as e:
                    print(f"Error processing row {idx}: {str(e)}")
                    continue

            # ? UPDATE BILL COLLECTION WITH ACTUAL PAID AMOUNT
            collection.pay_amount = total_paid
            collection.due_amount = Decimal(data['trans_amount']) - total_paid

            # ? UPDATE BILL DUE
            bill_due = session.query(BillDue).filter_by(shop_id=int(data['shop_id'])).first()
            if bill_due:
                bill_due.due_amount = (bill_due.due_amount or Decimal('0')) - total_paid
            else:
                bill_due = BillDue(shop_id=int(data['shop_id']), due_amount=-total_paid)
                session.add(bill_due)

            # Create accounting entries
            # self.create_accounting_entries(session, collection, total_paid, data)

            session.commit()
            Messagebox.show_info("Collection saved successfully!", "Success")
            self.collection_form.destroy()

        except Exception as e:
            session.rollback()
            print('error in save collection',e)
            Messagebox.show_error(f"Error saving collection: {str(e)}", "Error")
            # traceback.print_exc()
        finally:
            session.close()


    def show_previous_form(self):
        self.collection_form.destroy()
        self.pack(fill='both', expand=True)


    # insert to accounting table

    # House Rent
    def insert_house_rent_to_accounting(self, session, collection, amount, data):

        # ? INSERT TO ACCOUNTING TABLE
        drHeadId, crHeadId, tdsDrHeadId, drRentPrvHeadId = 7, 6, 35, 21  
        tdsCrHeadId, crRentRevenueHeadId, crPaybleOwnerHeadId = 22, 16, 11
        bank_id = self.bank_dict.get(data['bank_name']) if data['trans_mode'] == 'Bank' else None

        # Determine debit head based on payment mode
        if data['trans_mode'] == 'Cash':
            drHeadId = 4  # Cash Head ID
        else:
            bank_id = self.bank_dict.get(data['bank_name'])
            head = session.query(AccHeadOfAccounts).filter_by(bank_id=bank_id).first()
            drHeadId = head.id if head else 1 
        # 1st

        tdsOfficeRentAmount = amount * 0.05 # 5%
        cashOrBankAmount = amount * 0.95 # 95%
        receivableHeadForRent = amount

        # Collection Debit Entry
        # ? INSERT TO THE BANK HEAD OR CASH HEAD @DEBIT
        AccountingController.manage_transaction(session, [
            "+", "insert", drHeadId, collection.id,
            collection.trans_date, cashOrBankAmount, 
            bank_id, '1', None,
            "bill_colct_id", collection.id,
            "dr", "Bill Collection - Debit"
        ])

        # ? INSERT TO THE TDS HEAD @DEBIT
        AccountingController.manage_transaction(session, [
            "+", "insert", tdsDrHeadId, collection.id,
            collection.trans_date, tdsOfficeRentAmount, 
            bank_id, '1', None,
            "bill_colct_id", collection.id,
            "dr", "Bill Collection - Debit"
        ])

        # ? INSERT TO RECEIVABLE HEAD FOR RENT @CREDIT
        AccountingController.manage_transaction(session, [
            "+", "insert", crHeadId, collection.id,
            collection.trans_date, receivableHeadForRent, 
            drHeadId, '1', None,
            "bill_colct_id", collection.id,
            "dr", "Bill Collection - CREDIT"
        ])

        # 2nd


        provisionalOfficeRentAmount = amount
        prvTDSOfficeRentAmount = amount * 0.05 # 5%
        revenueRentCommission = amount * 0.05 # 5%
        payableToOwner = amount * 0.90 # 90%

        # ? Provisional for rent @DEBIT
        AccountingController.manage_transaction(session, [
            "+", "insert", drRentPrvHeadId, collection.id,
            collection.trans_date, provisionalOfficeRentAmount, 
            bank_id, '1', None,
            "bill_colct_id", collection.id,
            "dr", "Bill Collection - Debit"
        ])

        # ? TDS FOR RENT @CREDIT
        AccountingController.manage_transaction(session, [
            "+", "insert", tdsCrHeadId, collection.id,
            collection.trans_date, prvTDSOfficeRentAmount, 
            None, '1', None,
            "bill_colct_id", collection.id,
            "dr", "Bill Collection - Debit"
        ])

        # ? REVENUE FOR RENT COMMISSION @CREDIT
        AccountingController.manage_transaction(session, [
            "+", "insert", crRentRevenueHeadId, collection.id,
            collection.trans_date, revenueRentCommission, 
            None, '1', None,
            "bill_colct_id", collection.id,
            "dr", "Bill Collection - Debit"
        ])

        # ? PAYABLE TO OWNER @CREDIT
        AccountingController.manage_transaction(session, [
            "+", "insert", crPaybleOwnerHeadId, collection.id,
            collection.trans_date, payableToOwner, 
            None, '1', None,
            "bill_colct_id", collection.id,
            "dr", "Bill Collection - Debit"
        ])

