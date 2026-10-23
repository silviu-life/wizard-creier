---
name: noteaza
description: Pune o informație nouă despre firmă în sertarul potrivit al creierului și o trece în decizii.md cu data; fără argument, se uită prin sesiunea curentă și propune ce merită notat. Folosește la /noteaza, „notează asta", „ține minte că", „am schimbat prețul", „am un client nou", „s-a schimbat ceva", „ce am aflat azi". Nu e pentru importuri mari (pentru asta e /creier-import + /creier-sorteaza).
---

# Notează în creier

Un creier care nu se actualizează se învechește. Treaba ta e ca fiecare lucru nou să ajungă într-un singur loc, cel corect, și să rămână urma lui: ce s-a schimbat și când.

## Cu argument — „/noteaza am crescut prețul la Standard la 700 lei"

1. Găsește sertarul potrivit. Citește harta din `CLAUDE.md` și caută informația veche în sertare.
2. **Dacă înlocuiește ceva**, îi arăți: „Acum scrie 650 lei, îl fac 700 lei?" Scrii doar după ce spune da.
3. Modifici sertarul. Schimbi doar rândul respectiv, nu rescrii fișierul.
4. Dacă informația apare și în alte sertare (n-ar trebui, dar se întâmplă), le corectezi și pe ele sau pui acolo trimitere spre sertarul principal.
5. Adaugi sus în `decizii.md`: `- AAAA-LL-ZZ — Pachetul Standard costă 700 lei (înainte: 650 lei).`
6. Confirmi într-un rând ce ai modificat și unde.

**Client nou:** creezi `clienti/<nume>.md`, cu ce știi și „de completat" unde nu știi.

**Nu se potrivește în niciun sertar:** propui un sertar nou și îl adaugi și în harta din `CLAUDE.md`, după ce spune da.

## Fără argument — „/noteaza"

1. Te uiți prin ce s-a vorbit în sesiunea curentă.
2. Scoți lucrurile noi despre firmă: prețuri, clienți, decizii, procese, răspunsuri bune la întrebări de client.
3. Le arăți ca listă scurtă și îl întrebi pe care le notezi (AskUserQuestion, selecție multiplă).
4. Pentru cele alese, faci pașii de mai sus.

## Nu face

- Nu notezi nimic fără confirmare când se înlocuiește o informație existentă.
- Nu notezi lucruri personale sau de o zi (ce a mâncat, o întâlnire anulată), decât dacă îți cere el.
- Nu ștergi istoria din `decizii.md`.
