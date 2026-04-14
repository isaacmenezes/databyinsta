# 📊 Instagram Data Collector

![Status](https://img.shields.io/badge/Status-Em_Desenvolvimento-yellow?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.9+-3776AB?style=for-the-badge&logo=python&logoColor=white)

## Sobre o Projeto

**Instagram Data Collector** é um projeto acadêmico de **Iniciação Científica** que implementa múltiplas estratégias para coleta, processamento e análise de dados públicos de perfis do Instagram. 

O projeto oferece **três abordagens distintas** para web scraping, cada uma com características e trade-offs únicos:

| Abordagem | Tecnologia | Velocidade | Confiabilidade | Complexidade |
|-----------|-----------|-----------|---------------|----|
| **Selenium** | Automação Browser | Média | Alta | Alta |
| **Instagrapi** | API Simulada | Rápida | Média | Média |
| **Instaloader** | Biblioteca Nativa | Rápida | Alta | Baixa |

---

## 🎯 Objetivo

Comparar diferentes metodologias de coleta de dados do Instagram sob aspectos de:
- **Performance e escalabilidade**
- **Robustez contra bloqueios**
- **Qualidade e completude dos dados**
- **Facilidade de manutenção e extensão**

> **Nota Ética:** Este projeto é estritamente para fins acadêmicos. A coleta respeita os Termos de Serviço do Instagram e utiliza apenas dados públicos.

---

## 🛠️ Tecnologias Utilizadas

### Web Scraping
- **Selenium WebDriver** - Automação de browser com Chrome
- **Instagrapi** - Cliente Python não-oficial do Instagram
- **Instaloader** - Biblioteca especializada em scraping

### Data Processing
- **Pandas** - Manipulação e exportação de dados (CSV/Excel)
- **Python 3.9+** - Linguagem base

### Infrastructure & Config
- **python-dotenv** - Gerenciamento de variáveis de ambiente
- **Logging** - Rastreamento estruturado de operações
- **Git/GitHub** - Versionamento

### Development Tools
- **Type Hints** - Tipagem estática completa
- **Dataclasses** - Estruturação de dados
- **Enums** - Definição de constantes type-safe

---

## 📁 Estrutura do Projeto

```
instagram-data-scraper/
├── selenium/
│   ├── complete_version.py      # Web scraping com automação browser
│   ├── simple_version.py        # Versão simplificada
│   ├── .env                     # Configurações
│   └── scraper.log              # Logs de execução
│
├── instagrapi/
│   ├── instagrapi.py           # Coleta via API simulada (com login)
│   ├── .env                     # Configurações
│   ├── collector.log            # Logs
│   ├── firstlogin_manually.py   # Setup de sessão
│   └── no_login/
│       ├── collector.py        # Coleta sem login (via Session ID) ⭐
│       ├── analysis.py         # Análise de engajamento 📊
│       ├── .env                # Configurações (IG_SESSION_ID)
│       ├── collector.log       # Logs
│       └── output/
│           ├── posts.csv                           # Dados coletados
│           └── analysis/                           # Pasta de análises
│               ├── relatorio.txt                   # Relatório textual
│               ├── 1_engajamento_por_perfil.png
│               ├── 2_distribuicao_engajamento.png
│               ├── 3_hashtags_vs_engajamento.png
│               ├── 4_legenda_vs_engajamento.png
│               └── 5_tipo_post_vs_engajamento.png
│
├── instaloader/
│   ├── instaloader.py          # Coleta em massa
│   ├── .env                     # Configurações
│   ├── bulk_scraper.log        # Logs
│   ├── firstlogin_manually.py
│   └── loadsession_manually.py
│
├── .gitignore
├── requirements.txt            # Dependências
├── README.md                   # Este arquivo
└── dados_instagram.csv         # Saída (ignorado no git)
```

---

## 🚀 Funcionalidades

### ✅ Selenium (complete_version.py)
- [x] Login com credenciais seguras via `.env`
- [x] Coleta de posts com scroll automático
- [x] Extração de likes, comentários, captions
- [x] Tratamento robusto de popups
- [x] Logging estruturado
- [x] Retry automático com backoff

### ✅ Instagrapi (instagrapi.py)
- [x] Autenticação com tratamento de exceções específicas
- [x] Coleta de perfil e posts
- [x] Classificação automática de tipo de mídia (Foto/Vídeo/Carrossel)
- [x] Extração de visualizações (vídeos)
- [x] Modelo de dados type-safe
- [x] Exibição formatada de resultados

### ✅ Instagrapi - Sem Login (no_login/collector.py) ⭐
- [x] Autenticação via Session ID (sem credenciais)
- [x] Coleta de perfil e posts
- [x] Exportação em CSV automatizada
- [x] Tratamento robusto de sessões expiradas
- [x] Performance otimizada
- [x] Ideal para produção

### ✅ Análise de Engajamento (no_login/analysis.py) 📊
- [x] Carregamento e processamento de dados CSV
- [x] Cálculo de métricas de engajamento
- [x] Visualizações avançadas com Matplotlib/Seaborn
- [x] Análise multidimensional (hashtags, legenda, tipo de post)
- [x] Relatório textual detalhado por perfil
- [x] Comparação entre perfis e correlações
- [x] Exportação de gráficos em alta qualidade (150 DPI)

### ✅ Instaloader (instaloader.py)
- [x] Autenticação com fallback para sessão salva
- [x] Coleta em massa de múltiplos perfis
- [x] Configuração granular de delays
- [x] Retry com backoff exponencial
- [x] Dados estruturados em CSV
- [x] Logging detalhado

---

## 🔧 Instalação

### Pré-requisitos

```bash
Python 3.9+
pip ou conda
Chrome/Chromium (para Selenium)
```

### 1. Clonar e Configurar Ambiente

```bash
git clone <seu-repo>
cd instagram-data-scraper

python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
```

### 2. Instalar Dependências

```bash
pip install -r requirements.txt
```

**requirements.txt:**
```
selenium>=4.0.0
instagrapi>=2.0.0
instaloader>=4.0.0
pandas>=1.5.0
python-dotenv>=1.0.0
webdriver-manager>=3.8.0
matplotlib>=3.5.0
seaborn>=0.12.0
```

### 3. Configurar Variáveis de Ambiente

Cada abordagem possui seu próprio `.env`:

**selenium/.env:**
```env
IG_USERNAME=seu_usuario
IG_PASSWORD=sua_senha
TARGET_PROFILES=perfil1
POSTS_PER_PROFILE=10
DRIVER_TIMEOUT=15
LOGIN_WAIT_TIME=8
```

**instagrapi/.env:**
```env
IG_USERNAME=seu_usuario
IG_PASSWORD=sua_senha
TARGET_PROFILE=neymarjr
POST_LIMIT=10
```

**instaloader/.env:**
```env
IG_USERNAME=seu_usuario
IG_PASSWORD=sua_senha
TARGET_PROFILES=perfil1,perfil2,perfil3
POSTS_PER_PROFILE=30
REQUEST_DELAY_MIN=2
REQUEST_DELAY_MAX=5
PROFILE_DELAY_MIN=5
PROFILE_DELAY_MAX=10
MAX_RETRIES=3
```

---

## Como Usar

### Selenium (Automação Browser)

```bash
cd selenium
python complete_version.py
```

**Saída:**
- `dados_instagram.csv` - Dados dos posts
- `scraper.log` - Log detalhado

**Ideal para:**
- Dados que requerem interação com o browser
- Quando a API simulada não funciona
- Precisão máxima na extração

---

### Instagrapi (API Simulada) - Com Login

```bash
cd instagrapi
python instagrapi.py
```

**Saída:**
- Exibição formatada no console
- `collector.log` - Log de operações

**Ideal para:**
- Coleta rápida de um perfil
- Melhor performance
- Menor overhead

---

### Instagrapi (Sem Login) - Recomendado

```bash
cd instagrapi/no_login
python collector.py
```

**Saída:**
- `output/instagram_posts.csv` - Dados dos posts coletados
- `collector.log` - Log detalhado

**Configuração (.env):**
```env
IG_SESSION_ID=seu_session_id_aqui
```

**Como obter Session ID:**
1. Acesse Instagram no browser
2. Abra DevTools (`F12`)
3. Vá para **Application** → **Cookies** → **https://www.instagram.com**
4. Procure por `sessionid` e copie o valor completo
5. Cole no `.env`

**Ideal para:**
- Sem necessidade de credenciais de login armazenadas
- Usa Session ID para autenticação mais segura
- Melhor performance e confiabilidade
- Menor risco de bloqueio por tentativas de login frequentes
- Session pode ser reutilizada entre execuções

---

### Instaloader (Bulk Collection)

```bash
cd instaloader
python instaloader.py
```

**Saída:**
- `dados_brutos.csv` - Dados de múltiplos perfis
- `bulk_scraper.log` - Log detalhado

**Ideal para:**
- Coleta em massa
- Múltiplos perfis simultaneamente
- Melhor confiabilidade

---

## 📊 Análise de Dados

Após coletar os dados, o módulo de análise gera visualizações e relatórios detalhados sobre engajamento, hashtags, tipos de post e outros métricas.

### Rodando a Análise

```bash
cd instagrapi/no_login
python analysis.py
```

**Pré-requisito:**
- Arquivo `output/posts.csv` gerado pela coleta

**Saída:**
- `output/analysis/relatorio.txt` - Relatório textual completo
- `output/analysis/1_engajamento_por_perfil.png` - Gráficos de engajamento
- `output/analysis/2_distribuicao_engajamento.png` - Histograma de distribuição
- `output/analysis/3_hashtags_vs_engajamento.png` - Influência de hashtags
- `output/analysis/4_legenda_vs_engajamento.png` - Impacto do tamanho da legenda
- `output/analysis/5_tipo_post_vs_engajamento.png` - Engajamento por tipo de post

### Métricas Analisadas

| Métrica | Descrição |
|---------|-----------|
| **Engajamento Absoluto** | Likes + Comentários por post |
| **Taxa de Engajamento (%)** | (Engajamento / Seguidores) × 100 |
| **Hashtags** | Número de hashtags por post |
| **Tamanho da Legenda** | Quantidade de caracteres na descrição |
| **Tipo de Post** | Imagem, Carrossel ou Reel |

### Visualizações Geradas

1. **Média de Engajamento por Perfil**
   - Gráficos comparativos de engajamento médio
   - Taxa de engajamento média por perfil

2. **Distribuição de Engajamento**
   - Histogramas com distribuição normal
   - Comparação entre perfis
   - Visualização de outliers

3. **Hashtags vs Engajamento**
   - Scatter plot: número de hashtags × engajamento
   - Linha: influência de hashtags na taxa de engajamento

4. **Legenda vs Engajamento**
   - Análise do impacto do tamanho da legenda
   - Tamanho da legenda em faixas vs taxa média

5. **Tipo de Post vs Engajamento**
   - Box plot de distribuição por tipo
   - Taxa de engajamento média por tipo de post

### Exemplo de Saída - Relatório

```
============================================================
  RELATÓRIO DE ANÁLISE DE ENGAJAMENTO
  Perfis: @alanaanijar, @thomytalks, @psi.bianca, @despatologiza, ...
  Total de posts analisados: 70
============================================================

0. VISÃO GERAL
  Total de posts:           70
  Likes médios:             5,875
  Comentários médios:       87
  Engajamento médio:        5,962
  Taxa de engajamento:      7.4592%
  Maior engajamento:        129,200 (issonaoeumaterapia)
```

---

## 🔄 Pipeline Completo: Coleta + Análise

Para executar o workflow completo de coleta e análise:

```bash
# 1. Navegar para o módulo no_login
cd instagrapi/no_login

# 2. Coletar dados (gera output/posts.csv)
python collector.py

# 3. Executar análise (gera relatórios e gráficos)
python analysis.py
```

**Saiba o que esperar:**
1. ✅ Coleta: 2-5 minutos (depende do número de perfis/posts)
2. ✅ Análise: 30-60 segundos
3. ✅ Arquivo de saída: `relatorio.txt` + 5 gráficos PNG
4. ✅ Pasta: `output/analysis/`

**Resultado Final:**
```
output/analysis/
├── relatorio.txt                    # Análise textual detalhada
├── 1_engajamento_por_perfil.png     # Comparação de perfis
├── 2_distribuicao_engajamento.png   # Distribuição de dados
├── 3_hashtags_vs_engajamento.png    # Impacto de hashtags
├── 4_legenda_vs_engajamento.png     # Impacto da legenda
└── 5_tipo_post_vs_engajamento.png   # Performance por tipo
```

---

## Arquitetura e Design

### Padrões Implementados

#### 1. **Type Hints & Type Safety**
```python
def fetch_profile_posts(
    client: Client, 
    username: str, 
    post_limit: int = 10
) -> Optional[ProfileData]:
    ...
```

#### 2. **Dataclasses para Estruturação**
```python
@dataclass
class PostData:
    position: int
    url: str
    likes: int
    comments: int
    
    def to_dict(self) -> Dict[str, Any]:
        return {...}
```

#### 3. **Enums para Constantes Type-Safe**
```python
class MediaType(Enum):
    PHOTO = (1, "Foto")
    VIDEO = (2, "Vídeo/Reel")
    CAROUSEL = (8, "Carrossel")
```

#### 4. **Logging Estruturado**
```python
logger.info("✓ Autenticação bem-sucedida")
logger.warning("⚠️ Sessão não encontrada")
logger.error("❌ Falha ao coletar dados")
```

#### 5. **Retry com Backoff**
```python
for attempt in range(max_retries):
    try:
        # operation
    except Exception as e:
        if attempt < max_retries - 1:
            wait_time = 10 * (attempt + 1)
            time.sleep(wait_time)
```

---

## Comparação de Abordagens

### Performance

| Métrica | Selenium | Instagrapi | Instagrapi (No-Login) | Instaloader |
|---------|----------|-----------|--------------------|-|
| Posts/min (1 perfil) | 3-5 | 10-15 | 12-18 | 15-20 |
| Overhead de memória | Alto | Baixo | Baixo | Baixo |
| Tempo de setup | Médio | Rápido | Instantâneo | Rápido |
| Requer credenciais | Sim | Sim | Não (Session ID) | Sim |

### Confiabilidade

| Aspecto | Selenium | Instagrapi | Instagrapi (No-Login) | Instaloader |
|---------|----------|-----------|--------------------|-|
| Taxa de bloqueio | Média | Alta | Baixa | Baixa |
| Requer login | Sim | Sim | Não | Sim |
| Dados completos | ✓ | ✓ | ✓✓ | ✓✓ |
| Ideal para produção | ✗ | ✗ | ✓ | ✓ |

---

## 🔐 Segurança

**Boas Práticas Implementadas:**
- Credenciais em `.env` (nunca no código)
- `.gitignore` para proteger dados sensíveis
- Validação de credenciais antes de uso
- Tratamento seguro de exceções
- Logs sem informações sensíveis

⚠️ **Considerações:**
- Cache local de sessões (proteger pasta de sessões)
- Usar credenciais de conta teste
- Respeitar rate limits do Instagram
- Cumprir Termos de Serviço

---

## Output CSV

### Formato dos Dados

**dados_instagram.csv (Selenium/Instaloader):**
```csv
profile,link,caption,likes,comments
user1,https://www.instagram.com/p/ABC123/,Caption text,1500,45
user1,https://www.instagram.com/p/DEF456/,Another text,2300,87
```

**collector.log (Instagrapi):**
```
Conta,Seguidores,Posts (JSON)
neymarjr,200000,"[{...}, {...}]"
```

---

## Troubleshooting

### "Login failed"
```
Solução: Verifique credenciais no .env
         Tente fazer login manualmente
         Verifique se há verificação 2FA ativada
```

### "Element not found (Selenium)"
```
Solução: Instagram pode ter alterado layout
         Aumente timeouts em .env
         Verifique selectors XPath/CSS
```

### "Rate limited"
```
Solução: Aumente delays em .env
         Use menos perfis por execução
         Distribua coletas em diferentes horários
```

### "Session not found"
```
Solução: Execute firstlogin_manually.py
         Verifique se sessão foi salva
         Login novamente
```

### "Analysis failed: CSV file not found"
```
Solução: Certifique-se de executar collector.py primeiro
         Verifique se output/posts.csv foi criado
         Confirme que o CSV tem dados
```

### "Matplotlib/Seaborn import error"
```
Solução: pip install matplotlib seaborn
         Verifique se requirements.txt foi instalado
```

---

## 📈 Insights Extraídos da Análise

A análise fornece insights valiosos para otimização de conteúdo:

### Principais Métricas Encontradas
- **Taxa de Engajamento**: Varia significativamente entre perfis (0.05% a 41.79%)
- **Tipo de Post**: Reels apresentam maior taxa de engajamento (12.10%) vs Imagens (2.97%)
- **Hashtags**: Correlação não-linear - quantidade excessiva pode prejudicar engajamento
- **Legenda**: Posts com legendas de tamanho médio tendem a ter melhor engajamento
- **Outliers**: Alguns posts específicos geram engajamento 200x maior que a média

### Uso Prático
1. **Criadores de Conteúdo**: Otimizar trabalhos com base em dados dos melhores posts
2. **Pesquisadores**: Entender padrões de engagement em diferentes nichos
3. **Benchmarking**: Comparar performance contra concorrentes
4. **Tendências**: Identificar formato de conteúdo mais efetivo

---

## Referências & Documentação

- [Selenium Docs](https://selenium-python.readthedocs.io/)
- [Instagrapi GitHub](https://github.com/adw0rd/instagrapi)
- [Instaloader Docs](https://instaloader.github.io/)
- [Pandas Documentation](https://pandas.pydata.org/docs/)
- [Matplotlib Documentation](https://matplotlib.org/)
- [Seaborn Documentation](https://seaborn.pydata.org/)
- [Instagram Terms of Service](https://help.instagram.com/581066165581870)

---

## Licença

MIT License - Veja [LICENSE](LICENSE) para detalhes
