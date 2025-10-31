function togglePassword() {
    const input = document.getElementById("id_contraseña"); // Django genera id_contraseña
    const icon = document.querySelector(".toggle-password");

    if (input.type === "password") {
      input.type = "text";
      icon.classList.remove("fa-eye");
      icon.classList.add("fa-eye-slash");
    } else {
      input.type = "password";
      icon.classList.remove("fa-eye-slash");
      icon.classList.add("fa-eye");
    }
  }

function togglePassword(id) {
        const input = document.getElementById(id);
        input.type = input.type === "password" ? "text" : "password";
      }

      const passwordInput = document.getElementById("id_contraseña");
      const errorMsg = document.getElementById("passwordHelp");
      const regex = /^(?=.*[A-Z]).{6,}$/;

      // Validación SOLO al enviar formulario
      function validarPassword() {
        const pass = passwordInput.value;
        if (!regex.test(pass)) {
          errorMsg.classList.add("show-error");
          setTimeout(() => {
            errorMsg.classList.remove("show-error");
          }, 5500); // se oculta después de la animación
          return false; // evita enviar el form
        }
        return true;
      }
