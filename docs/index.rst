
Subuser - Securing the linux desktop with Docker
================================================

.. raw :: html

  <script>
  numSlides = 22
  slide=1
  var autoplay=true
  function moveSlidePointerNext(){
      slide++
      if(slide > numSlides) {
        slide = numSlides
      }
  }
  function moveSlidePointerPrevious(){
      slide--
      if(slide < 1) {
        slide = 1
      }
  }
  function changeSlide(moveSlidePointer){
      var presentationSVG1 = document.getElementById("presentationSVG")
      var presentationSVG  = presentationSVG1.getSVGDocument()
 
      previousSlideElement = presentationSVG.getElementById("id"+slide)
      previousSlideElement.setAttribute("visibility","hidden")
      moveSlidePointer()
      currentSlideElement = presentationSVG.getElementById("id"+slide)
      currentSlideElement.setAttribute("visibility","visible")
  }
  function previousSlide(){
    changeSlide(moveSlidePointerPrevious);
  }
  function nextSlide(){
    changeSlide(moveSlidePointerNext);
  }
  function toggleAutoplay(){
    playPauseButton = document.getElementById("playPauseButton")
    playPauseButtonText = "Play";
    autoplay = !autoplay 
    if(autoplay){
      playPauseButtonText = "Pause"
    }
    playPauseButton.innerHTML = playPauseButtonText
  }

  var interval = setInterval(function() {
    if(autoplay){
      nextSlide()
    }
  }, 3000);
  </script>


  <center><embed id="presentationSVG" src="_static/images/subuser-website.svg" width="80%"></embed></center>
  <center><button onclick="previousSlide()">&lt;--</button><button id="playPauseButton" onclick="toggleAutoplay()">Pause</button><button onclick="nextSlide()">--&gt;</button></center>


Index
-----

.. toctree::

  what-is-subuser
  security
  installation
  tutorial-use
  commands/index
  packaging
  subuser-standard/standard
  flaws
  community
  related-projects
