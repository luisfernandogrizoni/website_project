# ERP Restauração 

Este repositório contém a estrutura base de um ERP desenvolvido para a **Associação Restauração**. O foco do projeto foi substituir processos manuais e registros físicos por uma solução digital integrada, unificando a comunicação entre polos administrativos.

## Stack Tecnológica
- **Linguagem:** Python 3.12
- **Web Framework:** Flask (Blueprints para modularização)
- **ORM:** SQLAlchemy (Modelagem Relacional Complexa) 
- **Database:** Migração estratégica de MySQL para PostgreSQL 
- **Frontend:** Vanilla JavaScript, HTML5, CSS3 (Custom Properties) 

## Desafios de Negócio Resolvidos
1. **Unificação de Polos:** Sincronização de prontuários para eliminar a latência de dados entre unidades.
2. **Automação Financeira:** Digitalização de orçamentos e prestações de contas.
3. **Eficiência na Admissão:** Redução do tempo de cadastro manual de 1h para <5min por interno.

## Arquitetura do Projeto
O sistema foi desenhado seguindo padrões de **Eficiência Operacional e Governança de TI**, separando logicamente as camadas de API, Regras de Negócio e Templates.

## Nota sobre Segurança e Privacidade
Este repositório é uma versão de demonstração. Código sensível, chaves de API e dados reais da instituição foram omitidos ou protegidos via variáveis de ambiente (.env) para garantir a conformidade com a LGPD e o sigilo institucional.

## Como Executar
1. Instale as dependências: `pip install -r requirements.txt`
2. Configure o seu `.env` com a `DATABASE_URL`
3. Execute: `python main.py`
