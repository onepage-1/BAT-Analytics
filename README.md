# BAT Analytics

Uma aplicação web moderna para análise de dados utilizando Flask e integração com a API Deepseek.

## Características

- Interface moderna e responsiva com TailwindCSS
- Sistema de login seguro
- Upload de arquivos XLSX e CSV
- Análise de dados através da API Deepseek
- Visualização de diagnósticos detalhados

## Requisitos

- Python 3.8+
- Pip (Gerenciador de pacotes Python)

## Instalação

1. Clone o repositório:
```bash
git clone [url-do-repositorio]
cd bat_analytics
```

2. Crie um ambiente virtual e ative-o:
```bash
python -m venv venv
.\venv\Scripts\activate  # Windows
```

3. Instale as dependências:
```bash
pip install -r requirements.txt
```

## Executando a Aplicação

1. Ative o ambiente virtual (se ainda não estiver ativo):
```bash
.\venv\Scripts\activate  # Windows
```

2. Execute a aplicação:
```bash
python app.py
```

3. Acesse a aplicação em seu navegador:
```
http://localhost:5000
```

## Credenciais de Acesso

- Usuário: 1234
- Senha: 1234

## Estrutura do Projeto

```
bat_analytics/
├── app.py              # Aplicação principal Flask
├── requirements.txt    # Dependências do projeto
├── uploads/           # Diretório para arquivos enviados
└── templates/         # Templates HTML
    ├── base.html      # Template base
    ├── login.html     # Página de login
    ├── upload.html    # Página de upload
    └── results.html   # Página de resultados
```
