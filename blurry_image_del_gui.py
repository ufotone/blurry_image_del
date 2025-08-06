import cv2
import os
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import Spinbox

def is_blurry(image_path, threshold=100):
    image = cv2.imread(image_path)
    if image is None:
        return False
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    lap_var = cv2.Laplacian(gray, cv2.CV_64F).var()
    return lap_var < threshold

def suggest_threshold(folder):
    variances = []
    for filename in sorted(os.listdir(folder)):
        if filename.lower().endswith('.jpg'):
            path = os.path.join(folder, filename)
            image = cv2.imread(path)
            if image is not None:
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                lap_var = cv2.Laplacian(gray, cv2.CV_64F).var()
                variances.append(lap_var)
    if not variances:
        return 100
    avg = sum(variances) / len(variances)
    return int(avg * 0.7)

def select_folder():
    folder = filedialog.askdirectory()
    if folder:
        input_entry.delete(0, tk.END)
        input_entry.insert(0, folder)

def set_suggested_threshold():
    folder = input_entry.get()
    if not os.path.isdir(folder):
        messagebox.showerror("Error", "有効なフォルダを選択してください")
        return
    suggested = suggest_threshold(folder)
    threshold_entry.delete(0, tk.END)
    threshold_entry.insert(0, str(suggested))
    messagebox.showinfo("おすすめしきい値", f"画像群から推定: {suggested}")

def preview_images():
    input_folder = input_entry.get()
    try:
        threshold = int(threshold_entry.get())
    except ValueError:
        messagebox.showerror("Error", "しきい値には整数を入力してください")
        return

    for filename in sorted(os.listdir(input_folder)):
        if filename.lower().endswith('.jpg'):
            path = os.path.join(input_folder, filename)
            image = cv2.imread(path)
            if image is None:
                continue
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            lap_var = cv2.Laplacian(gray, cv2.CV_64F).var()
            status = "BLURRY" if lap_var < threshold else "SHARP"
            preview = image.copy()
            text = f"{filename} - {status} (Var: {lap_var:.2f})"
            cv2.putText(preview, text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1,
                        (0, 0, 255) if status == "BLURRY" else (0, 255, 0), 2)
            cv2.imshow("Preview", preview)
            if cv2.waitKey(100) == 27:  # ESCで終了
                break
    cv2.destroyAllWindows()

def run_detection():
    input_folder = input_entry.get()
    try:
        threshold = int(threshold_entry.get())
    except ValueError:
        messagebox.showerror("Error", "しきい値には整数を入力してください")
        return

    output_folder = os.path.join(input_folder, "blurry_images")
    os.makedirs(output_folder, exist_ok=True)

    blurry_count = 0
    for filename in sorted(os.listdir(input_folder)):
        if filename.lower().endswith('.jpg'):
            path = os.path.join(input_folder, filename)
            if is_blurry(path, threshold):
                cv2.imwrite(os.path.join(output_folder, filename), cv2.imread(path))
                blurry_count += 1

    messagebox.showinfo("Finished", f"{blurry_count} 枚のぼけ画像を抽出しました。\n保存先: {output_folder}")

# GUI 構築
root = tk.Tk()
root.title("ぼけ画像抽出ツール")

tk.Label(root, text="画像フォルダ:").grid(row=0, column=0, sticky="e")
input_entry = tk.Entry(root, width=40)
input_entry.grid(row=0, column=1)
tk.Button(root, text="参照", command=select_folder).grid(row=0, column=2)

tk.Label(root, text="しきい値:").grid(row=1, column=0, sticky="e")
threshold_entry = Spinbox(root, from_=10, to=1000)
threshold_entry.delete(0, tk.END)
threshold_entry.insert(0, "100")
threshold_entry.grid(row=1, column=1)
tk.Button(root, text="おすすめ設定", command=set_suggested_threshold).grid(row=1, column=2)

tk.Button(root, text="プレビュー", command=preview_images).grid(row=2, column=0, pady=10)
tk.Button(root, text="抽出開始", command=run_detection).grid(row=2, column=1, pady=10)

root.mainloop()