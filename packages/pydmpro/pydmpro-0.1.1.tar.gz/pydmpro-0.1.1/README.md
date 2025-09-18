# pydm 🐍

A Python package designed to streamline dependency injection and parameter management for Python applications.

---

## Features

- **Service Container**: Manage services and dependencies with ease.
- **Interface Bindings**: Bind interfaces to implementations for seamless dependency management.
- **Parameters Bag**: Access application parameters from memory or environment variables.
- **Factory Bindings**: Create services dynamically using factory methods.

___

## 📦 Installation

Install from source:

```bash
pip install git+https://github.com/ariana126/pydm.git
```
or PyPI
```bash
pip install pydmpro
```

---

## 🚀 Quick Start

### An example in your project:
```python
from pydm import ServiceContainer, EnvParametersBag
from dotenv import load_dotenv

class DatabaseConnectionInterface:
    pass
class MySQLConnection:
    def __init__(self, base_url: str):
        self.__base_url = base_url
class Repository:
    def __init__(self, conn: DatabaseConnectionInterface):
        self.__conn = conn

def boot() -> None:
    service_container: ServiceContainer = ServiceContainer.get_instance()

    load_dotenv()
    service_container.set_parameters(EnvParametersBag())

    service_container.bind_parameters(MySQLConnection, {'base_url': 'MYSQL_URL'})
    service_container.bind(DatabaseConnectionInterface, MySQLConnection)

boot()
repository = ServiceContainer.get_instance().get_service(Repository) # Repositoy instance
```

## 🧪 Running Tests

```bash
pytest
```

---

## 📄 License
This project is licensed under the **MIT License** – see the [LICENSE](https://github.com/ariana126/pydm/blob/main/LICENSE) file for details.

---

## 🤝 Contributing
Contributions are welcome!  
If you have an improvement or find a bug:
1. Fork the repo
2. Create your branch
3. Submit a pull request

---

## 💡 About
`pydm` is a lightweight dependency management package designed to simplify service container management and parameter handling in Python projects. Originally created by [Ariana](https://github.com/ariana126), it provides tools to maintain clean, scalable architecture and streamline the injection of dependencies and configuration parameters.