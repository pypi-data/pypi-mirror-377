from . import estados, grupos, obitos

from .estados import Estado
from .grupos import GruposCID10ObitosPorCausasExternas
from .obitos import TabNetObitos

__all__ = [
    "Estado",
    "GruposCID10ObitosPorCausasExternas",
    "TabNetObitos",
    "estados",
    "grupos",
    "obitos",
]
