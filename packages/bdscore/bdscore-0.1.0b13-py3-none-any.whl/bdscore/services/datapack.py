from ..enums import ResponseFormat, DynamicDate, CorporateActionType, BooleanString
from typing import Union, Optional


class DataPack:

    def __init__(self, core):
        self._core = core

    # ====================================
    # MÉTODOS DE MERCADO FINANCEIRO
    # ====================================

    def getFX(self, Symbols, InitialDate, FinalDate: Optional[Union[str, DynamicDate]] = None, Fields=None, Interval=None, IgnDefault=None, Lang=None, Page=None, Rows=None, Format: Optional[ResponseFormat] = None, IgnNull: Optional[BooleanString] = None, isActive=None):
        """
        Obtém dados de câmbio e moedas estrangeiras.
        
        Args:
            Symbols (str): Símbolos das moedas para consulta (obrigatório)
            InitialDate (str): Data inicial da consulta (obrigatório)
            FinalDate (str | DynamicDate): Data final da consulta (opcional)
                                         Aceita datas dinâmicas: DynamicDate.YESTERDAY, DynamicDate.LAST_BUSINESS_DAY, etc.
            Fields (str): Campos específicos a retornar
            Interval (str): Intervalo dos dados
            IgnDefault (str): Ignorar valores padrão
            Lang (str): Idioma da resposta
            Page (int): Número da página
            Rows (int): Quantidade de linhas por página
            Format (ResponseFormat): Formato de retorno (default: ResponseFormat.JSON)
                                   Opções: ResponseFormat.JSON, ResponseFormat.XML, ResponseFormat.CSV, ResponseFormat.EXCEL
            IgnNull (BooleanString): Se deve retornar valores nulos (default: BooleanString.FALSE)
                                   Opções: BooleanString.TRUE, BooleanString.FALSE
            isActive (str): Filtrar apenas símbolos ativos
            
        Returns:
            dict: Dados de câmbio para os símbolos especificados
        """
        return self._core._BDSCore__make_request(
            self._core.datapack_url,
            "getFX",
            Symbols=Symbols,
            InitialDate=InitialDate,
            FinalDate=FinalDate.value if isinstance(FinalDate, DynamicDate) else FinalDate,
            Fields=Fields,
            Interval=Interval,
            IgnDefault=IgnDefault,
            Lang=Lang,
            Page=Page,
            Rows=Rows,
            Format=Format.value if isinstance(Format, ResponseFormat) else Format,
            IgnNull=IgnNull.value if isinstance(IgnNull, BooleanString) else IgnNull,
            isActive=isActive
        )

    def getEquitiesB3(self, Symbols, InitialDate, FinalDate=None, Fields=None, Interval=None, IgnDefault=None, Lang=None, Page=None, Rows=None, Format=None, IgnNull=None, isActive=None):
        """
        Obtém dados de ações negociadas na B3 (Bolsa de Valores do Brasil).
        
        Args:
            Symbols (str): Símbolos das ações para consulta (obrigatório)
            InitialDate (str): Data inicial da consulta (obrigatório)
            FinalDate (str): Data final da consulta (opcional)
            Fields (str): Campos específicos a retornar
            Interval (str): Intervalo dos dados
            IgnDefault (str): Ignorar valores padrão
            Lang (str): Idioma da resposta
            Page (int): Número da página
            Rows (int): Quantidade de linhas por página
            Format (str): Formato de retorno (default: "Json")
            IgnNull (str): Se deve retornar valores nulos (default: "False")
            isActive (str): Filtrar apenas símbolos ativos
            
        Returns:
            dict: Dados de ações da B3 para os símbolos especificados
        """
        return self._core._BDSCore__make_request(
            self._core.datapack_url,
            "getEquitiesB3",
            Symbols=Symbols,
            InitialDate=InitialDate,
            FinalDate=FinalDate,
            Fields=Fields,
            Interval=Interval,
            IgnDefault=IgnDefault,
            Lang=Lang,
            Page=Page,
            Rows=Rows,
            Format=Format,
            IgnNull=IgnNull,
            isActive=isActive
        )

    def getBrazilianTreasury(self, Symbols, InitialDate, FinalDate=None, Fields=None, Interval=None, IgnDefault=None, Lang=None, Page=None, Rows=None, Format=None, IgnNull=None, isActive=None):
        """
        Obtém dados cadastrais e de valores de títulos públicos brasileiros (LFT, LTN, NTN-B, NTN-C, NTN-F).
        
        Args:
            Symbols (str): Símbolos dos títulos públicos para consulta (obrigatório)
            InitialDate (str): Data inicial da consulta (obrigatório)
            FinalDate (str): Data final da consulta
            Fields (str): Campos específicos a retornar
            Interval (str): Intervalo dos dados
            IgnDefault (str): Ignorar valores padrão
            Lang (str): Idioma da resposta
            Page (int): Número da página
            Rows (int): Quantidade de linhas por página
            Format (str): Formato de retorno (default: "Json")
            IgnNull (str): Se deve retornar valores nulos (default: "False")
            isActive (str): Filtrar apenas símbolos ativos
            
        Returns:
            dict: Dados de títulos do Tesouro Nacional
        """
        return self._core._BDSCore__make_request(
            self._core.datapack_url,
            "getBrazilianTreasury",
            Symbols=Symbols,
            InitialDate=InitialDate,
            FinalDate=FinalDate,
            Fields=Fields,
            Interval=Interval,
            IgnDefault=IgnDefault,
            Lang=Lang,
            Page=Page,
            Rows=Rows,
            Format=Format,
            IgnNull=IgnNull,
            isActive=isActive
        )

    def getCommodities(self, Symbols, InitialDate, FinalDate=None, Fields=None, Interval=None, IgnDefault=None, Lang=None, Page=None, Rows=None, Format=None, IgnNull=None, isActive=None):
        """
        Obtém dados de commodities negociadas no mercado internacional.
        
        Args:
            Symbols (str): Símbolos das commodities para consulta (obrigatório)
            InitialDate (str): Data inicial da consulta (obrigatório)
            FinalDate (str): Data final da consulta (opcional)
            Fields (str): Campos específicos a retornar
            Interval (str): Intervalo dos dados
            IgnDefault (str): Ignorar valores padrão
            Lang (str): Idioma da resposta
            Page (int): Número da página
            Rows (int): Quantidade de linhas por página
            Format (str): Formato de retorno (default: "Json")
            IgnNull (str): Se deve retornar valores nulos (default: "False")
            isActive (str): Filtrar apenas símbolos ativos
            
        Returns:
            dict: Dados de commodities para os símbolos especificados
        """
        return self._core._BDSCore__make_request(
            self._core.datapack_url,
            "getCommodities",
            Symbols=Symbols,
            InitialDate=InitialDate,
            FinalDate=FinalDate,
            Fields=Fields,
            Interval=Interval,
            IgnDefault=IgnDefault,
            Lang=Lang,
            Page=Page,
            Rows=Rows,
            Format=Format,
            IgnNull=IgnNull,
            isActive=isActive
        )

    def getIndex(self, Symbols, InitialDate, FinalDate=None, Fields=None, Interval=None, IgnDefault=None, Lang=None, Page=None, Rows=None, Format=None, IgnNull=None, isActive=None):
        """
        Obtém dados de índices financeiros internacionais.
        
        Args:
            Symbols (str): Símbolos dos índices para consulta (obrigatório)
            InitialDate (str): Data inicial da consulta (obrigatório)
            FinalDate (str): Data final da consulta (opcional)
            Fields (str): Campos específicos a retornar
            Interval (str): Intervalo dos dados
            IgnDefault (str): Ignorar valores padrão
            Lang (str): Idioma da resposta
            Page (int): Número da página
            Rows (int): Quantidade de linhas por página
            Format (str): Formato de retorno (default: "Json")
            IgnNull (str): Se deve retornar valores nulos (default: "False")
            isActive (str): Filtrar apenas símbolos ativos
            
        Returns:
            dict: Dados de índices financeiros
        """
        return self._make_request(
            "getIndex",
            Symbols=Symbols,
            InitialDate=InitialDate,
            FinalDate=FinalDate,
            Fields=Fields,
            Interval=Interval,
            IgnDefault=IgnDefault,
            Lang=Lang,
            Page=Page,
            Rows=Rows,
            Format=Format,
            IgnNull=IgnNull,
            isActive=isActive
        )

    def getIndexB3(self, Symbols, InitialDate, FinalDate=None, Fields=None, Interval=None, IgnDefault=None, Lang=None, Page=None, Rows=None, Format=None, IgnNull=None, isActive=None):
        """
        Obtém dados de índices negociados na B3 (ex: Ibovespa, IBrX-100, etc.).
        
        Args:
            Symbols (str): Símbolos dos índices B3 para consulta (obrigatório)
            InitialDate (str): Data inicial da consulta (obrigatório)
            FinalDate (str): Data final da consulta (opcional)
            Fields (str): Campos específicos a retornar
            Interval (str): Intervalo dos dados
            IgnDefault (str): Ignorar valores padrão
            Lang (str): Idioma da resposta
            Page (int): Número da página
            Rows (int): Quantidade de linhas por página
            Format (str): Formato de retorno (default: "Json")
            IgnNull (str): Se deve retornar valores nulos (default: "False")
            isActive (str): Filtrar apenas símbolos ativos
            
        Returns:
            dict: Dados de índices da B3
        """
        return self._make_request(
            "getIndexB3",
            Symbols=Symbols,
            InitialDate=InitialDate,
            FinalDate=FinalDate,
            Fields=Fields,
            Interval=Interval,
            IgnDefault=IgnDefault,
            Lang=Lang,
            Page=Page,
            Rows=Rows,
            Format=Format,
            IgnNull=IgnNull,
            isActive=isActive
        )

    def getIndexPortfolioB3(self, Symbols, InitialDate, FinalDate=None, Fields=None, Interval=None, IgnDefault=None, Lang=None, Page=None, Rows=None, Format=None, IgnNull=None, isActive=None):
        """
        Obtém dados de portfólio dos índices negociados na B3.
        
        Args:
            Symbols (str): Símbolos dos índices para consulta (obrigatório)
            InitialDate (str): Data inicial da consulta (obrigatório)
            FinalDate (str): Data final da consulta (opcional)
            Fields (str): Campos específicos a retornar
            Interval (str): Intervalo dos dados
            IgnDefault (str): Ignorar valores padrão
            Lang (str): Idioma da resposta
            Page (int): Número da página
            Rows (int): Quantidade de linhas por página
            Format (str): Formato de retorno (default: "Json")
            IgnNull (str): Se deve retornar valores nulos (default: "False")
            isActive (str): Filtrar apenas símbolos ativos
            
        Returns:
            dict: Dados de portfólio dos índices B3
        """
        return self._make_request(
            "getIndexPortfolioB3",
            Symbols=Symbols,
            InitialDate=InitialDate,
            FinalDate=FinalDate,
            Fields=Fields,
            Interval=Interval,
            IgnDefault=IgnDefault,
            Lang=Lang,
            Page=Page,
            Rows=Rows,
            Format=Format,
            IgnNull=IgnNull,
            isActive=isActive
        )

    # ====================================
    # MÉTODOS DE DERIVATIVOS E FUTUROS
    # ====================================

    def getFuturesB3(self, Symbols, InitialDate, FinalDate=None, Fields=None, Interval=None, IgnDefault=None, Lang=None, Page=None, Rows=None, Format=None, IgnNull=None, isActive=None):
        """
        Obtém dados de contratos futuros negociados na B3.
        
        Args:
            Symbols (str): Símbolos dos futuros para consulta (obrigatório)
            InitialDate (str): Data inicial da consulta (obrigatório)
            FinalDate (str): Data final da consulta (opcional)
            Fields (str): Campos específicos a retornar
            Interval (str): Intervalo dos dados
            IgnDefault (str): Ignorar valores padrão
            Lang (str): Idioma da resposta
            Page (int): Número da página
            Rows (int): Quantidade de linhas por página
            Format (str): Formato de retorno (default: "Json")
            IgnNull (str): Se deve retornar valores nulos (default: "False")
            isActive (str): Filtrar apenas símbolos ativos
            
        Returns:
            dict: Dados de contratos futuros da B3
        """
        return self._make_request(
            "getFuturesB3",
            Symbols=Symbols,
            InitialDate=InitialDate,
            FinalDate=FinalDate,
            Fields=Fields,
            Interval=Interval,
            IgnDefault=IgnDefault,
            Lang=Lang,
            Page=Page,
            Rows=Rows,
            Format=Format,
            IgnNull=IgnNull,
            isActive=isActive
        )

    def getFuturesCME(self, Symbols, InitialDate, FinalDate=None, Fields=None, Interval=None, IgnDefault=None, Lang=None, Page=None, Rows=None, Format=None, IgnNull=None, isActive=None):
        """
        Obtém dados de contratos futuros negociados na CME (Chicago Mercantile Exchange).
        
        Args:
            Symbols (str): Símbolos dos futuros CME para consulta (obrigatório)
            InitialDate (str): Data inicial da consulta (obrigatório)
            FinalDate (str): Data final da consulta (opcional)
            Fields (str): Campos específicos a retornar
            Interval (str): Intervalo dos dados
            IgnDefault (str): Ignorar valores padrão
            Lang (str): Idioma da resposta
            Page (int): Número da página
            Rows (int): Quantidade de linhas por página
            Format (str): Formato de retorno (default: "Json")
            IgnNull (str): Se deve retornar valores nulos (default: "False")
            isActive (str): Filtrar apenas símbolos ativos
            
        Returns:
            dict: Dados de contratos futuros da CME
        """
        return self._make_request(
            "getFuturesCME",
            Symbols=Symbols,
            InitialDate=InitialDate,
            FinalDate=FinalDate,
            Fields=Fields,
            Interval=Interval,
            IgnDefault=IgnDefault,
            Lang=Lang,
            Page=Page,
            Rows=Rows,
            Format=Format,
            IgnNull=IgnNull,
            isActive=isActive
        )

    def getCMEAgricFutures(self, Symbols, InitialDate, FinalDate=None, Fields=None, Interval=None, IgnDefault=None, Lang=None, Page=None, Rows=None, Format=None, IgnNull=None, isActive=None):
        """
        Obtém dados de futuros agrícolas negociados na CME.
        
        Args:
            Symbols (str): Símbolos dos futuros agrícolas para consulta (obrigatório)
            InitialDate (str): Data inicial da consulta (obrigatório)
            FinalDate (str): Data final da consulta (opcional)
            Fields (str): Campos específicos a retornar
            Interval (str): Intervalo dos dados
            IgnDefault (str): Ignorar valores padrão
            Lang (str): Idioma da resposta
            Page (int): Número da página
            Rows (int): Quantidade de linhas por página
            Format (str): Formato de retorno (default: "Json")
            IgnNull (str): Se deve retornar valores nulos (default: "False")
            isActive (str): Filtrar apenas símbolos ativos
            
        Returns:
            dict: Dados de futuros agrícolas da CME
        """
        return self._make_request(
            "getCMEAgricFutures",
            Symbols=Symbols,
            InitialDate=InitialDate,
            FinalDate=FinalDate,
            Fields=Fields,
            Interval=Interval,
            IgnDefault=IgnDefault,
            Lang=Lang,
            Page=Page,
            Rows=Rows,
            Format=Format,
            IgnNull=IgnNull,
            isActive=isActive
        )

    def getCMEFuturesCommodities(self, Symbols, InitialDate, FinalDate=None, Fields=None, Interval=None, IgnDefault=None, Lang=None, Page=None, Rows=None, Format=None, IgnNull=None, isActive=None):
        """
        Obtém dados de futuros de commodities negociados na CME.
        
        Args:
            Symbols (str): Símbolos dos futuros de commodities para consulta (obrigatório)
            InitialDate (str): Data inicial da consulta (obrigatório)
            FinalDate (str): Data final da consulta (opcional)
            Fields (str): Campos específicos a retornar
            Interval (str): Intervalo dos dados
            IgnDefault (str): Ignorar valores padrão
            Lang (str): Idioma da resposta
            Page (int): Número da página
            Rows (int): Quantidade de linhas por página
            Format (str): Formato de retorno (default: "Json")
            IgnNull (str): Se deve retornar valores nulos (default: "False")
            isActive (str): Filtrar apenas símbolos ativos
            
        Returns:
            dict: Dados de futuros de commodities da CME
        """
        return self._make_request(
            "getCMEFuturesCommodities",
            Symbols=Symbols,
            InitialDate=InitialDate,
            FinalDate=FinalDate,
            Fields=Fields,
            Interval=Interval,
            IgnDefault=IgnDefault,
            Lang=Lang,
            Page=Page,
            Rows=Rows,
            Format=Format,
            IgnNull=IgnNull,
            isActive=isActive
        )

    def getFuturesOptionsB3(self, Symbols, InitialDate, FinalDate=None, Fields=None, Interval=None, IgnDefault=None, Lang=None, Page=None, Rows=None, Format=None, IgnNull=None, isActive=None):
        """
        Obtém dados de opções sobre futuros negociadas na B3.
        
        Args:
            Symbols (str): Símbolos das opções sobre futuros para consulta (obrigatório)
            InitialDate (str): Data inicial da consulta (obrigatório)
            FinalDate (str): Data final da consulta (opcional)
            Fields (str): Campos específicos a retornar
            Interval (str): Intervalo dos dados
            IgnDefault (str): Ignorar valores padrão
            Lang (str): Idioma da resposta
            Page (int): Número da página
            Rows (int): Quantidade de linhas por página
            Format (str): Formato de retorno (default: "Json")
            IgnNull (str): Se deve retornar valores nulos (default: "False")
            isActive (str): Filtrar apenas símbolos ativos
            
        Returns:
            dict: Dados de opções sobre futuros da B3
        """
        return self._make_request(
            "getFuturesOptionsB3",
            Symbols=Symbols,
            InitialDate=InitialDate,
            FinalDate=FinalDate,
            Fields=Fields,
            Interval=Interval,
            IgnDefault=IgnDefault,
            Lang=Lang,
            Page=Page,
            Rows=Rows,
            Format=Format,
            IgnNull=IgnNull,
            isActive=isActive
        )

    def getOptionsOnEquitiesB3(self, Symbols, InitialDate, FinalDate=None, Fields=None, Interval=None, IgnDefault=None, Lang=None, Page=None, Rows=None, Format=None, IgnNull=None, isActive=None):
        """
        Obtém dados de opções sobre ações negociadas na B3.
        
        Args:
            Symbols (str): Símbolos das opções sobre ações para consulta (obrigatório)
            InitialDate (str): Data inicial da consulta (obrigatório)
            FinalDate (str): Data final da consulta (opcional)
            Fields (str): Campos específicos a retornar
            Interval (str): Intervalo dos dados
            IgnDefault (str): Ignorar valores padrão
            Lang (str): Idioma da resposta
            Page (int): Número da página
            Rows (int): Quantidade de linhas por página
            Format (str): Formato de retorno (default: "Json")
            IgnNull (str): Se deve retornar valores nulos (default: "False")
            isActive (str): Filtrar apenas símbolos ativos
            
        Returns:
            dict: Dados de opções sobre ações da B3
        """
        return self._core._BDSCore__make_request(
            self._core.datapack_url,
            "getOptionsOnEquitiesB3",
            Symbols=Symbols,
            InitialDate=InitialDate,
            FinalDate=FinalDate,
            Fields=Fields,
            Interval=Interval,
            IgnDefault=IgnDefault,
            Lang=Lang,
            Page=Page,
            Rows=Rows,
            Format=Format,
            IgnNull=IgnNull,
            isActive=isActive
        )

    # ====================================
    # MÉTODOS DE EVENTOS CORPORATIVOS 
    # ====================================

    def getAdjQuoteHistory(self, Symbols, InitialDate, FinalDate: Optional[Union[str, DynamicDate]] = None, NominalValue: Optional[bool] = None, MissingValues: Optional[bool] = None, Page: Optional[int] = None, Rows: Optional[int] = None, Format: Optional[ResponseFormat] = None):
        """
        Retorna o histórico completo de cotações ajustadas aos proventos de um ativo específico.
        
        Este endpoint fornece preços de abertura, fechamento, máximo, mínimo, volume negociado e 
        fatores de ajuste aplicados devido a eventos corporativos como dividendos, splits, bonificações, etc.
        
        Args:
            Symbols (str): Código de identificação do ativo na bolsa de valores (ticker symbol) (obrigatório)
                          Exemplos: PETR4 (Petrobras PN), VALE3 (Vale ON), ITUB4 (Itaú Unibanco PN)
            InitialDate (str): Data de início do período para consulta no formato YYYY-MM-DD (ISO 8601) (obrigatório)
                              Aceita datas dinâmicas: DynamicDate.YESTERDAY, DynamicDate.LAST_BUSINESS_DAY, DynamicDate.FIRST_BUSINESS_DAY_PREV_MONTH
            FinalDate (str | DynamicDate): Data de fim do período para consulta no formato YYYY-MM-DD (ISO 8601) (opcional)
                           Se não informado: retorna dados apenas da data inicial
            NominalValue (bool): Define se os valores nominais (não ajustados) devem ser incluídos na resposta (opcional)
                               True: retorna valores ajustados + nominais para comparação
                               False: apenas valores ajustados (padrão)
            MissingValues (bool): Define se deve preencher dados ausentes com valores específicos (opcional)
                                Útil para análises que requerem continuidade temporal (padrão: False)
            Page (int): Número da página para paginação dos resultados (opcional)
                       Inicia em 1, se não informado: retorna a primeira página
            Rows (int): Quantidade máxima de registros por página (opcional)
                       Máximo geral: 1.000 registros, Formato Excel: automaticamente ajustado para 10.000 registros
            Format (ResponseFormat): Formato de serialização da resposta da API (opcional)
                         Opções: ResponseFormat.JSON (padrão), ResponseFormat.XML, ResponseFormat.CSV, ResponseFormat.EXCEL
            
        Returns:
            BDSResult: Histórico de cotações ajustadas com preços corrigidos por proventos e eventos corporativos
                      Inclui preços ajustados, volumes, quantidades e fatores de correção aplicados
        """
        return self._core._BDSCore__make_request(
            self._core.datapack_url,
            "getAdjQuoteHistory",
            Symbols=Symbols,
            InitialDate=InitialDate,
            FinalDate=FinalDate.value if isinstance(FinalDate, DynamicDate) else FinalDate,
            NominalValue=NominalValue,
            MissingValues=MissingValues,
            Page=Page,
            Rows=Rows,
            Format=Format.value if isinstance(Format, ResponseFormat) else Format
        )

    def getCorporateActions(self, Symbols, InitialDate, FinalDate: Optional[Union[str, DynamicDate]] = None, EvtActnTpCd: Optional[CorporateActionType] = None, Page: Optional[int] = None, Rows: Optional[int] = None, Format: Optional[ResponseFormat] = None):
        """
        Retorna informações detalhadas sobre eventos corporativos de ativos listados na bolsa.
        
        Tipos de eventos corporativos incluem distribuição de proventos (dividendos, JCP, bonificações),
        alterações no capital (splits, grupamentos, incorporações), direitos de subscrição e outros eventos
        que afetam o preço e quantidade de ações.
        
        Args:
            Symbols (str): Código de identificação do ativo na bolsa de valores (ticker symbol) (obrigatório)
                          Exemplos: PETR4 (Petrobras PN), VALE3 (Vale ON), ITUB4 (Itaú Unibanco PN)
            InitialDate (str): Data de início do período para consulta no formato YYYY-MM-DD (ISO 8601) (obrigatório)
                              Aceita datas dinâmicas: DynamicDate.YESTERDAY, DynamicDate.LAST_BUSINESS_DAY, DynamicDate.FIRST_BUSINESS_DAY_PREV_MONTH
            FinalDate (str | DynamicDate): Data de fim do período para consulta no formato YYYY-MM-DD (ISO 8601) (opcional)
                           Se não informado: busca eventos apenas na data inicial
            EvtActnTpCd (CorporateActionType): Filtra por tipo específico de evento corporativo (opcional)
                              Códigos principais:
                              - CorporateActionType.DIVIDEND: Dividendo
                              - CorporateActionType.INTEREST_ON_EQUITY: Juros sobre Capital Próprio
                              - CorporateActionType.STOCK_SPLIT: Desdobramento (Split)
                              - CorporateActionType.STOCK_GROUPING: Grupamento
                              - CorporateActionType.INCORPORATION: Incorporação
                              - CorporateActionType.MERGER: Fusão
                              E muitos outros... (veja CorporateActionType para lista completa)
            Page (int): Número da página para paginação dos resultados (opcional)
                       Inicia em 1, se não informado: retorna a primeira página
            Rows (int): Quantidade máxima de registros por página (opcional)
                       Máximo geral: 1.000 registros, Formato Excel: automaticamente ajustado para 10.000 registros
            Format (ResponseFormat): Formato de serialização da resposta da API (opcional)
                         Opções: ResponseFormat.JSON (padrão), ResponseFormat.XML, ResponseFormat.CSV, ResponseFormat.EXCEL
            
        Returns:
            BDSResult: Lista de eventos corporativos com detalhes completos incluindo datas, valores, 
                      tipos de evento e informações societárias
        """
        return self._core._BDSCore__make_request(
            self._core.datapack_url,
            "getCorporateActions",
            Symbols=Symbols,
            InitialDate=InitialDate,
            FinalDate=FinalDate.value if isinstance(FinalDate, DynamicDate) else FinalDate,
            EvtActnTpCd=EvtActnTpCd.value if isinstance(EvtActnTpCd, CorporateActionType) else EvtActnTpCd,
            Page=Page,
            Rows=Rows,
            Format=Format.value if isinstance(Format, ResponseFormat) else Format
        )
