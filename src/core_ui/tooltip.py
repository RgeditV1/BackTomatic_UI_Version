import customtkinter as ctk


class ToolTip:

    def __init__(self, widget, texto, delay=400):
        self.widget = widget
        self.texto = texto
        self.delay = delay

        self.tooltip = None
        self.after_id = None

        widget.bind("<Enter>", self._programar)
        widget.bind("<Leave>", self._ocultar)
        widget.bind("<ButtonPress>", self._ocultar)

    # ================= INTERNO =================

    def _programar(self, event=None):
        self.after_id = self.widget.after(self.delay, self._mostrar)

    def _mostrar(self):

        if self.tooltip:
            return

        x = self.widget.winfo_rootx() + 20
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 10

        self.tooltip = ctk.CTkToplevel(self.widget)
        self.tooltip.overrideredirect(True)
        self.tooltip.attributes("-topmost", True)

        self.tooltip.geometry(f"+{x}+{y}")

        frame = ctk.CTkFrame(self.tooltip, corner_radius=8)
        frame.pack()

        label = ctk.CTkLabel(
            frame,
            text=self.texto,
            justify="left",
            wraplength=260
        )
        label.pack(padx=10, pady=6)

    def _ocultar(self, event=None):

        if self.after_id:
            self.widget.after_cancel(self.after_id)
            self.after_id = None

        if self.tooltip:
            self.tooltip.destroy()
            self.tooltip = None
