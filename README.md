# wizard-creier

Plugin Claude Code pentru cursul **De la chat la sisteme AI**. Construiești **al doilea creier**: un folder pe calculatorul tău cu ce ai decis că e adevărat despre tine și munca ta, din care Claude Code lucrează ca un coleg care te cunoaște. Când lucrezi în folderul ăsta, nu mai explici de la zero.

## Instalare

În Claude Code:

```
/plugin marketplace add silviu-life/wizard-creier
/plugin install wizard-creier@wizard-creier
```

Alegi **„Install for you (user scope)"**. Verificare: scrii `/creier` în terminal și derulezi prin listă sau scrii `/creier-import` direct. Aplicația Desktop are propria listă de pluginuri.

**Actualizare:** `/plugin` → **Marketplaces** → wizard-creier → **„Update marketplace"**. Actualizarea automată e oprită implicit la pluginurile de acest fel.

## Comenzile

| Comandă | Ce face |
|---|---|
| `/creier-import` | Aduce în `00-brut/` exporturile din claude.ai și ChatGPT, ce știu alte AI-uri, ce ai lucrat în CoWork, textele copiate, foldere și ZIP-uri amestecate. |
| `/creier-sorteaza` | Pune totul în sertare, după regula „un lucru, un singur loc", și te întreabă la fiecare contradicție și la fiecare gol. |
| `/creier-reguli` | Scrie `CLAUDE.md`, harta și regulile casei, și `voce.md`, cum scrii tu. |
| `/noteaza` | Pune o informație nouă în sertarul potrivit și o trece în `decizii.md`. |
| `/procedura-noua` | Transformă un lucru pe care îl faci des într-o comandă proprie, de exemplu `/oferta`, care lucrează din creier. |
| `/blocat` | Explică o eroare pe înțeles și îți dă un singur pas următor. |
| `/creier-verifica` | Controlul lunar: ce lipsește, ce s-a învechit, ce se contrazice, plus verificarea listei tale. |

Ordinea din curs: `/creier-import` → `/creier-sorteaza` → `/creier-reguli` → `/noteaza` → `/procedura-noua` → `/creier-verifica`. Porți Claude Code mereu în folderul creierului. Dacă `/blocat` nu apare (plugin neinstalat) sau ai atins limita de utilizare, vezi lecția 3 a cursului.

## Cerințe

- Claude Code
- Python 3.9 sau mai nou, doar pentru `/creier-import`. Dacă lipsește, skill-ul îți cere voie să-l instaleze.
- Git, pentru instalarea pluginului din marketplace.

Formate: conversiile complete sunt pentru exporturile claude.ai și ChatGPT. Word, Excel și PowerPoint moderne primesc o copie text. Formatele vechi (`.doc`, `.xls`) și PDF-urile scanate se raportează ca necitite.

## Verificarea scriptului de import

```
python plugins/wizard-creier/skills/creier-import/scripts/importa.py --test
```
