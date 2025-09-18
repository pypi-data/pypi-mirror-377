"""Este módulo guarda todas as funções do MCP visíveis para o Agente usar"""

from os import getenv
from typing import Literal, Sequence

import aiohttp
import ujson
from siga_mcp._types import (
    EquipeSistemasType,
    FiltrosOSType,
    OrigemAtendimentoAvulsoSistemasType,
    ProjetoType,
    SistemasType,
    TipoAtendimentoAvulsoSistemasType,
    TipoAtendimentosOSType,
    TiposAtendimentosOSType,
)
from siga_mcp.decorators import controlar_acesso_matricula, resolve_matricula
from siga_mcp.constants import (
    COLABORADORES_PROMPT,
    EQUIPE_TO_NUMBER,
    ORIGEM_TO_NUMBER,
    PROJETO_TO_NUMBER,
    SISTEMA_TO_NUMBER,
    SYSTEM_INSTRUCTIONS,
    TIPO_TO_NUMBER_ATENDIMENTO_AVULSO,
    TYPE_TO_NUMBER,
)
from siga_mcp.utils import converter_data_siga
from siga_mcp.xml_builder import XMLBuilder

async def instrucoes_de_uso_siga() -> str:
    return SYSTEM_INSTRUCTIONS

async def colaboradores_ativos_siga() -> str:
    return COLABORADORES_PROMPT


async def buscar_informacoes_atendimentos_os(codigo_atendimento: int) -> str:
    async with aiohttp.ClientSession(json_serialize=ujson.dumps) as session:
        async with session.post(
            "https://ava3.uniube.br/ava/api/atendimentosOs/buscarInfoAtendimentosOsSigaIA/",
            json={
                "atendimento": codigo_atendimento,
                "apiKey": getenv("AVA_API_KEY"),
            },
        ) as response:
            try:
                json = await response.json(content_type=None)
                retorno = XMLBuilder().build_xml(
                    data=json["result"],
                    root_element_name="info_atendimentos_os",
                    item_element_name="info_atendimentos_os",
                    root_attributes={
                        "atendimento": str(codigo_atendimento),
                    },
                    custom_attributes={"sistema": "SIGA"},
                )

                return retorno

            except Exception:
                return "Erro ao buscar as informações do atendimento."

@resolve_matricula
@controlar_acesso_matricula
async def buscar_pendencias_lancamentos_atendimentos(
    *,
    matricula: str | int | Literal["CURRENT_USER"] = "CURRENT_USER",
    dataIni: str,
    dataFim: str,
) -> str:
    async with aiohttp.ClientSession(json_serialize=ujson.dumps) as session:
        async with session.post(
            "https://ava3.uniube.br/ava/api/atendimentosAvulsos/buscarPendenciasRegistroAtendimentosSigaIA/",
            json={
                "matricula": matricula,
                "dataIni": converter_data_siga(dataIni),
                "dataFim": converter_data_siga(dataFim),
                "apiKey": getenv("AVA_API_KEY"),
            },
        ) as response:
            try:
                # Verifica se a requisição HTTP foi bem-sucedida (status 2xx)
                response.raise_for_status()

                # Converte a resposta para JSON, permitindo qualquer content-type
                data = await response.json(content_type=None)

                retorno = XMLBuilder().build_xml(
                    # Usa [] se 'result' não existir ou for None
                    data=data.get("result", []),
                    root_element_name="pendencias_lançamentos",
                    item_element_name="pendencias_lançamentos",
                    root_attributes={"matricula": str(matricula)},
                    custom_attributes={"sistema": "SIGA"},
                )

                return retorno

            except Exception:
                # Captura qualquer outro erro não previsto
                return "Erro ao consultar todas as pendências de registros SIGA do usuário."


@resolve_matricula
async def buscar_todas_os_usuario(
    *,
    matricula: str | Sequence[str] | Literal["CURRENT_USER"] | None = "CURRENT_USER",
    os: str | Sequence[str] | None = None,
    filtrar_por: Sequence[FiltrosOSType]
    | Literal["Todas OS em Aberto"]
    | str
    | None = None,
    data_inicio: str | None = None,
    data_fim: str | None = None,
) -> str:
    if not matricula and not os:
        return "Erro: É necessário informar pelo menos a matrícula ou o código da OS para realizar a consulta."

    if filtrar_por == "Todas OS em Aberto":
        filtrar_por = [
            "Pendente-Atendimento",
            "Em Teste",
            "Pendente-Teste",
            "Em Atendimento",
            "Em Implantação",
            "Pendente-Liberação",
            "Não Planejada",
            "Pendente-Sist. Administrativos",
            "Pendente-AVA",
            "Pendente-Consultoria",
            "Solicitação em Aprovação",
            "Pendente-Aprovação",
            "Pendente-Sist. Acadêmicos",
            "Pendente-Marketing",
            "Pendente-Equipe Manutenção",
            "Pendente-Equipe Infraestrutura",
            "Pendente-Atualização de Versão",
            "Pendente-Help-Desk",
            "Pendente-Fornecedor",
            "Pendente-Usuário",
        ]

    async with aiohttp.ClientSession(json_serialize=ujson.dumps) as session:
        async with session.post(
            "https://ava3.uniube.br/ava/api/os/buscarTodasOsPorMatriculaSigaIA/",
            json={
                "descricaoStatusOs": filtrar_por or "",  # Array ou string puro
                "matricula": matricula or "",  # Array ou string puro
                "codOs": os or "",  # Array ou string puro
                "dataIni": converter_data_siga(data_inicio) if data_inicio else "",
                "dataFim": converter_data_siga(data_fim) if data_fim else "",
                "apiKey": getenv("AVA_API_KEY"),
            },
        ) as response:
            try:
                # Verifica se a requisição HTTP foi bem-sucedida (status 2xx)
                # response.raise_for_status()

                data = await response.json(content_type=None)
                retorno = XMLBuilder().build_xml(
                    data=data["result"],
                    root_element_name="ordens_servico",
                    item_element_name="ordem_servico",
                    root_attributes={"matricula": str(matricula)},
                    custom_attributes={"sistema": "SIGA"},
                )

                return retorno

            except Exception as e:
                # Captura qualquer outro erro não previsto
                return f"Erro ao consultar dados da(s) OS. {e} Matrícula: {matricula}"


