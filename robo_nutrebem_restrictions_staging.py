from playwright.sync_api import sync_playwright
import pandas as pd
import time
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def limpar_restricoes_staging():
    # Get credentials from environment variables
    email = os.getenv('STAGING_EMAIL')
    password = os.getenv('STAGING_PASSWORD')
    csv_file = os.getenv('STAGING_CSV_FILE', 'dados_teste_staging.csv')
    
    if not email or not password:
        raise ValueError("STAGING_EMAIL and STAGING_PASSWORD environment variables are required. See .env.example for setup.")
    
    if not os.path.exists(csv_file):
        raise FileNotFoundError(f"CSV file not found: {csv_file}")
    
    print("Carregando base de dados de Staging...")
    # 1. Load CSV file
    df = pd.read_csv(csv_file)
    
    # 2. Removido o filtro da escola 199. Agora ele pega os IDs únicos do arquivo inteiro!
    produtos_unicos = df['product_id'].unique()
    
    total_tarefas = len(produtos_unicos)
    print(f"Total de produtos únicos para atualizar no Staging: {total_tarefas}")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36"
        )
        page = context.new_page()

        # Aceita (clica em OK) em qualquer modal/alerta do navegador automaticamente
        page.on("dialog", lambda dialog: dialog.accept())

        # 3. Fazer Login (Nova URL de Staging)
        print("Iniciando processo de Login no Staging...")
        page.goto("https://nutrebem.dev.nutrebem.com.br/pt-BR/login") 
        
        # Use credentials from environment variables
        page.fill("input[type='text']", email)
        page.fill("input[type='password']", password)
        page.click("input[type='submit'], button:has-text('Entrar')") 
        
        page.wait_for_load_state('networkidle')
        print("Login realizado com sucesso! Iniciando as correções em massa...")

        sucessos = 0
        erros = 0
        
        # Iterar sobre todos os produtos mapeados
        for i, produto_id in enumerate(produtos_unicos):
            print(f"[{i + 1}/{total_tarefas}] Atualizando Produto {produto_id}...")
            
            # 4. Nova URL de edição de produtos (Staging)
            url_edicao = f"https://nutrebem.dev.nutrebem.com.br/pt-BR/canteen_operator/product_restrictions/{produto_id}/edit"
            
            try:
                page.goto(url_edicao)
                page.wait_for_load_state('load') 
                
                # Clica em Salvar (O sistema limpa as séries fantasmas e o script aceita o modal)
                page.click("input[name='commit'][value='Salvar restrições']")
                
                # Aguarda o salvamento e o redirecionamento
                page.wait_for_load_state('networkidle')
                print(f" -> Sucesso!")
                sucessos += 1
                    
            except Exception as e:
                print(f" -> ERRO ao processar produto {produto_id}: {e}")
                erros += 1
                
            time.sleep(1)

        print("\n" + "="*40)
        print("PROCESSO DE STAGING FINALIZADO!")
        print(f"Sucessos: {sucessos} | Erros: {erros}")
        print("="*40)

        browser.close()

if __name__ == "__main__":
    limpar_restricoes_staging()