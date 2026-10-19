"""
FastAPI Main Application












































































































































































































































































































































































































































































**Versão do Sistema:** 2.0 (Refatoração Completa - Navegação Direta)**Última Atualização:** 18/12/2025 às 14:30 UTC-3  ---- Debug screenshots: Path completo em caso de falha- Captura screenshot: URL acessada e configurações- PDFMapService: Configurações de inicialização- Startup: Avisos sobre multi-workers**Logs Importantes:**- `ROTAS_MAPAS_README.md` - Documentação de endpoints- `EXPORTAR_PDF_README.md` - Guia de uso da rota- `SISTEMA_MAPAS_PDF_CONSOLIDADO.md` - Histórico de desenvolvimento**Documentação Adicional:**## 📞 Suporte---- [ ] Verificar proporção do PDF: `identify teste.pdf` (se ImageMagick disponível)- [ ] Teste de geração: `curl -o teste.pdf "http://localhost:8000/api/exportar-pdf/mapa"`- [ ] GeoJSON `geojs-15-mun.json` no `app/data/`- [ ] Diretório `temp_maps/` com permissões 755- [ ] Uvicorn com `--workers 4` ou mais- [ ] Variável `BASE_URL` configurada corretamente- [ ] Dependências sistema: `playwright install-deps chromium`- [ ] Playwright instalado: `playwright install chromium`## ✅ Checklist de Deploy---**Solução:** Sempre manter **1.615:1** em ambas camadas.```pdf.image(..., w=210, h=130)  # Proporção: 1.615 ✅# PDFviewport = {'width': 1615, 'height': 1000}  # Proporção: 1.615# Viewport```python**Verificação:****Causa:** Proporção entre viewport e PDF diferente### Erro: "Mapa distorcido (Pará achatado)"---2. Aumentar `wait_for_timeout(2000)` para 3000ms1. Usar `--disable-gpu` nos args (já configurado)**Soluções:**2. Timeout insuficiente para renderização1. Headless=True com GPU incompatível**Causas:**### Erro: "Screenshot vazio/preto"---3. Analisar `debug_error_*.png`2. Verificar `BASE_URL` em logs1. Usar `--workers 4`**Soluções:**3. Erro 500 na rota de visualização2. BASE_URL incorreta1. Servidor com 1 worker (deadlock)**Causas:**### Erro: "Timeout ao aguardar .leaflet-container"## 🚨 Troubleshooting---**Otimização:** Multi-workers permite processar PDFs simultaneamente.3. Montagem PDF FPDF2 (1-2s)2. Captura screenshot Playwright (3-8s)1. Renderização Leaflet/Folium (2-5s)**Gargalos:**| Mapa Município + Status | 8-12s || Mapa Município (1 filtro) | 10-15s || Mapa Estado (sem filtros) | 15-20s ||---------|---------------|| Cenário | Tempo Estimado |### Tempo Médio de Geração## ⚡ Performance---```└── CONFIGURACAO_PDF_FINAL.md            # Este documento├── requirements.txt├── main.py                              # FastAPI app com eventos startup/shutdown│   └── temp_screenshot_*.png│   ├── debug_error_20251218_143052.png│   ├── mapa_gis_abc123.pdf├── temp_maps/                           # PDFs e screenshots temporários│       └── geojs-15-mun.json            # 143 municípios do Pará (IBGE)│   └── data/│   │   └── pdf_service.py               # PDFMapService (Playwright + FPDF2)│   ├── services/│   │   └── relatorio_mapa_visualizar.py # Visualização HTML (Folium)│   │   ├── exportar_pdf.py              # Rota unificada /api/exportar-pdf/mapa│   ├── routers/├── app/api_svegpa/```## 📁 Estrutura de Arquivos---```PDF_DEBUG=false  # SEMPRE false em produçãoBASE_URL=https://api.svegpa.gov.br```bash**Produção/VPS:**```PDF_DEBUG=false                  # true = navegador visível (apenas local)BASE_URL=http://127.0.0.1:8000  # URL base da aplicação# .env ou export no shell```bash## 🔐 Variáveis de Ambiente---```playwright install-deps chromium# 3. Ubuntu/Debian: Instalar dependências do sistemaplaywright install chromium# 2. Instalar browser Chromiumpip install playwright==1.57.0# 1. Instalar biblioteca Python```bash**Instalação Playwright:**```sqlalchemy==2.0.36folium==0.15.1fpdf2==2.8.2playwright==1.57.0fastapi==0.115.5```txt## 📦 Dependências Críticas---**Legenda automática:** Folium adiciona legenda com as cores no canto superior direito.```)    popup=f"{municipio} - {status}"    weight=1,    fill_opacity=0.8,    fill_color=STATUS_COLORS[status],    fill=True,    color=STATUS_COLORS[status],    radius=5,    location=[lat, lon],CircleMarker(}    'POSITIVO': 'red'      # #FF0000    'SUSPEITA': 'orange',  # #FFA500    'NORMAL': 'blue',      # #0000FFSTATUS_COLORS = {```python## 🎨 Cores dos CircleMarkers---```# Visão completa do estadozoom_start = 6center = [-3.85, -52.5]```python**3. Fallback 2: Estado do Pará**```# delta = 20% da amplitude para contexto          [max_lat + delta, max_lon + delta]]bounds = [[min_lat - delta, min_lon - delta], ```python**2. Fallback 1: Dispersão de Pontos + 20%**```m.fit_bounds(bounds)# Extrai [[min_lat, min_lon], [max_lat, max_lon]] do Polygon/MultiPolygonbounds = _get_municipio_bounds_from_geojson(municipio_nome)```python**1. Tentativa Primária: Limites do GeoJSON**### Estratégia em 3 Níveis## 🗺️ Zoom Territorial (GeoJSON IBGE)---```# Screenshot de debug será salvo em temp_maps/debug_error_YYYYMMDD_HHMMSS.png# Playwright não conseguirá acessar visualização# Parar servidor temporariamente e tentar gerar PDF```bashSimular falha:### 4. **Teste de Debug Screenshot**- Total de pontos = registros com status POSITIVO- Apenas marcadores vermelhos**Esperado:**```curl -o positivos.pdf "http://localhost:8000/api/exportar-pdf/mapa?status=POSITIVO"```bash### 3. **Teste com Status**- Metadados técnicos corretos no carimbo lateral- PDF A4 Paisagem com moldura dupla- Marcadores azuis (NORMAL), laranjas (SUSPEITA), vermelhos (POSITIVO)- Zoom automático nos limites territoriais de Prainha (GeoJSON)**Esperado:**```curl -o mapa_prainha.pdf "http://localhost:8000/api/exportar-pdf/mapa?municipio=Prainha"```bash### 2. **Teste com Município**```curl -o mapa.pdf "http://localhost:8000/api/exportar-pdf/mapa"```bash### 1. **Teste Básico (sem filtros)**## 🧪 Testes de Validação---**IMPORTANTE:** Estes dados **NÃO** são extraídos do screenshot, mas sim **diretamente do banco de dados** para garantir fé pública.```}    'data_fim': '31/12/2025',    'data_inicio': '01/01/2025',    'municipios': ['Prainha'],  # Lista de municípios únicos    'total_records': 150,       # Total de registros consultados    'total_markers': 150,       # Contagem direta no banco    'lon_center': -47.8822,     # Média ponderada dos pontos REAIS    'lat_center': -15.7942,     # Média ponderada dos pontos REAISmetadata = {```python### Metadados Extraídos do Banco## 📊 Dados Técnicos (Fé Pública)---3. Log indica possíveis causas (500, auth, HTML)2. Exception detalhada é lançada com path do debug1. Screenshot de debug é salvoSe `.leaflet-container` falhar:### 3. **Fallback de Seletor**```   - Headless: True   - Viewport: 1615x1000 (proporção 1.615:1 - PDF 210x130mm)   - Timeout: 60000ms (60s)   - Seletor aguardado: .leaflet-container🎯 Configurações:   http://127.0.0.1:8000/api/relatorio-mapa/visualizar?municipio=Prainha🌐 URL DA VISUALIZAÇÃO HTML:```### 2. **Logs Detalhados**- HTML incompleto/inválido?- Problema de autenticação?- Erro 500 do servidor?**Uso:** Analisar visualmente o que Playwright viu:```await page.screenshot(path=f"temp_maps/{debug_filename}", full_page=True)debug_filename = f"debug_error_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"```pythonSe `.leaflet-container` não for encontrado em 20s:### 1. **Screenshot de Debug Automático**## 🛡️ Resiliência e Debug---**Vantagem:** Compatibilidade automática com Linux/Windows```screenshot_path = output_dir / "screenshot.png"output_dir = Path("temp_maps").resolve()from pathlib import Path```python### 3. **Pathlib (não strings)****Permissões:** `rwxr-xr-x` (755)```output_dir.mkdir(parents=True, exist_ok=True, mode=0o755)```python### 2. **Permissões do Diretório**```]    '--disable-software-rasterizer',    '--disable-gpu',    '--disable-dev-shm-usage',  # Importante em containers/VPS    '--disable-setuid-sandbox',    '--no-sandbox',args=[```python### 1. **Argumentos do Chromium**## 🐧 Otimizações Ubuntu/Linux---- Workers 3-4: Reserva para outras requisições simultâneas- Worker 2: Atende requisição do Playwright para visualização- Worker 1: Processa a geração do PDF**Explicação:**```uvicorn main:app --reload --host 0.0.0.0 --port 8000 --workers 4```bash**SOLUÇÃO:**- Mesmo worker está ocupado → **timeout**- Playwright tenta acessar `/api/relatorio-mapa/visualizar`- Worker único processa `/api/exportar-pdf/mapa`**PROBLEMA:** Com 1 worker, ocorre **DEADLOCK**:### ⚠️ IMPORTANTE: Multi-Workers## 🚀 Execução Recomendada---- `trimestre` - Trimestre (1-4)- `ano` - Ano (YYYY)- `id_programa` - ID do programa- `data_fim` - Data fim (YYYY-MM-DD)- `data_inicio` - Data início (YYYY-MM-DD)- `status` - NORMAL, SUSPEITA, POSITIVO- `cultura` - Filtro por cultura- `municipio` - Filtro por município**Query Parameters suportados:**```http://127.0.0.1:8000/api/relatorio-mapa/visualizar?municipio=Prainha&status=POSITIVO```**Exemplo com filtros:**```/api/relatorio-mapa/visualizar```**Endpoint de Visualização:****BASE_URL:** `http://127.0.0.1:8000` (configurável via env)### 4. **URL de Captura**---- `wait_for_selector('.leaflet-container', timeout=20000)` → 20s para Leaflet renderizar- `timeout=60000` → 60s total para carregamento- `wait_until='load'` → Mais confiável que `'networkidle'` em servidores**Otimização Ubuntu:**```await page.goto(map_url, wait_until='load', timeout=60000)```python### 3. **Navegação Playwright**---**Proporção:** 210 ÷ 130 = **1.615:1** ✅```pdf.image(screenshot_path, x=10, y=35, w=210, h=130)```python### 2. **PDF (FPDF2)**---**Proporção:** 1615 ÷ 1000 = **1.615:1**```device_scale_factor=2  # 2x para qualidadeviewport={'width': 1615, 'height': 1000}```python### 1. **Viewport Playwright**## 🔧 Configurações Técnicas---```8. CLIENTE ← FileResponse com PDF (download)                         ↓7. FPDF2 monta PDF A4 Paisagem 210x130mm                         ↓6. Screenshot 1615x1000 @ 2x scale                         ↓5. Aguarda .leaflet-container (20s timeout)                         ↓4. PDFMapService (Playwright) navega para essa URL                         ↓3. Constrói URL: http://127.0.0.1:8000/api/relatorio-mapa/visualizar?municipio=Prainha                         ↓2. FastAPI consulta BD e calcula metadados reais                         ↓1. CLIENTE → GET /api/exportar-pdf/mapa?municipio=Prainha```### Fluxo de Geração de PDF## 🎯 Arquitetura do Sistema---- ✅ Resiliência no Ubuntu/Linux- ✅ Screenshots de debug automáticos- ✅ Multi-workers para evitar deadlock- ✅ CircleMarkers com cores por status (blue, orange, red)- ✅ Zoom territorial com limites GeoJSON IBGE- ✅ Proporção matemática 1.615:1 (sem distorção do Pará)- ✅ Navegação direta para visualização HTML validadaSistema de geração de PDFs de mapas GIS/Engenharia com:## 📋 Resumo Executivo---**Status:** ✅ VALIDADO E OTIMIZADO  **Data da Consolidação:** 18/12/2025  
CRITICAL: Configuração de Event Loop Policy para Windows DEVE estar no topo.
Resolve NotImplementedError com subprocessos (Playwright/Chromium) no Windows.
"""

