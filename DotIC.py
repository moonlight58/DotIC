import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from tkinter import Frame, Label, Button, Entry, Scale, StringVar, IntVar
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageTk
import threading
import os

class DotArtGenerator:
    def __init__(self, grid_cols=50, grid_rows=50, max_dot_size=8, min_dot_size=1):
        self.grid_cols = grid_cols
        self.grid_rows = grid_rows
        self.max_dot_size = max_dot_size
        self.min_dot_size = min_dot_size
    
    def calculate_luminance(self, rgb):
        if len(rgb.shape) == 3:
            return 0.299 * rgb[:,:,0] + 0.587 * rgb[:,:,1] + 0.114 * rgb[:,:,2]
        return rgb
    
    def process_image(self, image_path, output_size=(800, 800), color_mode='grayscale', progress_callback=None):
        # Charger l'image
        img = cv2.imread(image_path)
        if img is None:
            raise ValueError(f"Impossible de charger l'image: {image_path}")
        
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img_resized = cv2.resize(img_rgb, (self.grid_cols, self.grid_rows))
        
        # Calculer la luminance
        luminance = self.calculate_luminance(img_resized.astype(float))
        luminance_normalized = luminance / 255.0
        
        # Créer l'image de sortie
        output_img = Image.new('RGB', output_size, 'white')
        draw = ImageDraw.Draw(output_img)
        
        cell_width = output_size[0] / self.grid_cols
        cell_height = output_size[1] / self.grid_rows
        
        total_cells = self.grid_rows * self.grid_cols
        processed_cells = 0
        
        for row in range(self.grid_rows):
            for col in range(self.grid_cols):
                center_x = (col + 0.5) * cell_width
                center_y = (row + 0.5) * cell_height
                
                lum = 1.0 - luminance_normalized[row, col]
                dot_size = self.min_dot_size + (self.max_dot_size - self.min_dot_size) * lum
                
                # Choisir la couleur selon le mode
                if color_mode == 'original':
                    orig_color = img_resized[row, col]
                    color = tuple(orig_color)
                elif color_mode == 'sepia':
                    intensity = int(255 * (1 - lum * 0.6))
                    color = (intensity, int(intensity * 0.8), int(intensity * 0.6))
                else:  # grayscale
                    color_intensity = int(255 * (1 - lum * 0.8))
                    color = (color_intensity, color_intensity, color_intensity)
                
                if dot_size > 0.5:
                    bbox = [
                        center_x - dot_size/2,
                        center_y - dot_size/2,
                        center_x + dot_size/2,
                        center_y + dot_size/2
                    ]
                    draw.ellipse(bbox, fill=color)
                
                # Callback pour la barre de progression
                processed_cells += 1
                if progress_callback and processed_cells % 100 == 0:
                    progress = (processed_cells / total_cells) * 100
                    progress_callback(progress)
        
        if progress_callback:
            progress_callback(100)
        
        return output_img

class DotArtGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Générateur d'Art Pointillé")
        self.root.geometry("1000x700")
        self.root.configure(bg='#f0f0f0')
        
        # Variables
        self.image_path = StringVar()
        self.grid_cols = IntVar(value=50)
        self.grid_rows = IntVar(value=50)
        self.max_dot_size = IntVar(value=8)
        self.min_dot_size = IntVar(value=1)
        self.color_mode = StringVar(value='grayscale')
        self.output_size = IntVar(value=800)
        
        self.generator = DotArtGenerator()
        self.original_image = None
        self.result_image = None
        self.processing = False
        
        self.setup_ui()
    
    def setup_ui(self):
        # Style
        style = ttk.Style()
        style.theme_use('clam')
        
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configuration de la grille
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # === PANNEAU DE CONTROLE ===
        control_frame = ttk.LabelFrame(main_frame, text="Paramètres", padding="10")
        control_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N), padx=(0, 10))
        
        # Sélection d'image
        ttk.Label(control_frame, text="Image:").grid(row=0, column=0, sticky=tk.W, pady=2)
        image_frame = ttk.Frame(control_frame)
        image_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        image_frame.columnconfigure(0, weight=1)
        
        self.image_entry = ttk.Entry(image_frame, textvariable=self.image_path, state='readonly')
        self.image_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        
        ttk.Button(image_frame, text="Parcourir", command=self.select_image).grid(row=0, column=1)
        
        # Paramètres de grille
        ttk.Label(control_frame, text="Grille - Colonnes:").grid(row=2, column=0, sticky=tk.W, pady=(10, 2))
        self.cols_scale = Scale(control_frame, from_=10, to=150, orient=tk.HORIZONTAL, 
                               variable=self.grid_cols, command=self.update_preview)
        self.cols_scale.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=2)
        
        ttk.Label(control_frame, text="Grille - Lignes:").grid(row=4, column=0, sticky=tk.W, pady=2)
        self.rows_scale = Scale(control_frame, from_=10, to=150, orient=tk.HORIZONTAL, 
                               variable=self.grid_rows, command=self.update_preview)
        self.rows_scale.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=2)
        
        # Taille des points
        ttk.Label(control_frame, text="Taille max des points:").grid(row=6, column=0, sticky=tk.W, pady=(10, 2))
        self.max_dot_scale = Scale(control_frame, from_=2, to=20, orient=tk.HORIZONTAL, 
                                  variable=self.max_dot_size, command=self.update_preview)
        self.max_dot_scale.grid(row=7, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=2)
        
        ttk.Label(control_frame, text="Taille min des points:").grid(row=8, column=0, sticky=tk.W, pady=2)
        self.min_dot_scale = Scale(control_frame, from_=0, to=5, orient=tk.HORIZONTAL, 
                                  variable=self.min_dot_size, command=self.update_preview)
        self.min_dot_scale.grid(row=9, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=2)
        
        # Mode de couleur
        ttk.Label(control_frame, text="Mode de couleur:").grid(row=10, column=0, sticky=tk.W, pady=(10, 2))
        color_frame = ttk.Frame(control_frame)
        color_frame.grid(row=11, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=2)
        
        ttk.Radiobutton(color_frame, text="Niveaux de gris", variable=self.color_mode, 
                       value='grayscale', command=self.update_preview).pack(anchor=tk.W)
        ttk.Radiobutton(color_frame, text="Couleurs originales", variable=self.color_mode, 
                       value='original', command=self.update_preview).pack(anchor=tk.W)
        ttk.Radiobutton(color_frame, text="Sépia", variable=self.color_mode, 
                       value='sepia', command=self.update_preview).pack(anchor=tk.W)
        
        # Taille de sortie
        ttk.Label(control_frame, text="Taille de sortie (px):").grid(row=12, column=0, sticky=tk.W, pady=(10, 2))
        size_frame = ttk.Frame(control_frame)
        size_frame.grid(row=13, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=2)
        
        for size in [400, 600, 800, 1000, 1200]:
            ttk.Radiobutton(size_frame, text=f"{size}x{size}", variable=self.output_size, 
                           value=size).pack(side=tk.LEFT, padx=2)
        
        # Boutons
        button_frame = ttk.Frame(control_frame)
        button_frame.grid(row=14, column=0, columnspan=2, pady=(20, 0))
        
        self.preview_btn = ttk.Button(button_frame, text="Aperçu", command=self.generate_preview)
        self.preview_btn.pack(side=tk.LEFT, padx=2)
        
        self.generate_btn = ttk.Button(button_frame, text="Générer", command=self.generate_full)
        self.generate_btn.pack(side=tk.LEFT, padx=2)
        
        self.save_btn = ttk.Button(button_frame, text="Sauvegarder", command=self.save_image, state='disabled')
        self.save_btn.pack(side=tk.LEFT, padx=2)
        
        # Barre de progression
        self.progress = ttk.Progressbar(control_frame, mode='determinate')
        self.progress.grid(row=15, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        
        # === ZONE D'AFFICHAGE ===
        display_frame = ttk.LabelFrame(main_frame, text="Aperçu", padding="10")
        display_frame.grid(row=0, column=1, rowspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        display_frame.columnconfigure(0, weight=1)
        display_frame.rowconfigure(0, weight=1)
        
        # Canvas avec scrollbars
        canvas_frame = ttk.Frame(display_frame)
        canvas_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        canvas_frame.columnconfigure(0, weight=1)
        canvas_frame.rowconfigure(0, weight=1)
        
        self.canvas = tk.Canvas(canvas_frame, bg='white')
        self.canvas.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(canvas_frame, orient=tk.VERTICAL, command=self.canvas.yview)
        v_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.canvas.configure(yscrollcommand=v_scrollbar.set)
        
        h_scrollbar = ttk.Scrollbar(canvas_frame, orient=tk.HORIZONTAL, command=self.canvas.xview)
        h_scrollbar.grid(row=1, column=0, sticky=(tk.W, tk.E))
        self.canvas.configure(xscrollcommand=h_scrollbar.set)
        
        # === STATUS BAR ===
        self.status_var = StringVar(value="Prêt - Sélectionnez une image pour commencer")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
    
    def select_image(self):
        filename = filedialog.askopenfilename(
            title="Sélectionner une image",
            filetypes=[
                ("Images", "*.jpg *.jpeg *.png *.bmp *.tiff"),
                ("JPEG", "*.jpg *.jpeg"),
                ("PNG", "*.png"),
                ("Tous les fichiers", "*.*")
            ]
        )
        if filename:
            self.image_path.set(filename)
            self.load_original_image()
            self.status_var.set(f"Image chargée: {os.path.basename(filename)}")
    
    def load_original_image(self):
        try:
            # Charger et afficher l'image originale
            self.original_image = Image.open(self.image_path.get())
            self.display_image(self.original_image, "Image originale")
            
            # Activer les boutons
            self.preview_btn.config(state='normal')
            self.generate_btn.config(state='normal')
            
        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible de charger l'image:\n{str(e)}")
    
    def display_image(self, image, title=""):
        # Redimensionner pour l'affichage si nécessaire
        display_size = (600, 600)
        img_copy = image.copy()
        img_copy.thumbnail(display_size, Image.Resampling.LANCZOS)
        
        # Convertir pour tkinter
        self.photo = ImageTk.PhotoImage(img_copy)
        
        # Afficher sur le canvas
        self.canvas.delete("all")
        self.canvas.create_image(10, 10, anchor=tk.NW, image=self.photo)
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        
        if title:
            self.canvas.create_text(10, img_copy.height + 20, anchor=tk.NW, text=title, 
                                   font=("Arial", 12, "bold"))
    
    def update_preview(self, *args):
        # Mise à jour automatique de l'aperçu (optionnel)
        pass
    
    def update_progress(self, value):
        self.progress['value'] = value
        self.root.update_idletasks()
    
    def generate_preview(self):
        if not self.image_path.get():
            messagebox.showwarning("Attention", "Veuillez sélectionner une image d'abord")
            return
        
        self.generate_image(preview=True)
    
    def generate_full(self):
        if not self.image_path.get():
            messagebox.showwarning("Attention", "Veuillez sélectionner une image d'abord")
            return
        
        self.generate_image(preview=False)
    
    def generate_image(self, preview=True):
        if self.processing:
            return
        
        self.processing = True
        self.progress['value'] = 0
        
        # Paramètres
        size = 400 if preview else self.output_size.get()
        
        # Thread pour éviter de bloquer l'interface
        def process():
            try:
                self.status_var.set("Génération en cours...")
                
                # Mettre à jour le générateur
                self.generator.grid_cols = self.grid_cols.get()
                self.generator.grid_rows = self.grid_rows.get()
                self.generator.max_dot_size = self.max_dot_size.get()
                self.generator.min_dot_size = self.min_dot_size.get()
                
                # Générer l'image
                result = self.generator.process_image(
                    self.image_path.get(),
                    output_size=(size, size),
                    color_mode=self.color_mode.get(),
                    progress_callback=self.update_progress
                )
                
                # Afficher le résultat
                self.result_image = result
                self.root.after(0, lambda: self.display_image(result, "Art pointillé"))
                self.root.after(0, lambda: self.save_btn.config(state='normal'))
                self.root.after(0, lambda: self.status_var.set("Génération terminée"))
                
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Erreur", f"Erreur lors de la génération:\n{str(e)}"))
                self.root.after(0, lambda: self.status_var.set("Erreur lors de la génération"))
            
            finally:
                self.processing = False
                self.root.after(0, lambda: self.progress.configure(value=0))
        
        thread = threading.Thread(target=process)
        thread.daemon = True
        thread.start()
    
    def save_image(self):
        if not self.result_image:
            messagebox.showwarning("Attention", "Aucune image à sauvegarder")
            return
        
        filename = filedialog.asksaveasfilename(
            title="Sauvegarder l'art pointillé",
            defaultextension=".png",
            filetypes=[
                ("PNG", "*.png"),
                ("JPEG", "*.jpg"),
                ("Tous les fichiers", "*.*")
            ]
        )
        
        if filename:
            try:
                self.result_image.save(filename)
                self.status_var.set(f"Image sauvegardée: {os.path.basename(filename)}")
                messagebox.showinfo("Succès", f"Image sauvegardée avec succès:\n{filename}")
            except Exception as e:
                messagebox.showerror("Erreur", f"Impossible de sauvegarder l'image:\n{str(e)}")

def main():
    root = tk.Tk()
    app = DotArtGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()