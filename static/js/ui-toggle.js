function setupToggle(toggleId, boxUtfprId, boxExternoId, campusId, programaId, instituicaoId, cidadeId) {
    const toggle = document.getElementById(toggleId);
    const boxUtfpr = document.getElementById(boxUtfprId);
    const boxExterno = document.getElementById(boxExternoId);

    if (toggle) {
        toggle.addEventListener('change', function() {
            if (this.checked) {
                if (boxUtfpr) boxUtfpr.style.display = 'none';
                if (boxExterno) boxExterno.style.display = 'block';
                const c = document.getElementById(campusId);
                const p = document.getElementById(programaId);
                if (c) c.value = '';
                if (p) p.value = '';
            } else {
                if (boxUtfpr) boxUtfpr.style.display = 'block';
                if (boxExterno) boxExterno.style.display = 'none';
                const i = document.getElementById(instituicaoId);
                const cid = document.getElementById(cidadeId);
                if (i) i.value = '';
                if (cid) cid.value = '';
            }
        });
    }
}

document.addEventListener('DOMContentLoaded', function() {
    // Novo Candidato
    setupToggle('chk-vinculo-externo', 'box-selecao-utfpr', 'box-preenchimento-externo', 'campus_id', 'programa_id', 'instituicao', 'cidade');
    
    // Editar Candidato
    setupToggle('editCandIsExterno', 'box-edit-utfpr', 'box-edit-externo', 'editCandCampusId', 'editCandProgramaId', 'editCandInstituicao', 'editCandCidade');
});
