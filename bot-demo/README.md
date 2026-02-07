# Proyecto bot-demo: Bot de WhatsApp, Instagram y Messenger

## Descripción General

Este proyecto `bot-demo` es un bot conversacional desarrollado en Python utilizando el framework Flask. Actúa como un manejador de webhooks para plataformas de mensajería (WhatsApp Business API, Instagram y Messenger de Facebook), procesando mensajes entrantes, gestionando flujos de conversación y enviando respuestas. El bot está diseñado para ser modular, permitiendo la fácil adición de nuevos flujos de conversación y opciones de menú.

## Estructura del Proyecto

El proyecto está organizado en las siguientes carpetas y archivos principales:

-   `engine.py`: El corazón de la aplicación, maneja los webhooks y la lógica principal.
-   `requirements.txt`: Lista las dependencias del proyecto.
-   `config/`: Contiene el archivo de configuración `settings.json`.
-   `utils.py`: Funciones de utilidad para logging y gestión de rutas de usuario.
-   `flows/`: Directorio que contiene la lógica para diferentes flujos de conversación.
-   `menus/`: Directorio con las definiciones de los menús del bot.
-   `responses.py`: Define respuestas genéricas para el bot.
-   `welcome.py`: Contiene el mensaje de bienvenida inicial.

## Archivos Clave y Cómo Modificarlos

### `engine.py`

-   **Función:** Este es el archivo principal de la aplicación. Configura el servidor Flask, maneja las solicitudes `GET` y `POST` del webhook, carga la configuración y los flujos de submenú, y dirige los mensajes entrantes a los manejadores de flujo apropiados.
-   **Modificación Segura:**
    -   **Lógica de enrutamiento:** Si necesitas añadir un nuevo flujo principal o comando, añade una nueva condición `if text == "tu_comando":` y llama a la función `handle_tu_flujo(cfg, sender, send_msg)`. Asegúrate de que `handle_tu_flujo` esté importada correctamente.
    -   **Recarga de flujos:** Para recargar los flujos de submenú dinámicamente, el bot responde al comando `/reload`.
    -   **Configuración:** La configuración se carga desde `config/settings.json` y variables de entorno. Evita modificar directamente las credenciales aquí; usa las variables de entorno.

### `requirements.txt`

-   **Función:** Lista las librerías de Python necesarias para que el bot funcione (`flask`, `requests`).
-   **Modificación Segura:**
    -   Para añadir nuevas dependencias, simplemente agrégalas al archivo, una por línea, con su versión específica si es necesario (ej: `nueva_libreria==1.0.0`).
    -   Después de modificar este archivo, siempre ejecuta `pip install -r requirements.txt` para instalar las nuevas dependencias.

### `config/settings.json`

-   **Función:** Almacena la configuración sensible y general del bot, como tokens de API, IDs de teléfono, tokens de verificación y URLs de Ngrok.
-   **Modificación Segura:**
    -   **Nunca comitas información sensible directamente en el código.** Utiliza variables de entorno (`os.getenv`) para `WHATSAPP_BUSINESS_API_TOKEN`, `WHATSAPP_BUSINESS_PHONE_ID`, `VERIFY_TOKEN`, `META_APP_ID`, `META_APP_SECRET`, y `NGROK_PUBLIC_URL` en entornos de producción. Los valores en este archivo se usan como respaldo o para desarrollo local.
    -   Modifica este archivo solo para cambiar valores predeterminados o para añadir nuevas configuraciones no sensibles.

### `utils.py`

-   **Función:** Contiene funciones auxiliares para la creación de directorios de usuario, la configuración del sistema de logging y el registro de mensajes.
-   **Modificación Segura:**
    -   **`get_user_data_path(sender)`:** No modifiques la lógica de creación de rutas a menos que quieras cambiar radicalmente dónde se almacenan los datos de chat y estado del usuario.
    -   **`setup_logging()`:** Puedes ajustar el nivel de logging (`logging.INFO`, `logging.DEBUG`, etc.) o añadir nuevos manejadores de log si lo necesitas.
    -   **`log_message(sender, text)`:** Si deseas cambiar el formato del log o dónde se guardan los mensajes, modifícalo aquí.

