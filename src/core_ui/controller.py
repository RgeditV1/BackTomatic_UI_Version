import threading
from pathlib import Path

from core.backup_engine import crear_backup


class UIController:
    def __init__(self, view):
        self.view = view
        self._ejecutando = False

    # ================= PUBLICO =================

    def iniciar_backup(self):
        """
        Método llamado por el botón 'Iniciar Backup'
        """

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
        encriptar = self.view.encrypt_check.get()  # (todavía no se usa)

        self.view.append_log("Preparando backup...")
        self.view.append_log(f"Excluir temporales: {'Sí' if excluir_temporales else 'No'}")
        self.view.append_log(f"Nivel de compresión: {nivel_ui}")

        # -------- BLOQUEAR EJECUCIÓN --------
        self._ejecutando = True

        # -------- HILO --------
        hilo = threading.Thread(
            target=self._backup_real,
            args=(ruta, nivel_ui, excluir_temporales),
            daemon=True
        )
        hilo.start()

    # ================= INTERNO =================

    def _backup_real(self, ruta: Path, nivel_ui: str, excluir_temporales: bool):
        """
        Ejecuta el backup real (ZIP)
        """

        try:
            self.view.after(
                0,
                self.view.actualizar_estado,
                "Comprimiendo archivos...",
                0.1
            )

            # -------- MAPEO NIVEL --------
            mapa_nivel = {
                "Bajo (ZIP)": 1,
                "Medio (ZIP)": 5,
                "Alto (ZIP)": 9,
            }

            nivel_real = mapa_nivel.get(nivel_ui, 5)

            # -------- DESTINO --------
            destino_zip = ruta.parent / "backup.zip"

            # -------- CREAR ZIP --------
            total_archivos = crear_backup(
                carpeta_origen=ruta,
                destino_zip=destino_zip,
                nivel_compresion=nivel_real,
                excluir_temporales=excluir_temporales,
            )

            # -------- FINAL --------
            self.view.after(
                0,
                self.view.actualizar_estado,
                f"{total_archivos} archivos comprimidos",
                1.0
            )

            self.view.append_log(f"Backup creado correctamente.")
            self.view.append_log(f"Ubicación: {destino_zip}")

        except Exception as e:
            self.view.append_log(f"Error durante el backup: {e}")

        finally:
            self._ejecutando = False
