// carousel function
const carousel = document.querySelector('.carousel');
      const slides = carousel.querySelector('.slides');
      const images = slides.querySelectorAll('img');
      let currentIndex = 0;

      function showSlide(index) {
          slides.style.transform = `translateX(-${index * 100}%)`;
      }

      function nextSlide() {
          currentIndex = (currentIndex + 1) % images.length;
          showSlide(currentIndex);
      }

      setInterval(nextSlide, 3000); // Auto-advance every 3 seconds