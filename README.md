# wizard-creier

Plugin Claude Code pentru cursul **De la chat la sisteme AI**. Construiești **al doilea creier al firmei**: un folder pe calculatorul tău cu tot ce știe Claude despre business-ul tău, din care Claude Code lucrează ca un coleg care știe firma.

## Instalare

În Claude Code:

```
/plugin marketplace add silviu-life/wizard-creier
/plugin install wizard-creier@wizard-creier
```

Alegi **„Install for you (user scope)"**. Verificare: scrii `/creier` și vezi comenzile de mai jos.

**Actualizare:** `/plugin` → **Marketplaces** → wizard-creier → **„Update marketplace"**.

## Comenzile

| Comandă | Ce face |
|---|---|
| `/creier-import` | Aduce în `00-brut/` exportul din claude.ai (conversații, proiecte, memorie), ce ai lucrat în CoWork, textele copiate, foldere și ZIP-uri amestecate. |
| `/creier-sorteaza` | Pune totul în sertare, după regula „un lucru, un singur loc", și te întreabă la fiecare contradicție. |
| `/creier-reguli` | Scrie `CLAUDE.md`, harta și regulile casei, și `voce.md`, cum scrii tu. |
| `/noteaza` | Pune o informație nouă în sertarul potrivit și o trece în `decizii.md`. |
| `/procedura-noua` | Transformă un lucru pe care îl faci des într-o comandă proprie, de exemplu `/oferta`, care lucrează din creier. |
| `/blocat` | Explică o eroare pe înțeles și îți dă un singur pas următor. |
| `/creier-verifica` | Controlul lunar: ce lipsește, ce s-a învechit, ce se contrazice. |

Ordinea din curs: `/creier-import` → `/creier-sorteaza` → `/creier-reguli` → `/noteaza` → `/procedura-noua` → `/creier-verifica`. Porți Claude Code mereu în folderul creierului.

## Cerințe

- Claude Code
- Python 3.9 sau mai nou, doar pentru `/creier-import`. Dacă lipsește, skill-ul îți cere voie să-l instaleze.

## Verificarea scriptului de import

```
python plugins/wizard-creier/skills/creier-import/scripts/importa.py --test
```
