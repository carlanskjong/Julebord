# Rutine: følg med på bekreftelse fra Cru

Denne filen er oppskriften den planlagte oppgaven («Julebord: ringeklokke (hver time)») følger. Endre her, ikke i oppgaven.

## Status (3. nov.)
- Carl-Andreas har bestilt julebord hos **Cru** (post@cru.no) lørdag 12. desember kl. 19:45, 9 personer, 5 retter à 950 kr.
- Én gjest tåler ikke melk, egg, nøtter og sennep. Det gir tilpasset meny med 150 kr tillegg.
- Bestillingen ble sendt som svar i tråden «Forespørsel booking Julebord» 3. nov. Nå venter vi på bekreftelse.
- De andre restaurantene er ute av bildet:
  - Vaaghals, Kolonialen og Arakataka har fått nei takk.
  - Eik og Klosteret har aldri svart. Skulle de svare, skal de ikke få svar.

## Absolutte regler
- Ikke send, svar på, videresend eller lag utkast til e-post. Ikke book, endre eller avbestill noe.
- Det automatiske avslaget av alternativ dato er avviklet og skal ikke brukes.

## Steg
1. **Søk etter nye meldinger fra Cru.** Søk i Gmail med `from:cru.no newer_than:14d`. Hent tråden med get_thread (PLAIN_TEXT). Sjekk meldings-IDene med `python3 -I verktoy/oppdater.py nye <ID> ...`.
   - Er det ingenting nytt, avslutter du med «Ingen nye svar». Da gjør du ingen endringer.
2. **Ny melding fra Cru:**
   - **Bekrefter de bestillingen**, kjører du:
     `python3 -I verktoy/oppdater.py booking status=Bekreftet bekreftet=<ISO-tid for meldingen, +01:00>`
     Oppdater huskelisten: fjern «Vent på bekreftelse fra Cru.» og legg til det Cru ber om, f.eks. frister, forhåndsbetaling eller allergiliste:
     `booking "huskeliste=Punkt 1|Punkt 2|..."`
     Endrer de tid, antall, meny eller pris, oppdaterer du tilsvarende felt (`tid=`, `antall=`, `meny=`, `pris_pp=`, `vilkar=...|...`).
   - **Spør de om noe eller foreslår en endring**, setter du `booking "status=Cru trenger svar"` og legger spørsmålet øverst i huskelisten. Ikke svar dem.
   - **Avslår de**, setter du `booking "status=Avslått av Cru"`.
3. **Meldinger fra Eik eller Klosteret:** Ikke svar, og ikke oppdater siden. Nevn dem kort i oppsummeringen.
4. **Merk som behandlet** med `python3 -I verktoy/oppdater.py marker <nye ID-er>`. Kjør deretter `python3 -I verktoy/oppdater.py valider`.
5. **Publiser.**
   - Commit med forfatter `Carl-Andreas Skjong <carlan.skjong@gmail.com>`. Avslutt commit-meldingen med linjen `Co-Authored-By: Claude <noreply@anthropic.com>`.
   - Push til main. GitHub Pages publiserer automatisk til https://carlanskjong.github.io/Julebord/.
   - Bekreft at bygget er ferdig med `gh api repos/carlanskjong/Julebord/actions/runs --jq '.workflow_runs[0] | [.status,.conclusion] | @tsv'`.
6. **Oppdater Claude-oversikten** (https://claude.ai/artifact/2JU67PddyPSLvVAHvfoiAb).
   - Kjør `python3 -I verktoy/oppdater.py artefakt <scratch>/svar.json`.
   - Last opp filen med Artifact publish (url = oversikten, file_path = svar.json, asset: true).
   - Hent `datasets/svar` med ArtifactData get. Oppdater den med if_version: `source = {kind:"file", url:"<ny /_blob/-url>", name:"svar.json"}` og `updated = {at:<nå>, by:"Claude"}`.
   - Ikke endre `files/index.html`.
7. **Oppsummer** på norsk, kort. Begynn med det viktigste, f.eks. «Cru har bekreftet bookingen» eller «Cru trenger svar: …».

## Når oppgaven skal slå seg av
Deaktiver den planlagte oppgaven med update_trigger enabled=false når én av disse er sann:
- Bookingen har status «Bekreftet» eller «Avslått av Cru».
- Dagens dato er etter 12. desember 2026.
