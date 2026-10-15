# Instrukcje repo dla Claude (FlowerSite-staging)

Poligon testowy strony Flower. Tu stoi nowy sklep, zanim trafi na oficjalną stronę.

| Repo | Widoczność | Rola |
| --- | --- | --- |
| `GRKarol/FlowerSite-staging` (to repo) | publiczne, `noindex` | podgląd sklepu, testy, poprawki |
| `GRKarol/FlowerSite.github.io` | publiczne | oficjalna strona (flower.theworkpc.com, później readwithflower.com) |

Zasady, tak samo jak w `czytnik01`:

- Cała bieżąca praca idzie tutaj, na `staging`.
- Na oficjalne repo nic nie trafia bez wyraźnego „wypchnij na oficjalną stronę” od Karola.
- W tym repo nie ma pliku `CNAME`. Gdyby się pojawił, GitHub zabrałby domenę oficjalnej stronie.

Sklep to jeden plik `index.html`. Lista zdjęć do zrobienia: `zdjecia.html`. Podstrony: `#kup`, `#specyfikacja`, `#pytania`, `#historia`, `#dostawa`, `#zwroty`, `#regulamin`, `#prywatnosc`, `#bezpieczenstwo`, `#dziekujemy`. Płatności (Stripe) nie są jeszcze podpięte.
