import os
import speech_recognition as sr
import googlemaps
from gtts import gTTS

API_KEY = 'Your_GoogleMaps_API_Key'

SAIR = 'SAIR'
INICIAR_INTERACAO = 'INICIAR_INTERACAO'
PROCURAR_ESTABELECIMENTO = 'PROCURAR_ESTABELECIMENTO'
OBTER_DETALHES = 'OBTER_DETALHES'

intencao = INICIAR_INTERACAO

gmaps = googlemaps.Client(API_KEY)
texto_busca = ''
localizacao = (-25.50126708932149, -49.237472946625495)
locais = []

#Função para ouvir e reconhecer a fala
def ouvir_microfone():
    #Habilita o microfone do usuário
    microfone = sr.Recognizer()
    frase = ''
    #usando o microfone
    with sr.Microphone() as source:
        
        #Chama um algoritmo de reducao de ruidos no som
        microfone.adjust_for_ambient_noise(source)
        
        #Frase para o usuario dizer algo
        print("Diga alguma coisa: ")
        
        #Armazena o que foi dito numa variavel
        audio = microfone.listen(source)
        
    try:
        #Passa a variável para o algoritmo reconhecedor de padroes
        frase = microfone.recognize_google(audio,language='pt-BR')
        
        #Retorna a frase pronunciada
        print("Você disse: " + frase)
        
    #Se nao reconheceu o padrao de fala, exibe a mensagem
    except sr.UnknownValueError:
        exibe_ou_fala("Não entendi")
        
    return frase

def processar_frase(frase):
    result = 'NAO_IDENTIFICADO'

    if ("reiniciar" in frase) or ("começar" in frase):
        result = INICIAR_INTERACAO

    elif ("encerrar" in frase) or ("sair" in frase):
        result = SAIR

    elif any(substring in frase.lower() for substring in ['procur', 'encontr', 'busca', 'busque'] ):
        estabelecimento, local = identificar_busca(frase)
        global locais
        locais = procurar_estabelecimentos(localizacao, estabelecimento)
        result = PROCURAR_ESTABELECIMENTO

    elif any(substring in frase.lower() for substring in ['telefone', 'site'] ):
        processar_busca_detalhes(frase)
        result = OBTER_DETALHES

    return result

def identificar_busca(frase):
    palavras = frase.split()

    concat_estabelecimento = False
    concat_local = False

    estabelecimento = ''
    local = ''

    for palavra in palavras:
        if any(substring in palavra.lower() for substring in ['procur', 'encontr', 'busca', 'busque', 'uma', 'um', 'por'] ):
            concat_estabelecimento = True
            concat_local = False
        elif any(substring in palavra.lower() for substring in ['em','na','no','perto','aqui','daqui'] ):
            concat_estabelecimento = False
            concat_local = True
        elif concat_estabelecimento:
            estabelecimento = estabelecimento + palavra + " "
        elif concat_local:
            local = local + palavra + " "
    #TODO: utilizar a localidade falada pelo usuário e buscar as coordenadas com a API do google
    return estabelecimento, local

def processar_busca_detalhes(frase):
    palavras = frase.split()

    exibir_fone = False
    exibir_site = False
    concat_estabelecimento = False
    estabelecimento = ''

    if "telefone" in frase:
        exibir_fone = True
    if "site" in frase:
        exibir_site = True

    for palavra in palavras:
        if any(substring in palavra.lower() for substring in ['da','do'] ):
            concat_estabelecimento = True
        elif concat_estabelecimento:
            if estabelecimento == "":
                estabelecimento = palavra
            else:
                estabelecimento = estabelecimento + " " + palavra

    id_estabelecimento = ''
    for local in locais:
        if estabelecimento.lower() in local['name'].lower():
            id_estabelecimento = local['place_id']

    if id_estabelecimento == '':
        exibe_ou_fala('Não consegui identificar o estabelecimento desejado')
    else:
        detalhes = obter_detalhes_estabelecimento(id_estabelecimento)
        resposta = ''

        if exibir_fone:
            resposta = resposta + 'Telefone: ' + detalhes['formatted_phone_number']
        if exibir_site:
            resposta = resposta + 'Website: ' + detalhes['website']
        
        exibe_ou_fala(resposta)


def procurar_estabelecimentos(localizacao, texto):
    resp = gmaps.places_nearby(
        location=localizacao,
        keyword=texto,
        radius=1000
    )

    return resp.get('results')

def obter_detalhes_estabelecimento(id):
    resp = gmaps.place(
        place_id=id,
        language='pt-BR'
    )

    return resp.get('result')

def exibe_ou_fala(texto):
    audio = gTTS(text=texto, lang="pt-BR", slow=False)
    audio.save("resultado.mp3")
    os.system("start resultado.mp3")    
    print(texto)



while (intencao != SAIR):
    if intencao == INICIAR_INTERACAO:
        locais = []
        exibe_ou_fala("O que você deseja que eu busque?")

    frase = ouvir_microfone()
    intencao = processar_frase(frase)
    
    if (intencao == PROCURAR_ESTABELECIMENTO):
        locais_encontrados = 'Estes são os locais que eu encontrei: '
        for local in locais:
            locais_encontrados = locais_encontrados + local['name'] + '.\n'
        exibe_ou_fala(locais_encontrados)

