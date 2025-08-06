import cv2
import os
import tkinter as tk
from tkinter import filedialog, messagebox

def is_blurry(image_path, threshold=100):
    image = cv2.imread(image_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    lap_var = cv2.Laplacian(gray, cv2.CV_64F).var()
    return lap_var < threshold

def select_folder():
    folder = filedialog.askdirectory()
    if folder:
        input_entry.delete(0, tk.END)
        input_entry.insert(0, folder)

def run_detection():
    input_folder = input_entry.get()
    output_folder = os.path.join(input_folder, "blurry_images")
    os.makedirs(output_folder, exist_ok=True)

    blurry_count = 0
    for filename in sorted(os.listdir(input_folder)):
        if filename.lower().endswith('.jpg'):
            full_path = os.path.join(input_folder, filename)
            if is_blurry(full_path, threshold=threshold_var.get()):
                cv2.imwrite(os.path.join(output_folder, filename), cv2.imread(full_path))
                blurry_count += 1

    messagebox.showinfo("完了", f"{blurry_count} 枚のぼけ画像を抽出しました。\n保存先: {output_folder}")

# GUI構築
root = tk.Tk()
root.title("ぼけ画像抽出ツール")

tk.Label(root, text="画像フォルダ:").grid(row=0, column=0, sticky="e")
input_entry = tk.Entry(root, width=40)
input_entry.grid(row=0, column=1)
tk.Button(root, text="参照", command=select_folder).grid(row=0, column=2)

tk.Label(root, text="判定しきい値:").grid(row=1, column=0, sticky="e")
threshold_var = tk.IntVar(value=100)
tk.Entry(root, textvariable=threshold_var).grid(row=1, column=1)

tk.Button(root, text="抽出開始", command=run_detection).grid(row=2, column=1, pady=10)

root.mainloop()