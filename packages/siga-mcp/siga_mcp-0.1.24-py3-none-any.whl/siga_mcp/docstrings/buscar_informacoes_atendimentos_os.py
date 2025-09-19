from textwrap import dedent


def docs() -> str:
    return dedent("""\
            Busca informações detalhadas de um atendimento de Ordem de Serviço (OS) específico.

            Esta função realiza uma consulta ao sistema SIGA através da API do AVA para obter
            todas as informações relacionadas a um atendimento de OS específico. É especialmente
            útil para consultar dados antes de realizar edições no atendimento.

            Funcionalidades:
            - Consulta dados completos de um atendimento OS pelo código
            - Retorna informações estruturadas em formato XML
            - Inclui tratamento de erros para requisições mal-sucedidas
            - Utiliza autenticação via API Key do AVA

            Endpoint utilizado:
            - URL: https://ava3.uniube.br/ava/api/atendimentosOs/buscarInfoAtendimentosOsSigaIA/
            - Método: POST
            - Autenticação: API Key (AVA_API_KEY)

            Estrutura do XML retornado:
            - Elemento raiz: <info_atendimentos_os>
            - Atributos do elemento raiz: atendimento (código do atendimento)
            - Atributos customizados: sistema="SIGA"
            - Contém todos os dados do atendimento retornados pela API

            Args:
                codigo_atendimento (int): Código único identificador do atendimento OS.
                                            Deve ser um número inteiro válido correspondente
                                            a um atendimento existente no sistema SIGA.

            Returns:
                str: XML bem formatado contendo as informações do atendimento OS.
                        Em caso de erro na requisição ou processamento, retorna a mensagem:
                        "Erro ao buscar as informações do atendimento."

            Raises:
                Exception: Captura qualquer exceção durante a requisição HTTP ou
                            processamento dos dados, retornando mensagem de erro amigável.

            Example:
                >>> resultado = await buscar_informacoes_atendimentos_os(12345)
                >>> print(resultado)
                <?xml version="1.0" ?>
                <info_atendimentos_os atendimento="12345" sistema="SIGA">
                    <campo1>valor1</campo1>
                    <campo2>valor2</campo2>
                    ...
                </info_atendimentos_os>

            Note:
                - Requer variável de ambiente AVA_API_KEY configurada
                - A função é assíncrona e deve ser chamada com await
                - Utiliza aiohttp para requisições HTTP assíncronas
                - O XML é formatado usando a classe XMLBuilder interna
            """)
