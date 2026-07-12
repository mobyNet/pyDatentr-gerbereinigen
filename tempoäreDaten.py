import ctypes
import shutil
import getpass
import os
import sys
import tempfile


# -------------------------------
#  MENÜ
# -------------------------------

def main_menu():
    print("\nWas möchtest du ausführen?")
    print("1) 🧹 Temp + Windows-Temp löschen (Papierkorb wird auch geleert)")
    print("2) 🔒 Papierkorb leeren + Secure-Wipe")
    print("3) 📦 Update-Cache anzeigen und optional löschen")
    print("4) 🌐 Browser-Cache löschen")
    print("5) ❌ Beenden")

    choice = input("Auswahl: ")
    return choice


# -------------------------------
#  TEMP CLEANER
# -------------------------------

def delete_temp_files():
    temp_dirs = [
        tempfile.gettempdir(),
        os.path.join(os.environ.get("SystemRoot", "C:\\Windows"), "Temp")
    ]

    deleted_files = 0
    deleted_dirs = 0
    skipped_files = 0

    print("\n📂 Scanne Temp-Ordner...")

    for temp_dir in temp_dirs:
        print(f"\n📁 Ordner: {temp_dir}")

        if not os.path.exists(temp_dir):
            print("   ❌ Ordner existiert nicht.")
            continue

        for root, dirs, files in os.walk(temp_dir, topdown=False):

            # Dateien prüfen
            for file in files:
                file_path = os.path.join(root, file)

                # Prüfen, ob Datei gesperrt ist
                try:
                    with open(file_path, "rb"):
                        pass
                except Exception:
                    skipped_files += 1
                    continue

                # Datei ist NICHT gesperrt → löschen
                try:
                    os.remove(file_path)
                    deleted_files += 1
                except Exception:
                    skipped_files += 1

            # Ordner löschen
            for dir_name in dirs:
                dir_path = os.path.join(root, dir_name)
                try:
                    shutil.rmtree(dir_path, ignore_errors=False)
                    deleted_dirs += 1
                except Exception:
                    skipped_files += 1

    print("\n✅ Temp-Ordner fertig!")
    print(f"   🗑️ Dateien gelöscht: {deleted_files}")
    print(f"   📂 Ordner gelöscht: {deleted_dirs}")
    print(f"   🚫 Nicht löschbar (in Benutzung): {skipped_files}")


# -------------------------------
#  PAPIERKORB LEEREN
# -------------------------------

def empty_recycle_bin():
    SHERB_NOCONFIRMATION = 0x00000001
    SHERB_NOPROGRESSUI = 0x00000002
    SHERB_NOSOUND = 0x00000004

    try:
        ctypes.windll.shell32.SHEmptyRecycleBinW(
            None, None,
            SHERB_NOCONFIRMATION | SHERB_NOPROGRESSUI | SHERB_NOSOUND
        )
        print("🗑️ Papierkorb geleert.")
    except Exception as e:
        print(f"⚠️ Fehler beim Leeren des Papierkorbs: {e}")


# -------------------------------
#  SECURE WIPE
# -------------------------------

def wipe_free_space(drive="C:\\", chunk_size=1024 * 1024 * 400):
    print(f"\n🔒 Starte Secure Wipe für freien Speicher auf {drive}")

    free_bytes = shutil.disk_usage(drive).free
    print(f"   📊 Freier Speicher: {free_bytes / (1024**3):.2f} GB")

    wipe_file = os.path.join(tempfile.gettempdir(), "wipe_temp_file.bin")
    print(f"   📁 Erstelle Wipe-Datei: {wipe_file}")

    total_to_write = free_bytes - (chunk_size * 2)
    written = 0

    try:
        with open(wipe_file, "wb") as f:
            while written < total_to_write:
                f.write(os.urandom(chunk_size))
                written += chunk_size

                progress = written / total_to_write
                bar_length = 40
                filled = int(progress * bar_length)
                bar = "█" * filled + "-" * (bar_length - filled)

                sys.stdout.write(
                    f"\r   ➕ Fortschritt: [{bar}] {progress*100:.1f}%"
                )
                sys.stdout.flush()

        print("\n   ✔️ Wipe-Datei vollständig geschrieben.")

    except KeyboardInterrupt:
        print("\n   ❌ Wipe abgebrochen!")
    except Exception as e:
        print(f"\n   ⚠️ Fehler beim Schreiben der Wipe-Datei: {e}")

    finally:
        if os.path.exists(wipe_file):
            os.remove(wipe_file)
            print(f"   🗑️ Wipe-Datei gelöscht: {wipe_file}")

    print("🔐 Secure Wipe abgeschlossen.")


