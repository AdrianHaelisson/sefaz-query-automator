# SEFAZ Query Automator

Automatize a preparação e o acompanhamento de solicitações de XMLs no portal SEFAZ. Uma interface Streamlit orienta o envio da planilha e apresenta o andamento do processamento em Python.

[Código do projeto](https://github.com/AdrianHaelisson/sefaz-query-automator) · [Explorar simulação AH XML Fiscal](https://ah-automacoes-demo.vercel.app/xml-fiscal) · [Portfólio](https://haelisson.com.br)

## O fluxo

1. Configure o ambiente e o acesso ao portal suportado pelo projeto.
2. Forneça a planilha usada para organizar as solicitações.
3. Acompanhe as etapas e os registros do processamento na interface.
4. Retome o trabalho a partir do progresso salvo, quando aplicável.

O objetivo é diminuir a repetição de navegação e preenchimento, mantendo o andamento visível.

## Recursos

- Interface web em Streamlit.
- Solicitações organizadas a partir de planilha.
- Automação de navegador com Selenium.
- Registros de execução e persistência de progresso.
- Configuração de credenciais por variáveis de ambiente.
- Opção de navegador em modo headless.

O comportamento depende do portal implementado e das permissões de acesso. O nome do projeto não implica suporte a todas as SEFAZ estaduais, a todos os documentos fiscais ou a mudanças futuras dos portais.

## Stack

Python, Streamlit, Selenium, Pandas, OpenPyXL, `webdriver-manager` e `python-decouple`.

## Executar localmente

Pré-requisitos: Python, navegador e dependências compatíveis com `requirements.txt`.

```bash
git clone https://github.com/AdrianHaelisson/sefaz-query-automator.git
cd sefaz-query-automator
python -m venv venv
```

Ative o ambiente virtual:

```bash
# Linux/macOS
source venv/bin/activate
```

```powershell
# Windows PowerShell
.\venv\Scripts\Activate.ps1
```

Instale as dependências:

```bash
pip install -r requirements.txt
```

Copie `env.example` para `.env` e preencha `SEFAZ_USUARIO` e `SEFAZ_SENHA` com o acesso autorizado ao ambiente pretendido. Não versione o arquivo preenchido.

Inicie a aplicação:

```bash
python run.py
```

Abra `http://localhost:8501`.

## Hospedagem

Para hospedar no Streamlit Community Cloud, confira as dependências de navegador, as permissões do portal e a exposição da interface. Configure `SEFAZ_USUARIO` e `SEFAZ_SENHA` no mecanismo de secrets do ambiente, sem colocá-los em código ou no README. Consulte a [documentação oficial de publicação do Streamlit](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app).

## Demonstração comercial

O [AH XML Fiscal](https://ah-automacoes-demo.vercel.app/xml-fiscal) apresenta um fluxo ilustrativo de solicitação, espera, download, extração, validação e encaminhamento. Usa dados fictícios e não executa este código nem acessa portais reais.

## Licença

MIT.
