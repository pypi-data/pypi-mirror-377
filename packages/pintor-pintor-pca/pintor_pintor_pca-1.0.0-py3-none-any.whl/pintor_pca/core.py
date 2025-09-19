"""
Biblioteca Pessoal para Análise de Componentes Principais (PCA)
Autor: Pedro
Data: Setembro 2025
"""

import pandas as pd
import numpy as np
from factor_analyzer import FactorAnalyzer
from factor_analyzer.factor_analyzer import calculate_bartlett_sphericity


class PintorPintor:
    """
    Classe principal para realizar análise de Componentes Principais (PCA)
    em conjuntos de dados numéricos.
    
    Esta classe fornece métodos para executar todos os passos necessários
    para uma análise PCA completa, desde a preparação dos dados até a
    interpretação dos resultados.
    """
    
    def __init__(self, dados=None):
        """
        Inicializa a classe PintorPCA.
        
        Parâmetros:
        -----------
        dados : pandas.DataFrame, opcional
            DataFrame contendo os dados numéricos para análise PCA.
            Se não fornecido, pode ser definido posteriormente.
        """
        # dados
        self.dados = dados
        self.dados_numericos = None
        # teste de Bartlett
        self.bartlett_result = None
        self.p_value = None
        self.adequado_para_pca = None
        # autovalores
        self.autovalores = None
        self.n_fatores = None
        # pontuação dos componentes principais
        self.pontuacao_fatores = None
        self.dados_com_pontuacao_fatores = None
        
        
        print("✅ Classe PintorPCA inicializada com sucesso!")
        if dados is not None:
            print(f"📊 Dados carregados: {dados.shape[0]} linhas x {dados.shape[1]} colunas")
    
    def __str__(self):
        """Representação em string da classe."""
        print('=' * 40)
        print(" informacoes sobre o Teste de Bartlett \n")
        print(f"Teste de Bartlett: {self.bartlett_result} \n")
        print(f"P-value: {self.p_value} \n")

        print('=' * 40)
        print(" informacoes sobre os autovalores \n")
        print(f"Autovalores: {self.autovalores} \n")
        print(f"Número de fatores: {self.n_fatores} \n")
    
        return f"PintorPCA(dados: {self.dados.shape[0]}x{self.dados.shape[1]}) \n"

        
    
    def __repr__(self):
        """Representação técnica da classe."""
        return self.__str__()
    
    def help_variaveis(self):
        "mostra somente o nome das variaveis da classe"
        print(self.__dict__.keys())
    
    # PASSO 1: Separar as colunas numéricas da tabela de dados
    def separar_colunas_numericas(self, colunas_selecionadas=None):
        """
        Separa as colunas numéricas adequadas para aplicar o PCA.
        
        Parâmetros:
        -----------
        colunas_selecionadas : list, opcional
            Lista com nomes das colunas específicas para usar no PCA.
            Se None, usa todas as colunas numéricas.
        
        Retorna:
        --------
        pandas.DataFrame : DataFrame com colunas numéricas selecionadas
        """
        if self.dados is None:
            raise ValueError("❌ Nenhum dado foi carregado. Forneça dados primeiro.")
        
        if colunas_selecionadas is not None:
            # Usar colunas específicas fornecidas pelo usuário
            df_numericas = self.dados[colunas_selecionadas].copy()
        else:
            # Selecionar automaticamente todas as colunas numéricas
            df_numericas = self.dados.select_dtypes(include=[np.number]).copy()
            print(f"Colunas numéricas selecionadas: {list(df_numericas.columns)}")
        
        # Verificar se temos dados suficientes
        if df_numericas.empty:
            raise ValueError("Nenhuma coluna numérica encontrada nos dados.")
        
        if df_numericas.shape[1] < 2:
            raise ValueError("É necessário pelo menos 2 variáveis numéricas para aplicar PCA.")
        
        # Guardar na classe
        self.dados_numericos = df_numericas
        
        return df_numericas
    
    # PASSO 2: Aplicar o teste de Hipótese de Bartlett
    def teste_bartlett(self, df):
        """
        Aplica o teste de esfericidade de Bartlett.
        
        H0: a matriz correlação é uma matriz identidade (variáveis não relacionadas)
        Ha: a matriz correlação não é uma matriz identidade
        
        Parâmetros:
        -----------
        df : pandas.DataFrame
            DataFrame com dados numéricos para testar
        
        Retorna:
        --------
        tuple : (bartlett_result, p_value, adequado_para_pca)
        """

        try:
            bartlett_result, p_value = calculate_bartlett_sphericity(df)
            
            # Critério: p-value < 0.05 para rejeitar H0
            adequado_para_pca = p_value < 0.05
            
            if adequado_para_pca:
                print(" RESULTADO: Rejeitamos H0. Dados adequados para PCA!")
                print("   As variáveis são suficientemente correlacionadas.")
            else:
                print(" RESULTADO: Não rejeitamos H0. Dados podem não ser adequados para PCA.")
                print("   As variáveis podem ter baixa correlação entre si.")
            
            # Guardar na classe
            self.bartlett_result = bartlett_result
            self.p_value = p_value
            self.adequado_para_pca = adequado_para_pca

            return adequado_para_pca
            
        except Exception as e:
            print(f"Erro no teste de Bartlett: {str(e)}")
            raise
    
    # PASSO 3.1: Descobrir os autovalores da matriz (critério de Kaiser)
    def descobrir_autovalores(self, df):
        """
        Descobre quantos autovalores são > 1 usando o critério de Kaiser.
        
        Parâmetros:
        -----------
        df : pandas.DataFrame
            DataFrame com dados numéricos
        
        Retorna:
        --------
        int : n_fatores
        """
        # Criar um FactorAnalyzer temporário só para calcular autovalores
        fa_temp = FactorAnalyzer()
        fa_temp.fit(df)
        
        # Obter autovalores
        autovalores = fa_temp.get_eigenvalues()[0]  
        
        # Aplicar critério de Kaiser: autovalores > 1
        n_fatores = sum(autovalores > 1)
        
        # Guardar na classe
        self.autovalores = autovalores
        self.n_fatores = n_fatores

        return n_fatores
    
    # PASSO 3.2: Configurar e treinar o FactorAnalyzer
    def configurar_factor_analyzer(self, df, n_fatores):
        """
        Configura e treina o FactorAnalyzer com os parâmetros especificados.
        
        Parâmetros:
        -----------
        df : pandas.DataFrame
            DataFrame com dados numéricos
        n_fatores : int
            Número de fatores (autovalores > 1)
        
        Retorna:
        --------
        FactorAnalyzer : Objeto treinado do FactorAnalyzer
        """
        # Criar e configurar o FactorAnalyzer
        f = FactorAnalyzer()
        f.set_params(n_factors=n_fatores, method='principal', rotation=None)
        
        # Treinar o modelo
        f.fit(df)
        
        return f
    
    # PASSO 3.3: Pontuação dos fatores para o conjunto de dados
    def calcular_pontuacao_fatores(self, df, f):
        """
        Calcula a pontuação dos fatores (transformação dos dados).
        
        Parâmetros:
        -----------
        df : pandas.DataFrame
            DataFrame original com dados numéricos
        f : FactorAnalyzer
            Objeto FactorAnalyzer já treinado
        
        Retorna:
        --------
        pandas.DataFrame : DataFrame com pontuações dos fatores
        """
        # Transformar os dados usando o FactorAnalyzer treinado
        pontuacao_fatores = pd.DataFrame(f.transform(df))
        
        # Nomear as colunas como "Fator 1", "Fator 2", etc.
        pontuacao_fatores.columns = [f"Fator {i+1}" for i in range(pontuacao_fatores.shape[1])]
        
        # Guardar na classe
        self.pontuacao_fatores = pontuacao_fatores
        
        return pontuacao_fatores
    
    # MÉTODO PRINCIPAL: Executa todos os passos do PCA em sequência
    def aplicar_pca(self, colunas_selecionadas=None):
        """
        Executa todos os passos principais do PCA em sequência.
        
        Parâmetros:
        -----------
        colunas_selecionadas : list, opcional
            Lista com nomes das colunas específicas para usar no PCA.
            Se None, usa todas as colunas numéricas.
        
        Retorna:
        --------
        pandas.DataFrame : DataFrame com pontuações dos fatores
        """
        
        try:
            # PASSO 1: Separar colunas numéricas
            df = self.separar_colunas_numericas(colunas_selecionadas)
            
            # PASSO 2: Teste de Bartlett
            adequado = self.teste_bartlett(df)
            
            if not adequado:
                print("\n Nao passou no teste de Hipotese de Bartlett.")
                return None
            
            # PASSO 3.1: Descobrir autovalores
            n_fatores = self.descobrir_autovalores(df)
            
            if n_fatores == 0:
                print("\n Nenhum autovalor > 1 encontrado.")
                return None
            
            # PASSO 3.2: Configurar FactorAnalyzer
            f = self.configurar_factor_analyzer(df, n_fatores)
            
            # PASSO 3.3: Calcular pontuação dos fatores
            pontuacao_fatores = self.calcular_pontuacao_fatores(df, f)

            # PASSO 4: Concatenar os dados originais com a pontuacao dos fatores
            df_concatenado = pd.concat([df, pontuacao_fatores], axis=1)
            
            print("PCA CONCLUIDO COM SUCESSO!")
        
            # Guardar informações importantes na classe
            self.dados_com_pontuacao_fatores = df_concatenado
            
            return pontuacao_fatores
            
        except Exception as e:
            print(f"\n ERRO durante a análise PCA: {str(e)}")
            raise


