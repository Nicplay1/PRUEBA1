// HAMBUERGER //
const hamburger = document.getElementById('hamburger');
        const navMenu = document.getElementById('nav-menu');

        hamburger.addEventListener('click', () => {
            hamburger.classList.toggle('active');
            navMenu.classList.toggle('active');
        });

        // Cerrar menú al hacer click en un enlace (móvil)
        document.querySelectorAll('.nav-link').forEach(link => {
            link.addEventListener('click', () => {
                if (window.innerWidth <= 768) {
                    hamburger.classList.remove('active');
                    navMenu.classList.remove('active');
                }
            });
        });

        // Cerrar menú al cambiar tamaño de ventana
        window.addEventListener('resize', () => {
            if (window.innerWidth > 768) {
                hamburger.classList.remove('active');
                navMenu.classList.remove('active');
            }
        });

        // Efecto de scroll suave
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', function (e) {
                e.preventDefault();
                const target = document.querySelector(this.getAttribute('href'));
                if (target) {
                    target.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            });
        });

// INCREMENTO DE NUMEROS //
function animateCounter(counter) {
    const target = +counter.getAttribute("data-target");
    const increment = target / 200; // velocidad
    let current = 0;

    const updateCounter = () => {
      current += increment;
      if (current < target) {
        counter.textContent = Math.floor(current);
        requestAnimationFrame(updateCounter);
      } else {
        counter.textContent = target;
      }
    };

    updateCounter();
  }

  // IntersectionObserver para activar animación al hacer scroll
  function animateCounter(counter) {
    const target = +counter.getAttribute("data-target");
    const increment = target / 200; // velocidad
    let current = 0;

    const updateCounter = () => {
      current += increment;
      if (current < target) {
        counter.textContent = Math.floor(current);
        requestAnimationFrame(updateCounter);
      } else {
        counter.textContent = target;
      }
    };

    updateCounter();
  }

  // 🚀 Animar todos los números al cargar la página
  window.addEventListener("DOMContentLoaded", () => {
    const counters = document.querySelectorAll(".numero");
    counters.forEach(counter => {
      counter.classList.add("visible"); // fade in
      animateCounter(counter);
    });
  });

