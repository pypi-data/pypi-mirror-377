def docs() -> str:
    return """Exclui um atendimento avulso do sistema SIGA.

Esta função remove permanentemente um atendimento avulso específico do sistema,
utilizando apenas o código do atendimento como identificador. A operação
é irreversível e deve ser usada com cautela.

**Endpoint utilizado:** `excluiAtendimentoAvulsoSigaIA`

**Estrutura do XML retornado:**
```xml
<exclusões_atendimento_avulso atendimento="123" sistema="SIGA">
    <exclusão sistema="SIGA">
        <status>sucesso</status>
        <mensagem>Atendimento avulso excluído com sucesso!</mensagem>
    </exclusão>
</exclusões_atendimento_avulso>
```

**Em caso de erro:**
```xml
<exclusões_atendimento_avulso atendimento="123" sistema="SIGA">
    <exclusão sistema="SIGA">
        <status>erro</status>
        <mensagem>Não foi possível excluir o atendimento avulso. Verifique as informações digitadas.</mensagem>
    </exclusão>
</exclusões_atendimento_avulso>
```

Args:
    codigo_atendimento (int): Código único do atendimento avulso a ser excluído.
        Este código deve corresponder a um atendimento avulso existente no sistema.

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
    >>> # Excluir atendimento avulso específico
    >>> xml = await excluir_atendimento_avulso_sistemas(codigo_atendimento=12345)

    >>> # Exemplo de uso em contexto de limpeza
    >>> atendimentos_para_excluir = [123, 456, 789]
    >>> for codigo in atendimentos_para_excluir:
    ...     resultado = await excluir_atendimento_avulso_sistemas(codigo_atendimento=codigo)
    ...     print(f"Resultado para atendimento {codigo}: {resultado}")

Notes:
    - **ATENÇÃO**: Esta operação é irreversível. Uma vez excluído, o atendimento avulso
        não pode ser recuperado através da API
    - A função valida apenas se o código do atendimento existe no sistema
    - Esta função é específica para atendimentos avulsos da ÁREA SISTEMAS (área=1)
    - Não há validação de permissões - qualquer usuário com acesso à API pode excluir
    - A API key é obtida automaticamente da variável de ambiente AVA_API_KEY
    - Em caso de falha na requisição HTTP, retorna erro interno formatado em XML
    - O resultado da API (1 = sucesso, outros valores = erro) é interpretado automaticamente

Warning:
    Use esta função com extrema cautela em ambientes de produção. Considere
    implementar validações adicionais ou logs de auditoria antes da exclusão.
    Atendimentos avulsos excluídos não podem ser recuperados.
"""
