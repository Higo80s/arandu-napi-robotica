import os

# Path to the file
file_path = r'c:\Users\higosantos\Documents\gestao_editais\gestao_editais_novo\templates\bolsistas\form.html'

def update_form():
    if not os.path.exists(file_path):
        print(f"Error: File not found at {file_path}")
        return

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Define the block start and key identifier for the end
    start_marker = '<div id="add-mobilidade-form" class="card"'
    # The cancel button onclick inside the form is a unique enough anchor for the end
    end_anchor = "document.getElementById('add-mobilidade-form').style.display='none'"
    
    start_idx = content.find(start_marker)
    if start_idx == -1:
        print("Start marker not found. Block might already be replaced.")
        return

    # Find the end of the div. 
    # Logic: Find the end_anchor, then find the next closing </div> which closes the card.
    
    anchor_idx = content.find(end_anchor, start_idx)
    if anchor_idx == -1:
        print("End anchor not found.")
        return
        
    # Find the closing form tag
    form_close_idx = content.find('</form>', anchor_idx)
    # Find the closing div tag after form close
    div_close_idx = content.find('</div>', form_close_idx) + 6 # include </div>

    if div_close_idx == -1:
        print("Could not find closing div.")
        return

    old_block = content[start_idx:div_close_idx]
    
    # New Modal Content
    new_html = """<!-- MOBILIDADE MODAL (Updated via Script) -->
<div id="mobilidadeModal" class="modal-overlay" style="display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.5); z-index: 2000;">
    <div class="modal-content" style="background: white; padding: 2rem; border-radius: 8px; max-width: 700px; margin: 5% auto; position: relative;">
        
        <h3 style="color: var(--primary-color); margin-top: 0; margin-bottom: 1.5rem;">Registrar Mobilidade Internacional</h3>
        
        <form action="{{ url_for('mobilidade_novo', id=bolsista.id) }}" method="POST">
            
            <div style="margin-bottom: 1.5rem;">
                <label class="form-label" style="color: #111827; font-weight: 600; display: block; margin-bottom: 0.5rem;">Fluxo (Direção)</label>
                <select name="tipo_fluxo" id="mob_tipo_fluxo" class="form-control form-select" onchange="updateMobLabels()"
                    style="width: 100%; padding: 0.75rem; border: 1px solid #d1d5db; border-radius: 0.375rem; font-size: 1rem;">
                    <option value="saida">Saída (Brasileiro indo ao Exterior)</option>
                    <option value="entrada">Entrada (Estrangeiro vindo à UTFPR)</option>
                </select>
            </div>

            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin-bottom: 1rem;">
                <div>
                    <label class="form-label" id="lbl_pais" style="color: #111827; font-weight: 500; display: block; margin-bottom: 0.5rem;">País de Destino</label>
                    <input type="text" name="pais_destino" required class="form-control" placeholder="Ex: França"
                        style="width: 100%; padding: 0.5rem; border: 1px solid #d1d5db; border-radius: 0.375rem;">
                </div>
                <div>
                    <label class="form-label" id="lbl_inst" style="color: #111827; font-weight: 500; display: block; margin-bottom: 0.5rem;">Instituição de Destino</label>
                    <input type="text" name="instituicao_destino" required class="form-control" placeholder="Ex: Sorbonne"
                        style="width: 100%; padding: 0.5rem; border: 1px solid #d1d5db; border-radius: 0.375rem;">
                </div>
            </div>
            
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin-bottom: 1rem;">
                 <div>
                    <label class="form-label" style="color: #111827; font-weight: 500; display: block; margin-bottom: 0.5rem;">Início</label>
                    <input type="date" name="data_inicio" required class="form-control"
                        style="width: 100%; padding: 0.5rem; border: 1px solid #d1d5db; border-radius: 0.375rem;">
                </div>
                <div>
                    <label class="form-label" style="color: #111827; font-weight: 500; display: block; margin-bottom: 0.5rem;">Fim</label>
                    <input type="date" name="data_fim" required class="form-control"
                        style="width: 100%; padding: 0.5rem; border: 1px solid #d1d5db; border-radius: 0.375rem;">
                </div>
            </div>

            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin-bottom: 1.5rem;">
                 <div>
                    <label class="form-label" style="color: #111827; font-weight: 500; display: block; margin-bottom: 0.5rem;">Tipo</label>
                    <select name="tipo_mobilidade" class="form-control form-select"
                        style="width: 100%; padding: 0.5rem; border: 1px solid #d1d5db; border-radius: 0.375rem;">
                        <option value="Doutorado Sanduíche">Doutorado Sanduíche</option>
                        <option value="Pos-Doutorado">Pós-Doutorado (Exterior)</option>
                        <option value="Estágio Sênior">Estágio Sênior</option>
                        <option value="Co-tutela">Co-tutela</option>
                        <option value="Dupla Diplomação">Dupla Diplomação</option>
                        <option value="Visita Técnica">Visita Técnica</option>
                        <option value="Intercâmbio (Graduação)">Intercâmbio (Graduação)</option>
                        <option value="Outros">Outros</option>
                    </select>
                </div>
                <div>
                    <label class="form-label" style="color: #111827; font-weight: 500; display: block; margin-bottom: 0.5rem;">Agência (Opcional)</label>
                    <input type="text" name="agencia_fomento" class="form-control" placeholder="Ex: CAPES-PrInt"
                         style="width: 100%; padding: 0.5rem; border: 1px solid #d1d5db; border-radius: 0.375rem;">
                </div>
            </div>
            
            <div class="d-flex gap-2" style="display: flex; gap: 1rem;">
                <button type="submit" class="btn btn-primary" style="flex: 1; padding: 0.75rem; background-color: var(--primary-color); color: white; border: none; border-radius: 0.375rem; cursor: pointer;">Salvar Registro</button>
                <button type="button" class="btn btn-secondary" style="flex: 1; padding: 0.75rem; background-color: #9ca3af; color: white; border: none; border-radius: 0.375rem; cursor: pointer;"
                    onclick="document.getElementById('mobilidadeModal').style.display='none'">Cancelar</button>
            </div>
        </form>
    </div>
</div>

<script>
    function updateMobLabels() {
        const fluxo = document.getElementById('mob_tipo_fluxo').value;
        const lblPais = document.getElementById('lbl_pais');
        const lblInst = document.getElementById('lbl_inst');
        
        if (fluxo === 'entrada') {
            lblPais.innerText = "País de Origem (Instituição Parceira)";
            lblInst.innerText = "Instituição de Origem (Parceira)";
        } else {
            lblPais.innerText = "País de Destino (Exterior)";
            lblInst.innerText = "Instituição de Destino (Parceira)";
        }
    }
</script>"""

    new_content = content.replace(old_block, new_html)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print("Form updated successfully.")

if __name__ == "__main__":
    update_form()
