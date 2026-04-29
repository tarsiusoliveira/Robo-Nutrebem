import pdfplumber
import pandas as pd
import re
import os

def identificar_codigo_banco(texto):
    texto_lower = texto.lower()
    mapa_bancos = {
        '001': ['banco do brasil', 'bb'], '341': ['itaú', 'itau', 'unibanco'],
        '104': ['caixa', 'cef', 'caixa econômica', 'caixa economica'],
        '237': ['bradesco'], '033': ['santander'], '260': ['nubank', 'nu pagamentos', 'nu'],
        '077': ['inter'], '336': ['c6'], '748': ['sicredi'], '756': ['sicoob'],
        '085': ['ailos', 'cecred', 'viacredi'], '290': ['pagseguro', 'pagbank'],
        '380': ['picpay'], '041': ['banrisul'], '422': ['safra'],
        '074': ['j. safra', 'j safra'], '212': ['original'],
        '655': ['neon', 'votorantim'], '136': ['unicred'],
        '070': ['brb', 'banco de brasília'], '389': ['mercantil'], '403': ['cora']
    }
    match_3digitos = re.search(r'\b(\d{3})\b', texto)
    if match_3digitos: return match_3digitos.group(1)
    for codigo, palavras_chave in mapa_bancos.items():
        for palavra in palavras_chave:
            if palavra in texto_lower: return codigo
    return texto.strip()

def extrair_dados_contrato(caminho_pdf):
    print(f"Lendo o arquivo: {os.path.basename(caminho_pdf)}...")
    texto_completo = ""
    
    try:
        with pdfplumber.open(caminho_pdf) as pdf:
            for page in pdf.pages:
                texto_completo += page.extract_text() + "\n"
    except Exception as e:
        print(f"Erro ao ler o PDF: {e}")
        return []

    dados_loja = {
        'escola_nome': '', 'escola_cep': '', 'escola_numero': '', 'escola_complemento': '', 
        'loja_contratante_nome': '', 'loja_cidade': '', 'loja_estado': '', 
        'loja_documento': '', 'loja_banco': '', 'loja_agencia': '', 'loja_agencia_digito': '', 
        'loja_conta': '', 'loja_conta_digito': '', 
        'loja_conta_titular_nome': '', 'loja_conta_titular_documento': '', 
        'loja_chave_pix': '', 'loja_taxa': '', 
        'contato_nome': '', 'contato_email': '', 'contato_telefone': '', 'crm_url': ''
    }

    match_contratante = re.search(r'\[(?:Razão Social|Nome|Nome Completo)\]\s*([^\n]+)', texto_completo, re.IGNORECASE)
    if match_contratante: dados_loja['loja_contratante_nome'] = match_contratante.group(1).strip()

    match_cnpj = re.search(r'\[(?:CNPJ|CPF)\]\s*([\d\.\-\/]+)', texto_completo, re.IGNORECASE)
    if match_cnpj: dados_loja['loja_documento'] = match_cnpj.group(1).strip()
        
    match_cidade_estado = re.search(r'\[MUNICÍPIO\]\s*(.+?)\s*-\s*([A-Za-z]{2})', texto_completo, re.IGNORECASE)
    if match_cidade_estado: 
        dados_loja['loja_cidade'] = match_cidade_estado.group(1).strip()
        dados_loja['loja_estado'] = match_cidade_estado.group(2).strip()

    match_banco = re.search(r'Banco:\s*([^\n]+)', texto_completo, re.IGNORECASE)
    if match_banco: dados_loja['loja_banco'] = identificar_codigo_banco(match_banco.group(1).strip())

    match_agencia = re.search(r'Agência:\s*(\d+)(?:[-]([\dxX]))?', texto_completo, re.IGNORECASE)
    if match_agencia:
        dados_loja['loja_agencia'] = match_agencia.group(1)
        dados_loja['loja_agencia_digito'] = match_agencia.group(2) if match_agencia.group(2) else ''

    match_conta = re.search(r'Conta Corrente:\s*(\d+)(?:[-]([\dxX]))?', texto_completo, re.IGNORECASE)
    if match_conta:
        dados_loja['loja_conta'] = match_conta.group(1)
        dados_loja['loja_conta_digito'] = match_conta.group(2) if match_conta.group(2) else ''

    match_chave_pix = re.search(r'Chave\s*Pix:\s*([^\n]+)', texto_completo, re.IGNORECASE)
    if match_chave_pix: dados_loja['loja_chave_pix'] = match_chave_pix.group(1).strip()

    match_titular = re.search(r'Titular:\s*([^\n]+)', texto_completo, re.IGNORECASE)
    if match_titular: 
        dados_loja['loja_conta_titular_nome'] = match_titular.group(1).strip()
        match_titular_doc = re.search(r'(?:CNPJ|CPF)[:\s]*([\d\.\-\/]+)', texto_completo[match_titular.end():], re.IGNORECASE)
        if match_titular_doc: dados_loja['loja_conta_titular_documento'] = match_titular_doc.group(1).strip()

    match_taxa = re.search(r'([\d\,\.]+\s*%)\s*da\s*receita', texto_completo, re.IGNORECASE)
    if match_taxa: dados_loja['loja_taxa'] = match_taxa.group(1).replace(' ', '').strip()

    match_nome = re.search(r'Nome do Responsável:\s*\n?([^\n]+)', texto_completo, re.IGNORECASE)
    if match_nome: dados_loja['contato_nome'] = match_nome.group(1).strip()

    match_email = re.search(r'E-mail do Responsável:\s*\n?([^\n]+)', texto_completo, re.IGNORECASE)
    if match_email: dados_loja['contato_email'] = match_email.group(1).strip()

    match_tel = re.search(r'Telefone do Responsável:\s*\n?([^\n]+)', texto_completo, re.IGNORECASE)
    if match_tel: dados_loja['contato_telefone'] = match_tel.group(1).strip()

    # ==========================================
    # NOVO MOTOR AGRESSIVO DE BUSCA DE ESCOLAS
    # ==========================================
    linhas_exportacao = []

    match_bloco_escolas = re.search(r'LOCAL DE INSTALA[ÇC][ÃA]O.*?([\r\n].*?)(?:Observa[çc][ãa]o|CONTA PARA DEP[ÓO]SITO|FORMA DE PAGAMENTO|DADOS DO)', texto_completo, re.IGNORECASE | re.DOTALL)
    
    if match_bloco_escolas:
        bloco_escolas = match_bloco_escolas.group(1).strip()
        escolas_fatiadas = re.split(r'\n\s*\d+[\)\.\-]\s+', '\n' + bloco_escolas)
        escolas_fatiadas = [e.strip() for e in escolas_fatiadas if len(e.strip()) > 5]

        for texto_escola in escolas_fatiadas:
            linha = dados_loja.copy()
            
            texto_escola = re.sub(r'(?:0\d|\d+)?\s*Termina(?:l|is).*?(\n|$)', '', texto_escola, flags=re.IGNORECASE|re.DOTALL).strip()
            
            # ATUALIZADO: Removido o 'Vila' da regra que indica endereço para não cortar nomes de escolas.
            match_nome = re.search(r'^(.*?)(?:Rua\b|R\.|Av\.|Avenida\b|Rodovia\b|Praça\b|Alameda\b|Estrada\b|Quadra\b|Setor\b|Lote\b|Travessa\b)', texto_escola, re.IGNORECASE | re.DOTALL)
            
            if match_nome:
                linha['escola_nome'] = match_nome.group(1).replace('\n', ' ').strip()
            else:
                linha['escola_nome'] = texto_escola.split('\n')[0].strip()

            match_cep = re.search(r'\b(\d{5}[\-\.]?\d{3})\b', texto_escola)
            if match_cep:
                linha['escola_cep'] = match_cep.group(1).replace('.', '').strip()

            match_numero = re.search(r'(?:,|n[ºo]|N[ºO]|Número|Numero)\s*(\d+[A-Za-z\d]*|[Ss]/[Nn]|S/N|SN)\b', texto_escola)
            if match_numero:
                linha['escola_numero'] = match_numero.group(1).strip()

            linhas_exportacao.append(linha)

    return linhas_exportacao

