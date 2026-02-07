import threading
from pathlib import Path
import os

from core.drive_auth import get_drive_service
from googleapiclient.http import MediaFileUpload

from core.backup_engine import crear_backup
from core_ui.password_dialog import PasswordDialog



class UIController:
    def __init__(self, ui):
        self.ui = ui

    def subir_a_drive(self, ruta_zip):
        service = get_drive_service()
        if not service:
            self.ui.append_log("No se pudo autenticar con Google Drive.")
            self.ui.drive_status.configure(text="● Error de conexión a Drive")
            return

        try:
            file_metadata = {'name': os.path.basename(ruta_zip)}
            media = MediaFileUpload(ruta_zip, mimetype='application/zip')
            file = service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id'
            ).execute()

            self.ui.append_log(f"Backup subido a Drive con ID: {file.get('id')}")
            self.ui.drive_status.configure(text="● Conectado a Google Drive")
        except Exception as e:
            self.ui.append_log(f"Error al subir a Drive: {e}")
            self.ui.drive_status.configure(text="● Error de subida")



    def iniciar_backup(self):
        """Método llamado por el botón 'Iniciar Backup'"""

        if self._ejecutando:
            self.view.append_log("Ya hay un backup en ejecución.")
            return

        carpeta = self.view.source_entry.get().strip()
        

        # -------- VALIDACIONES --------
        if not carpeta:
            self.view.append_log("Debes seleccionar una carpeta.")
            return

        ruta = Path(carpeta)

        if not ruta.exists():
            self.view.append_log("La ruta ingresada no existe.")
            return

        if not ruta.is_dir():
            self.view.append_log("La ruta no es una carpeta válida.")
            return

        if not any(ruta.iterdir()):
            self.view.append_log("La carpeta está vacía.")
            return

        # -------- OPCIONES UI --------
        nivel_ui = self.view.compress_combo.get()
        excluir_temporales = self.view.exclude_tmp.get()
        encriptar = self.view.encrypt_check.get()
        
         # ← NUEVO: Pedir contraseña si se marcó encriptación
        password = None
        if encriptar:
            dialog = PasswordDialog(self.view)
            password = dialog.get_password()
            
            if not password:
                self.view.append_log("Encriptación cancelada.")
                return

        self.view.append_log("Preparando backup...")
        self.view.append_log(f"Excluir temporales: {'Sí' if excluir_temporales else 'No'}")
        self.view.append_log(f"Nivel de compresión: {nivel_ui}")
        self.view.append_log(f"Encriptación: {'Sí (AES-256)' if encriptar else 'No'}")
        
        # -------- BLOQUEAR EJECUCIÓN --------
        self._ejecutando = True

        # -------- HILO --------
        hilo = threading.Thread(
            target=self._backup_real,
            args=(ruta, nivel_ui, excluir_temporales, encriptar, password),
            daemon=True
        )
        hilo.start()

    # ================= INTERNO =================

    def _backup_real(self, ruta: Path, nivel_ui: str, excluir_temporales: bool,
                     encriptar: bool, password: str):
        """Ejecuta el backup real con progreso"""
        self.view.start_btn.configure(state="disabled")
        self.view.drive_btn.configure(state="disabled")

        try:
            mapa_nivel = {
                "Bajo (ZIP)": 1,
                "Medio (ZIP)": 5,
                "Alto (ZIP)": 9,
            }

            nivel_real = mapa_nivel.get(nivel_ui, 5)

            destino_zip = ruta.parent / "backup.zip"

            def progreso(actual, total):
                porcentaje = actual / total

                self.view.after(
                    0,
                    self.view.actualizar_estado,
                    f"Comprimiendo {actual}/{total} archivos",
                    porcentaje
                )

            total_archivos = crear_backup(
                carpeta_origen=ruta,
                destino_zip=destino_zip,
                nivel_compresion=nivel_real,
                excluir_temporales=excluir_temporales,
                encriptar=encriptar,
                password=password,
                progreso_callback=progreso,
            )

            self.view.after(
                0,
                self.view.actualizar_estado,
                "Backup completado",
                1.0
            )

            self.view.append_log("Backup creado correctamente.")
            self.view.append_log(f"Archivos comprimidos: {total_archivos}")
            self.view.append_log(f"Ubicación: {destino_zip}")
            
            if encriptar:
                self.view.append_log("Backup protegido con AES-256")

        except Exception as e:
            self.view.append_log(f"Error durante el backup: {e}")

        finally:
            self.view.start_btn.configure(state="normal")
            if self.view.zip_entry.get().strip():
                self.view.drive_btn.configure(state="normal")

            self._ejecutando = False

