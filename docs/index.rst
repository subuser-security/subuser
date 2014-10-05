
Subuser - Securing the linux desktop with Docker
================================================

.. raw :: html

  <div id="marketingClaim"> <h1> Welcome to Subuser! </h1> </div>
  <div id="slide1"><h1>Docker on the Desktop</h1></div>
  <dif id="slide2"><h1>Bedrock linux meets Android permissions lists</h1></div>
  <div id="slide3"><h1>QubesOS light</h1></div>
  <div id="slide4"><h1>A package manager with an undo function</h1></div>
 
  <script>
  slides = ["slide1"
           ,"slide2"
           ,"slide3"
           ,"slide4"]
  for(slide=0;slide<slides.length;slide++){
      currentSlideElement = document.getElementById(slides[slide])
      currentSlideElement.style.display = "none"
  }
  slide=0
  var interval = setInterval(function() {
      currentSlideElement = document.getElementById(slides[slide++])
      document.getElementById('marketingClaim').innerHTML = currentSlideElement.innerHTML;
      if(slide == slides.length) {
        slide = 0
      }
  
  }, 2000);
  </script>


.. toctree::

  what-is-subuser
  security
  installation
  tutorial-use
  commands/index
  packaging
  flaws
  related-projects
