-- 1. Performance: Índice para Dashboards de Evolução Histórica
-- Acelera consultas que filtram por Ano e Agência (ex: "Evolução CAPES 2014-2025")
CREATE INDEX IF NOT EXISTS idx_bolsa_agregado 
ON bolsa_historico (ano, agencia, nivel);

-- 2. Segurança: Tabela de Log de Auditoria
CREATE TABLE IF NOT EXISTS auditoria_logs (
    id SERIAL PRIMARY KEY,
    tabela_afetada VARCHAR(50),
    id_registro INTEGER,
    coluna_afetada VARCHAR(50),
    valor_antigo TEXT,
    valor_novo TEXT,
    usuario_responsavel VARCHAR(100), -- Capturar do Flask User
    data_alteracao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. Trigger: Monitorar alterações críticas em 'tipo_oferta'
-- Impede que um Programa Profissional vire Acadêmico sem registro
CREATE OR REPLACE FUNCTION log_alteracao_programa()
RETURNS TRIGGER AS $$
BEGIN
    IF OLD.tipo_oferta IS DISTINCT FROM NEW.tipo_oferta THEN
        INSERT INTO auditoria_logs (tabela_afetada, id_registro, coluna_afetada, valor_antigo, valor_novo, usuario_responsavel)
        VALUES ('programa_academico', NEW.id, 'tipo_oferta', OLD.tipo_oferta, NEW.tipo_oferta, current_user);
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_audit_programa ON programa_academico;

CREATE TRIGGER trg_audit_programa
AFTER UPDATE ON programa_academico
FOR EACH ROW
EXECUTE FUNCTION log_alteracao_programa();