### Directorio `flows/`

Este directorio contiene la lógica para los diferentes flujos de conversación que el bot puede manejar. Cada flujo (o grupo de flujos) tiene su propio módulo.

#### `flows/__init__.py`

-   **Función:** Marca `flows` como un paquete de Python. Puede usarse para inicializaciones a nivel de paquete o exportar funciones comunes.
-   **Modificación Segura:** Generalmente no necesita ser modificado.

#### `flows/whatsapp.py`, `flows/instagram.py`, `flows/messenger.py`

-   **Función:** Cada uno de estos archivos define una función (`handle_whatsapp`, `handle_instagram`, `handle_messenger` respectivamente) que envía un mensaje predefinido describiendo las características del bot para esa plataforma. Son flujos simples sin gestión de estado.
-   **Modificación Segura:**
    -   Puedes modificar el texto del mensaje que se envía para cada plataforma.
    -   Para añadir lógica más compleja, deberías considerar crear un subdirectorio como `flows/shop/` e implementar la lógica de estado allí.

#### `flows/contact.py`

-   **Función:** Define la función `handle_contact` que solicita al usuario que deje su información de contacto para ser atendido por un asesor.
-   **Modificación Segura:** Solo modifica el texto del mensaje si es necesario.

#### Directorio `flows/shop/`

Este es un ejemplo de un flujo de conversación más complejo con gestión de estado.

##### `flows/shop/main.py`

-   **Función:** Contiene la lógica principal para el flujo de compra, incluyendo la lista de productos y los pasos para la selección del producto y el método de pago.
-   **Modificación Segura:**
    -   **`PRODUCTS`:** Puedes añadir, modificar o eliminar productos en este diccionario. Asegúrate de que las claves (`"1"`, `"2"`, etc.) sean únicas.
    -   **`handle_shop_entry`:** Modifica el mensaje de bienvenida del flujo de compra y las instrucciones.
    -   **`handle_shop_flow`:** Aquí es donde reside la lógica de los pasos. Si añades nuevos pasos o cambias la secuencia, hazlo con cuidado, actualizando la variable `state["step"]` y las condiciones `if step == "..."`. Asegúrate de manejar correctamente la entrada del usuario en cada paso.

##### `flows/shop/submenu.json`

-   **Función:** Este archivo de configuración permite que el flujo de compra se cargue dinámicamente en el menú principal del bot. Define el texto de la opción en el menú y el punto de entrada (función `handle_shop_entry` en `main.py`) que se llamará al seleccionar esa opción.
-   **Modificación Segura:**
    -   **`option_text`:** Puedes cambiar el texto que aparece en el menú para este flujo.
    -   **`entry_point`:** Si cambias el nombre de la función de entrada o la mueves a otro archivo dentro del flujo `shop`, debes actualizar esta ruta (`main.handle_shop_entry`).

#### `flows/state.py`

-   **Función:** Provee un sistema simple de gestión de estado basado en archivos JSON para cada usuario. Permite guardar y recuperar el progreso de la conversación.
-   **Modificación Segura:**
    -   Las funciones `get`, `set`, `clear` y `active` son la interfaz para la gestión de estado. No modifiques estas funciones a menos que estés implementando un sistema de estado completamente diferente (ej. base de datos).
    -   Los datos se almacenan en `chats/<sender>/state.json`.

### Directorio `menus/`

Contiene las definiciones de los diferentes menús que el bot puede presentar.

#### `menus/main_menu.py`

