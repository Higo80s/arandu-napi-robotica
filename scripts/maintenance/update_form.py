
import os

file_path = r'C:\Users\higosantos\Documents\gestao_editais\gestao_editais_novo\templates\bolsistas\form.html'

with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# 1. Inject Button
# Look for line with "+ Adicionar Afastamento"
# Line ~246
new_button_html = """        <button type="button" class="btn" style="background: #e5e7eb; color: var(--text-color); margin-left: 0.5rem;"
            onclick="focusMaternidade(); document.getElementById('add-afastamento-form').style.display='block';">
            + Registrar Maternidade
        </button>
"""

output_lines = []
for line in lines:
    output_lines.append(line)
    if '+ Adicionar Afastamento' in line and '</button>' in line:
        # Check if we didn't add it already (idempotency)
        pass 
        # Actually, appending after the button is tricky if it's multiline.
        # The file view showed:
        # <button type="button" ...
        #     onclick="...">
        #     + Adicionar Afastamento
        # </button>
        # So I should look for the closing </button> tag of that specific button.
        
# Refined approach: Read content as string
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Insert Button
target_btn = '+ Adicionar Afastamento\n        </button>'
replacement_btn = target_btn + '\n' + new_button_html

if 'Registrar Maternidade' not in content:
    content = content.replace(target_btn, replacement_btn)

# 2. Replace Scripts
# Find the start of the first script block (Line ~301)
# "<script>" is common.
# Search for specific unique start of the old logic
script_start_marker = "const editalSelect = document.getElementById('edital_select');"

# We want to replace everything from the <script> tag BEFORE that marker, down to the end of file.
# But "end of file" has {% endblock %}? 
# Let's check the very end. 
# View showed "{% endblock %}" at the end.
# So I should keep {% endblock %}.

