# Bibliotecas para Extração de Fontes do CLP

## TabNet Óbitos

```python
from tabnet.estados import Estado
from tabnet.obitos import TabNetObitos as TabNet
from tabnet.grupos import GruposCID10ObitosPorCausasExternas as GrupoCID10

# Dados são retornados como um DataFrame do Pandas
dados = TabNet(
  ano=2023,
  estado=Estado.RR,
  grupo=GrupoCID10.ACIDENTES_TERRESTRES,
).get_dados()

print(dados)
```
