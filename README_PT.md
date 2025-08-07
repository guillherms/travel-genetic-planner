# 🧬 Travel Genetic Planner

**Travel Genetic Planner** é um projeto que utiliza um **Algoritmo Genético (AG)** para otimizar o roteiro de uma viagem, encontrando a melhor ordem para visitar pontos turísticos com base na localização geográfica e outras restrições.

---

## 🎯 Objetivo

Minimizar o tempo de deslocamento e organizar um roteiro de viagem eficiente, respeitando horários de funcionamento e preferências do usuário (como locais prioritários).

---

## 📁 Estrutura do Projeto

```
travel-genetic-planner/
app/
├── streamlit_app.py                  # VIEW (interface com usuário)
├── core/
│   ├── api/                          # APIs externas (Google, OpenAI)
│   ├── genetic/                      # Algoritmo Genético
│   ├── model/
│   │   └── file_input_model.py       # Validação de entrada
│   ├── prompt/
│   │   └── templates.py              # Prompt para geração de locais
│   ├── services/
│   │   └── planning_service.py       # CONTROLADOR
│   └── utils/                        # Funções auxiliares
├── data/                             # Arquivos de entrada
|README_PT.md                         # Este arquivo
|requirements.txt                     # Dependências do projeto
|.gitignore
```

---

## ✅ Requisitos

Instale as dependências:

```bash
pip install -r requirements.txt
```

---

## 🚀 Como Utilizar

Execute o app:

```bash
streamlit run app/streamlit_app.py
```

---

## 📌 Passo a passo do código

```markdown
# Fluxo principal do projeto:

1. O usuário insere o nome do hotel.
2. E seleciona se o input inicial será um arquivo com os lugares que seja conhecer ou se deseja uma sugestão. Caso selecione sugestão é realizada requsição para API do OpenAI enviando um prompt de pontos turisticos para lugar informado.
3. Além da consulta API OpenAi é feita uma requisição para API google geocoding retorno a latitude e longitude do hotel
3. Após inserir o arquivo ou receber a resposta da API, usuário pode executar o algotimo genético.
4. O algoritmo genético retorna a melhor caminho para conhecer os pontos turisticos.
4. A melhor solução é exibida em um mapa para cada dia da viagem.
```

---

## 🧠 Perguntas sobre o Algoritmo Genético

### 🧩 O que você está otimizando?
Otimizamos a ordem de execução das tarefas de um projeto de tecnologia, buscando:
- Minimizar o tempo total de entrega
- Maximizar o valor agregado por sprint, com base na prioridade das funcionalidades

---
### 🧬 Qual é a representação da solução (genoma)?
O cromossomo é uma lista ordenada de IDs de pontos turísticos, por exemplo:  
`[1, 2, 6, 3, 4, 5, ...]`


---
### 💡 Função de Fitness

A função de fitness avalia a qualidade de cada roteiro com base em **recompensas positivas** que consideram múltiplos critérios:

#### 📆 Usar menos dias da viagem  
Roteiros que utilizam menos dias (com mais locais por dia) recebem maior pontuação:  
`+ (lugares_total - dias_utilizados) * 200`

#### ⭐ Visitar locais prioritários  
Cada ponto turístico com `priority == 1` visitado rende um bônus:  
`+100 por local prioritário`

#### 🕒 Visitar locais dentro do horário de funcionamento  
Cada local visitado **dentro da janela de funcionamento** rende um bônus adicional:  
`+50 por local no horário`

#### 🛣️ Minimizar deslocamento total  
Quanto menor o tempo total de deslocamento (em minutos), maior a pontuação:  
`+(lugares_total * 30 - tempo_total_de_deslocamento)`  
*(com mínimo de 1 para evitar pontuação negativa)*

---

### 🎯 Qual é o método de seleção?
Utilizamos uma combinação de **elitismo** e **torneio**:
- **Elitismo**: garante que os melhores indivíduos da geração atual sejam mantidos na próxima geração.
- **Torneio**: seleciona os demais pais através de uma competição entre indivíduos aleatórios, favorecendo os mais aptos.

---

### 🔀 Qual método de crossover está implementado?
Order Crossover (OX): preserva a ordem relativa dos pontos turísticos.

---

### 🧪 Qual o método de inicialização?
A população inicial é gerada por embaralhamento aleatório dos pontos turísticos, respeitando eventuais dependências.

---

### 🛑 Qual o critério de parada?
- Estagnação (sem melhora na melhor solução após 5 gerações)

---

## 📮 Contato
- - [LinkedIn](https://www.linkedin.com/in/guilherme-santos-de-oliveira-ba9986161/)
