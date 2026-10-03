# DARKRISE PROJECT

RPG de acción lateral 2D con estilo pixel-art, desarrollado en **Python + Pygame CE**.

El proyecto incluye selección de personajes, combate, enemigos, jefe, progresión RPG, armas, mejoras, recompensas y guardado de datos.

---

## ⚡ Instalación y ejecución rápida

### 1. Requisitos

- **Windows 10 o superior**
- **Python 3.12+** recomendado
- **Pygame CE**
- Una copia completa de la carpeta del proyecto

> **Importante:** ejecuta el proyecto desde su carpeta raíz para que las rutas de `assets/` funcionen correctamente.

---

### 2. Comprobar Python

Abre **PowerShell** o **CMD** y escribe:

```bash
python --version
```

También puedes probar:

```bash
py --version
```

Debe aparecer una versión de Python instalada.

---

### 3. Entrar a la carpeta del proyecto

Ejemplo:

```bash
cd E:\darkrise_project
```

Cambia la ruta por la ubicación real de tu proyecto.

---

### 4. Crear un entorno virtual (recomendado)

```bash
python -m venv .venv
```

Activarlo en PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Activarlo en CMD:

```cmd
.venv\Scripts\activate
```

---

### 5. Instalar Pygame CE

```bash
python -m pip install --upgrade pip
python -m pip install pygame-ce
```

Comprobar la instalación:

```bash
python -m pygame.examples.aliens
```

Si se abre el ejemplo de Pygame, la instalación funciona correctamente.

---

### 6. Ejecutar Darkrise

Desde la carpeta principal del proyecto:

```bash
python main.py
```

También puede funcionar:

```bash
py main.py
```

---

## 🎮 Controles

| Tecla | Acción |
|---|---|
| **ENTER** | Empezar / seleccionar |
| **A / D** | Moverse / cambiar personaje |
| **← / →** | Cambiar personaje o arma |
| **ESPACIO** | Saltar |
| **J** | Atacar |
| **SHIFT** | Esquiva / Dash |
| **E** | Interactuar / abrir cofre |
| **P** | Pausar / reanudar |
| **M** | Volver al menú |
| **C** | Abrir pantalla de personaje |
| **R** | Reaparecer después de morir |
| **I / U** | Mejoras del personaje/arma según la pestaña |
| **TAB** | Cambiar de pestaña |
| **ESC** | Volver / salir según la pantalla |

---

## 📁 Estructura básica del proyecto

La carpeta principal debería contener archivos Python del juego y carpetas de recursos similares a estas:

```text
darkrise_project/
│
├── main.py
├── player.py
├── enemy.py
├── boss.py
├── character_menu.py
├── rpg_system.py
├── settings.py
├── utils.py
├── camera.py
├── world.py
├── platform.py
├── tilemap.py
├── decoration.py
├── particle.py
├── hit_spark.py
├── damage_text.py
│
└── assets/
    ├── player/
    ├── character_menu/
    ├── background/
    └── audio/
```

> No elimines ni muevas la carpeta `assets/` fuera del proyecto: el juego carga imágenes y sonidos utilizando rutas relativas.

---

## 🧙‍♀️ Animaciones del menú de personajes

La animación especial de la Hechicera utiliza:

```text
assets/character_menu/menu_idle/hechicera_menu_idle.png
```

El menú carga esta spritesheet con frames de **256 × 384 px**.

Si el archivo falta o está en otra ubicación, el personaje mostrará el mensaje de que no se encontró la animación.

---

## 🔊 Audio

El juego utiliza recursos de audio dentro de:

```text
assets/audio/music/
assets/audio/sfx/
```

Entre ellos se encuentran la música de fondo y los efectos de ataque/golpe.

---

## 💾 Guardado RPG

El sistema RPG utiliza datos de progresión como niveles, EXP, oro, materiales y equipamiento.

Mantén los archivos de guardado generados por el proyecto en la ubicación esperada por `rpg_system.py` para conservar el progreso.

---

## 🛠️ Solución rápida de problemas

### `ModuleNotFoundError: No module named 'pygame'`

Instala Pygame CE:

```bash
python -m pip install pygame-ce
```

### `FileNotFoundError` para una imagen o sonido

Comprueba que:

1. Estás ejecutando `main.py` desde la carpeta principal del proyecto.
2. La carpeta `assets/` existe.
3. Los nombres de archivos y carpetas coinciden exactamente con los utilizados por el código.

### Python no reconoce el comando `python`

Prueba:

```bash
py --version
```

Y luego:

```bash
py main.py
```

### El juego se abre y se cierra inmediatamente

Ejecuta el juego desde **CMD o PowerShell** en lugar de abrir `main.py` directamente. Así podrás ver el mensaje de error:

```bash
python main.py
```

---

## 🚀 Ejecución en una computadora nueva

Para ejecutar el proyecto en otro PC:

```bash
cd ruta\a\darkrise_project
python -m pip install pygame-ce
python main.py
```

No necesitas abrir el proyecto desde un IDE como VS Code para ejecutarlo; **Python y Pygame CE son suficientes**.

---

## 📌 Nota para distribución

Esta versión del README describe la ejecución del proyecto como código fuente de Python.

Para distribuir Darkrise como una aplicación que pueda ejecutarse en otros equipos sin instalar Python, el proyecto debe empaquetarse posteriormente como **`.exe`** (por ejemplo, utilizando PyInstaller).

---

## 👤 Proyecto

**Darkrise Project**  
Python + Pygame CE  
2D Action RPG / Pixel Art