def processar_contratos():
    pasta_atual = os.getcwd()
    pasta_contratos = os.path.join(pasta_atual, "contratos_leitura")
    
    if not os.path.exists(pasta_contratos):
        os.makedirs(pasta_contratos)
        return

    arquivos_pdf = [f for f in os.listdir(pasta_contratos) if f.endswith('.pdf')]
    if not arquivos_pdf: return

    lista_dados = []
    for arquivo in arquivos_pdf:
        linhas_extraidas = extrair_dados_contrato(os.path.join(pasta_contratos, arquivo))
        if linhas_extraidas: lista_dados.extend(linhas_extraidas) 

    if lista_dados:
        ordem_colunas = [
            'escola_nome', 'escola_cep', 'escola_numero', 'escola_complemento',
            'loja_contratante_nome', 'loja_documento', 'loja_cidade', 'loja_estado', 
            'loja_banco', 'loja_agencia', 'loja_agencia_digito', 'loja_conta', 'loja_conta_digito', 
            'loja_conta_titular_nome', 'loja_conta_titular_documento', 'loja_chave_pix', 'loja_taxa', 
            'contato_nome', 'contato_email', 'contato_telefone', 'crm_url'
        ]
        df = pd.DataFrame(lista_dados)
        df = df.reindex(columns=ordem_colunas) 
        df.to_csv("planilha_onboarding_gerada.csv", index=False, encoding='utf-8-sig')
        print(f"Sucesso! Geradas {len(lista_dados)} linhas de {len(arquivos_pdf)} contratos lidos.")

if __name__ == "__main__":
    processar_contratos()