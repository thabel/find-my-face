# Commentaire
# Partie 1 : Embedding des images de la banque d'images de l'évènement

import time
import insightface
import numpy as np
import cv2
import os


# start time
start_time = time.time()
# 1️⃣ Charger le modèle ArcFace
model = insightface.app.FaceAnalysis()
model.prepare(ctx_id=0)  # -1 = CPU, ctx_id=0 pour GPU

# Dossier des images
image_folder = "data/img_GBU"
target_image_path = "brenda.jpg"
output_folder = "data/similar_images"  # Dossier pour les images similaires

# Créer le dossier de sortie s'il n'existe pas
os.makedirs(output_folder, exist_ok=True)

# 2️⃣ Fonction pour extraire embeddings d'une image
def get_face_embeddings(img_path):
    img = cv2.imread(img_path)
    faces = model.get(img)
    embeddings = [f.embedding for f in faces]
    return embeddings

# 3️⃣ Préparer la base
num_faces_per_image = dict()
embeddings_list = []
image_paths = []

for filename in os.listdir(image_folder):
    if not filename.lower().endswith(('.png', '.jpg', '.jpeg')):
        continue
    path = os.path.join(image_folder, filename)
    embeddings = get_face_embeddings(path)
    num_faces_per_image[path] = len(embeddings)
    for emb in embeddings:
        embeddings_list.append(emb)
        image_paths.append(path)

embeddings_array = np.array(embeddings_list).astype('float32')
print(f"Nombre de visages indexés : {len(embeddings_array)}")

end_time = time.time()
print(f"\nTemps d'exécution partie embedding : {end_time - start_time:.2f} secondes")
