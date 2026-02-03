# ParkingProject 🚗🅿️

ParkingProject este o aplicație în consolă care gestionează o parcare cu locuri numerotate, unde poți parca vehicule, scoate vehicule, vedea statusul parcării și genera un raport cu încasările de azi. Datele se salvează într-o bază de date SQLite, ca să nu se piardă la închidere.

## Ce face aplicația
- Parcarea are **N locuri** (ex: 50), numerotate de la `1` la `N`
- Un loc poate avea **doar un vehicul**
- Fiecare vehicul are număr de înmatriculare + ora intrării
- La plecare se calculează automat **orele** și **taxa** (`ore * pret_ora`)
- Totul se salvează în SQLite (fișierul `parcare.db`)

## Comenzi disponibile
**1) Parchează vehicul**
- Cere număr de înmatriculare și un loc (1-N)
- Verifică dacă locul există și este liber
- Verifică dacă vehiculul nu e deja parcat
- Dacă e ok: parchează vehiculul și salvează în baza de date

**2) Plecare vehicul**
- Cere numărul de înmatriculare
- Caută vehiculul în parcare
- Dacă îl găsește:
  - calculează durata (minim 1 oră)
  - calculează taxa (ore * pret_ora)
  - eliberează locul
  - salvează plecarea în istoricul din baza de date

**3) Status parcare**
- Afișează toate locurile:
  - `Liber` dacă locul e gol
  - `Ocupat` + număr + ore + taxa curentă dacă e ocupat

**4) Raport azi (încasări)**
- Afișează pentru ziua curentă:
  - câte vehicule au plecat azi
  - totalul încasărilor de azi

**0) Ieșire**
- Închide conexiunea la baza de date și oprește aplicația

## Cum rulezi
Rulează fișierul `main.py`:
```bash
python main.py