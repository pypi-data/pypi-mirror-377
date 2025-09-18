import functools
import inspect
import re
import types
import importlib
from functools import wraps
from typing import Awaitable, Callable, Literal, Union, get_args, get_origin

from fastmcp import FastMCP

from siga_mcp.constants import MATRICULA_USUARIO_ATUAL


def tool(server: FastMCP, transport: Literal["stdio", "http"]):
    """
    Decorator that conditionally removes CURRENT_USER support based on MCP_TRANSPORT.

    If MCP_TRANSPORT != "stdio", removes Literal["CURRENT_USER"] from function signatures
    and cleans related documentation.
    """

    def decorator(func: Callable[..., Awaitable]) -> Callable[..., Awaitable]:
        # Carrega a docstring a partir de um módulo homônimo em siga_mcp.docstrings
        module_name = f"siga_mcp.docstrings.{func.__name__.lower()}"
        try:
            doc_module = importlib.import_module(module_name)
        except ModuleNotFoundError as e:
            raise ModuleNotFoundError(
                f"Arquivo de docstring não encontrado para a função '{func.__name__}'. "
                f"Esperado: siga_mcp/docstrings/{func.__name__}.py"
            ) from e

        if not hasattr(doc_module, "docs") or not callable(getattr(doc_module, "docs")):
            raise AttributeError(
                f"O módulo '{module_name}' não possui a função docs()."
            )

        try:
            raw_docstring = doc_module.docs()
            if not isinstance(raw_docstring, str):
                raise TypeError("A função docs() deve retornar uma string.")
        except Exception as e:
            raise RuntimeError(
                f"Falha ao obter docstring a partir de {module_name}.docs()."
            ) from e

        if transport == "stdio":
            # Em modo stdio, mantém a assinatura original e apenas atualiza a docstring
            func.__doc__ = raw_docstring
            return server.tool(func)

        # Remove CURRENT_USER from annotations
        def remove_current_user_from_annotation(annotation):
            if annotation == inspect.Parameter.empty or annotation is None:
                return annotation

            origin = get_origin(annotation)

            if origin is Union or (
                hasattr(types, "UnionType") and isinstance(annotation, types.UnionType)
            ):
                args = get_args(annotation)
                new_args = [
                    arg
                    for arg in args
                    if not (
                        get_origin(arg) is Literal and "CURRENT_USER" in get_args(arg)
                    )
                ]

                if len(new_args) == 0:
                    return str
                elif len(new_args) == 1:
                    return new_args[0]
                else:
                    if hasattr(types, "UnionType") and isinstance(
                        annotation, types.UnionType
                    ):
                        result = new_args[0]
                        for arg in new_args[1:]:
                            result = result | arg
                        return result
                    else:
                        return Union[tuple(new_args)]

            if get_origin(annotation) is Literal and "CURRENT_USER" in get_args(
                annotation
            ):
                return str

            return annotation

        # Remove CURRENT_USER from docstring
        def remove_current_user_from_docstring(docstring):
            if not docstring:
                return docstring

            lines = docstring.split("\n")
            new_lines = []
            skip_next_lines = False

            for line in lines:
                if any(
                    phrase in line
                    for phrase in [
                        'If "CURRENT_USER"',
                        'Se "CURRENT_USER"',
                        'If matricula == "CURRENT_USER"',
                        '- "CURRENT_USER":',
                    ]
                ):
                    skip_next_lines = True
                    continue

                if skip_next_lines:
                    if line.strip() and (
                        line.strip().endswith(":")
                        or line.lstrip().startswith(
                            ("Args:", "Returns:", "Raises:", "Examples:", "Notes:")
                        )
                        or re.match(r"\s*\w+\s*\([^)]*\):", line)
                    ):
                        skip_next_lines = False
                    else:
                        continue

                cleaned_line = line
                cleaned_line = re.sub(
                    r'\s*\|\s*Literal\["CURRENT_USER"\]', "", cleaned_line
                )
                cleaned_line = re.sub(
                    r'Literal\["CURRENT_USER"\]\s*\|\s*', "", cleaned_line
                )
                cleaned_line = re.sub(r',?\s*"CURRENT_USER"[^,\n]*', "", cleaned_line)
                cleaned_line = re.sub(r'\s*-\s*"CURRENT_USER"[^-\n]*', "", cleaned_line)
                cleaned_line = re.sub(r"\s+", " ", cleaned_line)
                cleaned_line = re.sub(r"\s*\|\s*\)", ")", cleaned_line)
                cleaned_line = re.sub(r",\s*\)", ")", cleaned_line)

                new_lines.append(cleaned_line)

            result = "\n".join(new_lines)
            return re.sub(r"\n\s*\n\s*\n", "\n\n", result)

        # Create modified function
        sig = inspect.signature(func)
        new_params = []

        for param_name, param in sig.parameters.items():
            new_annotation = remove_current_user_from_annotation(param.annotation)
            new_default = (
                param.default
                if param.default != "CURRENT_USER"
                else inspect.Parameter.empty
            )
            new_param = param.replace(annotation=new_annotation, default=new_default)
            new_params.append(new_param)

        new_sig = sig.replace(parameters=new_params)
        new_docstring = remove_current_user_from_docstring(raw_docstring or "")

        if inspect.iscoroutinefunction(func):

            @wraps(func)
            async def wrapper(*args, **kwargs):
                return await func(*args, **kwargs)
        else:

            @wraps(func)
            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)

        wrapper.__signature__ = new_sig
        wrapper.__doc__ = new_docstring

        new_annotations = {}
        for param_name, param in new_sig.parameters.items():
            if param.annotation != inspect.Parameter.empty:
                new_annotations[param_name] = param.annotation

        if hasattr(func, "__annotations__") and "return" in func.__annotations__:
            new_annotations["return"] = func.__annotations__["return"]

        wrapper.__annotations__ = new_annotations

        return server.tool(wrapper)

    return decorator


