# Praca z ROS2

Spis treści

- [Praca z ROS2](#praca-z-ros2)
  - [Wprowadzenie](#wprowadzenie)
  - [Struktura paczki](#struktura-paczki)
  - [Struktura plików](#struktura-plików)
    - [Konfiguracyjnych *params.yaml*](#konfiguracyjnych-paramsyaml)
    - [Uruchomieniowych](#uruchomieniowych)
      - [python *packagename.launch.py*](#python-package_namelaunchpy)
      - [xml *packagename.launch.xml*](#xml-package_namelaunchxml)
    - [CMake](#cmake)
    - [package.xml](#packagexml)
  - [Tworzenie wiadomości i serwisów](#tworzenie-wiadomości-i-serwisów)
  - [Dokumentacja](#dokumentacja)
  - [Istotne koncepcje](#istotne-koncepcje)
  - [Przydatne narzędzia](#przydatne-narzędzia)

## Wprowadzenie

W ramach rozwoju oprogramowania z wykorzystaniem frameworka ROS2 istnieją różne koncepcje tworzenia paczek oraz implementacji plików launch czy konfiguracyjnych. Poniżej zostaną przedstawione ogólne zasady ich tworzenia, a także zaznaczone preferowane formy wykorzystania w celu ujednolicenia tworzonych modułów.

## Struktura paczki

Struktura paczki bazuje na koncepcie przedstawionym w oficjalnej [instrukcji ROS2](https://docs.ros.org/en/humble/Tutorials/Beginner-Client-Libraries/Creating-Your-First-ROS2-Package.html). Preferowany stylem tworzenia paczki jest wykorzystanie `CMake` ze względu na intuicyjną konfigurację i możliwość dodawania niezbędnych bibliotek C++.

W przypadku paczki bazującej na C++ struktura plików wygląda następująco

```bash
.
├── doc
├── config
│   └── params_<package_name>.yaml
├── include
│   └── <package_name>
├── launch
│   ├── <package_name>.launch.xml # This type of launch
│   └── <package_name>.launch.py # Or this type
├── src
│   ├── <package_name>.cpp
│   └── <package_name>_node.cpp
├── CMakeLists.txt
├── package.xml
└── README.md
```

Dla paczki Python

```bash
.
├── doc
├── config
│   └── params_<package_name>.yaml
├── launch
│   ├── <package_name>.launch.xml # This type of launch
│   └── <package_name>.launch.py # Or this type
├── <package_name>
│   ├── __init__.py
│   └── module_to_import.py
├── scripts
│   └── <package_name>.py
├── CMakeLists.txt
├── package.xml
└── README.md
```

> **Uwaga:** W przypadku wykorzystania obydwu języków programowania struktura bazuje na plikach CMake i uzupełniana jest o brakujące foldery konieczne do wykorzystania do Python. Więcej na ten temat można znaleźć [tutaj](https://roboticsbackend.com/ros2-package-for-both-python-and-cpp-nodes/).

Dodatkowo stworzony plik README.md powinien być zrealizowany na [szablonie](./ros_readme.md) niezależnie od języka programowania wykorzystanego w danej paczce. Istotne jest również, żeby pamiętać o dodawaniu pliku [.gitignore](.ros_gitignore) przy dodawaniu paczki do repozytorium git.

## Struktura plików

W ramach tworzonych paczek panuje struktura plików konfiguracyjnych, uruchomieniowych oraz definiujących sposób budowania danej paczki.

### Konfiguracyjnych *params.yaml*

Dla tworzonych plików konfiguracyjnych `yaml` preferowane jest tworzenie pliku z nazwą paczki, który jest plikiem bazowym wykorzystywanym domyślnie w paczce, pliki dodatkowe realizujących określone funkcjonalności, powinny mieć zdefiniowane nazwy adekwatne do implementowanej konfiguracji.

```yaml
node_name:                                  # One node params
  ros__parameters:
    bool_value: True
    int_number: 5
    float_number: 3.14
    str_text: "Hello Universe"
    bool_array: [True, False, True]
    int_array: [10, 11, 12, 13]
    float_array: [7.5, 400.4]
    str_array: ['Nice', 'more', 'params']
    bytes_array: [0x01, 0xF1, 0xA2]
    nested_param:
      another_int: 7

/**:                                        # All nodes params
  ros__parameters:
    bool_value: True
    int_number: 5
    float_number: 3.14
    str_text: "Hello Universe"
    bool_array: [True, False, True]
    int_array: [10, 11, 12, 13]
    float_array: [7.5, 400.4]
    str_array: ['Nice', 'more', 'params']
    bytes_array: [0x01, 0xF1, 0xA2]
    nested_param:
      another_int: 7
```

### Uruchomieniowych

Pliki uruchomieniowe `launch` w ramach ROS2 mogą być implementowane na dwa sposoby w ramach pliku `.py` oraz pliku `.xml` wywodzącego się z ROS. W przypadku tworzenia nowej paczki należy korzystać z konwencji plików `launch.py`.

#### python *package_name.launch.py*

Przykład implementacji pliku `launch.py`, więcej o samej implementacji można znaleźć w [dokumentacji](https://docs.ros.org/en/humble/Tutorials/Intermediate/Launch/Launch-Main.html). Najistotniejsza jest implementacja niezbędnych modułów z `launch` lub `launch_ros`, które pozwalają na definicję kolejnych elementów takich jak argumenty, wyrażenia logiczne itd. W przypadku definicji argumentów launch oraz tych przekazywanych do węzła, preferowana jest deklaracja z wykorzystaniem parametrów.

```python
import os
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.substitutions import LaunchConfiguration, FindPackageShare
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node

def generate_launch_description():
    ld = LaunchDescription()
    param = LaunchConfiguration('param_name', default='value')

    param_launch_arg = DeclareLaunchArgument(
        'param_name',
        default_value = 'value',
        description='Some description'
    )

    pkg_config_path = os.path.join(
        FindPackageShare("pkg_name"), "config", "param_pkg_name.yaml"
    )

    pkg_name_to_launch = IncludeLaunchDescription(
            PythonLaunchDescriptionSource([
                FindPackageShare("pkg_name"), '/launch', '/pkg_name.launch.py']),
                launch_arguments=[pkg_config_path]
        )

    pkg_node = Node(
        package="pkg_name", 
        executable="pkg_run_file",
        condition=IfCondition(param_launch_arg)
    )

    ld.add_action(param_launch_arg)
    ld.add_action(pkg_name_to_launch)
    ld.add_action(pkg_node)
    return ld
```

Wywołanie danego pliku uruchamiającego paczkę

```bash
ros2 launch package_name package_name.launch.py
```

Analogiczna komenda z przekazaniem argumentu

```bash
ros2 launch package_name package_name.launch.py arg_name:=value
```

#### xml *package_name.launch.xml*

Przykład pliku uruchamiającego paczkę w ramach rozszerzenia `launch.xml`, pliki te powinny być implementowane w ostateczności przy migracji z ROS.

```xml
<launch>
    <node pkg="pkg_name" exec="exec_name" name="node_name" output="screen">
        <param name="param" value="param_value"/>
    </node>
</launch>
```

### CMake

Struktura pliku CMake zależy od koniecznych do załączenia bibliotek, pakietów i zależności tworzonej paczki. W tym celu niezbędne jest zdefiniowanie niezbędnych folderów, w których znajdują się definiowane biblioteki i wykorzystywane pliki. Dodatkowo w ramach samego ROS2 konieczne jest określenie zależności `ament`, które mogą być przydatne w zależności od tworzonej paczki, więcej na ten temat można przeczytać [tutaj](https://docs.ros.org/en/humble/Concepts/Advanced/About-Build-System.html#term-ament-Python-package).

Przykładowy plik CMake

```cmake
cmake_minimum_required(VERSION 3.5)
project(<package_name>)

# Default to C++14
if(NOT CMAKE_CXX_STANDARD)
    set(CMAKE_CXX_STANDARD 14)
endif()

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
    add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# Needed packages
find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(std_msgs REQUIRED)

# Define executable files
add_executable(node_name src/<package_name>_node.cpp)
ament_target_dependencies(node_name rclcpp std_msgs)

install(TARGETS
    node_name
    DESTINATION lib/${PROJECT_NAME})

ament_package()
```

### package.xml

Plik z manifestem służący do opisu danej paczki w ROS2, *package.xml* jest plikiem niezbędnym do poprawnego działania frameworka oraz rozpoznawania paczek. W ramach pliku konieczne jest zdefiniowanie nazwy paczki oraz zależności od innych paczek, dzięki poprawnym definicjom zależności możliwe jest późniejsze wykorzystanie `rosdep`, który umożliwia automatyczną instalację zależności - [link](https://docs.ros.org/en/independent/api/rosdep/html/) do dokumentacji narzędzia.

```xml
<?xml version="1.0"?>
<?xml-model
   href="http://download.ros.org/schema/package_format3.xsd"
   schematypens="http://www.w3.org/2001/XMLSchema"?>
<package format="3">
    <name>my_package</name>
    <version>0.0.0</version>
    <description>TODO: Package description</description>
    <maintainer email="maintainer@example.com">maintainer</maintainer>
    <license>TODO: License declaration</license>

    <buildtool_depend>ament_cmake</buildtool_depend>

    <test_depend>ament_lint_auto</test_depend>
    <test_depend>ament_lint_common</test_depend>

    <export>
        <build_type>ament_cmake</build_type>
    </export>
</package>
```

Instalacja i konfiguracja  `rosdep`

```bash
sudo apt-get install python3-rosdep
```

```bash
sudo rosdep init
rosdep update
```

Instalacja zależności, więcej na temat wykorzystanych argumentów można znaleźć [tutaj](https://docs.ros.org/en/independent/api/rosdep/html/)

```bash
rosdep install --from-paths src -y --ignore-src
```

## Tworzenie wiadomości i serwisów

W przypadku dodawania własnych wiadomości i serwisów w ramach paczki, konieczne jest opisanie ich w ramach tworzonego pliku `.msg`, w którym zawarte będą informacje dotyczące wykorzystanych jednostek oraz informacje przydatne w ich użytkowaniu. Jeżeli wiadomość przekazuje informację z parametrami fizycznymi to powinny być one zgodne z [REP-103](https://www.ros.org/reps/rep-0103.html), o ile jest to możliwe i zgodne z logiką działania programu.

Przykład opisu wiadomości:

```bash
# Message allows to comunicate with CAN magistral on PAWO robot 
std_msgs/Header header
int32 ac_counter        #  Counter for CAN msgs form 0 to 255
int32 ac_wheel_twist    #  Wheel twist from 0 to 255 where 0 is -180 degree (maximum to rigth) and 255 is 180 degree (maximum to left) 
int32 ac_brake_force    #  Brake force in N where 0 is 0N and 255 is 250N
int32 ac_velocity       #  Velocity in km/h where 0 is 0 km/h and 255 is 255 km/h
int32 ac_max_velocity   #  Maximum velocity in km/h setting on robot where where 0 is 0 km/h and 255 is 255 km/h
bool ac_direction       #  Driving direction where 0 is forward and 1 is reverse
```

## Dokumentacja

W celu tworzenia dokumentacji ROS2 konieczna jest instalacja pakietu [rosdoc2](https://github.com/ros-infrastructure/rosdoc2#installation), odpowiadającego za automatyczne generowanie dokumentacji. Narzędzie to wspiera generowanie dokumentacji dla `Doxygen` w przypadku C++ oraz `Sphinx` dla Pythona. `rosdoc2` korzysta z pakietów [breathe](https://breathe.readthedocs.io/en/latest/) i [exhale](https://exhale.readthedocs.io/en/latest/), tworzac podstawową konfigurację i integrację.

W celu wygenerowania dokumentacji w HTML należy użyć komendy, która wygeneruje dokumentację w pliku `docs_output/<package-name>/index.html`.

```bash
rosdoc2 build --package-path <package-path>
```

Dzięki wykorzystaniu `Sphinx` do ogólnego generowania dokumentacji, możliwa jest konfiguracja plików oraz stylu wyświetlania docelowej strony. Definicja konfiguracji powinna być ustalana przed rozpoczęciem danego projektu, więcej o dostosowaniu tego narzędzia można znaleźć [tutaj](https://docs.ros.org/en/humble/How-To-Guides/Documenting-a-ROS-2-Package.html#customizing-sphinx-documentation).

Jeszcze więcej opisów o dokumentacji [tutaj](https://design.ros2.org/articles/per_package_documentation.html).

## Istotne koncepcje

W ROS2 obowiązują pewne koncepcje warte uwagi, które mogą wpłynąć na działanie albo rozwijanie pakietów. Zasady pracy z nimi zależą od rozwijanego pakietu oraz projektu, w związku z tym każdy kto rozpoczyna pracę z ROS2 powinien się z nimi zapoznać. Zagadnienia o których mowa dotyczą takich pojęć jak:

- [Quality of Service](https://docs.ros.org/en/humble/Concepts/Intermediate/About-Quality-of-Service-Settings.html) - definiującej polityki komunikacji pomiędzy węzłami,
- [Composition](https://docs.ros.org/en/humble/Concepts/Intermediate/About-Composition.html) - odpowiednik nodeletów dla ROS, pozwalający na włączanie węzłów w ramach jednego procesu,
- [Life cycle](https://design.ros2.org/articles/node_lifecycle.html) - opis jak wygląda cykl życia zarządzanego węzła,
- [ROS 2 Security](https://docs.ros.org/en/humble/Concepts/Intermediate/About-Security.html) - opis możliwości zabezpieczeń w ROS2.

Demo pokazujące przykłady użycia powyższych koncepcji:

- [Użycie QoS](https://docs.ros.org/en/humble/Tutorials/Demos/Quality-of-Service.html)
- [Użycie Composition w launch](https://docs.ros.org/en/humble/How-To-Guides/Launching-composable-nodes.html)
- [Zarządzanie cyklem życia węzłów](https://github.com/ros2/demos/blob/humble/lifecycle/README.rst)
- [Zarządzenie komunikacją wewnątrz procesową](https://docs.ros.org/en/humble/Tutorials/Demos/Intra-Process-Communication.html).

## Przydatne narzędzia

Lista narzędzi oraz komend przydatnych do pracy z ROS2:

- narzędzia `rqt_tf_tree` oraz `rqt_graph` itp.
- [tf2_tools](https://index.ros.org/p/tf2_tools/)
- [RQt](https://docs.ros.org/en/humble/Concepts/Intermediate/About-RQt.html)

