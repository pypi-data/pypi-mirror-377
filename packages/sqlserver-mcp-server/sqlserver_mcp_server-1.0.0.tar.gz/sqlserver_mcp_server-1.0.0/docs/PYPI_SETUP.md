# Configuração de Publicação no PyPI

Este documento explica como configurar a publicação automática do SQL Server MCP Server no PyPI.

## Configuração dos Secrets do GitHub

Para habilitar a publicação automática via GitHub Actions, você precisa configurar os seguintes secrets no seu repositório GitHub:

### 1. Acessar as Configurações do Repositório

1. Vá para o seu repositório no GitHub
2. Clique em **Settings** (Configurações)
3. No menu lateral, clique em **Secrets and variables** → **Actions**

### 2. Configurar o Secret PYPI_API_TOKEN

1. Clique em **New repository secret**
2. **Name**: `PYPI_API_TOKEN`
3. **Secret**: Seu token de API do PyPI

#### Como obter o token do PyPI:

1. Acesse [PyPI.org](https://pypi.org) e faça login
2. Vá para **Account settings** → **API tokens**
3. Clique em **Add API token**
4. **Token name**: `sqlserver-mcp-server-github`
5. **Scope**: `Entire account (all projects)` ou `Specific project: sqlserver-mcp-server`
6. Copie o token gerado (formato: `pypi-...`)

### 3. Configurar o Secret TESTPYPI_API_TOKEN (Opcional)

Para publicar também no TestPyPI:

1. Clique em **New repository secret**
2. **Name**: `TESTPYPI_API_TOKEN`
3. **Secret**: Seu token de API do TestPyPI

#### Como obter o token do TestPyPI:

1. Acesse [TestPyPI.org](https://test.pypi.org) e faça login
2. Siga os mesmos passos do PyPI principal

## Configuração do Ambiente de Produção

1. No GitHub, vá para **Settings** → **Environments**
2. Clique em **New environment**
3. **Name**: `production`
4. Clique em **Create environment**
5. Em **Environment secrets**, adicione:
   - `PYPI_API_TOKEN`: Seu token do PyPI

## Configuração Local

### 1. Arquivo .pypirc

Crie um arquivo `.pypirc` na raiz do projeto:

```ini
[distutils]
index-servers = 
    pypi
    testpypi

[pypi]
repository = https://upload.pypi.org/legacy/
username = __token__
password = your-pypi-api-token-here

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = your-testpypi-api-token-here
```

### 2. Variáveis de Ambiente

Alternativamente, você pode usar variáveis de ambiente:

```bash
export TWINE_USERNAME=__token__
export TWINE_PASSWORD=your-pypi-api-token-here
```

## Comandos de Publicação

### Build Local

```bash
# Build completo com validações
make build

# Build simples
make build-simple
```

### Publicação Local

```bash
# Publicar no PyPI
make publish

# Publicar no TestPyPI
make publish-test

# Dry run (teste sem publicar)
make publish-dry-run

# Dry run no TestPyPI
make publish-test-dry-run
```

### Publicação Manual

```bash
# Build
python build.py

# Publicar
python scripts/publish.py

# Publicar no TestPyPI
python scripts/publish.py --repository testpypi

# Dry run
python scripts/publish.py --dry-run
```

## Publicação Automática via GitHub Actions

A publicação automática é configurada no arquivo `.github/workflows/ci.yml` e é executada quando:

1. Um push é feito para a branch `main`
2. Todos os testes passam
3. O build é bem-sucedido
4. Os secrets estão configurados

### Workflow de Publicação

1. **Build**: O pacote é construído
2. **Verificação**: O pacote é verificado com `twine check`
3. **Upload**: O pacote é enviado para o PyPI
4. **Notificação**: O resultado é notificado

## Verificação da Publicação

Após a publicação, verifique:

1. **PyPI**: https://pypi.org/project/sqlserver-mcp-server/
2. **TestPyPI**: https://test.pypi.org/project/sqlserver-mcp-server/

## Instalação do Pacote Publicado

```bash
# Instalar do PyPI
pip install sqlserver-mcp-server

# Instalar do TestPyPI
pip install --index-url https://test.pypi.org/simple/ sqlserver-mcp-server

# Instalar com dependências de desenvolvimento
pip install sqlserver-mcp-server[dev]

# Instalar com dependências de teste
pip install sqlserver-mcp-server[test]
```

## Troubleshooting

### Erro de Autenticação

- Verifique se o token está correto
- Certifique-se de que o token tem as permissões necessárias
- Verifique se o secret está configurado corretamente no GitHub

### Erro de Build

- Execute `python build.py` localmente para verificar
- Verifique se todas as dependências estão instaladas
- Execute os testes: `pytest tests/contract/`

### Erro de Upload

- Verifique se o pacote já existe no PyPI
- Para TestPyPI, você pode sobrescrever
- Para PyPI, você precisa incrementar a versão

### Incremento de Versão

Para publicar uma nova versão:

1. Atualize a versão em `pyproject.toml`
2. Atualize o `CHANGELOG.md`
3. Faça commit e push para `main`
4. A publicação automática será executada

## Segurança

- **Nunca** commite tokens de API no código
- Use sempre secrets do GitHub para tokens
- Mantenha os tokens seguros e rotacione-os periodicamente
- Use TestPyPI para testes antes de publicar no PyPI principal
