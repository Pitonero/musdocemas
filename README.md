# Musdocemas 🎴

**Musdocemas** es una aplicación web para jugar al **Mus online**, desarrollada en **Python (Flask)** con frontend en **HTML, CSS y JavaScript**.  
Permite partidas multijugador en tiempo real mediante **WebSockets**, incluyendo chat y gestión de partidas.

> Proyecto personal actualmente estable (musdocemas.com).

---

## 🚀 Características

- Juego de Mus online
- Sala de espera para jugadores
- Chat en tiempo real
- Gestión de partidas, puntos y lances
- Sistema de registro y activación de usuarios por correo
- Soporte de **bots** para completar mesas

✅ Para iniciar una partida es obligatorio **al menos 1 jugador real**.  
El resto de jugadores hasta completar 4 pueden ser **bots**.

---

## 🛠️ Tecnologías utilizadas

- **Backend:** Python, Flask  
- **Frontend:** HTML, CSS, JavaScript  
- **Tiempo real:** WebSockets  
- **Base de datos:** PostgreSQL  
- **Correo:** SMTP (activación de usuarios)

---

## 📦 Instalación y ejecución en local

### 1️⃣ Clonar el repositorio
```bash
git clone https://github.com/Pitonero/musdocemas.git
cd musdocemas
```

### 2️⃣ Crear entorno virtual (recomendado)
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux / macOS
source venv/bin/activate
```

### 3️⃣ Instalar dependencias
```bash
pip install -r requirements.txt
```

---

## ⚙️ Configuración

La aplicación utiliza **variables de entorno** para su configuración.

Crea un archivo `.env` a partir del ejemplo:
```bash
cp .env.example .env
```

Nota: la activación por correo requiere variables SMTP adicionales que no están incluidas en `.env.example`, ya que actualmente no se utilizan en el despliegue activo.

---

## 🗄️ Base de datos (PostgreSQL)

Musdocemas utiliza **PostgreSQL**. Antes de arrancar la aplicación debes:

1. Crear una base de datos vacía (local o en Render)
2. Crear la tabla `usuarios`

El esquema mínimo está en `db/schema.sql` e incluye **índices únicos** sobre `alias` y `email` para evitar duplicidades.

> Nota: la aplicación necesita que exista la BD y la tabla `usuarios` para el registro, login y activación de usuarios.

---

## 📧 Activación de usuarios

El registro de usuarios incluye un **correo de activación**.

- Requiere un servidor SMTP configurado  
- En desarrollo puede adaptarse para:
  - desactivar el envío de correos  
  - o mostrar el código de activación por consola  

---

## ▶️ Ejecutar la aplicación
```bash
python app.py
```

Por defecto se iniciará en:
```
http://localhost:5000
```

---

## ☁️ Despliegue

El proyecto fue desplegado originalmente usando **Render / Railway**, utilizando este repositorio como fuente.

Es necesario configurar:
- variables de entorno (incluida `DATABASE_URL`)
- un servicio PostgreSQL gestionado

Puede adaptarse fácilmente a otros servicios compatibles con aplicaciones Flask.

---

## 📄 Licencia

Este proyecto se distribuye bajo la licencia **GNU AGPL-3.0**.

Cualquier uso del código como servicio accesible por red (por ejemplo, una aplicación web desplegada) debe poner a disposición pública las modificaciones realizadas, conforme a los términos de la licencia.

---

## 🧭 Notas finales
El fichero requirements.txt incluye dependencias históricas del entorno de desarrollo. No todas son necesarias para Musdocemas.

Este repositorio se publica con fines **educativos y demostrativos**.

El proyecto se encuentra **activo y estable en producción** (musdocemas.com), aunque el desarrollo está actualmente pausado.  
Puede servir como base o referencia para aplicaciones web multijugador en tiempo real.
