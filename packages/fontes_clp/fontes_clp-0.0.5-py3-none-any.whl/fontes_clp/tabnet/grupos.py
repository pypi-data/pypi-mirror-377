from enum import Enum

_nomes_grupos_cid10_obitos_por_causas_externas = {
    1: "Pedestre traumatizado em um acidente de transporte",
    2: "Ciclista traumatizado em um acidente de transporte",
    3: "Motociclista traumat em um acidente de transporte",
    4: "Ocupante triciclo motorizado traumat acid transp",
    5: "Ocupante automóvel traumat acidente transporte",
    6: "Ocupante caminhonete traumat acidente transporte",
    7: "Ocupante veíc transp pesado traumat acid transp",
    8: "Ocupante ônibus traumat acidente de transporte",
    9: "Outros acidentes de transporte terrestre",
    10: "Acidentes de transporte por água",
    11: "Acidentes de transporte aéreo e espacial",
    12: "Outros acidentes de transporte e os não especif",
    13: "Quedas",
    14: "Exposição a forças mecânicas inanimadas",
    15: "Exposição a forças mecânicas animadas",
    16: "Afogamento e submersão acidentais",
    17: "Outros riscos acidentais à respiração",
    18: "Expos corr elétr, radiação e temp press extrem amb",
    19: "Exposição à fumaça, ao fogo e às chamas",
    20: "Contato com fonte de calor ou substâncias quentes",
    21: "Contato com animais e plantas venenosos",
    22: "Exposição às forças da natureza",
    23: "Envenenamento acidental e exposição subst nocivas",
    24: "Excesso de esforços, viagens e privações",
    25: "Exposição acidental a outr fatores e aos não espec",
    26: "Lesões autoprovocadas intencionalmente",
    27: "Agressões",
    28: "Eventos (fatos) cuja intenção é indeterminada",
    29: "Intervenções legais e operações de guerra",
    30: "Ef advers drog, medic e subst biológ finalid terap",
    31: "Acid ocorr pacientes prest cuid médicos e cirúrg",
    32: "Incid advers atos diagn terap assoc disposit médic",
    33: "Reaç anorm compl tard proc cirúrg méd s/menç acid",
    34: "Seqüelas causas externas de morbidade e mortalidad",
    35: "Fatores supl relac causas de morbid e mortalid COP",
}


class GruposCID10ObitosPorCausasExternas(Enum):
    # Agrupamentos
    ACIDENTES_TERRESTRES = range(1, 10)

    PEDESTRE_TRAUMATIZADO_EM_UM_ACIDENTE_DE_TRANSPORTE = 1
    CICLISTA_TRAUMATIZADO_EM_UM_ACIDENTE_DE_TRANSPORTE = 2
    MOTOCICLISTA_TRAUMAT_EM_UM_ACIDENTE_DE_TRANSPORTE = 3
    OCUPANTE_TRICICLO_MOTORIZADO_TRAUMAT_ACID_TRANSP = 4
    OCUPANTE_AUTOMOVEL_TRAUMAT_ACIDENTE_TRANSPORTE = 5
    OCUPANTE_CAMINHONETE_TRAUMAT_ACIDENTE_TRANSPORTE = 6
    OCUPANTE_VEIC_TRANSP_PESADO_TRAUMAT_ACID_TRANSP = 7
    OCUPANTE_ONIBUS_TRAUMAT_ACIDENTE_DE_TRANSPORTE = 8
    OUTROS_ACIDENTES_DE_TRANSPORTE_TERRESTRE = 9
    ACIDENTES_DE_TRANSPORTE_POR_AGUA = 10
    ACIDENTES_DE_TRANSPORTE_AEREO_E_ESPACIAL = 11
    OUTROS_ACIDENTES_DE_TRANSPORTE_E_OS_NAO_ESPECIF = 12
    QUEDAS = 13
    EXPOSICAO_A_FORCAS_MECANICAS_INANIMADAS = 14
    EXPOSICAO_A_FORCAS_MECANICAS_ANIMADAS = 15
    AFOGAMENTO_E_SUBMERSAO_ACIDENTAIS = 16
    OUTROS_RISCOS_ACIDENTAIS_A_RESPIRACAO = 17
    EXPOS_CORR_ELETR_RADIACAO_E_TEMP_PRESS_EXTREM_AMB = 18
    EXPOSICAO_A_FUMACA_AO_FOGO_E_AS_CHAMAS = 19
    CONTATO_COM_FONTE_DE_CALOR_OU_SUBSTANCIAS_QUENTES = 20
    CONTATO_COM_ANIMAIS_E_PLANTAS_VENENOSOS = 21
    EXPOSICAO_AS_FORCAS_DA_NATUREZA = 22
    ENVENENAMENTO_ACIDENTAL_E_EXPOSICAO_SUBST_NOCIVAS = 23
    EXCESSO_DE_ESFORCOS_VIAGENS_E_PRIVACOES = 24
    EXPOSICAO_ACIDENTAL_A_OUTR_FATORES_E_AOS_NAO_ESPEC = 25
    LESOES_AUTOPROVOCADAS_INTENCIONALMENTE = 26
    AGRESSOES = 27
    EVENTOS_FATOS_CUJA_INTENCAO_E_INDETERMINADA = 28
    INTERVENCOES_LEGAIS_E_OPERACOES_DE_GUERRA = 29
    EF_ADVERS_DROG_MEDIC_E_SUBST_BIOLOG_FINALID_TERAP = 30
    ACID_OCORR_PACIENTES_PREST_CUID_MEDICOS_E_CIRURG = 31
    INCID_ADVERS_ATOS_DIAGN_TERAP_ASSOC_DISPOSIT_MEDIC = 32
    REAC_ANORM_COMPL_TARD_PROC_CIRURG_MED_S_MENC_ACID = 33
    SEQUELAS_CAUSAS_EXTERNAS_DE_MORBIDADE_E_MORTALIDAD = 34
    FATORES_SUPL_RELAC_CAUSAS_DE_MORBID_E_MORTALID_COP = 35

    def get_nome(self) -> str:
        if self == self.ACIDENTES_TERRESTRES:
            return "Acidentes terrestres"

        return _nomes_grupos_cid10_obitos_por_causas_externas.get(self.value)

    def get_sigla(self) -> str:
        return self.name
