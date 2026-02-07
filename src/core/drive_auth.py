from __future__ import print_function
import os
from pathlib import Path
from tkinter import filedialog, messagebox
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/drive.file']

# Ruta fija en la carpeta del ejecutable
APP_DIR = Path.cwd()
CREDENTIALS_PATH = APP_DIR / "credentials.json"
TOKEN_PATH = APP_DIR / "token.json"

def load_credentials_via_gui():
    """Permite al usuario seleccionar credentials.json y lo guarda en APP_DIR."""
    file_path = filedialog.askopenfilename(
        title="Selecciona tu archivo credentials.json",
        filetypes=[("JSON files", "*.json")]
    )
    if not file_path:
        messagebox.showerror("Error", "No seleccionaste ningún archivo de credenciales.")
        return None
    try:
        # Copiar el archivo seleccionado a la ruta del ejecutable
        import shutil
        shutil.copy(file_path, CREDENTIALS_PATH)
        messagebox.showinfo("Éxito", f"Credenciales guardadas en {CREDENTIALS_PATH}")
        return str(CREDENTIALS_PATH)
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo guardar credenciales: {e}")
        return None

def get_drive_service():
    """Devuelve un servicio autenticado de Google Drive con persistencia."""
    creds = None

    # Si ya existe token.json, lo carga
    if TOKEN_PATH.exists():
        creds = Credentials.from_authorized_user_file(str(TOKEN_PATH), SCOPES)

    # Si no hay credenciales válidas, inicia flujo OAuth
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # Si no existe credentials.json, pedirlo desde GUI
            if not CREDENTIALS_PATH.exists():
                cred_path = load_credentials_via_gui()
                if not cred_path:
                    return None
            else:
                cred_path = str(CREDENTIALS_PATH)

            try:
                flow = InstalledAppFlow.from_client_secrets_file(
                    cred_path, SCOPES
                )
                creds = flow.run_local_server(port=0)
            except Exception as e:
                messagebox.showerror("Error", f"Credenciales inválidas: {e}")
                return None

        # Guarda el token para futuras ejecuciones (persistencia)
        with open(TOKEN_PATH, 'w') as token:
            token.write(creds.to_json())

    return build('drive', 'v3', credentials=creds)
