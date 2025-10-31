setTimeout(() => {
            document.querySelectorAll('.alert-modern').forEach(el => {
                el.style.opacity = '0';
                el.style.transform = 'translate(-50%, -20px)';
                setTimeout(() => el.remove(), 300);
            });
        }, 5000);

// Validación de fortaleza de contraseña
        const nuevaPassword = document.getElementById('nuevaPassword');
        const confirmPassword = document.getElementById('confirmPassword');
        const passwordStrength = document.getElementById('passwordStrength');
        const passwordMatch = document.getElementById('passwordMatch');

        nuevaPassword.addEventListener('input', function() {
            const password = this.value;
            let strength = '';
            let color = '';

            if (password.length === 0) {
                strength = '';
            } else if (password.length < 6) {
                strength = 'Débil - Mínimo 6 caracteres';
                color = 'strength-weak';
            } else if (password.length < 8) {
                strength = 'Media - Recomendado 8+ caracteres';
                color = 'strength-medium';
            } else {
                // Verificar si tiene números y caracteres especiales
                const hasNumbers = /\d/.test(password);
                const hasSpecial = /[!@#$%^&*(),.?":{}|<>]/.test(password);
                
                if (hasNumbers && hasSpecial) {
                    strength = 'Fuerte - Excelente contraseña';
                    color = 'strength-strong';
                } else if (hasNumbers || hasSpecial) {
                    strength = 'Media - Agrega más variedad de caracteres';
                    color = 'strength-medium';
                } else {
                    strength = 'Débil - Agrega números y símbolos';
                    color = 'strength-weak';
                }
            }

            passwordStrength.innerHTML = strength ? `<span class="${color}">${strength}</span>` : '';
        });

        // Validación de coincidencia de contraseñas
        confirmPassword.addEventListener('input', function() {
            if (nuevaPassword.value && this.value) {
                if (nuevaPassword.value === this.value) {
                    passwordMatch.innerHTML = '<span class="strength-strong">✓ Las contraseñas coinciden</span>';
                } else {
                    passwordMatch.innerHTML = '<span class="strength-weak">✗ Las contraseñas no coinciden</span>';
                }
            } else {
                passwordMatch.innerHTML = '';
            }
        });

        // Validación del formulario
        document.getElementById('passwordForm').addEventListener('submit', function(e) {
            if (nuevaPassword.value !== confirmPassword.value) {
                e.preventDefault();
                passwordMatch.innerHTML = '<span class="strength-weak">✗ Las contraseñas deben coincidir</span>';
                confirmPassword.focus();
            }
        });