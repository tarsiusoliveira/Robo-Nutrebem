from playwright.sync_api import sync_playwright
import pandas as pd
import time
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# ==========================================
# CONFIGURAÇÕES DO ROBÔ
# ==========================================
AMBIENTE = "STAGING"  # Mude para "PRODUCAO" quando for rodar o real
ARQUIVO_CSV = os.getenv('PROMO_CSV_FILE', 'dados_credito_promo.csv')
NOME_PROMO = os.getenv('PROMO_NAME', 'Sorteio Nutrebem 15 Anos')

# Get credentials from environment variables
EMAIL = os.getenv('PROMO_EMAIL')
PASSWORD = os.getenv('PROMO_PASSWORD')

if not EMAIL or not PASSWORD:
    raise ValueError("PROMO_EMAIL and PROMO_PASSWORD environment variables are required. See .env.example for setup.")

# Dicionário de URLs para facilitar a troca de ambiente
URLS = {
    "STAGING": {
        "login": "https://nutrebem.dev.nutrebem.com.br/pt-BR/login",
        "credito": "https://nutrebem.dev.nutrebem.com.br/pt-BR/admin/students/{}/promotional_credits/new"
    },
    "PRODUCAO": {
        "login": "https://app.nutrebem.com.br/pt-BR/login",
        "credito": "https://app.nutrebem.com.br/pt-BR/admin/students/{}/promotional_credits/new"
    }
}

def lancar_creditos_promocionais():
    print(f"[{AMBIENTE}] Carregando base de dados: {ARQUIVO_CSV}...")
    
    try:
        # Lê o arquivo. Força o prize_amount a ser lido como string para não perder formatação (ex: 10,00)
        df = pd.read_csv(ARQUIVO_CSV, dtype={'student_id': str, 'prize_amount': str})
    except FileNotFoundError:
        print(f"ERRO: Arquivo {ARQUIVO_CSV} não encontrado na pasta.")
        return

    total_alunos = len(df)
    print(f"Total de alunos para receber crédito: {total_alunos}")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36"
        )
        page = context.new_page()

        # Aceita modais de confirmação automaticamente (mesma tática que usamos com sucesso antes!)
        page.on("dialog", lambda dialog: dialog.accept())

        # 1. Fazer Login
        print(f"Iniciando processo de Login ({AMBIENTE})...")
        page.goto(URLS[AMBIENTE]["login"]) 
        
        # Use credentials from environment variables
        page.fill("input[type='text'], input[type='email']", EMAIL)
        page.fill("input[type='password']", PASSWORD)
        page.click("input[type='submit'], button:has-text('Entrar')") 
        
        page.wait_for_load_state('networkidle')
        print("Login realizado com sucesso! Iniciando os lançamentos de crédito...")

        sucessos = 0
        erros = 0
        
        # 2. Iterar sobre os alunos
        for index, row in df.iterrows():
            aluno_id = row['student_id'].strip()
            valor_credito = row['prize_amount'].strip()
            
            print(f"[{index + 1}/{total_alunos}] Lançando R$ {valor_credito} para o Aluno ID {aluno_id}...")
            
            # Monta a URL trocando o "{}" pelo ID do aluno
            url_aluno = URLS[AMBIENTE]["credito"].format(aluno_id)
            
            try:
                page.goto(url_aluno)
                page.wait_for_load_state('load')
                
                # Preenche os campos usando os seletores de ID que você forneceu
                page.fill("input[id='credit_value']", valor_credito)
                page.fill("input[id='credit_sale_name']", NOME_PROMO)
                
                # Clica em Salvar (busca o input de envio do formulário)
                page.click("input[type='submit'][name='commit'], button[type='submit']")
                
                # Aguarda o salvamento
                page.wait_for_load_state('networkidle')
                print(f" -> Sucesso!")
                sucessos += 1
                    
            except Exception as e:
                print(f" -> ERRO ao processar Aluno ID {aluno_id}: {e}")
                erros += 1
                
            # Pausa de 1 segundo para não sobrecarregar o sistema
            time.sleep(1)

        print("\n" + "="*45)
        print(f"PROCESSO DE {AMBIENTE} FINALIZADO!")
        print(f"Total Sucessos: {sucessos} | Total Erros: {erros}")
        print("="*45)

        browser.close()

if __name__ == "__main__":
    lancar_creditos_promocionais()