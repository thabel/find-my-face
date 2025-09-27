import face_recognition
import os
import numpy as np
import faiss

# Dossier des images
image_folder = "data/img_voyages"
target_image_path = "target.jpg"

# 1️⃣ Préparer la base : calculer et stocker tous les embeddings
embeddings = []
image_paths = []

for filename in os.listdir(image_folder):
    if not filename.lower().endswith(('.png', '.jpg', '.jpeg')):
        continue
    path = os.path.join(image_folder, filename)
    image = face_recognition.load_image_file(path)
    face_encs = face_recognition.face_encodings(image)
    for enc in face_encs:
        embeddings.append(enc)
        image_paths.append(path)

embeddings = np.array(embeddings).astype('float32')
print(f"Nombre de visages indexés : {len(embeddings)}")

# 2️⃣ Créer l'index FAISS
d = embeddings.shape[1]  # dimension des embeddings (128)
index = faiss.IndexFlatL2(d)
index.add(embeddings)
print("Index FAISS créé avec succès.")

# 3️⃣ Encoder le visage cible
target_image = face_recognition.load_image_file(target_image_path)
target_encs = face_recognition.face_encodings(target_image)

if len(target_encs) == 0:
    raise Exception("Aucun visage détecté dans l'image cible")
target_enc = np.array([target_encs[0]]).astype('float32')

# 4️⃣ Rechercher les visages similaires
k = 5  # nombre de résultats à retourner
distances, indices = index.search(target_enc, k)

print("\nImages similaires :")
for i, idx in enumerate(indices[0]):
    print(f"{i+1}. {image_paths[idx]} (distance={distances[0][i]:.4f})")
