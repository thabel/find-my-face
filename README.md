# Find My Face

**Find My Face** est une solution innovante de livraison de photos à la minute pendant et après un événement couvert par un photographe, en utilisant la reconnaissance faciale pour retrouver facilement les images des participants.

---

## 🎯 Objectif

Permettre aux participants d’un événement de retrouver et télécharger rapidement toutes les photos où ils apparaissent, sans chercher manuellement parmi des centaines d’images.  

**Processus :**  
1. Le photographe sélectionne les photos réussies et les upload sur l’interface Admin.  
2. Les participants scannent un QR code affiché sur le lieu de l’événement.  
3. Ils accèdent à une interface web et prennent un selfie.  
4. Le système recherche toutes les images contenant leur visage parmi celles uploadées.  
5. Les participants peuvent ensuite télécharger leurs photos directement sur leur téléphone.  

> L’expérience utilisateur est fluide et rapide, inspirée du fonctionnement de Google Photos.

---

## 🧑‍💻 Fonctionnalités principales

- Upload sécurisé de photos par les photographes.  
- Reconnaissance faciale pour retrouver les participants dans les photos.  
- Interface web intuitive pour les participants.  
- Téléchargement direct des images.  
- Support possible pour étendre à la vidéo et à des applications mobiles.  

---

## 🔍 Exploration et idées futures

- **API Google Photos :** L’API est partiellement fermée, mais certaines fonctionnalités peuvent être utilisées selon les conditions d’usage.  
- **Extension aux vidéos :** La reconnaissance faciale peut être appliquée à chaque frame ou segment clé pour retrouver des personnes dans les vidéos.  
- **Application mobile :** Une version mobile améliorerait l’expérience, mais nécessiterait un moteur de recherche efficace et optimisé pour le mobile.  
- **Travaux similaires :** Des solutions comme Google Photos, Amazon Rekognition ou Microsoft Azure Face API permettent des recherches similaires, mais Find My Face se concentre sur l’usage événementiel et la livraison instantanée.

---

## 🛠️ Technologies possibles

- **Backend :** Python (Flask/Django), Node.js  
- **Reconnaissance faciale :** OpenCV, `face_recognition`, DeepFace, ou API cloud (AWS, Azure, Google)  
- **Frontend :** React / Vue / Angular  
- **Base de données :** PostgreSQL / MongoDB  
- **Mobile (optionnel) :** Flutter ou React Native  

---

## 🚀 Prochaines étapes

1. Implémenter le moteur de recherche de visages avec un petit dataset de test.  
2. Ajouter le téléchargement sécurisé des images.  
3. Explorer l’extension aux vidéos.  
4. Concevoir une application mobile pour l’accès utilisateur.  
5. Optimiser le moteur de recherche pour de grandes quantités d’images.  
