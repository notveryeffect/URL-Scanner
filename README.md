# 🔍 URL Footer Contact Scraper
A simple but powerful desktop app built with Python and Tkinter that scans website footers for contact information like emails, phone numbers, and WhatsApp links. Perfect for lead generation, research, or just scraping useful contact info from multiple websites — with one click.

## 🚀 Features
🧠 Smart Footer Scanning
Automatically detects and parses the <footer> section of a website for contact-related content.

### 🔑 Custom Keyword Filtering
Add your own keywords (like contact, support, office) to find specific info.

### 📧 Automatic Email & Phone Detection
Uses regex to pick up emails, phone numbers, and optional WhatsApp mentions.

### 🖱️ Easy-to-Use GUI
Built with Tkinter — just copy-paste URLs, tweak your settings, and hit scan.

### 💾 Export Formats
Save results in JSON, CSV, or TXT with one click.

### 📋 Clipboard Copy
Double-click a result to instantly copy it to your clipboard.

## 📦 Requirements
Install the required libraries if you haven’t already:

bash
Copia
Modifica
pip install requests beautifulsoup4
🖥️ How to Use
Run the script:

bash
Copia
Modifica
python url_footer_scraper.py
Enter URLs (comma-separated).

Add keywords to search for (optional).

Choose what to scan:
✅ Email, ☎ Phone, 💬 WhatsApp (toggle via checkboxes).

Select export format: JSON / CSV / TXT.

Click "Start Scan" — that’s it!

Export or copy results from the table.

## 📁 Output Formats
JSON
json
Copia
Modifica
```
{
  "https://example.com": [
    "info@example.com",
    "+1 234 567 890"
  ]
}
```

CSV
```
URL	                Contact
https://site.com	contact@site.com
```
TXT

```
markdown
Copia
Modifica
URL: https://example.com
Contacts:
support@example.com
+39 347 123 4567
----------------------------------------
```
## 💡 Use Cases
Lead scraping from agency or directory sites

Quick contact discovery for B2B research

Extract support or business info from clients’ websites

Academic or marketing research

⚠️ Notes
Works best on websites with properly structured <footer> tags.

May miss dynamically loaded content (JavaScript-based).

Respect robots.txt and site scraping policies.
