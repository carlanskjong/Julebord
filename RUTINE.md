# Rutine: innbokssjekk for julebord

Denne filen er oppskriften den planlagte oppgaven følger. Endre her, ikke i oppgaven.

## Bakgrunn
- Carl-Andreas (carlan.skjong@gmail.com) planlegger julebord lørdag 12. desember: 8–9 personer, middag 19–21.
- Én gjest tåler ikke melk, egg, nøtter og sennep.
- Forespørsel («Forespørsel booking Julebord») ble sendt 28. okt til:
  - Cru (post@cru.no)
  - Kolonialen (post@kolonialenbislett.no)
  - Eik (eik@restauranteik.no)
  - Klosteret (bestilling@klosteret.no)
  - Vaaghals (post@vaaghals.com)
  - Arakataka (postarakataka@gmail.com)

## Absolutte regler
- Ikke send, svar på, videresend eller lag utkast til e-post. Ikke book noe.
- Bare les e-post, oppdater oversikten og skriv en oppsummering.

## Steg
1. **Finn kandidater.** Søk i Gmail med `subject:julebord newer_than:14d -in:sent -from:me`. Samle meldings-IDene til meldingene i trådene som ikke er sendt av Carl-Andreas. Hent hver tråd med get_thread (PLAIN_TEXT).
2. **Sjekk hva som er nytt.** Kjør `python3 -I verktoy/oppdater.py nye <ID> <ID> ...`.
   - Gir den ingen utskrift, finnes det ingenting nytt. Avslutt da med «Ingen nye svar» og ingenting annet. Ikke commit og ikke oppdater artefakten.
3. **Oppdater hver ny melding** med `python3 -I verktoy/oppdater.py sett "<Restaurant>" felt=verdi ...`.
   - Feltene er status, svar, meny, pris_pp, allergi, tid, rom, vilkar og neste.
   - status er Svart, Venter, Avslått eller Booket.
   - svar er svartidspunktet som ISO-tid med +01:00.
   - meny er kort, f.eks. «5 retter».
   - pris_pp er kr per person.
   - vilkar er én setning om kansellering, servicetillegg og regning.
   - neste er det restauranten venter svar på fra oss.
   - Er svaret et oppfølgingssvar i en tråd der Carl-Andreas har svart, oppdaterer du de feltene som er endret.
4. **Lagre menyvedlegg** (bilde eller PDF). Hent meldingen med get_message messageFormat RAW. Resultatet lagres som en fil. Kjør `python3 -I verktoy/oppdater.py vedlegg <fil> "<Restaurant>"`.
   **Uten vedlegg:** Når en restaurant har oppgitt meny eller pris, men ikke lagt ved menyen, henter du den fra nettsiden deres.
   - Bruk WebSearch eller WebFetch på restaurantens nettside. Finn lenken til selskaps-, gruppe- eller julemenyen (ofte en PDF) og les den med WebFetch.
   - Skallet kan vanligvis ikke laste ned fra restaurantsider, så legg menyen inn som tekst:
     `sett "<Restaurant>" "meny_tekst=Rett 1 (allergener)|Rett 2 (allergener)|..." "meny_lenke=https://<lenke til menyen>" "meny_kilde=Hentet fra <kilde> på <nettsted>. <evt. forbehold>"`
   - Skriv kort med egne ord. Ta med retten, hovedråvarene og allergenene, og bruk den menyen restauranten viste til.
   - Finner du ingen meny, setter du bare meny_lenke til menysiden deres.
   - Restauranter som allerede har meny_bilde eller meny_tekst, hoppes over.
5. **Merk som behandlet** med `python3 -I verktoy/oppdater.py marker <nye ID-er>`. Kjør deretter `python3 -I verktoy/oppdater.py valider`.
6. **Publiser.**
   - Commit med forfatter `Carl-Andreas Skjong <carlan.skjong@gmail.com>`. Avslutt commit-meldingen med linjen `Co-Authored-By: Claude <noreply@anthropic.com>`.
   - Push til main. GitHub Pages publiserer automatisk til https://carlanskjong.github.io/Julebord/.
   - Bekreft at bygget er ferdig med `gh api repos/carlanskjong/Julebord/actions/runs --jq '.workflow_runs[0] | [.status,.conclusion] | @tsv'`.
7. **Oppdater Claude-oversikten** (https://claude.ai/artifact/2JU67PddyPSLvVAHvfoiAb).
   - Kjør `python3 -I verktoy/oppdater.py artefakt <scratch>/svar.json`.
   - Last opp filen med Artifact publish (url = oversikten, file_path = svar.json, asset: true).
   - Hent `datasets/svar` med ArtifactData get. Oppdater den med if_version: `source = {kind:"file", url:"<ny /_blob/-url>", name:"svar.json"}` og `updated = {at:<nå>, by:"Claude"}`.
   - Ikke endre `files/index.html`.
8. **Oppsummer** på norsk, kort. Ta med:
   - hvem som har svart,
   - pris per person og om allergiene kan tilpasses,
   - ledig tid,
   - hva hver av dem venter på fra oss.
   Nevn også restauranter som ikke har svart på mer enn 2 døgn som «kan purres», men ikke purr selv.

## Når oppgaven skal slå seg av
Deaktiver den planlagte oppgaven med update_trigger enabled=false når én av disse er sann:
- Dagens dato er etter 12. desember 2026.
- Noen rad har status «Booket».
- Alle seks har svart, og det har ikke kommet nye svar på 3 døgn.
