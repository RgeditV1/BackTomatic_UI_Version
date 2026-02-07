import customtkinter as ctk


class PasswordDialog(ctk.CTkToplevel):
    """Diálogo para ingresar contraseña de encriptación"""
    
    def __init__(self, parent):
        super().__init__(parent)
        
        self.password = None
        
        # Configuración
        self.title("Contraseña de Encriptación")
        self.geometry("400x180")
        self.resizable(False, False)
        
        # Modal
        self.transient(parent)
        self.grab_set()
        
        # Centrar
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - 200
        y = (self.winfo_screenheight() // 2) - 90
        self.geometry(f"+{x}+{y}")
        
        # UI
        self._build_ui()
        
    def _build_ui(self):
        # Título
        ctk.CTkLabel(
            self,
            text="Ingresa una contraseña para proteger el backup:",
            font=("Segoe UI", 12)
        ).pack(pady=(20, 10))
        
        # Entry
        self.password_entry = ctk.CTkEntry(
            self,
            width=320,
            height=35,
            show="●",
            font=("Segoe UI", 12)
        )
        self.password_entry.pack(pady=10)
        self.password_entry.focus()
        
        # Botones
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(pady=15)
        
        ctk.CTkButton(
            btn_frame,
            text="Aceptar",
            width=100,
            command=self._on_accept
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            btn_frame,
            text="Cancelar",
            width=100,
            fg_color="gray",
            hover_color="darkgray",
            command=self._on_cancel
        ).pack(side="left", padx=5)
        
        # Enter para aceptar
        self.password_entry.bind("<Return>", lambda e: self._on_accept())
        
    def _on_accept(self):
        pwd = self.password_entry.get().strip()
        if pwd:
            self.password = pwd
            self.destroy()
        else:
            # Mensaje de error
            self.password_entry.configure(border_color="red")
            self.after(1000, lambda: self.password_entry.configure(border_color=""))
            
    def _on_cancel(self):
        self.password = None
        self.destroy()
        
    def get_password(self):
        self.wait_window()
        return self.password