# -------------------------------
#  UPDATE CACHE
# -------------------------------

def get_update_cache_size():
    folder = r"C:\Windows\SoftwareDistribution\Download"
    total_size = 0

    for root, dirs, files in os.walk(folder):
        for f in files:
            fp = os.path.join(root, f)
            try:
                total_size += os.path.getsize(fp)
            except:
                pass

    return total_size


def delete_update_cache():
    folder = r"C:\Windows\SoftwareDistribution\Download"

    print("\n📦 Lösche Update-Cache...")

    try:
        shutil.rmtree(folder)
        os.makedirs(folder)
        print("✔️ Update-Cache gelöscht.")
    except Exception as e:
        print(f"⚠️ Fehler beim Löschen des Update-Caches: {e}")


# -------------------------------
#  BROWSER CACHE
# -------------------------------

def get_folder_size(path):
    total = 0
    for root, dirs, files in os.walk(path):
        for f in files:
            try:
                total += os.path.getsize(os.path.join(root, f))
            except:
                pass
    return total


def delete_browser_cache():
    chrome_cache = os.path.expandvars(
        r"%LOCALAPPDATA%\Google\Chrome\User Data\Default\Cache")
    edge_cache = os.path.expandvars(
        r"%LOCALAPPDATA%\Microsoft\Edge\User Data\Default\Cache")

    print("\n🌐 Browser-Cache Analyse...")

    total_size = 0
    cache_paths = [chrome_cache, edge_cache]

    # Größe berechnen
    for cache in cache_paths:
        if os.path.exists(cache):
            size = get_folder_size(cache)
            total_size += size
            print(f"   📦 {cache} → {size / (1024**2):.2f} MB")

    print(f"\n📊 Gesamtgröße Browser-Cache: {total_size / (1024**2):.2f} MB")

    print("\n🌐 Lösche Browser-Cache...")

    deleted_files = 0
    deleted_dirs = 0
    skipped = 0

    for cache in cache_paths:
        if os.path.exists(cache):
            for root, dirs, files in os.walk(cache, topdown=False):

                # Dateien löschen
                for f in files:
                    fp = os.path.join(root, f)
                    try:
                        os.remove(fp)
                        deleted_files += 1
                    except:
                        skipped += 1

                # Ordner löschen
                for d in dirs:
                    dp = os.path.join(root, d)
                    try:
                        shutil.rmtree(dp)
                        deleted_dirs += 1
                    except:
                        skipped += 1

    print("\n🌐 Browser-Cache fertig!")
    print(f"   🗑️ Dateien gelöscht: {deleted_files}")
    print(f"   📂 Ordner gelöscht: {deleted_dirs}")
    print(f"   🚫 Nicht löschbar (in Benutzung): {skipped}")


# -------------------------------
#  HAUPTTEIL
# -------------------------------
if __name__ == "__main__":
    print(f"🚀 Starte Cleaner als Benutzer: {getpass.getuser()}")

    while True:
        choice = main_menu()

        if choice == "1":
            delete_temp_files()
            empty_recycle_bin()
            print("✔️ Fertig ohne Secure-Wipe.")

        elif choice == "2":
            delete_temp_files()
            empty_recycle_bin()
            wipe_free_space("C:\\")

        elif choice == "3":
            size = get_update_cache_size()
            print(f"\n📦 Update-Cache Größe: {size / (1024**2):.2f} MB")

            ask = input("Möchtest du löschen? (j/n): ").lower()
            if ask == "j":
                delete_update_cache()
            else:
                print("❌ Update-Cache nicht gelöscht.")

        elif choice == "4":
            delete_browser_cache()

        elif choice == "5":
            print("👋 Cleaner beendet.")
            break

        else:
            print("❌ Ungültige Eingabe.")
