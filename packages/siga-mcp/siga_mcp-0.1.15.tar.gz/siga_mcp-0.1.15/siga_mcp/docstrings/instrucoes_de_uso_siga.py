from textwrap import dedent


def docs() -> str:
    return dedent("""\
            **IMPORTANTE**
            Antes de chamar outra função, chame esta para obter as instruções de uso do SIGA.
            """)
