import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
from PIL import Image, ImageTk
import numpy as np
import tensorflow as tf

class ImageClassifierApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Görüntü Sınıflandırma Uygulaması")
        
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.load_button = ttk.Button(self.main_frame, text="Görüntü Yükle", command=self.load_image)
        self.load_button.grid(row=0, column=0, pady=10)
        
        self.classify_button = ttk.Button(self.main_frame, text="Sınıflandır", command=self.classify_image, state='disabled')
        self.classify_button.grid(row=0, column=1, pady=10)
        
        self.save_button = ttk.Button(self.main_frame, text="Sonucu Kaydet", command=self.save_result, state='disabled')
        self.save_button.grid(row=0, column=2, pady=10)
        
        self.history_button = ttk.Button(self.main_frame, text="Geçmişi Görüntüle", command=self.show_history)
        self.history_button.grid(row=0, column=3, pady=10)
        
        self.model_selection = ttk.Combobox(self.main_frame, values=["MobileNetV2", "ResNet50"])
        self.model_selection.current(0)
        self.model_selection.grid(row=0, column=4, pady=10)
        
        self.image_label = ttk.Label(self.main_frame)
        self.image_label.grid(row=1, column=0, columnspan=5, pady=20)
        
        self.result_label = ttk.Label(self.main_frame, text="Sonuç: -")
        self.result_label.grid(row=2, column=0, columnspan=5, pady=10)
        
        self.model = self.load_model("MobileNetV2")
        self.image = None
        self.history = []
    
    def load_model(self, model_name):
        if model_name == "MobileNetV2":
            model = tf.keras.applications.MobileNetV2(weights='imagenet')
        elif model_name == "ResNet50":
            model = tf.keras.applications.ResNet50(weights='imagenet')
        return model
    
    def load_image(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            image = Image.open(file_path)
            image = image.resize((224, 224))
            self.image = image
            photo = ImageTk.PhotoImage(image)
            self.image_label.config(image=photo)
            self.image_label.image = photo
            self.classify_button.config(state='normal')
    
    def classify_image(self):
        if self.image:
            image_array = np.array(self.image)
            image_array = np.expand_dims(image_array, axis=0)
            image_array = tf.keras.applications.mobilenet_v2.preprocess_input(image_array)
            predictions = self.model.predict(image_array)
            decoded_predictions = tf.keras.applications.mobilenet_v2.decode_predictions(predictions, top=1)
            class_name = decoded_predictions[0][0][1]
            self.result_label.config(text=f"Sonuç: {class_name}")
            self.save_button.config(state='normal')
            self.history.append((self.image, class_name))
    
    def save_result(self):
        if self.history:
            last_result = self.history[-1]
            image, result = last_result
            file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")])
            if file_path:
                with open(file_path, 'w') as file:
                    file.write(f"Sonuç: {result}\n")
                messagebox.showinfo("Başarılı", "Sonuç başarıyla kaydedildi.")
    
    def show_history(self):
        history_window = tk.Toplevel(self.root)
        history_window.title("Sınıflandırma Geçmişi")
        history_frame = ttk.Frame(history_window, padding="10")
        history_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        history_listbox = tk.Listbox(history_frame, height=10)
        history_listbox.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        for i, (image, result) in enumerate(self.history):
            history_listbox.insert(tk.END, f"{i+1}. Sonuç: {result}")

if __name__ == "__main__":
    root = tk.Tk()
    app = ImageClassifierApp(root)
    root.mainloop()