from embeddings import get_face_embeddings, embeddings_array, image_paths, num_faces_per_image,output_folder

import faiss
import shutil  # Importer shutil pour copier les fichiers
import time
import numpy as np


target_image_path = "brenda.jpg"
# start time
start_time = time.time()

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
k = 10
distances, indices = index.search(target_emb, k)

print("\nImages similaires :")
for i, idx in enumerate(indices[0]):
    similar_image_path = image_paths[idx]
    print(f"{i+1}. {similar_image_path} (distance={distances[0][i]:.4f})({num_faces_per_image[similar_image_path]})")

    # Copier l'image similaire dans le dossier de sortie
    shutil.copy(similar_image_path, output_folder)

print(f"\nLes images similaires ont été copiées dans le dossier : {output_folder}")
# end time
end_time = time.time()
print(f"\nTemps d'exécution : {end_time - start_time:.2f} secondes")