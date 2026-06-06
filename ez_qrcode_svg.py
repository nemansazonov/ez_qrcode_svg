import sys
import os
import time
import re
import tkinter as tk
from tkinter import messagebox, colorchooser
import qrcode
import qrcode.image.svg
import lxml.etree as etree

TOOL_NAME_EN = "Neman's EZ QRCode SVG"
TOOL_NAME_RU = "Генератор SVG QR-кодов"
TOOL_VER = "1.4.3"

UI_OPACITY_SCALE_FROM = 0.0
UI_OPACITY_SCALE_TO = 1.0
UI_OPACITY_SCALE_RES = 0.05
UI_OPACITY_SCALE_LENGTH = 180
UI_CONFIRM_COLOR_FG = "#FFFFFF"
UI_CONFIRM_COLOR_BG = "#4CAF50"
UI_CONFIRM_BUTTON_W = 30
UI_CANCEL_CHAR ="✖"
UI_CANCEL_COLOR_FG = "#FFFFFF"
UI_CANCEL_COLOR_BG = "#f44336"
UI_CANCEL_BUTTON_W = 3

SVG_PADDING = 2
SVG_COLOR_QR = "#000000"
SVG_COLOR_BG = "#FFFFFF"

def choose_qr_color():
    global SVG_COLOR_QR
    color = colorchooser.askcolor(title="Выберите цвет QR-кода", color=SVG_COLOR_QR)
    if color[1]:
        SVG_COLOR_QR = color[1]
        btn_qr_preview.config(bg=SVG_COLOR_QR)
        entry_qr_hex.delete(0, tk.END)
        entry_qr_hex.insert(0, SVG_COLOR_QR)

def choose_bg_color():
    global SVG_COLOR_BG
    color = colorchooser.askcolor(title="Выберите цвет фона", color=SVG_COLOR_BG)
    if color[1]:
        SVG_COLOR_BG = color[1]
        btn_bg_preview.config(bg=SVG_COLOR_BG)
        entry_bg_hex.delete(0, tk.END)
        entry_bg_hex.insert(0, SVG_COLOR_BG)

def clear_name_field(): entry_name.delete(0, tk.END)
def clear_text_field(): entry_text.delete(0, tk.END)

def generate_qr():
    raw_file_name = entry_name.get().strip()
    qr_text = entry_text.get().strip()
    
    qr_color_final = entry_qr_hex.get().strip()
    bg_color_final = entry_bg_hex.get().strip()
    
    hex_pattern = re.compile(r'^#[0-9a-fA-F]{6}$')
    if not hex_pattern.match(qr_color_final) or not hex_pattern.match(bg_color_final):
        messagebox.showerror("Ошибка", "Цвет должен быть в формате #RRGGBB!")
        return
    
    if not raw_file_name or not qr_text:
        messagebox.showerror("Ошибка", "Заполните имя файла и текст QR!")
        return

    try:
        if raw_file_name.lower().endswith('.svg'):
            raw_file_name = raw_file_name[:-4].strip()
            
        clean_name = re.sub(r'[\/*?:"<>|\\#%&*{}\[\];@^`~+=]', '', raw_file_name)
        clean_name = re.sub(r'\s+', '_', clean_name)
        
        if not clean_name:
            clean_name = "qrcode"
            
        timestamp = int(time.time())
        full_filename = f"{clean_name}_{timestamp}.svg"
        
        # Получаем значения прозрачности из ползунков
        qr_opacity = float(scale_qr_opacity.get())
        bg_opacity = float(scale_bg_opacity.get())
        
        class CustomSvgFactory(qrcode.image.svg.SvgPathImage):
            UNIT = "px"
            QR_PATH_STYLE = {
                'fill': qr_color_final,
                'fill-opacity': str(qr_opacity),
                'fill-rule': 'nonzero',
                'stroke': 'none'
            }
        
        try:
            border_val = int(entry_border.get().strip())
        except ValueError:
            border_val = int(SVG_PADDING)
            
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_M,
            box_size=10,       
            border=border_val,  
        )
        qr.add_data(qr_text)
        qr.make(fit=True)
        
        img = qr.make_image(image_factory=CustomSvgFactory)
        svg_root = img._img
        
        # Вычищаем лишние нестандартные атрибуты библиотеки из тега <svg>
        attribs_to_del = ['fill_color', 'back_color', 'style']
        for attr in attribs_to_del:
            if attr in svg_root.attrib: 
                del svg_root.attrib[attr]
        
        width_px = svg_root.attrib['width']
        height_px = svg_root.attrib['height']
        svg_root.attrib['width'] = f"{width_px}px"
        svg_root.attrib['height'] = f"{height_px}px"
        
        # Создаем честную фоновую подложку
        bg_rect = svg_root.makeelement('rect', {
            'width': '100%',
            'height': '100%',
            'fill': bg_color_final,
            'fill-opacity': str(bg_opacity)
        })
        svg_root.insert(0, bg_rect)
            
        xml_bytes = etree.tostring(svg_root, encoding='UTF-8', xml_declaration=True, pretty_print=True)
        
        with open(full_filename, 'wb') as f:
            f.write(xml_bytes)
        
        messagebox.showinfo("Успех", f"SVG QR-код сохранен как:\n{full_filename}")
        
    except Exception as e:
        messagebox.showerror("Ошибка", f"Не удалось создать файл:\n{str(e)}")

