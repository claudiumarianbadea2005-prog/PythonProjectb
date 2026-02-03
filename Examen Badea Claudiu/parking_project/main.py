from parcare import Parcare


def afiseaza_meniu():
    print("\n=== MENIU PARCARE ===")
    print("1) Parcheaza vehicul")
    print("2) Plecare vehicul")
    print("3) Status parcare")
    print("4) Raport azi (incasari)")
    print("0) Iesire")


def main():
    parcare = Parcare(nr_locuri=50, pret_ora=10)

    while True:
        afiseaza_meniu()
        opt = input("Alege: ").strip()

        if opt == "1":
            nr = input("Numar inmatriculare: ")
            # validare: minim 6 caractere (dupa ce scoatem spatiile de la inceput/sfarsit)
            if len(nr.strip()) < 6:
                print("Numarul de inmatriculare trebuie sa aiba minim 6 caractere.")
                continue

            try:
                loc = int(input("Loc (1-50): "))
            except ValueError:
                print("Loc invalid (nu e numar).")
                continue

            parcare.parcare_vehicul(nr, loc)

        elif opt == "2":
            nr = input("Numar inmatriculare: ")
            # validare: minim 6 caractere
            if len(nr.strip()) < 6:
                print("Numarul de inmatriculare trebuie sa aiba minim 6 caractere.")
                continue

            parcare.plecare_vehicul(nr)

        elif opt == "3":
            parcare.status()

        elif opt == "4":
            parcare.raport_azi()

        elif opt == "0":
            parcare.inchide()
            print("La revedere!")
            break

        else:
            print("Optiune invalida.")


if __name__ == "__main__":
    main()