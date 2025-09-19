# 📱 kadb – Déboguer Flutter/Android en Wi-Fi sans câble

**kadb** est un petit outil en Python qui permet de se connecter à un appareil Android pour le déboguer via Wi-Fi (sans câble USB) en utilisant `adb`.

---

## 🚀 Installation

### 1. Prérequis
- Python 3.7 ou supérieur
- `adb` (Android Debug Bridge) installé et accessible depuis le terminal (`adb version`)
- Un téléphone Android avec **Options développeur** activées
- **Débogage USB activé** sur le téléphone

👉 Première connexion : **branche ton téléphone en USB** et active le débogage USB.

### 2. Installation de kadb

Installe la librairie via pip :

```bash
pip install kadb
