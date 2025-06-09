# file: url_footer_scraper.py

import requests
from bs4 import BeautifulSoup
import tkinter as tk
from tkinter import messagebox, filedialog, ttk
import json
import csv
import re


def fetch_contacts_from_footer(url):
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
            if 'email' in tl or 'telefono' in tl:
                filtered.append(t)
            elif re.search(r'\b\w+@\w+\.\w+\b', t):
                filtered.append(t)
            elif re.search(r'(\+?\d{1,4}[\s-]?)?(\(?\d{2,4}\)?[\s-]?)?\d{3,4}[\s-]?\d{3,4}', t):
                filtered.append(t)

        return filtered if filtered else ['Nessuna informazione di contatto trovata.']
    except Exception as e:
        return [f'Errore: {str(e)}']


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
                writer.writerow([url, '\n'.join(data)])
    else:  # txt
        with open(file_path, 'w', encoding='utf-8') as f:
            for url, data in results.items():
                f.write("URL: {}\nContatti:\n{}\n{}\n".format(url, '\n'.join(data), '-' * 40))



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


def start_scan():
    urls = entry.get("1.0", tk.END).strip().split(',')
    urls = [u.strip() for u in urls if u.strip()]
    fmt = format_var.get()

    if not urls:
        messagebox.showerror("Errore", "Inserisci almeno un URL valido.")
        return

    results = {}
    output.delete("1.0", tk.END)
    for i in table.get_children():
        table.delete(i)

    for url in urls:
        output.insert(tk.END, f"Analizzo {url}...\n")
        result = fetch_contacts_from_footer(url)
        results[url] = result
        for r in result:
            table.insert('', 'end', values=(url, r))
        output.insert(tk.END, f"→ {'; '.join(result)}\n\n")

    save_results(results, fmt)
    messagebox.showinfo("Finito", f"Analisi completata e salvata in formato {fmt.upper()}.")


# === GUI ===
root = tk.Tk()
root.title("Contatti Footer Scanner")
root.geometry("800x650")

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

# Tabella risultati
table_frame = tk.Frame(root)
table_frame.pack(fill=tk.BOTH, expand=True, padx=10)

columns = ('URL', 'Contatti')
table = ttk.Treeview(table_frame, columns=columns, show='headings')
table.heading('URL', text='URL')
table.heading('Contatti', text='Contatti')
table.pack(fill=tk.BOTH, expand=True)
table.bind('<Double-1>', copy_selected)

export_btn = tk.Button(root, text="Esporta da tabella", command=export_table)
export_btn.pack(pady=5)

output = tk.Text(root, height=10, bg="#f0f0f0")
output.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

root.mainloop()