async def editar_atendimentos_os(
    codigo_atendimento: int,
    codigo_os: int,
    data_inicio: str,
    codigo_analista: int,
    descricao_atendimento: str,
    tipo_atendimento: TiposAtendimentosOSType = "Implementação",
    data_fim: str | None = None,
    primeiro_atendimento: bool = False,
    apresenta_solucao: bool = False,
) -> str:
    if data_inicio:
        data_inicio = converter_data_siga(data_inicio, manter_horas=True)

    if data_fim:
        data_fim = converter_data_siga(data_fim, manter_horas=True)

    # Busca o tipo correto na constante TYPE_TO_NUMBER ignorando maiúsculas/minúsculas
    tipo_normalizado = next(
        # Expressão geradora que itera sobre todas as chaves do dicionário TYPE_TO_NUMBER
        (
            key
            for key in TYPE_TO_NUMBER.keys()
            # Compara a chave atual em minúsculas com o tipo recebido em minúsculas
            if str(key).lower() == str(tipo_atendimento).lower()
        ),
        # Se nenhuma correspondência for encontrada, retorna None como valor padrão
        None,
    )

    # Verifica se foi encontrado um tipo válido após a busca case-insensitive
    if tipo_normalizado is None:
        # Retorna XML de erro em vez de levantar exceção
        return XMLBuilder().build_xml(
            data=[
                {
                    "status": "erro",
                    "tipo_erro": "tipo_invalido",
                    "tipo_informado": tipo_atendimento,
                    "mensagem": f"Tipo '{tipo_atendimento}' não encontrado na constante TYPE_TO_NUMBER",
                    "tipos_validos": list(TYPE_TO_NUMBER.keys()),
                }
            ],
            root_element_name="erro_validacao",
            item_element_name="erro",
            root_attributes={"sistema": "SIGA", "funcao": "editar_atendimentos_os"},
            custom_attributes={"sistema": "SIGA"},
        )

    tipo_final = TYPE_TO_NUMBER[tipo_normalizado]

    try:
        async with aiohttp.ClientSession(json_serialize=ujson.dumps) as session:
            async with session.post(
                "https://ava3.uniube.br/ava/api/atendimentosOs/updateAtendimentosOsSigaIA/",
                json={
                    "atendimento": codigo_atendimento,
                    "os": codigo_os,
                    "dataIni": data_inicio,
                    "analista": codigo_analista,
                    "descricao": descricao_atendimento,
                    "tipo": tipo_final,
                    "dataFim": data_fim,
                    "primeiroAtendimento": primeiro_atendimento,
                    "apresentaSolucao": apresenta_solucao,
                    "apiKey": getenv("AVA_API_KEY"),
                },
            ) as response:
                json_response = await response.json(content_type=None)
                result_data = json_response.get("result")

                # Trata a resposta
                if result_data is None:
                    data_final = [
                        {
                            "status": "erro",
                            "mensagem": "Não foi possível editar o atendimento. Verifique as informações digitadas.",
                        }
                    ]
                elif result_data == 1:
                    data_final = [
                        {
                            "status": "sucesso",
                            "mensagem": "Atendimento editado com sucesso!",
                        }
                    ]
                else:
                    data_final = [
                        {
                            "status": "erro",
                            "mensagem": "Erro ao editar o atendimento. Tente novamente.",
                        }
                    ]

                # Adiciona os root_attributes
                return XMLBuilder().build_xml(
                    data=data_final,
                    root_element_name="ordens_servico",
                    item_element_name="ordem_servico",
                    root_attributes={
                        "os": str(codigo_os),
                        "dataIni": str(data_inicio),
                        "analista": str(codigo_analista),
                        "descricao": str(descricao_atendimento),
                        "tipo": str(tipo_normalizado),
                        "dataFim": str(data_fim),
                        "primeiroAtendimento": str(primeiro_atendimento),
                        "apresentaSolucao": str(apresenta_solucao),
                    },
                    custom_attributes={"sistema": "SIGA"},
                )

    except Exception as e:
        return XMLBuilder().build_xml(
            data=[
                {
                    "status": "erro",
                    "mensagem": f"Erro interno: {str(e)}. Tente novamente mais tarde.",
                }
            ],
            root_element_name="resultado",
            item_element_name="item",
            custom_attributes={"sistema": "SIGA"},
        )


