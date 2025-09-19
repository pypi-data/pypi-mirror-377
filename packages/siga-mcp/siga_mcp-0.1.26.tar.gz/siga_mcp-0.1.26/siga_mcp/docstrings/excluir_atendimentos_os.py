def docs() -> str:
    return """
Exclui um atendimento de Ordem de Serviço (OS) do sistema SIGA.

Esta função remove permanentemente um atendimento específico do sistema,
utilizando apenas o código do atendimento como identificador. A operação
é irreversível e deve ser usada com cautela.

**Endpoint utilizado:** `excluiAtendimentosOsSigaIA`

**Estrutura do XML retornado:**
```xml
<exclusões_atendimento_os atendimento="123" sistema="SIGA">
    <exclusão sistema="SIGA">
        <status>sucesso</status>
        <mensagem>Atendimento excluído com sucesso!</mensagem>
    </exclusão>
</exclusões_atendimento_os>
```

**Em caso de erro:**
```xml
<exclusões_atendimento_os atendimento="123" sistema="SIGA">
    <exclusão sistema="SIGA">
        <status>erro</status>
        <mensagem>Não foi possível excluir o atendimento. Verifique as informações digitadas.</mensagem>
    </exclusão>
</exclusões_atendimento_os>
```

Args:
    codigo_atendimento (int): Código único do atendimento a ser excluído.
        Este código deve corresponder a um atendimento existente no sistema.

Returns:
    str: XML formatado contendo:
        - Em caso de sucesso: confirmação da exclusão com status "sucesso"
        - Em caso de erro de validação: mensagem indicando problema com os dados
        - Em caso de erro de API: mensagem de erro específica
        - Em caso de erro interno: mensagem de erro genérica

        O XML sempre inclui o código do atendimento como atributo do elemento raiz.

Raises:
    Não levanta exceções diretamente. Todos os erros são capturados e retornados
    como XML formatado com informações detalhadas do erro.

Examples:
    >>> # Excluir atendimento específico
    >>> xml = await excluir_atendimentos_os(codigo_atendimento=12345)

    >>> # Exemplo de uso em contexto de limpeza
    >>> atendimentos_para_excluir = [123, 456, 789]
    >>> for codigo in atendimentos_para_excluir:
    ...     resultado = await excluir_atendimentos_os(codigo_atendimento=codigo)
    ...     print(f"Resultado para atendimento {codigo}: {resultado}")

Notes:
    - **ATENÇÃO**: Esta operação é irreversível. Uma vez excluído, o atendimento
        não pode ser recuperado através da API
    - A função valida apenas se o código do atendimento existe no sistema
    - Não há validação de permissões - qualquer usuário com acesso à API pode excluir
    - A API key é obtida automaticamente da variável de ambiente AVA_API_KEY
    - Em caso de falha na requisição HTTP, retorna erro interno formatado em XML
    - O resultado da API (1 = sucesso, outros valores = erro) é interpretado automaticamente

Warning:
    Use esta função com extrema cautela em ambientes de produção. Considere
    implementar validações adicionais ou logs de auditoria antes da exclusão.

"""