def resolve_matricula[T](
    func: Callable[..., Awaitable[T]],
) -> Callable[..., Awaitable[T]]:
    """
    Decorator que resolve automaticamente qualquer argumento com valor "CURRENT_USER".

    Em vez de depender do nome do parâmetro (por exemplo, 'matricula'), este decorator
    percorre todos os argumentos posicionais e nomeados e substitui qualquer ocorrência
    do valor literal "CURRENT_USER" pelo valor de MATRICULA_USUARIO_ATUAL. Isso inclui
    valores aninhados em coleções simples (list, tuple, set, dict - apenas valores).

    Regras:
    1) A substituição só ocorre quando MCP_TRANSPORT == "stdio"; caso contrário, lança erro
       se for detectado ao menos um "CURRENT_USER" nos argumentos.
    2) Somente valores exatamente iguais à string "CURRENT_USER" são substituídos (não faz
       match parcial dentro de outras strings).

    Funciona com funções assíncronas.
    """

    def _replace_current_user(value):
        # Substitui apenas valores exatamente iguais a "CURRENT_USER"
        if isinstance(value, str):
            return MATRICULA_USUARIO_ATUAL if value == "CURRENT_USER" else value
        # Coleções comuns: processa recursivamente
        if isinstance(value, list):
            return [_replace_current_user(v) for v in value]
        if isinstance(value, tuple):
            return tuple(_replace_current_user(v) for v in value)
        if isinstance(value, set):
            return {_replace_current_user(v) for v in value}
        if isinstance(value, dict):
            # Apenas valores; chaves permanecem inalteradas
            return {k: _replace_current_user(v) for k, v in value.items()}
        return value

    def _has_current_user(value) -> bool:
        if isinstance(value, str):
            return value == "CURRENT_USER"
        if isinstance(value, (list, tuple, set)):
            return any(_has_current_user(v) for v in value)
        if isinstance(value, dict):
            return any(_has_current_user(v) for v in value.values())
        return False

    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        # Obtém a assinatura da função para mapear argumentos posicionais
        sig = inspect.signature(func)
        bound_args = sig.bind(*args, **kwargs)
        bound_args.apply_defaults()

        # Verifica se existe qualquer ocorrência de "CURRENT_USER" em qualquer argumento
        any_current_user = any(
            _has_current_user(val) for val in bound_args.arguments.values()
        )

        if any_current_user:
            from siga_mcp.constants import MCP_TRANSPORT

            if MCP_TRANSPORT != "stdio":
                raise ValueError(
                    "MCP_TRANSPORT must be stdio to get current AD user (found 'CURRENT_USER' in arguments)"
                )

            # Substitui "CURRENT_USER" por MATRICULA_USUARIO_ATUAL em todos os argumentos
            for name, val in list(bound_args.arguments.items()):
                new_val = _replace_current_user(val)
                bound_args.arguments[name] = new_val

        # Chama a função original com os argumentos atualizados
        return await func(*bound_args.args, **bound_args.kwargs)

    return wrapper


def controlar_acesso_matricula[T](
    func: Callable[..., Awaitable[T]],
) -> Callable[..., Awaitable[T]]:
    """
    Decorator que verifica automaticamente permissões de acesso à matrícula.

    Este decorator intercepta chamadas de função e verifica se o usuário atual
    tem permissão para acessar os dados da matrícula especificada:
    1. Obtém o parâmetro 'matricula' da função
    2. Verifica permissão usando verificar_permissao_acesso_matricula()
    3. Retorna erro 401 se não houver permissão
    4. Permite execução da função se houver permissão

    Funciona com funções assíncronas que tenham o parâmetro 'matricula'.
    """

    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        # Obtém a assinatura da função para mapear argumentos posicionais
        sig = inspect.signature(func)
        bound_args = sig.bind(*args, **kwargs)
        bound_args.apply_defaults()

        # Verifica se existe o parâmetro 'matricula'
        if "matricula" in bound_args.arguments:
            from siga_mcp.utils import verificar_permissao_acesso_matricula

            matricula = bound_args.arguments["matricula"]

            if matricula == "CURRENT_USER":
                matricula = MATRICULA_USUARIO_ATUAL

            # Verifica se o usuário tem permissão para acessar esta matrícula
            usuario_nao_pode_acessar = not verificar_permissao_acesso_matricula(
                matricula
            )

            if usuario_nao_pode_acessar:
                # Retorna o nome da função para contextualizar o erro
                func_name = func.__name__
                return f"Erro 401: Permissão negada para '{func_name}'. Usuário atual logado é diferente do solicitado. Você não pode acessar essa função. Contate seu administrador."

        # Chama a função original se tiver permissão
        return await func(*args, **kwargs)

    return wrapper
