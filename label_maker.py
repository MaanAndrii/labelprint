import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import tkinterdnd2 as dnd
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.lib.pagesizes import A4
from PIL import Image

from label_presets import (
    CUSTOM_PRESET,
    DEFAULT_PRESET,
    LABEL_SIZE_PRESETS,
    find_matching_preset,
)

MARGIN_MM = 20  # мінімальні поля 20 мм

class LabelData:
    def __init__(self, filepath, width_mm=None, height_mm=None, count=1, original_ratio=1):
        self.filepath = filepath
        self.filename = filepath.split('/')[-1]
        self.width_mm = width_mm
        self.height_mm = height_mm
        self.count = count
        self.original_ratio = original_ratio # width / height

def make_labels(labels_to_print, output="druk.pdf", gap_px=2):
    page_w, page_h = A4
    margin = MARGIN_MM * mm
    gap = gap_px
    c = canvas.Canvas(output, pagesize=A4)
    work_w = page_w - 2 * margin
    work_h = page_h - 2 * margin

    flat_list = []
    for label in labels_to_print:
        flat_list.extend([label] * label.count)

    current_index = 0
    while current_index < len(flat_list):
        current_x, current_y = margin, page_h - margin
        page_is_full = False
        
        while not page_is_full and current_index < len(flat_list):
            label = flat_list[current_index]
            label_w = label.width_mm * mm
            label_h = label.height_mm * mm

            if label_w > work_w or label_h > work_h:
                print(f"Warning: Skipping label {label.filename} as it's too large for the page.")
                current_index += 1
                continue

            if current_x + label_w <= page_w - margin:
                c.drawImage(label.filepath, current_x, current_y - label_h, width=label_w, height=label_h, preserveAspectRatio=True)
                current_x += label_w + gap
                current_index += 1
            else:
                current_y -= label_h + gap
                current_x = margin
                if current_y - label_h < margin:
                    page_is_full = True
                else:
                    c.drawImage(label.filepath, current_x, current_y - label_h, width=label_w, height=label_h, preserveAspectRatio=True)
                    current_x += label_w + gap
                    current_index += 1
        
        if current_index < len(flat_list):
            c.showPage()
    
    c.save()

