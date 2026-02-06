from pathlib import Path
import zipfile


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
):
    """
    Crea un ZIP desde carpeta_origen.

    Retorna:
        total_archivos
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

    with zipfile.ZipFile(
        destino_zip,
        "w",
        zipfile.ZIP_DEFLATED,
        compresslevel=nivel_compresion,
    ) as zipf:

        for archivo in archivos:
            zipf.write(
                archivo,
                archivo.relative_to(carpeta_origen)
            )

    return len(archivos)
