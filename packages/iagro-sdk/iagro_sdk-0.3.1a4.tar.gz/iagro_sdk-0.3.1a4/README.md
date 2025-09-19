# IAgro SDK

O IAgro SDK é um pacote Python que fornece componentes reutilizáveis para projetos da IAgro, incluindo modelos base, repositórios, schemas e tratamento de exceções personalizadas.


## Descrição

O IAgro SDK fornece componentes base comuns para aplicações Python da IAgro, incluindo:

- **Modelos Base**: Classes base para entidades de banco de dados com campos automáticos (ID, timestamps)
- **Repository Pattern**: Implementação genérica do padrão Repository com operações CRUD
- **Schemas**: Schemas base para serialização/deserialização usando Pydantic
- **Tratamento de Exceções**: Exceções personalizadas para diferentes cenários de erro

## Instalação

### Via PyPI

```bash
pip install iagro-sdk
```

### Para desenvolvimento local

```bash
git clone <repositorio-url>
cd iagro-sdk
poetry install
```

## Uso Rápido

```python
from iagro_sdk.model import BaseModelMixin
from iagro_sdk.repository import BaseRepository

# Definir modelo
class User(BaseModelMixin, table=True):
    name: str
    email: str

# Definir repository
class Repository(BaseRepository[User]):
    def __init__(self):
        super().__init__(User)
        
# Usar repository
repository = Repository()
users = await repository.list(session)
```

## Documentação

Para documentação completa da API, consulte: [docs/api-reference.md](docs/api-reference.md)

## Dependências

- **Python**: >= 3.12
- **SQLAlchemy**: >= 2.0.43, < 3.0.0
- **SQLModel**: >= 0.0.24, < 0.0.25
- **Pydantic**: >= 2.11.9, < 3.0.0

## Desenvolvimento

### Configuração do ambiente

```bash
# Clonar repositório
git clone https://github.com/IAgro-Solutions/iagro-sdk.git
cd iagro-sdk

# Instalar dependências
poetry install

# Ativar ambiente virtual
poetry env activate
```

### Scripts de Build e Publicação

O projeto utiliza um Makefile com comandos para facilitar o processo de versionamento e publicação.

#### Comandos de Versionamento

```bash
# Versão de pré-lançamento (ex: 0.2.1 -> 0.2.2-alpha.0)
make pre-release

# Versão patch (correções de bugs: 0.2.1 -> 0.2.2)
make release-patch

# Versão minor (novas funcionalidades compatíveis: 0.2.1 -> 0.3.0)
make release-minor

# Versão major (mudanças incompatíveis: 0.2.1 -> 1.0.0)
make release-major
```

#### Build do Pacote

```bash
# Construir o pacote (gera arquivos em dist/)
make build
```

#### Publicação no PyPI

**Requisitos:**
- Token de acesso

```bash
# Configurar token PyPI como variável de ambiente
export PYPI_TOKEN="seu-token-aqui"

# Publicar (executa build automaticamente)
make publish
```
Ou
```
make publish PYPI_TOKEN="seu-token-aqui"
```

### Versionamento Semântico

O projeto segue o padrão [SemVer](https://semver.org/):

- **PATCH** (x.x.X): Correções de bugs compatíveis
- **MINOR** (x.X.x): Novas funcionalidades compatíveis
- **MAJOR** (X.x.x): Mudanças incompatíveis na API

### Estrutura do Projeto

```
iagro-sdk/
├── iagro_sdk/
│   ├── __init__.py
│   ├── exceptions.py      # Exceções personalizadas
│   ├── model.py          # Modelo base com campos automáticos
│   ├── repository.py     # Repository pattern genérico
│   └── schemas.py        # Schemas base para serialização
├── docs/
│   └── api-reference.md  # Documentação da API
├── pyproject.toml        # Configuração do projeto
├── Makefile             # Scripts de build e publicação
└── README.md
```
## Licença

Este projeto é propriedade da IAgro.

## Autor

**Armando Luz** - armandoari.288@gmail.com