class LabelApp:
    def __init__(self, root: dnd.Tk):
        self.root = root
        self.root.title("Друк етикеток (v2.2 Rounding)")
        self.root.geometry("600x450")
        self.labels = []
        self.selected_label_index = -1
        self.create_widgets()
        self.listbox_labels.drop_target_register(dnd.DND_FILES)
        self.listbox_labels.dnd_bind('<<Drop>>', self.handle_drop)

    def create_widgets(self):
        label_frame = ttk.LabelFrame(self.root, text="Керування етикетками (перетягніть файли або двічі клікніть для редагування)")
        label_frame.pack(padx=10, pady=10, fill="x")
        self.listbox_labels = tk.Listbox(label_frame, height=8, selectmode=tk.SINGLE)
        self.listbox_labels.pack(side=tk.LEFT, fill="both", expand=True, padx=5, pady=5)
        self.listbox_labels.bind("<Double-Button-1>", self.configure_label)
        self.listbox_labels.bind("<<ListboxSelect>>", self.on_label_select)
        scrollbar = ttk.Scrollbar(label_frame, orient="vertical", command=self.listbox_labels.yview)
        scrollbar.pack(side=tk.RIGHT, fill="y")
        self.listbox_labels.config(yscrollcommand=scrollbar.set)
        button_frame = ttk.Frame(label_frame)
        button_frame.pack(side=tk.RIGHT, fill="y", padx=5, pady=5)
        ttk.Button(button_frame, text="Додати етикетку", command=self.add_label_dialog).pack(fill="x", pady=5)
        ttk.Button(button_frame, text="Видалити етикетку", command=self.remove_label).pack(fill="x", pady=5)
        ttk.Button(button_frame, text="Налаштувати...", command=self.configure_label).pack(fill="x", pady=5)
        ttk.Button(button_frame, text="Очистити список", command=self.clear_labels).pack(fill="x", pady=5)
        settings_frame = ttk.LabelFrame(self.root, text="Загальні налаштування")
        settings_frame.pack(padx=10, pady=10, fill="x")
        ttk.Label(settings_frame, text="Проміжок між етикетками (px):").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.entry_gap = ttk.Entry(settings_frame, width=10)
        self.entry_gap.insert(0, "2")
        self.entry_gap.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        ttk.Button(self.root, text="Згенерувати PDF", command=self.generate_pdf).pack(pady=10)

    def handle_drop(self, event):
        filepaths_str = event.data.strip('{}')
        filepaths = filepaths_str.split('} {')
        for filepath in filepaths:
            if filepath.lower().endswith(('.png', '.jpg', '.jpeg')):
                self.add_label_from_path(filepath)

    def add_label_dialog(self):
        filename = filedialog.askopenfilename(filetypes=[("Image files", "*.png;*.jpg;*.jpeg")])
        if filename:
            self.add_label_from_path(filename)

    def add_label_from_path(self, filename):
        try:
            img = Image.open(filename)
            dpi = img.info.get("dpi", (96, 96))
            w_px, h_px = img.size
            orig_w_mm = w_px / dpi[0] * 25.4
            orig_h_mm = h_px / dpi[1] * 25.4
            initial_width_mm, initial_height_mm = LABEL_SIZE_PRESETS[DEFAULT_PRESET]
            label_data = LabelData(filepath=filename, width_mm=initial_width_mm, height_mm=initial_height_mm, count=1, original_ratio=orig_w_mm / orig_h_mm if orig_h_mm > 0 else 1)
            self.labels.append(label_data)
            self.update_listbox()
        except Exception as e:
            messagebox.showerror("Помилка при завантаженні зображення", str(e))

    def remove_label(self):
        if self.selected_label_index != -1:
            self.labels.pop(self.selected_label_index)
            self.update_listbox()
            self.selected_label_index = -1
    
    def clear_labels(self):
        self.labels.clear()
        self.update_listbox()
        self.selected_label_index = -1

    def on_label_select(self, event):
        selection = self.listbox_labels.curselection()
        if selection: self.selected_label_index = selection[0]
        else: self.selected_label_index = -1

    def update_listbox(self):
        self.listbox_labels.delete(0, tk.END)
        for i, label_data in enumerate(self.labels):
            self.listbox_labels.insert(tk.END, f"{i+1}. {label_data.filename} (К-ть: {label_data.count}, W: {round(label_data.width_mm)}мм, H: {round(label_data.height_mm)}мм)")

    def configure_label(self, event=None):
        if self.selected_label_index == -1:
            messagebox.showwarning("Вибір етикетки", "Будь ласка, виберіть етикетку зі списку для налаштування.")
            return
        label_data = self.labels[self.selected_label_index]
        config_window = tk.Toplevel(self.root)
        config_window.title(f"Налаштування: {label_data.filename}")
        config_window.transient(self.root)
        config_window.grab_set()
        config_window.update_idletasks()
        root_x, root_y = self.root.winfo_x(), self.root.winfo_y()
        root_w, root_h = self.root.winfo_width(), self.root.winfo_height()
        dialog_w, dialog_h = config_window.winfo_width(), config_window.winfo_height()
        pos_x = root_x + (root_w // 2) - (dialog_w // 2)
        pos_y = root_y + (root_h // 2) - (dialog_h // 2)
        config_window.geometry(f"+{pos_x}+{pos_y}")
        width_var = tk.DoubleVar(value=label_data.width_mm)
        height_var = tk.DoubleVar(value=label_data.height_mm)
        count_var = tk.IntVar(value=label_data.count)
        preset_var = tk.StringVar(
            value=find_matching_preset(label_data.width_mm, label_data.height_mm)
        )
        dimensions_are_updating = False

        def sync_from_width(*args):
            nonlocal dimensions_are_updating
            if dimensions_are_updating:
                return
            try:
                if width_var.get() > 0 and label_data.original_ratio > 0:
                    dimensions_are_updating = True
                    height_var.set(round(width_var.get() / label_data.original_ratio))
                    preset_var.set(CUSTOM_PRESET)
            except (tk.TclError, ValueError):
                pass
            finally:
                dimensions_are_updating = False

        def sync_from_height(*args):
            nonlocal dimensions_are_updating
            if dimensions_are_updating:
                return
            try:
                if height_var.get() > 0:
                    dimensions_are_updating = True
                    width_var.set(round(height_var.get() * label_data.original_ratio))
                    preset_var.set(CUSTOM_PRESET)
            except (tk.TclError, ValueError):
                pass
            finally:
                dimensions_are_updating = False

        def apply_preset(event=None):
            nonlocal dimensions_are_updating
            dimensions = LABEL_SIZE_PRESETS.get(preset_var.get())
            if dimensions is None:
                return
            dimensions_are_updating = True
            width_var.set(dimensions[0])
            height_var.set(dimensions[1])
            dimensions_are_updating = False

        ttk.Label(config_window, text="Пресет розміру:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        preset_combobox = ttk.Combobox(
            config_window,
            textvariable=preset_var,
            values=[CUSTOM_PRESET, *LABEL_SIZE_PRESETS],
            state="readonly",
        )
        preset_combobox.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        preset_combobox.bind("<<ComboboxSelected>>", apply_preset)

        entry_width = ttk.Entry(config_window, textvariable=width_var)
        entry_height = ttk.Entry(config_window, textvariable=height_var)
        width_var.trace_add("write", lambda n, i, m, e=entry_height: self.root.focus_get() != e and sync_from_width())
        height_var.trace_add("write", lambda n, i, m, e=entry_width: self.root.focus_get() != e and sync_from_height())

        ttk.Label(config_window, text="Ширина (мм):").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        entry_width.grid(row=1, column=1, sticky="ew", padx=5, pady=5)
        ttk.Label(config_window, text="Висота (мм):").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        entry_height.grid(row=2, column=1, sticky="ew", padx=5, pady=5)
        ttk.Label(config_window, text="Кількість для друку:").grid(row=3, column=0, sticky="w", padx=5, pady=5)
        ttk.Entry(config_window, textvariable=count_var).grid(row=3, column=1, sticky="ew", padx=5, pady=5)

        def save_config():
            try:
                label_data.width_mm, label_data.height_mm, label_data.count = float(width_var.get()), float(height_var.get()), int(count_var.get())
                self.update_listbox()
                config_window.destroy()
            except ValueError: messagebox.showerror("Помилка вводу", "Введіть дійсні числа.")
        ttk.Button(config_window, text="Зберегти", command=save_config).grid(row=4, column=0, columnspan=2, pady=10)

    def generate_pdf(self):
        if not self.labels:
            messagebox.showwarning("Немає етикеток", "Додайте хоча б одну етикетку для друку.")
            return
        try:
            gap = int(self.entry_gap.get())
            if gap < 0: raise ValueError("Проміжок не може бути від'ємним.")
            output_filename = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF Documents", "*.pdf")], initialfile="druk.pdf", title="Зберегти PDF як...")
            if output_filename:
                make_labels(self.labels, output_filename, gap)
                messagebox.showinfo("Готово", f"Файл {output_filename} успішно створено!")
        except ValueError as e: messagebox.showerror("Помилка вводу", f"Некоректні дані: {e}")
        except Exception as e: messagebox.showerror("Помилка генерації PDF", str(e))

if __name__ == "__main__":
    root = dnd.Tk()
    app = LabelApp(root)
    root.mainloop()
