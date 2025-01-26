import os
import requests
import pandas as pd
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY')
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"

# Lista de TVs e suas zonas para referência
TV_ZONES = {
    'BH1': ['3990_400_001', '3990_400_003', '3990_400_004', '3990_400_005', '3990_400_007', '3990_400_008', 
            '3990_400_009', '3990_400_010', '3990_400_011', '3990_400_012', '3990_400_013', '3990_400_014'],
    'JZF': ['3990_401_021', '3990_401_022', '3990_401_023', '3990_401_024', '3990_401_025', '3990_401_026',
            '3990_401_027', '3990_401_028', '3990_401_029', '3990_401_030'],
    'TRG': ['3990_402_041', '3990_402_043', '3990_402_044', '3990_402_046', '3990_402_047', '3990_402_048',
            '3990_402_049', '3990_402_050', '3990_402_051', '3990_402_052', '3990_402_054', '3990_402_056'],
    'MGS': ['3990_403_061', '3990_403_062', '3990_403_063', '3990_403_064', '3990_403_066', '3990_403_071',
            '3990_403_072', '3990_403_073', '3990_403_074', '3990_403_075', '3990_403_076', '3990_403_077',
            '3990_403_078', '3990_403_079'],
    'MGL': ['3990_404_082', '3990_404_083', '3990_404_084', '3990_404_085', '3990_404_086', '3990_404_087',
            '3990_404_090', '3990_404_091', '3990_404_092', '3990_404_093', '3990_404_094', '3990_404_095'],
    'BSB': ['3990_405_101', '3990_405_102', '3990_405_104', '3990_405_105', '3990_405_106', '3990_405_107',
            '3990_405_108', '3990_405_109', '3990_405_110', '3990_405_116', '3990_405_117', '3990_405_118'],
    'CGR': ['3990_406_130', '3990_406_131', '3990_406_132', '3990_406_133', '3990_406_134', '3990_406_135',
            '3990_406_136', '3990_406_137', '3990_406_138', '3990_406_139', '3990_406_140', '3990_406_141',
            '3990_406_142'],
    'CBA': ['3990_407_141', '3990_407_142', '3990_407_143', '3990_407_145', '3990_407_146', '3990_407_147',
            '3990_407_148', '3990_407_149', '3990_407_150', '3990_407_151', '3990_407_152', '3990_407_153',
            '3990_407_154', '3990_407_155', '3990_407_156', '3990_407_157'],
    'GO': ['3990_410_180', '3990_410_181', '3990_410_182', '3990_410_183', '3990_410_184', '3990_410_185',
           '3990_410_186', '3990_410_187', '3990_410_188', '3990_410_189', '3990_410_190', '3990_410_192',
           '3990_410_193']
}

def get_date_range():
    """Get the date range for the previous week (Monday to Friday)"""
    current_date = datetime.now()
    
    # Encontrar a última segunda-feira
    days_until_monday = current_date.weekday()  # 0 = Segunda, 1 = Terça, ..., 6 = Domingo
    if days_until_monday == 6:  # Se é domingo
        days_until_monday = 13  # Volta 13 dias (para pegar segunda da semana anterior)
    else:
        days_until_monday += 7  # Volta 7 dias + dias até segunda
    
    last_monday = current_date - timedelta(days=days_until_monday)
    last_friday = last_monday + timedelta(days=4)  # 4 dias após segunda = sexta
    
    return last_monday.strftime('%d/%m/%Y'), last_friday.strftime('%d/%m/%Y')

def extract_section(text, section_name, next_section=None):
    """Extract a section from the text between section_name and next_section"""
    try:
        start = text.index(section_name) + len(section_name)
        if next_section:
            end = text.index(next_section)
            content = text[start:end]
        else:
            content = text[start:]
        return [line.strip() for line in content.strip().split('\n') if line.strip()]
    except ValueError:
        return []

