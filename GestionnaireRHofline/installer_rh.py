"""
GestionnaireRH Guinée — Installateur Windows
=============================================
Auteur  : ICG Guinea
Version : 1.0.0

Installe GestionnaireRH dans C:\GestionnaireRH\,
crée un raccourci Bureau et un raccourci Menu Démarrer.
Supporte le mode Mise à jour : préserve les données existantes.
"""
import os
import sys
import shutil
import threading
import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path

# ─── Configuration ─────────────────────────────────────────────────────────────
APP_NAME      = "GestionnaireRH"
APP_VERSION   = "1.0"
APP_PUBLISHER = "ICG Guinea"
INSTALL_DIR   = Path(r"C:\GestionnaireRH")
EXE_NAME      = "GestionnaireRH.exe"

# Couleurs
BG      = '#ecf0f1'
HDR_BG  = '#1a5276'
HDR_FG  = 'white'
ACCENT  = '#27ae60'
GREY    = '#7f8c8d'

# Répertoire source = dossier de l'exe (quand frozen) ou dossier du script
if getattr(sys, 'frozen', False):
    SRC_DIR = Path(sys.executable).parent
else:
    SRC_DIR = Path(__file__).parent

# ─── Détection mode mise à jour ───────────────────────────────────────────────
IS_UPDATE = (INSTALL_DIR / EXE_NAME).exists()

# Fichiers/dossiers à NE PAS écraser lors d'une mise à jour (données utilisateur)
UPDATE_PRESERVE_FILES = {'db.sqlite3', 'license.dat', '.trial_start',
                          '.secret_key', '.env'}
UPDATE_PRESERVE_DIRS  = {'media'}


# ─── Utilitaires ──────────────────────────────────────────────────────────────
def create_shortcut(target: Path, shortcut_path: Path, icon: Path = None):
    """Crée un raccourci Windows (.lnk) via PowerShell."""
    icon_str = str(icon) if icon and icon.exists() else str(target)
    ps_script = (
        f'$ws = New-Object -ComObject WScript.Shell; '
        f'$s = $ws.CreateShortcut("{shortcut_path}"); '
        f'$s.TargetPath = "{target}"; '
        f'$s.WorkingDirectory = "{target.parent}"; '
        f'$s.IconLocation = "{icon_str}"; '
        f'$s.Save()'
    )
    import subprocess
    try:
        subprocess.run(
            ['powershell', '-NoProfile', '-ExecutionPolicy', 'Bypass',
             '-Command', ps_script],
            capture_output=True, timeout=15
        )
    except Exception:
        pass


def register_uninstall():
    """Enregistre l'application dans Ajout/Suppression de programmes."""
    try:
        import winreg
        key_path = (
            r'SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\GestionnaireRH'
        )
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, key_path) as key:
            winreg.SetValueEx(key, 'DisplayName',      0, winreg.REG_SZ, APP_NAME)
            winreg.SetValueEx(key, 'DisplayVersion',   0, winreg.REG_SZ, APP_VERSION)
            winreg.SetValueEx(key, 'Publisher',        0, winreg.REG_SZ, APP_PUBLISHER)
            winreg.SetValueEx(key, 'InstallLocation',  0, winreg.REG_SZ, str(INSTALL_DIR))
            winreg.SetValueEx(key, 'UninstallString',  0, winreg.REG_SZ,
                              str(INSTALL_DIR / 'desinstaller.bat'))
            winreg.SetValueEx(key, 'NoModify',         0, winreg.REG_DWORD, 1)
            winreg.SetValueEx(key, 'NoRepair',         0, winreg.REG_DWORD, 1)
    except Exception:
        pass


