# IMPORTS:
import random

# Listas para geração randômica de frases:
#   - adjunto + sujeito + verbo + complemento [+ conexão].
adjuntos = [
    "ainda hoje",
    "em tempo hábil",
    "de forma estratégica",
    "através de uma abordagem holística",
    "com foco no core business",
    "visando a otimização de recursos",
    "nesse sentido",
    "de forma sinérgica",
    "com a finalidade de",
    "em caráter de urgência",
    "na prática",
    "de forma proativa",
    "em resumo",
    "pensando na performance",
    "para garantir o alinhamento",
    "considerando o cenário atual",
    "buscando a excelência",
    "no contexto do nosso escopo",
    "a fim de mitigar riscos",
    "para alavancar resultados",
    "com base nas melhores práticas",
    "olhando para o futuro",
    "com o objetivo de",
    "em última análise",
    "no âmbito de nossas atividades",
    "sob o ponto de vista da governança",
    "dentro da nossa visão de futuro",
    "para assegurar a consistência",
    "visando a redução de custos",
    "no que tange à usabilidade",
    "pensando na experiência do cliente",
    "com o intuito de inovar",
    "para garantir a sustentabilidade",
    "diante do novo cenário",
    "em face dos desafios",
    "com uma visão 360",
    "através de uma análise criteriosa",
    "em um esforço conjunto",
    "para potencializar a performance",
    "considerando a nossa missão",
    "com a devida diligência",
    "em prol da sinergia",
    "buscando um novo paradigma",
    "na medida em que evoluímos",
    "para garantir a eficiência operacional",
    "tendo em vista o nosso planejamento",
    "com o olhar no futuro",
    "no cenário de transformação digital",
    "para maximizar o retorno sobre o investimento",
    "olhando para o ciclo de vida do produto",
    "de modo a garantir a aderência",
    "com o propósito de agregar valor",
    "para viabilizar a implantação"
]
sujeitos = [
    "a sinergia das equipes",
    "a inovação disruptiva",
    "o roadmap do projeto",
    "a governança corporativa",
    "o benchmarking do mercado",
    "a escalabilidade da solução",
    "o novo paradigma",
    "a usabilidade da interface",
    "o engajamento dos stakeholders",
    "o capital intelectual",
    "o mindset de crescimento",
    "a proatividade do time",
    "a melhoria contínua",
    "a performance do negócio",
    "o alinhamento estratégico",
    "a arquitetura da informação",
    "a visão de futuro",
    "a entrega de valor",
    "a capacidade de adaptação",
    "o planejamento holístico",
    "o ecossistema de parceiros",
    "a diligência do processo",
    "o design thinking",
    "o fluxo de trabalho",
    "a análise preditiva",
    "o ciclo de vida do produto",
    "o retorno sobre o investimento (ROI)",
    "a metodologia ágil",
    "o ambiente colaborativo",
    "o processo de onboarding",
    "a gestão de projetos",
    "a cultura organizacional",
    "o feedback contínuo",
    "o plano de ação",
    "o diferencial competitivo",
    "a tecnologia de ponta",
    "o nicho de mercado",
    "a experiência do usuário (UX)",
    "a curva de aprendizado",
    "a comunicação assertiva",
    "a sustentabilidade do negócio",
    "o know-how da equipe",
    "a base de conhecimento",
    "o ponto de contato",
    "a estratégia de marketing",
    "o funil de vendas",
    "a otimização de recursos",
    "a inteligência de mercado",
    "o framework de trabalho",
    "a jornada do cliente",
    "o nível de maturidade"
]
verbos = [
    "está potencializando",
    "precisa ser alinhada com",
    "dá o start para",
    "vai convergir com",
    "desmistifica",
    "desafia",
    "vai impactar",
    "alavanca",
    "está otimizando",
    "fortalece",
    "integra",
    "vai consolidar",
    "direciona",
    "permite",
    "agrega valor",
    "conecta com",
    "garante",
    "facilita",
    "otimiza",
    "busca aprimorar",
    "gera sinergia",
    "impulsiona",
    "promove",
    "catalisa",
    "viabiliza",
    "maximiza",
    "assegura",
    "complementa",
    "reformula",
    "engaja",
    "padroniza",
    "consiste em",
    "reflete",
    "antecipa",
    "dimensiona",
    "estrutura",
    "prioriza",
    "reforça",
    "contribui para",
    "cria um novo panorama para",
    "está remodelando",
    "tem como objetivo",
    "é fundamental para",
    "está aprimorando",
    "impulsiona",
    "está transformando",
    "vai gerar um impacto em",
    "está se tornando um diferencial em",
    "é a base para",
    "revela a importância"
]
complementos = [
    "a melhoria contínua dos processos",
    "a otimização de recursos",
    "as métricas de sucesso",
    "o engajamento dos stakeholders",
    "o core business da empresa",
    "o novo mindset da equipe",
    "o ciclo de vida do produto",
    "a experiência do usuário",
    "a nossa visão de futuro",
    "o sucesso da iniciativa",
    "a usabilidade da plataforma",
    "o processo de tomada de decisão",
    "as nossas necessidades de negócio",
    "a nossa capacidade de execução",
    "a nossa maturidade digital",
    "o nosso planejamento estratégico",
    "a cultura de inovação",
    "o retorno sobre o investimento (ROI)",
    "as nossas atividades diárias",
    "o fluxo de informações",
    "a gestão da mudança",
    "os objetivos de curto e longo prazo",
    "o ambiente de trabalho",
    "os novos paradigmas do mercado",
    "a comunicação interdepartamental",
    "a performance do time",
    "o fluxo de caixa",
    "as metas de faturamento",
    "a competitividade no mercado",
    "a proatividade dos colaboradores",
    "os padrões de qualidade",
    "a sustentabilidade do negócio",
    "a jornada de crescimento",
    "o alinhamento de expectativas",
    "os novos modelos de negócio",
    "a nossa base de conhecimento",
    "a satisfação do cliente",
    "a escalabilidade do projeto",
    "o planejamento de metas",
    "os padrões de excelência",
    "a análise de dados",
    "a viabilidade técnica",
    "o desempenho das vendas",
    "a nossa infraestrutura tecnológica",
    "a nossa capacidade de entrega",
    "o funil de conversão",
    "o relacionamento com o cliente",
    "a evolução do nosso produto",
    "o nosso posicionamento de mercado",
    "o nosso modelo de gestão"
]
conexoes = [
    ", enquanto isso",
    " e,",
    ", portanto",
    ", além disso",
    ", ainda assim,",
    ", e é possível também que",
    ", podendo também dizer que,",
    ", podendo também afirmar que",
    ", e se não bastasse isso,"
]

