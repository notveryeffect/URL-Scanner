# file: Scanner GUI.py

import requests
from bs4 import BeautifulSoup
import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox, filedialog
import json
import csv
import re
import threading
import webbrowser
from PIL import Image, ImageTk
import spacy
from urllib.parse import urlparse
import phonenumbers

# Carica modello italiano spaCy (solo una volta)
nlp = spacy.load("it_core_news_sm")

# Importa tkinterdnd2 per drag and drop
from tkinterdnd2 import DND_FILES, TkinterDnD

ctk.set_appearance_mode("white")   # if white theme = white | if black theme = black
ctk.set_default_color_theme("blue") # always blue

# Core scraping logic
#def fetch_contacts_from_footer(url, keywords):
#    try:
#        response = requests.get(url, timeout=10)
#        soup = BeautifulSoup(response.text, 'html.parser')
#        footer = soup.find('footer')
#        if not footer:
#            return ['Nessun footer trovato.']
#
#        # Cerca elementi con class_='list-item', tag <a>, <p>, <li> e href
#        items = footer.find_all(['a']) + footer.find_all('href') + footer.find_all(class_='list-item') + footer.find_all(['p'])
#
#        # Rimuove duplicati mantenendo l'ordine
#        seen = set()
#        unique_items = []
#        for item in items:
#            if item not in seen:
#                unique_items.append(item)
#                seen.add(item)
#
#        texts = [item.get_text(strip=True) for item in unique_items]
#
#
#        filtered = []
#        for t in texts:
#            tl = t.lower()
#            if any(k in tl for k in keywords):
#                filtered.append(t)
#            elif re.search(r'\b\w+@\w+\.\w+\b', t):
#                filtered.append(t)
#            elif re.search(r'(\+?\d{1,4}[\s-]?)?(\(?\d{2,4}\)?[\s-]?)?\d{3,4}[\s-]?\d{3,4}', t):
#                filtered.append(t)
#
#        return filtered if filtered else ['Nessuna informazione di contatto trovata.']
#    except Exception as e:
#        return [f'Errore: {str(e)}']

def normalize_url(url):
    parsed = urlparse(url)
    if not parsed.scheme:
        url = 'http://' + url
    return url

def extract_phone_numbers(text, default_region='IT'):
    phone_numbers = []
    for match in phonenumbers.PhoneNumberMatcher(text, default_region):
        number = phonenumbers.format_number(match.number, phonenumbers.PhoneNumberFormat.E164)
        if number not in phone_numbers:
            phone_numbers.append(number)
    return phone_numbers

def fetch_contacts_from_footer(url):
    try:
        url = normalize_url(url)
        print(f"Fetching URL: {url}")
        response = requests.get(url, timeout=15)
        print("Response received, parsing HTML...")
        soup = BeautifulSoup(response.text, 'html.parser')

        footer = soup.find('footer')
        if footer:
            print("Footer found, extracting text from footer...")
            search_area = footer
        else:
            print("Footer not found, using body...")
            search_area = soup.body or soup

        elements = search_area.find_all(['li', 'p', 'a'])
        print(f"Found {len(elements)} elements to scan.")

        testi = [el.get_text(separator=' ', strip=True) for el in elements if el.get_text(strip=True)]

        exclude_keywords = ['cookie', 'privacy', 'note legali', 'facebook', 'instagram', 'youtube', 'telegram',
                            'twitter', 'whistleblowing', 'amministrazione trasparente', 'albo online',
                            'ufficio relazioni', 'pagina visualizzata', 'obiettivi di accessibilità',
                            'gestione consensi', 'dichiarazione di accessibilità']

        indirizzo_pattern = re.compile(r'\b(via|viale|corso|piazza|strada|località|contrada|borgo|lungo)\b.*', re.IGNORECASE)
        email_pattern = re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+")
        phone_pattern = re.compile(r"\+?\d[\d\s()./-]{5,}\d")

        filtered_lines = []

        for line in testi:
            lower_line = line.lower()
            if any(ex in lower_line for ex in exclude_keywords):
                continue

            # email
            emails = email_pattern.findall(line)
            for email in emails:
                if email not in filtered_lines:
                    filtered_lines.append(email)

            # phones con phonenumbers
            phones = extract_phone_numbers(line)
            for phone in phones:
                if phone not in filtered_lines:
                    filtered_lines.append(phone)

            # indirizzi
            if indirizzo_pattern.search(line):
                if line not in filtered_lines:
                    filtered_lines.append(line)

        if not filtered_lines:
            return ['Nessuna informazione di contatto trovata.']

        print(f"Contacts found: {len(filtered_lines)}")
        return filtered_lines

    except requests.exceptions.RequestException as req_err:
        return [f'Errore di richiesta: {str(req_err)}']
    except Exception as e:
        return [f'Errore generico: {str(e)}']


