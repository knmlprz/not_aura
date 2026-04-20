# Strategia branchowania

Spis treści

- [Strategia branchowania](#strategia-branchowania)
  - [Ogólne pojęcia](#ogólne-pojęcia)
  - [Główne branche](#główne-branche)
  - [Gałęzie pomocnicze](#gałęzie-pomocnicze)
  - [Gałęzie funkcji (feature branches)](#gałęzie-funkcji-feature-branches)
    - [Tworzenie gałęzi funkcji](#tworzenie-gałęzi-funkcji)
    - [Włączanie zakończonej funkcji do develop](#włączanie-zakończonej-funkcji-do-develop)
  - [Gałęzie wydań](#gałęzie-wydań)
    - [Tworzenie gałęzi wydania](#tworzenie-gałęzi-wydania)
    - [Zakończenie gałęzi wydania](#zakończenie-gałęzi-wydania)
  - [Gałęzie naprawy błędów](#gałęzie-naprawy-błędów)
    - [Tworzenie gałęzi naprawy błędów](#tworzenie-gałęzi-naprawy-błędów)
    - [Zakończenie gałęzi naprawy błędów](#zakończenie-gałęzi-naprawy-błędów)

## Ogólne pojęcia

System kontroli wersji `git` pozwala na śledzenie zmian w kodzie źródłowym, a tym samym zachowanie historii wersji kodu oraz umożliwia łączenie i wprowadzanie zmian wykonanych w różnym czasie. Ogólna konwencja opiera się na gałęziach (branch), które pozwalają na prowadzenie równoległych zmian, wprowadzanych w ramach komitów (commits). Ze względu na dowolność nazewnictwa gałęzi wprowadzane są podstawowe zasady pozwalające uporządkować zmiany w kodzie. Gałęzie te dzielimy na główne oraz pomocnicze.

## Główne branche

 Centralne repozytorium zawiera dwie główne gałęzie o nieskończonym czasie życia:

- `main`
- `develop`

Gałąź `main` (czasem też zwana `master`) w `origin` powinna być znana każdemu użytkownikowi Git. Równolegle do gałęzi `main` istnieje inna gałąź o nazwie `develop`. 

> NOTE: W przypadku rozwijania paczki dla więcej niż jednej wersji ROS2 wymagane jest aby powstały branche deweloperskie adekwatne do nazwy wykorzystywanej wersji: ROS2 humble -> `humble-dev` | ROS2 Iron -> `iron-dev`.

Uważamy `origin/main` za główną gałąź, gdzie kod źródłowy `HEAD` zawsze odzwierciedla stan gotowy do produkcji.

Z kolei `origin/develop` jest główną gałęzią, gdzie kod źródłowy `HEAD` zawsze odzwierciedla stan z najnowszymi zmianami rozwijanymi na następne wydanie. Niektórzy nazywają to "gałęzią integracyjną". Gałąź rozwojowa jest miejscem, z którego potencjalnie mogą być budowane automatyczne, nocne kompilacje.

Kiedy kod źródłowy w gałęzi `develop` osiąga stabilny punkt i jest gotowy do wydania, wszystkie zmiany powinny zostać scalone z powrotem do `main` i oznaczone numerem wydania. Jak dokładnie wygląda przebieg takiego scalenia omówimy dalej.

## Gałęzie pomocnicze

Obok głównych gałęzi `main` i `develop`, nasz model rozwoju używa różnych gałęzi pomocniczych, aby wspomóc równoległy rozwój między członkami zespołu, ułatwić śledzenie funkcji, przygotować wydania produkcyjne i pomóc w szybkim naprawianiu problemów z produkcją na żywo. W przeciwieństwie do głównych gałęzi, te gałęzie zawsze mają ograniczony czas życia, ponieważ ostatecznie zostaną usunięte.

Różne typy gałęzi, które możemy używać, to:

- Gałęzie funkcji (feature branches)
- Gałęzie wydań (release branches)
- Gałęzie naprawy błędów (hotfix branches)

Każda z tych gałęzi ma określone przeznaczenie i jest związana z surowymi zasadami dotyczącymi tego, które gałęzie mogą być ich gałęzią źródłową, a które gałęzie muszą być ich celami scalania. Przejdziemy przez nie za chwilę.

W żadnym wypadku te gałęzie nie są "specjalne" z technicznego punktu widzenia. Typy gałęzi są kategoryzowane przez to, jak z nich korzystamy. Są oczywiście zwykłymi starymi gałęziami Git.

## Gałęzie funkcji (feature branches)

Mogą odgałęziać się od:

- `develop`

Muszą być scalone z powrotem do:

- `develop`

Konwencja nazewnictwa gałęzi:

- `feat/name`, gdzie "name" to nazwa funkcjonalności.

Gałęzie funkcji (czasami nazywane gałęziami tematycznymi) są używane do rozwijania nowych funkcji na nadchodzące lub dalekie przyszłe wydanie. Kiedy zaczyna się rozwój funkcji, docelowe wydanie, w którym ta funkcja zostanie włączona, może być w tym momencie nieznane. Istotą gałęzi funkcji jest to, że istnieje tak długo, jak długo trwa rozwój funkcji, ale ostatecznie zostanie scalona z powrotem do `develop` (aby na pewno dodać nową funkcję do nadchodzącego wydania) lub odrzucona (w przypadku niesatysfakcjonującego rozwoju).

### Tworzenie gałęzi funkcji

Podczas rozpoczynania pracy nad nową funkcją, odgałęź się od gałęzi `develop`.

```shell
$ git checkout -b feat/name develop
# Przełączono na nową gałąź "feat/name"
```

### Włączanie zakończonej funkcji do develop

Zakończone funkcje mogą być scalane do gałęzi `develop`, aby na pewno dodać je do nadchodzącego wydania:

```shell
$ git checkout develop
# Switched to branch 'develop'
$ git merge --no-ff feat/name
# Updating ea1b82a..05e9557
# (Summary of changes)
$ git branch -d feat/name
# Deleted branch feat/name (was 05e9557).
$ git push origin develop
```

> **Uwaga:** Wymagana jest akceptacja danego scalenia funkcjonalności przez innego członka zespołu.

Flaga `--no-ff` powoduje, że scalanie zawsze tworzy nowy obiekt komit (commit), nawet jeśli scalanie mogło być wykonane za pomocą szybkiego przesunięcia (fast-forward). Unika to utraty informacji o historycznym istnieniu gałęzi funkcji i grupuje razem wszystkie komity, które razem dodały funkcję. Poniżej porównanie:

W drugim przypadku, z historii Git nie można zobaczyć, które z obiektów komit razem zaimplementowały funkcję - musiałbyś ręcznie czytać wszystkie komunikaty logów. Cofnięcie całej funkcji (tj. grupy komitów) jest prawdziwym bólem głowy w drugiej sytuacji, podczas gdy jest łatwe do zrobienia, jeśli użyto flagi `--no-ff`.

## Gałęzie wydań

Mogą odgałęziać się od:

- `develop`

Muszą być scalone z powrotem do:

- `develop` i `main`

Konwencja nazewnictwa gałęzi:

- `release/`*

Gałęzie wydań wspierają przygotowanie nowego wydania produkcyjnego. Pozwalają na ostatnią chwilę na dopięcie wszystkich szczegółów. Ponadto, pozwalają na drobne naprawy błędów i przygotowanie metadanych dla wydania (numer wersji, daty budowy, itp.). Wykonując całą tę pracę na gałęzi wydania, gałąź `develop` jest czyszczona, aby otrzymać funkcje dla następnego dużego wydania.

Kluczowym momentem do odgałęzienia nowej gałęzi wydania od `develop` jest moment, gdy `develop` (prawie) odzwierciedla pożądany stan nowego wydania. Przynajmniej wszystkie funkcje, które są kierowane na wydanie, które ma być zbudowane, muszą być scalone do `develop` w tym momencie.

Dokładnie na początku gałęzi wydania nadchodzące wydanie otrzymuje przypisany numer wersji - nie wcześniej. Do tego momentu, gałąź `develop` odzwierciedlała zmiany dla "następnego wydania", ale nie jest jasne, czy to "następne wydanie" ostatecznie stanie się 0.3 czy 1.0, dopóki nie zostanie rozpoczęta gałąź wydania. Ta decyzja jest podejmowana na początku gałęzi wydania i jest realizowana zgodnie z zasadami projektu dotyczącymi zwiększania numeru wersji.

### Tworzenie gałęzi wydania

Gałęzie wydań są tworzone z gałęzi `develop`. Na przykład, powiedzmy, że wersja 1.1.5 jest obecnym wydaniem produkcyjnym i mamy duże wydanie nadchodzące. Stan `develop` jest gotowy na "następne wydanie" i zdecydowaliśmy, że stanie się to wersją 1.2 (a nie 1.1.6 lub 2.0). Więc odgałęziamy i nadajemy gałęzi wydania nazwę odzwierciedlającą nowy numer wersji:

```shell
$ git checkout -b release/1.2 develop
# Switched to a new branch "release-1.2"
# Zmień numer wersji ręcznie w odpowiednich plikach (np. package.xml / setup.py)
$ git commit -a -m "Bumped version number to 1.2"
# [release/1.2 74d9424] Bumped version number to 1.2
# 1 files changed, 1 insertions(+), 1 deletions(-)
```

Po utworzeniu nowej gałęzi i przełączeniu na nią, podnosimy numer wersji ręcznie przez edycję odpowiednich plików, a następnie zatwierdzamy zmiany.

Ta nowa gałąź może istnieć tam przez jakiś czas, aż do momentu, gdy wydanie może być na pewno wdrożone. W tym czasie, naprawy błędów mogą być stosowane w tej gałęzi (a nie na gałęzi `develop`). Dodawanie tutaj dużych nowych funkcji jest surowo zabronione. Muszą one być scalone do `develop`, a więc czekać na następne duże wydanie.

### Zakończenie gałęzi wydania

Kiedy stan gałęzi wydania jest gotowy, aby stać się prawdziwym wydaniem, należy podjąć pewne działania. Po pierwsze, gałąź wydania jest scalana do `main` (ponieważ każdy komit na `main` to nowe wydanie z definicji, pamiętaj). Następnie, ten komit na `main` musi być oznaczony tagiem dla łatwego przyszłego odniesienia do tej historycznej wersji. Na koniec, zmiany dokonane na gałęzi wydania muszą być scalone z powrotem do `develop`, aby przyszłe wydania również zawierały te poprawki błędów.

```shell
$ git checkout main
# Switched to branch 'main'
$ git merge --no-ff release/1.2
# Merge made by recursive.
# (Summary of changes)
$ git tag -a 1.2
```

Wydanie jest teraz gotowe i oznaczone tagiem dla przyszłych odniesień.

> **Uwaga:** Możesz również chcieć użyć flag `-s` lub `-u`  do kryptograficznego podpisania twojego tagu.

Aby zachować zmiany dokonane na gałęzi wydania, musimy je scalić z powrotem do `develop`. W Git:

```shell
$ git checkout develop
# Switched to branch 'develop'
$ git merge --no-ff release/1.2
# Merge made by recursive.
# (Summary of changes)
```

Ten krok może prowadzić do konfliktu scalania (prawdopodobnie nawet, ponieważ zmieniliśmy numer wersji). Jeśli tak, napraw to i zatwierdź.

Teraz jesteśmy naprawdę gotowi i gałąź wydania może być usunięta, ponieważ już jej nie potrzebujemy:

```shell
$ git branch -d release/1.2
# Deleted branch release/1.2 (was ff452fe).
```

## Gałęzie naprawy błędów

Mogą odgałęziać się od:

- `main`

Muszą być scalone z powrotem do:

- `develop` i `main`

Konwencja nazewnictwa gałęzi:

- `hotfix/*`

Gałęzie naprawy błędów są bardzo podobne do gałęzi wydań, ponieważ również mają na celu przygotowanie nowego wydania produkcyjnego, choć nieplanowanego. Powstają z konieczności natychmiastowego działania w przypadku niepożądanego stanu działającej na żywo wersji produkcyjnej. Kiedy krytyczny błąd w wersji produkcyjnej musi być natychmiast rozwiązany, gałąź naprawy błędów może być odgałęziona od odpowiadającego tagu na gałęzi głównej, który oznacza wersję produkcyjną.

Istotą jest to, że praca członków zespołu (na gałęzi `develop`) może trwać, podczas gdy inna osoba przygotowuje szybką naprawę produkcji.

### Tworzenie gałęzi naprawy błędów

Gałęzie naprawy błędów są tworzone z gałęzi `main`. Na przykład, powiedzmy, że wersja 1.2 jest obecnym wydaniem produkcyjnym działającym na żywo i powodującym kłopoty z powodu poważnego błędu. Ale zmiany na `develop` są jeszcze niestabilne. Możemy wtedy odgałęzić gałąź naprawy błędów i zacząć naprawiać problem:

```shell
$ git checkout -b hotfix/name main
# Switched to a new branch "hotfix/name"
# Zmień numer wersji ręcznie w odpowiednich plikach (np. package.xml / setup.py)
$ git commit -a -m "Bumped version number to 1.2.1"
# [hotfix/name 41e61bb] Bumped version number to 1.2.1
# 1 files changed, 1 insertions(+), 1 deletions(-)
```

Nie zapomnij podnieść numeru wersji po odgałęzieniu!

Następnie napraw błąd i zatwierdź naprawę w jednym lub więcej oddzielnych komitach.

```shell
$ git commit -m "Fixed severe production problem"
# [hotfix/name abbe5d6] Fixed severe production problem
# 5 files changed, 32 insertions(+), 17 deletions(-)
```

### Zakończenie gałęzi naprawy błędów

Gdy naprawa jest gotowa, musi być scalona z powrotem do `main`, ale także musi być scalona z powrotem do `develop`, aby zapewnić, że naprawa błędu będzie zawarta także w następnym wydaniu. Jest to całkowicie podobne do tego, jak kończone są gałęzie wydań.

Najpierw zaktualizuj `main` i oznacz wydanie.

```shell
$ git checkout main
# Switched to branch 'main'
$ git merge --no-ff hotfix/name
# Merge made by recursive.
# (Summary of changes)
$ git tag -a 1.2.1
```

> **Uwaga:** Możesz również chcieć użyć flag `-s` lub `-u`  do kryptograficznego podpisania twojego tagu.

Następnie, uwzględnij naprawę błędu również w `develop`:

```shell
$ git checkout develop
# Switched to branch 'develop'
$ git merge --no-ff hotfix/name
# Merge made by recursive.
# (Summary of changes)
```

Jednym wyjątkiem od tej zasady jest to, że **kiedy istnieje obecnie gałąź wydania, zmiany naprawy błędów muszą być scalone do tej gałęzi wydania, a nie do** `develop`. Scalenie z powrotem naprawy błędów do gałęzi wydania ostatecznie spowoduje, że naprawa błędu zostanie scalona również do `develop`, gdy gałąź wydania zostanie zakończona. (Jeśli praca na `develop` natychmiast wymaga tej naprawy błędu i nie może czekać na zakończenie gałęzi wydania, możesz bezpiecznie scalić naprawę błędu do `develop` już teraz.)

Na koniec, usuń tymczasową gałąź:

```shell
$ git branch -d hotfix/name
# Deleted branch hotfix/name (was abbe5d6).
```

