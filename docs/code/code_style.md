# Jak pisać kod?

<details>
<summary markdown="span"> Spis treści </summary>

- [Jak pisać kod?](#jak-pisać-kod)
  - [Wprowadzenie](#wprowadzenie)
  - [Python](#python)
    - [Zmienne](#zmienne)
    - [Klasy](#klasy)
    - [Metody i funkcje](#metody-i-funkcje)
    - [Dokumentacja](#dokumentacja)
  - [C++](#c)
    - [Zmienne](#zmienne-1)
    - [Klasy, struktury danych i typy](#klasy-struktury-danych-i-typy)
    - [Funkcje](#funkcje)
    - [Dokumentacja](#dokumentacja-1)
  - [C#](#c-1)
    - [Zmienne](#zmienne-2)
    - [Klasy, interfejsy, struktury i delegaty](#klasy-interfejsy-struktury-i-delegaty)
    - [Metody](#metody)
    - [Dokumentacja](#dokumentacja-2)

</details>

## Wprowadzenie

W zależności od języka programowania, w którym rozwijane jest dane oprogramowanie obowiązują inne zasady stylu, formatowania czy tworzenia dokumentacji. Jednak niezależnie od tego w którym języku rowijane jest dane oprogramowanie konieczne jest:

1. Zapewnienie obiektowości i przejrzystości kodu zgodnie z regułami zapisanymi w [Dobre praktyki](./object_programming.md),
2. Używanie języka angielskiego do deklarowania zmiennych, pisania komentarzy, metod, dokumentacji itp.,
3. Zachowanie modułowości rozwijanego oprogramowania,
4. Zdefiniowania formatowania tabulatora jako 4 spacji.

## Python

Kod pisany w języku Python powinien być zgodny z zasadami zdefiniowanymi w [pep8](https://peps.python.org/pep-0008/) oraz formatowany za pomocą formatera [black](https://github.com/psf/black).

Nazwy plików `.py` powinny być nazywane za pomocą `snake_case` i zawierać się w logicznych dla danego projektu folderach (zwykle zależnych od wykorzystywanego frameworku).

### Zmienne

Przyjęta konwencja nazw zmiennych to `snake_case`, czyli opisywanie zmiennych małymi literami z `_` jako przerwa logiczna w danej nazwie.

```python
new_variable = 0
is_door_open = True
```

Ze względu na charakter języka i jego braku hermetyzacji, określanie zmiennych prywatnych jest kwestią umowną podkreślaną przez dodanie `_` przed nazwą zmiennej.

```python
_any_private_variable = "I am only to internal use"
```

W przypadku definiowania zmiennych, które zachowują stałe wartości niezmienne w trakcie wykonywania kodu. Przyjmuje się ich deklarację poprzez wykorzystanie tak zwanego `UPERCASE` z ewentualnym wykorzsytaniem `_` jako logiczny przerywnik w nazwie.

```python
M_PI = 3.141592653589793238
```

### Klasy

W Pythonie nazwy klas definiowane są z wykorzystaniem `PascalCase` tzn. rozpoczynaniu przerwy logicznej nazwy z wielkiej litery.

```python
class MyClass:
    ...
```

Dodatkowo dana klasa powinna znajdować się w oddzielnych plikach, chyba że jej wielkość jest niedługa (nie zajmuje wiecej niż około 200 lini).

### Metody i funkcje

W przypadku metod i funkcji konwencja nazw zmiennych to `snake_case` jak w przypadku zmiennych.

```python
def long_function_name(
        var_one, var_two, var_three,
        var_four):
    print(var_one)
```

### Dokumentacja

Dokumentacja tworzona jest z wykorzystaniem `doc_string`, przy definicji klas oraz funkcji konieczne jest opisanie danych wejściowych, wyjściowych, a w przypadku klas również atrybutów.

```python
def complex(real=0.0, imag=0.0):
    """Form a complex number.

    Keyword arguments:
    real -- the real part (default 0.0)
    imag -- the imaginary part (default 0.0)
    """
```

Więcej przykładów oraz dobrych praktyk pisania dokumentacji w Pythonie definiuje [pep275](https://peps.python.org/pep-0257/).

## C++

Kod w C++ rozwijany jest dla wersji C++17 zgodnie z [Google C++ styleguide](https://google.github.io/styleguide/cppguide.html#Variable_Names).

Nazwy plików `.cpp` oraz `.hpp` powinny być nazywane za pomocą `snake_case` i zawierać się odpowiednio w folderach `src` oraz `include`.

Zawartość plików nagłówkowych powinna zawierać tzw. include guards w postaci `#pragama once`.

Dodatkowo nawiasy rozpoczynający deklarację danej sekcji kody `{}` powinny być deklarowane od nowej linii w celu zapewnienia większej przejrzystości kodu.

```cpp
void Foo()
{
    ...
}
```

### Zmienne

Nazwy zmiennych powinny być zadeklarowane przy użyciu `snake_case`.

```cpp
int variable = 0;
```

W przypadku użycia zmiennych prywatnych (`private`) w ramach metody klasy konieczne jest zdefiniowanie ich nazwy z `_` na końcu nazwy.

```cpp
class TableInfo 
{
    ...
    private:
        std::string table_name_;  // OK - underscore at end.
        static Pool<TableInfo>* pool_;  // OK.
};
```

Wartości definiowane w ramach dyrektywy preprocesora `#define`, które nie zmieniają swojej wartości deklarowane są z wykorzystaniem `UPERCASE` z wykorzystaniem `_` jako logiczny przerywnik w nazwie.

Pozostałe stałe definiowane np. jako atrybut klasy powinny być definiowane `mixed_case` - głównie `CamelCase` z poprzedzeniem za pomocą litery `k`.

```cpp
const int kDaysInAWeek = 7;
const int kAndroid8_0_0 = 24;  // Android 8.0.0
```

Typy wyliczeniowe analogicznie ze wzgledu na występowanie w `enum` mogą mieć klasyczną nazwę w `CamelCase`.

```cpp
enum class UrlTableError 
{
    Ok = 0,
    OutOfMemory,
    MalformedInput,
};
```

### Klasy, struktury danych i typy

Nazwy struktur danych oraz klasy definiowane są na pomocą `PascalCase`.

Przykład deklaracji klasy, z deklaracją atrybutów

```cpp
class MyClass
{
    public:
        int CountFooErrors(const std::vector<Foo>& foos) 
        {
            int n = 0;  // Clear meaning given limited scope and context
            for (const auto& foo : foos) 
            {
            ...
            ++n;
            }
            return n;
        }
        void DoSomethingImportant() 
        {
            std::string fqdn = ...;  // Well-known abbreviation for Fully Qualified Domain Name
        }
    private:
        const int kMaxAllowedConnections = ...;  // Clear meaning within context
};
```

Przykład deklaracji struktury:

```cpp
struct UrlTableProperties 
{
    std::string name;
    int num_entries;
    static Pool<UrlTableProperties>* pool;
};
```

Nazwy typów oraz aliasy  powinny być definiowane nazywane z wykorzystaniem konwencji `PascalCase` np.

```cpp
typedef hash_map<UrlTableProperties *, std::string> PropertiesMap;
using PropertiesMap = hash_map<UrlTableProperties *, std::string>;
```

### Funkcje

Nazwy funkcji powinny być definiowane za pomocą `PascalCase`, analogicznie  w przypadku deklaracji metod w klasie.

```cpp
AddTableEntry()
DeleteUrl()
OpenFileOrDie()
```

### Dokumentacja

Dokumentacja kodu w C++ rozwijana jest za pomocą [Doxygen](https://www.doxygen.nl/manual/index.html), który zapewnia wygenerowanie odnośników HTML z opisem metod i klas. Opisy są tworzone w postaci komentarzy w plikach nagłówkowych, przed deklaracją definicji klas oraz metod. Konieczne jest opisanie danych wejściowych oraz wyjściowych przy użyciu odpowiednich dekoratorów.

```cpp
/**
 * A brief history of JavaDoc-style (C-style) comments.
 *
 * This is the typical JavaDoc-style C-style comment. It starts with two
 * asterisks.
 *
 * @param theory Even if there is only one possible unified theory. it is just a
 *               set of rules and equations.
 */
void cstyle( int theory );
```

Więcej o dokumentowaniu w Doxygenie można znaleźć [tutaj](https://darkognu.eu/programming/tutorials/doxygen_tutorial_cpp/#documenting-the-code).

## C\#

Kod pisany w języku C\# powinien być zgodne z konwencją zawartą w [Unity C# Code](https://blog.unity.com/engine-platform/clean-up-your-code-how-to-create-your-own-c-code-style) oraz ogólnymi zasadami dla [.NET](https://learn.microsoft.com/en-us/dotnet/csharp/fundamentals/coding-style/identifier-names)

### Zmienne

Nazwy zmiennych powinne być pisane w zachowaniu konwencji `camelCase` w przypadku zmiennych lokalnych przyjmuje się, że zmienne powinny być pisane małą literą np.

```csharp
string nameForHuman = "John";
```

W przypadku zmiennych prywatnych, powinny być one deklarowane przez dodanie `m_` w analogicznej konwencji dalszej nazwy

```csharp
private double m_seconds;
```

Z kolei własciwości (`Properties`) danej klasy powinny być pisane `PascalCase`

```csharp
public double Hours
{
    ...
}
```

### Klasy, interfejsy, struktury i delegaty

Nazwy klasy, interfejsów, struktur oraz delegatów zapisywane są z wykorzystaniem konwencji `PascalCase`.

```csharp
public double Hours
{
    ...
}
```

```csharp
public record PhysicalAddress(
    string Street,
    string City,
    string StateOrProvince,
    string ZipCode);
```

```csharp
public struct ValueCoordinate
{
}
```

```csharp
public delegate void DelegateType(string message);
```

W przypadku nazewnictwa interfejsów dodatkowo jest dodawany prefiks `I`, który sygnalizuje, że dana nazwa wskazuje na interfejs

```csharp
public interface IWorkerQueue
{
}
```

### Metody

Nazwy metod oraz funkcji nadawane są w konwencji `PascalCase`

```csharp
// Method
public void StartEventProcessing()
{
    // Local function
    static int CountQueueItems() => WorkerQueue.Count;
    // ...
}
```

### Dokumentacja

Dokumentacja tworzonego kodu realizowana jest z wykorzystaniem [XML Commands](https://www.doxygen.nl/manual/xmlcmds.html), który umożliwia późniejsze wygenerowanie dokumentacji w [Doxygen](https://www.doxygen.nl/manual/index.html).

```csharp
/// <summary>
/// A search engine.
/// </summary>
class Engine
{
  /// <summary>
  /// The Search method takes a series of parameters to specify the search criterion
  /// and returns a dataset containing the result set.
  /// </summary>
  /// <param name="connectionString">the connection string to connect to the
  /// database holding the content to search</param>
  /// <param name="maxRows">The maximum number of rows to
  /// return in the result set</param>
  /// <param name="searchString">The text that we are searching for</param>
  /// <returns>A DataSet instance containing the matching rows. It contains a maximum
  /// number of rows specified by the maxRows parameter</returns>
  public DataSet Search(string connectionString, int maxRows, int searchString)
  {
    DataSet ds = new DataSet();
    return ds;
  }
}
```
