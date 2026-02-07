# Instrucciones para Descifrar all_env_files.env.gpg

Este archivo (`all_env_files.env.gpg`) contiene variables de entorno importantes y está cifrado simétricamente utilizando **GnuPG (GPG)** con el algoritmo AES256.

Para poder utilizar las variables de entorno, primero debes descifrar este archivo. Necesitarás la contraseña que se utilizó para cifrarlo.

## Librería/Herramienta utilizada para el cifrado y descifrado:
*   **GnuPG (GPG)**: Es una implementación del estándar OpenPGP. Generalmente ya está instalado en la mayoría de los sistemas Linux.

## Pasos para Descifrar:

1.  **Asegúrate de tener GnuPG instalado:**
    Si no lo tienes, puedes instalarlo en sistemas basados en Debian/Ubuntu con:
    ```bash
    sudo apt install gnupg
    ```
    Para otros sistemas operativos, consulta la documentación oficial de GnuPG.

2.  **Descifra el archivo:**
    Abre una terminal y ejecuta el siguiente comando en la misma ubicación donde se encuentra `all_env_files.env.gpg` (o ajusta la ruta):

    ```bash
    gpg --output all_env_files.env --decrypt all_env_files.env.gpg
    ```

    *   `--output all_env_files.env`: Especifica que el contenido descifrado se guardará en un nuevo archivo llamado `all_env_files.env`.
    *   `--decrypt`: Indica que la operación a realizar es descifrar.

3.  **Introduce la Contraseña:**
    El comando te pedirá la contraseña que se usó durante el cifrado. Ingrésala y presiona Enter.

4.  **Uso del archivo descifrado:**
    Una vez descifrado, tendrás un archivo `all_env_files.env` en texto plano con todas tus variables de entorno consolidadas.

## Recomendaciones de Seguridad:

*   **Nunca subas el archivo `all_env_files.env` (sin cifrar) a tu repositorio Git.** Asegúrate de que esté incluido en tu archivo `.gitignore`.
*   Mantén la contraseña de cifrado en un lugar muy seguro y no la compartas.
*   Descifra el archivo solo cuando lo necesites para el desarrollo local o la implementación segura en entornos controlados, y elimínalo después de su uso si es posible.
