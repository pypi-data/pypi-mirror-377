import subprocess
import re
import sys


def run_cmd(cmd):
    try:
        result = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT, text=True)
        return result.strip()
    except subprocess.CalledProcessError as e:
        print(f"[ERREUR] Commande échouée: {cmd}\n{e.output}")
        sys.exit(1)


def choisir_device(devices):
    print("\n=== Appareils détectés ===")
    for i, d in enumerate(devices):
        print(f"{i + 1}. {d}")
    choix = input("👉 Choisis l’appareil à utiliser (1, 2, ...): ")
    try:
        index = int(choix) - 1
        return devices[index]
    except (ValueError, IndexError):
        print("[ERREUR] Choix invalide.")
        sys.exit(1)


def main():
    print("=== Débogage Flutter/Android en Wi-Fi ===")

    # Vérifier adb
    adb_version = run_cmd("adb version")
    print(f"[OK] {adb_version}")

    # Récupérer la liste des devices
    devices_output = run_cmd("adb devices").splitlines()
    devices = [line.split()[0] for line in devices_output if "device" in line and not line.startswith("List")]

    if not devices:
        print("[ERREUR] Aucun appareil détecté. Branche ton téléphone en USB avec débogage activé.")
        sys.exit(1)

    # Si plusieurs devices, demander à l'utilisateur de choisir
    if len(devices) > 1:
        device = choisir_device(devices)
    else:
        device = devices[0]
        print(f"[OK] Téléphone détecté: {device}")

    # Récupérer l’adresse IP du téléphone choisi
    ip_info = run_cmd(f"adb -s {device} shell ip addr show wlan0")
    match = re.search(r"inet (\d+\.\d+\.\d+\.\d+)", ip_info)
    if not match:
        print("[ERREUR] Impossible de récupérer l'IP du téléphone. Vérifie qu'il est connecté au Wi-Fi.")
        sys.exit(1)
    phone_ip = match.group(1)
    print(f"[OK] IP du téléphone: {phone_ip}")

    # Activer adb TCP/IP
    run_cmd(f"adb -s {device} tcpip 5555")
    print("[OK] adb écoute maintenant sur le port 5555.")

    # Connecter via Wi-Fi
    run_cmd(f"adb connect {phone_ip}:5555")
    print(f"[OK] Connecté au téléphone via Wi-Fi ({phone_ip})")

    # Vérifier connexion
    devices_after = run_cmd("adb devices")
    if phone_ip in devices_after:
        print(f"[SUCCÈS] Débogage sans câble activé ✅ ({phone_ip})")
    else:
        print("[ERREUR] Le téléphone ne s'est pas connecté en Wi-Fi.")


if __name__ == "__main__":
    main()