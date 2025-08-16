import os
from langchain_groq import ChatGroq
from langchain.prompts import ChatPromptTemplate
from dotenv import load_dotenv
from langchain_tavily import TavilySearch
import time

load_dotenv()


GROQ_API_KEY = os.getenv("GROQ_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

chat = ChatGroq(model="llama3-70b-8192")


#! Função para gerar a resposta do bot com base no texto enviado pelo usuário
def resposta_bot(documento_para_analise):
    if not documento_para_analise:
        return "⚠️ Nenhuma informação carregada. Tente enviar novamente."

    system_prompt = '''Você é um assistente que verifica textos. Seu objetivo é analisar o texto que o usuário mandou,
e verificar se esse texto é de algum site da internet. Você trabalhará com um sistema de pontuação, de 0 a 100. Quanto maior a pontuação,
maior a chance de ser um texto plagiado, quanto menor, menor a chance de ser plagiado. Essa pontuação se dá com base da similaridade do
texto com algum da internet. Se houver algum trecho na internet idêntico ao texto enviado, a pontuação será de 100, se houver muita similaridade,
a pontuação será entre 50 e 99, se houver pouca similaridade, a pontuação será entre 1 e 49, se não houver nenhuma similaridade, a pontuação será 0. 
Você também deve explicar o motivo da pontuação. Se a pontuação for maior que 50, você deve listar os links onde o texto foi encontrado na internet. 
Se a pontuação for menor ou igual a 50, você não precisa listar os links. Use o contexto da busca na internet (se fornecido) para embasar sua análise. 
Na pesquisa, priorize os sites mais confiáveis, como Wikipedia, jornais e revistas. Você que definirá a pontuação e o motivo da pontuação. 
Seja imparcial e objetivo. Seu trabalho é verificar se o texto é plagiado ou não, e não julgar a qualidade do texto.

Exemplo de texto nota 100: 
"A revolução industrial foi um período de grandes mudanças tecnológicas, sociais e econômicas que começou no final do 
século XVIII e se estendeu até o início do século XIX." 
Pontuação: 100 
Motivo: O texto é idêntico a um ou mais textos encontrados na internet. O que é plagiado. 
Links: https://pt.wikipedia.org/wiki/Revolu%C3%A7%C3%A3o_Industrial 
               
Exemplo de texto nota 99 a 50: "A Revolução Industrial, ocorrida na Inglaterra no século XVIII, trouxe avanços tecnológicos que mudaram a economia 
e a sociedade da época." 
Pontuação: 82 
Motivo: O texto tem alta similaridade com textos encontrados na internet. O que é parcialmente plagiado. 
Links: https://pt.wikipedia.org/wiki/Revolu%C3%A7%C3%A3o_Industrial 
             
Exemplo de texto nota 49 a 1: 
Entre 1750 e 1850, a invenção de máquinas a vapor e o crescimento das fábricas na Europa marcaram o início de uma nova era econômica." 
Pontuação: 36 Motivo: O texto tem baixa similaridade com textos encontrados na internet. O que é parcialmente autoral. 
             
Exemplo de texto nota 0: "O desenvolvimento de teares mecânicos em Manchester, aliado ao uso intensivo do carvão, acelerou a produção têxtil 
britânica no final do século XVIII." 
Pontuação: 0 Motivo: O texto não tem similaridade com textos encontrados na internet. O que é autoral. 
             
Responda APENAS no seguinte formato, sem adicionar texto extra antes ou depois: 
Pontuação: <pontuação> 
Motivo: <motivo> 
Links: <links, se houver, ou "Nenhum" caso contrário>'''


    prompt_template = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("user", "{documento}")
    ])


    chain = prompt_template | chat

    try:

        resposta = chain.invoke({"documento": documento_para_analise})
        return resposta.content
    except Exception as e:
        return f"Erro ao gerar resposta: {e}"


#! Função para obter dados do usuário e realizar pesquisa na internet
def obter_dados_para_verificacao():
    texto_usuario = input("Digite o texto que deseja verificar: ").strip()
    if not texto_usuario:
        print("⚠️ Texto vazio. Tente novamente.")
        return None

    documento_final = f"Texto a ser analisado:\n'''{texto_usuario}'''"

    while True:
        escolha = input("Deseja pesquisar na internet para melhorar a análise? (s/n): ").strip().lower()
        if escolha == 's':
            print("\nIniciando pesquisa na internet...")
            try:
                tool = TavilySearch(max_results=5)
                resultados_pesquisa = tool.invoke(texto_usuario)
                print("Pesquisa concluída.")
                documento_final += f"\n\nContexto da pesquisa na internet para comparação:\n'''{str(resultados_pesquisa)}'''"
                return documento_final
            except Exception as e:
                print(f"Houve um erro na busca: {e}")
                return documento_final
        elif escolha == 'n':
            return documento_final
        else:
            print("Opção inválida. Digite 's' ou 'n'.")


def mensagem_inicial():
    print("Olá! Eu sou o Verificador de Plágio.")
    print("Envie um texto para que eu possa verificar se ele é plagiado ou não.\n")
    time.sleep(1)


def verificar_novamente():
    while True:
        novamente = input("\nDeseja verificar outro texto? (s/n): ").strip().lower()
        if novamente == 's':
            return True
        elif novamente == 'n':
            print("Ok, encerrando o programa. Até mais!")
            return False
        else:
            print("Opção inválida. Digite 's' ou 'n'.")


#! Função principal do programa
def main():
    mensagem_inicial()
    
    while True:
        documento_completo = obter_dados_para_verificacao()
        
        if not documento_completo:

            continue


        print("\nAnalisando o texto... Por favor, aguarde.")
        resposta = resposta_bot(documento_completo)
        
        print("\n--- ANÁLISE DO BOT ---")
        print(resposta)
        print("--------------------")

        if not verificar_novamente():
            break


if __name__ == "__main__":
    main()
