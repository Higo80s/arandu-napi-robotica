# Guia de Registro de Software no INPI (Contexto Universitário)

Este guia orienta o processo de registro do **Gestão de Editais** no Instituto Nacional da Propriedade Industrial (INPI).

> **IMPORTANTE:** Como o software foi desenvolvido no contexto da **UTFPR** (Universidade Pública), é altamente provável que a instituição seja **Cotitular** (Dona em conjunto) da propriedade intelectual.

## 1. Passo Zero: Falar com o NIT
Antes de pagar qualquer guia no INPI, entre em contato com o **Núcleo de Inovação Tecnológica (NIT)** ou **DIRAGI** do seu campus.

*   **Por quê?** A universidade geralmente paga as taxas e cuida da burocracia para você.
*   **O que levar?** Eles vão pedir o "Código Fonte" e o "Hash". Nós já geramos isso para você (veja abaixo).

## 2. Documentos Gerados (Já estão prontos!)
Executei um script que preparou o pacote técnico exigido pelo INPI em 2025.

1.  **Arquivo de Fonte e Hash**: `docs/INPI_FONTE_PARA_PDF.txt`
    *   **Ação Necessária**: Abra este arquivo e "Imprima como PDF".
    *   Este PDF contém o **Hash SHA-256** (A "digital" do seu software) e as primeiras/últimas linhas do código fonte, provando que ele existe.

## 3. Fluxo no INPI (Se você for fazer sozinho)
Caso o NIT autorize você a fazer o registro em seu nome (ou se for projeto pessoal):

1.  **Acesso**: Entre no [e-INPI](https://gru.inpi.gov.br/pePI/).
2.  **GRU**: Gere a Guia de Recolhimento (Serviço 730 - Registro de Programa de Computador).
    *   *Valor aprox:* R$ 185,00.
    *   *Dica:* Guarde o número da GRU ("Nosso Número").
3.  **Formulário e-Software**:
    *   Acesse o sistema e-Software.
    *   Insira o número da GRU paga.
    *   **Campo "Resumo Hash"**: Copie o código HASH que está na primeira linha do arquivo `INPI_FONTE_PARA_PDF.txt`.
    *   **Anexo**: Anexe a **Declaração de Veracidade (DV)** assinada digitalmente (Gov.br).

## 4. O que é o HASH?
O INPI não pede mais o código fonte inteiro (CD/Pendrive). Eles pedem um **Resumo Criptográfico (Hash)**.
Se alguém copiar seu software no futuro, um perito judicial calculará o hash da cópia pirata. Se bater com o hash que registramos hoje, está provada a cópia.

---
**Seu Hash Gerado (SHA-256):**
*(Verifique no arquivo gerado `docs/INPI_FONTE_PARA_PDF.txt`)*
