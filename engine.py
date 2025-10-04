import time
import insightface
import numpy as np
import cv2
import os
import faiss
import shutil  # Importer shutil pour copier les fichiers

# start time
start_time = time.time()
# 1️⃣ Charger le modèle ArcFace
model = insightface.app.FaceAnalysis()
model.prepare(ctx_id=-1)  # -1 = CPU, ctx_id=0 pour GPU

# Dossier des images
image_folder = "data/img_voyages"
target_image_path = "target.png"
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
embeddings_list = []
image_paths = []

for filename in os.listdir(image_folder):
    if not filename.lower().endswith(('.png', '.jpg', '.jpeg')):
        continue
    path = os.path.join(image_folder, filename)
    embeddings = get_face_embeddings(path)
    for emb in embeddings:
        embeddings_list.append(emb)
        image_paths.append(path)

embeddings_array = np.array(embeddings_list).astype('float32')
print(f"Nombre de visages indexés : {len(embeddings_array)}")

# 4️⃣ Créer l'index FAISS
d = embeddings_array.shape[1]  # dimension des embeddings (512 pour ArcFace)
index = faiss.IndexFlatL2(d)
index.add(embeddings_array)

# 5️⃣ Encoder le visage cible
target_emb = get_face_embeddings(target_image_path)
if len(target_emb) == 0:
    raise Exception("Aucun visage détecté dans l'image cible")
target_emb = np.array([target_emb[0]]).astype('float32')

# 6️⃣ Rechercher les visages similaires
k = 5
distances, indices = index.search(target_emb, k)

print("\nImages similaires :")
for i, idx in enumerate(indices[0]):
    similar_image_path = image_paths[idx]
    print(f"{i+1}. {similar_image_path} (distance={distances[0][i]:.4f})")
    
    # Copier l'image similaire dans le dossier de sortie
    shutil.copy(similar_image_path, output_folder)

print(f"\nLes images similaires ont été copiées dans le dossier : {output_folder}")
# end time
end_time = time.time()
print(f"\nTemps d'exécution : {end_time - start_time:.2f} secondes")
