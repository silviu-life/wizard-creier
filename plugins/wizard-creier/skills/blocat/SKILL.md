---
name: blocat
description: Ajutor când utilizatorul s-a blocat — citește eroarea sau ce vede pe ecran, explică pe înțeles ce s-a întâmplat și dă un singur pas următor. Folosește la /blocat, „nu merge", „am o eroare", „m-am blocat", „nu înțeleg ce scrie", „nu apare", „ce fac acum", „s-a stricat", „help".
---

# M-am blocat

Utilizatorul nu e tehnic și urmărește un curs înregistrat, deci nu are pe cine să întrebe. Treaba ta: liniștește-l, înțelege, **un singur pas**, apoi aștepți să-ți spună ce a ieșit.

## Pasul 1 — Ce s-a întâmplat

Dacă nu ți-a spus deja, îl întrebi:
- ce încerca să facă (la ce lecție e, ce comandă a dat);
- ce a apărut. Îi ceri să copieze textul erorii sau să facă o poză a ecranului și să o tragă în fereastră.

Citește eroarea întreagă. De cele mai multe ori, răspunsul e scris chiar în ea.

## Pasul 2 — Explică într-o frază

Spune ce înseamnă, fără termeni tehnici: „Claude nu găsește fișierul pentru că e în alt folder decât cel în care lucrăm." Nu-i spune că a greșit el.

## Pasul 3 — Un singur pas

Dă **un** pas, cel mai mic, apoi aștepți. Dacă pasul e o comandă pe care o poți rula tu, ceri voie și o rulezi tu.

Cazuri frecvente:

| Ce vede | Ce înseamnă | Pasul |
|---|---|---|
| `You've hit your session limit · resets …` | s-a consumat limita pe intervalul ăsta | lasă sesiunea deschisă; după ora scrisă, scrie „continuă" |
| Claude nu vede un fișier | fișierul e în afara folderului `creier/` | trage fișierul în fereastră sau copiază-l în `00-brut/` |
| `/creier-import` sau altă comandă a cursului nu apare | pluginul nu e instalat sau nu s-a încărcat | scrie `/reload-plugins`; dacă tot nu apare, `/plugin` și verifici că `wizard-creier` e instalat |
| O procedură făcută de tine (`/oferta`) nu apare | skill-ul nou nu s-a încărcat încă | închide sesiunea și deschide-o din nou în folderul `creier/` |
| `python` nu e recunoscut | Python nu e instalat | rulează `/creier-import` din nou; te întreabă dacă îl instalează |
| Claude nu vede Gmail sau Drive | conectorul nu e legat de contul tău | în claude.ai, la Settings → Connectors, conectezi Gmail sau Drive, apoi deschizi o sesiune nouă |
| Claude întreabă dacă are voie să facă ceva | cere permisiune | citește ce vrea să facă; dacă e în folderul `creier/` și are legătură cu lecția, alegi Yes |
| Claude a făcut altceva decât ai vrut | cererea a fost înțeleasă altfel | spune-i exact ce vrei, în cuvintele tale, și ce să nu facă |

Dacă nu recunoști eroarea, o cauți pe internet (WebSearch) înainte să ghicești. Spune-i ce ai găsit.

## Pasul 4 — A mers?

Îl întrebi ce a ieșit. Dacă merge, îi spui unde rămăsese în lecție. Dacă nu, treci la pasul următor, tot unul singur.

După trei pași fără rezultat, îi spui cinstit: „Nu reușesc de aici." Îi faci un rezumat scurt pe care să-l trimită în comunitatea cursului: ce încerca, ce eroare a apărut, ce ați încercat deja.

## Nu face

- Nu șterge fișiere și nu rula comenzi care schimbă lucruri în afara folderului `creier/` fără să explici și să ceri voie.
- Nu-i cere parole, chei API sau coduri de card în chat.
- Nu da cinci soluții deodată.
