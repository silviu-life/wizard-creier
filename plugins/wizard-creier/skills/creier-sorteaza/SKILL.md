---
name: creier-sorteaza
description: Transformă grămada din creier/00-brut/ în sertarele creierului (firma, ofertă și prețuri, clienți, voce, procese, întrebări frecvente, decizii), după regula „un lucru, un singur loc", și îl întreabă pe utilizator la fiecare contradicție. Folosește la /creier-sorteaza, „sortează-mi creierul", „pune ordine în ce am importat", „fă sertarele", „am adus fișiere noi în 00-brut". Rulează după /creier-import; se poate rula din nou când apar fișiere noi.
---

# Sortarea creierului

O grămadă de fișiere nu e încă un creier. Faci sertare, pui fiecare informație într-un singur loc și scoți la iveală contradicțiile. **Deciziile le ia utilizatorul, nu tu.**

Vorbești în română, simplu. Nu ștergi nimic din `00-brut/`.

## Pasul 1 — Citește grămada

- Dacă în folderul curent nu există `00-brut/`, te oprești. Îi spui să deschidă Claude Code în folderul creierului sau să ruleze întâi `/creier-import`.

- Citește tot din `00-brut/`, în afară de `_arhiva/`. La conversații, pornește de la `index.md`.
- Dacă sunt multe fișiere (peste 30 sau peste câteva sute de pagini), împarte-le pe surse și dă fiecare bucată unui sub-agent. Fiecare sub-agent întoarce fapte scurte, fiecare cu fișierul din care vine. Altfel citești tu.
- Dacă există deja sertare de la o sortare anterioară, citește-le întâi. Acum doar completezi, nu rescrii.

## Pasul 2 — Propune sertarele

Structura de pornire, adaptată la ce ai găsit:

| Sertar | Ce ține |
|---|---|
| `firma.md` | cine e, ce face, pentru cine, istoria pe scurt |
| `oferta-si-preturi.md` | servicii sau produse, prețuri, pachete, condiții |
| `clienti/<nume>.md` | câte o fișă pe client important: cine e, ce a cumpărat, ce vrea, cum vorbește |
| `voce.md` | cum scrie și vorbește firma |
| `procese/<nume>.md` | cum se face un lucru, pas cu pas |
| `intrebari-frecvente.md` | ce întreabă clienții și ce răspunde firma |
| `decizii.md` | ce s-a hotărât și când, cel mai recent sus |

Arată propunerea în câteva rânduri și cere-i aprobarea (AskUserQuestion: „Așa e bine" / „Vreau să schimb ceva"). Nu scrie nimic până nu aprobă.

## Pasul 3 — Umple sertarele

- **Un lucru, un singur loc.** Prețul stă doar în `oferta-si-preturi.md`. Fișa clientului scrie „vezi pachetul Standard din oferta-si-preturi.md", nu repetă prețul.
- Scrie scurt și concret, ca o fișă, nu ca o conversație.
- La finalul fiecărui sertar pui `## Surse`, cu fișierele din `00-brut/` din care ai luat informația.
- Nu inventa nimic. Dacă nu găsești un lucru, nu-l completezi din presupuneri.

## Pasul 4 — Contradicțiile

Când găsești același lucru cu valori diferite (trei prețuri pentru același serviciu, două adrese, condiții diferite):

1. Le aduni pe toate și le pui la final, nu una câte una în timp ce scrii.
2. Pentru fiecare contradicție îl întrebi (AskUserQuestion). Fiecare variantă arată valoarea, sursa și data: „500 lei — oferta-2024.pdf", „650 lei — conversația din martie 2026", plus opțiunea „Altă valoare".
3. Scrii în sertar doar valoarea aleasă.
4. Adaugi în `decizii.md`: `- AAAA-LL-ZZ — Prețul pachetului Standard e 650 lei (înainte apărea și 500 lei, în oferta-2024.pdf).`

## Pasul 5 — Raportul

Actualizează `inventar.md` cu o secțiune `## După sortare`. Ea spune ce sertare există, câte fișe de client sunt, ce contradicții s-au rezolvat și **ce lipsește** (de exemplu „nu știu condițiile de plată").

Spune-i rezumatul în 4–6 rânduri. Pasul următor: `/creier-reguli`.

## Nu face

- Nu șterge și nu muta nimic din `00-brut/`. E arhiva lui.
- Nu alege tu între două valori care se contrazic.
- Nu copia conversații întregi în sertare.
