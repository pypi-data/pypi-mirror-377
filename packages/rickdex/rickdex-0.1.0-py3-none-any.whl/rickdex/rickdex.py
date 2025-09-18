import requests

base_url = "https://rickandmortyapi.com/api"
personagem_url = f"{base_url}/character"
localizacao_url = f"{base_url}/location"
episodio_url = f"{base_url}/episode"

class Base:
    """Classe base para obter informações gerais da API Rick and Morty."""
    def info():
        """Retorna informações gerais da API."""
        try:
            return requests.get(base_url).json()
        except Exception as e:
            return {"erro": str(e)}

class Personagem:
    """Classe para operações relacionadas a personagens."""
    @staticmethod
    def info() -> dict:
        """Retorna as informações gerais da API relacionado aos personagens"""
        try:
            resp = requests.get(personagem_url).json()
            return resp.get("info", [])
        except Exception as e:
            return {"erro": str(e)}

    @staticmethod
    def pegarVarios(lista: list = None) -> dict:
        """
        Retorna uma lista de personagens pelo ID.
        Parâmetros:
            lista (list): Lista de IDs dos personagens.
        """
        try:
            if lista is None:
                total = Personagem.info()["count"]
                lista = list(range(1, total + 1))
            return requests.get(f"{personagem_url}/{lista}").json()
        except Exception as e:
            return {"erro": str(e)}

    @staticmethod
    def pegarUm(id: int) -> dict:
        """
        Retorna um personagem específico pelo ID.
        Parâmetros:
            id (int): ID do personagem.
        """
        try:
            if 1 <= id <= Personagem.info()["count"]:
                return requests.get(f"{personagem_url}/{id}").json()
            else:
                return {"erro": "ID inexistente na API"}
        except Exception as e:
            return {"erro": str(e)}

    @staticmethod
    def filtro(name: str = None, status: str = None, species: str = None, type: str = None, gender: str = None) -> dict:
        """
        Filtra personagens pelos parâmetros fornecidos.
        Parâmetros:
            name (str): Nome do personagem.
            status (str): Status do personagem (alive, dead ou unknown).
            species (str): Espécie do personagem.
            type (str): Tipo do personagem.
            gender (str): Gênero do personagem (female, male, genderless ou unknown).
        """
        try:
            params = {}
            if name is not None: params["name"] = name
            if status is not None: params["status"] = status
            if species is not None: params["species"] = species
            if type is not None: params["type"] = type
            if gender is not None: params["gender"] = gender
            
            resp = requests.get(personagem_url, params=params).json()
            return resp.get("results", [])
        except Exception as e:
            return {"erro": str(e)}
    
    @staticmethod
    def persoFiltro(id: int, filtro: list) -> dict:
        try:
            if 1 <= id <= Personagem.info()["count"]:
                resultado = {}
                personagem = Personagem.pegarUm(id)
                for chave, valor in personagem.items():
                    if chave in filtro:
                        resultado[chave] = valor
                return resultado
            else:
                return {"erro": f"ID inexistente na API"}
        except Exception as e:
            return {"erro": str(e)}

class Localizacao:
    """Classe para operações relacionadas a localizações."""
    @staticmethod
    def info() -> dict:
        """Retorna as informações gerais da API relacionado as localizações"""
        try:
            resp = requests.get(localizacao_url).json()
            return resp.get("info", [])
        except Exception as e:
            return {"erro": str(e)}

    @staticmethod
    def variosLocais(lista: list = None) -> dict:
        """
        Retorna uma lista de localizações pelo ID.
        Parâmetros:
            lista (list): Lista de IDs das localizações.
        """
        try:
            if lista is None:
                total = Localizacao.info()["count"]
                lista = list(range(1, total + 1))
            return requests.get(f"{localizacao_url}/{lista}").json()
        except Exception as e:
            return {"erro": str(e)}

    @staticmethod
    def umLocal(id: int) -> dict:
        """
        Retorna uma localização específica pelo ID.
        Parâmetros:
            id (int): ID da localização.
        """
        try:
            if 1 >= id <= Localizacao.info()["count"]:
                return requests.get(f"{localizacao_url}/{id}").json()
            else:
                return {"erro": "ID inexistente na API"}
        except Exception as e:
            return {"erro": str(e)}
    
    @staticmethod
    def filtro(name: str = None, type: str = None, dimension: str = None) -> dict:
        """
        Filtra localizações pelos parâmetros fornecidos.
        Parâmetros:
            name (str): Nome da localização.
            type (str): Tipo da localização.
            dimension (str): Dimensão da localização.
        """
        try:
            params = {}
            if name is not None: params["name"] = name
            if type is not None: params["type"] = type
            if dimension is not None: params["dimension"] = dimension

            resp = requests.get(localizacao_url, params=params).json()
            return resp.get("results", [])
        except Exception as e:
            return {"erro": str(e)}
    
    @staticmethod
    def localFiltro(id: int, filtro: list) -> dict:
        try:
            if 1 >= id <= Localizacao.info()["count"]:
                local = Localizacao.umLocal(id)
                resultado = {}
                for chave, valor in local.items():
                    if chave in filtro:
                        resultado[chave] = valor
                return resultado
            else:
                return {"erro": "ID inexistente na API"}
        except Exception as e:
            return {"erro": str(e)}

class Episodio:
    """Classe para operações relacionadas a episódios."""
    @staticmethod
    def info() -> dict:
        """Retorna as informações gerais da API relacionado aos episódios"""
        try:
            resp = requests.get(episodio_url).json()
            return resp.get("info", [])
        except Exception as e:
            return {"erro": str(e)}

    @staticmethod
    def variosEp(lista: list = None) -> dict:
        """
        Retorna uma lista de episódios pelo ID.
        Parâmetros:
            lista (list): Lista de IDs dos episódios.
        """
        try:
            if lista is None:
                total = requests.get(episodio_url).json()["info"]["count"]
                lista = list(range(1, total + 1))
            return requests.get(f"{episodio_url}/{lista}").json()
        except Exception as e:
            return {"erro": str(e)}

    @staticmethod
    def umEp(id: int) -> dict:
        """
        Retorna um episódio específico pelo ID.
        Parâmetros:
            id (int): ID do episódio.
        """
        try:
            if 1 <= id <= Episodio.info()["count"]:
                return requests.get(f"{episodio_url}/{id}").json()
            else:
                return {"erro": "ID inexistente na API"}
        except Exception as e:
            return {"erro": str(e)}

    @staticmethod
    def filtro(name: str = None, episode: str = None) -> dict:
        """
        Filtra episódios pelos parâmetros fornecidos.
        Parâmetros:
            name (str): Nome do episódio.
            episode (str): Código do episódio (ex: S01E01).
        """
        try:
            params = {}
            if name is not None: params["name"] = name
            if episode is not None: params["episode"] = episode
            
            resp = requests.get(episodio_url, params=params).json()
            return resp.get("results", [])
        except Exception as e:
            return {"erro": str(e)}
    
    @staticmethod
    def epFiltro(id: int, filtro: list) -> dict:
        try:
            if 1 <= id <= Episodio.info()["count"]:
                episodio = Episodio.umEp(id)
                resultado = {}
                for chave, valor in episodio.items():
                    if chave in filtro:
                        resultado[chave] = valor
                return resultado
            else:
                return {"erro": "ID inexistente na API"}
        except Exception as e:
            return {"erro": str(e)}