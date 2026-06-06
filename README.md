# EZ QR Code SVG Generator

![Иконка утилиты, лис вкрутых очках](./readme_pics/readme_ez_qrcode_svg_logo.webp?raw=true "Neman's EZ QR Code SVG")

Простая и быстрая утилита на Python/Tkinter для локальной генерации векторных QR-кодов в формате SVG.

![Внешний вид утилиты в версии 1.4.3](./readme_pics/readme_ez_qrcode_svg_demo.webp?raw=true "Внешний вид утилиты")

## Особенности

- Полностью локально - для работы не требует подключения к Интернету
- Полностью векторный вывод (масштабируется без потери качества).
- Настройка цветов кода и фона с поддержкой прозрачности.
- Исправлен баг Tkinter с неработающими горячими клавишами (**<kbd>Ctrl</kbd>+<kbd>C</kbd> / <kbd>Ctrl</kbd>+<kbd>V</kbd>**) на не-английских раскладках.

## Установка и запуск из исходников

Выполните следующие команды в вашем терминале (командной строке):

1. **Клонируйте репозиторий и перейдите в папку проекта:**
   ```bash
   git clone git@github.com:nemansazonov/ez_qrcode_svg.git
   cd ez_qrcode_svg
   ```

2. **Создайте и активируйте виртуальное окружение:**
   - **Для Windows:**
     ```bash
     python -m venv env
     env\Scripts\activate
     ```
   - **Для macOS / Linux:**
     ```bash
     python3 -m venv env
     source env/bin/activate
     ```

3. **Установите зависимости:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Запустите скрипт:**
   ```bash
   python ez_qrcode_svg.py
   ```

## Сборка в автономный .exe

Для сборки готового исполняемого файла под Windows используется PyInstaller:

```bash
pyinstaller --onefile --noconsole --icon=ez_qrcode_svg.ico --add-data "ez_qrcode_svg.ico;." --exclude-module PIL --exclude-module tkinter.test ez_qrcode_svg.py
```