async def excluir_atendimentos_os(
    codigo_atendimento: int,
) -> str:
    try:
        async with aiohttp.ClientSession(json_serialize=ujson.dumps) as session:
            async with session.post(
                "https://ava3.uniube.br/ava/api/atendimentosOs/excluiAtendimentosOsSigaIA/",
                json={
                    "atendimento": codigo_atendimento,
                    "apiKey": getenv("AVA_API_KEY"),
                },
            ) as response:
                json_response = await response.json(content_type=None)
                result_data = json_response.get("result")

                # Trata a resposta
                if result_data is None:
                    data_final = [
                        {
                            "status": "erro",
                            "mensagem": "Não foi possível excluir o atendimento. Verifique as informações digitadas.",
                        }
                    ]
                elif result_data == 1:
                    data_final = [
                        {
                            "status": "sucesso",
                            "mensagem": "Atendimento excluído com sucesso!",
                        }
                    ]
                else:
                    data_final = [
                        {
                            "status": "erro",
                            "mensagem": "Erro ao excluir o atendimento. Tente novamente.",
                        }
                    ]

                # Adiciona os root_attributes
                return XMLBuilder().build_xml(
                    data=data_final,
                    root_element_name="exclusões_atendimento_os",
                    item_element_name="exclusão",
                    root_attributes={
                        "atendimento": str(codigo_atendimento),
                    },
                    custom_attributes={"sistema": "SIGA"},
                )

    except Exception as e:
        return XMLBuilder().build_xml(
            data=[
                {
                    "status": "erro",
                    "mensagem": f"Erro interno: {str(e)}. Tente novamente mais tarde.",
                }
            ],
            root_element_name="resultado",
            item_element_name="item",
            custom_attributes={"sistema": "SIGA"},
        )


async def inserir_atendimentos_os(
    codigo_os: int,
    data_inicio: str,
    codigo_analista: int,
    descricao_atendimento: str,
    tipo: TipoAtendimentosOSType = "Implementação",
    data_fim: str | None = None,
    primeiro_atendimento: bool = False,
    apresenta_solucao: bool = False,
) -> str:
    if data_inicio:
        data_inicio = converter_data_siga(data_inicio, manter_horas=True)

    if data_fim:
        data_fim = converter_data_siga(data_fim, manter_horas=True)

    # Busca o tipo correto na constante TYPE_TO_NUMBER ignorando maiúsculas/minúsculas
    tipo_normalizado = next(
        # Expressão geradora que itera sobre todas as chaves do dicionário TYPE_TO_NUMBER
        (
            key
            for key in TYPE_TO_NUMBER.keys()
            # Compara a chave atual em minúsculas com o tipo recebido em minúsculas
            if str(key).lower() == str(tipo).lower()
        ),
        # Se nenhuma correspondência for encontrada, retorna None como valor padrão
        None,
    )

    # Verifica se foi encontrado um tipo válido após a busca case-insensitive
    if tipo_normalizado is None:
        # Retorna XML de erro em vez de levantar exceção
        return XMLBuilder().build_xml(
            data=[
                {
                    "status": "erro",
                    "tipo_erro": "tipo_invalido",
                    "tipo_informado": tipo,
                    "mensagem": f"Tipo '{tipo}' não encontrado na constante TYPE_TO_NUMBER",
                    "tipos_validos": list(TYPE_TO_NUMBER.keys()),
                }
            ],
            root_element_name="erro_validacao",
            item_element_name="erro",
            root_attributes={"sistema": "SIGA", "funcao": "inserir_atendimentos_os"},
            custom_attributes={"sistema": "SIGA"},
        )

    tipo_final = TYPE_TO_NUMBER[tipo_normalizado]

    try:
        async with aiohttp.ClientSession(json_serialize=ujson.dumps) as session:
            async with session.post(
                "https://ava3.uniube.br/ava/api/atendimentosOs/inserirAtendimentosOsSigaIA/",
                json={
                    "os": codigo_os,
                    "dataIni": data_inicio,
                    "analista": codigo_analista,
                    "descricao": descricao_atendimento,
                    "tipo": tipo_final,
                    "dataFim": data_fim,
                    "primeiroAtendimento": primeiro_atendimento,
                    "apresentaSolucao": apresenta_solucao,
                    "apiKey": getenv("AVA_API_KEY"),
                },
            ) as response:
                json_response = await response.json(content_type=None)
                result_data = json_response.get("result")

                # Trata a resposta
                if result_data is None:
                    data_final = [
                        {
                            "status": "erro",
                            "mensagem": "Não foi possível salvar o atendimento. Verifique as informações digitadas.",
                        }
                    ]
                elif result_data == 1:
                    data_final = [
                        {
                            "status": "sucesso",
                            "mensagem": "Atendimento cadastrado com sucesso!",
                        }
                    ]
                else:
                    data_final = [
                        {
                            "status": "erro",
                            "mensagem": "Erro ao gravar o atendimento. Tente novamente.",
                        }
                    ]

                # Adiciona os root_attributes
                return XMLBuilder().build_xml(
                    data=data_final,
                    root_element_name="ordens_servico",
                    item_element_name="ordem_servico",
                    root_attributes={
                        "os": str(codigo_os),
                        "dataIni": str(data_inicio),
                        "analista": str(codigo_analista),
                        "descricao": str(descricao_atendimento),
                        "tipo": str(tipo_normalizado),
                        "dataFim": str(data_fim),
                        "primeiroAtendimento": str(primeiro_atendimento),
                        "apresentaSolucao": str(apresenta_solucao),
                    },
                    custom_attributes={"sistema": "SIGA"},
                )

    except Exception as e:
        return XMLBuilder().build_xml(
            data=[
                {
                    "status": "erro",
                    "mensagem": f"Erro interno: {str(e)}. Tente novamente mais tarde.",
                }
            ],
            root_element_name="resultado",
            item_element_name="item",
            custom_attributes={"sistema": "SIGA"},
        )