def do_install(log):
    """Effectue l'installation complète ou la mise à jour."""
    try:
        if IS_UPDATE:
            # ── MODE MISE À JOUR ──────────────────────────────────────────────
            log("=== Mode Mise à jour détecté ===")
            log(f"Installation existante : {INSTALL_DIR}")
            log("")

            # Arrêter l'application si elle est en cours d'exécution
            log("Arrêt de l'application en cours (si active)...")
            import subprocess, time
            try:
                subprocess.run(
                    ['taskkill', '/F', '/IM', EXE_NAME, '/T'],
                    capture_output=True, timeout=10
                )
                time.sleep(1)
                log("OK Application arrêtée.")
            except Exception:
                pass

            # Copier les nouveaux fichiers en préservant les données utilisateur
            log("Mise à jour des fichiers de l'application...")
            total = 0
            preserved = 0
            for item in SRC_DIR.rglob('*'):
                if not item.is_file():
                    continue
                rel = item.relative_to(SRC_DIR)
                parts = rel.parts

                # Ignorer l'installateur lui-même
                if parts[0] in {EXE_NAME, 'installer_rh.py',
                                 'Installer_GestionnaireRH.exe',
                                 'Installateur_GestionnaireRH.exe'}:
                    continue

                # Préserver les données utilisateur
                if parts[0] in UPDATE_PRESERVE_FILES:
                    log(f"  [PRESERVE] {rel}")
                    preserved += 1
                    continue
                if parts[0] in UPDATE_PRESERVE_DIRS:
                    log(f"  [PRESERVE] {rel}")
                    preserved += 1
                    continue

                dst = INSTALL_DIR / rel
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(item, dst)
                total += 1
                if total % 50 == 0:
                    log(f"  {total} fichiers mis à jour...")

            log(f"OK {total} fichiers mis à jour ({preserved} fichiers préservés)")
            log("")
            log("=" * 48)
            log(f"  Mise à jour terminée dans {INSTALL_DIR}")
            log("  Vos données ont été préservées.")
            log("=" * 48)
            return True

        else:
            # ── MODE INSTALLATION FRAÎCHE ─────────────────────────────────────
            # 1. Créer le répertoire d'installation
            log("Création du répertoire d'installation...")
            INSTALL_DIR.mkdir(parents=True, exist_ok=True)

            # 2. Copier tous les fichiers
            # Fichiers exclus : l'essai et la licence doivent être vierges chez le client
            SKIP_FILES = {'.trial_start', 'license.dat', '.secret_key'}

            log("Copie des fichiers (cela peut prendre quelques instants)...")
            total = 0
            for item in SRC_DIR.rglob('*'):
                if item.is_file() and item.name not in SKIP_FILES:
                    rel = item.relative_to(SRC_DIR)
                    dst = INSTALL_DIR / rel
                    dst.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(item, dst)
                    total += 1
                    if total % 50 == 0:
                        log(f"  {total} fichiers copiés...")
            log(f"OK {total} fichiers copiés vers {INSTALL_DIR}")

            # 3. Créer les fichiers BAT
            bat_start = INSTALL_DIR / 'Demarrer_GestionnaireRH.bat'
            bat_stop  = INSTALL_DIR / 'Arreter_GestionnaireRH.bat'
            bat_unins = INSTALL_DIR / 'desinstaller.bat'

            bat_start.write_text(
                f'@echo off\ncd /d "{INSTALL_DIR}"\n'
                f'title {APP_NAME}\necho Demarrage...\n'
                f'start "" "{INSTALL_DIR / EXE_NAME}"\n',
                encoding='cp1252')
            bat_stop.write_text(
                f'@echo off\ntaskkill /F /IM {EXE_NAME} /T 2>nul\n'
                f'echo {APP_NAME} arrete.\npause\n',
                encoding='cp1252')
            bat_unins.write_text(
                f'@echo off\necho Desinstallation de {APP_NAME}...\n'
                f'taskkill /F /IM {EXE_NAME} /T 2>nul\n'
                f'rd /s /q "{INSTALL_DIR}" 2>nul\n'
                f'echo Desinstallation terminee.\npause\n',
                encoding='cp1252')
            log("OK Fichiers de démarrage créés")

            # 4. Raccourci Bureau
            desktop = Path(os.path.expanduser('~')) / 'Desktop'
            icon = INSTALL_DIR / 'static' / 'img' / 'logo.ico'
            if not icon.exists():
                icon = INSTALL_DIR / 'logo.ico'
            shortcut_desktop = desktop / f"{APP_NAME}.lnk"
            create_shortcut(INSTALL_DIR / EXE_NAME, shortcut_desktop, icon)
            log(f"OK Raccourci Bureau : {shortcut_desktop}")

            # 5. Raccourci Menu Démarrer
            try:
                start_menu = Path(os.environ.get('APPDATA', '')) / \
                    'Microsoft' / 'Windows' / 'Start Menu' / 'Programs'
                start_menu.mkdir(parents=True, exist_ok=True)
                shortcut_start = start_menu / f"{APP_NAME}.lnk"
                create_shortcut(INSTALL_DIR / EXE_NAME, shortcut_start, icon)
                log("OK Raccourci Menu Démarrer créé")
            except Exception:
                pass

            # 6. Registre Windows
            register_uninstall()
            log("OK Enregistrement dans Windows (Ajout/Suppression de programmes)")

            log("")
            log("=" * 48)
            log(f"  Installation terminée dans {INSTALL_DIR}")
            log("=" * 48)
            return True

    except Exception as exc:
        log(f"ERREUR : {exc}")
        import traceback
        log(traceback.format_exc())
        return False