# --- БЛОК ИНТЕРФЕЙСА (TKINTER) ---
# СНАЧАЛА ОБЪЯВЛЯЕМ КОРНЕВОЕ ОКНО ROOT
root = tk.Tk()

# === УНИВЕРСАЛЬНОЕ ИСПРАВЛЕНИЕ ГОРЯЧИХ КЛАВИШ (ДЛЯ ЛЮБОЙ РАСКЛАДКИ) ===
def fix_universal_hotkeys(window):
    # Словарик: физический код клавиши -> системное событие Tkinter
    keycodes = {
        65: "<<SelectAll>>",  # Клавиша A
        88: "<<Cut>>",        # Клавиша X
        67: "<<Copy>>",       # Клавиша C
        86: "<<Paste>>"       # Клавиша V
    }
    
    def handle_key(event):
        # 0x0004 — это зажатый Ctrl в Windows
        if event.state & 0x0004 and event.keycode in keycodes:
            event.widget.event_generate(keycodes[event.keycode])
            return "break" # Отменяем стандартное поведение

    # Применяем ко всем полям ввода Entry
    window.bind_class("Entry", "<Control-KeyPress>", handle_key)

fix_universal_hotkeys(root)
# =====================================================================

root.title(f"{str(TOOL_NAME_EN)} v.{str(TOOL_VER)} - {str(TOOL_NAME_RU)}")
root.geometry("540x400")
root.resizable(False, False)

# УМНОЕ ПОДКЛЮЧЕНИЕ ИКОНКИ ИЗНУТРИ EXE:
try:
    base_path = sys._MEIPASS
except AttributeError:
    base_path = os.path.abspath(".")

icon_path = os.path.join(base_path, "ez_qrcode_svg.ico")

if os.path.exists(icon_path):
    root.iconbitmap(icon_path)

# --- Новый блок полей ввода с кнопками очистки ---
inputs_frame = tk.Frame(root)
inputs_frame.pack(pady=10, padx=10)

# Строка имени файла
tk.Label(inputs_frame, text="Имя файла (без .svg):", anchor="w").grid(row=0, column=0, columnspan=2, sticky="w", pady=(5, 0))
entry_name = tk.Entry(inputs_frame, width=54)
entry_name.grid(row=1, column=0, padx=(0, 5), pady=2)
btn_clear_name = tk.Button(inputs_frame, text=UI_CANCEL_CHAR, command=clear_name_field, width=UI_CANCEL_BUTTON_W, bg=UI_CANCEL_COLOR_BG, fg=UI_CANCEL_COLOR_FG, font=("Arial", 8, "bold"))
btn_clear_name.grid(row=1, column=1, pady=2)

