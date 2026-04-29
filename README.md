# Robo Nutrebem

[![Python 3.7+](https://img.shields.io/badge/python-3.7%2B-blue)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-UNLICENSED-red)](./LICENSE)
[![Security](https://img.shields.io/badge/security-hardened-brightgreen)](./SECURITY.md)

**Automation using Python Playwright** - A comprehensive automation toolkit for managing product restrictions and promotional credits in Nutrebem canteen systems across production and staging environments.

## 📋 About

This project provides a suite of automated robots for managing Nutrebem canteen operations. It uses Playwright for browser automation to:

- Read product IDs and student data from CSV files
- Navigate to the web application automatically
- Update product restrictions in bulk across environments
- Launch promotional credits to students
- Handle both production and staging environments
- Provide detailed logging and error reporting

**Target Systems:**
- **Production:** https://app.nutrebem.com.br
- **Staging:** https://nutrebem.dev.nutrebem.com.br

---

## 📊 Project Metadata

- **Version:** 1.0.0
- **Author:** Tarsius Oliveira
- **Repository:** https://github.com/tarsiusoliveira/Robos-Nutrebem
- **Python Version:** 3.7+
- **Status:** Active

---

## ⚠️ Security & Privacy

This project uses browser automation to manage restricted data. **Never commit sensitive data to version control:**

- ✅ `.gitignore` excludes:
  - `.env` files containing credentials
  - All `.csv` data files
  - Virtual environment files
  - IDE configuration

- ✅ Use environment variables for credentials (never hardcode)
- ✅ Use `.env.example` as a template for configuration
- ✅ Keep your `.env` file local and never share it

## Project Structure

```
.
├── .github/
│   └── copilot-instructions.md
├── .env.example                              (Template for environment variables)
├── .gitignore                                (Prevents accidental commits of sensitive data)
├── venv/                                     (Virtual environment - created by setup)
├── requirements.txt                          (Project dependencies)
├── robo_nutrebem_restrictions_prod.py        (Product restrictions for Production)
├── robo_nutrebem_restrictions_staging.py     (Product restrictions for Staging)
├── robo_promocredits.py                      (Promotional credits launcher)
├── leitor_contrato.py                        (Contract PDF data extractor)
├── SECURITY.md                               (Security guidelines)
├── README.md                                 (This file)
├── dados_exec_prod.csv                       (Production data - NOT committed)
└── dados_credito_promo.csv                   (Promo credits data - NOT committed)
```

## Setup Instructions

### 1. Clone the Repository

```bash
git clone <repository-url>
cd Testes_python
```

### 2. Create Virtual Environment

**On Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**On macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

**Create a `.env` file** (copy from `.env.example` and add your credentials):

```bash
cp .env.example .env
```

**Edit `.env` with your credentials:**
```
PROD_EMAIL=your_email@example.com
PROD_PASSWORD=your_password
STAGING_EMAIL=your_staging_email@example.com
STAGING_PASSWORD=your_staging_password
```

⚠️ **Never commit your `.env` file!** It's in `.gitignore` and should only exist locally.

### 5. Add Your Data Files

Place your CSV data files in the project root:
- `dados_exec_prod.csv` - Product IDs for production restrictions (Robo Restrições Produção)
- `dados_teste_staging.csv` - Product IDs for staging restrictions (Robo Restrições Staging)
- `dados_credito_promo.csv` - Student IDs and credit amounts (Robo Créditos Promocionais)

Or specify custom paths in your `.env` file:
```
PROD_CSV_FILE=path/to/your/prod_data.csv
STAGING_CSV_FILE=path/to/your/staging_data.csv
```

**CSV File Formats:**

**dados_exec_prod.csv & dados_teste_staging.csv:**
```
product_id
12345
67890
...
```

**dados_credito_promo.csv:**
```
student_id,prize_amount
S12345,10,00
S67890,15,00
...
```

⚠️ **Note:** All CSV files should be in `.gitignore` and never committed to version control.

## 🤖 Available Robots

### 1. **Robo Restrições Produção** (`robo_nutrebem_restrictions_prod.py`)
Updates product restrictions in the **production environment**.

**What it does:**
- Reads product IDs from `dados_exec_prod.csv`
- Authenticates using production credentials (`PROD_EMAIL` / `PROD_PASSWORD`)
- Batch updates product restrictions in https://app.nutrebem.com.br
- Provides detailed logging of all operations

**Configuration:**
```
PROD_EMAIL=your_prod_email@example.com
PROD_PASSWORD=your_prod_password
PROD_CSV_FILE=dados_exec_prod.csv
```

---

### 2. **Robo Restrições Staging** (`robo_nutrebem_restrictions_staging.py`)
Updates product restrictions in the **staging environment** for testing.

**What it does:**
- Reads product IDs from staging data file
- Authenticates using staging credentials (`STAGING_EMAIL` / `STAGING_PASSWORD`)
- Batch updates product restrictions in https://nutrebem.dev.nutrebem.com.br
- Provides detailed logging of all operations

**Configuration:**
```
STAGING_EMAIL=your_staging_email@example.com
STAGING_PASSWORD=your_staging_password
STAGING_CSV_FILE=dados_teste_staging.csv
```

---

### 3. **Robo Créditos Promocionais** (`robo_promocredits.py`)
Launches promotional credits to students (supports both production and staging).

**What it does:**
- Reads student IDs and promotional credit amounts from `dados_credito_promo.csv`
- Authenticates based on configured environment (STAGING or PRODUCAO)
- Batch creates promotional credit entries for each student
- Associates credits with a promotion name (e.g., "Sorteio Nutrebem 15 Anos")

**Configuration:**
- Edit the script to set `AMBIENTE = "PRODUCAO"` or `AMBIENTE = "STAGING"`
- Update `ARQUIVO_CSV` and `NOME_PROMO` as needed
- Uses same credentials as restriction robots

---

### 4. **Leitor Contrato** (`leitor_contrato.py`)
Extracts contract data from PDF files for bulk processing.

**What it does:**
- Reads PDF contract files from the specified directory
- Extracts structured data including:
  - School/Client information (name, address, CEP, etc.)
  - Bank account details (bank code, agency, account number)
  - Contact information (name, email, phone)
  - PIX keys and transaction rates
- Generates CSV output with extracted contract data
- Automatically identifies bank codes from text descriptions

**Configuration:**
- Specify the PDF directory path in the script
- Optional: Customize the output CSV file name
- Uses `pdfplumber` for PDF parsing

---

## Usage

### Run Production Restrictions Robot
```bash
python robo_nutrebem_restrictions_prod.py
```

### Run Staging Restrictions Robot
```bash
python robo_nutrebem_restrictions_staging.py
```

### Run Promotional Credits Robot
```bash
python robo_promocredits.py
```

### Run Contract Reader Robot
```bash
python leitor_contrato.py
```

**Tip:** Before running, modify the `AMBIENTE` variable in the script to select Production or Staging.

## Dependencies

- **playwright** (v1.40+) - Browser automation
- **pandas** (v2.0+) - Data handling
- **python-dotenv** (v1.0+) - Environment variable management

See `requirements.txt` for specific versions.

## Requirements

- Python 3.7+
- Internet connection (to access web applications)

## Security Checklist Before Publishing

- [ ] `.env` file is in `.gitignore` (never committed)
- [ ] `.csv` files are in `.gitignore` (never committed)
- [ ] `requirements.txt` contains all dependencies with pinned versions
- [ ] `.env.example` contains placeholder values (no real credentials)
- [ ] No hardcoded passwords, tokens, or API keys in Python files
- [ ] All sensitive data is loaded from environment variables
- [ ] README.md documents security practices

## Troubleshooting

### "PROD_EMAIL and PROD_PASSWORD environment variables are required"
- Ensure your `.env` file exists and contains valid credentials
- Check that `.env` is in the project root directory
- Verify environment variables are properly formatted

### "CSV file not found"
- Ensure your CSV files are in the project root or path specified in `.env`
- Check file names match exactly (case-sensitive on Linux/Mac)

### Import errors
- Activate your virtual environment: `source venv/bin/activate` (or `venv\Scripts\activate` on Windows)
- Reinstall dependencies: `pip install -r requirements.txt`

## Development

For local development, follow the setup instructions above. All configuration is environment-based, making it safe for collaborative development without sharing credentials.

## License

This project is currently **UNLICENSED**. 

For licensing inquiries or to discuss using this code, please contact the author.

## Contributing

We welcome contributions! Please read [CONTRIBUTING.md](./.github/CONTRIBUTING.md) for guidelines on:

- How to set up your development environment
- Code style and best practices
- Security considerations for sensitive projects
- Pull request process
- Reporting issues

**Key requirement:** Never commit sensitive data (credentials, tokens, API keys, or CSV files).

## Support

For issues, questions, or feature requests:
1. Check the [Troubleshooting](#troubleshooting) section
2. Review [SECURITY.md](./SECURITY.md) for security-related questions
3. Open an issue on GitHub (without sharing sensitive information)

## Changelog

### v1.0.0 (2026-04-23)
- Initial public release
- Environment-based credential management
- Security hardening for public deployment
- Comprehensive documentation
- Contribution guidelines
- Support for both production and staging environments

---

**Copyright © 2026 Tarsio Oliveira. All rights reserved.**


To add new dependencies, update `requirements.txt` and reinstall:
```bash
pip install -r requirements.txt
```
