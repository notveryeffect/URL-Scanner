# file: url_footer_scraper_gui.py

import requests
from bs4 import BeautifulSoup
import customtkinter as ctk
from tkinter import messagebox, filedialog
import json
import csv
import re
import threading

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

# Core scraping logic
def fetch_contacts_from_footer(url, keywords):
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        footer = soup.find('footer')
        if not footer:
            return ['Nessun footer trovato.']

        items = footer.find_all(class_='list-item')
        texts = [item.get_text(strip=True) for item in items]

        filtered = []
        for t in texts:
            tl = t.lower()
            if any(k in tl for k in keywords):
                filtered.append(t)
            elif re.search(r'\b\w+@\w+\.\w+\b', t):
                filtered.append(t)
            elif re.search(r'(\+?\d{1,4}[\s-]?)?(\(?\d{2,4}\)?[\s-]?)?\d{3,4}[\s-]?\d{3,4}', t):
                filtered.append(t)

        return filtered if filtered else ['Nessuna informazione di contatto trovata.']
    except Exception as e:
        return [f'Errore: {str(e)}']

# Save results
def save_results(results, file_format):
    file_path = filedialog.asksaveasfilename(defaultextension=f".{file_format}",
                                             filetypes=[(f"{file_format.upper()} file", f"*.{file_format}")])
    if not file_path:
        return

    if file_format == 'json':
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
    elif file_format == 'csv':
        with open(file_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['URL', 'Contatti'])
            for url, data in results.items():
                for d in data:
                    writer.writerow([url, d])
    else:
        with open(file_path, 'w', encoding='utf-8') as f:
            for url, data in results.items():
                f.write(f"URL: {url}\nContatti:\n{chr(10).join(data)}\n{'-' * 40}\n")

# GUI Functionality
def export_table():
    results = {}
    for row in table.get(0, "end"):
        url, contact = row.split(" → ", 1)
        if url not in results:
            results[url] = []
        results[url].append(contact)
    fmt = format_var.get()
    save_results(results, fmt)

def copy_selected(event):
    try:
        selected = table.curselection()
        content = "\n".join([table.get(i) for i in selected])
        app.clipboard_clear()
        app.clipboard_append(content)
        app.update()
        messagebox.showinfo("Copiato", "Contenuto copiato negli appunti.")
    except:
        pass

def perform_scan(urls, keywords, fmt):
    results = {}
    output.delete("0.0", "end")
    table.delete(0, "end")

    total = len(urls)
    for idx, url in enumerate(urls, 1):
        output.insert("end", f"Analizzo {url}...\n")
        result = fetch_contacts_from_footer(url, keywords)
        results[url] = result
        for r in result:
            table.insert("end", f"{url} → {r}")
        output.insert("end", f"→ {'; '.join(result)}\n\n")
        progress_var.set((idx / total) * 100)
        app.update_idletasks()

    save_results(results, fmt)
    messagebox.showinfo("Finito", f"Analisi completata e salvata in formato {fmt.upper()}.")
    progress_var.set(0)

def start_scan():
    urls = entry.get("0.0", "end").strip().split(',')
    urls = [u.strip() for u in urls if u.strip()]
    fmt = format_var.get()
    keywords = keyword_entry.get().lower().split(',')
    keywords = [k.strip() for k in keywords if k.strip()]

    if email_var.get(): keywords.append("email")
    if phone_var.get(): keywords.append("telefono")
    if whatsapp_var.get(): keywords.append("whatsapp")
    keywords = list(set(keywords))

    if not urls:
        messagebox.showerror("Errore", "Inserisci almeno un URL valido.")
        return

    thread = threading.Thread(target=perform_scan, args=(urls, keywords, fmt))
    thread.start()

# === Modern GUI ===
app = ctk.CTk()
app.title("🌐 Contatti Footer Scanner Pro")
app.geometry("1000x850")

ctk.CTkLabel(app, text="🔍 Analizzatore di Footer Web", font=("Segoe UI", 22, "bold")).pack(pady=10)

frame_inputs = ctk.CTkFrame(app)
frame_inputs.pack(fill="x", padx=20, pady=10)

ctk.CTkLabel(frame_inputs, text="Inserisci URL separati da virgola:").pack(anchor="w")
entry = ctk.CTkTextbox(frame_inputs, height=80)
entry.pack(fill="x", pady=5)

ctk.CTkLabel(frame_inputs, text="Parole chiave da cercare (separate da virgola):").pack(anchor="w")
keyword_entry = ctk.CTkEntry(frame_inputs)
keyword_entry.pack(fill="x", pady=5)

checkbox_frame = ctk.CTkFrame(frame_inputs)
checkbox_frame.pack(anchor='w', pady=5)
email_var = ctk.BooleanVar(value=True)
phone_var = ctk.BooleanVar(value=True)
whatsapp_var = ctk.BooleanVar(value=False)
ctk.CTkCheckBox(checkbox_frame, text="Email", variable=email_var).pack(side="left")
ctk.CTkCheckBox(checkbox_frame, text="Telefono", variable=phone_var).pack(side="left")
ctk.CTkCheckBox(checkbox_frame, text="Whatsapp", variable=whatsapp_var).pack(side="left")

format_var = ctk.StringVar(value="json")
format_frame = ctk.CTkFrame(app)
format_frame.pack(pady=5)
ctk.CTkLabel(format_frame, text="Formato esportazione:").pack(side="left")
for fmt in ['json', 'csv', 'txt']:
    ctk.CTkRadioButton(format_frame, text=fmt.upper(), variable=format_var, value=fmt).pack(side="left")

ctk.CTkButton(app, text="🚀 Avvia Scansione", command=start_scan).pack(pady=10)

progress_var = ctk.DoubleVar()
progress_bar = ctk.CTkProgressBar(app, variable=progress_var)
progress_bar.pack(fill="x", padx=20, pady=5)

ctk.CTkLabel(app, text="Risultati trovati:").pack()
table = ctk.CTkListbox(app, height=200)
table.pack(fill="both", expand=True, padx=20, pady=10)
table.bind("<Double-1>", copy_selected)

ctk.CTkButton(app, text="💾 Esporta Tabella", command=export_table).pack(pady=5)

output = ctk.CTkTextbox(app, height=140)
output.pack(fill="both", expand=True, padx=20, pady=10)

app.mainloop()