import asyncio
import sys

# ⚠️ CRITICAL: CONFIGURAR LOOP POLICY ANTES DE QUALQUER IMPORTAÇÃO
# Resolve NotImplementedError no Windows Python 3.12+ ao criar subprocessos
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    print("[OK] WindowsProactorEventLoopPolicy configurada no main.py")

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_redoc_html, get_swagger_ui_html
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from app.config.settings import get_settings
import os
from app.routers import sync
from app.routers import dashboard
from app.routers import (
    auth,
    orgaos_tipos,
    orgaos,
    unidades,
    cargos,
    formacoes,
    programas,
    hospedeiros,
    normas,
    users,
    produtores,
    propriedades,
    termo_inspecao,
    area_inspecionada,
    area_programa,
    amostra_coletada,
    laboratorios,
    relatorio_mapa,
    relatorio_mapa_visualizar,
    exportar_pdf,
    estados,
    produtos,
    reg_atividade,
    reg_metas,
    sec_users_api,
    sec_settings,
    dashboard_filtros,
)
from app.routers import municipios
from app.routers import relatorio_resumo
from app.routers import (
    levantamentos,
    inspecao_foto,
    auditoria_acesso,
    car,
)

settings = get_settings()

# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="API para integração com WeWeb.io e FlutterFlow.io",
    docs_url=None,
    redoc_url=None,
    openapi_url="/openapi.json"
)

