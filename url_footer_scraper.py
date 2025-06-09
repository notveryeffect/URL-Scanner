# file: url_footer_scraper_gui.py

import requests
from bs4 import BeautifulSoup
import tkinter as tk
from tkinter import messagebox, filedialog, ttk
import json
import csv
import re
import threading

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
    for row in table.get_children():
        url, contact = table.item(row)['values']
        if url not in results:
            results[url] = []
        results[url].append(contact)
    fmt = format_var.get()
    save_results(results, fmt)

def copy_selected(event):
    selected = table.selection()
    if selected:
        content = '\n'.join(['\t'.join(map(str, table.item(s)['values'])) for s in selected])
        root.clipboard_clear()
        root.clipboard_append(content)
        root.update()
        messagebox.showinfo("Copiato", "Contenuto copiato negli appunti.")

def perform_scan(urls, keywords, fmt):
    results = {}
    output.delete("1.0", tk.END)
    for i in table.get_children():
        table.delete(i)

    total = len(urls)
    for idx, url in enumerate(urls, 1):
        output.insert(tk.END, f"Analizzo {url}...\n")
        result = fetch_contacts_from_footer(url, keywords)
        results[url] = result
        for r in result:
            table.insert('', 'end', values=(url, r))
        output.insert(tk.END, f"→ {'; '.join(result)}\n\n")
        progress_var.set((idx / total) * 100)
        progress_bar.update()

    save_results(results, fmt)
    messagebox.showinfo("Finito", f"Analisi completata e salvata in formato {fmt.upper()}.")
    progress_var.set(0)

def start_scan():
    urls = entry.get("1.0", tk.END).strip().split(',')
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

# === Beautiful GUI ===
root = tk.Tk()
root.title("🌐 Contatti Footer Scanner Deluxe")
root.geometry("1000x850")
root.configure(bg="#fdf6e3")

style = ttk.Style()
style.theme_use('clam')
style.configure("Treeview", font=('Segoe UI', 10), rowheight=28)
style.configure("Treeview.Heading", font=('Segoe UI Semibold', 11), background="#268bd2", foreground="white")

title_label = tk.Label(root, text="🔍 Analizzatore di Footer Web", font=("Segoe UI", 20, "bold"), bg="#fdf6e3", fg="#002b36")
title_label.pack(pady=10)

frame_inputs = tk.Frame(root, bg="#fdf6e3")
frame_inputs.pack(fill=tk.X, padx=20, pady=10)

entry_label = tk.Label(frame_inputs, text="Inserisci URL separati da virgola:", bg="#fdf6e3")
entry_label.pack(anchor='w')

entry = tk.Text(frame_inputs, height=4, font=('Segoe UI', 10))
entry.pack(fill=tk.X, pady=5)

keyword_label = tk.Label(frame_inputs, text="Parole chiave da cercare (separate da virgola):", bg="#fdf6e3")
keyword_label.pack(anchor='w')

keyword_entry = tk.Entry(frame_inputs, font=('Segoe UI', 10))
keyword_entry.pack(fill=tk.X, pady=5)

checkbox_frame = tk.Frame(frame_inputs, bg="#fdf6e3")
checkbox_frame.pack(anchor='w', pady=5)
email_var = tk.BooleanVar(value=True)
phone_var = tk.BooleanVar(value=True)
whatsapp_var = tk.BooleanVar(value=False)
tk.Checkbutton(checkbox_frame, text="Email", variable=email_var, bg="#fdf6e3").pack(side=tk.LEFT)
tk.Checkbutton(checkbox_frame, text="Telefono", variable=phone_var, bg="#fdf6e3").pack(side=tk.LEFT)
tk.Checkbutton(checkbox_frame, text="Whatsapp", variable=whatsapp_var, bg="#fdf6e3").pack(side=tk.LEFT)

format_frame = tk.Frame(root, bg="#fdf6e3")
format_frame.pack(pady=5)
format_var = tk.StringVar(value='json')
tk.Label(format_frame, text="Formato esportazione:", bg="#fdf6e3").pack(side=tk.LEFT)
for fmt in ['json', 'csv', 'txt']:
    tk.Radiobutton(format_frame, text=fmt.upper(), variable=format_var, value=fmt, bg="#fdf6e3").pack(side=tk.LEFT)

scan_btn = tk.Button(root, text="🚀 Avvia Scansione", command=start_scan, bg="#2aa198", fg="white",
                     font=("Segoe UI", 11, "bold"), padx=10, pady=5)
scan_btn.pack(pady=10)

progress_var = tk.DoubleVar()
progress_bar = ttk.Progressbar(root, variable=progress_var, maximum=100)
progress_bar.pack(fill=tk.X, padx=20, pady=5)

# Table Section
table_frame = tk.Frame(root)
table_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
columns = ('URL', 'Contatti')
table = ttk.Treeview(table_frame, columns=columns, show='headings')
for col in columns:
    table.heading(col, text=col)
    table.column(col, anchor="w")
table.pack(fill=tk.BOTH, expand=True)
table.bind('<Double-1>', copy_selected)

export_btn = tk.Button(root, text="💾 Esporta Tabella", command=export_table, bg="#859900", fg="white",
                       font=("Segoe UI", 10, "bold"), padx=10, pady=5)
export_btn.pack(pady=5)

output = tk.Text(root, height=10, bg="#eee8d5", font=('Consolas', 10))
output.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

root.mainloop()
