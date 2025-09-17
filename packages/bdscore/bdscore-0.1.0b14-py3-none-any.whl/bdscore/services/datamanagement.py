import time


class DataManagement:

    def getFamilies(
        self,
        FamilyId=None,
        Status=None,
        FilterId=None,
        SourceId=None,
        AttributeId=None,
        NotebookId=None,
        CadasterId=None,
        TableId=None,
        Lang=None,
        Page=None,
        Rows=None
    ):
        """
        Método para consultar famílias de dados

        @param FamilyId: ID da família de dados
        @param Status: Status da família de dados
        @param FilterId: ID do filtro
        @param SourceId: ID da fonte de dados
        @param AttributeId: ID do atributo
        @param NotebookId: ID do caderno
        @param CadasterId: ID do cadastro
        @param TableId: ID da tabela
        @param Lang: Idioma da resposta
        @param Page: Número da página
        @param Rows: Número de linhas por página
        @return: Resposta da API DataManagement
        """
        url = f"{self._core.datamanagement_url}/Family"
        params = {}
        if FamilyId is not None: params["FamilyId"] = FamilyId
        if Status is not None: params["Status"] = Status
        if FilterId is not None: params["FilterId"] = FilterId
        if SourceId is not None: params["SourceId"] = SourceId
        if AttributeId is not None: params["AttributeId"] = AttributeId
        if NotebookId is not None: params["NotebookId"] = NotebookId
        if CadasterId is not None: params["CadasterId"] = CadasterId
        if TableId is not None: params["TableId"] = TableId
        if Lang is not None: params["Lang"] = Lang
        if Page is not None: params["Page"] = Page
        if Rows is not None: params["Rows"] = Rows

        return self._core._BDSCore__request(
            method="get",
            url=url,
            params=params
        )
    def __init__(self, core):
        self._core = core

    
    
    def getValues(
        self,
        FamilyId,
        InitialDate,
        SeriesId=None,
        Interval=None,
        AttributesId=None,
        CadastersId=None,
        FinalDate=None,
        IsActive=None,
        Lang=None,
        Page=None,
        Rows=None
    ):
        """
        Consulta valores de séries temporais de acordo com os parâmetros da API DataManagement.
        Parâmetros obrigatórios: FamilyId, InitialDate
        """
        if not FamilyId or not InitialDate:
            raise ValueError("Os parâmetros 'FamilyId' e 'InitialDate' são obrigatórios.")

        url = f"{self._core.datamanagement_url}/getValues"
        params = {
            "FamilyId": FamilyId,
            "InitialDate": InitialDate,
        }
        if SeriesId is not None: params["SeriesId"] = SeriesId
        if Interval is not None: params["Interval"] = Interval
        if AttributesId is not None: params["AttributesId"] = AttributesId
        if CadastersId is not None: params["CadastersId"] = CadastersId
        if FinalDate is not None: params["FinalDate"] = FinalDate
        if Lang is not None: params["Lang"] = Lang
        if Page is not None: params["Page"] = Page
        if Rows is not None: params["Rows"] = Rows

        return self._core._BDSCore__request(
            method="get",
            url=url,
            params=params
        )

    def getCurves(
        self,
        ReferenceDate,
        Name=None,
        Fields=None,
        Format=None,
        Lang=None,
        Page=None,
        Rows=None
    ):
        """
        Consulta curvas de juros e rendimentos calculadas.
        
        Args:
            ReferenceDate (str): Data de referência para a consulta (obrigatório)
                                Ex: "2024-01-01", "D-1" (dia anterior), "last" (último disponível)
            Name (str): Nome da curva específica (opcional)
                       Ex: "SOFR_USD", "DI_BRL", "TREASURIES_USD"
            Fields (str): Campos específicos a retornar (opcional)
                         Ex: ":all" para todos os campos, ou campos específicos separados por vírgula
            Format (str): Formato de retorno (opcional)
                         Ex: "json", "xml", "csv"
            Lang (str): Idioma da resposta (opcional)
            Page (int): Número da página para paginação (opcional)
            Rows (int): Número de linhas por página (opcional)
            
        Returns:
            BDSResult: Objeto com os dados das curvas de juros
            
        Example:
            # Buscar curva SOFR_USD do dia anterior
            curves = bds.datamanagement.getCurves(
                ReferenceDate="D-1",
                Name="SOFR_USD",
                Fields=":all",
                Format="json"
            )
            print(curves.data.to_df())
        """
        if not ReferenceDate:
            raise ValueError("O parâmetro 'ReferenceDate' é obrigatório.")

        url = f"{self._core.datamanagement_url}/Calculate/Curves"
        params = {
            "ReferenceDate": ReferenceDate,
        }
        if Name is not None: params["Name"] = Name
        if Fields is not None: params["Fields"] = Fields
        if Format is not None: params["Format"] = Format
        if Lang is not None: params["Lang"] = Lang
        if Page is not None: params["Page"] = Page
        if Rows is not None: params["Rows"] = Rows

        return self._core._BDSCore__request(
            method="get",
            url=url,
            params=params
        )