# Configure static files for temporary maps (touched to force reload)
TEMP_MAPS_DIR = os.path.join(os.path.dirname(__file__), "temp_maps")
os.makedirs(TEMP_MAPS_DIR, exist_ok=True)
app.mount("/mapas_temp", StaticFiles(directory=TEMP_MAPS_DIR), name="mapas_temp")

UPLOADS_DIR = os.path.join(os.path.dirname(__file__), "uploads")
os.makedirs(os.path.join(UPLOADS_DIR, "laudos"), exist_ok=True)
app.mount("/uploads", StaticFiles(directory=UPLOADS_DIR), name="uploads")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8080",
        "*"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(sync.router)
app.include_router(dashboard.router)
app.include_router(orgaos_tipos.router)
app.include_router(orgaos.router)
app.include_router(unidades.router)
app.include_router(cargos.router)
app.include_router(formacoes.router)
app.include_router(programas.router)
app.include_router(hospedeiros.router)
app.include_router(normas.router)
app.include_router(users.router)
app.include_router(produtores.router)
app.include_router(propriedades.router)
app.include_router(termo_inspecao.router)
app.include_router(area_inspecionada.router)
app.include_router(area_programa.router)
app.include_router(amostra_coletada.router)
app.include_router(laboratorios.router)
app.include_router(relatorio_mapa_visualizar.router)
app.include_router(exportar_pdf.router)
app.include_router(relatorio_mapa.router)
app.include_router(relatorio_resumo.router)
app.include_router(levantamentos.router)
app.include_router(estados.router)
app.include_router(municipios.router)
app.include_router(produtos.router)
app.include_router(reg_atividade.router)
app.include_router(reg_metas.router)
app.include_router(sec_users_api.router)
app.include_router(sec_settings.router)
app.include_router(dashboard_filtros.router)
app.include_router(inspecao_foto.router)
app.include_router(auditoria_acesso.router)
app.include_router(car.router)


