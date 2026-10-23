---
name: creier-reguli
description: Scrie CLAUDE.md — ușa de intrare a creierului: cine e utilizatorul, unde se află fiecare lucru, cum se lucrează și ce nu se face niciodată — și voce.md din texte reale ale lui. Folosește la /creier-reguli, „fă-mi CLAUDE.md", „scrie regulile casei", „vreau să-mi scrie ca mine", „învață-mi vocea". Rulează după /creier-sorteaza.
---

# Regulile casei

`CLAUDE.md` e primul lucru pe care Claude Code îl citește la fiecare pornire în folderul ăsta. Dacă e scurt și clar, creierul răspunde corect din prima. Dacă e lung, se pierde.

Vorbești în română, simplu.

## Pasul 1 — Ce știi deja

Citește `firma.md`, `inventar.md` și lista sertarelor. Nu-l întreba lucruri pe care le ai deja scrise. Le propui tu și el doar confirmă.

## Pasul 2 — Interviul

Pune-i întrebările pe rând (AskUserQuestion acolo unde ai variante, text liber unde nu):

1. Cine ești și ce face firma, în două fraze. Propui tu varianta din `firma.md`, el o corectează.
2. Cum vorbești cu clienții: „tu" sau „dumneavoastră", cât de formal.
3. În ce limbă se scrie de obicei.
4. Ce faci tu când lipsește o informație. Variante: „Întreabă-mă" (recomandat) / „Spune că nu știi" / „Pune un loc gol de completat".
5. Ce n-are voie să facă niciodată, de exemplu să trimită emailuri fără să întrebe sau să promită termene. Propui trei exemple, el alege și adaugă.
6. Cum îi place să primească răspunsurile: scurt sau detaliat, cu liste sau în paragrafe.

## Pasul 3 — `CLAUDE.md`

Scrie `CLAUDE.md` în rădăcina creierului, **maximum 60 de rânduri**, cu secțiunile:

- **Cine sunt**: 2–3 rânduri.
- **Harta creierului**: fiecare sertar, cu un rând despre ce e în el și când îl citești. Ex: „Oferte și orice întrebare de preț → `oferta-si-preturi.md`. Nu folosi alt preț decât cel de acolo."
- **Cum lucrăm**: ton, limbă, format.
- **Niciodată**: interdicțiile lui.
- **Când nu știi**: regula din întrebarea 4 și „nu inventa prețuri, date, nume sau cifre".
- **De unde știi**: când răspunzi din creier, poți spune din ce fișier ai luat informația, mai ales dacă te întreabă.
- **La final de sesiune**: dacă ai aflat ceva nou despre firmă, propune `/noteaza`.

Dacă `CLAUDE.md` există deja, îi arăți ce schimbi și îi ceri acordul înainte să scrii.

## Pasul 4 — `voce.md`

Îi ceri 3–5 texte scrise chiar de el: emailuri către clienți, postări, o ofertă. Le poate lipi în chat sau îți arată fișiere din `00-brut/`. Din ele scrii în `voce.md`:

- tonul, în 2–3 cuvinte, cu un exemplu;
- lungimea obișnuită a frazelor și a mesajelor;
- expresiile pe care le folosește des;
- ce nu folosește niciodată;
- cum începe și cum încheie un mesaj;
- un exemplu scurt, „așa sună", scris de tine în vocea lui. Îl întrebi dacă sună ca el și corectezi până spune da.

## Pasul 5 — Testul

Îi propui să închidă sesiunea, să deschidă una nouă și să pună o întrebare de pe lista lui (`lista.md`), fără să-ți dea alt context. Apoi să te întrebe „de unde știi?".

## Nu face

- Nu pune în `CLAUDE.md` conținutul sertarelor (prețuri, clienți). `CLAUDE.md` arată doar unde se află.
- Nu trece de 60 de rânduri.
