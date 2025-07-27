# 🎨 Dot Image Converter (DotIC) ✦

Un générateur d'art pointillé (halftone) qui transforme vos images en œuvres d'art constituées de points de taille variable basés sur la luminance. L'effet obtenu ressemble aux techniques d'impression traditionnelles ou aux tatouages pointillés modernes.

![Image tattoo](assets\image0.jpg)

## ✨ Fonctionnalités

- 🖼️ **Conversion d'images** : Transforme n'importe quelle image en art pointillé
- 🎛️ **Paramètres personnalisables** : Contrôle total sur la grille et la taille des points
- 🎨 **Modes de couleur multiples** : Niveaux de gris, couleurs originales, sépia
- 🖥️ **Interface graphique intuitive** : GUI complète avec aperçu en temps réel
- 📏 **Résolutions flexibles** : De 400px à 1200px ou plus
- 💾 **Export multiple** : PNG, JPEG et autres formats
- ⚡ **Traitement en arrière-plan** : Interface réactive avec barre de progression

## 🚀 Installation

### Prérequis

- Python 3.7 ou plus récent
- pip (gestionnaire de paquets Python)

### Installation des dépendances

```bash
pip install opencv-python pillow matplotlib numpy tkinter
```

## 📖 Utilisation

### Interface Graphique (Recommandé)

1. **Lancer l'application** :

```bash
python dot_art_gui.py
```

2. **Workflow simple** :
   - Cliquez sur "Parcourir" pour sélectionner votre image
   - Ajustez les paramètres selon vos préférences
   - Cliquez sur "Aperçu" pour un test rapide
   - Cliquez sur "Générer" pour la version finale
   - Utilisez "Sauvegarder" pour exporter le résultat

### Utilisation en ligne de commande

```python
from dot_art_generator import DotArtGenerator

# Créer le générateur
generator = DotArtGenerator(
    grid_cols=60,      # Nombre de colonnes
    grid_rows=60,      # Nombre de lignes
    max_dot_size=10,   # Taille max des points
    min_dot_size=1     # Taille min des points
)

# Traiter une image
result = generator.process_image("mon_image.jpg", output_size=(800, 800))
result.save("art_pointille.png")
```

## 🎛️ Paramètres

### Grille

- **Colonnes/Lignes** : 10-150 (défaut: 50)
  - Plus élevé = plus de détails, plus de points
  - Plus bas = effet plus artistique, moins de détails

### Taille des points

- **Taille maximale** : 2-20px (défaut: 8)
  - Taille des points dans les zones sombres
- **Taille minimale** : 0-5px (défaut: 1)
  - Taille des points dans les zones claires

### Modes de couleur

- **Niveaux de gris** : Effet classique en noir et blanc
- **Couleurs originales** : Conserve les couleurs de l'image source
- **Sépia** : Effet vintage avec teintes chaudes

### Résolution de sortie

- **400x400px** : Aperçu rapide
- **600x600px** : Qualité standard
- **800x800px** : Haute qualité (défaut)
- **1000x1000px** : Très haute qualité
- **1200x1200px** : Qualité maximale

## 📁 Structure du projet

```
dot-art-generator/
├── dot_art_generator.py    # Classe principale du générateur
├── dot_art_gui.py         # Interface graphique
├── requirements.txt       # Dépendances Python
├── README.md             # Ce fichier
├── examples/             # Images d'exemple
│   ├── input/           # Images sources
│   └── output/          # Résultats générés
└── screenshots/         # Captures d'écran de l'interface
```

## 🖼️ Exemples

### Portraits

Idéal pour créer des portraits artistiques avec un effet tatouage pointillé moderne.

### Paysages

Transforme les paysages en œuvres d'art avec des détails subtils dans les zones de lumière.

### Logos et graphiques

Parfait pour donner un aspect vintage ou artistique aux logos et éléments graphiques.

## 🛠️ Fonctionnalités avancées

### Traitement par lots

```python
import os
from dot_art_generator import DotArtGenerator

generator = DotArtGenerator(grid_cols=80, grid_rows=80)

# Traiter toutes les images d'un dossier
input_folder = "images_source/"
output_folder = "images_pointillees/"

for filename in os.listdir(input_folder):
    if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
        input_path = os.path.join(input_folder, filename)
        output_path = os.path.join(output_folder, f"pointille_{filename}")

        result = generator.process_image(input_path)
        result.save(output_path)
```

### Personnalisation avancée

```python
# Créer des effets personnalisés
generator = DotArtGenerator(
    grid_cols=120,        # Grille très fine
    grid_rows=120,
    max_dot_size=6,       # Points plus petits
    min_dot_size=0        # Zones blanches sans points
)

# Traitement avec callback de progression
def ma_progression(pourcentage):
    print(f"Progression: {pourcentage:.1f}%")

result = generator.process_image(
    "mon_image.jpg",
    output_size=(1500, 1500),  # Très haute résolution
    color_mode='original',
    progress_callback=ma_progression
)
```

## 🎯 Conseils d'utilisation

### Pour les meilleurs résultats :

- **Images haute résolution** : Utilisez des images d'au moins 800x800px
- **Bon contraste** : Les images avec des zones claires et sombres bien définies donnent de meilleurs résultats
- **Sujets simples** : Les portraits et objets simples fonctionnent mieux que les scènes complexes

### Paramètres recommandés :

- **Portraits** : 60-80 colonnes/lignes, taille max 8-12
- **Paysages** : 40-60 colonnes/lignes, taille max 6-10
- **Logos** : 30-50 colonnes/lignes, taille max 10-15

## 🐛 Résolution des problèmes

### Erreurs communes

**"Impossible de charger l'image"**

- Vérifiez que le chemin du fichier est correct
- Formats supportés : JPG, PNG, BMP, TIFF

**"Interface qui se bloque"**

- Le traitement se fait en arrière-plan, patientez
- Pour de très hautes résolutions, le traitement peut prendre plusieurs minutes

**"Points trop petits/grands"**

- Ajustez les paramètres de taille min/max
- Modifiez la résolution de la grille

### Performance

- Pour des aperçus rapides, utilisez une grille de 30x30
- Pour la qualité finale, montez jusqu'à 100x100 ou plus
- Les résolutions supérieures à 1200px peuvent être lentes

## 🤝 Contribution

Les contributions sont les bienvenues ! N'hésitez pas à :

- Signaler des bugs
- Proposer de nouvelles fonctionnalités
- Améliorer la documentation
- Partager vos créations

### Pour contribuer :

1. Fork le projet
2. Créez une branche pour votre fonctionnalité
3. Commitez vos changements
4. Poussez vers la branche
5. Ouvrez une Pull Request

## 📜 Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

## 🙏 Remerciements

- Inspiré par les techniques d'impression traditionnelles en demi-teintes
- Utilise les bibliothèques OpenCV, PIL et tkinter

## 📞 Support

Si vous rencontrez des problèmes ou avez des questions :

- Ouvrez une issue sur GitHub
- Consultez la section [Résolution des problèmes](#-résolution-des-problèmes)
- Partagez vos créations avec la communauté !

---

_Transformez vos photos en œuvres d'art pointillé en quelques clics !_ ✨