# ==========================================
# EVENTOS DE STARTUP E SHUTDOWN
# ==========================================

@app.on_event("startup")
async def startup_event():
    """Evento executado na inicialização da aplicação."""
    import logging
    logger = logging.getLogger("uvicorn")

    if not settings.SECRET_KEY:
        logger.error("ERRO: SECRET_KEY nao configurada! Autenticacao falhara.")
        logger.error("Configure SECRET_KEY no arquivo .env na raiz do projeto.")
    if not settings.DB_HOST:
        logger.error("ERRO: DB_HOST nao configurado! Conexao com banco falhara.")

    logger.info("=" * 80)
    logger.info("🚀 SVEGPA API INICIADA COM SUCESSO")
    logger.info("=" * 80)
    logger.info(f"📦 Versão: {settings.APP_VERSION}")
    logger.info(f"🐍 Python: {sys.version.split()[0]}")
    logger.info(f"🌐 Base URL: {os.getenv('BASE_URL', 'http://127.0.0.1:8000')}")
    logger.info("=" * 80)
    logger.warning("")
    logger.warning("⚠️  IMPORTANTE: GERAÇÃO DE PDFs COM PLAYWRIGHT")
    logger.warning("   Para evitar DEADLOCK entre captura PDF e visualização HTML,")
    logger.warning("   execute o Uvicorn com MÚLTIPLOS WORKERS:")
    logger.warning("")
    logger.warning("   ✅ RECOMENDADO:")
    logger.warning("      uvicorn main:app --reload --host 0.0.0.0 --port 8000 --workers 4")
    logger.warning("")
    logger.warning("   ❌ EVITAR (pode travar ao gerar PDF):")
    logger.warning("      uvicorn main:app --reload")
    logger.warning("")
    logger.warning("   Motivo: Playwright precisa acessar a rota de visualização HTML")
    logger.warning("   enquanto processa o PDF. Com 1 worker, ocorre deadlock.")
    logger.warning("")
    logger.info("=" * 80)


@app.on_event("shutdown")
async def shutdown_event():
    """Evento executado no encerramento da aplicação."""
    import logging
    logger = logging.getLogger("uvicorn")
    logger.info("🛑 SVEGPA API sendo encerrada...")


# ==========================================
# ROTAS DE DOCUMENTAÇÃO E HEALTH CHECK
# ==========================================

@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=f"{settings.APP_NAME} - Swagger UI",
        swagger_js_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-bundle.js",
        swagger_css_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui.css",
    )


@app.get("/redoc", include_in_schema=False)
async def redoc_html():
    return get_redoc_html(
        openapi_url=app.openapi_url,
        title=f"{settings.APP_NAME} - ReDoc",
        redoc_js_url="https://cdn.jsdelivr.net/npm/redoc@latest/bundles/redoc.standalone.js",
    )


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint - API health check."""
    return {
        "message": f"Welcome to {settings.APP_NAME}",
        "version": settings.APP_VERSION,
        "status": "running"
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "version": settings.APP_VERSION
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
