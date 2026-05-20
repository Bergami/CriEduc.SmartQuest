# Trilha: SmartQuest Tech Debt - Dependencias

## Objetivo

Concentrar debitos tecnicos do projeto Python `D:/Git/CriEduc.SmartQuest` para permitir evolucao imediata da API .NET com risco controlado de integracao futura.

## Escopo

- Lockfile e reprodutibilidade
- Compatibilidade FastAPI/Pydantic
- Vulnerability gate no CI
- Hardening de dependencias Azure
- Matriz de runtime Python
- Rotina mensal de upgrades

## Issues desta trilha

| Issue | Status | Prompt | Descricao |
| ----- | ------ | ------ | --------- |
| SQ-DEP-00 | NAO INICIADO | [issue-sq-dep-00-epic-smartquest-dependency-debt.md](issue-sq-dep-00-epic-smartquest-dependency-debt.md) | Issue-mae para coordenar o pacote completo |
| SQ-DEP-01 | NAO INICIADO | [issue-sq-dep-01-lockfile-reproducible-build.md](issue-sq-dep-01-lockfile-reproducible-build.md) | Lockfile reproduzivel para CI/Docker |
| SQ-DEP-02 | NAO INICIADO | [issue-sq-dep-02-fastapi-pydantic-compatibility-plan.md](issue-sq-dep-02-fastapi-pydantic-compatibility-plan.md) | Plano de compatibilidade FastAPI/Pydantic |
| SQ-DEP-03 | NAO INICIADO | [issue-sq-dep-03-vulnerability-gate-ci.md](issue-sq-dep-03-vulnerability-gate-ci.md) | Gate de vulnerabilidades de dependencias |
| SQ-DEP-04 | NAO INICIADO | [issue-sq-dep-04-azure-dependencies-hardening.md](issue-sq-dep-04-azure-dependencies-hardening.md) | Revisao de SDKs Azure e versoes estaveis |
| SQ-DEP-05 | NAO INICIADO | [issue-sq-dep-05-python-runtime-matrix.md](issue-sq-dep-05-python-runtime-matrix.md) | Matriz de testes por versao de Python |
| SQ-DEP-06 | NAO INICIADO | [issue-sq-dep-06-monthly-upgrade-routine.md](issue-sq-dep-06-monthly-upgrade-routine.md) | Rotina mensal de atualizacao de dependencias |

## Ordem recomendada

1. SQ-DEP-01
2. SQ-DEP-03
3. SQ-DEP-02
4. SQ-DEP-04
5. SQ-DEP-05
6. SQ-DEP-06

## Criterio de conclusao

- Instalacao reproduzivel em dev/CI/Docker
- Scans de vulnerabilidade ativos no pipeline
- Stack Python em trilha suportada
- Processo continuo de manutencao documentado
