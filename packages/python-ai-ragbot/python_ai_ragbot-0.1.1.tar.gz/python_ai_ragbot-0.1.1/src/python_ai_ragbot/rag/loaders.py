import os
import time
import requests
from bs4 import BeautifulSoup
from langchain_community.document_loaders import TextLoader, PyPDFLoader, UnstructuredWordDocumentLoader
from langchain.schema import Document

class URLScraper:
    def __init__(self, timeout=30, delay=1.2):
        self.timeout = timeout
        self.delay = delay
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })

    def extract_content(self, url):
        """Extract content from a URL similar to the Puppeteer implementation"""
        try:
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            
            # Add delay similar to Puppeteer
            time.sleep(self.delay)
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove unwanted elements
            unwanted_selectors = [
                'script', 'style', 'noscript', 'nav',
                '.cookie-banner', '.popup', '.modal', 
                '.advertisement', '.ads', '[class*="cookie"]',
                '[class*="popup"]', '[class*="modal"]',
                '[class*="ad"]', 'header', 'footer'
            ]
            
            for selector in unwanted_selectors:
                for element in soup.select(selector):
                    element.decompose()
            
            # Extract title
            title = ""
            title_element = soup.find('title')
            if title_element:
                title = title_element.get_text(strip=True)
            elif soup.find('h1'):
                title = soup.find('h1').get_text(strip=True)
            
            # Extract meta description
            meta_desc = ""
            meta_element = soup.find('meta', attrs={'name': 'description'})
            if meta_element:
                meta_desc = meta_element.get('content', '').strip()
            
            # Extract headings
            headings = []
            for tag in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                for heading in soup.find_all(tag):
                    text = heading.get_text(strip=True)
                    if len(text) > 3:
                        headings.append(f"{tag.upper()}: {text}")
            
            # Extract content blocks
            content_selectors = [
                'p', 'li', 'blockquote', 'section', 'article', 'main', 'div', 'span',
                '[role="main"]', '[role="article"]', '[role="contentinfo"]'
            ]
            
            content_blocks = []
            seen_texts = set()
            
            for selector in content_selectors:
                for element in soup.select(selector):
                    text = element.get_text(strip=True)
                    # Filter out short texts and duplicates
                    if (len(text) > 30 and 
                        text not in seen_texts and 
                        len([c for c in text if c.isalnum()]) > 10):
                        content_blocks.append(text)
                        seen_texts.add(text)
            
            # Build final content
            content_parts = []
            
            if title:
                content_parts.append(f"TITLE: {title}")
            
            if meta_desc:
                content_parts.append(f"DESCRIPTION: {meta_desc}")
            
            if headings:
                content_parts.append(f"HEADINGS:\n{chr(10).join(headings)}")
            
            if content_blocks:
                content_parts.append(f"CONTENT:\n{chr(10).join(content_blocks)}")
            
            final_content = "\n\n".join(content_parts)
            
            # Return content if it's substantial enough
            if len(final_content.strip()) > 50:
                return {'url': url, 'content': final_content}
            
            return None
            
        except Exception as e:
            return None

    def close(self):
        """Close the session"""
        self.session.close()


def load_documents(files=None, urls=None, logger=print):
    """
    Load documents from a list of files (txt, md, pdf, docx) and URLs.
    
    Args:
        files: List of file paths
        urls: List of URLs to scrape
        logger: Function to log messages
        
    Returns:
        List of Document objects
    """
    docs = []
    
    # Load files
    if files:
        for f in files:
            if not os.path.exists(f):
                logger(f"File not found: {f}")
                continue

            ext = os.path.splitext(f)[-1].lower()
            try:
                if ext in [".txt", ".md"]:
                    loader = TextLoader(f, encoding="utf-8")
                elif ext == ".pdf":
                    loader = PyPDFLoader(f)
                elif ext == ".docx":
                    loader = UnstructuredWordDocumentLoader(f)
                else:
                    logger(f"Unsupported file type: {f}")
                    continue

                file_docs = loader.load()
                docs.extend(file_docs)
                logger(f"Loaded {len(file_docs)} documents from {f}")

            except Exception as e:
                logger(f"Failed to load {f}: {e}")
    
    # Load URLs
    if urls:
        scraper = URLScraper()
        try:
            for url in urls:
                try:
                    logger(f"Scraping URL: {url}")
                    result = scraper.extract_content(url)
                    
                    if result:
                        # Create a Document object similar to langchain loaders
                        doc = Document(
                            page_content=result['content'],
                            metadata={
                                'source': result['url'],
                                'type': 'url'
                            }
                        )
                        docs.append(doc)
                        logger(f"Successfully scraped: {url}")
                    else:
                        logger(f"No substantial content found for: {url}")
                        
                except Exception as e:
                    logger(f"Failed to scrape {url}: {e}")
        finally:
            scraper.close()

    logger(f"Total documents loaded: {len(docs)}")
    return docs
