def docs() -> str:
    return """
Insere um novo atendimento em uma Ordem de Serviço (OS) no sistema SIGA.

Esta função cria um novo registro de atendimento associado a uma OS existente,
incluindo informações como datas, descrição, tipo, tempo gasto e flags de controle.
Realiza validação do tipo de atendimento e conversão automática de datas.

**Endpoint utilizado:** `inserirAtendimentosOsSigaIA`

**Estrutura do XML retornado:**
```xml
<ordens_servico os="123" dataIni="2024-01-15 09:00:00" analista="456"
                descricao="Descrição" tipo="Implementação" dataFim="2024-01-15 17:00:00"
                tempoGasto="480" primeiroAtendimento="False" apresentaSolucao="True"
                sistema="SIGA">
    <ordem_servico sistema="SIGA">
        <status>sucesso</status>
        <mensagem>Atendimento cadastrado com sucesso!</mensagem>
    </ordem_servico>
</ordens_servico>
```

**Em caso de erro de validação:**
```xml
<erro_validacao sistema="SIGA" funcao="inserir_atendimentos_os">
    <erro sistema="SIGA">
        <status>erro</status>
        <tipo_erro>tipo_invalido</tipo_erro>
        <tipo_informado>Tipo Inválido</tipo_informado>
        <mensagem>Tipo 'Tipo Inválido' não encontrado na constante TYPE_TO_NUMBER</mensagem>
        <tipos_validos>['Suporte Sistema', 'Implementação', ...]</tipos_validos>
    </erro>
</erro_validacao>
```

Args:
    codigo_os (int): Código da Ordem de Serviço à qual o atendimento será associado
    data_inicio (str | Literal): Data e hora de início do atendimento.
        Aceita formatos de data ou palavras-chave como "hoje", "agora", "ontem"
    codigo_analista (int): Matrícula do analista/usuário responsável pelo atendimento
    descricao_atendimento (str): Descrição detalhada do atendimento a ser realizado
    tipo (Literal): Tipo do atendimento, deve ser um dos valores válidos:
        - "Suporte Sistema" (código 1)
        - "Implementação" (código 2) - padrão
        - "Manutenção Corretiva" (código 3)
        - "Reunião" (código 4)
        - "Treinamento" (código 5)
        - "Mudança de Escopo" (código 20)
        - "Anexo" (código 12)
        - "Suporte Infraestrutura" (código 13)
        - "Monitoramento" (código 21)
        - "Incidente" (código 23)
        - "Requisição" (código 24)
    data_fim (str | Literal | None, optional): Data e hora de fim do atendimento.
        Aceita formatos de data ou palavras-chave como "hoje", "agora", "ontem".
        Se None, será enviado como string vazia. Defaults to None.
    primeiro_atendimento (bool, optional): Flag indicando se é o primeiro atendimento da OS.
        Defaults to False.
    apresenta_solucao (bool, optional): Flag indicando se o atendimento apresenta solução.
        Defaults to False.

Returns:
    str: XML formatado contendo:
        - Em caso de sucesso: confirmação da inserção com status "sucesso"
        - Em caso de erro de validação: detalhes do erro com tipos válidos
        - Em caso de erro de API: mensagem de erro específica
        - Em caso de erro interno: mensagem de erro genérica

        O XML sempre inclui os parâmetros enviados como atributos do elemento raiz.

Raises:
    Não levanta exceções diretamente. Todos os erros são capturados e retornados
    como XML formatado com informações detalhadas do erro.

Examples:
    >>> # Inserir atendimento básico
    >>> xml = await inserir_atendimentos_os(
    ...     codigo_os=456,
    ...     data_inicio="2024-01-15 09:00:00",
    ...     codigo_analista=789,
    ...     descricao_atendimento="Implementação de nova funcionalidade",
    ...     tipo="Implementação"
    ... )

    >>> # Inserir atendimento completo com solução
    >>> xml = await inserir_atendimentos_os(
    ...     codigo_os=456,
    ...     data_inicio="hoje 09:00",
    ...     codigo_analista=789,
    ...     descricao_atendimento="Correção de bug crítico",
    ...     tipo="Manutenção Corretiva",
    ...     data_fim="hoje 17:00",
    ...     primeiro_atendimento=True,
    ...     apresenta_solucao=True
    ... )

    >>> # Inserir primeiro atendimento de uma OS
    >>> xml = await inserir_atendimentos_os(
    ...     codigo_os=789,
    ...     data_inicio="agora",
    ...     codigo_analista=123,
    ...     descricao_atendimento="Análise inicial do problema",
    ...     tipo="Suporte Sistema",
    ...     primeiro_atendimento=True
    ... )

    >>> # Exemplo com tipo inválido (retorna erro)
    >>> xml = await inserir_atendimentos_os(
    ...     codigo_os=456,
    ...     data_inicio="2024-01-15 09:00:00",
    ...     codigo_analista=789,
    ...     descricao_atendimento="Teste",
    ...     tipo="Tipo Inexistente"  # Erro!
    ... )

Notes:
    - A função realiza validação case-insensitive do tipo de atendimento
    - As datas são automaticamente convertidas usando converter_data_siga com manter_horas=True
    - A função utiliza a constante TYPE_TO_NUMBER para mapear tipos para códigos numéricos
    - Todos os parâmetros enviados são incluídos como atributos no XML de resposta
    - A API key é obtida automaticamente da variável de ambiente AVA_API_KEY
    - Em caso de falha na requisição HTTP, retorna erro interno formatado em XML
    - O resultado da API (1 = sucesso, outros valores = erro) é interpretado automaticamente
    - Esta função cria um novo atendimento, diferente de editar_atendimentos_os que modifica existente

"""