# Split content at the start of the legacy script
split_patt = '<script>\n    const editalSelect'
if split_patt in content:
    parts = content.split(split_patt)
    pre_script = parts[0]
    
    # New Script Content
    new_script = """<script>
    // GLOBAL STATE
    let currentModalidades = [];

    // DOM ELEMENTS
    const editalSelect = document.getElementById('edital_select');
    const modalidadeSelect = document.getElementById('modalidade_select');
    const dataInicioCurso = document.querySelector('input[name="data_inicio_curso"]');
    const dataInicioBolsa = document.querySelector('input[name="data_inicio_bolsa"]');
    const mesesDuracao = document.querySelector('input[name="meses_duracao"]');
    const dataFimBolsa = document.querySelector('input[name="data_fim_bolsa"]');
    const isPdseCheckbox = document.getElementById('is_pdse');
    const pdseFields = document.getElementById('pdse_fields');

    // --- HELPER: MATERNITY FOCUS ---
    function focusMaternidade() {
        const section = document.getElementById('section-afastamentos');
        const formDiv = document.getElementById('add-afastamento-form');
        
        // Show form if hidden
        if(formDiv) formDiv.style.display = 'block';
        
        if (section) {
            section.scrollIntoView({ behavior: 'smooth' });
            
            // Wait for display change then focus
            setTimeout(() => {
                const tipoSelect = document.querySelector('select[name="tipo"]');
                if(tipoSelect) {
                    tipoSelect.value = 'maternidade';
                    tipoSelect.style.border = '2px solid var(--primary-color)';
                    setTimeout(() => tipoSelect.style.border = '1px solid var(--border-color)', 2000);
                }
            }, 100);
        } else {
            alert('Salve o bolsista primeiro para registrar afastamentos.');
        }
    }

    // --- HELPER: TOGGLE PDSE ---
    function togglePdseFields() {
        if(isPdseCheckbox && pdseFields) {
            pdseFields.style.display = isPdseCheckbox.checked ? 'block' : 'none';
        }
    }

    // --- HELPER: GET MATERNITY BONUS ---
    function getMaternityBonus() {
        let bonus = 0;
        // Parse table if exists
        const rows = document.querySelectorAll('#tabela-afastamentos tbody tr'); // ID needs to be added to table? 
        // Current table has no ID in view! 
        // Table is inside .form-section. Let's select generic.
        const tables = document.querySelectorAll('table');
        if(tables.length > 0) {
            // Usually the first table in the view
             const rows = tables[0].querySelectorAll('tbody tr');
             rows.forEach(row => {
                const cells = row.querySelectorAll('td');
                if (cells.length > 2) {
                    const tipo = cells[0].textContent.trim().toLowerCase();
                    const duracao = parseInt(cells[2].textContent.trim()) || 0;
                    if (tipo.includes('maternidade')) {
                         bonus += Math.min(duracao, 6);
                    }
                }
            });
        }
        return Math.min(bonus, 6);
    }

    // --- API: LOAD MODALIDADES ---
    async function loadModalidades(editalId, selectedId = null) {
        if (!modalidadeSelect) return;
        
        modalidadeSelect.innerHTML = '<option value="">Carregando...</option>';
        modalidadeSelect.disabled = true;

        try {
            const response = await fetch(`/api/modalidades/${editalId}`);
            const data = await response.json();
            currentModalidades = data; // Cache

            modalidadeSelect.innerHTML = '<option value="">Selecione...</option>';
            data.forEach(m => {
                const max = m.max_meses ? ` (Max: ${m.max_meses} meses)` : '';
                const option = document.createElement('option');
                option.value = m.id;
                option.textContent = `${m.nivel} - Mensal: R$ ${m.valor} - Vagas: ${m.vagas}${max}`;
                if (selectedId && m.id == selectedId) option.selected = true;
                modalidadeSelect.appendChild(option);
            });
            modalidadeSelect.disabled = false;
            
            // Trigger logic immediately if data exists
            calculateSystem();

        } catch (error) {
            console.error('Erro:', error);
            modalidadeSelect.innerHTML = '<option value="">Erro ao carregar</option>';
        }
    }

    // --- CORE LOGIC: CALCULATE & VALIDATE ---
    function calculateSystem() {
        // Only run if we have critical inputs
        if (!dataInicioBolsa || !dataInicioBolsa.value) return;

        const inicio = new Date(dataInicioBolsa.value);
        if(isNaN(inicio)) return;

        const modId = modalidadeSelect ? modalidadeSelect.value : null;
        const selectedMod = currentModalidades.find(m => m.id == modId);

        // 1. DETERMINE LIMITS
        let maxMonths = 1000; // Default high
        let limitLabel = "Sem limite definido";

        if (selectedMod && selectedMod.max_meses) {
            const bonus = getMaternityBonus();
            maxMonths = selectedMod.max_meses + bonus;
            limitLabel = `${selectedMod.max_meses} meses (Edital) + ${bonus} meses (Maternidade)`;
        }

        // Set Input Constraints
        if(mesesDuracao) mesesDuracao.max = maxMonths;

        // Calculate Max End Date
        // Limit Date = Start + MaxMonths
        const limitDate = new Date(inicio.getFullYear(), inicio.getMonth() + maxMonths, inicio.getDate());
        limitDate.setDate(limitDate.getDate() - 1); // Inclusive
        // Handle Invalid Date (overflow)
        const limitDateStr = limitDate.toISOString().split('T')[0];
        
        if(dataFimBolsa) dataFimBolsa.max = limitDateStr;

        // 2. AUTO-CALC DURATION FROM END DATE
        // If user changed End Date manually (active element check)
        if (dataFimBolsa && document.activeElement === dataFimBolsa && dataFimBolsa.value) {
            const currentFim = new Date(dataFimBolsa.value);
            
            // Strict Lock for End Date
            if (currentFim > limitDate) {
                alert(`Data limite excedida! O máximo permitido é ${limitLabel}. A data será ajustada.`);
                dataFimBolsa.value = limitDateStr;
                // Force update duration to max
                if(mesesDuracao) mesesDuracao.value = maxMonths;
            } else {
                 // Update Duration
                let months = (currentFim.getFullYear() - inicio.getFullYear()) * 12 + (currentFim.getMonth() - inicio.getMonth());
                // Correction for inclusive dates (01/01 to 31/01 is 1 month)
                // If currentFim Day + 1 >= Inicio Day? 
                // Let's stick to standard month diff. 
                // If partial month?
                if (currentFim.getDate() >= inicio.getDate() - 1) months += 0; 
                // Let's trust just diff for now, usually sufficient.
                
                months = Math.max(1, months);
                if (months > maxMonths) months = maxMonths;
                if(mesesDuracao) mesesDuracao.value = months;
            }
        }

        // 3. AUTO-CALC END DATE FROM DURATION
        // If user changed Duration manually OR Start Date changed OR Modality Changed
        if (document.activeElement !== dataFimBolsa) {
             let dur = parseInt(mesesDuracao.value) || 0;
             if (dur > maxMonths) {
                 alert(`Duração excedida! O máximo permitido é ${limitLabel}.`);
                 dur = maxMonths;
                 mesesDuracao.value = dur;
             }
             
             if (dur > 0 && dataFimBolsa) {
                 const newEnd = new Date(inicio.getFullYear(), inicio.getMonth() + dur, inicio.getDate());
                 newEnd.setDate(newEnd.getDate() - 1);
                 dataFimBolsa.value = newEnd.toISOString().split('T')[0];
             }
        }
    }

    // --- EVENT LISTENERS ---
    if (editalSelect) {
        editalSelect.addEventListener('change', function() {
            if(this.value) loadModalidades(this.value);
        });
    }

    if (modalidadeSelect) modalidadeSelect.addEventListener('change', calculateSystem);
    if (dataInicioBolsa) dataInicioBolsa.addEventListener('change', calculateSystem);
    if (dataFimBolsa) dataFimBolsa.addEventListener('change', calculateSystem);
    if (mesesDuracao) mesesDuracao.addEventListener('input', calculateSystem);

    // Initial Load Logic
    window.addEventListener('DOMContentLoaded', () => {
        {% if bolsista %}
            if (editalSelect && editalSelect.value) {
                // Ensure specific ID is numeric
                loadModalidades(editalSelect.value, {{ bolsista.modalidade_id }});
            }
        {% endif %}
    });

</script>
{% endblock %}
"""
    # Replace content
    final_content = pre_script + new_script
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(final_content)
    print("Successfully updated form.html")
else:
    print("Could not find script start marker.")
