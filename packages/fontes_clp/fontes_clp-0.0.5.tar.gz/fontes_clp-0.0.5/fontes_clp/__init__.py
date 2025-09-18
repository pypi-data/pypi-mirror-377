from importlib.metadata import version

try:
    __version__ = version("fontes_clp")
except:
    __version__ = "0.0.4"

from .tabnet import Estado, GruposCID10ObitosPorCausasExternas, TabNetObitos

__all__ = [
    "Estado",
    "GruposCID10ObitosPorCausasExternas",
    "TabNetObitos",
    "tabnet",
]