def analyze_data(file_path):
    """
    Analyze data from the uploaded file using Deepseek API
    """
    try:
        # Read the file
        if file_path.endswith('.csv'):
            df = pd.read_csv(file_path)
        else:  # xlsx
            df = pd.read_excel(file_path)
        
        start_date, end_date = get_date_range()
        
        # Preparar análise dos dados
        data_analysis = {
            'total_rows': len(df),
            'columns': df.columns.tolist(),
            'variations': {
                'tvs': {},
                'zones': {}
            }
        }

        # Analisar variações por TV e suas zonas
        for tv, zones in TV_ZONES.items():
            # Análise da TV (média das zonas)
            tv_data = df[df.iloc[:, 0].isin(zones)]
            if not tv_data.empty:
                # Calcular variação da TV em relação ao período anterior
                tv_latest = float(tv_data.iloc[:, -1].mean() * 100)  # último dia em %
                tv_first = float(tv_data.iloc[:, 1].mean() * 100)    # primeiro dia em %
                tv_variation = tv_latest - tv_first
                
                data_analysis['variations']['tvs'][tv] = {
                    'initial': f"{tv_first:.1f}",
                    'final': f"{tv_latest:.1f}",
                    'variation': f"{tv_variation:.1f}",
                    'target_diff': f"{(tv_latest - 95):.1f}"
                }
                
                # Análise individual das zonas
                zone_variations = []
                for zone in zones:
                    zone_data = df[df.iloc[:, 0] == zone]
                    if not zone_data.empty:
                        zone_latest = float(zone_data.iloc[0, -1] * 100)  # último dia em %
                        zone_first = float(zone_data.iloc[0, 1] * 100)    # primeiro dia em %
                        zone_variation = zone_latest - zone_first
                        
                        zone_info = {
                            'code': zone,
                            'initial': f"{zone_first:.1f}",
                            'final': f"{zone_latest:.1f}",
                            'variation': f"{zone_variation:.1f}",
                            'target_diff': f"{(zone_latest - 95):.1f}"
                        }
                        zone_variations.append(zone_info)
                
                # Ordenar zonas por variação (maior queda primeiro)
                zone_variations.sort(key=lambda x: float(x['variation']))
                
                # Pegar as 3 zonas com maior impacto
                critical_zones = zone_variations[:3] if tv_variation < 0 else zone_variations[-3:]
                
                data_analysis['variations']['zones'].update({
                    zone['code']: {
                        'tv': tv,
                        'initial': zone['initial'],
                        'final': zone['final'],
                        'variation': zone['variation'],
                        'target_diff': zone['target_diff']
                    } for zone in critical_zones
                })
        
        # Prepare the prompt for Deepseek
        prompt = f"""Você é um analista especializado em métricas de performance. Analise os dados fornecidos e gere um diagnóstico detalhado seguindo EXATAMENTE o formato abaixo.

        ESTRUTURA DOS DADOS:
        - Coluna A: Códigos das zonas organizados por TV (território)
        - Colunas B a F: Dados de performance diária (5 dias consecutivos)
        - Total de 116 zonas distribuídas entre as TVs
        - Target geral de performance: 95%

        IMPORTANTE:
        1. Para cada TV, indique:
           - Performance inicial (primeiro dia) e final (último dia)
           - Variação em p.p. (ganho ou perda)
           - Zonas que mais contribuíram para a queda/aumento
           - Diferença atual em relação ao target de 95%
        2. Para cada zona crítica:
           - Performance inicial e final
           - Variação em p.p.
           - Impacto na performance da TV

        ===== INÍCIO DO FORMATO =====

        Raio-X e Diagnóstico ({start_date} - {end_date})

        Resumo Geral:
        • Performance global das TVs
        • Principais variações no período
        • Gaps em relação ao target
        • TVs que demandam atenção imediata

        Análise por TV:

        1. TVs com Quedas:
        Para cada TV:
        • Nome do TV: iniciou a semana com X% e fechou com Y%, perdeu/ganhou Z p.p.
        • Em relação ao target de 95% está W p.p. abaixo/acima
        • Zonas que mais impactaram a queda:
            - Código: iniciou a semana com X% e fechou com Y%, perdeu Z p.p.
            - Código: iniciou a semana com X% e fechou com Y%, perdeu Z p.p.
        
        2. TVs Estáveis:
        Para cada TV:
        • Nome do TV: manteve-se entre X% e Y%, variação de ±Z p.p.
        • Em relação ao target de 95% está W p.p. abaixo/acima

        3. TVs com Avanços:
        Para cada TV:
        • Nome do TV: iniciou a semana com X% e fechou com Y%, ganhou Z p.p.
        • Em relação ao target de 95% está W p.p. abaixo/acima
        • Zonas que mais contribuíram:
            - Código: iniciou a semana com X% e fechou com Y%, ganhou Z p.p.
            - Código: iniciou a semana com X% e fechou com Y%, ganhou Z p.p.

        Ações Necessárias:
        Para cada TV crítica:
        • Nome do TV:
            - Principais zonas que precisam de atenção
            - Gaps específicos a serem fechados
            - Ações sugeridas para recuperação

        Conclusões:
        • Resumo das principais variações
        • Gaps mais relevantes
        • Oportunidades de melhoria

        Próximos Passos:
        • Prioridades por TV
        • Metas de recuperação
        • Pontos de monitoramento

        ===== FIM DO FORMATO =====

        Dados para análise:
        {data_analysis}

        Lembre-se:
        1. Use bullets (•) para todos os itens
        2. Mantenha a estrutura exata das seções
        3. SEMPRE use o formato "iniciou com X% e fechou com Y%, perdeu/ganhou Z p.p."
        4. SEMPRE especifique a diferença em relação ao target como "está W p.p. abaixo/acima do target"
        5. Priorize as zonas que mais impactaram o resultado da TV
        """

        # Make API request
        headers = {
            "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "deepseek-chat",
            "messages": [
                {"role": "system", "content": "Você é um analista especializado em métricas de performance, focado em análises detalhadas e estruturadas."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 3000
        }

        response = requests.post(DEEPSEEK_API_URL, headers=headers, json=payload)
        response.raise_for_status()
        
        # Extract the analysis
        analysis = response.json()['choices'][0]['message']['content']
        
        # Extract sections using the helper function
        diagnostic = {
            'titulo': f"Raio-X e Diagnóstico ({start_date} - {end_date})",
            'resumo': extract_section(analysis, "Resumo Geral:", "Análise por TV:"),
            'analise_por_tv': {
                'quedas': extract_section(analysis, "1. TVs com Quedas:", "2. TVs Estáveis:"),
                'estaveis': extract_section(analysis, "2. TVs Estáveis:", "3. TVs com Avanços:"),
                'avancos': extract_section(analysis, "3. TVs com Avanços:", "Ações Necessárias:")
            },
            'acoes_necessarias': extract_section(analysis, "Ações Necessárias:", "Conclusões:"),
            'conclusoes': extract_section(analysis, "Conclusões:", "Próximos Passos:"),
            'proximos_passos': extract_section(analysis, "Próximos Passos:", "===== FIM DO FORMATO =====")
        }
        
        return diagnostic
        
    except Exception as e:
        print(f"Erro na análise: {str(e)}")
        return {
            'titulo': f"Raio-X e Diagnóstico ({start_date} - {end_date})",
            'resumo': ["• Erro na análise dos dados"],
            'analise_por_tv': {
                'quedas': ["• Não foi possível analisar as quedas"],
                'estaveis': ["• Não foi possível analisar a estabilidade"],
                'avancos': ["• Não foi possível analisar os avanços"]
            },
            'acoes_necessarias': [f"• Erro: {str(e)}"],
            'conclusoes': ["• Por favor, verifique o formato dos dados e tente novamente."],
            'proximos_passos': ["• Verificar se o arquivo está no formato correto",
                              "• Garantir que todas as colunas necessárias estão presentes",
                              "• Verificar se há dados suficientes para análise"]
        }