def analizza_testo_con_spacy(testo):
    doc = nlp(testo)

    emails = re.findall(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", testo)
    pec = [e for e in emails if "pec" in e.lower()]
    telefoni = re.findall(r"\+?\d[\d\s().-]{6,}\d", testo)

    # Filtra fuori numeri troppo lunghi (es. codici fiscali)
    telefoni = [t.strip() for t in telefoni if 6 <= len(re.sub(r'\D', '', t)) <= 15]

    indirizzi = []
    for ent in doc.ents:
        if ent.label_ in ["LOC", "GPE", "FAC", "ADDRESS"]:
            indirizzi.append(ent.text)

    # Rimuovi parole inutili
    stopwords = {"tel", "telefono", "link", "per", "inviare", "una", "mail"}
    indirizzi = [i for i in indirizzi if i.lower() not in stopwords]

    risultati = set(emails + pec + telefoni + indirizzi)
    return list(risultati)


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
            writer.writerow(['URL', 'Telefono', 'Email', 'PEC'])

            for url, contatti in results.items():
                telefoni = []
                email = []
                pec = []

                for dato in contatti:
                    if re.search(r'@', dato):
                        if 'pec' in dato.lower():
                            pec.append(dato)
                        else:
                            email.append(dato)
                    elif re.search(r'\+?\d[\d\s().-]{6,}', dato):
                        telefoni.append(dato)

                row = [
                    url,
                    "; ".join(telefoni),
                    "; ".join(email),
                    "; ".join(pec)
                ]
                writer.writerow(row)

    else:  # txt
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
        result = fetch_contacts_from_footer(url)
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
app = TkinterDnD.Tk()   # Usa TkinterDnD per drag & drop
app.title("🌐 Scanner AI Pro")
app.geometry("550x950")

ctk.set_appearance_mode("System")   # se vuoi puoi anche spostare dopo la creazione app
ctk.set_default_color_theme("blue")

ctk.CTkLabel(app, text="🔍 Analizzatore Web", font=("Segoe UI", 22, "bold")).pack(pady=2)
ctk.CTkLabel(app, text="Powered by an efficient AI Engine", font=("Segoe UI", 14, "bold")).pack(pady=0.5)

frame_inputs = ctk.CTkFrame(app)
frame_inputs.pack(fill="x", padx=20, pady=10)

ctk.CTkLabel(frame_inputs, text="Inserisci URL separati da virgola oppure un .txt con l'elenco: ").pack(anchor="w")
entry = ctk.CTkTextbox(frame_inputs, height=100)
entry.pack(fill="x", pady=5)

# Aggiungi drag and drop file txt per entry
def drop(event):
    file_path = event.data
    if file_path.startswith('{') and file_path.endswith('}'):
        file_path = file_path[1:-1]

    if file_path.endswith('.txt'):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            entry.delete("0.0", "end")
            entry.insert("0.0", content)
            messagebox.showinfo("File caricato", f"File '{file_path}' caricato correttamente.")
        except Exception as e:
            messagebox.showerror("Errore file", f"Impossibile leggere il file: {str(e)}")
    else:
        messagebox.showwarning("Tipo file non supportato", "Puoi trascinare solo file .txt")

entry.drop_target_register(DND_FILES)
entry.dnd_bind('<<Drop>>', drop)

ctk.CTkLabel(frame_inputs, text="Parole chiave da cercare (separate da virgola):").pack(anchor="w")
keyword_entry = ctk.CTkEntry(frame_inputs)
keyword_entry.pack(fill="x", pady=5)

checkbox_frame = ctk.CTkFrame(frame_inputs)
checkbox_frame.pack(anchor='w', pady=5)
email_var = ctk.BooleanVar(value=True)
phone_var = ctk.BooleanVar(value=True)
Indirizzo_var = ctk.BooleanVar(value=True)
PIVA_var = ctk.BooleanVar(value=False)
whatsapp_var = ctk.BooleanVar(value=False)

ctk.CTkCheckBox(checkbox_frame, text="Email", variable=email_var).pack(side="left")
ctk.CTkCheckBox(checkbox_frame, text="Telefono", variable=phone_var).pack(side="left")
ctk.CTkCheckBox(checkbox_frame, text="Indirizzo", variable=Indirizzo_var).pack(side="left")
ctk.CTkCheckBox(checkbox_frame, text="Partita IVA", variable=PIVA_var).pack(side="left")
ctk.CTkCheckBox(checkbox_frame, text="Whatsapp", variable=whatsapp_var).pack(side="left")

format_var = ctk.StringVar(value="json")
format_frame = ctk.CTkFrame(app)
format_frame.pack(pady=5)
ctk.CTkLabel(format_frame, text="Formato esportazione: ").pack(side="left")
for fmt in ['json', 'csv', 'txt']:
    ctk.CTkRadioButton(format_frame, text=fmt.upper(), variable=format_var, value=fmt).pack(side="left")

ctk.CTkButton(app, text="🚀 Avvia Scansione", command=start_scan).pack(pady=10)

progress_var = ctk.DoubleVar()
progress_bar = ctk.CTkProgressBar(app, variable=progress_var)
progress_bar.pack(fill="x", padx=20, pady=5)

ctk.CTkLabel(app, text="Risultati trovati:").pack()
table_frame = ctk.CTkFrame(app)
table_frame.pack(fill="both", expand=True, padx=20, pady=10)
table_scroll = ctk.CTkScrollbar(table_frame)
table_scroll.pack(side="right", fill="y")
table = tk.Listbox(table_frame, yscrollcommand=table_scroll.set, font=("Segoe UI", 10))
table.pack(fill="both", expand=True)
table_scroll.configure(command=table.yview)
table.bind("<Double-1>", copy_selected)

ctk.CTkButton(app, text="💾 Esporta Tabella", command=export_table).pack(pady=5)

output = ctk.CTkTextbox(app, height=140)
output.pack(fill="both", expand=True, padx=20, pady=10)

# =====================================================================

# Footer Frame
footer_frame = ctk.CTkFrame(app, fg_color="transparent")
footer_frame.pack(pady=10)

# Scritta
credit_label = ctk.CTkLabel(footer_frame, text="Grazie per averci scelto !", font=("Segoe UI", 16))
credit_label.pack(side="top", padx=(10, 5))
credit_label = ctk.CTkLabel(footer_frame, text="Developed by Flavio Boarini", font=("Segoe UI", 12))
credit_label.pack(side="left", padx=(10, 5))

# Funzione per aprire il link GitHub
def open_github():
    webbrowser.open_new("https://github.com/notveryeffect")

# Carica immagine GitHub
github_image = ctk.CTkImage(Image.open("github_icon.png"), size=(32, 32))

# Bottone con icona GitHub
github_button = ctk.CTkButton(
    footer_frame,
    image=github_image,
    text="",
    width=30,
    height=30,
    fg_color="transparent",
    hover_color="#d0d0d0",
    command=open_github
)
github_button.pack(side="left", padx=5)

# ======================================================================

app.mainloop()