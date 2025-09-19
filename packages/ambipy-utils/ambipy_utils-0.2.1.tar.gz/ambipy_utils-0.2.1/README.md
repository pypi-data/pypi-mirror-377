# ambipy-utils
### Pacote interno da Ambipar Carbon

## Prerequisitos
- [Python 3.12+](https://www.python.org/downloads/)
- [uv](https://docs.astral.sh/uv/)

## Ambiente de desenvolvimento

Este projeto está configurado para utilizar [uv](https://docs.astral.sh/uv/) como gerenciador de dependências e ferramentas como [ruff](https://docs.astral.sh/ruff/), [taskipy](https://github.com/taskipy/taskipy) e [pytests](https://docs.pytest.org/) para linting, formatação e testes. Ainda conta com [pre-commit](https://pre-commit.com/) para rodar os hooks de linting, formatação e algumas verificações uteis antes de cada commit.

## Instalação do ambiente de desenvolvimento

```bash
# instalação e/ou sincronização do ambiente virtual (.venv por padrão)
uv sync

# instalação do pre-commit
pre-commit install

# adicionar dependências ao ambiente virtual
# veja: https://docs.astral.sh/uv/concepts/projects/dependencies/#development-dependencies
uv add <dependencia>
uv add --dev  <dependencia>  # para dependências de desenvolvimento

# fazer o build do projeto e ter o instalável do pacote
# veja: https://docs.astral.sh/uv/concepts/projects/build/
uv build
```

## Executando os testes

```bash
task test  # executa pytest conforme configurado no pyproject.toml
```

## Publicação de novas versões

Para publicar uma nova versão, é necessário criar um novo tag no git e fazer o build do pacote. Com isso, o pacote pode ser publicado no PyPI.

Criar tag:

```bash
git tag -a v0.1.0 -m "Release v0.1.0"
```

Geração de build:

```bash
# veja: https://docs.astral.sh/uv/guides/package/
uv build
```

Publicação no PyPI:

```bash
# veja: https://docs.astral.sh/uv/guides/package/#publishing-your-package
uv publish --token <token_pypi>
```