def gerar_frase(tamanho=1):
    """
    Gera uma frase de lero-lero com um tamanho específico.
    O tamanho se refere ao número de 'segmentos' na frase.
    Cada segmento é composto por: adjunto + sujeito + verbo + complemento [+ conexão].
    Ex: tamanho=2 -> 'Adjunto1 sujeito1 verbo1 complemento1 conexão1, adjunto2 sujeito2 verbo2 complemento2.'
    """
    if tamanho < 1:
        return ""

    frase_final = []
    
    for i in range(0, tamanho, 1):
        segmento = (
            random.choice(adjuntos) + " " +
            random.choice(sujeitos) + " " +
            random.choice(verbos) + " " +
            random.choice(complementos)
        )
        if i < tamanho-1:
            segmento += random.choice(conexoes)
        frase_final.append(segmento)

    # Conecta os segmentos com espaços:
    frase_completa = " ".join(frase_final) + "."
    
    # Capitaliza a primeira letra e adiciona um ponto final
    return frase_completa[0].upper() + frase_completa[1:]


def gerar_texto(num_frases=1, tamanho_min=1, tamanho_max=1):
    """
    Gera um parágrafo de lero-lero com múltiplas frases.
    Cada frase terá um tamanho aleatório entre tamanho_min e tamanho_max.
    """
    # Verifica e corrige a ordem dos tamanhos
    if tamanho_min > tamanho_max:
        tamanho_min, tamanho_max = tamanho_max, tamanho_min
    texto = ""
    for _ in range(num_frases):
        tamanho_frase = random.randint(tamanho_min, tamanho_max)
        texto += " " + gerar_frase(tamanho_frase)
    
    return texto.strip()