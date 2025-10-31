       // Script para el sidebar responsive
        const toggleBtn = document.getElementById('toggleSidebar');
        const sidebar = document.getElementById('sidebar');
        const overlay = document.getElementById('sidebarOverlay');
        const mainContent = document.getElementById('mainContent');

        function toggleSidebar() {
            sidebar.classList.toggle('active');
            overlay.classList.toggle('active');
        }

        toggleBtn.addEventListener('click', toggleSidebar);
        overlay.addEventListener('click', toggleSidebar);

        // Cerrar sidebar con tecla Escape
        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape' && sidebar.classList.contains('active')) {
                toggleSidebar();
            }
        });

        // Manejo responsive automático
        function handleResize() {
            if (window.innerWidth > 1024) {
                sidebar.classList.remove('active');
                overlay.classList.remove('active');
            }
        }

        window.addEventListener('resize', handleResize);

        // Script para las alertas
        setTimeout(() => {
            document.querySelectorAll('.alert-modern').forEach(el => {
                el.classList.remove('show');
                setTimeout(() => el.remove(), 300);
            });
        }, 4000);

        // Script del Calendario
        document.addEventListener("DOMContentLoaded", function () {
            var calendarEl = document.getElementById("calendar");
            var selectedDate = null; // Guardar la fecha seleccionada

            var calendar = new FullCalendar.Calendar(calendarEl, {
                initialView: "dayGridMonth",
                locale: "es",
                height: 600,
                events: function(fetchInfo, successCallback, failureCallback) {
                    fetch("{% url 'fechas_ocupadas' zona.id_zona %}")
                    .then(response => response.json())
                    .then(data => {
                        let events = data.fechas.map(fecha => ({
                            title: "Ocupado",
                            start: fecha,
                            color: "red"
                        }));
                        successCallback(events);
                    });
                },
                dateClick: function(info) {
                    let fecha = info.dateStr;
                    document.getElementById("id_fecha_uso").value = fecha;

                    // Quitar la selección anterior
                    if (selectedDate) {
                        let prevCell = document.querySelector('[data-date="' + selectedDate + '"]');
                        if (prevCell) {
                            prevCell.classList.remove("selected-date");
                        }
                    }

                    // Guardar y marcar la nueva fecha
                    selectedDate = fecha;
                    let newCell = document.querySelector('[data-date="' + fecha + '"]');
                    if (newCell) {
                        newCell.classList.add("selected-date");
                    }
                }
            });

            calendar.render();
        });