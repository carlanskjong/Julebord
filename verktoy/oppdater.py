#!/usr/bin/env python3
"""Hjelpeverktøy for julebord-oversikten.

Kommandoer (kjør fra repo-roten):
  python3 -I verktoy/oppdater.py nye ID [ID ...]
      Skriver ut meldings-IDer som ikke er behandlet ennå. Ingen utskrift = ingenting nytt.
  python3 -I verktoy/oppdater.py marker ID [ID ...]
      Legger meldings-IDer til i data.json["behandlet"].
  python3 -I verktoy/oppdater.py vedlegg RAW_JSON_FIL RESTAURANT
      Pakker ut første bilde/PDF fra en Gmail get_message(RAW)-fil til meny/<restaurant>.jpg
      (maks 1100 px bredde, JPEG 72) og setter meny_bilde på raden.
  python3 -I verktoy/oppdater.py sett RESTAURANT felt=verdi [felt=verdi ...]
      Oppdaterer felt på én rad. pris_pp gjøres om til tall. Setter «oppdatert».
  python3 -I verktoy/oppdater.py valider
      Sjekker data.json og at menybildene finnes. Avslutter med feilkode ved feil.
  python3 -I verktoy/oppdater.py artefakt UTFIL
      Lager svar.json til Claude-oversikten (meny_bilde som data-URL).
"""
import base64
import datetime as dt
import email
import email.policy
import io
import json
import os
import re
import subprocess
import sys
import tempfile

ROT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROT, "data.json")
FELT = ["restaurant", "status", "sendt", "svar", "meny", "pris_pp", "allergi",
        "tid", "rom", "vilkar", "neste", "meny_bilde"]
# Valgfrie felt: meny_tekst (liste med retter, skriv med | mellom retter i «sett»),
# meny_lenke (https-lenke til menyen på restaurantens nettside), meny_kilde (kort tekst).
VALGFRIE = ["meny_tekst", "meny_lenke", "meny_kilde"]
STATUSER = {"Svart", "Venter", "Avslått", "Booket"}
OSLO = dt.timezone(dt.timedelta(hours=1))


def les():
    with open(DATA, encoding="utf-8") as f:
        return json.load(f)


