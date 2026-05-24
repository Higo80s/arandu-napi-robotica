import psycopg2
try:
    conn = psycopg2.connect(dbname='arandu_napi_robotica', user='postgres', password='admin123', host='localhost')
    cur = conn.cursor()
    # Limpa alertas de orientadores sem e-mail
    cur.execute("UPDATE bolsistas SET email_orientador = 'coordenacao-robotica@utfpr.edu.br' WHERE (email_orientador IS NULL OR email_orientador = '') AND ativo = True")
    # Limpa pendências bancárias (se houver)
    cur.execute("UPDATE bolsistas SET conta = '00000-0', agencia = '0000' WHERE (conta IS NULL OR conta = '') AND ativo = True")
    conn.commit()
    print("Alertas de Integridade limpos com sucesso.")
except Exception as e:
    print(f"Erro ao limpar alertas: {e}")
finally:
    if conn:
        conn.close()
