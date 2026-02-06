import threading
import time
from pathlib import Path


class UIController:

    def __init__(self, view):
        self.view = view
        self._ejecutando = False

    # ================= PUBLICO =================

    def iniciar_backup(self):

        if self._ejecutando:
            self.view.append_log("Ya hay un backup en ejecución.")
            return

        carpeta = self.view.source_entry.get().strip()
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


        if not carpeta:
            self.view.append_log("Debes seleccionar una carpeta primero.")
            return

        nivel = self.view.compress_combo.get()
        encriptar = self.view.encrypt_check.get()

        self.view.append_log("Preparando backup...")
        self.view.append_log(f"Nivel de compresión: {nivel}")
        self.view.append_log(f"Encriptación: {'Sí' if encriptar else 'No'}")

        self._ejecutando = True

        hilo = threading.Thread(
            target=self._proceso_backup,
            args=(carpeta, nivel, encriptar),
            daemon=True
        )
        hilo.start()

    # ================= INTERNO =================

    def _proceso_backup(self, carpeta, nivel, encriptar):

        pasos = [
            ("Analizando archivos...", 0.10),
            ("Comprimiendo...", 0.35),
            ("Creando archivo ZIP...", 0.55),
            ("Conectando con Google Drive...", 0.70),
            ("Subiendo backup...", 0.90),
            ("Backup completado", 1.0),
        ]

        for texto, progreso in pasos:
            time.sleep(1.2)
            self.view.after(0, self.view.actualizar_estado, texto, progreso)

        self._ejecutando = False