def skriv(d):
    d["oppdatert"] = dt.datetime.now(OSLO).replace(microsecond=0).isoformat()
    with open(DATA, "w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False, indent=2)
        f.write("\n")


def slug(navn):
    s = navn.lower().replace("æ", "ae").replace("ø", "o").replace("å", "a")
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")


def rad(d, navn):
    for r in d["svar"]:
        if r["restaurant"].lower() == navn.lower():
            return r
    sys.exit(f"Fant ikke restauranten «{navn}» i data.json")


def til_jpg(innhold, mime):
    from PIL import Image
    if mime == "application/pdf":
        with tempfile.TemporaryDirectory() as t:
            pdf = os.path.join(t, "m.pdf")
            open(pdf, "wb").write(innhold)
            subprocess.run(["pdftoppm", "-f", "1", "-l", "1", "-r", "130", "-png", pdf, os.path.join(t, "s")], check=True)
            png = [p for p in os.listdir(t) if p.endswith(".png")][0]
            im = Image.open(os.path.join(t, png))
            im.load()
    else:
        im = Image.open(io.BytesIO(innhold))
    im = im.convert("RGB")
    if im.width > 1100:
        im = im.resize((1100, round(im.height * 1100 / im.width)), Image.LANCZOS)
    ut = io.BytesIO()
    im.save(ut, "JPEG", quality=72, optimize=True)
    return ut.getvalue()


def vedlegg(rawfil, navn):
    j = json.load(open(rawfil, encoding="utf-8"))
    raw = j["raw"] if isinstance(j, dict) else j
    try:
        b = base64.urlsafe_b64decode(raw + "=" * (-len(raw) % 4))
    except Exception:
        b = raw.encode()
    m = email.message_from_bytes(b, policy=email.policy.default)
    for p in m.iter_attachments():
        mime = p.get_content_type()
        if mime.startswith("image/") or mime == "application/pdf":
            jpg = til_jpg(p.get_content(), mime)
            os.makedirs(os.path.join(ROT, "meny"), exist_ok=True)
            sti = f"meny/{slug(navn)}.jpg"
            open(os.path.join(ROT, sti), "wb").write(jpg)
            d = les()
            rad(d, navn)["meny_bilde"] = sti
            skriv(d)
            print(f"{sti} ({len(jpg)//1024} kB, fra «{p.get_filename()}»)")
            return
    print("Ingen bilde- eller PDF-vedlegg i meldingen.")


def sett(navn, par):
    d = les()
    r = rad(d, navn)
    for p in par:
        k, _, v = p.partition("=")
        if k not in FELT + VALGFRIE:
            sys.exit(f"Ukjent felt: {k}")
        if k == "pris_pp":
            v = int(re.sub(r"[^\d]", "", v)) if re.search(r"\d", v) else None
        if k == "meny_tekst":
            v = [x.strip() for x in v.split("|") if x.strip()]
        if k == "meny_lenke" and v and not v.startswith("https://"):
            sys.exit("meny_lenke må starte med https://")
        r[k] = v
    skriv(d)


def valider():
    d = les()
    feil = []
    if not isinstance(d.get("svar"), list) or not d["svar"]:
        feil.append("svar mangler eller er tom")
    for r in d.get("svar", []):
        for k in FELT:
            if k not in r:
                feil.append(f"{r.get('restaurant')}: mangler {k}")
        if r.get("status") not in STATUSER:
            feil.append(f"{r.get('restaurant')}: ugyldig status {r.get('status')!r}")
        if r.get("pris_pp") not in (None, "") and not isinstance(r["pris_pp"], (int, float)):
            feil.append(f"{r.get('restaurant')}: pris_pp må være tall")
        mb = r.get("meny_bilde")
        if mb and not os.path.exists(os.path.join(ROT, mb)):
            feil.append(f"{r.get('restaurant')}: finner ikke {mb}")
        if "meny_tekst" in r and not (isinstance(r["meny_tekst"], list) and all(isinstance(x, str) for x in r["meny_tekst"])):
            feil.append(f"{r.get('restaurant')}: meny_tekst må være en liste med tekst")
        if r.get("meny_lenke") and not str(r["meny_lenke"]).startswith("https://"):
            feil.append(f"{r.get('restaurant')}: meny_lenke må starte med https://")
    if feil:
        print("\n".join(feil))
        sys.exit(1)
    print(f"OK: {len(d['svar'])} restauranter, {len(d.get('behandlet', []))} behandlede meldinger")


def artefakt(ut):
    d = les()
    rader = []
    for r in d["svar"]:
        r = dict(r)
        mb = r.get("meny_bilde")
        r["meny_bilde"] = ("data:image/jpeg;base64," + base64.b64encode(open(os.path.join(ROT, mb), "rb").read()).decode()) if mb else ""
        rader.append(r)
    json.dump(rader, open(ut, "w", encoding="utf-8"), ensure_ascii=False)
    print(f"{ut} ({os.path.getsize(ut)//1024} kB)")


def main(a):
    if not a:
        sys.exit(__doc__)
    k = a[0]
    if k == "nye":
        seen = set(les().get("behandlet", []))
        for i in a[1:]:
            if i not in seen:
                print(i)
    elif k == "marker":
        d = les()
        b = d.setdefault("behandlet", [])
        b.extend(i for i in a[1:] if i not in b)
        skriv(d)
    elif k == "vedlegg" and len(a) == 3:
        vedlegg(a[1], a[2])
    elif k == "sett" and len(a) >= 3:
        sett(a[1], a[2:])
    elif k == "valider":
        valider()
    elif k == "artefakt" and len(a) == 2:
        artefakt(a[1])
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main(sys.argv[1:])