# Строка текста для QR
tk.Label(inputs_frame, text="Текст или ссылка для QR:", anchor="w").grid(row=2, column=0, columnspan=2, sticky="w", pady=(5, 0))
entry_text = tk.Entry(inputs_frame, width=54)
entry_text.grid(row=3, column=0, padx=(0, 5), pady=2)
btn_clear_text = tk.Button(inputs_frame, text=UI_CANCEL_CHAR, command=clear_text_field, width=UI_CANCEL_BUTTON_W, bg=UI_CANCEL_COLOR_BG, fg=UI_CANCEL_COLOR_FG, font=("Arial", 8, "bold"))
btn_clear_text.grid(row=3, column=1, pady=2)

# Размер рамки (центрируем под полями)
tk.Label(inputs_frame, text="Отступ от края в размерах\nминимального модуля QR-кода («квадратика»):").grid(row=4, column=0, columnspan=2, pady=(5, 0))
entry_border = tk.Entry(inputs_frame, width=10, justify="center")
entry_border.insert(0, SVG_PADDING)
entry_border.grid(row=5, column=0, columnspan=2, pady=2)

# --- Блок управления цветом ---
grid_frame = tk.Frame(root)
grid_frame.pack(pady=15, padx=10)

# Строка 1: QR-код
tk.Label(grid_frame, text="Цвет QR-кода:", anchor="w", width=12).grid(row=0, column=0, padx=5, pady=5)
entry_qr_hex = tk.Entry(grid_frame, width=10, font=("Consolas", 10))
entry_qr_hex.insert(0, SVG_COLOR_QR)
entry_qr_hex.grid(row=0, column=1, padx=5, pady=5)

# Маленькая квадратная кнопка палитры
btn_qr_preview = tk.Button(grid_frame, width=3, height=1, bg=SVG_COLOR_QR, relief=tk.RAISED, command=choose_qr_color)
btn_qr_preview.grid(row=0, column=2, padx=5, pady=5)

scale_qr_opacity = tk.Scale(grid_frame, from_=UI_OPACITY_SCALE_FROM, to=UI_OPACITY_SCALE_TO, resolution=UI_OPACITY_SCALE_RES, orient=tk.HORIZONTAL, label="Прозрачность кода", length=UI_OPACITY_SCALE_LENGTH)
scale_qr_opacity.set(1.0)
scale_qr_opacity.grid(row=0, column=3, padx=10, pady=5)

# Строка 2: Фон
tk.Label(grid_frame, text="Цвет фона:", anchor="w", width=12).grid(row=1, column=0, padx=5, pady=5)
entry_bg_hex = tk.Entry(grid_frame, width=10, font=("Consolas", 10))
entry_bg_hex.insert(0, SVG_COLOR_BG)
entry_bg_hex.grid(row=1, column=1, padx=5, pady=5)

# Маленькая квадратная кнопка палитры без текста
btn_bg_preview = tk.Button(grid_frame, width=3, height=1, bg=SVG_COLOR_BG, relief=tk.RAISED, command=choose_bg_color)
btn_bg_preview.grid(row=1, column=2, padx=5, pady=5)

scale_bg_opacity = tk.Scale(grid_frame, from_=UI_OPACITY_SCALE_FROM, to=UI_OPACITY_SCALE_TO, resolution=UI_OPACITY_SCALE_RES, orient=tk.HORIZONTAL, label="Прозрачность фона", length=UI_OPACITY_SCALE_LENGTH)
scale_bg_opacity.set(1.0)
scale_bg_opacity.grid(row=1, column=3, padx=10, pady=5)

# Главная кнопка
btn_generate = tk.Button(root, text="Создать SVG QR-код", command=generate_qr, bg=UI_CONFIRM_COLOR_BG, fg=UI_CONFIRM_COLOR_FG, font=("Arial", 10, "bold"), width=UI_CONFIRM_BUTTON_W)
btn_generate.pack(pady=10)

root.mainloop()
