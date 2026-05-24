/**
 * Arandú Napi-Robótica - Visual UI Editor (V11.1)
 * Padrão Memento com Snapshots JSONB
 */

(function() {
    let isEditorMode = false;
    let originalTexts = {};

    // ── Estilos do Editor ──────────────────────────────────────────────
    const style = document.createElement('style');
    style.innerHTML = `
        .ui-editor-active [data-ui-key] {
            outline: 2px dashed #f59e0b !important;
            outline-offset: 2px;
            cursor: text !important;
            background-color: rgba(245, 158, 11, 0.1) !important;
        }
        .ui-editor-active [data-ui-key]:hover {
            background-color: rgba(245, 158, 11, 0.2) !important;
        }
        .ui-editor-panel {
            position: fixed;
            bottom: 20px;
            right: 20px;
            background: #ffffff;
            border-radius: 8px;
            box-shadow: 0 10px 25px rgba(0,0,0,0.2);
            padding: 15px;
            z-index: 10000;
            display: flex;
            flex-direction: column;
            gap: 10px;
            width: 250px;
            border: 1px solid #e5e7eb;
            transition: transform 0.3s ease;
        }
        .ui-editor-panel h4 { margin: 0; font-size: 0.9rem; color: #1f2937; }
        .ui-editor-panel .btn-group { display: flex; gap: 8px; }
        .ui-editor-panel button {
            padding: 8px 12px;
            border-radius: 4px;
            font-size: 0.85rem;
            font-weight: 600;
            cursor: pointer;
            border: none;
            flex: 1;
        }
        .btn-ui-save { background: #10b981; color: white; }
        .btn-ui-save:disabled { background: #6ee7b7; cursor: not-allowed; }
        .btn-ui-cancel { background: #ef4444; color: white; }
        
        .ui-toggle-btn {
            background: #f59e0b;
            color: white;
            padding: 5px 10px;
            border-radius: 4px;
            font-size: 0.75rem;
            font-weight: bold;
            border: none;
            cursor: pointer;
            margin-right: 10px;
        }
        
        .ui-editor-panel .spinner {
            width: 16px;
            height: 16px;
            border: 2px solid rgba(255,255,255,0.3);
            border-top-color: #fff;
            border-radius: 50%;
            animation: spin 0.8s linear infinite;
            display: inline-block;
            margin-right: 5px;
        }
    `;
    document.head.appendChild(style);

    // ── Inicialização ──────────────────────────────────────────────────
    document.addEventListener('DOMContentLoaded', () => {
        const topbar = document.querySelector('.user-info');
        if (!topbar) return;

        const toggleBtn = document.createElement('button');
        toggleBtn.className = 'ui-toggle-btn';
        toggleBtn.innerText = '📝 Editar UI';
        toggleBtn.onclick = toggleEditorMode;
        topbar.prepend(toggleBtn);
    });

    function toggleEditorMode() {
        isEditorMode = !isEditorMode;
        const root = document.body;
        const elements = document.querySelectorAll('[data-ui-key]');

        if (isEditorMode) {
            root.classList.add('ui-editor-active');
            elements.forEach(el => {
                const key = el.getAttribute('data-ui-key');
                originalTexts[key] = el.innerHTML;
                el.contentEditable = "true";
                // Previne navegação se o elemento for um link
                el.addEventListener('click', preventLinkClick);
            });
            showPanel();
        } else {
            root.classList.remove('ui-editor-active');
            elements.forEach(el => {
                el.contentEditable = "false";
                el.removeEventListener('click', preventLinkClick);
            });
            hidePanel();
        }
    }

    function preventLinkClick(e) {
        if (isEditorMode) {
            e.preventDefault();
            e.stopPropagation();
        }
    }

    // ── Painel de Controle ─────────────────────────────────────────────
    function showPanel() {
        let panel = document.getElementById('ui-editor-panel');
        if (!panel) {
            panel = document.createElement('div');
            panel.id = 'ui-editor-panel';
            panel.className = 'ui-editor-panel';
            panel.innerHTML = `
                <h4>🛠️ Modo Editor Ativo</h4>
                <p style="font-size: 0.75rem; color: #6b7280; margin: 0;">Clique em qualquer item com borda amarela para editar o texto.</p>
                <div class="btn-group">
                    <button class="btn-ui-save" onclick="window.saveUIChanges()">Gravar</button>
                    <button class="btn-ui-cancel" onclick="window.discardUIChanges()">Descartar</button>
                </div>
            `;
            document.body.appendChild(panel);
        } else {
            panel.style.display = 'flex';
        }
    }

    function hidePanel() {
        const panel = document.getElementById('ui-editor-panel');
        if (panel) panel.style.display = 'none';
    }

    // ── Ações Globais (Expostas para os botões do painel) ──────────────
    window.saveUIChanges = async function() {
        const saveBtn = document.querySelector('.btn-ui-save');
        const changes = {};
        const elements = document.querySelectorAll('[data-ui-key]');
        
        elements.forEach(el => {
            const key = el.getAttribute('data-ui-key');
            const currentText = el.innerHTML;
            if (currentText !== originalTexts[key]) {
                changes[key] = currentText;
            }
        });

        if (Object.keys(changes).length === 0) {
            alert("Nenhuma alteração detectada.");
            toggleEditorMode();
            return;
        }

        saveBtn.disabled = true;
        saveBtn.innerHTML = '<span class="spinner"></span> Salvando...';

        try {
            const response = await fetch('/admin/ui/save', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCsrfToken()
                },
                body: JSON.stringify({ changes })
            });

            const result = await response.json();
            if (result.success) {
                // Sucesso: Recarrega para aplicar o contexto global do Flask
                window.location.reload();
            } else {
                alert("Erro ao salvar: " + result.message);
                saveBtn.disabled = false;
                saveBtn.innerHTML = 'Gravar';
            }
        } catch (err) {
            console.error(err);
            alert("Erro crítico na comunicação com o servidor.");
            saveBtn.disabled = false;
            saveBtn.innerHTML = 'Gravar';
        }
    };

    window.discardUIChanges = function() {
        if (confirm("Descartar todas as alterações não salvas?")) {
            const elements = document.querySelectorAll('[data-ui-key]');
            elements.forEach(el => {
                const key = el.getAttribute('data-ui-key');
                if (originalTexts[key]) {
                    el.innerHTML = originalTexts[key];
                }
            });
            toggleEditorMode();
        }
    };

    function getCsrfToken() {
        const input = document.querySelector('input[name="csrf_token"]');
        return input ? input.value : "";
    }

})();
