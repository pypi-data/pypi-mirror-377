from pathlib import Path


class SpedError(Exception):
    pass


class ArquivoInvalido(SpedError):
    def __init__(self, arquivo: str) -> None:
        nome_arquivo = Path(arquivo).name
        self._message = f"o arquivo {nome_arquivo} não é um Sped FIscal válido."

    def __repr__(self) -> str:
        return self._message

    def __str__(self) -> str:
        return self._message


class TamanhoRegistroInvalido(SpedError):
    pass


class LinhaRegistroInvalida(SpedError):
    pass


class ValorCampoInvalido(SpedError):
    def __init__(self, campo: str, valor: str) -> None:
        self._campo = campo
        self._valor = valor
        self._message = f"A versao do arquivo SPED é {self._valor} e a aplicacoa está desatualizada. Contate o desenvolvedor e solicite a atualizacao."

    def __repr__(self) -> str:
        return self._message

    def __str__(self) -> str:
        return self._message
