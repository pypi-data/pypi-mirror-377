from enum import Enum

_nomes_estados = {
    1: "Acre",
    2: "Alagoas",
    3: "Amapá",
    4: "Amazonas",
    5: "Bahia",
    6: "Ceará",
    7: "Distrito Federal",
    8: "Espírito Santo",
    9: "Goiás",
    10: "Maranhão",
    11: "Mato Grosso",
    12: "Mato Grosso do Sul",
    13: "Minas Gerais",
    14: "Pará",
    15: "Paraíba",
    16: "Paraná",
    17: "Pernambuco",
    18: "Piauí",
    19: "Rio de Janeiro",
    20: "Rio Grande do Norte",
    21: "Rio Grande do Sul",
    22: "Rondônia",
    23: "Roraima",
    24: "Santa Catarina",
    25: "São Paulo",
    26: "Sergipe",
    27: "Tocantins",
}


class Estado(Enum):
    AC = 1
    AL = 2
    AP = 3
    AM = 4
    BA = 5
    CE = 6
    DF = 7
    ES = 8
    GO = 9
    MA = 10
    MT = 11
    MS = 12
    MG = 13
    PA = 14
    PB = 15
    PR = 16
    PE = 17
    PI = 18
    RJ = 19
    RN = 20
    RS = 21
    RO = 22
    RR = 23
    SC = 24
    SP = 25
    SE = 26
    TO = 27

    def get_nome(self) -> str:
        return _nomes_estados.get(self.value)

    def get_sigla(self) -> str:
        return self.name
