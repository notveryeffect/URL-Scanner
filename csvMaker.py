import pandas as pd

# Dati estratti manualmente
data = [
    ["https://www.ipsisgaslinimeucci.edu.it/", "0107403503", "GERI07000P@istruzione.it", "geri07000p@pec.istruzione.it"],
    ["https://www.firpobuonarroti.edu.it/", "0108317103 - 0108317116", "GEIS00700L@istruzione.it", "GEIS00700L@pec.istruzione.it"],
    ["https://www.convittoge.edu.it/", "0102512421", "gevc010002@istruzione.it", "gevc010002@pec.istruzione.it"],
    ["https://www.gastaldi-abba.edu.it/", "010.265305, 010.7450679", "geis01600b@istruzione.it", "geis01600b@pec.istruzione.it"],
    ["https://www.ecg-genova.edu.it/", "010261672, 010460646", "geis004005@istruzione.it", "geis004005@pec.istruzione.it"],
    ["https://calvino.edu.it/", "+39 010 6508778, +39 010 6504672", "GEIS01400Q@istruzione.it", "GEIS01400Q@pec.istruzione.it"],
    ["https://www.ipsiaodero.edu.it/", "010-6011232/234/235/236", "scuola@ipsiaodero.it", "GERI02000N@pec.istruzione.it"],
    ["https://www.istitutobergese.edu.it/", "010 6503862", "GEIS02300E@istruzione.it", "GEIS02300E@pec.istruzione.it"],
    ["https://www.ver.edu.it/", "+39 010 2470778", "geis00600r@istruzione.it", "geis00600r@pec.istruzione.it"],
    ["https://www.iovallescrivia.edu.it/", "010 9643160", "geis017007@istruzione.it", "geis017007@pec.istruzione.it"],
    ["https://iisdavigonicoloso.edu.it/", "0185 61082", "geis00100n@istruzione.it", "geis00100n@pec.istruzione.it"],
    ["https://www.majorana-giorgi.edu.it/", "010-8356661, 010-393341", "geis018003@istruzione.it", "GEIS018003@pec.istruzione.it"],
    ["https://www.itpchiavari.edu.it/", "0185 322108, 0185 325003", "geis01900v@istruzione.it", "geis01900v@pec.istruzione.it"],
    ["https://www.lanfranconi.edu.it/", "0106133813", "geps080004@istruzione.it", "geps080004@pec.istruzione.it"],
    ["https://www.liceokleebarabino.edu.it/", "010 37745 83 - 86", "gesl01000p@istruzione.it", "gesl01000p@pec.istruzione.it"],
    ["https://www.gobetti.edu.it/", "0106469787", "gepm030004@istruzione.it", ""],
    ["https://www.liceopertini.edu.it/", "+39 010 313824", "info@liceopertini.edu.it", "gepm04000p@pec.istruzione.it"],
    ["https://www.liceoartisticoluzzati.edu.it/", "+39 0185 307754", "GESD010008@istruzione.it", "GESD010008@pec.istruzione.it"],
    ["https://www.liceoking.edu.it/", "010380344, 3665846534", "geps07000d@istruzione.it", "geps07000d@pec.istruzione.it"],
    ["https://www.liceti.edu.it/", "0185 63936", "geis01300x@istruzione.it", "geis01300x@pec.istruzione.it"],
    ["https://www.liceocassini.it/", "010 580686", "geps030003@istruzione.it", "geps030003@pec.istruzione.it"],
    ["https://www.liceoleodavincige.edu.it/", "010/814900", "GEPS050008@istruzione.it", "GEPS050008@pec.istruzione.it"],
    ["https://www.nattadeambrosis.edu.it/", "", "geis011008@istruzione.it", "geis011008@pec.istruzione.it"]
]

# Creazione del DataFrame
df = pd.DataFrame(data, columns=["URL", "Telefono", "Email", "PEC"])

# Esporta in CSV
df.to_csv("contatti_scuole.csv", index=False)
print("File CSV creato: contatti_scuole.csv")
