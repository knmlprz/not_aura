# Strategia CodeReview

Spis treści

- [Strategia CodeReview](#strategia-codereview)
  - [Code Review](#code-review)
  - [Merge request](#merge-request)



## Code Review

Metoda oceny stworzonego kodu w celu identyfikacji błędów oraz poprawy jakości kodu. W przypadku prac projektowych weryfikacja kodu będzie przebiegać pod względem:

- **nazewnictwa**
  - zrozumiałe nazwy,
  - w języku angielskim,
  - adekwatne do zmiennej/metody,
- **komentarzy**
  - przydatne i potrzebne komentarze,
  - weryfikować czy ich nie brakuje,
- **funkcjonalności i złożoności**
  - sprawdzenie pod względem szybkich poprawek - recenzent ma pomysł jak to zrobić prościej to o tym pisze,
  - sprawdzanie obiektowość kodu i jego czytelności,
- **stylu**
  - dodawany kod w języku python formatowany z wykorzystaniem black,
  - kod napisany zgodnie z zasadami zawartymi w pliku [Styl kodu](../code/code_style.md)
- **testów**
  - wykonanie instrukcji instalacyjnej z zawartej w `README` danej paczki - pod względem kompilacji i uruchomienia,
- **dokumentacji**
  - aktualne `README` - opisane kolejne punkty według template'u,
  - aktualny przepływ sygnałów,
  - *aktualna dokumentacja w Doxygen lub doc string.*

Szczegóły procesu Code Review i Merge Request są opisane w tym dokumencie.

## Merge request

1. Będzie wykonywany obowiązkowo:
  - przy mergowaniu do developa - wersja działająca lokalnie na komputerze,
  - przy mergowaniu do mastera - wersja po wykonaniu testów na docelowym urządzeniu.
2. Powinien zawierać zmiany, które są fizycznie możliwe do sprawdzenia przez recenzenta (bez zmienionych miliona linii kodu).
3. Do każdego merge requesta będzie przypisany przynajmniej 1 recenzent, z czego recenzent nie może być autorem kodu.
4. Merge request będzie mergowany po wprowadzeniu niezbędnych zmian przez autora i uzyskaniu przynajmniej jednej akceptacji.
5. Tytuł MR powinien składać się z informacji o głównej wprowadzanej zmianie (zwykle nazwa brancha) oraz z identyfikatorem zadania, którego dotyczy, np. `Feature add logging [TASK-ID]`.