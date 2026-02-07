# Proyecto Bot Sorteos

Este es un chatbot basado en Python que utiliza Flask como servidor web. Está diseñado para funcionar con WhatsApp, Instagram y Facebook Messenger.

## Funcionalidades Principales

1.  **Sorteos (`sorteos`)**: Los usuarios pueden comprar tickets para sorteos. El bot genera un enlace de pago de MercadoPago para la compra del ticket.
2.  **Préstamos (`prestamos`)**: Los usuarios pueden solicitar préstamos. La disponibilidad de esta opción está vinculada al sistema de referidos.
3.  **Referidos (`referidos`)**: Los usuarios tienen un código de referido y pueden referir a otros usuarios. Esto se utiliza para desbloquear funciones como los préstamos.

## Arquitectura

*   **Framework**: Flask
*   **Plataformas de Mensajería**: WhatsApp, Instagram, Facebook Messenger
*   **Pasarela de Pago**: MercadoPago
*   **Estructura**:
    *   La aplicación es modular, con una clara separación de responsabilidades.
    *   Un `engine` central se encarga del procesamiento y enrutamiento de mensajes.
    *   La lógica de negocio está organizada en "flujos" (`flows`), que se cargan dinámicamente.
    *   Utiliza un simple diccionario en memoria para la gestión del estado, lo que es una limitación para el uso en producción.

## Estructura de Archivos y Usos

### Raíz del Proyecto

*   `.env`: Contiene las claves de la API de MercadoPago y un secreto para el webhook.
*   `config/settings.json`: Contiene tokens e IDs para la API de WhatsApp Business y Facebook, una URL pública de ngrok y un número de teléfono de prueba.
*   `run_dev.sh`: Script para exportar las variables de entorno desde `.env` y luego ejecutar `server.py`. Es el punto de entrada para ejecutar el servidor de desarrollo.
*   `server.py`: Aplicación Flask que gestiona los webhooks para WhatsApp, Instagram y Messenger. Es el punto de entrada de la aplicación.
*   `engine.py`: Contiene la lógica principal del bot. Procesa los mensajes entrantes y los eventos.
*   `welcome.py`: Contiene una función `send_welcome` que devuelve un mensaje de bienvenida. Parece no estar en uso.
*   `welcome_sorteos.py`: `send_welcome_sorteos` devuelve un mensaje de dos partes: una imagen de banner y un menú de texto. Este es el mensaje de bienvenida utilizado en `engine.py`.
*   `create_payment_link.py`: Script para crear un enlace de pago utilizando la API de MercadoPago.
*   `responses.py`: Proporciona una respuesta simple para comandos no reconocidos.
*   `utils.py`: Contiene funciones de logging simples que imprimen en la consola.
*   `patch_engine_flow_dispatch.txt`: Archivo de texto, propósito no determinado a partir del contenido.

### Directorio `flows`

Contiene la lógica de negocio de la aplicación, organizada en flujos.

*   `contact.py`: Gestiona la opción de "contacto", enviando un mensaje pidiendo al usuario que deje su información de contacto.
*   `instagram.py`: Placeholder para una futura integración con Instagram.
*   `messenger.py`: Placeholder para el manejo de Messenger.
*   `shop.py`: Un simple hook para un flujo de tienda. Responde a "comprar" o "buy".
*   `state.py`: Un sistema simple de gestión de estado en memoria.
*   `submenu.py`: Gestiona la visualización de los flujos de submenú cargados dinámicamente.
*   `whatsapp.py`: Placeholder para el manejo específico de WhatsApp.

#### Subdirectorios en `flows`

Cada subdirectorio representa un flujo específico y contiene un archivo `_flow.py` con la lógica y un `submenu.json` para su configuración.

*   `flows/prestamos/`:
    *   `prestamos_flow.py`: Permite a los usuarios solicitar préstamos, dependiendo de su número de referidos.
    *   `submenu.json`: Define el texto de la opción de menú para este flujo.
*   `flows/referidos/`:
    *   `referidos_flow.py`: Gestiona un sistema de referidos.
    *   `submenu.json`: Define el texto de la opción de menú para este flujo.
*   `flows/sorteos/`:
    *   `sorteos_flow.py`: Permite a los usuarios participar en sorteos, generando un enlace de pago de MercadoPago.
    *   `submenu.json`: Define el texto de la opción de menú para este flujo.

### Directorio `menus`

*   `main_menu.py`: `send_menu_payload` devuelve una cadena con las opciones del menú principal.
*   `services_menu.py`: `send_list_menu_payload` devuelve una cadena de marcador de posición para un submenú dinámico.

### Directorio `static`

*   `banner_bienvenida.jpeg`: Imagen de banner utilizada en el mensaje de bienvenida.

## Posibles Mejoras

*   **Estado en memoria**: El manejo del estado debería ser reemplazado por una solución persistente como Redis para un entorno de producción.
*   **URLs Fijas**: La URL de ngrok en `welcome_sorteos.py` debería ser configurable.
*   **Manejo de Errores**: El manejo de errores es básico y debería ser más robusto.
*   **Variable Global `last_sender`**: La variable global `last_sender` en `server.py` podría causar problemas en un entorno con múltiples usuarios simultáneos.
