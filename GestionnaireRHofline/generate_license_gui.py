#!/usr/bin/env python
"""
GestionnaireRH Guinée — Générateur de Licences (Outil Distributeur)
=====================================================================
Auteur  : ICG Guinea
Version : 1.0.0

Outil réservé au distributeur pour générer des fichiers de licence
(.lic) à envoyer aux clients après paiement.
"""
import os
import sys
import json

BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE)

import tkinter as tk
from tkinter import ttk, filedialog, messagebox

# ─── Protection anti-vol : vérification machine propriétaire ─────────────────
try:
    from project_guardian import guard_license_generation, is_owner_machine
    guard_license_generation()
except PermissionError as _pe:
    try:
        messagebox.showerror(
            "ACCÈS REFUSÉ",
            "Cette machine n'est PAS autorisée à générer des licences.\n\n"
            "Seule la machine propriétaire de ICG Guinea peut utiliser cet outil.\n\n"
            "Toute tentative de contournement est journalisée et signalée."
        )
    except Exception:
        print(str(_pe))
    sys.exit(1)
except ImportError:
    try:
        messagebox.showerror(
            "ERREUR DE SÉCURITÉ",
            "Module de protection introuvable (project_guardian.py).\n"
            "Le générateur de licences ne peut pas s'exécuter sans ce module."
        )
    except Exception:
        pass
    sys.exit(1)
# ─── Fin protection anti-vol ──────────────────────────────────────────────────

try:
    from license_manager import (
        generate_activation_file,
        get_machine_id,
        get_machine_id_short,
    )
except ImportError:
    messagebox.showerror(
        "Erreur",
        "license_manager.py est introuvable.\n"
        "Placez generate_license_gui.py dans le même dossier que license_manager.py."
    )
    sys.exit(1)

# ─── Couleurs ─────────────────────────────────────────────────────────────────
BG      = '#ecf0f1'
HDR_BG  = '#1a5276'
HDR_FG  = 'white'
ACCENT  = '#27ae60'
BLUE    = '#2980b9'
GREY    = '#7f8c8d'
RED     = '#c0392b'
LABEL_FG = '#2c3e50'
ENTRY_BG = '#ffffff'


