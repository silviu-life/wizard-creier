---
name: creier-import
description: Aduce în creier/00-brut/ tot ce știe Claude despre utilizator — exportul din claude.ai (conversații, proiecte, memorie), ce a lucrat în CoWork, instrucțiuni copiate, documentele firmei, foldere și ZIP-uri amestecate — și le face lizibile. Folosește la /creier-import, „importă-mi conversațiile", „mută ce am în chat", „adu ce am în CoWork", „am exportul de la Claude", „am un folder cu fișiere pentru creier". Nu sortează în sertare (pentru asta e /creier-sorteaza).
---

# Importul în creier

Scopul: tot contextul utilizatorului, risipit în chat, CoWork și documente, ajunge într-un singur loc, `00-brut/`, în fișiere pe care le poate citi. Nu sortezi nimic aici. Nu modifici niciodată originalele utilizatorului.

Vorbești în română, simplu, fără jargon. Un pas o dată.

Fișierele acestui skill (scriptul, textul pentru `00-brut/`) sunt în `${CLAUDE_SKILL_DIR}`. Folderul utilizatorului e altul, cel în care e deschis Claude Code.

## Pasul 0 — Unde stă creierul

Dacă în folderul curent există deja `00-brut/`, ăsta e creierul și treci la pasul 1.

Dacă nu există, îl întrebi (AskUserQuestion):
- **„Aici, în folderul ăsta"**, dacă folderul e gol sau se numește `creier`
- **„Un folder nou `creier` în Documente"** (recomandat)

Creezi `00-brut/` și copiezi în el `${CLAUDE_SKILL_DIR}/CITESTE-00-brut.md` cu numele `CITESTE.md`. Dacă ai creat un folder nou, îi spui să deschidă Claude Code în el și să ruleze din nou `/creier-import`. Toate celelalte skill-uri ale creierului lucrează în folderul în care e deschis Claude Code.

## Pasul 1 — Ce aduce

Întreabă (AskUserQuestion, selecție multiplă): „Ce vrei să aduci în creier?"
- **Exportul din claude.ai** — conversațiile, Proiectele și memoria, într-un ZIP
- **Ce ai lucrat în CoWork** — folderele pe care i le-ai dat și fișierele pe care ți le-a făcut
- **Instrucțiuni scrise de tine** — din Proiectele claude.ai, din CoWork, din setări
- **Documentele firmei** — oferte, prețuri, prezentări, textul de pe site, un folder sau ZIP cu de toate

Pentru fiecare ales, explică pe scurt de unde îl ia:

- **Exportul claude.ai:** în claude.ai, Settings → Privacy → Export data. Primește pe email un link și descarcă un ZIP. Durează de la câteva minute la câteva ore. Dacă meniul arată altfel, îl ajuți să-l găsească, nu inventezi pași.
- **CoWork:** nu are un singur buton de export. Ce a făcut CoWork stă în folderele pe care utilizatorul i le-a dat. Îl întrebi care sunt acele foldere. Instrucțiunile pe care le-a scris în CoWork le copiază și ți le lipește în chat.
- **Instrucțiunile și memoria:** le copiază din setări și ți le lipește în chat.
- **Documentele:** orice format. Poate da un folder întreg, cu ZIP-uri înăuntru.

Ca să-ți dea o cale, îi spui: „Trage folderul sau fișierul în fereastra asta" sau „lipește calea aici".

## Pasul 2 — Copierea

Pentru tot ce are cale (ZIP-uri, foldere, fișiere), rulezi scriptul o singură dată, cu toate căile:

```
python "${CLAUDE_SKILL_DIR}/scripts/importa.py" 00-brut "<cale 1>" "<cale 2>" ...
```

- Pe Windows, dacă `python` nu există, încerci `py -3`, apoi `python3`. Dacă nu există deloc Python, îi explici că e un program mic de care ai nevoie o dată și îi ceri voie să-l instalezi (`winget install Python.Python.3.12` pe Windows, `brew install python` pe Mac). Dacă refuză, faci aceeași conversie cu ce e disponibil, citind `conversations.json` pe bucăți.
- Scriptul copiază, dezarhivează ZIP-urile, iar orice export claude.ai îl transformă în `conversatii/*.md`, `proiecte/<nume>/` și `memorie.md`, plus un `index.md`. Originalele rămân neatinse.
- Citește ce a afișat scriptul. Dacă scrie `LIPSEȘTE`, `REFUZAT` sau `ATENȚIE`, îi spui utilizatorului pe înțeles ce s-a întâmplat.

Textul lipit în chat (instrucțiuni, memorie) îl scrii tu în `00-brut/lipite/<de-unde>.md`, de exemplu `proiect-firma-instructiuni.md` sau `cowork-instructiuni.md`. Pe prima linie scrii de unde vine.

## Pasul 3 — Ce păstrăm din conversații

Un export are de obicei sute de conversații. Majoritatea nu țin de firmă: rețete, teme, întrebări de o zi.

1. Citește `index.md` (titluri și date), nu conversațiile întregi.
2. Grupează titlurile pe teme și propune care țin de business.
3. Întreabă-l ce grupuri păstrează.
4. Mută restul în `00-brut/_arhiva/`. Nu șterge nimic. `/creier-sorteaza` ignoră `_arhiva/`.

## Pasul 4 — Lista din lecția 1

Întreabă-l dacă are lista „ce îi explic iar și iar". Dacă da, scrie-o în `lista.md`, în rădăcina creierului, ca `- [ ] <punct>`. Dacă nu o are, mergi mai departe.

## Pasul 5 — Raportul

Scrie sau actualizează `inventar.md`: ce sursă a venit, câte conversații, ce proiecte, ce documente, ce pare să lipsească (de exemplu „n-am văzut nicăieri prețuri"). Spune-i rezumatul în 4–6 rânduri și pasul următor: `/creier-sorteaza`.

## Nu face

- Nu sorta și nu rescrie conținutul. Aici doar aduci.
- Nu șterge și nu muta fișierele utilizatorului din afara `creier/`.
- Nu deschide conversațiile una câte una, decât dacă te roagă el.