@resolve_matricula
async def listar_atendimentos_avulsos(
    *,
    matricula: str | int | Literal["CURRENT_USER"] = "CURRENT_USER",
    data_inicio: str,
    data_fim: str,
) -> str:
    if data_inicio:
        data_inicio = converter_data_siga(data_inicio)

    if data_fim:
        data_fim = converter_data_siga(data_fim)

    async with aiohttp.ClientSession(json_serialize=ujson.dumps) as session:
        async with session.post(
            "https://ava3.uniube.br/ava/api/atendimentosAvulsos/buscarAtendimentosAvulsosSigaIA/",
            json={
                "matricula": matricula,
                "dataIni": data_inicio,
                "dataFim": data_fim,
                "apiKey": getenv("AVA_API_KEY"),
            },
        ) as response:
            try:
                json = await response.json(content_type=None)
                retorno = XMLBuilder().build_xml(
                    data=json["result"],
                    root_element_name="atendimentos_avulsos",
                    item_element_name="atendimentos_avulsos",
                    root_attributes={
                        "matricula": str(matricula),
                    },
                    custom_attributes={"sistema": "SIGA"},
                )

                return retorno

            except Exception:
                return "Erro ao listar atendimentos avulsos."


@resolve_matricula
@controlar_acesso_matricula
async def listar_atendimentos_os(
    matricula: str | int | Literal["CURRENT_USER"] = "CURRENT_USER",
    codigo_os: str | int | None = None,
    data_inicio: str | None = None,
    data_fim: str | None = None,
) -> str:
    async with aiohttp.ClientSession(json_serialize=ujson.dumps) as session:
        async with session.post(
            "https://ava3.uniube.br/ava/api/atendimentosOs/buscarAtendimentosOsSigaIA/",
            json={
                "matricula": str(matricula),
                "os": str(codigo_os) if codigo_os else "",
                "dataIni": converter_data_siga(data_inicio) if data_inicio else "",
                "dataFim": converter_data_siga(data_fim) if data_fim else "",
                "apiKey": getenv("AVA_API_KEY"),
            },
        ) as response:
            try:
                json = await response.json(content_type=None)
                retorno = XMLBuilder().build_xml(
                    data=json["result"],
                    root_element_name="atendimentos_os",
                    item_element_name="atendimentos_os",
                    root_attributes={
                        "matricula": str(matricula),
                        "os": str(codigo_os) if codigo_os else "",
                        "dataIni": str(data_inicio) if data_inicio else "",
                        "dataFim": str(data_fim) if data_fim else "",
                    },
                    custom_attributes={"sistema": "SIGA"},
                )

                return retorno

            except Exception:
                return "Erro ao listar atendimentos OS."


@resolve_matricula
@controlar_acesso_matricula
async def listar_horas_trabalhadas(
    *,
    matricula: str | int | Literal["CURRENT_USER"] = "CURRENT_USER",
    data_inicio: str,
    data_fim: str,
) -> str:
    async with aiohttp.ClientSession(json_serialize=ujson.dumps) as session:
        async with session.post(
            "https://ava3.uniube.br/ava/api/atendimentosAvulsos/buscarTotalHorasTrabalhadasSigaIA/",
            json={
                "matricula": matricula,
                "dataIni": converter_data_siga(data_inicio) if data_inicio else "",
                "dataFim": converter_data_siga(data_fim) if data_fim else "",
                "apiKey": getenv("AVA_API_KEY"),
            },
        ) as response:
            try:
                json = await response.json(content_type=None)
                resultado = json["result"]

                retorno = XMLBuilder().build_xml(
                    data=resultado,
                    root_element_name="atendimentos_avulsos",
                    item_element_name="atendimentos_avulsos",
                    root_attributes={
                        "matricula": str(matricula),
                    },
                    custom_attributes={"sistema": "SIGA"},
                )

                return retorno

            except Exception:
                return "Erro ao listar horas trabalhadas."


