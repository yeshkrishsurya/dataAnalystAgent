import requests
from bs4 import BeautifulSoup
import pandas as pd
import json
from typing import Dict, List, Any

class WebScrapingTools:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def scrape_wikipedia(self, url: str) -> str:
        """Scrape Wikipedia pages and extract tabular data"""
        try:
            response = self.session.get(url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find all tables on the page
            tables = soup.find_all('table', {'class': 'wikitable'})
            
            if not tables:
                return json.dumps({"error": "No wikitable found on the page"})
            
            # Process the first suitable table (usually the main data table)
            table_data = []
            for table in tables:
                rows = table.find_all('tr')
                if len(rows) < 2:  # Skip tables with no data rows
                    continue
                
                # Extract headers
                header_row = rows[0]
                headers = []
                for th in header_row.find_all(['th', 'td']):
                    text = th.get_text(strip=True)
                    headers.append(text)
                
                if not headers:
                    continue
                
                # Extract data rows
                for row in rows[1:]:
                    cells = row.find_all(['td', 'th'])
                    if len(cells) < len(headers):
                        continue
                    
                    row_data = {}
                    for i, cell in enumerate(cells[:len(headers)]):
                        cell_text = cell.get_text(strip=True)
                        # Clean up common Wikipedia formatting
                        cell_text = cell_text.replace('\n', ' ').replace('[edit]', '').strip()
                        if i < len(headers):
                            row_data[headers[i]] = cell_text
                    
                    if row_data:
                        table_data.append(row_data)
                
                # If we found data, break (use first table with data)
                if table_data:
                    break
            
            if not table_data:
                return json.dumps({"error": "No data found in tables"})
            
            return json.dumps({
                "success": True,
                "data": table_data,
                "headers": headers,
                "row_count": len(table_data)
            })
            
        except Exception as e:
            return json.dumps({"error": f"Failed to scrape Wikipedia: {str(e)}"})
    
    def scrape_web(self, url: str) -> str:
        """General web scraping for other sites"""
        try:
            response = self.session.get(url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Try to find tables first
            tables = soup.find_all('table')
            if tables:
                return self._extract_table_data(tables[0])
            
            # If no tables, return text content
            text_content = soup.get_text(strip=True)
            return json.dumps({
                "success": True,
                "content": text_content[:5000],  # Limit content size
                "type": "text"
            })
            
        except Exception as e:
            return json.dumps({"error": f"Failed to scrape web page: {str(e)}"})
    
    def _extract_table_data(self, table) -> str:
        """Extract data from HTML table"""
        try:
            rows = table.find_all('tr')
            if len(rows) < 2:
                return json.dumps({"error": "Table has insufficient data"})
            
            # Extract headers
            header_row = rows[0]
            headers = [th.get_text(strip=True) for th in header_row.find_all(['th', 'td'])]
            
            # Extract data
            table_data = []
            for row in rows[1:]:
                cells = row.find_all(['td', 'th'])
                if len(cells) >= len(headers):
                    row_data = {}
                    for i, cell in enumerate(cells[:len(headers)]):
                        row_data[headers[i]] = cell.get_text(strip=True)
                    table_data.append(row_data)
            
            return json.dumps({
                "success": True,
                "data": table_data,
                "headers": headers,
                "row_count": len(table_data)
            })
        except Exception as e:
            return json.dumps({"error": f"Failed to extract table data: {str(e)}"})