# ─── Interface graphique ───────────────────────────────────────────────────────
class InstallerApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        if IS_UPDATE:
            root.title(f"Mise à jour — {APP_NAME}")
        else:
            root.title(f"Installation — {APP_NAME}")
        root.resizable(False, False)
        root.configure(bg=BG)

        W, H = 540, 520
        root.geometry(f"{W}x{H}")
        root.update_idletasks()
        sw, sh = root.winfo_screenwidth(), root.winfo_screenheight()
        root.geometry(f"{W}x{H}+{(sw - W) // 2}+{(sh - H) // 2}")

        self.done = False
        self._build_ui()

    def _build_ui(self):
        # En-tête
        hdr = tk.Frame(self.root, bg=HDR_BG, height=72)
        hdr.pack(fill='x')
        hdr.pack_propagate(False)

        if IS_UPDATE:
            hdr_title = f"Mise à jour de {APP_NAME}"
        else:
            hdr_title = f"Installation de {APP_NAME}"

        tk.Label(hdr, text=hdr_title,
                 font=('Arial', 18, 'bold'), bg=HDR_BG, fg=HDR_FG).place(
            relx=0.5, rely=0.38, anchor='center')
        tk.Label(hdr, text=f"{APP_PUBLISHER} — Version {APP_VERSION}",
                 font=('Arial', 8), bg=HDR_BG, fg='#aed6f1').place(
            relx=0.5, rely=0.76, anchor='center')

        # Corps
        body = tk.Frame(self.root, bg=BG, padx=24, pady=18)
        body.pack(fill='both', expand=True)

        if IS_UPDATE:
            info_text = (
                f"Une mise à jour sera installée dans :\n{INSTALL_DIR}\n\n"
                "Vos données (base de données, licence, médias)\n"
                "seront préservées automatiquement."
            )
        else:
            info_text = f"L'application sera installée dans :\n{INSTALL_DIR}"

        tk.Label(body,
                 text=info_text,
                 font=('Arial', 10), bg=BG, fg='#2c3e50',
                 justify='left').pack(anchor='w', pady=(0, 16))

        # Barre de progression
        tk.Label(body, text="Progression :", font=('Arial', 9, 'bold'),
                 bg=BG, fg='#2c3e50').pack(anchor='w')
        self.progress = ttk.Progressbar(body, mode='indeterminate', length=460)
        self.progress.pack(fill='x', pady=(4, 12))

        # Journal
        tk.Label(body, text="Journal :", font=('Arial', 9, 'bold'),
                 bg=BG, fg='#2c3e50').pack(anchor='w')
        log_frame = tk.Frame(body, bg=BG)
        log_frame.pack(fill='both', expand=True)
        self.log_text = tk.Text(log_frame, font=('Courier', 8),
                                height=12, state='disabled',
                                bg='#f8f9fa', relief='flat', bd=1)
        scrollbar = ttk.Scrollbar(log_frame, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)
        self.log_text.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

        # ── Barre de boutons fixe en bas (hors zone scrollable) ──────────────
        # Séparateur
        tk.Frame(self.root, bg='#b2bec3', height=2).pack(fill='x')

        btn_bar = tk.Frame(self.root, bg='#dfe6e9', pady=12, padx=20)
        btn_bar.pack(fill='x', side='bottom')

        if IS_UPDATE:
            btn_text = f"  Mettre à jour  "
        else:
            btn_text = f"  Installer  "

        self.close_btn = tk.Button(
            btn_bar,
            text="  Fermer  ",
            command=self._on_close,
            font=('Segoe UI', 10, 'bold'),
            bg='#e74c3c', fg='white',
            activebackground='#c0392b', activeforeground='white',
            relief='flat', padx=18, pady=10, cursor='hand2', bd=0)
        self.close_btn.pack(side='right', padx=(6, 0))

        self.install_btn = tk.Button(
            btn_bar,
            text=btn_text,
            command=self._start_install,
            font=('Segoe UI', 11, 'bold'),
            bg='#27ae60', fg='white',
            activebackground='#1e8449', activeforeground='white',
            relief='flat', padx=22, pady=10, cursor='hand2', bd=0)
        self.install_btn.pack(side='right', padx=(6, 0))

        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

    def _log(self, msg: str):
        self.log_text.config(state='normal')
        self.log_text.insert('end', msg + '\n')
        self.log_text.see('end')
        self.log_text.config(state='disabled')
        self.root.update_idletasks()

    def _start_install(self):
        self.install_btn.config(state='disabled')
        self.progress.start(12)

        def run():
            success = do_install(self._log)
            self.progress.stop()
            if success:
                self.done = True
                self.root.after(0, self._on_success)
            else:
                self.root.after(0, lambda: messagebox.showerror(
                    "Erreur",
                    "L'opération a échoué.\nConsultez le journal ci-dessus."))
                self.install_btn.config(state='normal')

        threading.Thread(target=run, daemon=True).start()

    def _on_success(self):
        if IS_UPDATE:
            title = "Mise à jour réussie"
            msg = (
                f"{APP_NAME} a été mis à jour avec succès !\n\n"
                f"Répertoire : {INSTALL_DIR}\n"
                "Vos données ont été préservées.\n\n"
                "Voulez-vous lancer l'application maintenant ?"
            )
        else:
            title = "Installation réussie"
            msg = (
                f"{APP_NAME} a été installé avec succès !\n\n"
                f"Répertoire : {INSTALL_DIR}\n"
                "Raccourci Bureau créé.\n\n"
                "Voulez-vous lancer l'application maintenant ?"
            )
        if messagebox.askyesno(title, msg):
            import subprocess
            subprocess.Popen([str(INSTALL_DIR / EXE_NAME)],
                             cwd=str(INSTALL_DIR))
        self.root.destroy()

    def _on_close(self):
        if not self.done:
            label = "la mise à jour" if IS_UPDATE else "l'installation"
            if messagebox.askyesno("Quitter", f"Annuler {label} ?"):
                self.root.destroy()
        else:
            self.root.destroy()


def main():
    root = tk.Tk()
    InstallerApp(root)
    root.mainloop()


if __name__ == '__main__':
    main()
