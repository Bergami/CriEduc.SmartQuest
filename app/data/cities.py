from typing import Optional

# Lista oficial dos municípios do Espírito Santo
CITIES_ES = [
    "Afonso Cláudio",
    "Água Doce do Norte",
    "Águia Branca",
    "Alegre",
    "Alfredo Chaves",
    "Alto Rio Novo",
    "Anchieta",
    "Apiacá",
    "Aracruz",
    "Atilio Vivacqua",
    "Baixo Guandu",
    "Barra de São Francisco",
    "Boa Esperança",
    "Bom Jesus do Norte",
    "Brejetuba",
    "Cachoeiro de Itapemirim",
    "Cariacica",
    "Castelo",
    "Colatina",
    "Conceição da Barra",
    "Conceição do Castelo",
    "Divino de São Lourenço",
    "Domingos Martins",
    "Dores do Rio Preto",
    "Ecoporanga",
    "Fundão",
    "Governador Lindenberg",
    "Guaçuí",
    "Guarapari",
    "Ibatiba",
    "Ibiraçu",
    "Ibitirama",
    "Iconha",
    "Irupi",
    "Itaguaçu",
    "Itapemirim",
    "Itarana",
    "Iúna",
    "Jaguaré",
    "Jerônimo Monteiro",
    "João Neiva",
    "Laranja da Terra",
    "Linhares",
    "Mantenópolis",
    "Marataízes",
    "Marechal Floriano",
    "Marilândia",
    "Mimoso do Sul",
    "Montanha",
    "Mucurici",
    "Muniz Freire",
    "Muqui",
    "Nova Venécia",
    "Pancas",
    "Pedro Canário",
    "Pinheiros",
    "Piúma",
    "Ponto Belo",
    "Presidente Kennedy",
    "Rio Bananal",
    "Rio Novo do Sul",
    "Santa Leopoldina",
    "Santa Maria de Jetibá",
    "Santa Teresa",
    "São Domingos do Norte",
    "São Gabriel da Palha",
    "São José do Calçado",
    "São Mateus",
    "São Roque do Canaã",
    "Serra",
    "Sooretama",
    "Vargem Alta",
    "Venda Nova do Imigrante",
    "Viana",
    "Vila Pavão",
    "Vila Valério",
    "Vila Velha",
    "Vitória"
]


def extract_city(header: str) -> Optional[str]:
    """
    Extrai o nome da cidade do cabeçalho do documento.
    
    Args:
        header: Texto do cabeçalho para buscar a cidade
        
    Returns:
        Nome da cidade encontrada ou None
    """
    header_upper = header.upper()
    for city in CITIES_ES:
        if city.upper() in header_upper:
            return city
    return None
