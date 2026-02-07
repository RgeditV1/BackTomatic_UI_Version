import customtkinter as ctk
import tkinter.filedialog as filedialog
from datetime import datetime
from pathlib import Path

from PIL import Image, ImageTk, ImageSequence

from core_ui.controller import UIController
from core_ui.tooltip import ToolTip
from core.drive_auth import get_drive_service


class MainWin(ctk.CTk):
    """Ventana principal de BackTomatic."""

    def __init__(self):
        super().__init__()

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.title("BackTomatic - Backup Automático")

        # Intentar asignar icono, ignorar si no existe
        try:
            icon_path = Path.cwd().joinpath("src", "img", "ico.ico").resolve()
            if icon_path.exists():
                self.iconbitmap(icon_path)
        except Exception:
            pass

        self.geometry("920x690")
        self.resizable(False, False)
        
        # Construir UI y controlador
        self.build_ui()
        self.controller = UIController(self)

        # Intento de conexión automática a Google Drive al iniciar
        service = get_drive_service()
        if service:
            self.drive_status.configure(text="● Conectado a Google Drive")
            self.drive_btn.configure(state="normal")
            self.append_log("Conexión automática a Google Drive establecida.")
        else:
            self.append_log("No se encontraron credenciales válidas. Cárgalas desde la GUI.")

    # ----------------- Eventos relacionados con Drive -----------------

    def on_load_credentials(self):
        """Abrir diálogo para cargar credentials.json y actualizar estado."""
        service = get_drive_service()  # si no hay credentials, abrirá diálogo
        if service:
            self.append_log("Credenciales cargadas correctamente. Conectado a Google Drive.")
            self.drive_status.configure(text="● Conectado a Google Drive")
            self.drive_btn.configure(state="normal")
        else:
            self.append_log("Error al cargar credenciales.")
            self.drive_status.configure(text="● Error de credenciales")

    def on_browse_zip(self):
        """Seleccionar archivo ZIP desde GUI."""
        archivo = filedialog.askopenfilename(filetypes=[("Archivos ZIP", "*.zip")])
        if archivo:
            self.zip_entry.delete(0, "end")
            self.zip_entry.insert(0, archivo)
            # habilitar botón de subida si ya hay archivo
            self.drive_btn.configure(state="normal")

    def on_upload_drive(self):
        """Callback del botón 'Subir a Drive' — delega en el controlador."""
        ruta_zip = self.zip_entry.get().strip()
        if not ruta_zip:
            self.append_log("Debes seleccionar un archivo ZIP.")
            return
        self.controller.subir_a_drive(ruta_zip)

    # ----------------- Interfaz -----------------

    def build_ui(self):
        """Construye la interfaz completa."""
        gifPth = Path.cwd().joinpath("src", "gift", "trainloop.gif").resolve()

        # ---------- CABECERA ----------
        self.header = ctk.CTkFrame(self, height=90, corner_radius=8)
        self.header.pack(fill="x", padx=10, pady=(10, 5))

        # GIF animado ancho y bajo
        try:
            gif = Image.open(gifPth)
            self.gif_frames = [
                ImageTk.PhotoImage(frame.copy().resize((900, 80), Image.Resampling.LANCZOS))
                for frame in ImageSequence.Iterator(gif)
            ]
            self.gif_lbl = ctk.CTkLabel(self.header, text="", image=self.gif_frames[0])
            self.gif_lbl.pack(side="left", padx=20, pady=10)

            def update_gif(ind=0):
                frame = self.gif_frames[ind]
                self.gif_lbl.configure(image=frame)
                ind = (ind + 1) % len(self.gif_frames)
                self.after(100, update_gif, ind)

            update_gif()
        except Exception:
            # Si falla el GIF, no interrumpe la app
            ctk.CTkLabel(self.header, text="BackTomatic", font=("Montserrat", 20, "bold")).pack(padx=20, pady=20)

        # ---------- CARPETA ORIGEN ----------
        self.source_frame = ctk.CTkFrame(self)
        self.source_frame.pack(fill="x", padx=10, pady=5)

        ctk.CTkLabel(self.source_frame, text="Carpeta origen:").grid(row=0, column=0, padx=10, pady=5, sticky="w")

        self.source_entry = ctk.CTkEntry(self.source_frame, width=520)
        self.source_entry.grid(row=0, column=1, padx=5, pady=5)

        ctk.CTkButton(self.source_frame, text="Explorar...", width=100, command=self.on_browse).grid(
            row=0, column=2, padx=5, pady=5
        )

        # ---------- ARCHIVO ZIP ----------
        ctk.CTkLabel(self.source_frame, text="Archivo ZIP:").grid(row=1, column=0, padx=10, pady=5, sticky="w")

        self.zip_entry = ctk.CTkEntry(self.source_frame, width=520)
        self.zip_entry.grid(row=1, column=1, padx=5, pady=5)

        ctk.CTkButton(self.source_frame, text="Buscar ZIP...", width=100, command=self.on_browse_zip).grid(
            row=1, column=2, padx=5, pady=5
        )

        # ---------- OPCIONES ----------
        self.options_frame = ctk.CTkFrame(self)
        self.options_frame.pack(fill="x", padx=10, pady=5)

        ctk.CTkLabel(self.options_frame, text="Opciones de backup:", font=("Segoe UI", 14, "bold")).pack(
            anchor="w", padx=10, pady=(5, 0)
        )

        inner = ctk.CTkFrame(self.options_frame, fg_color="transparent")
        inner.pack(fill="x", padx=10, pady=5)

        ctk.CTkLabel(inner, text="Nivel de compresión:").grid(row=0, column=0, sticky="w")

        self.compress_combo = ctk.CTkComboBox(inner, values=["Bajo (ZIP)", "Medio (ZIP)", "Alto (ZIP)"], width=160)
        self.compress_combo.set("Alto (ZIP)")
        self.compress_combo.configure(state="readonly")
        self.compress_combo.grid(row=0, column=1, padx=10)
        ToolTip(
            self.compress_combo,
            "Bajo: compresión rápida, ZIP ligero\n"
            "Medio: balance entre tamaño y velocidad\n"
            "Alto: máxima compresión, más lento\n\n"
            "Recomendado: Alto",
        )

        self.exclude_tmp = ctk.CTkCheckBox(inner, text="Excluir archivos temporales")
        self.exclude_tmp.grid(row=0, column=2, padx=20, sticky="w")

        self.encrypt_check = ctk.CTkCheckBox(inner, text="Habilitar encriptación")
        self.encrypt_check.grid(row=1, column=2, padx=20, pady=5, sticky="w")

        # ---------- BOTONES PRINCIPALES ----------
        self.start_btn = ctk.CTkButton(
            self.options_frame,
            text="Iniciar Backup",
            height=60,
            width=200,
            fg_color="#2fa84f",
            hover_color="#23843e",
            font=("Segoe UI", 18, "bold"),
            command=self.on_start,
        )
        self.start_btn.pack(side="left", padx=10, pady=10)

        self.drive_btn = ctk.CTkButton(
            self.options_frame,
            text="Subir a Drive",
            height=60,
            width=200,
            fg_color="#4285F4",
            hover_color="#3367D6",
            font=("Segoe UI", 18, "bold"),
            command=self.on_upload_drive,
        )
        self.drive_btn.pack(side="right", padx=10, pady=10)
        self.drive_btn.configure(state="disabled")

        # ---------- CENTRO (Progreso + Logs) ----------
        self.center = ctk.CTkFrame(self)
        self.center.pack(fill="both", expand=True, padx=10, pady=5)

        # Progreso
        self.progress_frame = ctk.CTkFrame(self.center)
        self.progress_frame.pack(side="left", fill="both", expand=True, padx=(0, 5))

        ctk.CTkLabel(self.progress_frame, text="Progreso del backup:", font=("Segoe UI", 14, "bold")).pack(
            anchor="w", padx=10, pady=5
        )

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

        ctk.CTkLabel(self.log_frame, text="Registro de actividad", font=("Segoe UI", 14, "bold")).pack(
            anchor="w", padx=10, pady=5
        )

        self.log_box = ctk.CTkTextbox(self.log_frame)
        self.log_box.configure(state="disabled")
        self.log_box.pack(fill="both", expand=True, padx=10, pady=5)

        # ---------- BARRA DE ESTADO (fija y visible) ----------
        # Se crea al final para evitar que frames expansivos la oculten.
        self.status_frame = ctk.CTkFrame(self, height=40)
        self.status_frame.pack(fill="x", padx=10, pady=(5, 10))
        self.status_frame.pack_propagate(False)  # evita que el contenido colapse la barra

        # Usamos grid dentro del status_frame para alinear correctamente
        self.status_frame.grid_columnconfigure(0, weight=1)  # empuja botones a la derecha

        # Estado de conexión
        self.drive_status = ctk.CTkLabel(self.status_frame, text="● No conectado a Google Drive")
        self.drive_status.grid(row=0, column=0, sticky="w", padx=10)

        # Botón cargar credenciales (siempre visible)
        self.cred_btn = ctk.CTkButton(self.status_frame, text="Cargar credenciales", width=150, command=self.on_load_credentials)
        self.cred_btn.grid(row=0, column=1, sticky="e", padx=5)

        # Botón salir (siempre visible)
        self.exit_btn = ctk.CTkButton(self.status_frame, text="Salir", width=80, command=self.destroy)
        self.exit_btn.grid(row=0, column=2, sticky="e", padx=5)

        # Asegurar que la barra de estado quede encima si algo la tapa
        self.status_frame.lift()

    # ----------------- Otros eventos -----------------

    def on_browse(self):
        carpeta = filedialog.askdirectory()
        if carpeta:
            self.source_entry.delete(0, "end")
            self.source_entry.insert(0, carpeta)

    def on_start(self):
        self.controller.iniciar_backup()

    # ----------------- Actualizaciones UI -----------------

    def actualizar_estado(self, texto, progreso):
        """Actualizar barra de progreso y log."""
        porcentaje = int(progreso * 100)
        self.progress_text.configure(text=f"{porcentaje}% - {texto}")
        self.progress_bar.set(progreso)

        if progreso >= 1:
            self.append_log("Backup finalizado.")
        else:
            self.append_log(texto)

    # ----------------- Utilidades -----------------

    def append_log(self, texto):
        """Añade una línea al registro con timestamp."""
        ahora = datetime.now().strftime("%H:%M")
        self.log_box.configure(state="normal")
        self.log_box.insert("end", f"{ahora}: {texto}\n")
        self.log_box.see("end")
        self.log_box.configure(state="disabled")


if __name__ == "__main__":
    app = MainWin()
    app.mainloop()
