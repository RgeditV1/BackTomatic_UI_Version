from pathlib import Path
import zipfile

import pyzipper

EXTENSIONES_TEMP = {
    ".tmp",
    ".log",
    ".iso",
}


def crear_backup(
    carpeta_origen: Path,
    destino_zip: Path,
    nivel_compresion: int,
    excluir_temporales: bool,
    encriptar: bool = False,
    password: str = None,
    progreso_callback=None,
):
    """
    Crea un ZIP y reporta progreso por archivo.

    Si encriptar=True, usa AES-256 con la contraseña proporcionada.
    """

    archivos = []

    for p in carpeta_origen.rglob("*"):
        if not p.is_file():
            continue

        if excluir_temporales and p.suffix.lower() in EXTENSIONES_TEMP:
            continue

        archivos.append(p)

    if not archivos:
        raise RuntimeError("No hay archivos para comprimir.")

    total = len(archivos)
    
    # ← DECISIÓN: ¿ZIP normal o encriptado?
    if encriptar:
        if not password:
            raise ValueError("Se requiere contraseña para encriptar")
        
        # Crear ZIP encriptado con AES
        with pyzipper.AESZipFile(
            destino_zip,
            'w',
            compression=pyzipper.ZIP_DEFLATED,
            compresslevel=nivel_compresion,
            encryption=pyzipper.WZ_AES  # AES-256
        ) as zipf:
            zipf.setpassword(password.encode('utf-8'))
            
            for i, archivo in enumerate(archivos, start=1):
                zipf.write(archivo, archivo.relative_to(carpeta_origen))
                
                if progreso_callback:
                    progreso_callback(i, total)
    else:
        with zipfile.ZipFile(
            destino_zip,
            "w",
            zipfile.ZIP_DEFLATED,
            compresslevel=nivel_compresion,
        ) as zipf:

            for i, archivo in enumerate(archivos, start=1):

                zipf.write(
                    archivo,
                    archivo.relative_to(carpeta_origen)
                )

                if progreso_callback:
                    progreso_callback(i, total)

    return total
