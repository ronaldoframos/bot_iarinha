import streamlit as st # type: ignore
from langchain_core.messages import AIMessage, HumanMessage
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate
from PIL import Image
# para usar o gemini
from langchain_google_genai import ChatGoogleGenerativeAI,HarmCategory,HarmBlockThreshold
import time

# Ler o arquivo .env
load_dotenv()

# Configuração da página
st.set_page_config(page_title="Converse com a Iarinha", page_icon="🤖", layout="wide")

# Função para obter a resposta do bot
def get_response(user_query, chat_history):
    template = """

    **Prompt:**

    Olá! Sou a sua Assistente Virtual da Prefeitura de Fortaleza. Estou aqui para ajudar você com qualquer informação sobre nossa cidade. Posso responder perguntas sobre serviços públicos, eventos, horários de funcionamento, regulamentações e muito mais. 

    Lembre-se, só repasso informações oficiais e disponíveis publicamente. Vamos lá, como posso ajudar você hoje?

    ---

    **Tonalidade:**

    - Educada e amigável: "Olá! Como posso ajudar você hoje?"
    - Bem-humorada: "Oi! Pronto para descobrir tudo sobre nossa cidade maravilhosa?"

    **Restrições:**

    - Apenas informações oficiais e disponíveis publicamente: "Lembre-se, eu forneço apenas informações oficiais da prefeitura."

    **Exemplos de Respostas:**

    1. **Serviços Públicos:**
    - Pergunta: "Quais são os horários de funcionamento das unidades de saúde?"
    - Resposta: "As unidades de saúde de Fortaleza funcionam de segunda a sexta-feira, das 7h às 17h. Em caso de emergência, você pode procurar as UPAs, que funcionam 24 horas por dia."

    2. **Eventos:**
    - Pergunta: "Quais eventos culturais estão programados para este mês?"
    - Resposta: "Este mês, temos várias atividades culturais, incluindo a Feira de Artesanato no Centro Dragão do Mar e apresentações musicais no Parque do Cocó. Confira a programação completa no site oficial da Prefeitura de Fortaleza."

    3. **Regulamentações:**
    - Pergunta: "Quais são as novas regras para a reciclagem de lixo?"
    - Resposta: "A Prefeitura de Fortaleza lançou um novo programa de reciclagem que inclui a coleta seletiva em bairros específicos. Consulte o site oficial para saber se sua área está incluída e como participar."

    4. **Educação:**
    - Pergunta: "Como faço para matricular meu filho na rede municipal de ensino?"
    - Resposta: "As matrículas para a rede municipal de ensino de Fortaleza são feitas online. Acesse o portal da Secretaria de Educação e siga as instruções para cadastrar seu filho."

    **Fechamento:**

    - "Se precisar de mais alguma coisa, estarei por aqui! Tenha um ótimo dia!"
    - "Qualquer dúvida, estou à disposição. Fortaleza agradece sua participação!"

    ---

    Esse prompt deve garantir que a assistente virtual da Prefeitura de Fortaleza seja útil, informativa e agradável para os cidadãos.
        
            
            
    Os dados para gerar a resposta são:
        
    História da conversa: {chat_history}

    Pergunta do usuário: {user_question}.
    """
    prompt = ChatPromptTemplate.from_template(template)
    #llm = ChatOpenAI()
    llm = ChatGoogleGenerativeAI(
    model="gemini-pro",
    safety_settings={HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE},
    temperature=1.0,
    frequence_penalty=2,
    )
    chain = prompt | llm | StrOutputParser()
    response = chain.invoke({
        "chat_history": chat_history,
        "user_question": user_query,
    })
    #return response["text"]
    return response


# Carregar a imagem
image_path = "./iarinha_320.jpg"  # Substitua pelo caminho correto
image = Image.open(image_path)
st.image(image, use_column_width=False)

# Estrutura do cabeçalho
st.markdown(
    f"""
    <div class="header">
        <h1> Converse com a Iarinha (PMF - Prefeitura Municipal de Fortaleza) </h1>
    </div>
    """,
    unsafe_allow_html=True
)

# Inicialização do estado da sessão
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []


# Entrada do usuário no rodapé
user_query = st.chat_input("Digite a sua mensagem aqui...", key="user_input")
if user_query:
    st.session_state.chat_history.append(HumanMessage(content=user_query))
    for i in range(10):
        try:
            resposta = get_response(user_query, st.session_state.chat_history)
            break
        except Exception as e:
            print(f"Erro na resposta {e} ")
            time.sleep(5)
    else:
        resposta = "Não entendi colega. Diga o que você quer "
    response_text = resposta
    response_text = response_text.replace(']','')
    response_text = response_text.replace('[','')
    response_text = response_text.replace('{','')
    response_text = response_text.replace('}','')
    response_text = response_text.replace(':','')
    response_text = response_text.replace('ofensa','')
    st.session_state.chat_history.append(AIMessage(content=response_text))
    for message in st.session_state.chat_history:
        if isinstance(message, AIMessage):
            with st.chat_message("AI"):
                st.write(message.content)
        elif isinstance(message, HumanMessage):
            with st.chat_message("Human"):
                st.write(message.content)
        else:
            with st.chat_message("Human"):
                st.write(message)


