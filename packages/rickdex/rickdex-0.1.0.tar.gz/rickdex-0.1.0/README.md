# rickdex

Biblioteca Python para facilitar o acesso à [API Rick and Morty](https://rickandmortyapi.com/) de forma simples e intuitiva, permitindo a busca de informações sobre personagens, episódios e localizações diretamente no seu código Python.[^1]

### Instalação

A biblioteca depende do pacote `requests`. Para instalar, execute:

```bash
pip install requests
```

Copie ou adicione o arquivo `rickdex.py` ao seu projeto.[^1]

### Como Usar

Importe as classes principais:

```python
from rickdex import Base, Personagem, Localizacao, Episodio
```


#### Exemplos de Uso

- Buscar informações gerais da API:

```python
info = Base.info()
print(info)
```

- Buscar personagem por ID:

```python
rick = Personagem.pegarUm(1)
print(rick)
```

- Buscar vários personagens por lista de IDs:

```python
lista = Personagem.pegarVarios([1, 2, 3])
print(lista)
```

- Filtrar personagens:

```python
resultado = Personagem.filtro(name="Rick", status="alive")
print(resultado)
```

- Buscar localização por ID:

```python
local = Localizacao.umLocal(1)
print(local)
```

- Buscar episódio por código:

```python
ep = Episodio.filtro(episode="S01E01")
print(ep)
```


### Estrutura

- **Base**: Informações gerais da API.
- **Personagem**: Métodos para obter personagens, listar, filtrar e buscar atributos específicos.
- **Localizacao**: Métodos para obter e filtrar localizações.
- **Episodio**: Métodos para buscar, listar e filtrar episódios.[^1]


### Métodos Principais

| Classe | Método | Finalidade |
| :-- | :-- | :-- |
| Base | info() | Informações gerais da API |
| Personagem | pegarUm(id) | Retorna personagem por ID |
|  | pegarVarios(lista) | Retorna lista de personagens por IDs |
|  | filtro(...) | Filtra personagens por atributos |
| Localizacao | umLocal(id) | Retorna localização por ID |
|  | variosLocais(lista) | Lista localizações por IDs |
|  | filtro(...) | Filtra localizações |
| Episodio | umEp(id) | Retorna episódio por ID |
|  | variosEp(lista) | Lista episódios por IDs |
|  | filtro(...) | Filtra episódios |

[^1]

### Licença

Consulte a política de uso da API Rick and Morty. Recomenda-se utilizar esta biblioteca para fins pessoais ou acadêmicos, respeitando as diretrizes da API e do seu repositório de código.[^1]