// Datos de testimonios
        const testimonials = [
            {
                text: "La plataforma nos llevó a otro nivel, porque nos permitió adaptarnos a todos los tiempos digitales, así afirmamos asistencia a nuestros lugares.",
                author: "Ana García",
                stars: 5
            },
            {
                text: "Esta aplicación nos ayudó mucho para informarnos del manejo del dinero, además de que con su red social nos comunicamos más rápido y ahorramos tiempo.",
                author: "Carlos Rodríguez",
                stars: 5
            },
            {
                text: "Esta aplicación nos ayudó a comunicarnos más fácilmente con los residentes, manteníamos más ordenados en los registros de los ingresos y egresos, además de que los vecinos han podido promocionar sus servicios dentro de la misma privada.",
                author: "María López",
                stars: 5
            },
            {
                text: "La plataforma nos ayudó mucho para facilitar nuestros archivos del dinero, además de que con su red social nos comunicamos más rápido y ahorramos tiempo.",
                author: "José Martínez",
                stars: 5
            },
            {
                text: "Esta aplicación nos ayudó a comunicarnos más fácilmente con los residentes y mantener todo organizado.",
                author: "Laura Hernández",
                stars: 4
            },
            {
                text: "Una herramienta fundamental para la gestión de nuestra comunidad. Altamente recomendada.",
                author: "Pedro Sánchez",
                stars: 5
            }
        ];

        let currentIndex = 0;
        const testimonialsContainer = document.getElementById('testimonialsContainer');
        const dotsContainer = document.getElementById('dotsContainer');
        const prevBtn = document.getElementById('prevBtn');
        const nextBtn = document.getElementById('nextBtn');

        // Generar testimonios
        function generateTestimonials() {
            testimonialsContainer.innerHTML = '';
            
            testimonials.forEach((testimonial, index) => {
                const card = document.createElement('div');
                card.className = 'testimonial-card';
                card.innerHTML = `
                    <div class="stars">
                        ${'★'.repeat(testimonial.stars)}${'☆'.repeat(5 - testimonial.stars)}
                    </div>
                    <div class="testimonial-text">"${testimonial.text}"</div>
                    <div class="testimonial-author">- ${testimonial.author}</div>
                `;
                
                card.addEventListener('click', () => goToSlide(index));
                testimonialsContainer.appendChild(card);
            });
        }

        // Generar dots
        function generateDots() {
            dotsContainer.innerHTML = '';
            
            testimonials.forEach((_, index) => {
                const dot = document.createElement('div');
                dot.className = 'dot';
                dot.addEventListener('click', () => goToSlide(index));
                dotsContainer.appendChild(dot);
            });
        }

        // Posicionar testimonios
        function positionTestimonials() {
            const cards = document.querySelectorAll('.testimonial-card');
            const dots = document.querySelectorAll('.dot');
            
            cards.forEach((card, index) => {
                card.classList.remove('active', 'left', 'center-left', 'center', 'center-right', 'right', 'hidden');
                
                const position = (index - currentIndex + testimonials.length) % testimonials.length;
                
                switch(position) {
                    case 0:
                        card.classList.add('center', 'active');
                        break;
                    case 1:
                        card.classList.add('center-right');
                        break;
                    case 2:
                        card.classList.add('right');
                        break;
                    case testimonials.length - 1:
                        card.classList.add('center-left');
                        break;
                    case testimonials.length - 2:
                        card.classList.add('left');
                        break;
                    default:
                        card.classList.add('hidden');
                }
            });
            
            // Actualizar dots
            dots.forEach((dot, index) => {
                dot.classList.toggle('active', index === currentIndex);
            });
        }

        // Ir a slide específico
        function goToSlide(index) {
            currentIndex = index;
            positionTestimonials();
        }

        // Siguiente slide
        function nextSlide() {
            currentIndex = (currentIndex + 1) % testimonials.length;
            positionTestimonials();
        }

        // Slide anterior
        function prevSlide() {
            currentIndex = (currentIndex - 1 + testimonials.length) % testimonials.length;
            positionTestimonials();
        }

        // Auto-play
        let autoPlayInterval;
        
        function startAutoPlay() {
            autoPlayInterval = setInterval(nextSlide, 5000);
        }
        
        function stopAutoPlay() {
            clearInterval(autoPlayInterval);
        }

        // Event listeners
        prevBtn.addEventListener('click', () => {
            prevSlide();
            stopAutoPlay();
            setTimeout(startAutoPlay, 10000);
        });

        nextBtn.addEventListener('click', () => {
            nextSlide();
            stopAutoPlay();
            setTimeout(startAutoPlay, 10000);
        });

        // Pausar auto-play al hacer hover
        testimonialsContainer.addEventListener('mouseenter', stopAutoPlay);
        testimonialsContainer.addEventListener('mouseleave', startAutoPlay);

        // Soporte para swipe en móviles
        let startX = 0;
        let endX = 0;

        testimonialsContainer.addEventListener('touchstart', (e) => {
            startX = e.touches[0].clientX;
        });

        testimonialsContainer.addEventListener('touchend', (e) => {
            endX = e.changedTouches[0].clientX;
            handleSwipe();
        });

        function handleSwipe() {
            const threshold = 50;
            const diff = startX - endX;
            
            if (Math.abs(diff) > threshold) {
                if (diff > 0) {
                    nextSlide();
                } else {
                    prevSlide();
                }
                stopAutoPlay();
                setTimeout(startAutoPlay, 10000);
            }
        }

        // Soporte para teclado
        document.addEventListener('keydown', (e) => {
            if (e.key === 'ArrowLeft') {
                prevSlide();
                stopAutoPlay();
                setTimeout(startAutoPlay, 10000);
            } else if (e.key === 'ArrowRight') {
                nextSlide();
                stopAutoPlay();
                setTimeout(startAutoPlay, 10000);
            }
        });

        // Inicializar
        document.addEventListener('DOMContentLoaded', () => {
            generateTestimonials();
            generateDots();
            positionTestimonials();
            startAutoPlay();
        });
