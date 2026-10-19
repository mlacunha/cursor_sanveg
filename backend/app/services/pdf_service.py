"""
PDF Service - Geração profissional de PDFs padrão GIS/Engenharia
Utiliza Playwright para captura de mapas e FPDF2 para montagem do documento.

ESPECIFICAÇÕES TÉCNICAS (Validadas Ubuntu 18/12/2025):
- Viewport: 1615x1000 (proporção 1.615:1)
- PDF: 210x130mm (proporção 1.615:1)
- wait_until='load' (mais confiável que networkidle no Ubuntu)
- wait_for_selector: 20s
- Pathlib para caminhos (Linux-friendly)
- ThreadPoolExecutor para FPDF2 (síncrono)
"""

import os
import asyncio
import logging
import traceback
from datetime import datetime
from typing import Optional, Dict, Any
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger(__name__)


class PDFMapService:
    """Serviço para geração de PDFs de mapas em padrão GIS/Engenharia."""
    
    def __init__(self, output_dir: str = "temp_maps", base_url: Optional[str] = None, debug_mode: bool = False):
        """
        Inicializa o serviço de PDF para ambiente Linux/Ubuntu.
        
        Args:
            output_dir: Diretório onde os PDFs serão salvos
            base_url: URL base da aplicação (ex: http://127.0.0.1:8000)
            debug_mode: Se True, abre navegador visível para debug
        """
        # 🐧 PATHLIB: Compatibilidade total com Linux
        self.output_dir = Path(output_dir).resolve()
        
        # 🔒 PERMISSÕES: Criar diretório com permissões corretas
        self.output_dir.mkdir(parents=True, exist_ok=True, mode=0o755)
        
        # ThreadPoolExecutor para tarefas síncronas (FPDF)
        self.executor = ThreadPoolExecutor(max_workers=2)
        
        # 🌐 BASE URL: Prioridade para 127.0.0.1
        if base_url:
            self.base_url = base_url.rstrip('/')
        else:
            self.base_url = os.getenv('BASE_URL', 'http://127.0.0.1:8000').rstrip('/')
        
        # 🖥️ HEADLESS MODE: Sempre True em produção
        self.debug_mode = debug_mode and os.getenv('PDF_DEBUG', 'false').lower() == 'true'
        
        logger.info(f"PDFMapService inicializado (Ubuntu/Linux):")
        logger.info(f"  - base_url: {self.base_url}")
        logger.info(f"  - output_dir: {self.output_dir}")
        logger.info(f"  - debug_mode: {self.debug_mode} {'(NAVEGADOR VISÍVEL)' if self.debug_mode else '(headless)'}")
        logger.info(f"  - permissions: 0o755")
        
    async def capture_map_screenshot(
        self,
        html_content: str,
        width: int = 1615,
        height: int = 1000
    ) -> bytes:
        """
        Captura screenshot do mapa usando Playwright com INJEÇÃO DIRETA DE HTML.
        
        OTIMIZAÇÕES UBUNTU (18/12/2025 - INJEÇÃO HTML DIRETA):
        - set_content() com HTML string (SEM requisições HTTP)
        - wait_until='load' (aguarda DOM load event)
        - wait_for_timeout 5s (renderização Leaflet + tiles + CircleMarkers)
        - --disable-web-security (sem CORS/autenticação)
        - Viewport 1615x1000 (proporção 1.615:1 exata)
        
        Args:
            html_content: String HTML completa do mapa Folium
            width: Largura da viewport (1615px)
            height: Altura da viewport (1000px)
            
        Returns:
            bytes: Screenshot em formato PNG
        """
        from playwright.async_api import async_playwright
        
        browser = None
        context = None
        
        try:
            logger.info("=" * 80)
            logger.info("🚀 INICIANDO CAPTURA DE SCREENSHOT (Playwright - INJEÇÃO HTML)")
            logger.info("=" * 80)
            logger.info(f"📄 HTML Content: {len(html_content)} caracteres")
            logger.info(f"🎯 Viewport: {width}x{height} (proporção 1.615:1)")
            logger.info("=" * 80)
            
            # PLAYWRIGHT: Context manager async
            async with async_playwright() as p:
                logger.info("✓ Playwright inicializado")
                
                # 🐧 UBUNTU/LINUX: headless=True com args otimizados
                browser = await p.chromium.launch(
                    headless=not self.debug_mode,
                    args=[
                        '--no-sandbox',
                        '--disable-setuid-sandbox',
                        '--disable-dev-shm-usage',
                        '--disable-gpu',
                        '--disable-software-rasterizer',
                        '--disable-extensions',
                        '--disable-web-security',  # Sem CORS/autenticação
                        '--disable-features=IsolateOrigins,site-per-process'
                    ]
                )
                logger.info(f"✓ Chromium lançado (headless={not self.debug_mode})")
                
                # Context com viewport exato
                context = await browser.new_context(
                    viewport={'width': width, 'height': height},
                    device_scale_factor=2,  # 2x para qualidade
                    locale='pt-BR',
                    timezone_id='America/Sao_Paulo'
                )
                logger.info(f"✓ Context criado: {width}x{height} @ 2x scale")
                
                page = await context.new_page()
                logger.info("✓ Nova página criada")
                
                # 📄 INJEÇÃO HTML DIRETA: sem rede, sem autenticação, sem latência
                logger.info("📄 Injetando HTML diretamente na página...")
                logger.info("   (set_content - SEM requisições HTTP)")
                
                await page.set_content(html_content, wait_until='load')
                logger.info("✓ HTML injetado e processado (DOM load event)")
                
                # ⏳ AGUARDAR RENDERIZAÇÃO (5s para Leaflet + tiles + CircleMarkers)
                logger.info("⏳ Aguardando 5s para renderização Leaflet completa...")
                logger.info("   (tiles satélite + CircleMarkers + GeoJSON)")
                
                await page.wait_for_timeout(5000)  # 5 segundos fixos
                logger.info("✓ Renderização completa")
                
                # 📸 CAPTURA: Screenshot da página inteira (100vw x 100vh = mapa completo)
                logger.info("📸 Capturando screenshot da página...")
                logger.info("   (CSS: #map = 100vw x 100vh - captura automática do viewport)")
                
                screenshot_bytes = await page.screenshot(type='png')
                
                size_kb = len(screenshot_bytes) / 1024
                logger.info(f"✓ Screenshot capturado: {len(screenshot_bytes):,} bytes ({size_kb:.1f} KB)")
                logger.info("=" * 80)
                logger.info("✅ SCREENSHOT CAPTURADO COM SUCESSO")
                logger.info("=" * 80)
                
                return screenshot_bytes
                
        except Exception as e:
            error_trace = traceback.format_exc()
            
            logger.error("=" * 80)
            logger.error("🚨 ERRO AO CAPTURAR SCREENSHOT")
            logger.error("=" * 80)
            logger.error(f"HTML Content: {len(html_content)} caracteres")
            logger.error(f"Tipo: {type(e).__name__}")
            logger.error(f"Mensagem: {str(e)}")
            logger.error(f"\nTraceback:\n{error_trace}")
            logger.error("=" * 80)
            
            raise Exception(
                f"Falha ao capturar screenshot do mapa via injeção HTML. "
                f"HTML size: {len(html_content)} caracteres | Erro: {repr(e)}"
            ) from e
            
        finally:
            # 🧹 CLEANUP
            if context:
                try:
                    await context.close()
                    logger.info("✓ Context fechado")
                except Exception as cleanup_err:
                    logger.warning(f"Erro ao fechar context: {cleanup_err}")
                    
            if browser:
                try:
                    await browser.close()
                    logger.info("✓ Browser fechado")
                except Exception as cleanup_err:
                    logger.warning(f"Erro ao fechar browser: {cleanup_err}")
    
    def _generate_pdf_sync(
        self,
        screenshot_path: str,
        output_filename: str,
        metadata: Dict[str, Any]
    ) -> str:
        """
        Gera PDF no padrão GIS/Engenharia com FPDF2.
        
        Layout:
        - A4 Paisagem (297x210mm)
        - Cabeçalho azul profissional
        - Mapa centralizado 210x130mm (proporção 1.615:1)
        - Moldura dupla
        - Carimbo técnico lateral
        - Rodapé com fé pública
        
        Args:
            screenshot_path: Caminho para o screenshot do mapa
            output_filename: Nome do arquivo PDF de saída
            metadata: Metadados REAIS do banco
            
        Returns:
            str: Caminho completo do PDF gerado
        """
        from fpdf import FPDF
        
        try:
            logger.info("=" * 80)
            logger.info("GERANDO PDF PADRÃO GIS/ENGENHARIA")
            logger.info(f"Arquivo: {output_filename}")
            logger.info(f"Dados: {metadata.get('total_markers', 0)} pontos")
            logger.info("=" * 80)
            
            # Criar PDF A4 Paisagem
            pdf = FPDF(orientation='L', unit='mm', format='A4')
            pdf.add_page()
            pdf.set_auto_page_break(auto=False)
            
            # --- CABEÇALHO ---
            pdf.set_fill_color(41, 128, 185)  # Azul profissional
            pdf.rect(0, 0, 297, 25, 'F')
            
            pdf.set_text_color(255, 255, 255)
            pdf.set_font('Arial', 'B', 16)
            pdf.set_xy(10, 8)
            pdf.cell(0, 10, metadata.get('title', 'Mapa GIS'), align='C')
            
            pdf.set_font('Arial', '', 10)
            pdf.set_xy(10, 16)
            pdf.cell(0, 6, f"{metadata.get('project', 'SVEGPA')} | {metadata.get('institution', 'MAPA')}", align='C')
            
            # Data de geração
            pdf.set_xy(240, 8)
            pdf.set_font('Arial', '', 9)
            pdf.cell(50, 5, f"Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M')}", align='R')
            
            # --- MAPA COM MOLDURA DUPLA ---
            pdf.set_text_color(0, 0, 0)
            
            map_x = 10
            map_y = 35
            map_width = 210
            map_height = 130
            
            # Moldura externa (preta grossa)
            pdf.set_draw_color(0, 0, 0)
            pdf.set_line_width(1.0)
            pdf.rect(map_x - 1, map_y - 1, map_width + 2, map_height + 2)
            
            # Moldura interna (preta fina)
            pdf.set_line_width(0.3)
            pdf.rect(map_x, map_y, map_width, map_height)
            
            # 📸 INSERIR MAPA: Proporção 1.615:1 (210mm / 130mm = 1.615)
            if os.path.exists(screenshot_path):
                pdf.image(screenshot_path, x=10, y=35, w=210, h=130)
                logger.info(f"✓ Imagem inserida: 210x130mm (proporção 1.615:1)")
            else:
                logger.warning(f"⚠️  Screenshot não encontrado: {screenshot_path}")
            
            # --- CARIMBO TÉCNICO ---
            stamp_x = 225
            stamp_y = 35
            stamp_width = 62
            
            pdf.set_fill_color(240, 240, 240)
            pdf.rect(stamp_x, stamp_y, stamp_width, 130, 'F')
            
            pdf.set_font('Arial', 'B', 10)
            pdf.set_xy(stamp_x + 2, stamp_y + 5)
            pdf.cell(stamp_width - 4, 6, 'DADOS TÉCNICOS', align='C')
            
            pdf.set_font('Arial', '', 8)
            y_offset = stamp_y + 15
            
            # Coordenadas centrais
            lat_center = metadata.get('lat_center')
            lon_center = metadata.get('lon_center')
            
            pdf.set_xy(stamp_x + 2, y_offset)
            pdf.cell(stamp_width - 4, 5, 'Coordenadas Centrais:', align='L')
            y_offset += 5
            
            if lat_center is not None and lon_center is not None:
                pdf.set_xy(stamp_x + 2, y_offset)
                pdf.cell(stamp_width - 4, 4, f'Lat: {lat_center:.6f}', align='L')
                y_offset += 4
                pdf.set_xy(stamp_x + 2, y_offset)
                pdf.cell(stamp_width - 4, 4, f'Lon: {lon_center:.6f}', align='L')
            else:
                pdf.set_xy(stamp_x + 2, y_offset)
                pdf.cell(stamp_width - 4, 4, 'N/A', align='L')
            
            y_offset += 8
            
            # Total de marcadores
            pdf.set_xy(stamp_x + 2, y_offset)
            pdf.cell(stamp_width - 4, 5, f'Total de Pontos: {metadata.get("total_markers", 0)}', align='L')
            y_offset += 8
            
            # Escala
            pdf.set_xy(stamp_x + 2, y_offset)
            pdf.cell(stamp_width - 4, 5, f'Escala: {metadata.get("scale", "1:50.000")}', align='L')
            y_offset += 8
            
            # Responsável
            pdf.set_xy(stamp_x + 2, y_offset)
            pdf.cell(stamp_width - 4, 5, 'Responsável:', align='L')
            y_offset += 5
            pdf.set_xy(stamp_x + 2, y_offset)
            pdf.multi_cell(stamp_width - 4, 4, metadata.get('responsible', 'N/A'))
            
            # --- RODAPÉ ---
            pdf.set_font('Arial', 'I', 8)
            pdf.set_text_color(100, 100, 100)
            pdf.set_xy(10, 200)
            pdf.cell(
                277,
                5,
                'Documento gerado automaticamente | Dados extraídos do banco de dados',
                align='C'
            )
            
            # Salvar PDF
            output_path = self.output_dir / output_filename
            pdf.output(str(output_path))
            
            file_size = output_path.stat().st_size / 1024
            logger.info(f"✓ PDF gerado: {output_path}")
            logger.info(f"✓ Tamanho: {file_size:.1f} KB")
            
            return str(output_path)
            
        except Exception as e:
            error_trace = traceback.format_exc()
            logger.error("=" * 80)
            logger.error("🚨 ERRO NA GERAÇÃO DO PDF (FPDF2)")
            logger.error(f"Tipo: {type(e).__name__}")
            logger.error(f"Mensagem: {str(e)}")
            logger.error(f"Traceback:\n{error_trace}")
            logger.error("=" * 80)
            raise Exception(f"Erro na geração do PDF: {str(e)}") from e
    
    async def generate_map_pdf(
        self,
        html_content: str,
        output_filename: str,
        metadata: Dict[str, Any]
    ) -> str:
        """
        📄 PIPELINE COMPLETO: HTML → Screenshot → PDF (INJEÇÃO HTML)
        
        FLUXO:
        1. Injeta HTML direto no Playwright (page.set_content)
        2. Aguarda renderização Leaflet (5s fixo)
        3. Captura screenshot (async via Playwright)
        4. Salva temporário
        5. Gera PDF (sync via ThreadPoolExecutor)
        6. Limpa temporários
        
        ESTRATÉGIA:
        - Sem requisições HTTP (HTML injetado diretamente)
        - Sem autenticação necessária
        - Sem latência de rede
        
        Args:
            html_content: HTML completo do mapa (Folium._repr_html_())
            output_filename: Nome do arquivo PDF final
            metadata: Metadados REAIS do BD
            
        Returns:
            str: Caminho completo do PDF gerado
        """
        screenshot_path = None
        
        try:
            total_markers = metadata.get('total_markers', 0)
            
            print("\n" + "📄" * 40)
            print("📄 INICIANDO GERAÇÃO DE PDF COMPLETO (INJEÇÃO HTML)")
            print("📄" * 40)
            print(f"\n📊 Metadados:")
            print(f"   - Total de pontos: {total_markers}")
            print(f"   - Centro: ({metadata.get('lat_center')}, {metadata.get('lon_center')})")
            print(f"   - Arquivo: {output_filename}")
            print(f"\n📄 HTML Content: {len(html_content):,} caracteres")
            print("📄" * 40 + "\n")
            
            logger.info(f"Iniciando geração de PDF: {total_markers} pontos")
            logger.info(f"HTML content: {len(html_content)} caracteres")
            
            # PASSO 1: Capturar screenshot via Playwright (HTML injection)
            print("📸 PASSO 1/4: Capturando screenshot com Playwright (HTML injection)...")
            logger.info("Chamando capture_map_screenshot com HTML content...")
            
            screenshot_bytes = await self.capture_map_screenshot(html_content)
            
            print("✓ Screenshot capturado em memória\n")
            logger.info("Screenshot capturado com sucesso")
            
            # PASSO 2: Salvar screenshot temporário
            print("💾 PASSO 2/4: Salvando screenshot temporário...")
            logger.info("Salvando bytes em arquivo temporário...")
            
            screenshot_filename = f"screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            screenshot_path = str(self.output_dir / screenshot_filename)
            
            with open(screenshot_path, 'wb') as f:
                f.write(screenshot_bytes)
            
            print(f"✓ Screenshot salvo: {screenshot_path}\n")
            logger.info(f"Screenshot salvo: {screenshot_path}")
            
            # PASSO 3: Gerar PDF (SYNC via executor)
            print("📝 PASSO 3/4: Gerando PDF com FPDF2...")
            logger.info("Executando _generate_pdf_sync via ThreadPoolExecutor...")
            
            loop = asyncio.get_running_loop()
            pdf_path = await loop.run_in_executor(
                self.executor,
                self._generate_pdf_sync,
                screenshot_path,
                output_filename,
                metadata
            )
            
            print(f"✓ PDF gerado: {pdf_path}\n")
            logger.info(f"PDF completo: {pdf_path}")
            
            print("✅ PDF GERADO COM SUCESSO\n")
            return pdf_path
            
        except Exception as e:
            error_trace = traceback.format_exc()
            
            logger.error("=" * 80)
            logger.error("🚨 ERRO NO FLUXO DE GERAÇÃO DE PDF")
            logger.error(f"Tipo: {type(e).__name__}")
            logger.error(f"Mensagem: {str(e)}")
            logger.error(f"Traceback:\n{error_trace}")
            logger.error("=" * 80)
            
            raise Exception(f"Erro na geração do PDF: {repr(e)}") from e
            
        finally:
            # 🧹 CLEANUP: Remover screenshot temporário
            if screenshot_path:
                screenshot_file = Path(screenshot_path)
                if screenshot_file.exists():
                    try:
                        screenshot_file.unlink()
                        logger.debug(f"✓ Screenshot temporário removido")
                    except Exception as cleanup_err:
                        logger.warning(f"⚠️  Erro ao remover temporário: {cleanup_err}")
    
    def __del__(self):
        """Cleanup do executor ao destruir o serviço."""
        if hasattr(self, 'executor'):
            self.executor.shutdown(wait=False)
