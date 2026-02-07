from __future__ import print_function
import os
from tkinter import filedialog, messagebox
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/drive.file']

def load_credentials_via_gui():
    """Permite al usuario seleccionar credentials.json desde la GUI."""
    file_path = filedialog.askopenfilename(
        title="Selecciona tu archivo credentials.json",
        filetypes=[("JSON files", "*.json")]
    )
    if not file_path:
        messagebox.showerror("Error", "No seleccionaste ningún archivo de credenciales.")
        return None
    if not os.path.exists(file_path):
        messagebox.showerror("Error", "El archivo no existe.")
        return None
    return file_path

def get_drive_service(credentials_path=None):
    """Devuelve un servicio autenticado de Google Drive con persistencia."""
    creds = None

    # Si ya existe token.json, lo carga
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)

    # Si no hay credenciales válidas, inicia flujo OAuth
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # Si no se pasó ruta, pedirla desde GUI
            if not credentials_path:
                credentials_path = load_credentials_via_gui()
                if not credentials_path:
                    return None

            try:
                flow = InstalledAppFlow.from_client_secrets_file(
                    credentials_path, SCOPES
                )
                creds = flow.run_local_server(port=0)
            except Exception as e:
                messagebox.showerror("Error", f"Credenciales inválidas: {e}")
                return None

        # Guarda el token para futuras ejecuciones (persistencia)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    return build('drive', 'v3', credentials=creds)
