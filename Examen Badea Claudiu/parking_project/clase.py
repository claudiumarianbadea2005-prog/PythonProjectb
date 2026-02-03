from datetime import datetime


class Vehicul:
    """
    Reprezintă un vehicul parcat.
    Păstrează:
      - numărul de înmatriculare
      - timestamp-ul (momentul intrării în parcare)
    """

    def __init__(self, nr_inmatriculare, timestamp=None):
        self.nr_inmatriculare = nr_inmatriculare.strip().upper()
        self.timestamp = timestamp or datetime.now()
# Dacă nu primim timestamp (vehicul nou parcat), folosim timpul curent

class SpatiuParcare:
    """
    Reprezintă un spațiu (un loc) de parcare.
    Păstrează:
      - numărul locului
      - vehiculul asociat (None dacă locul e liber)
    """

    def __init__(self, numar, vehicul=None):
        # Numărul locului (ex: 1..50)
        self.numar = numar

        # Vehiculul parcat pe loc (sau None dacă e liber)
        self.vehicul = vehicul

    def este_liber(self):
        """
        Verifică dacă locul este liber.
        Returnează True dacă nu există vehicul asociat.
        """
        return self.vehicul is None