class LicenseGeneratorApp:
    """Fenêtre principale du générateur de licences GestionnaireRH."""

    def __init__(self, root: tk.Tk):
        self.root = root
        root.title("GestionnaireRH — Générateur de Licences")
        root.resizable(False, False)
        root.configure(bg=BG)

        W, H = 580, 630
        root.geometry(f"{W}x{H}")
        root.update_idletasks()
        sw, sh = root.winfo_screenwidth(), root.winfo_screenheight()
        root.geometry(f"{W}x{H}+{(sw - W) // 2}+{(sh - H) // 2}")

        self._build_ui()

    def _build_ui(self):
        self._build_header()
        self._build_body()
        self._build_footer()

    def _build_header(self):
        hdr = tk.Frame(self.root, bg=HDR_BG, height=80)
        hdr.pack(fill='x')
        hdr.pack_propagate(False)
        tk.Label(hdr, text="GestionnaireRH — Générateur de Licences",
                 font=('Arial', 17, 'bold'), bg=HDR_BG, fg=HDR_FG).place(
            relx=0.5, rely=0.35, anchor='center')
        tk.Label(hdr, text="Réservé à ICG Guinea — Distributeur",
                 font=('Arial', 9, 'italic'), bg=HDR_BG, fg='#aed6f1').place(
            relx=0.5, rely=0.73, anchor='center')

    def _build_body(self):
        body = tk.Frame(self.root, bg=BG, padx=26, pady=20)
        body.pack(fill='both', expand=True)

        # ── Section tarification ──
        price_frm = tk.LabelFrame(
            body, text="  Tarification (pour référence)  ",
            bg=BG, font=('Arial', 9, 'bold'), fg=HDR_BG,
            padx=14, pady=8, relief='groove')
        price_frm.pack(fill='x', pady=(0, 12))

        prices = [
            ("Starter  (10 emp.)", "500 000 GNF/mois", "5 000 000 GNF/an"),
            ("Pro      (50 emp.)", "1 500 000 GNF/mois", "15 000 000 GNF/an"),
            ("Enterprise (illim.)", "3 000 000 GNF/mois", "30 000 000 GNF/an"),
        ]
        for i, (plan, monthly, yearly) in enumerate(prices):
            tk.Label(price_frm, text=f"{plan}:", font=('Arial', 8, 'bold'),
                     bg=BG, fg=LABEL_FG, width=20, anchor='w').grid(
                row=i, column=0, sticky='w')
            tk.Label(price_frm, text=monthly, font=('Arial', 8), bg=BG,
                     fg='#666').grid(row=i, column=1, sticky='w', padx=(10, 20))
            tk.Label(price_frm, text=yearly, font=('Arial', 8, 'bold'),
                     bg=BG, fg=ACCENT).grid(row=i, column=2, sticky='w')

        # ── Section client ──
        client_frm = tk.LabelFrame(
            body, text="  Informations du client  ",
            bg=BG, font=('Arial', 9, 'bold'), fg=HDR_BG,
            padx=14, pady=12, relief='groove')
        client_frm.pack(fill='x', pady=(0, 12))

        # ID Machine
        tk.Label(client_frm, text="ID Machine du client :",
                 font=('Arial', 9, 'bold'), bg=BG, fg=LABEL_FG).grid(
            row=0, column=0, columnspan=2, sticky='w', pady=(0, 3))
        self.mid_var = tk.StringVar()
        tk.Entry(client_frm, textvariable=self.mid_var,
                 font=('Courier', 10), width=44,
                 relief='flat', bd=1, bg=ENTRY_BG, fg=HDR_BG).grid(
            row=1, column=0, columnspan=2, sticky='ew',
            ipady=5, pady=(0, 10))

        # Nom de l'entreprise
        tk.Label(client_frm, text="Nom de l'entreprise :",
                 font=('Arial', 9, 'bold'), bg=BG, fg=LABEL_FG).grid(
            row=2, column=0, columnspan=2, sticky='w', pady=(0, 3))
        self.company_var = tk.StringVar()
        tk.Entry(client_frm, textvariable=self.company_var,
                 font=('Arial', 10), width=44,
                 relief='flat', bd=1, bg=ENTRY_BG).grid(
            row=3, column=0, columnspan=2, sticky='ew',
            ipady=5, pady=(0, 10))

        # Édition + Durée
        left = tk.Frame(client_frm, bg=BG)
        left.grid(row=4, column=0, sticky='w')
        right = tk.Frame(client_frm, bg=BG)
        right.grid(row=4, column=1, sticky='w', padx=(20, 0))

        tk.Label(left, text="Édition :",
                 font=('Arial', 9, 'bold'), bg=BG, fg=LABEL_FG).pack(anchor='w')
        self.edition_var = tk.StringVar(value='Standard')
        ttk.Combobox(left, textvariable=self.edition_var,
                     values=['Starter', 'Pro', 'Enterprise'],
                     state='readonly', width=14,
                     font=('Arial', 10)).pack(anchor='w', pady=(4, 0))

        tk.Label(right, text="Durée (jours) :",
                 font=('Arial', 9, 'bold'), bg=BG, fg=LABEL_FG).pack(anchor='w')
        days_row = tk.Frame(right, bg=BG)
        days_row.pack(anchor='w', pady=(4, 0))
        self.days_var = tk.StringVar(value='365')
        tk.Entry(days_row, textvariable=self.days_var,
                 font=('Arial', 10), width=7,
                 relief='flat', bd=1, bg=ENTRY_BG).pack(side='left', ipady=4)
        tk.Label(days_row, text=" jours  (365 = 1 an)",
                 font=('Arial', 8), bg=BG, fg='#888').pack(side='left')

        client_frm.columnconfigure(0, weight=1)
        client_frm.columnconfigure(1, weight=1)

        # ── Fichier de sortie ──
        out_frm = tk.LabelFrame(
            body, text="  Fichier de licence à générer  ",
            bg=BG, font=('Arial', 9, 'bold'), fg=HDR_BG,
            padx=14, pady=10, relief='groove')
        out_frm.pack(fill='x', pady=(0, 12))

        self.out_var = tk.StringVar(value="")
        out_row = tk.Frame(out_frm, bg=BG)
        out_row.pack(fill='x')
        tk.Entry(out_row, textvariable=self.out_var,
                 font=('Arial', 9), state='readonly',
                 readonlybackground='#f9f9f9',
                 relief='flat', bd=1).pack(
            side='left', fill='x', expand=True, ipady=5)

        def _browse_out():
            mid_short = self.mid_var.get().strip()[:8] or 'client'
            p = filedialog.asksaveasfilename(
                title="Enregistrer le fichier de licence",
                initialfile=f"licence_{mid_short}.lic",
                defaultextension=".lic",
                filetypes=[("Fichier licence", "*.lic"),
                           ("Tous les fichiers", "*.*")])
            if p:
                self.out_var.set(p)

        tk.Button(out_row, text="  Choisir…  ", command=_browse_out,
                  font=('Arial', 9), bg=GREY, fg='white',
                  relief='flat', padx=6, pady=5, cursor='hand2').pack(
            side='left', padx=(6, 0))
        tk.Label(out_frm,
                 text="Laissez vide pour enregistrer dans le dossier courant.",
                 font=('Arial', 8), bg=BG, fg='#888').pack(anchor='w', pady=(4, 0))

        # ── Résultat ──
        self.result_var = tk.StringVar(value="")
        self.result_lbl = tk.Label(body, textvariable=self.result_var,
                                   font=('Arial', 9), bg=BG, fg=ACCENT,
                                   wraplength=520, justify='left')
        self.result_lbl.pack(anchor='w', pady=(0, 8))

        # ── Bouton Générer ──
        tk.Button(body,
                  text="      Générer le fichier de licence      ",
                  command=self._generate,
                  font=('Arial', 12, 'bold'), bg=ACCENT, fg='white',
                  relief='flat', padx=14, pady=10,
                  cursor='hand2').pack(anchor='center')

    def _build_footer(self):
        footer = tk.Frame(self.root, bg='#d5d8dc', height=36)
        footer.pack(fill='x', side='bottom')
        footer.pack_propagate(False)
        try:
            my_mid = get_machine_id()
            short = my_mid[:8] + "...  (complet : " + my_mid + ")"
        except Exception:
            short = "N/A"
        tk.Label(footer, text=f"Machine distributeur : {short}",
                 font=('Arial', 7), bg='#d5d8dc', fg='#555').place(
            relx=0.5, rely=0.5, anchor='center')

    def _generate(self):
        mid     = self.mid_var.get().strip()
        company = self.company_var.get().strip()
        edition = self.edition_var.get().strip() or 'Starter'
        days_str = self.days_var.get().strip()
        out_path = self.out_var.get().strip()

        if not mid:
            messagebox.showwarning("Champ manquant",
                                   "Veuillez saisir l'identifiant machine du client.")
            return
        if len(mid) < 8:
            messagebox.showwarning("Identifiant invalide",
                                   "L'identifiant machine doit faire au moins 8 caractères.")
            return
        if not company:
            messagebox.showwarning("Champ manquant",
                                   "Veuillez saisir le nom de l'entreprise.")
            return
        try:
            days = int(days_str)
            if not (1 <= days <= 3650):
                raise ValueError()
        except ValueError:
            messagebox.showwarning("Durée invalide",
                                   "La durée doit être un entier entre 1 et 3650 jours.")
            return

        try:
            lic_data = generate_activation_file(mid, days, company, edition)
        except Exception as exc:
            messagebox.showerror("Erreur de génération", str(exc))
            return

        if not out_path:
            out_path = os.path.join(BASE, f"licence_{mid[:8]}.lic")
            self.out_var.set(out_path)

        try:
            with open(out_path, 'w', encoding='utf-8') as f:
                json.dump(lic_data, f, indent=2, ensure_ascii=False)
        except Exception as exc:
            messagebox.showerror("Erreur d'écriture", str(exc))
            return

        from datetime import datetime, timedelta
        exp_date = (datetime.utcnow() + timedelta(days=days)).strftime('%d/%m/%Y')
        filename = os.path.basename(out_path)
        self.result_var.set(
            f"Licence générée : {filename}\n"
            f"   Entreprise : {company}  |  Édition : {edition}  |  Expire le : {exp_date}")
        self.result_lbl.config(fg=ACCENT)
        messagebox.showinfo(
            "Licence générée avec succès",
            f"Fichier créé !\n\n"
            f"Fichier    : {filename}\n"
            f"Entreprise : {company}\n"
            f"Édition    : {edition}\n"
            f"Durée      : {days} jour(s)\n"
            f"Expire     : {exp_date}\n\n"
            f"Envoyez ce fichier au client par email.")


def main():
    root = tk.Tk()
    LicenseGeneratorApp(root)
    root.mainloop()


if __name__ == '__main__':
    main()
