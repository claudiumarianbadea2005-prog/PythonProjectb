import sqlite3
from datetime import datetime

from clase import Vehicul, SpatiuParcare


class Parcare:
    def __init__(self, nr_locuri=50, pret_ora=10, db_name="parcare.db"):
        # Câte locuri + preț pe oră
        self.nr_locuri = nr_locuri
        self.pret_ora = pret_ora

        # Locuri în memorie (1..50)
        self.locuri = {i: SpatiuParcare(i) for i in range(1, nr_locuri + 1)}

        self.conn = None
        self.db_name = db_name

        # Pregătim DB + încărcăm ocuparea curentă
        self.db_init()
        self.incarca_din_baza()

    def db_init(self):
        # Conectare DB + creare tabele
        self.conn = sqlite3.connect(self.db_name)
        cur = self.conn.cursor()

        # ocupare = starea curentă (un vehicul pe un loc + când a intrat acestaa)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS ocupare (
                loc INTEGER PRIMARY KEY,
                nr TEXT UNIQUE NOT NULL,
                intrare_ts TEXT NOT NULL
            )
        """)

        # istoric = toate intrările/ieșirile + ore + sumă (pt calculul final)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS istoric (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nr TEXT NOT NULL,
                loc INTEGER NOT NULL,
                intrare_ts TEXT NOT NULL,
                iesire_ts TEXT,
                ore INTEGER,
                suma REAL
            )
        """)

        self.conn.commit()

    def incarca_din_baza(self):
        # Reface ocuparea curentă în memorie din tabelul ocupare (in functie de ce se intampla)
        cur = self.conn.cursor()
        rows = cur.execute("SELECT loc, nr, intrare_ts FROM ocupare").fetchall()

        for loc, nr, intrare_ts in rows:
            if loc in self.locuri:
                ts = datetime.strptime(intrare_ts, "%Y-%m-%d %H:%M:%S")
                self.locuri[loc].vehicul = Vehicul(nr, ts)

    def _calc_taxa(self, vehicul: Vehicul):
        # Calculează orele + taxa (minim 1 oră)
        durata = datetime.now() - vehicul.timestamp
        ore = max(1, int(durata.total_seconds() // 3600))
        taxa = ore * self.pret_ora
        return ore, taxa

    def _vehicul_deja_parcat(self, nr):
        # Verifică dacă nr-ul există deja în parcare
        for sp in self.locuri.values():
            if sp.vehicul and sp.vehicul.nr_inmatriculare == nr:
                return True
        return False

    def parcare_vehicul(self, nr_inmatriculare, loc):
        # Parchează un vehicul la un loc (dacă acesta este liber)
        nr = nr_inmatriculare.strip().upper()

        if loc not in self.locuri:
            print("Loc invalid.")
            return

        if not self.locuri[loc].este_liber():
            print("Locul este ocupat.")
            return

        if self._vehicul_deja_parcat(nr):
            print("Vehiculul este deja parcat.")
            return

        veh = Vehicul(nr)
        self.locuri[loc].vehicul = veh

        intrare_ts = veh.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        cur = self.conn.cursor()

        # salvăm ocuparea curentă
        cur.execute("INSERT INTO ocupare (loc, nr, intrare_ts) VALUES (?, ?, ?)", (loc, nr, intrare_ts))

        # salvăm în istoric doar intrarea (ieșirea se completează la plecarea vehiculului)
        cur.execute("INSERT INTO istoric (nr, loc, intrare_ts) VALUES (?, ?, ?)", (nr, loc, intrare_ts))

        self.conn.commit()
        print(f"OK: {nr} parcat la locul {loc}. Pret: {self.pret_ora} Lei/ora.")

    def plecare_vehicul(self, nr_inmatriculare):
        # Scoate un vehicul din parcare + calculează taxa + istoric
        nr = nr_inmatriculare.strip().upper()

        for loc, sp in self.locuri.items():
            if sp.vehicul and sp.vehicul.nr_inmatriculare == nr:
                ore, taxa = self._calc_taxa(sp.vehicul)

                # eliberăm locul în memorie
                sp.vehicul = None

                cur = self.conn.cursor()

                # ștergem din ocupare (starea curentă)
                cur.execute("DELETE FROM ocupare WHERE nr = ?", (nr,))

                # completăm ieșirea în istoric (ultima intrare fără ieșire)
                iesire_ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                cur.execute("""
                    UPDATE istoric
                    SET iesire_ts = ?, ore = ?, suma = ?
                    WHERE id = (
                        SELECT id FROM istoric
                        WHERE nr = ? AND iesire_ts IS NULL
                        ORDER BY id DESC
                        LIMIT 1
                    )
                """, (iesire_ts, ore, taxa, nr))

                self.conn.commit()
                print(f"OK: {nr} a plecat de la locul {loc}. Ore: {ore}, Taxa: {taxa} Lei.")
                return

        print("Vehiculul nu a fost gasit.")

    def status(self):
        # Afișează toate locurile (liber / ocupat + taxa)
        for loc in range(1, self.nr_locuri + 1):
            sp = self.locuri[loc]
            if sp.este_liber():
                print(f"Loc {loc}: Liber")
            else:
                ore, taxa = self._calc_taxa(sp.vehicul)
                print(f"Loc {loc}: {sp.vehicul.nr_inmatriculare} (ore: {ore}, taxa: {taxa} Lei)")

    def ocupare(self):
        # Câte locuri sunt ocupate / libere
        ocupate = sum(1 for sp in self.locuri.values() if not sp.este_liber())
        libere = self.nr_locuri - ocupate
        print(f"Ocupate: {ocupate} | Libere: {libere} | Total: {self.nr_locuri}")

    def raport_azi(self):
        # Încasări azi + câte ieșiri azi
        azi = datetime.now().strftime("%Y-%m-%d")
        cur = self.conn.cursor()

        total = cur.execute("""
            SELECT COALESCE(SUM(suma), 0)
            FROM istoric
            WHERE iesire_ts IS NOT NULL
              AND substr(iesire_ts, 1, 10) = ?
        """, (azi,)).fetchone()[0]

        iesiri = cur.execute("""
            SELECT COUNT(*)
            FROM istoric
            WHERE iesire_ts IS NOT NULL
              AND substr(iesire_ts, 1, 10) = ?
        """, (azi,)).fetchone()[0]

        print(f"RAPORT AZI ({azi}) -> Iesiri: {iesiri}, Incasari: {total} Lei")

    def inchide(self):
        # Închidem conexiunea DB cand se termina programul
        if self.conn:
            self.conn.close()