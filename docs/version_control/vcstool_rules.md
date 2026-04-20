# Instrukcja Używania Narzędzi vcstool i ripvcs

## VCS

vcstool: Menedżer Obszarów Roboczych Wielu Repozytoriów
  vcstool to narzędzie wiersza poleceń stworzone do zarządzania obszarem roboczym składającym się z projektów pochodzących z różnych systemów kontroli wersji. Jest ono szeroko stosowane w ekosystemie Robot Operating System (ROS) i zastąpiło wcześniejsze narzędzie wstool.

### 1. Instalacja vcstool

vcstool jest dostępny w pakietach systemowych dla systemów opartych na Debianie/Ubuntu lub poprzez menedżer pakietów Python pip:

Dla systemów Debian/Ubuntu:

```bash
sudo apt install python3-vcstool
```

Dla innych systemów lub w przypadku braku pakietu apt:

```bash
sudo pip install -U vcstool
```

### 2. Kluczowe Funkcjonalności i Polecenia vcstool

vcstool obsługuje wiele systemów kontroli wersji, w tym Git, Mercurial (hg), Subversion (svn) i Bazaar, co czyni go wszechstronnym narzędziem do zarządzania różnorodnymi środowiskami deweloperskimi.

**Zarządzanie obszarem roboczym z pliku .repos lub .rosinstall**:

Vcstool zarządza lokalnymi repozytoriami SCM w oparciu o pojedynczy plik definicji obszaru roboczego, zazwyczaj w formacie .repos lub .rosinstall.
Przykład struktury pliku .repos:

```YAML
repositories:
  my_repo_1:
    type: git
    url: https://example.com/group/my_repo_1.git
    version: main
  my_repo_2:
    type: svn
    url: https://svn.example.com/my_repo_2/trunk
```

**Wypełnianie obszaru roboczego**:
To polecenie klonuje wszystkie repozytoria wymienione w określonym pliku definicji do bieżącego katalogu roboczego.

```bash
vcs import src < my_workspace.repos
```

**Aktualizowanie obszaru roboczego**:
Pobiera najnowsze zmiany lub przełącza na określone wersje we wszystkich zarządzanych repozytoriach.

```bash
vcs pull src
```

**Sprawdzanie statusu**:
Zapewnia skonsolidowany przegląd statusu (np. niezacommitowane zmiany, nie wypchnięte commity) dla wszystkich repozytoriów w obszarze roboczym.

```bash
vcs status src
```

**Eksportowanie definicji repozytoriów**:
Generuje plik .repos z istniejącego obszaru roboczego, co jest przydatne do udostępniania konfiguracji lub przechwytywania dokładnego stanu środowiska pracy.

```bash
vcs export --exact-with-tags src > current_workspace.repos
```

**Walidacja pliku definicji**:
Sprawdza poprawność struktury i zawartości pliku .repos.

```bash
vcs validate --input my_workspace.repos
```

## RV ripvcs

ripvcs: Wysokowydajny Menedżer Repozytoriów Git
ripvcs (często wywoływane jako rv) to narzędzie wiersza poleceń napisane w języku Go, zaprojektowane z myślą o wysokiej wydajności i efektywności w zarządzaniu licznymi repozytoriami Git. Jest pozycjonowane jako nowoczesna alternatywa dla vcstool, szczególnie dla przepływów pracy skoncentrowanych na Git.

### 1. Instalacja ripvcs

```bash
RIPVCS_VERSION=$(curl -s "https://api.example.com/repos/org/ripvcs/releases/latest" | \grep -Po '"tag_name": *"v\K[^"]*')
ARCHITECTURE="linux_amd64"
curl -Lo ~/.local/bin/rv "https://example.com/org/ripvcs/releases/download/v${RIPVCS_VERSION}/ripvcs_${RIPVCS_VERSION}_${ARCHITECTURE}"
chmod +x ~/.local/bin/rv
```

### 2. Kluczowe Funkcjonalności i Polecenia ripvcs

Ripvcs koncentruje się wyłącznie na repozytoriach Git, wykorzystując współbieżność Go (goroutines) do optymalizacji wydajności.

**Ogólne użycie**:
Wszystkie polecenia ripvcs są dostępne poprzez `rv`. Możesz uzyskać szczegółową pomoc dla każdego polecenia, uruchamiając `rv help`.

**Importowanie repozytoriów** `rv import`:
Klonuje repozytoria wymienione w danym pliku .repos. To polecenie jest bardzo elastyczne i obsługuje rekurencyjne wyszukiwanie innych plików .repos w zagnieżdżonych katalogach.

```bash
rv import --input my_workspace.repos
```

**Przydatne flagi dla rv import**:

```bash
--depth-recursive: Kontroluje głębokość rekurencyjnego wyszukiwania plików .repos (domyślnie -1 dla nieograniczonej głębokości).
--exclude lub -x: Lista plików i/lub katalogów do wykluczenia podczas rekurencyjnego importu.
--force: Wymusza nadpisywanie istniejących repozytoriów.
--recurse-submodules: Rekurencyjnie klonuje podmoduły Git, zapewniając pełne rozwiązywanie zależności.
--retry: Ponawia nieudane operacje importu.
--shallow: Wykonuje płytkie klonowanie (bez pełnej historii), przydatne do zmniejszania rozmiaru pobierania.
--workers: Ustawia liczbę równoległych workerów dla operacji współbieżnych, co znacznie przyspiesza proces. Przykład z flagami:
```

```bash
rv import --input my_complex_workspace.repos --recurse-submodules --workers 8 --shallow
```

**Pobieranie najnowszych zmian**:

Pobiera najnowszą wersję z zdalnych repozytoriów dla całego obszaru roboczego.

```bash
rv pull
```

**Sprawdzanie statusu**:

Sprawdza i raportuje status wszystkich repozytoriów w obszarze roboczym.

```bash
rv status path
```

**Przełączanie wersji repozytoriów**:

Ułatwia przełączanie wersji repozytoriów w całym obszarze roboczym.

```bash
rv switch my_repo -b my_branch
```

**Synchronizowanie repozytoriów**:

Synchronizuje wszystkie znalezione repozytoria, zapewniając spójność. Stashuje aktualne zmiany, pobiera najnowsze aktualizacje i wraca z przechowanymi zmianami.

```bash
rv sync
```

**Walidacja pliku definicji**:

Waliduje strukturę i zawartość pliku .repos. Sprawdza czy jest dostęp do podanego url oraz czy istnieje branch podany w pliku `.repos` 

```bash
rv validate --input my_workspace.repos
```

> NOTE: Jeżeli któreś repozytorium używa submodułów warto użyć dodatkowo flagi `--recurse-submodules`

**Eksportowanie listy repozytoriów**:

Eksportuje listę dostępnych repozytoriów, podobnie jak vcstool export.

```bash
rv export > current_rv_workspace.repos
```

**Generowanie autouzupełniania shell'a**:

rv obsługuje generowanie skryptów autouzupełniania dla bash, fish, powershell i zsh.
Przykład dla zsh:

```bash
rv completion zsh > _ripvcs # Następnie umieść plik _ripvcs w odpowiednim miejscu, aby był ładowany przez konfigurację zsh.
```

