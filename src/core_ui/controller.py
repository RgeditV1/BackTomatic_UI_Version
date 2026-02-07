import threading
import os
from pathlib import Path
from typing import Optional

from googleapiclient.http import MediaFileUpload

from core.drive_auth import get_drive_service
from core.backup_engine import crear_backup
from core_ui.password_dialog import PasswordDialog


class UIController:
    """
    Controlador de la UI: coordina backups y subidas a Google Drive.
    Actualiza la UI mediante self.ui.after(...) para ejecutar cambios en el hilo principal.
    """

    def __init__(self, ui):
        self.ui = ui
        self._ejecutando = False
        self._upload_lock = threading.Lock()

    # -------------------- Subida a Google Drive --------------------

    def subir_a_drive(self, ruta_zip: str):
        ruta_zip = ruta_zip.strip()
        if not ruta_zip:
            self.ui.append_log("Ruta de ZIP vacía.")
            return

        zip_path = Path(ruta_zip)
        if not zip_path.exists() or not zip_path.is_file():
            self.ui.append_log("El archivo ZIP no existe.")
            return

        if self._upload_lock.locked():
            self.ui.append_log("Ya hay una subida en curso.")
            return

        hilo = threading.Thread(target=self._upload_thread, args=(zip_path,), daemon=True)
        hilo.start()

    def _upload_thread(self, zip_path: Path):
        with self._upload_lock:
            # Indicadores iniciales en UI
            self.ui.after(0, self.ui.append_log, f"Iniciando subida de {zip_path.name} a Google Drive...")
            self.ui.after(0, self.ui.drive_status.configure, {"text": "● Subiendo a Google Drive"})
            self.ui.after(0, self.ui.drive_btn.configure, {"state": "disabled"})
            # Inicializar barra de progreso para la subida
            self.ui.after(0, self.ui.progress_bar.set, 0.0)
            self.ui.after(0, self.ui.progress_text.configure, {"text": "0% - Subiendo a Drive"})

            try:
                service = get_drive_service()
                if not service:
                    self.ui.after(0, self.ui.append_log, "No se pudo autenticar con Google Drive.")
                    self.ui.after(0, self.ui.drive_status.configure, {"text": "● No conectado a Google Drive"})
                    return

                media = MediaFileUpload(str(zip_path), mimetype="application/zip", resumable=True)
                file_metadata = {"name": zip_path.name}
                request = service.files().create(body=file_metadata, media_body=media, fields="id")

                response = None
                # Subida resumible: next_chunk devuelve (status, response)
                while response is None:
                    status, response = request.next_chunk()
                    if status:
                        progreso = float(status.progress())  # 0.0 - 1.0
                        porcentaje = int(progreso * 100)
                        # Actualizar barra de progreso y texto en UI con el texto solicitado
                        self.ui.after(0, self.ui.progress_bar.set, progreso)
                        self.ui.after(0, self.ui.progress_text.configure, {"text": f"{porcentaje}% - Subiendo a Drive"})
                        self.ui.after(0, self.ui.append_log, f"Subida {porcentaje}%")

                file_id = response.get("id")
                self.ui.after(0, self.ui.append_log, f"Backup subido a Drive con ID: {file_id}")
                self.ui.after(0, self.ui.drive_status.configure, {"text": "● Conectado a Google Drive"})
                # Finalizar barra de progreso
                self.ui.after(0, self.ui.progress_bar.set, 1.0)
                self.ui.after(0, self.ui.progress_text.configure, {"text": "100% - Subida completada"})
            except Exception as e:
                self.ui.after(0, self.ui.append_log, f"Error al subir a Drive: {e}")
                self.ui.after(0, self.ui.drive_status.configure, {"text": "● Error de subida"})
                self.ui.after(0, self.ui.progress_text.configure, {"text": "Error durante la subida"})
            finally:
                # Restaurar estado del botón de Drive según si hay ZIP seleccionado
                def _restore_button():
                    if self.ui.zip_entry.get().strip():
                        self.ui.drive_btn.configure(state="normal")
                    else:
                        self.ui.drive_btn.configure(state="disabled")

                self.ui.after(0, _restore_button)

    # -------------------- Proceso de backup --------------------

    def iniciar_backup(self):
        if self._ejecutando:
            self.ui.append_log("Ya hay un backup en ejecución.")
            return

        carpeta = self.ui.source_entry.get().strip()
        if not carpeta:
            self.ui.append_log("Debes seleccionar una carpeta.")
            return

        ruta = Path(carpeta)
        if not ruta.exists():
            self.ui.append_log("La ruta ingresada no existe.")
            return
        if not ruta.is_dir():
            self.ui.append_log("La ruta no es una carpeta válida.")
            return
        try:
            iterator = next(ruta.iterdir(), None)
            if iterator is None:
                self.ui.append_log("La carpeta está vacía.")
                return
        except Exception:
            self.ui.append_log("No se pudo leer la carpeta seleccionada.")
            return

        nivel_ui = self.ui.compress_combo.get()
        excluir_temporales = bool(self.ui.exclude_tmp.get())
        encriptar = bool(self.ui.encrypt_check.get())

        password: Optional[str] = None
        if encriptar:
            dialog = PasswordDialog(self.ui)
            password = dialog.get_password()
            if not password:
                self.ui.append_log("Encriptación cancelada.")
                return

        self.ui.append_log("Preparando backup...")
        self.ui.append_log(f"Excluir temporales: {'Sí' if excluir_temporales else 'No'}")
        self.ui.append_log(f"Nivel de compresión: {nivel_ui}")
        self.ui.append_log(f"Encriptación: {'Sí (AES-256)' if encriptar else 'No'}")

        self._ejecutando = True
        hilo = threading.Thread(
            target=self._backup_real,
            args=(ruta, nivel_ui, excluir_temporales, encriptar, password),
            daemon=True,
        )
        hilo.start()

    def _backup_real(self, ruta: Path, nivel_ui: str, excluir_temporales: bool, encriptar: bool, password: Optional[str]):
        self.ui.after(0, self.ui.start_btn.configure, {"state": "disabled"})
        self.ui.after(0, self.ui.drive_btn.configure, {"state": "disabled"})

        try:
            mapa_nivel = {"Bajo (ZIP)": 1, "Medio (ZIP)": 5, "Alto (ZIP)": 9}
            nivel_real = mapa_nivel.get(nivel_ui, 5)

            destino_zip = ruta.parent / "backup.zip"

            def progreso(actual: int, total: int):
                porcentaje = actual / total if total else 0.0
                texto = "Haciendo backup"
                # Actualizar la UI con el texto "Haciendo backup"
                self.ui.after(0, self.ui.actualizar_estado, texto, porcentaje)

            total_archivos = crear_backup(
                carpeta_origen=ruta,
                destino_zip=destino_zip,
                nivel_compresion=nivel_real,
                excluir_temporales=excluir_temporales,
                encriptar=encriptar,
                password=password,
                progreso_callback=progreso,
            )

            self.ui.after(0, self.ui.actualizar_estado, "Backup completado", 1.0)
            self.ui.after(0, self.ui.append_log, "Backup creado correctamente.")
            self.ui.after(0, self.ui.append_log, f"Archivos comprimidos: {total_archivos}")
            self.ui.after(0, self.ui.append_log, f"Ubicación: {destino_zip}")
            if encriptar:
                self.ui.after(0, self.ui.append_log, "Backup protegido con AES-256")

            if destino_zip.exists():
                self.ui.after(0, self.ui.drive_btn.configure, {"state": "normal"})

        except Exception as e:
            self.ui.after(0, self.ui.append_log, f"Error durante el backup: {e}")
            self.ui.after(0, self.ui.progress_text.configure, {"text": "Error durante el backup"})
        finally:
            self.ui.after(0, self.ui.start_btn.configure, {"state": "normal"})

            def _maybe_enable_drive():
                if self.ui.zip_entry.get().strip():
                    self.ui.drive_btn.configure(state="normal")
                else:
                    self.ui.drive_btn.configure(state="disabled")

            self.ui.after(0, _maybe_enable_drive)
            self._ejecutando = False
