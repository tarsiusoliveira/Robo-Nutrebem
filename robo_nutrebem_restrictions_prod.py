from playwright.sync_api import sync_playwright
import pandas as pd
import time
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def limpar_restricoes_producao():
    # Get credentials from environment variables
    email = os.getenv('PROD_EMAIL')
    password = os.getenv('PROD_PASSWORD')
    csv_file = os.getenv('PROD_CSV_FILE', 'dados_exec_prod.csv')
    
    if not email or not password:
        raise ValueError("PROD_EMAIL and PROD_PASSWORD environment variables are required. See .env.example for setup.")
    
    if not os.path.exists(csv_file):
        raise FileNotFoundError(f"CSV file not found: {csv_file}")
    
    print("Carregando base de dados de PRODUÇÃO...")
    # 1. Load CSV file
    df = pd.read_csv(csv_file)
    
    # 2. Varredura completa: pega todos os IDs únicos do arquivo inteiro
    produtos_unicos = df['product_id'].unique()
    
    total_tarefas = len(produtos_unicos)
    print(f"Total de produtos únicos para atualizar em PRODUÇÃO: {total_tarefas}")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36"
        )
        page = context.new_page()

        # Intercepta e clica em "OK" em qualquer modal/alerta do sistema
        page.on("dialog", lambda dialog: dialog.accept())

        # 3. Fazer Login (URL de Produção)
        print("Iniciando processo de Login em Produção...")
        page.goto("https://app.nutrebem.com.br/pt-BR/login") 
        
        # Use credentials from environment variables
        page.fill("input[type='text']", email)
        page.fill("input[type='password']", password)
        page.click("input[type='submit'], button:has-text('Entrar')") 
        
        page.wait_for_load_state('networkidle')
        print("Login realizado com sucesso! Iniciando as correções em massa...")

        sucessos = 0
        erros = 0
        
        # Iterar sobre todos os produtos problemáticos
        for i, produto_id in enumerate(produtos_unicos):
            print(f"[{i + 1}/{total_tarefas}] Atualizando Produto {produto_id}...")
            
            # 4. URL de edição de produtos (Produção)
            url_edicao = f"https://app.nutrebem.com.br/pt-BR/canteen_operator/product_restrictions/{produto_id}/edit"
            
            try:
                page.goto(url_edicao)
                page.wait_for_load_state('load') 
                
                # Clica em Salvar (gatilhando a limpeza automática do banco e aceitando o modal)
                page.click("input[name='commit'][value='Salvar restrições']")
                
                # Aguarda o salvamento e o redirecionamento
                page.wait_for_load_state('networkidle')
                print(f" -> Sucesso!")
                sucessos += 1
                    
            except Exception as e:
                print(f" -> ERRO ao processar produto {produto_id}: {e}")
                erros += 1
                
            # Pausa de 1 segundo mantida para não sobrecarregar o servidor de Produção
            time.sleep(1)

        print("\n" + "="*40)
        print("PROCESSO DE PRODUÇÃO FINALIZADO!")
        print(f"Sucessos: {sucessos} | Erros: {erros}")
        print("="*40)

        browser.close()

if __name__ == "__main__":
    limpar_restricoes_producao()