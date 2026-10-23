---
name: procedura-noua
description: Transformă un lucru pe care utilizatorul îl face des (o ofertă, răspunsul la un client, o postare, un rezumat de ședință) într-o procedură proprie — un skill nou în .claude/skills/ care folosește creierul — printr-un interviu scurt, apoi o testează pe loc. Folosește la /procedura-noua, „fă-mi o procedură", „vreau o comandă pentru oferte", „automatizează-mi lucrul ăsta", „creează un skill", „vreau /oferta".
---

# Procedură nouă

Creierul ține **ce** știe firma. Procedura ține **cum** face firma un lucru. Puse împreună, dau un coleg care face lucrul ăsta ca utilizatorul, de fiecare dată.

Vorbești în română, simplu. Nu-i ceri să scrie el skill-ul: îl scrii tu, din răspunsurile lui.

## Pasul 1 — Interviul

Pune-i întrebările pe rând. Propune tu un răspuns din ce știi din creier și lasă-l să corecteze.

1. **Ce lucru** vrei să faci așa? Dacă nu știe, îi propui două sau trei din `lista.md` sau din `procese/`.
2. **Ce primești** când începe lucrul ăsta: un email de la client, notițe, un nume, o cerere în două rânduri?
3. **Ce trebuie să iasă**: o ofertă, un email, o postare? În ce format: text în chat, fișier `.md`, document?
4. **Cum faci tu azi**, pas cu pas. Lasă-l să povestească, apoi îi rezumi pașii și îi confirmă.
5. **Un exemplu bun**: un rezultat real de care e mulțumit. Opțional, dar ajută mult.
6. **Ce n-are voie** procedura: să inventeze reduceri, să promită termene și altele.

## Pasul 2 — Scrie skill-ul

Numele e scurt, cu litere mici, fără diacritice, cu cratimă: `oferta`, `raspunde-client`, `postare`. Fișierul e `.claude/skills/<nume>/SKILL.md`:

```markdown
---
name: <nume>
description: <ce face, într-o frază> Folosește la /<nume>, „<2-4 feluri în care ar cere-o el>".
---

# <Titlu>

## Ce citești întâi
- `CLAUDE.md`
- <sertarele de care are nevoie, explicit: oferta-si-preturi.md, voce.md, clienti/<client>.md ...>

## Ce primești
<din întrebarea 2; dacă lipsește ceva esențial, întreabă>

## Pașii
<din întrebarea 4, numerotați>

## Ce iese
<formatul din întrebarea 3; dacă e cazul, unde se salvează>

## Verifică înainte să predai
- Fiecare preț, nume și condiție vine din creier, nu din presupuneri.
- Sună ca în voce.md.
- <interdicțiile din întrebarea 6>

## La final
Dacă ai aflat ceva nou (client nou, cerere nouă), propune /noteaza.
```

Dacă a dat un exemplu bun, îl pui în același folder, ca `exemplu.md`, și îl treci la „Ce citești întâi".

## Pasul 3 — Testul pe loc

1. Îi spui: „Gata. Hai s-o încercăm." Rulezi procedura pe un caz real sau pe unul din `00-brut/`.
2. Îl întrebi ce ar schimba la rezultat.
3. Ce spune se duce **în procedură**, nu doar în textul de acum: modifici `SKILL.md` și rulezi încă o dată.
4. Te oprești când spune că ar trimite rezultatul așa cum e.

Dacă `/<nume>` nu apare în listă, îi spui să închidă sesiunea și să o deschidă din nou.

## Nu face

- Nu pune prețuri, clienți sau alte date ale firmei în `SKILL.md`. Procedura le citește din creier, ca să rămână corecte când se schimbă.
- Nu face o procedură care trimite, publică sau plătește ceva fără să întrebe.
