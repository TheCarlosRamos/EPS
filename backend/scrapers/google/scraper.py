import requests
import random
import time
import os
import asyncio
from bs4 import BeautifulSoup
from scrapers.base import BaseScraper
from datetime import datetime

# Tentar importar Playwright
try:
    from playwright.async_api import async_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False

class GoogleScraper(BaseScraper):
    name = "google"
    supported_types = ["NAME", "CPF", "EMAIL", "PHONE"]
    
    USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15"
    ]

    def _get_demo_results(self, q):
        """Demo results for testing - usando endpoints corretos"""
        q_lower = q.lower()
        results = []
        
        # Gerar resultados demo realistas com endpoints CORRETOS
        demo_entries = [
            {
                "title": f"Informações sobre {q}",
                "url": f"https://pt.wikipedia.org/w/api.php?action=query&list=search&srsearch={q.replace(' ', '+')}&format=json",
                "source": "wikipedia",
                "note": "API endpoint - use /wiki/ para artigos diretos"
            },
            {
                "title": f"{q} - GitHub",
                "url": f"https://github.com/search?q={q.replace(' ', '%20')}",
                "source": "github"
            },
            {
                "title": f"{q} - Twitter/X",
                "url": f"https://x.com/search?q={q.replace(' ', '%20')}",
                "source": "twitter"
            }
        ]
        
        # NOTA: LinkedIn e Facebook removidos porque não permitem scraping público
        # LinkedIn redireciona todas as buscas públicas para login
        # Facebook bloqueia agressivamente scrapers
        
        return demo_entries[:3]

    def search_with_playwright(self, q):
        """Usar Playwright para renderizar JavaScript do Google"""
        if not PLAYWRIGHT_AVAILABLE:
            return []
        
        try:
            print(f"[GoogleScraper-Playwright] Tentando buscar: {q}")
            
            # Usar event loop existing ou criar novo
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            
            results = loop.run_until_complete(self._search_playwright_async(q))
            return results
            
        except Exception as e:
            print(f"[GoogleScraper-Playwright] Error: {e}")
            return []
    
    async def _search_playwright_async(self, q):
        """Async helper para Playwright (sem proxy para evitar timeout)"""
        try:
            async with async_playwright() as p:
                # Chromium com argumentos anti-detecção, SEM proxy
                browser = await p.chromium.launch(
                    headless=True,
                    args=[
                        "--no-sandbox",
                        "--disable-setuid-sandbox",
                        "--disable-web-resources",
                        "--disable-blink-features=AutomationControlled"
                    ]
                )
                
                context = await browser.new_context(
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                    viewport={"width": 1920, "height": 1080}
                )
                
                # Stealth: Hide webdriver property
                await context.add_init_script("""
                    Object.defineProperty(navigator, 'webdriver', {
                        get: () => false,
                    });
                """)
                
                page = await context.new_page()
                
                try:
                    url = f"https://www.google.com/search?q={q}&hl=pt-BR&num=10"
                    print(f"[GoogleScraper-Playwright] Navegando para: {url}")
                    
                    await page.goto(url, wait_until="networkidle", timeout=15000)
                    print("[GoogleScraper-Playwright] Página carregada")
                    
                    # Aceitar cookies/consentimento se houver botão
                    try:
                        await page.click("button:has-text('I agree'), button:has-text('Agree'), button:has-text('Aceitar')", timeout=1000)
                        await page.wait_for_timeout(500)
                    except:
                        pass
                    
                    # Extrair HTML
                    html = await page.content()
                    html_size = len(html)
                    print(f"[GoogleScraper-Playwright] HTML size: {html_size} bytes")
                    
                    # Se HTML muito pequeno, Google bloqueou
                    if html_size < 10000:
                        print("[GoogleScraper-Playwright] ⚠️ Google retornou página minimizada (bloqueado)")
                        return []
                    
                    soup = BeautifulSoup(html, 'html.parser')
                    results = []
                    
                    # Procurar qualquer <a> com href válido
                    for a in soup.select('a[href]'):
                        href = a.get('href', '')
                        text = a.text.strip()
                        
                        # Filtros básicos
                        if not href or len(text) < 3:
                            continue
                        
                        # Pular links do Google
                        if any(x in href.lower() for x in ['google.com', 'accounts.google', 'policies.google', 'mail.google', 'support.google', 'youtube.com']):
                            continue
                        
                        # URL processing
                        try:
                            if '/url?q=' in href:
                                from urllib.parse import unquote
                                url_clean = href.split('&sa=')[0].replace('/url?q=', '')
                                url_clean = unquote(url_clean)
                            elif href.startswith(('http://', 'https://')):
                                url_clean = href
                            elif href.startswith('/search'):
                                continue
                            else:
                                continue
                            
                            # Validar URL
                            if not url_clean.startswith(('http://', 'https://')):
                                continue
                            
                            result = {
                                "title": text[:100],
                                "url": url_clean,
                                "source": "google"
                            }
                            
                            # Evitar duplicatas
                            if not any(r['url'] == result['url'] for r in results):
                                results.append(result)
                                print(f"[GoogleScraper-Playwright] ✓ Found: {text[:50]}")
                                
                                if len(results) >= 5:
                                    break
                        except Exception as e:
                            continue
                    
                    print(f"[GoogleScraper-Playwright] Total encontrado: {len(results)} resultados")
                    return results
                    
                except Exception as e:
                    print(f"[GoogleScraper-Playwright] Error: {e}")
                    import traceback
                    traceback.print_exc()
                    return []
                        
                finally:
                    await page.close()
                    await context.close()
                    await browser.close()
                    
        except Exception as e:
            print(f"[GoogleScraper-Playwright-Async] Critical error: {e}")
            import traceback
            traceback.print_exc()
            return []

    def search(self, intent):
        q = intent['value']
        url = f"https://www.google.com/search?q={q}&hl=pt-BR&num=10"
        
        # Tentar com Playwright primeiro (renderiza JavaScript)
        if PLAYWRIGHT_AVAILABLE:
            print(f"[GoogleScraper] Tentando com Playwright: {q}")
            results = self.search_with_playwright(q)
            if results:
                return results
        
        # Fallback: BeautifulSoup
        print(f"[GoogleScraper] Fallback para BeautifulSoup: {q}")
        
        for attempt in range(2):
            try:
                headers = {
                    "User-Agent": random.choice(self.USER_AGENTS),
                    "Accept-Language": "pt-BR,pt;q=0.9",
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
                }
                r = requests.get(url, headers=headers, timeout=5)
                print(f"[GoogleScraper] Status: {r.status_code}")
                
                if r.status_code == 200:
                    soup = BeautifulSoup(r.text, 'html.parser')
                    results = []
                    
                    for item in soup.select('div.g, div[data-sokoban-container]')[:5]:
                        title_elem = item.select_one('h3')
                        link_elem = None
                        
                        for link in item.select('a'):
                            if link.get('href', '').startswith(('http', '/url')):
                                link_elem = link
                                break
                        
                        if title_elem and link_elem:
                            href = link_elem['href']
                            if '/url?q=' in href:
                                url_clean = href.split('&')[0].replace('/url?q=', '')
                            else:
                                url_clean = href
                            
                            if url_clean.startswith(('http://', 'https://')):
                                results.append({
                                    "title": title_elem.text.strip()[:100],
                                    "url": url_clean,
                                    "source": "google"
                                })
                    
                    if results:
                        print(f"[GoogleScraper] ✓ Encontrados {len(results)} links")
                        return results
                        
            except Exception as e:
                print(f"[GoogleScraper] Error (attempt {attempt+1}): {e}")
                time.sleep(0.5)
        
        # Fallback final: Demo data
        print(f"[GoogleScraper] Usando demo data para: {q}")
        return self._get_demo_results(q)
