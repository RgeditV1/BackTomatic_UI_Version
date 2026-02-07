import customtkinter as ctk
import tkinter.filedialog as filedialog
from datetime import datetime

from core_ui.controller import UIController
from core_ui.tooltip import ToolTip


class MainWin(ctk.CTk):

    def __init__(self):
        super().__init__()

        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")

        self.title("Gestor de Backups")
        self.geometry("920x600")
        self.resizable(False, False)

        self.build_ui()

        # Conectar controlador
        self.controller = UIController(self)
        
    def on_browse_zip(self):
        archivo = filedialog.askopenfilename(
            filetypes=[("Archivos ZIP", "*.zip")]
            )
        if archivo:
            self.zip_entry.delete(0, "end")
            self.zip_entry.insert(0, archivo)
            self.drive_btn.configure(state="normal")

    def on_upload_drive(self):
        ruta_zip = self.zip_entry.get().strip()
        if not ruta_zip:
            self.append_log("Debes seleccionar un archivo ZIP.")
            return
        self.controller.subir_a_drive(ruta_zip)


    # ================= INTERFAZ =================

    def build_ui(self):

        # ---------- CABECERA ----------
        self.header = ctk.CTkFrame(self, height=90, corner_radius=8)
        self.header.pack(fill="x", padx=10, pady=(10, 5))

        self.title_lbl = ctk.CTkLabel(
            self.header,
            text="BACKTOMATIC",
            font=("Segoe UI", 26, "bold")
        )
        self.title_lbl.pack(anchor="w", padx=20, pady=(15, 0))

        self.subtitle = ctk.CTkLabel(
            self.header,
            text="Backup automático y subida a la nube"
        )
        self.subtitle.pack(anchor="w", padx=20)

        # ---------- CARPETA ORIGEN ----------
        self.source_frame = ctk.CTkFrame(self)
        self.source_frame.pack(fill="x", padx=10, pady=5)

        ctk.CTkLabel(self.source_frame, text="Carpeta origen:").grid(row=0, column=0, padx=10, pady=5, sticky="w")

        self.source_entry = ctk.CTkEntry(self.source_frame, width=520)
        self.source_entry.grid(row=0, column=1, padx=5, pady=5)

        ctk.CTkButton(
            self.source_frame,
            text="Explorar...",
            width=100,
            command=self.on_browse
        ).grid(row=0, column=2, padx=5, pady=5)

        # ---------- ARCHIVO ZIP ----------
        ctk.CTkLabel(self.source_frame, text="Archivo ZIP:").grid(row=1, column=0, padx=10, pady=5, sticky="w")

        self.zip_entry = ctk.CTkEntry(self.source_frame, width=520)
        self.zip_entry.grid(row=1, column=1, padx=5, pady=5)

        ctk.CTkButton(
            self.source_frame,
            text="Buscar ZIP...",
            width=100,
            command=self.on_browse_zip
        ).grid(row=1, column=2, padx=5, pady=5)



        # ---------- OPCIONES ----------
        self.options_frame = ctk.CTkFrame(self)
        self.options_frame.pack(fill="x", padx=10, pady=5)

        ctk.CTkLabel(
            self.options_frame,
            text="Opciones de backup:",
            font=("Segoe UI", 14, "bold")
        ).pack(anchor="w", padx=10, pady=(5, 0))

        inner = ctk.CTkFrame(self.options_frame, fg_color="transparent")
        inner.pack(fill="x", padx=10, pady=5)

        ctk.CTkLabel(inner, text="Nivel de compresión:").grid(row=0, column=0, sticky="w")

        self.compress_combo = ctk.CTkComboBox(
            inner,
            values=["Bajo (ZIP)", "Medio (ZIP)", "Alto (ZIP)"],
            width=160
        )
        self.compress_combo.set("Alto (ZIP)")
        self.compress_combo.configure(state="readonly")
        self.compress_combo.grid(row=0, column=1, padx=10)
        ToolTip(
            self.compress_combo,
            "Bajo: compresión rápida, ZIP ligero\n"
            "Medio: balance entre tamaño y velocidad\n"
            "Alto: máxima compresión, más lento\n\n"
            "Recomendado: Alto")


        self.exclude_tmp = ctk.CTkCheckBox(inner, text="Excluir archivos temporales")
        self.exclude_tmp.grid(row=0, column=2, padx=20, sticky="w")

        self.encrypt_check = ctk.CTkCheckBox(inner, text="Habilitar encriptación")
        self.encrypt_check.grid(row=1, column=2, padx=20, pady=5, sticky="w")

        # ---------- BOTÓN INICIAR ----------
        self.start_btn = ctk.CTkButton(
            self.options_frame,
            text="Iniciar Backup",
            height=60,
            width=200,
            fg_color="#2fa84f",
            hover_color="#23843e",
            font=("Segoe UI", 18, "bold"),
            command=self.on_start
        )
        self.start_btn.pack(side="left", padx=10, pady=10)

        #DRIVEEEE
        self.drive_btn = ctk.CTkButton(
            self.options_frame,
            text="Subir a Drive",
            height=60,
            width=200,
            fg_color="#4285F4",
            hover_color="#3367D6",
            font=("Segoe UI", 18, "bold"),
            command=self.on_upload_drive
        )
        self.drive_btn.pack(side="right", padx=10, pady=10)
        self.drive_btn.configure(state="disabled")


        # ---------- CENTRO ----------
        self.center = ctk.CTkFrame(self)
        self.center.pack(fill="both", expand=True, padx=10, pady=5)

        # Progreso
        self.progress_frame = ctk.CTkFrame(self.center)
        self.progress_frame.pack(side="left", fill="both", expand=True, padx=(0, 5))

        ctk.CTkLabel(
            self.progress_frame,
            text="Progreso del backup:",
            font=("Segoe UI", 14, "bold")
        ).pack(anchor="w", padx=10, pady=5)

        self.progress_text = ctk.CTkLabel(self.progress_frame, text="0% - En espera")
        self.progress_text.pack()

        self.progress_bar = ctk.CTkProgressBar(self.progress_frame)
        self.progress_bar.pack(fill="x", padx=10, pady=10)
        self.progress_bar.set(0)

        self.bytes_lbl = ctk.CTkLabel(self.progress_frame, text="0 MB de 0 MB")
        self.bytes_lbl.pack(anchor="w", padx=10)

        self.time_lbl = ctk.CTkLabel(self.progress_frame, text="Tiempo restante: --:--")
        self.time_lbl.pack(anchor="w", padx=10)

        # Logs
        self.log_frame = ctk.CTkFrame(self.center)
        self.log_frame.pack(side="left", fill="both", expand=True, padx=(5, 0))

        ctk.CTkLabel(
            self.log_frame,
            text="Registro de actividad",
            font=("Segoe UI", 14, "bold"),            
        ).pack(anchor="w", padx=10, pady=5)

        self.log_box = ctk.CTkTextbox(self.log_frame)
        self.log_box.configure(state="disabled")
        self.log_box.pack(fill="both", expand=True, padx=10, pady=5)

        # ---------- ESTADO ----------
        self.status_frame = ctk.CTkFrame(self, height=35)
        self.status_frame.pack(fill="x", padx=10, pady=(5, 10))

        self.drive_status = ctk.CTkLabel(
            self.status_frame,
            text="● No conectado a Google Drive"
        )
        self.drive_status.pack(side="left", padx=10)

        ctk.CTkButton(
            self.status_frame,
            text="Salir",
            width=80,
            command=self.destroy
        ).pack(side="right", padx=10)

    # ================= EVENTOS =================

    def on_browse(self):
        carpeta = filedialog.askdirectory()
        if carpeta:
            self.source_entry.delete(0, "end")
            self.source_entry.insert(0, carpeta)

    def on_start(self):
        self.controller.iniciar_backup()

    # ================= ACTUALIZACIONES =================

    def actualizar_estado(self, texto, progreso):
        porcentaje = int(progreso * 100)
        self.progress_text.configure(text=f"{porcentaje}% - {texto}")
        self.progress_bar.set(progreso)

        if progreso >= 1:
            self.append_log("Backup finalizado.")
        else:
            self.append_log(texto)

    # ================= UTILIDADES =================

    def append_log(self, texto):

        ahora = datetime.now().strftime("%H:%M")

        self.log_box.configure(state="normal")

        self.log_box.insert("end", f"{ahora}: {texto}\n")
        self.log_box.see("end")

        self.log_box.configure(state="disabled")



if __name__ == "__main__":
    app = MainWin()
    app.mainloop()
