
# --- Fase 5: Rotas Administrativas ---

@app.route('/admin/programas')
def admin_programas_lista():
    """Lista todos os programas acadêmicos para edição."""
    from models import ProgramaAcademico
    programas = ProgramaAcademico.query.order_by(ProgramaAcademico.nome_programa).all()
    return render_template('admin/programas.html', programas=programas)

@app.route('/admin/programas/editar/<int:id>', methods=['GET', 'POST'])
def admin_programas_editar(id):
    """Edita um programa acadêmico específico."""
    from models import ProgramaAcademico
    programa = ProgramaAcademico.query.get_or_404(id)
    
    if request.method == 'POST':
        try:
            programa.nome_programa = request.form['nome_programa']
            programa.sigla_programa = request.form['sigla_programa']
            programa.codigo_programa = request.form['codigo_programa']
            programa.niveis = request.form['niveis']
            programa.nota_capes = request.form['nota_capes']
            
            db.session.commit()
            flash('Programa atualizado com sucesso!', 'success')
            return redirect(url_for('admin_programas_lista'))
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao atualizar: {str(e)}', 'error')
            
    return render_template('admin/programas_editar.html', programa=programa)
