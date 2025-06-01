import ttkbootstrap as ttk

class BalanceSheetView(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.pack(fill="both", expand=True)
        self.create_widgets()