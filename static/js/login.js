/**
 * LOGIN PAGE - INTERACTIVITY
 * ===========================
 */

// Toggle password visibility
function togglePassword() {
    const passwordInput = document.getElementById('password');
    const toggleBtn = document.querySelector('.toggle-password');

    if (passwordInput.type === 'password') {
        passwordInput.type = 'text';
        toggleBtn.querySelector('i').setAttribute('data-lucide', 'eye-off');
    } else {
        passwordInput.type = 'password';
        toggleBtn.querySelector('i').setAttribute('data-lucide', 'eye');
    }

    // Re-initialize Lucide icons
    lucide.createIcons();
}

// Show help modal
function showHelp(type) {
    const modal = document.getElementById('helpModal');
    const content = document.getElementById('helpContent');

    const helpContent = {
        password: `
            <h2 style="margin-bottom: 1rem; color: #1f2937;">Esqueci minha senha</h2>
            <p style="color: #6b7280; margin-bottom: 1rem;">
                Para redefinir sua senha, entre em contato com:
            </p>
            <ul style="color: #6b7280; margin-left: 1.5rem; line-height: 1.8;">
                <li>📧 Email: <strong>proppg@utfpr.edu.br</strong></li>
                <li>📞 Telefone: <strong>(41) 3310-4545</strong></li>
            </ul>
        `,
        access: `
            <h2 style="margin-bottom: 1rem; color: #1f2937;">Problemas de acesso</h2>
            <p style="color: #6b7280; margin-bottom: 1rem;">
                Verifique:
            </p>
            <ul style="color: #6b7280; margin-left: 1.5rem; line-height: 1.8;">
                <li>✓ Usuário e senha estão corretos</li>
                <li>✓ Caps Lock está desativado</li>
                <li>✓ Você possui permissão de acesso ao sistema</li>
            </ul>
            <p style="color: #6b7280; margin-top: 1rem;">
                Se o problema persistir, contate o suporte técnico.
            </p>
        `,
        bug: `
            <h2 style="margin-bottom: 1rem; color: #1f2937;">Reportar problema</h2>
            <p style="color: #6b7280; margin-bottom: 1rem;">
                Encontrou um bug ou erro no sistema?
            </p>
            <p style="color: #6b7280; margin-bottom: 1rem;">
                Envie um email para <strong>proppg@utfpr.edu.br</strong> com:
            </p>
            <ul style="color: #6b7280; margin-left: 1.5rem; line-height: 1.8;">
                <li>📝 Descrição do problema</li>
                <li>📸 Print da tela (se possível)</li>
                <li>🕒 Horário que ocorreu</li>
                <li>💻 Navegador utilizado</li>
            </ul>
        `
    };

    content.innerHTML = helpContent[type] || '';
    modal.style.display = 'flex';
}

// Close help modal
function closeHelp() {
    const modal = document.getElementById('helpModal');
    modal.style.display = 'none';
}

// Close modal on background click
document.addEventListener('click', (e) => {
    const modal = document.getElementById('helpModal');
    if (e.target === modal) {
        closeHelp();
    }
});

// Form validation
document.getElementById('loginForm')?.addEventListener('submit', function (e) {
    const username = document.getElementById('username').value.trim();
    const password = document.getElementById('password').value;

    if (!username || !password) {
        e.preventDefault();
        alert('Por favor, preencha todos os campos');
    }
});