async def inserir_atendimento_avulso_sistemas(
    data_inicio: str,
    data_fim: str,
    matricula_solicitante: str | Literal["CURRENT_USER"],
    descricao_atendimento: str,
    codigo_analista: str | Literal["CURRENT_USER"] = "CURRENT_USER",
    tipo: TipoAtendimentoAvulsoSistemasType = "Atividade Interna",
    origem: OrigemAtendimentoAvulsoSistemasType = "Teams",
    sistema: SistemasType = "Sistemas AVA",
    equipe: EquipeSistemasType = "Equipe AVA",
    projeto: ProjetoType = "Operação AVA",
) -> str:
    if data_inicio:
        data_inicio = converter_data_siga(data_inicio, manter_horas=True)

    if data_fim:
        data_fim = converter_data_siga(data_fim, manter_horas=True)

    # CRIANDO NORMALIZAÇÃO DAS LITERAIS

    # NORMALIZANDO LITERAL "TIPO"

    # Busca o tipo correto na constante TIPO_TO_NUMBER_ATENDIMENTO_AVULSO ignorando maiúsculas/minúsculas
    tipo_normalizado = next(
        # Expressão geradora que itera sobre todas as chaves do dicionário TIPO_TO_NUMBER_ATENDIMENTO_AVULSO
        (
            key
            for key in TIPO_TO_NUMBER_ATENDIMENTO_AVULSO.keys()
            # Compara a chave atual em minúsculas com o tipo recebido em minúsculas
            if str(key).lower() == str(tipo).lower()
        ),
        # Se nenhuma correspondência for encontrada, retorna None como valor padrão
        None,
    )

    # Verifica se foi encontrado um tipo válido após a busca case-insensitive
    if tipo_normalizado is None:
        # Retorna XML de erro em vez de levantar exceção
        return XMLBuilder().build_xml(
            data=[
                {
                    "status": "erro",
                    "tipo_erro": "tipo_invalido",
                    "tipo_informado": tipo,
                    "mensagem": f"Tipo '{tipo}' não encontrado na constante TIPO_TO_NUMBER_ATENDIMENTO_AVULSO",
                    "tipos_validos": list(TIPO_TO_NUMBER_ATENDIMENTO_AVULSO.keys()),
                }
            ],
            root_element_name="erro_validacao",
            item_element_name="erro",
            root_attributes={
                "sistema": "SIGA",
                "funcao": "inserir_atendimento_avulso_sistemas",
            },
            custom_attributes={"sistema": "SIGA"},
        )

    tipo_final = TIPO_TO_NUMBER_ATENDIMENTO_AVULSO[tipo_normalizado]

    # Busca a origem correta na constante ORIGEM_TO_NUMBER ignorando maiúsculas/minúsculas
    origem_normalizada = next(
        # Expressão geradora que itera sobre todas as chaves do dicionário ORIGEM_TO_NUMBER
        (
            key
            for key in ORIGEM_TO_NUMBER.keys()
            # Compara a chave atual em minúsculas com a origem recebida em minúsculas
            if str(key).lower() == str(origem).lower()
        ),
        # Se nenhuma correspondência for encontrada, retorna None como valor padrão
        None,
    )

    # Verifica se foi encontrada uma origem válida após a busca case-insensitive
    if origem_normalizada is None:
        # Retorna XML de erro em vez de levantar exceção
        return XMLBuilder().build_xml(
            data=[
                {
                    "status": "erro",
                    "tipo_erro": "origem_invalida",
                    "origem_informada": origem,
                    "mensagem": f"Origem '{origem}' não encontrada na constante ORIGEM_TO_NUMBER",
                    "origens_validas": list(ORIGEM_TO_NUMBER.keys()),
                }
            ],
            root_element_name="erro_validacao",
            item_element_name="erro",
            root_attributes={
                "sistema": "SIGA",
                "funcao": "inserir_atendimento_avulso_sistemas",
            },
            custom_attributes={"sistema": "SIGA"},
        )

    origem_final = ORIGEM_TO_NUMBER[origem_normalizada]

    # Busca o sistema correto na constante SISTEMA_TO_NUMBER ignorando maiúsculas/minúsculas
    sistema_normalizado = next(
        # Expressão geradora que itera sobre todas as chaves do dicionário SISTEMA_TO_NUMBER
        (
            key
            for key in SISTEMA_TO_NUMBER.keys()
            # Compara a chave atual em minúsculas com o sistema recebido em minúsculas
            if str(key).lower() == str(sistema).lower()
        ),
        # Se nenhuma correspondência for encontrada, retorna None como valor padrão
        None,
    )

    # Verifica se foi encontrado um sistema válido após a busca case-insensitive
    if sistema_normalizado is None:
        # Retorna XML de erro em vez de levantar exceção
        return XMLBuilder().build_xml(
            data=[
                {
                    "status": "erro",
                    "tipo_erro": "sistema_invalido",
                    "sistema_informado": sistema,
                    "mensagem": f"Sistema '{sistema}' não encontrado na constante SISTEMA_TO_NUMBER",
                    "sistemas_validos": list(SISTEMA_TO_NUMBER.keys()),
                }
            ],
            root_element_name="erro_validacao",
            item_element_name="erro",
            root_attributes={
                "sistema": "SIGA",
                "funcao": "inserir_atendimento_avulso_sistemas",
            },
            custom_attributes={"sistema": "SIGA"},
        )

    sistema_final = SISTEMA_TO_NUMBER[sistema_normalizado]

    # Busca a equipe correta na constante EQUIPE_TO_NUMBER ignorando maiúsculas/minúsculas
    equipe_normalizada = next(
        # Expressão geradora que itera sobre todas as chaves do dicionário EQUIPE_TO_NUMBER
        (
            key
            for key in EQUIPE_TO_NUMBER.keys()
            # Compara a chave atual em minúsculas com a equipe recebida em minúsculas
            if str(key).lower() == str(equipe).lower()
        ),
        # Se nenhuma correspondência for encontrada, retorna None como valor padrão
        None,
    )

    # Verifica se foi encontrada uma equipe válida após a busca case-insensitive
    if equipe_normalizada is None:
        # Retorna XML de erro em vez de levantar exceção
        return XMLBuilder().build_xml(
            data=[
                {
                    "status": "erro",
                    "tipo_erro": "equipe_invalida",
                    "equipe_informada": equipe,
                    "mensagem": f"Equipe '{equipe}' não encontrada na constante EQUIPE_TO_NUMBER",
                    "equipes_validas": list(EQUIPE_TO_NUMBER.keys()),
                }
            ],
            root_element_name="erro_validacao",
            item_element_name="erro",
            root_attributes={
                "sistema": "SIGA",
                "funcao": "inserir_atendimento_avulso_sistemas",
            },
            custom_attributes={"sistema": "SIGA"},
        )

    equipe_final = EQUIPE_TO_NUMBER[equipe_normalizada]

    # Busca o projeto correto na constante PROJETO_TO_NUMBER ignorando maiúsculas/minúsculas
    projeto_normalizado = next(
        # Expressão geradora que itera sobre todas as chaves do dicionário PROJETO_TO_NUMBER
        (
            key
            for key in PROJETO_TO_NUMBER.keys()
            # Compara a chave atual em minúsculas com o projeto recebido em minúsculas
            if str(key).lower() == str(projeto).lower()
        ),
        # Se nenhuma correspondência for encontrada, retorna None como valor padrão
        None,
    )

    # Verifica se foi encontrado um projeto válido após a busca case-insensitive
    if projeto_normalizado is None:
        # Retorna XML de erro em vez de levantar exceção
        return XMLBuilder().build_xml(
            data=[
                {
                    "status": "erro",
                    "tipo_erro": "projeto_invalido",
                    "projeto_informado": projeto,
                    "mensagem": f"Projeto '{projeto}' não encontrado na constante PROJETO_TO_NUMBER",
                    "projetos_validos": list(PROJETO_TO_NUMBER.keys()),
                }
            ],
            root_element_name="erro_validacao",
            item_element_name="erro",
            root_attributes={
                "sistema": "SIGA",
                "funcao": "inserir_atendimento_avulso_sistemas",
            },
            custom_attributes={"sistema": "SIGA"},
        )

    projeto_final = PROJETO_TO_NUMBER[projeto_normalizado]

    # FUNÇÃO PARA GRAVAR INFORMAÇÕES
    try:
        async with aiohttp.ClientSession(json_serialize=ujson.dumps) as session:
            async with session.post(
                "https://ava3.uniube.br/ava/api/atendimentosAvulsos/inserirAtendimentoAvulsoSigaIA/",
                # "https://9f7a79af77d0.ngrok-free.app/ava/api/atendimentosAvulsos/inserirAtendimentoAvulsoSigaIA/",
                json={
                    "apiKey": "92a61a8a-395e-40f9-abe1-7d172ce79df4",
                    "dataIni": data_inicio,
                    "dataFim": data_fim,
                    "matSolicitante": matricula_solicitante,
                    "tipo": tipo_final,
                    "descricao": descricao_atendimento,
                    "origem": origem_final,
                    "area": 1,
                    "equipe": equipe_final,
                    "analista": codigo_analista,
                    "projeto": projeto_final,
                    "sistema": sistema_final,
                    "nomeSolicitante": "",
                    "centroCusto": "",
                    "setor": "",
                    "matGestor": "",
                    "tempoGasto": "",
                    "campus": "",
                    "categoria": "",
                    "plaqueta": "",
                    "ramal": "",
                },
            ) as response:
                json_response = await response.json(content_type=None)
                result_data = json_response.get("result")

                # Trata a resposta
                if result_data is None:
                    data_final = [
                        {
                            "status": "erro",
                            "mensagem": "Não foi possível salvar o atendimento avulso. Verifique as informações digitadas.",
                        }
                    ]
                elif result_data == 1:
                    data_final = [
                        {
                            "status": "sucesso",
                            "mensagem": "Atendimento avulso cadastrado com sucesso!",
                        }
                    ]
                else:
                    data_final = [
                        {
                            "status": "erro",
                            "mensagem": "Erro ao gravar o atendimento avulso. Tente novamente.",
                        }
                    ]

                # Adiciona os root_attributes
                return XMLBuilder().build_xml(
                    data=data_final,
                    root_element_name="atendimentos_avulsos",
                    item_element_name="atendimento_avulso",
                    root_attributes={
                        "dataIni": str(data_inicio),
                        "dataFim": str(data_fim),
                        "matSolicitante": str(matricula_solicitante),
                        "tipo": str(tipo_final),
                        "descricao": str(descricao_atendimento),
                        "origem": str(origem_final),
                        "equipe": str(equipe_final),
                        "analista": str(codigo_analista),
                        "projeto": str(projeto_final),
                        "sistema": str(sistema_final),
                    },
                    custom_attributes={"sistema": "SIGA"},
                )

    except Exception as e:
        return XMLBuilder().build_xml(
            data=[
                {
                    "status": "erro",
                    "mensagem": f"Erro interno: {str(e)}. Tente novamente mais tarde.",
                }
            ],
            root_element_name="resultado",
            item_element_name="item",
            custom_attributes={"sistema": "SIGA"},
        )


