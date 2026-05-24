import matplotlib.pyplot as plt
import io

def gerar_mapa_png():
    """
    Gera uma imagem estática (PNG) com a distribuição dos campi.
    Estilo: Monocromático Escuro com Destaques Claros.
    """
    # Coordenadas (Latitude, Longitude)
    campi = [
        {'sigla': 'AP', 'nome': 'Apucarana', 'lat': -23.55, 'lon': -51.46},
        {'sigla': 'CM', 'nome': 'Campo Mourão', 'lat': -24.04, 'lon': -52.38},
        {'sigla': 'CP', 'nome': 'Cornélio Procópio', 'lat': -23.18, 'lon': -50.65},
        {'sigla': 'CT', 'nome': 'Curitiba', 'lat': -25.44, 'lon': -49.27},
        {'sigla': 'DV', 'nome': 'Dois Vizinhos', 'lat': -25.74, 'lon': -53.05},
        {'sigla': 'FB', 'nome': 'Francisco Beltrão', 'lat': -26.07, 'lon': -53.05},
        {'sigla': 'GP', 'nome': 'Guarapuava', 'lat': -25.39, 'lon': -51.46},
        {'sigla': 'LD', 'nome': 'Londrina', 'lat': -23.30, 'lon': -51.16},
        {'sigla': 'MD', 'nome': 'Medianeira', 'lat': -25.29, 'lon': -54.09},
        {'sigla': 'PB', 'nome': 'Pato Branco', 'lat': -26.22, 'lon': -52.67},
        {'sigla': 'PG', 'nome': 'Ponta Grossa', 'lat': -25.09, 'lon': -50.16},
        {'sigla': 'SH', 'nome': 'Santa Helena', 'lat': -24.85, 'lon': -54.33},
        {'sigla': 'TD', 'nome': 'Toledo', 'lat': -24.72, 'lon': -53.74}
    ]

    # Configuração do Plot (Estilo Dark)
    plt.style.use('dark_background')
    fig, ax = plt.subplots(figsize=(10, 8))
    
    # Remover eixos
    ax.axis('off')
    
    # Plotar Pontos
    lats = [c['lat'] for c in campi]
    lons = [c['lon'] for c in campi]
    
    # Scatter plot (Cor clara: #ffd700/Gold ou White)
    ax.scatter(lons, lats, c='#FFD700', s=150, alpha=0.9, edgecolors='white', linewidth=1.5, zorder=2)
    
    # Adicionar Labels
    for c in campi:
        ax.annotate(c['sigla'], (c['lon'], c['lat']), 
                    xytext=(8, 8), textcoords='offset points',
                    color='white', fontsize=9, fontweight='bold', fontname='Arial')

    # Título (opcional, pode ser removido se for para PDF)
    # ax.set_title("UTFPR - Distribuição de Campi", color='white', pad=20)
    
    # Ajustar limites para parecer "Zoomed in" no PR
    # Margem simples
    ax.set_xlim(min(lons) - 1, max(lons) + 1)
    ax.set_ylim(min(lats) - 1, max(lats) + 1)
    
    # Salvar em BytesIO
    img_buffer = io.BytesIO()
    plt.savefig(img_buffer, format='png', transparent=True, dpi=150)
    img_buffer.seek(0)
    plt.close()
    
    return img_buffer

if __name__ == "__main__":
    # Teste local
    buf = gerar_mapa_png()
    with open("mapa_teste.png", "wb") as f:
        f.write(buf.getbuffer())
    print("Mapa gerado: mapa_teste.png")
