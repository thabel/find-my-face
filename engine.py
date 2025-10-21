import time
import insightface
import numpy as np
import cv2
import os
import faiss
import shutil
import argparse
import pickle

# Globals
MODEL = None

def load_model(ctx_id=-1):
    """Charger le modèle ArcFace (singleton)."""
    global MODEL
    if MODEL is None:
        MODEL = insightface.app.FaceAnalysis()
        MODEL.prepare(ctx_id=ctx_id)
    return MODEL


def get_face_embeddings(img_path, ctx_id=-1):
    """Retourne la liste des embeddings (numpy arrays) pour toutes les faces trouvées dans l'image.

    Args:
        img_path (str): chemin vers l'image.
        ctx_id (int): contexte pour insightface (-1 CPU, 0 GPU).
    Returns:
        list[numpy.array]
    """
    model = load_model(ctx_id=ctx_id)
    img = cv2.imread(img_path)
    if img is None:
        return []
    faces = model.get(img)
    embeddings = [f.embedding for f in faces]
    return embeddings


def build_embeddings(image_folder, output_folder='data/similar_images', ctx_id=-1):
    """Parcourt le dossier d'images et construit les tableaux d'embeddings et métadata.

    Sauvegarde les résultats dans `data/embeddings.npz` et `data/meta.pkl`.
    Retourne (embeddings_array, image_paths, num_faces_per_image, output_folder)
    """
    os.makedirs(output_folder, exist_ok=True)
    embeddings_list = []
    image_paths = []
    num_faces_per_image = {}

    for filename in os.listdir(image_folder):
        if not filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            continue
        path = os.path.join(image_folder, filename)
        embeddings = get_face_embeddings(path, ctx_id=ctx_id)
        num_faces_per_image[path] = len(embeddings)
        for emb in embeddings:
            embeddings_list.append(emb)
            image_paths.append(path)

    if len(embeddings_list) == 0:
        embeddings_array = np.empty((0, 512), dtype='float32')
    else:
        embeddings_array = np.array(embeddings_list).astype('float32')

    # Save to disk for re-use
    os.makedirs('data', exist_ok=True)
    np.savez_compressed('data/embeddings.npz', embeddings=embeddings_array)
    with open('data/meta.pkl', 'wb') as f:
        pickle.dump({'image_paths': image_paths, 'num_faces_per_image': num_faces_per_image, 'output_folder': output_folder}, f)

    print(f"Nombre de visages indexés : {len(embeddings_array)}")
    return embeddings_array, image_paths, num_faces_per_image, output_folder


def load_embeddings():
    """Charge embeddings et métadata depuis le disque. Retourne la même structure que build_embeddings()"""
    if not os.path.exists('data/embeddings.npz') or not os.path.exists('data/meta.pkl'):
        raise FileNotFoundError("Les fichiers d'embeddings n'existent pas. Exécutez d'abord `build`.")
    data = np.load('data/embeddings.npz')
    embeddings_array = data['embeddings']
    with open('data/meta.pkl', 'rb') as f:
        meta = pickle.load(f)
    return embeddings_array, meta['image_paths'], meta['num_faces_per_image'], meta.get('output_folder', 'data/similar_images')


def build_faiss_index(embeddings_array):
    if embeddings_array.size == 0:
        raise ValueError('Pas d\'embeddings pour construire l\'index')
    d = embeddings_array.shape[1]
    index = faiss.IndexFlatL2(d)
    index.add(embeddings_array)
    return index


def search_image(target_image_path, k=5, ctx_id=-1, copy_results=True):
    """Charge les embeddings, encode l'image cible, et recherche les k plus proches.

    Copie les images similaires dans le dossier `output_folder` si copy_results=True.
    Retourne une liste de tuples (similar_image_path, distance)
    """
    embeddings_array, image_paths, num_faces_per_image, output_folder = load_embeddings()
    if embeddings_array.size == 0:
        raise ValueError('Les embeddings sont vides. Exécutez build avant search.')

    index = build_faiss_index(embeddings_array)

    target_embs = get_face_embeddings(target_image_path, ctx_id=ctx_id)
    if len(target_embs) == 0:
        raise Exception("Aucun visage détecté dans l'image cible")
    target_emb = np.array([target_embs[0]]).astype('float32')

    distances, indices = index.search(target_emb, k)

    results = []
    for i, idx in enumerate(indices[0]):
        similar_image_path = image_paths[idx]
        dist = float(distances[0][i])
        results.append((similar_image_path, dist))
        if copy_results:
            os.makedirs(output_folder, exist_ok=True)
            try:
                shutil.copy(similar_image_path, output_folder)
            except Exception:
                pass

    return results


def main():
    parser = argparse.ArgumentParser(description='Engine pour embeddings + recherche par visage')
    sub = parser.add_subparsers(dest='cmd')

    p_build = sub.add_parser('build', help='Construire et sauvegarder les embeddings à partir d\'un dossier d\'images')
    p_build.add_argument('--images', '-i', required=True, help='Dossier contenant les images à indexer')
    p_build.add_argument('--out', '-o', default='data/similar_images', help='Dossier de sortie pour les images similaires')
    p_build.add_argument('--ctx', type=int, default=-1, help='ctx_id pour insightface (-1 CPU, 0 GPU)')

    p_search = sub.add_parser('search', help='Rechercher les visages similaires pour une image cible (utilise les embeddings sauvegardés)')
    p_search.add_argument('--target', '-t', required=True, help='Chemin vers l\'image cible')
    p_search.add_argument('--k', '-k', type=int, default=5, help='Nombre de résultats à retourner')
    p_search.add_argument('--ctx', type=int, default=-1, help='ctx_id pour insightface (-1 CPU, 0 GPU)')
    p_search.add_argument('--no-copy', action='store_true', help="Ne pas copier les images similaires dans le dossier d\'output")

    args = parser.parse_args()
    if args.cmd == 'build':
        build_embeddings(args.images, output_folder=args.out, ctx_id=args.ctx)
    elif args.cmd == 'search':
        results = search_image(args.target, k=args.k, ctx_id=args.ctx, copy_results=not args.no_copy)
        print('\nImages similaires :')
        for i, (path, dist) in enumerate(results, start=1):
            print(f"{i}. {path} (distance={dist:.4f})")
        print(f"\nLes images similaires ont été copiées dans le dossier : {load_embeddings()[3]}")
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
