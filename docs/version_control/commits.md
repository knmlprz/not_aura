# Pisanie komitów

Spis treści

- [Pisanie komitów](#pisanie-komitów)
  - [Ogólna koncepcja](#ogólna-koncepcja)
  - [Tworzenie opisów](#tworzenie-opisów)
    - [Przykłady](#przykłady)
    - [Integracja systemu zgłoszeń](#integracja-systemu-zgloszen)
  - [Przydatne linki](#przydatne-linki)



## Ogólna koncepcja

Komity mają na celu dostarczenie informacji o tym czego dotyczą zamiany wprowadzone w danym kodzie, w ten sposób utrzymując logiczny porządek łatwiejsze jest zrozumienie co zostało zmienione.

W celu dodania wprowadzonych zmian należy najpierw wybrać pliki, które zostały zmienione

```git
git add path/to/changed_file
```

lub dla dodania wszystkich plików w folderze

```git
git add .
```

> **Uwaga:** Wymaga dokładnej weryfikacji dodawanych plików

Następnie po dodaniu odpowiednich plików konieczne jest dodanie komentarza do opisującego wprowadzane zmiany, udoskonalenia czy naprawy. Komentarz dodaje się za pomocą komendy:

```git
git commit
```

Ogólna struktura komita wygląda następująco:

```git
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

Możliwe jest też dodanie komita w wersji skróconej przez dodanie flagi `-m`

```git
git commit -m "<type>: Some description"
```

## Tworzenie opisów

Przy opisywaniu komitów konieczne jest określenie czego dotyczą zmiany, zwykle realizowane jest to w formie określającej wcześniej wspomniany rodzaj zmiany `<type>` a także jej opis `<description>`.

Typy wiadomości określane są w następujący sposób:

- `feat`: Nowa funkcja, którą dodajesz do konkretnej aplikacji
- `fix`: Naprawa błędu
- `style`: Funkcje i aktualizacje związane ze stylem
- `refactor`: Refaktoryzacja określonej sekcji kodu
- `test`: Wszystko związane z testowaniem
- `docs`: Wszystko związane z dokumentacją
- `chore`: Regularne utrzymanie kodu, np. zmiany w .gitignore.

Opis wiadomości powinien w prosty i zrozumiały sposób opisywać zmiany wprowadzone w kodzie. W przypadku konieczności zawarcia dłuższego opisu możliwe jest sformatowanie go w paru liniach oraz opisanie dokładniej wprowadzonych zmian.

### Przykłady

Poniżej znajdują się przykłady opisów komitów oraz informacji, które mogą zawierać.

Przykład wiadomości z wieloma akapitami i stópką:

```git
fix: Prevent racing of requests

Introduce a request id and a reference to latest request. Dismiss
incoming responses other than from latest request.

Remove timeouts which were used to mitigate the racing issue but are
obsolete now.

Reviewed-by: Z
Refs: #123
```

Komit bez długiego opisu

```git
docs: Correct spelling of CHANGELOG
```

Wiadomość komita z zdefiniowaniem obszaru zmian w kodzie

```git
feat(lang): Add Polish language
```

Wiadomość komita z opisem i stopką dotyczącą istotnej zmiany

```git
feat: Allow provided config object to extend other configs

BREAKING CHANGE: `extends` key in config file is now used for extending other config files
```

Wiadomość komita z “!” zwracającym uwagę na zmianę naruszającą zgodność

```git
feat!: Send an email to the customer when a product is shipped
```

Wiadomość komita z określonym zakresem zamian "()" i “!” zwracającym uwagę na zmianę naruszającą zgodność

```git
feat(api)!: Send an email to the customer when a product is shipped
```

Wiadomość komita z zarówno “!” jak i stopką BREAKING CHANGE

```git
chore!: Drop support for Node 6
BREAKING CHANGE: Use JavaScript features not available in Node 6.
```

### Integracja systemu zgłoszeń

Gdy projekt jest połączony z systemem zgłoszeń, możliwe jest zamieszczenie w komentarzu do komita informacji, jakiego zadania dotyczy zmiana - wystarczy dodać identyfikator zadania w formie `[TASK-ID]`.

## Przydatne linki

[Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/)

[Writing good commit messages, a practical guide](https://www.freecodecamp.org/news/writing-good-commit-messages-a-practical-guide/)