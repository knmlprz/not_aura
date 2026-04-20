# package_name

Package description

Table of contents

- [packagename](#package_name)
  - [Project structure](#project-structure)
  - [Dependencies](#dependencies)
    - [Subscribers](#subscribers)
    - [Publishers](#publishers)
    - [Services](#services)
  - [Installation](#installation)
  - [Parameters](#parameters)
  - [Usage](#usage)
  - [Class diagram](#class-diagram)
  - [Visuals](#visuals)
  - [Roadmap](#roadmap)
  - [Contributor(s)](#contributors)



## Project structure

```bash
.
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

## Dependencies

```bash
pkg_1
pkg_2
```

### Subscribers

Worth to add in own packages


| topic name    | message type                                                                           | example message |
| ------------- | -------------------------------------------------------------------------------------- | --------------- |
| `/topic/name` | [geometry_msgs/Twist](https://docs.ros2.org/galactic/api/geometry_msgs/msg/Twist.html) | ...             |


### Publishers

Worth to add in own packages


| topic name       | message type                                                                                                                                    | example message |
| ---------------- | ----------------------------------------------------------------------------------------------------------------------------------------------- | --------------- |
| `/control/topic` | [control_msgs/SteeringControllerStatus](https://github.com/ros-controls/control_msgs/blob/humble/control_msgs/msg/SteeringControllerStatus.msg) | ...             |


### Services

Worth to add in own packages


| service name               | service type            | example service |
| -------------------------- | ----------------------- | --------------- |
| `/<package_name_node>/srv` | [std_msgs/AnyMassage]() | ...             |
| `/<package_name_node>/srv` | [std_msgs/AnyMassage]() | ...             |


## Installation

Describe how to install your pkg

```shell
cd && cd ros2_ws/src/
git clone git@example.com:organization/repository.git
cd ..
colcon build --symlik-install
```

## Parameters

Parameters in [config](../config) dir. Files allow to config:

- `params_<package_name>.yaml` description

## Usage

To launch package_name:

## Class diagram

Diagram of classes

## Visuals

Image showing how the package works

## Roadmap

- Apply ...
- Config ...
- Add ...
- In the future...

## Contributor(s)

Contributors (contact details removed)