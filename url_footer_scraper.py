# file: url_footer_scraper.py

import requests
from bs4 import BeautifulSoup
import tkinter as tk
from tkinter import messagebox, filedialog
import json
import csv


def fetch_contacts_from_footer(url):
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        footer = soup.find('footer')
        if not footer:
            return 'Nessun footer trovato.'

        # Heuristic search for contact info
        contact_section = footer.find_all(string=lambda text: text and 'contatt' in text.lower())
        return '\n'.join(set(t.strip() for t in contact_section)) or 'Nessun contatto trovato.'
    except Exception as e:
        return f'Errore: {str(e)}'


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
                writer.writerow([url, data])
    else:  # txt
        with open(file_path, 'w', encoding='utf-8') as f:
            for url, data in results.items():
                f.write(f"URL: {url}\nContatti:\n{data}\n{'-'*40}\n")


def start_scan():
    urls = entry.get("1.0", tk.END).strip().split(',')
    urls = [u.strip() for u in urls if u.strip()]
    fmt = format_var.get()
    
    if not urls:
        messagebox.showerror("Errore", "Inserisci almeno un URL valido.")
        return

    results = {}
    output.delete("1.0", tk.END)

    for url in urls:
        output.insert(tk.END, f"Analizzo {url}...\n")
        result = fetch_contacts_from_footer(url)
        results[url] = result
        output.insert(tk.END, f"→ {result}\n\n")

    save_results(results, fmt)
    messagebox.showinfo("Finito", f"Analisi completata e salvata in formato {fmt.upper()}.")


# === GUI ===
root = tk.Tk()
root.title("Contatti Footer Scanner")
root.geometry("600x500")

label = tk.Label(root, text="Inserisci URL separati da virgola:")
label.pack()

entry = tk.Text(root, height=5)
entry.pack(fill=tk.X, padx=10)

format_var = tk.StringVar(value='json')
format_frame = tk.Frame(root)
for fmt in ['json', 'csv', 'txt']:
    tk.Radiobutton(format_frame, text=fmt.upper(), variable=format_var, value=fmt).pack(side=tk.LEFT)
format_frame.pack(pady=5)

btn = tk.Button(root, text="Avvia Scansione", command=start_scan)
btn.pack(pady=5)

output = tk.Text(root, height=20, bg="#f0f0f0")
output.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

root.mainloop()
