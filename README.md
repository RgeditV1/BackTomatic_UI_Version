# BackTomatic - Backup Automático con Google Drive

BackTomatic es una aplicación de escritorio desarrollada en **Python** con **CustomTkinter** que permite crear respaldos automáticos de carpetas en formato ZIP, con opciones de compresión y encriptación, y subirlos directamente a **Google Drive**.

---

## ✨ Características principales

- **Interfaz gráfica moderna** con CustomTkinter.
- **Selección de carpeta origen** y generación de archivo ZIP.
- **Opciones de compresión**: Bajo, Medio, Alto.
- **Exclusión de archivos temporales** para respaldos más limpios.
- **Encriptación AES-256** opcional con contraseña.
- **Subida directa a Google Drive** con autenticación OAuth2.
- **Barra de progreso en tiempo real**:
  - Durante el backup: muestra *Haciendo backup*.
  - Durante la subida: muestra *Subiendo a Drive*.
- **Registro de actividad (log)** con marcas de tiempo.
- **Barra de estado fija** con:
  - Estado de conexión a Google Drive.
  - Botón para cargar credenciales.
  - Botón de salida.

---

## 📸 Interfaz

- **Cabecera animada** con GIF.
- **Sección de opciones** para configurar compresión, exclusión y encriptación.
- **Botones principales**:
  - `Iniciar Backup`
  - `Subir a Drive`
- **Centro de la ventana**:
  - Progreso del backup/subida.
  - Registro de actividad con scroll.
- **Barra de estado inferior**:
  - Estado de conexión a Drive.
  - Botón `Cargar credenciales`.
  - Botón `Salir`.

---

## 🚀 Uso

1. **Abrir la aplicación** (`python mainWin.py`).
2. **Seleccionar carpeta origen**.
3. **Configurar opciones**:
   - Nivel de compresión.
   - Excluir temporales.
   - Encriptación (si se desea).
4. **Iniciar backup** con el botón verde.
5. **Subir a Drive**:
   - Cargar credenciales (`credentials.json`) la primera vez.
   - El programa guarda `token.json` para futuras conexiones.
   - Pulsar `Subir a Drive` para enviar el ZIP.

---

## 🔒 Autenticación con Google Drive

- La primera vez se debe seleccionar el archivo `credentials.json` (descargado desde Google Cloud Console).
- El programa guarda automáticamente:
  - `credentials.json`
  - `token.json`
- Ambos se almacenan en la carpeta del ejecutable, para que la conexión sea automática en futuras ejecuciones.

---

## 🛠️ Requisitos

- Python 3.9+
- Librerías:
  - `customtkinter`
  - `Pillow`
  - `google-auth-oauthlib`
  - `google-api-python-client`

Instalación rápida:

```bash
pip install -r ./requirements.txt
```
```bash
src/
├── mainWin.py              # Ventana principal
├── core/
│   ├── drive_auth.py       # Autenticación con Google Drive
│   ├── backup_engine.py    # Lógica de creación de backups
├── core_ui/
│   ├── controller.py       # Controlador de la UI
│   ├── password_dialog.py  # Diálogo para contraseña de encriptación
│   ├── tooltip.py          # Tooltips en la interfaz
```

🤝 Contribución
Haz un fork del repositorio.

Crea una rama (feature/nueva-funcionalidad).

Haz tus cambios y pruebas.

Envía un pull request.

📜 Licencia
Este proyecto está bajo la licencia MIT. Puedes usarlo, modificarlo y distribuirlo libremente, siempre dando crédito al autor original.

💡 Nota
BackTomatic está pensado para usuarios que necesitan respaldos rápidos y seguros, con la comodidad de una interfaz gráfica y la integración directa con Google Drive.