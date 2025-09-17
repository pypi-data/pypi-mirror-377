# csv_parser_utils/main.py

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

def contar_linhas(caminho_arquivo):
    """
    Lê um arquivo CSV e retorna o número de linhas de dados (excluindo o cabeçalho).

    Args:
        caminho_arquivo (str): O caminho para o arquivo CSV.

    Returns:
        int: O número de linhas de dados.
    """
    try:
        df = pd.read_csv(caminho_arquivo)
        return len(df)
    except FileNotFoundError:
        print(f"Erro: O arquivo '{caminho_arquivo}' não foi encontrado.")
        return 0

def calcular_media_coluna(caminho_arquivo, nome_coluna):
    """
    Lê um arquivo CSV e calcula a média de uma coluna específica.

    Args:
        caminho_arquivo (str): O caminho para o arquivo CSV.
        nome_coluna (str): O nome da coluna a ser calculada.

    Returns:
        float: A média da coluna, ou 0 se a coluna não for numérica
               ou se o arquivo não for encontrado.
    """
    try:
        df = pd.read_csv(caminho_arquivo)
        if nome_coluna in df.columns:
            coluna_numerica = pd.to_numeric(df[nome_coluna], errors='coerce')
            return coluna_numerica.mean()
        else:
            print(f"Erro: A coluna '{nome_coluna}' não foi encontrada no arquivo.")
            return 0
    except FileNotFoundError:
        print(f"Erro: O arquivo '{caminho_arquivo}' não foi encontrado.")
        return 0

def obter_resumo_estatistico(caminho_arquivo, nome_coluna):
    """
    Lê um arquivo CSV e retorna um resumo estatístico de uma coluna.

    Args:
        caminho_arquivo (str): O caminho para o arquivo CSV.
        nome_coluna (str): O nome da coluna a ser analisada.

    Returns:
        pandas.Series: Um resumo estatístico da coluna.
    """
    try:
        df = pd.read_csv(caminho_arquivo)
        if nome_coluna in df.columns:
            return df[nome_coluna].describe()
        else:
            print(f"Erro: A coluna '{nome_coluna}' não foi encontrada no arquivo.")
            return pd.Series()
    except FileNotFoundError:
        print(f"Erro: O arquivo '{caminho_arquivo}' não foi encontrado.")
        return pd.Series()

def plotar_histograma(caminho_arquivo, nome_coluna, caminho_saida="histograma.png"):
    """
    Cria e salva um histograma de uma coluna numérica.

    Args:
        caminho_arquivo (str): O caminho para o arquivo CSV.
        nome_coluna (str): O nome da coluna a ser plotada.
        caminho_saida (str): O caminho para salvar a imagem do histograma.
    """
    try:
        df = pd.read_csv(caminho_arquivo)
        if nome_coluna in df.columns:
            plt.figure(figsize=(10, 6))
            sns.histplot(data=df, x=nome_coluna, kde=True)
            plt.title(f"Distribuição de '{nome_coluna}'")
            plt.xlabel(nome_coluna)
            plt.ylabel("Frequência")
            plt.savefig(caminho_saida)
            plt.close()
            print(f"Histograma salvo em '{caminho_saida}'.")
        else:
            print(f"Erro: A coluna '{nome_coluna}' não foi encontrada no arquivo.")
    except FileNotFoundError:
        print(f"Erro: O arquivo '{caminho_arquivo}' não foi encontrado.")