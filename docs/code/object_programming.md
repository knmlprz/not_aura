# Dobre praktyki programowania obiektowego

Programowanie obiektowe, znane również jako OOP (Object Oriented Programming), to paradygmat programowania, który służy do tworzenia oprogramowania w oparciu o koncepcję „obiektów”.

## SOLID

Mnemonik opisujący pięć podstawowych zasad założeń programowania obiektowego:

1. Jednej odpowiedzialności (ang. single responsibility principle),
2. Otwarte-zamknięte (ang. open-close principle),
3. Podstawienia Liskov (ang. Liskov substitution principle),
4. Segregacji interfejsów (ang. interface segregation principle),
5. Odwrócenia zależności (ang. dependency inversion principle).

### Single responsibility Principle

Zasada jednej odpowiedzialności (SRP) opisuje, że klasa lub metoda powinna mieć tylko jedną odpowiedzialność i posiadać tylko jeden powód do zmiany - nigdy nie powinno być więcej niż jednego powodu do istnienia danej klasy. Znaczy to, że dana klasa powinna być odpowiedzialna tylko za jeden proces.

W przypadku rozważania modułu, który generuje i drukuje raport występuje odpowiedzialność za dwa procesy, które mogą się w przyszłości zmieniać. W przypadku generowania może się zmieniać treść raportu, a w drugim np. format wydruku. W związku z tym oba te procesy powinny zostać zaimplementowane jako dwa oddzielne klasy lub moduły komunikujące się między sobą.

### Open-closed Principle

Zasada otwarte-zamknięte (OCP) mówi o tym, że elementy systemu takie jak klasy, metody, funkcje powinny być otwarte na wprowadzanie rozszerzeń, ale zamknięta na jej modyfikacje. W przypadku zachowania tej zasady redukowane jest zagrożenie zepsucia istniejącej funkcjonalności i większa otwartość na potencjalne wykorzystanie w innych miejscach.

Dotyczy to na przykład wprowadzanych abstrakcji lub dziedziczenia, które zapewniają uniwersalność kodu i jego łatwiejszy rozwój dla konkretnych przypadków wykorzystania. Jednak trzeba być ostrożnym, żeby nie okazało się, że finalnie każda część kodu będzie elementem abstrakcji. Warto to stosować z rozwagą w momencie, gdy dana część systemu będzie rozwijana w przyszłości.

### Liskov Substitution Principle

Zasada podstawienia Liskov'a (LSP) mówi o tym, że funkcje, które używają wskaźników lub referencji klas bazowych muszą być w stanie używać również obiektów klas dziedziczących po klasach bazowych bez dokładnej znajomości tych obiektów. Tym samym klasa dziedzicząca powinna tylko rozszerzać możliwości klasy bazowej i nie zmieniać tego, co ona robiła już wcześniej. Powoduje to, że obiekt nadrzędny powinien móc być zastąpiony w poprawny sposób nie wpływając tym samym na działanie obiektów pochodnych.

### Interface Segregation Principle

Zasada segregacji interfejsów (ISP) polega na implementacji w klasie wielu mniejszych, dedykowanych interfejsów niż jednego ogólnego. Dodatkowo istotne jest, żeby nie implementować metod, które są niepotrzebne lub nieużywane.

Zapewnia to utrzymanie kodu przejrzystym i zapewnieniu dostarczeniu przez metodę tylko tego za co jest potrzebne, bez zbędnych funkcjonalności pobocznych.

### Dependency Inversion Principle

Zasada odwrócenia zależności (DIP), mówi o tym, że wysoko poziomowe moduły nie powinny zależeć od modułów na niższym poziomie. Tym samym sprawiając, że zależności między nimi powinny wynikać z abstrakcji.

Implementacja tej zasady pozwala na możliwość odwrócenia logiki implementacji pojedynczej jednostki, a tym samym sprawia, że wykorzystanie abstrakcji nie wymaga zmiany modułu nadrzędnego.

Przykład praktyczny zasady DIP warto omawiać na kodzie projektowym (brak grafiki referencyjnej w tym repozytorium).

## KISS

Reguła **KISS (ang. Keep It Simple Stupid)** powstała w latach 60. XX w. w środowisku amerykańskich inżynierów wojskowych, została zaadaptowana w wielu branżach inżynierskich oraz programistycznych. Polega na zachowaniu przejrzystej struktury bez dodawania niepotrzebnych elementów. Istnieje również polski zapis tej zasady pod akronimem BUZI (Bez Udziwnień Zapisu, Idioto).

## DRY

Reguła **DRY (ang. Don’t Repeat Yourself)** jest regułą stosowaną w procesie wytwarzania oprogramowania i polega na unikaniu różnego rodzaju powtórzeń nie tylko w kodzie, ale również czynnościach wykonywanych przez programistów. Zasada zachęca do tworzenia wszelkiego rodzaju modułów elementów powtarzalnych oraz automatyzacji pracy ręcznej.

W przypadku wytwarzania oprogramowania w językach obiektowych zaleca się używanie funkcji, szablonów, struktur, klas, ale również stałych redukując tym samym liczbę tzw. *magic number*. Dodatkowo w automatyzacji pracy ręcznej znajduje swoje zastosowanie przez plany testów, budowania paczek oraz dokumentacji.

## YAGNI

Reguła **YAGNI (ang. You aren't gonna need it)** jest jedną z zasad programowania ekstremalnego, która mówi, że nie powinno się dodawać funkcjonalności, dopóki nie jest ona uznana za konieczną. Implementacja tej zasady pozwala uniknąć ryzyka późniejszej refaktoryzacji kodu, który będzie konieczny do zmiany, gdy pojawi się konkretna potrzeba danej funkcjonalności.
