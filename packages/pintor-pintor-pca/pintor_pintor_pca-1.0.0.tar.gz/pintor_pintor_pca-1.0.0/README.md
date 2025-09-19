# Metodo para Aplicar o PCA


**1. separar as colunas numericas da tabela de dados**

aqui vamos fazer uma separacao das colunas presente na tabela para pegar aquelas colunas que apresentam:
- variaveis que aprensentam um sentido para serem colocadas para fazer o PCA
- variaveis que apresentam uma correlacao suficientemente significante para aplicar o PCA

        df = conjunto de valores numericos separados para aplicar o PCA

**2. aplicar o teste de Hipotese de Bartlett**

`Ho:` a matriz correlacao é uma matriz identidade( ou seja , nao relacionadas)

`Ha:` a matriz correlacao nao é uma matrix identidade

caso passe recusamos a hipotese nula, podemos continuar a aplicacao do metodo de PCA

**3. Aqui que a magica começa. Vamos criar um objeto do FactorAnalyzer() que disponibilizar metodos para conseguirmos aplicar os proximos passos**

        f = FactorAnalyzer()

**3.1. Descobrir os autovalores da matriz**

utilizar o criterio de Kaiser que diz que para cada autovalor > 1 adicionamos um Fator que representaram as nossas combinações lineares do PCA

    ev, v = fa.get_eigenvalues()

`n_autovalores = quantidade de autovalores (ev) > 1`

**3.2. Descoberto os autovalores > 1, aplicamos o metodo:**

- `f` = objetivo criado pelo FactorAnalyzer()
- `n_factors: quantidade de autovalores > 1 `= n_autovalores
- `df` = conjunto de valores numericos separados para aplicar o PCA

        f.set_params( n_factors= n_autovalores, method='principal', rotation = None)
        f.fit(df)

**3.3 Pontuação dos fatores para o conjunto de dados**

    pontuacao_fatores = pd.DataFrame(f.transform(df))
    pontuacao_fatores.columns =  [f"Fator {i+1}" for i, v in enumerate(pontuacao_fatores.columns)]

**4. Informacoes adicionais para complementar as analises do PCA**

`obs:` para conseguir realizar os passos da etapa 4, é necessario ja ter completado os passos anteriores

**4.1 Grafico para observar a Variancia Acumulado que os dados estao representando**

 Com o objeto 'f' ja treinado, vamos criar uma tabela com os valores de:
- autovalor para cada Fator
- Variancia explicada individulmente 
- Variancia acumulada 

        autovalores_dos_fatores = f.get_factor_variance()
        tabela_autovalores_fatores = pd.DataFrame(autovalores_dos_fatores)
        tabela_autovalores_fatores.columns = [f"Fator {i+1}" for i, v in enumerate(tabela_autovalores_fatores.columns)]
        tabela_autovalores_fatores.index = ['Autovalor','Variância', 'Variância Acumulada']
        tabela_autovalores_fatores = tabela_autovalores_fatores.T

com a tabela_autovalores_fatores criada, fazer uma visualizacao grafica 

**4.2. Grafico de Comunalidade explicada pelos Fatores para cada Variave**l

    comunalidades = f.get_communalities()
    tabela_comunalidades = pd.DataFrame(comunalidades)
    tabela_comunalidades.columns = ['Comunalidades']
    tabela_comunalidades.index = df.columns

com a tabela_comunalidades criada, fazer uma visualizacao grafica 

**4.3. Grafico dos Pesos dos Fatores**

    pesos = fa.weights_
    tabela_pesos_fatores = pd.DataFrame(pesos)
    tabela_pesos_fatores.columns = [f"Fator {i+1}" for i, v in enumerate(tabela_pesos_fatores.columns)]
    tabela_pesos_fatores.index = df.columns

com a tabela_pesos_fatores criada, fazer uma visualizacao grafica

**5. Verificacoes**

**5.1 verificar a correlacao das pontuaçoes dos Fatores**

    corr = df.corr()

temos que verificar se nao existe uma correlaçao entre os Fatores, caso exista, algo esta errado

**6. Algumas Aplicações**

**6.1 Criar um ranking**

`obs:` precisa ter construido a tabela: tabela_autovalores_fatores

    df['Rankin'] = 0
    for index, item in enumerate(list(tabela_autovalores_fatores.index)):
        variancia = tabela_autovalores_fatores.loc[item]['Variância']
        df['Ranking'] = df['Ranking'] + df[tabela_autovalores_fatores.index[index]]*variancia

**6.2 Criar um grupo**

`obs:` precisa ter feito um ranking 

        q1 = df['Ranking'].quantile(0.25)
        q3 = df['Ranking'].quantile(0.75)


        df['Grupo'] = 'Mediano'


        df.loc[df['Ranking'] < q1, 'Grupo'] = 'Baixo Desempenho'
        df.loc[df['Ranking'] > q3, 'Grupo'] = 'Alto Desempenho'

