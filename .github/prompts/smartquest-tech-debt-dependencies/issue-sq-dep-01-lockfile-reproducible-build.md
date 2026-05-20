# Issue SQ-DEP-01: Lockfile Reproduzivel para Build

## Objetivo

Implementar lock de dependencias Python para instalacao deterministica em dev, CI e Docker.

## Tarefas

- Criar estrategia de dependencias de alto nivel e lockfile com hashes
- Ajustar Docker/CI para instalar a partir do lock
- Atualizar documentacao com fluxo oficial de install

## Criterios de Aceite

- [ ] Instalacao reproduzivel em ambientes locais e CI
- [ ] Build do container usa lockfile
- [ ] Testes existentes continuam passando

**Status**: Nao iniciado  
**Prioridade**: Alta  
**Estimativa**: 1-2 dias
