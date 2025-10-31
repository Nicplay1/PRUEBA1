setTimeout(() => {
            document.querySelectorAll('.alert-modern').forEach(el => {
                el.style.opacity = '0';
                el.style.transform = 'translate(-50%, -20px)';
                setTimeout(() => el.remove(), 300);
            });
        }, 5000);