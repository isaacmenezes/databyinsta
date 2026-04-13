# 📊 Instagram Data Collector

![Status](https://img.shields.io/badge/Status-Em_Desenvolvimento-yellow?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.9+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Selenium](https://img.shields.io/badge/Selenium-43B02A?style=for-the-badge&logo=selenium&logoColor=white)
![License](https://img.shields.io/badge/Licença-MIT-green?style=for-the-badge)

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
│   ├── instagrapi.py           # Coleta via API simulada
│   ├── .env                     # Configurações
│   ├── collector.log            # Logs
│   └── firstlogin_manually.py   # Setup de sessão
│
├── instaloader/
│   ├── instaloader.py          # Coleta em massa
│   ├── .env                     # Configurações
│   ├── bulk_scraper.log        # Logs
│   ├── firstlogin_manually.py
│   └── loadsession_manually.py
│
├── .gitignore
├── README.md                    # Este arquivo
└── dados_instagram.csv          # Saída (ignorado no git)
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

## 💻 Como Usar

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

### Instagrapi (API Simulada)

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

## 📊 Arquitetura e Design

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

## 📈 Comparação de Abordagens

### Performance

| Métrica | Selenium | Instagrapi | Instaloader |
|---------|----------|-----------|------------|
| Posts/min (1 perfil) | 3-5 | 10-15 | 15-20 |
| Overhead de memória | Alto | Baixo | Baixo |
| Tempo de setup | Médio | Rápido | Rápido |

### Confiabilidade

| Aspecto | Selenium | Instagrapi | Instaloader |
|---------|----------|-----------|------------|
| Taxa de bloqueio | Média | Alta | Baixa |
| Requer sessão | Não | Sim | Sim |
| Dados completos | ✓ | ✓ | ✓✓ |

---

## 🔐 Segurança

✅ **Boas Práticas Implementadas:**
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

## 📝 Output CSV

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

## 🐛 Troubleshooting

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

---

## 📚 Referências & Documentação

- [Selenium Docs](https://selenium-python.readthedocs.io/)
- [Instagrapi GitHub](https://github.com/adw0rd/instagrapi)
- [Instaloader Docs](https://instaloader.github.io/)
- [Instagram Terms of Service](https://help.instagram.com/581066165581870)

---

## 👨‍🎓 Contexto Acadêmico

Este projeto foi desenvolvido como parte do programa de **Iniciação Científica**, com foco em:

- Análise comparativa de técnicas de web scraping
- Implementação de boas práticas em Python moderno
- Estruturação profissional de código
- Documentação técnica e versionamento

---

## 📄 Licença

MIT License - Veja [LICENSE](LICENSE) para detalhes

---

## ✨ Contribuições & Melhorias Futuras

- [ ] Integração com banco de dados (SQLite/PostgreSQL)
- [ ] API REST para exposição dos dados
- [ ] Dashboard web com visualizações
- [ ] Análise de sentimento dos captions
- [ ] Scheduler automático de coletas
- [ ] Testes unitários e integração
- [ ] Docker containerization

---

## 📧 Contato & Suporte

Para dúvidas, sugestões ou relatos de bugs:

```
📧 Email: seu-email@example.com
🐙 GitHub: seu-github-profile
```

---

**Desenvolvido com ❤️ para Iniciação Científica**

*Última atualização: Abril 2026*
