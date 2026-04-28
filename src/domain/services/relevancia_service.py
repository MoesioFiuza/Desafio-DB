class RelevanciaService:
    """Service simples para score por ocorrencias de termo."""

    @staticmethod
    def score_termo(texto: str, termo: str) -> int:
        if not texto:
            return 0
        return texto.casefold().count(termo.casefold())