-   **Función:** Define el mensaje del menú principal, que incluye las opciones de los bots para diferentes plataformas y la demo de compra.
-   **Modificación Segura:**
    -   Puedes cambiar el texto de las opciones del menú.
    -   Si añades un nuevo flujo principal que se activa por un número, actualiza este menú y la lógica en `engine.py` para manejar esa nueva opción.

#### `menus/services_menu.py`

-   **Función:** Define un menú secundario que lista los servicios complementarios.
-   **Modificación Segura:** Solo modifica el texto de los servicios o las instrucciones que se muestran.

### `responses.py`

-   **Función:** Proporciona respuestas genéricas para mensajes de usuario que no son manejados por ningún flujo específico o comando.
-   **Modificación Segura:**
    -   Puedes añadir nuevas respuestas para palabras clave o frases específicas (ej. "dudas", "pregunta").
    -   Modifica la respuesta predeterminada (`"🤔 No entendí tu mensaje."`) para guiar mejor al usuario si es necesario.

### `welcome.py`

-   **Función:** Contiene el mensaje de bienvenida que se envía al iniciar una nueva conversación o al usar comandos como `/start`.
-   **Modificación Segura:** Modifica libremente el texto de bienvenida para adaptarlo al propósito de tu bot.

## Cómo Ejecutar el Proyecto

1.  **Clonar el repositorio** (si aún no lo has hecho).
2.  **Navegar al directorio del proyecto:** `cd bot-demo`
3.  **Crear un entorno virtual** (recomendado):
    `python3 -m venv env`
4.  **Activar el entorno virtual:**
    -   Linux/macOS: `source env/bin/activate`
    -   Windows: `.\env\Scripts\activate`
5.  **Instalar las dependencias:**
    `pip install -r requirements.txt`
6.  **Configurar variables de entorno:**
    Asegúrate de que las siguientes variables de entorno estén configuradas o, como alternativa, los valores en `config/settings.json` serán usados. **Para producción, siempre usa variables de entorno.**
    -   `WHATSAPP_BUSINESS_API_TOKEN`
    -   `WHATSAPP_BUSINESS_PHONE_ID`
    -   `VERIFY_TOKEN`
    -   `META_APP_ID`
    -   `META_APP_SECRET`
    -   `NGROK_PUBLIC_URL` (o similar, si usas otra herramienta de tunneling)
    
    Puedes crear un archivo `.env` en la raíz del proyecto para desarrollo local (ej: `export WHATSAPP_BUSINESS_API_TOKEN="tu_token"` y luego `source .env`).
7.  **Ejecutar el bot:**
    `python engine.py`
    El bot se ejecutará en el puerto 3000 por defecto (o el que se especifique en la variable de entorno `PORT`).

## Cómo Modificar el Proyecto de Forma Segura

-   **Modularidad:** Aprovecha la estructura modular. Si quieres añadir un nuevo flujo de conversación complejo, crea un nuevo subdirectorio en `flows/` (ej: `flows/tu_nuevo_flujo/`) con su propio `main.py` y, si es necesario, `submenu.json`.
-   **Pruebas:** Antes de desplegar cambios, prueba exhaustivamente tus modificaciones. Si es posible, implementa pruebas unitarias para tus nuevos flujos y funciones.
-   **Control de Versiones:** Utiliza Git para el control de versiones. Realiza commits pequeños y descriptivos. No comitas secretos directamente en el repositorio.
-   **Variables de Entorno:** Siempre que sea posible, utiliza variables de entorno para la configuración sensible y que pueda cambiar entre diferentes entornos (desarrollo, producción).
-   **Logs:** Utiliza la función `log_message` y el módulo `logging` para depurar y monitorear el comportamiento de tu bot.
-   **No Modifiques Archivos del Entorno Virtual:** Nunca edites directamente los archivos dentro de la carpeta `env/` o las dependencias instaladas.
-   **Respeta la Convención de Nombres:** Sigue la convención de nombres existente para archivos, funciones y variables para mantener la coherencia.