async def editar_atendimento_avulso_sistemas(
    codigo_atendimento: int,
    data_inicio: str,
    data_fim: str,
    matricula_solicitante: str | Literal["CURRENT_USER"],
    descricao_atendimento: str,
    codigo_analista: str | Literal["CURRENT_USER"] = "CURRENT_USER",
    tipo: TipoAtendimentoAvulsoSistemasType = "Atividade Interna",
    origem: OrigemAtendimentoAvulsoSistemasType = "Teams",
    sistema: SistemasType = "Sistemas AVA",
    equipe: EquipeSistemasType = "Equipe AVA",
    projeto: ProjetoType = "Operação AVA",
) -> str:
    if data_inicio:
        data_inicio = converter_data_siga(data_inicio, manter_horas=True)

    if data_fim:
        data_fim = converter_data_siga(data_fim, manter_horas=True)

    # CRIANDO NORMALIZAÇÃO DAS LITERAIS

    # NORMALIZANDO LITERAL "TIPO"

    # Busca o tipo correto na constante TIPO_TO_NUMBER_ATENDIMENTO_AVULSO ignorando maiúsculas/minúsculas
    tipo_normalizado = next(
        # Expressão geradora que itera sobre todas as chaves do dicionário TIPO_TO_NUMBER_ATENDIMENTO_AVULSO
        (
            key
            for key in TIPO_TO_NUMBER_ATENDIMENTO_AVULSO.keys()
            # Compara a chave atual em minúsculas com o tipo recebido em minúsculas
            if str(key).lower() == str(tipo).lower()
        ),
        # Se nenhuma correspondência for encontrada, retorna None como valor padrão
        None,
    )

    # Verifica se foi encontrado um tipo válido após a busca case-insensitive
    if tipo_normalizado is None:
        # Retorna XML de erro em vez de levantar exceção
        return XMLBuilder().build_xml(
            data=[
                {
                    "status": "erro",
                    "tipo_erro": "tipo_invalido",
                    "tipo_informado": tipo,
                    "mensagem": f"Tipo '{tipo}' não encontrado na constante TIPO_TO_NUMBER_ATENDIMENTO_AVULSO",
                    "tipos_validos": list(TIPO_TO_NUMBER_ATENDIMENTO_AVULSO.keys()),
                }
            ],
            root_element_name="erro_validacao",
            item_element_name="erro",
            root_attributes={
                "sistema": "SIGA",
                "funcao": "editar_atendimento_avulso_sistemas",
            },
            custom_attributes={"sistema": "SIGA"},
        )

    tipo_final = TIPO_TO_NUMBER_ATENDIMENTO_AVULSO[tipo_normalizado]

    # Busca a origem correta na constante ORIGEM_TO_NUMBER ignorando maiúsculas/minúsculas
    origem_normalizada = next(
        # Expressão geradora que itera sobre todas as chaves do dicionário ORIGEM_TO_NUMBER
        (
            key
            for key in ORIGEM_TO_NUMBER.keys()
            # Compara a chave atual em minúsculas com a origem recebida em minúsculas
            if str(key).lower() == str(origem).lower()
        ),
        # Se nenhuma correspondência for encontrada, retorna None como valor padrão
        None,
    )

    # Verifica se foi encontrada uma origem válida após a busca case-insensitive
    if origem_normalizada is None:
        # Retorna XML de erro em vez de levantar exceção
        return XMLBuilder().build_xml(
            data=[
                {
                    "status": "erro",
                    "tipo_erro": "origem_invalida",
                    "origem_informada": origem,
                    "mensagem": f"Origem '{origem}' não encontrada na constante ORIGEM_TO_NUMBER",
                    "origens_validas": list(ORIGEM_TO_NUMBER.keys()),
                }
            ],
            root_element_name="erro_validacao",
            item_element_name="erro",
            root_attributes={
                "sistema": "SIGA",
                "funcao": "editar_atendimento_avulso_sistemas",
            },
            custom_attributes={"sistema": "SIGA"},
        )

    origem_final = ORIGEM_TO_NUMBER[origem_normalizada]

    # Busca o sistema correto na constante SISTEMA_TO_NUMBER ignorando maiúsculas/minúsculas
    sistema_normalizado = next(
        # Expressão geradora que itera sobre todas as chaves do dicionário SISTEMA_TO_NUMBER
        (
            key
            for key in SISTEMA_TO_NUMBER.keys()
            # Compara a chave atual em minúsculas com o sistema recebido em minúsculas
            if str(key).lower() == str(sistema).lower()
        ),
        # Se nenhuma correspondência for encontrada, retorna None como valor padrão
        None,
    )

    # Verifica se foi encontrado um sistema válido após a busca case-insensitive
    if sistema_normalizado is None:
        # Retorna XML de erro em vez de levantar exceção
        return XMLBuilder().build_xml(
            data=[
                {
                    "status": "erro",
                    "tipo_erro": "sistema_invalido",
                    "sistema_informado": sistema,
                    "mensagem": f"Sistema '{sistema}' não encontrado na constante SISTEMA_TO_NUMBER",
                    "sistemas_validos": list(SISTEMA_TO_NUMBER.keys()),
                }
            ],
            root_element_name="erro_validacao",
            item_element_name="erro",
            root_attributes={
                "sistema": "SIGA",
                "funcao": "editar_atendimento_avulso_sistemas",
            },
            custom_attributes={"sistema": "SIGA"},
        )

    sistema_final = SISTEMA_TO_NUMBER[sistema_normalizado]

    # Busca a equipe correta na constante EQUIPE_TO_NUMBER ignorando maiúsculas/minúsculas
    equipe_normalizada = next(
        # Expressão geradora que itera sobre todas as chaves do dicionário EQUIPE_TO_NUMBER
        (
            key
            for key in EQUIPE_TO_NUMBER.keys()
            # Compara a chave atual em minúsculas com a equipe recebida em minúsculas
            if str(key).lower() == str(equipe).lower()
        ),
        # Se nenhuma correspondência for encontrada, retorna None como valor padrão
        None,
    )

    # Verifica se foi encontrada uma equipe válida após a busca case-insensitive
    if equipe_normalizada is None:
        # Retorna XML de erro em vez de levantar exceção
        return XMLBuilder().build_xml(
            data=[
                {
                    "status": "erro",
                    "tipo_erro": "equipe_invalida",
                    "equipe_informada": equipe,
                    "mensagem": f"Equipe '{equipe}' não encontrada na constante EQUIPE_TO_NUMBER",
                    "equipes_validas": list(EQUIPE_TO_NUMBER.keys()),
                }
            ],
            root_element_name="erro_validacao",
            item_element_name="erro",
            root_attributes={
                "sistema": "SIGA",
                "funcao": "editar_atendimento_avulso_sistemas",
            },
            custom_attributes={"sistema": "SIGA"},
        )

    equipe_final = EQUIPE_TO_NUMBER[equipe_normalizada]

    # Busca o projeto correto na constante PROJETO_TO_NUMBER ignorando maiúsculas/minúsculas
    projeto_normalizado = next(
        # Expressão geradora que itera sobre todas as chaves do dicionário PROJETO_TO_NUMBER
        (
            key
            for key in PROJETO_TO_NUMBER.keys()
            # Compara a chave atual em minúsculas com o projeto recebido em minúsculas
            if str(key).lower() == str(projeto).lower()
        ),
        # Se nenhuma correspondência for encontrada, retorna None como valor padrão
        None,
    )

    # Verifica se foi encontrado um projeto válido após a busca case-insensitive
    if projeto_normalizado is None:
        # Retorna XML de erro em vez de levantar exceção
        return XMLBuilder().build_xml(
            data=[
                {
                    "status": "erro",
                    "tipo_erro": "projeto_invalido",
                    "projeto_informado": projeto,
                    "mensagem": f"Projeto '{projeto}' não encontrado na constante PROJETO_TO_NUMBER",
                    "projetos_validos": list(PROJETO_TO_NUMBER.keys()),
                }
            ],
            root_element_name="erro_validacao",
            item_element_name="erro",
            root_attributes={
                "sistema": "SIGA",
                "funcao": "editar_atendimento_avulso_sistemas",
            },
            custom_attributes={"sistema": "SIGA"},
        )

    projeto_final = PROJETO_TO_NUMBER[projeto_normalizado]

    # FUNÇÃO PARA GRAVAR INFORMAÇÕES
    try:
        async with aiohttp.ClientSession(json_serialize=ujson.dumps) as session:
            async with session.post(
                "https://ava3.uniube.br/ava/api/atendimentosAvulsos/atualizarAtendimentoAvulsoSigaIA/",
                json={
                    "apiKey": "92a61a8a-395e-40f9-abe1-7d172ce79df4",
                    "atendimento": codigo_atendimento,
                    "dataIni": data_inicio,
                    "dataFim": data_fim,
                    "matSolicitante": matricula_solicitante,
                    "tipo": tipo_final,
                    "descricao": descricao_atendimento,
                    "origem": origem_final,
                    "area": 1,
                    "equipe": equipe_final,
                    "analista": codigo_analista,
                    "projeto": projeto_final,
                    "sistema": sistema_final,
                    "nomeSolicitante": "",
                    "centroCusto": "",
                    "setor": "",
                    "matGestor": "",
                    "tempoGasto": "",
                    "campus": "",
                    "categoria": "",
                    "plaqueta": "",
                    "ramal": "",
                },
            ) as response:
                json_response = await response.json(content_type=None)
                result_data = json_response.get("result")

                # Trata a resposta
                if result_data is None:
                    data_final = [
                        {
                            "status": "erro",
                            "mensagem": "Não foi possível salvar o atendimento avulso. Verifique as informações digitadas.",
                        }
                    ]
                elif result_data == 1:
                    data_final = [
                        {
                            "status": "sucesso",
                            "mensagem": "Atendimento avulso editado com sucesso!",
                        }
                    ]
                else:
                    data_final = [
                        {
                            "status": "erro",
                            "mensagem": "Erro ao gravar o atendimento avulso. Tente novamente.",
                        }
                    ]

                # Adiciona os root_attributes
                return XMLBuilder().build_xml(
                    data=data_final,
                    root_element_name="atendimentos_avulsos",
                    item_element_name="atendimento_avulso",
                    root_attributes={
                        "codigo_atendimento": str(codigo_atendimento),
                        "dataIni": str(data_inicio),
                        "dataFim": str(data_fim),
                        "matSolicitante": str(matricula_solicitante),
                        "tipo": str(tipo_final),
                        "descricao": str(descricao_atendimento),
                        "origem": str(origem_final),
                        "equipe": str(equipe_final),
                        "analista": str(codigo_analista),
                        "projeto": str(projeto_final),
                        "sistema": str(sistema_final),
                    },
                    custom_attributes={"sistema": "SIGA"},
                )

    except Exception as e:
        return XMLBuilder().build_xml(
            data=[
                {
                    "status": "erro",
                    "mensagem": f"Erro interno: {str(e)}. Tente novamente mais tarde.",
                }
            ],
            root_element_name="resultado",
            item_element_name="item",
            custom_attributes={"sistema": "SIGA"},
        )