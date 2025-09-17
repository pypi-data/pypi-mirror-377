# tests/test_main.py

import os
import pandas as pd
from csv_parser_utils.main import (
    contar_linhas,
    calcular_media_coluna,
    obter_resumo_estatistico,
    plotar_histograma
)

# Define o caminho do arquivo de teste. A função os.path.join() garante que o caminho funcione em qualquer sistema operacional.
caminho_teste = os.path.join(os.path.dirname(__file__), 'dados_teste.csv')

def test_contar_linhas():
    """Testa se a função contar_linhas retorna o número correto de linhas."""
    assert contar_linhas(caminho_teste) == 4

def test_calcular_media_coluna():
    """Testa se a função calcular_media_coluna calcula a média corretamente."""
    # A média de 85.5, 90.0, 78.2 e 88.0 é 85.425
    assert calcular_media_coluna(caminho_teste, 'Pontuacao') == 85.425

def test_obter_resumo_estatistico():
    """Testa se a função obter_resumo_estatistico retorna uma série do pandas."""
    resumo = obter_resumo_estatistico(caminho_teste, 'Pontuacao')
    assert isinstance(resumo, pd.Series)
    assert resumo['mean'] == 85.425

def test_plotar_histograma():
    """Testa se a função plotar_histograma cria um arquivo de imagem."""
    caminho_saida_teste = 'test_histograma.png'
    plotar_histograma(caminho_teste, 'Pontuacao', caminho_saida_teste)
    
    # Verifica se o arquivo foi criado
    assert os.path.exists(caminho_saida_teste)
    
    # Limpa o arquivo de teste após a verificação
    os.remove(caminho_saida_teste)