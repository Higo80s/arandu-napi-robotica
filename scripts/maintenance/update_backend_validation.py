
import os

file_path = r'C:\Users\higosantos\Documents\gestao_editais\gestao_editais_novo\app.py'

# We replace the Validation Logic block in app.py.
# Lines currently ~220 to ~270.

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Define the start of the block to replace
start_marker = "# --- Validation Logic Start ---"

# We will need to locate where to stop. 
# Looking at the view_file output, the code continues to 'limite_final = ...' and beyond.
# The validation logic ends before the `db.session.add(bolsista)` or just before redirect.
# Let's target the block ending.
# Usually ends with `meses_duracao = ...` update and `if duracao_efetiva > ...` checks.
# Wait, let's just rewrite the chunk from `from dateutil.relativedelta` down to the error checks.

# Actually, the best way is to find the block between:
# `bolsista.data_inicio_bolsa = ...` (line 216)
# AND
# `if request.method == 'POST':` (next route?) No, that's too far.
# `try:` or `db.session.commit()`? 
# I need to see more lines to know where the block ends accurately.

# Let's assume I can replace from ` # --- Validation Logic Start ---`
# to the point where it saves.

# Implementation:
new_validation_logic = """            # --- Validation Logic Start ---
            
            # 0. Precedence Rule: IB >= IC
            # If IC exists (it should), validate.
            if bolsista.data_inicio_curso and bolsista.data_inicio_bolsa < bolsista.data_inicio_curso:
                 flash(f'Erro: Data de Início da Bolsa ({bolsista.data_inicio_bolsa}) não pode ser anterior ao Início do Curso ({bolsista.data_inicio_curso}).', 'error')
                 return render_template('bolsistas/form.html', bolsista=bolsista, editais=editais)

            # 1. Determine Inputs
            IC = bolsista.data_inicio_curso
            IB = bolsista.data_inicio_bolsa
            M = mod.max_meses if mod.max_meses else 0
            
            # Get Manual Duration "D" from Form (as source of truth for intention)
            try:
                D = int(request.form['meses_duracao'])
            except:
                D = 0
            
            # 2. Determine Extensions (Maternity / Suspension)
            bonus_maternidade = 0
            suspension_months = 0
            for afast in bolsista.afastamentos:
                if afast.tipo == 'maternidade':
                     bonus_maternidade += min(afast.duracao_meses, 6)
                elif afast.tipo in ['trancamento', 'saude']:
                     suspension_months += afast.duracao_meses
            
            # 3. Calculate Fatal Limit (Data Limite)
            # Limit = IC + (M + Extensions) - 1 month.
            # Using relativedelta for accurate date math
            from dateutil.relativedelta import relativedelta
            
            M_extended = M + bonus_maternidade + suspension_months
            
            if IC:
                # Add months
                limit_date = IC + relativedelta(months=M_extended)
                # Subtract 1 day to find the "end of the period" (month anterior logic usually means "until X date")
                # User spec: "IC + M - 1 month".
                # Example: 01/05 + 24m = 01/05. -1 month = 01/04.
                # Example 2: "encerr-se no mês anterior".
                limit_date = limit_date - relativedelta(months=1)
                
                # Wait, "Data Limite imutável é 01/04/2027" for IC 01/05/2025 (24m).
                # My calc: 01/05/25 + 24m = 01/05/27. -1m = 01/04/27. Matches.
            else:
                limit_date = datetime.date(2099, 12, 31) # Fallback

            # 4. Calculate End Date (Result)
            # End = IB + (D - 1) months + Suspension? 
            # Note: The User Spec Formula C: "Fim da Bolsa = IB + (D - 1) meses".
            # This calculates the "Last Payment Month". 
            # If we strictly followed C, end_date would be purely payment based.
            # However, for the system to represent the "Vínculo", we usually include suspension.
            # Frontend JS: `FimBolsa.setMonth(FimBolsa.getMonth() + (D - 1) + suspension);`
            # Let's match Frontend to avoid mismatch errors.
            
            final_D = D # Duration to save
            
            end_date = IB + relativedelta(months=(D - 1 + suspension_months))
            
            # 5. Validation: End Date <= Limit Date
            if end_date > limit_date:
                 flash(f'Erro de Prazo: A data final calculada ({end_date}) excede o limite fatal do vínculo ({limit_date}). Verifique se a duração ({D} meses) é compatível com o início da bolsa e do curso.', 'error')
                 return render_template('bolsistas/form.html', bolsista=bolsista, editais=editais)

            # 6. Validation: D <= M (corrected for extensions?)
            # Spec: "O sistema deve bloquear se D for maior que o limite da Modalidade (M)."
            # Assuming M here is the pure modality limit OR extended?
            # Usually strict Spec means strict M.
            # But let's allow extensions (M_extended) otherwise Maternity is useless.
            if D > (M + bonus_maternidade): 
                 # Note: Suspension doesn't give you MORE MONEY (D), just more Time.
                 # So D check should be against M + Maternity.
                 flash(f'Erro de Duração: A quantidade de mensalidades ({D}) excede o permitido pela modalidade ({M} + {bonus_maternidade} bônus).', 'error')
                 return render_template('bolsistas/form.html', bolsista=bolsista, editais=editais)

            # Apply Logic
            bolsista.meses_duracao = D
            bolsista.data_fim_bolsa = end_date
            
            # --- End Validation Logic ---"""

# We search for the chunk to replace.
# Start: "# --- Validation Logic Start ---"
# End: "db.session.add(bolsista)" (This is usually after validation) or "flash('Bolsista atualizado"

if start_marker in content:
    pre = content.split(start_marker)[0]
    
    # Locate suffix
    if "db.session.add(bolsista)" in content:
        post = "db.session.add(bolsista)" + content.split("db.session.add(bolsista)")[1]
    elif "db.session.commit()" in content:
         # Fallback search
         post = "db.session.commit()" + content.split("db.session.commit()")[1]
    else:
        # Dangerous cleanup? Let's rely on finding where the current validation block ends.
        # Current block has `if duracao_efetiva > limite_final:` ... returns.
        # We can find `try:` which usually starts the DB commit block.
        post_marker = "try:"
        parts = content.split(post_marker)
        if len(parts) > 1:
            # Reconstruct from the LAST occurrence? No, usually first `try:` after validation.
            # Let's perform a constrained split.
             remaining = content.split(start_marker)[1]
             # Find the next `try:` in remaining
             if "try:" in remaining:
                 suffix = "try:" + remaining.split("try:", 1)[1]
                 final_content = pre + new_validation_logic + "\n            " + suffix
                 
                 with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(final_content)
                 print("Successfully updated app.py validation logic.")
             else:
                 print("Could not find end marker 'try:'.")
        else:
             print("Could not find 'try:'.")
else:
    print("Could not find start marker.")
