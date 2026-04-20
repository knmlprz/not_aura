# Praca z gitem

Spis treści

- [Praca z gitem](#praca-z-gitem)
  - [Wprowadzenie](#wprowadzenie)
  - [Istotne narzędzia](#istotne-narzędzia)
    - [Submodules](#submodules)
    - [LFS](#lfs)
  - [Zasady](#zasady)

## Wprowadzenie

Ze względu na ujednolicenie pracy ustalone zostały zasady dotyczące tworzenia gałęzi, których teoria została opisana w [Strategii branchowania](branching_strategy.md), a także [Pisania komitów](commits.md), które opisują ogólną koncepcję pracy z `git`.

## Istotne narzędzia

W ramach pracy z gitem warto wspomnieć o narzędziach, które oferuje git i są zaimplementowane w realizowanych projektach. Na te narzędzia składają się `submodules` oraz `git lfs`.

### Submodules

Submoduły umożliwiają tworzenie odnośnika do innego repozytorium git w tworzonym repozytorium. Funkcjonalność ta jest przydatna przy tworzeniu projektu, który składa się z innych podprojektów lub modułów. Przy dodawaniu submodułu jest tworzony plik `.gitmodules`, w którym zawarte są najważniejsze informacje o submodułach, ich lokalizacji oraz odnośnikach do gałęzi. Warto pamiętać, żeby w przypadku klonowania projektów zawierających submoduły korzystać z flagi `--recurse-submodules`.

Dodanie submodułu w projekcie

```bash
git submodule add git@example.com:group/repository.git
```

istnieje możliwość dodania flagi `--branch`, która umożliwia dodawanie submodułu na odpowiedniej gałęzi,

```bash
git submodule add git@example.com:group/repository.git --branch develop
```

oraz dodanie submodułu ze ścieżką docelową, do której ma zostać zaciągnięty moduł

```bash
git submodule add git@example.com:group/repository.git /path/to/clone
```

Podobnie jak w przypadku klonowania repozytorium przy dodawaniu submodułu może być przydatne użycie flagi `--recurse-submodules`, która zainicjalizuje moduł od razu z wykorzystaną flagą.

Aktualizacja submodułu wykonywana jest przez komendę

```bash
git submodule update --remote
```

z kolei jego inicjalizacja przez komendę

```bash
git submodule update --init --recursive
```

jeżeli w projekcie jest wiele submodułów i zależy nam na sprawnej zmianie gałęzi lub wykonaniu innej operacji dla każdego z repozytorium, warto użyć komendy `foreach` a następnie podać komendę, która ma być wykonana w danym repozytorium

```bash
git submodule foreach 'git checkout develop'
```

spowoduje to iteracyjne przejście przez każdy submoduł dodany w projekcie i wykonanie zadanej komendy. Więcej o submodułach można znaleźć w [dokumentacji git](https://www.git-scm.com/book/en/v2/Git-Tools-Submodules).

### LFS

Git LFS (Large File Storage) to narzędzie pozwalające na zastąpienie dużych plików takich jak grafiki, wideo, bazy danych odnośnikiem do danego pliku. Zapewnia to brak duplikowania danego pliku w historii, w efekcie zmniejszając pamięć zajmowanego repozytorium.

Aby korzystać z `git lfs` należy zainstalować rozszerzenie za pomocą komendy

```bash
sudo apt install git-lfs
```

Następnie, gdy repozytorium znajduje się plik, który powinien być dodany z wykorzystaniem `git lfs` należy skorzystać z komendy z odpowiednim rozszerzeniem plików, które powinny być w taki sposób przechowywane lub konkretną nazwą pliku. Informację o plikach przechowywanych za pomocą `git lfs` zostaną zaktualizowane w pliku `.gitattributes`.

```bash
git lfs track "*.mesh"
```

Następnie wystarczy dodać pliki i zakomitować wprowadzone zmiany. Więcej na temat `git lfs` można znaleźć na [oficjalnej stronie](https://git-lfs.com/).

### Komunikatory i integracje

Dodatkowo istnieje możliwość dodania integracji z komunikatorem zespołowym, aby wysyłać powiadomienia o merge requestach i zmianach w repozytorium (konfiguracja zależy od używanej platformy, np. GitLab/GitHub oraz Slack/Teams).

## Zasady

W ramach pracy z gitem zostały ustalone zasady takie jak:

1. Podstawowym językiem opisu jest język angielski, dotyczy to tworzenia komitów, gałęzi oraz opisów wydania.
2. Tworzone branche powinny być zgodnie z następującym podziałem:
  - `main`
  - `develop`
  - `feat`
  - `hotfix`
  - `release`
3. Każda z gałęzi rozpoczyna się z odpowiednim prefixem określającym jego kategorię, a następnie z odpowiednim opisem poprzedzonym `/` np. `feat/add_navigation_module`.
4. Każdy z komitów ma opisywać rzeczywiście dodane zmiany, z uwzględnieniem podziału na:
  - `feat`
  - `fix`
  - `style`
  - `refactor`
  - `test`
  - `docs`
  - `chore`
5. Opis wiadomości komita powinna zaczynać się od dużej litery.
6. Jeżeli dany projekt korzysta z zewnętrznego systemu zgłoszeń, warto zawrzeć informację, którego zadania dotyczy zmiana (dokładny opis w zakładce [Integracja systemu zgłoszeń](commits.md#integracja-systemu-zgloszen))
7. Wraz z łączeniem pracy na branch `main` powinien być wykonywany `release` danego kodu.

