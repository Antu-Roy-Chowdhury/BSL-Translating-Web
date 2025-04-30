document.addEventListener("DOMContentLoaded", () => {
  const signCards = document.querySelectorAll(".sign-card")
  const modal = document.getElementById("sign-modal")
  const modalImage = document.getElementById("modal-sign-image")
  const modalTitle = document.getElementById("modal-sign-title")
  const modalLabel = document.getElementById("modal-sign-label")
  const modalDescription = document.getElementById("modal-sign-description")
  const modalSpeakBtn = document.getElementById("modal-speak-btn")
  const closeBtn = document.querySelector(".close")

  // Sign card click event
  signCards.forEach((card) => {
    card.addEventListener("click", function () {
      const label = this.getAttribute("data-label")
      const bangla = this.querySelector("h3").textContent
      const image = this.querySelector("img").src

      modalImage.src = image
      modalImage.alt = bangla
      modalTitle.textContent = bangla
      modalLabel.textContent = label
      modalDescription.textContent = `This is the sign for "${bangla}" (${label}) in Bangla Sign Language.`

      modal.style.display = "block"
    })
  })

  // Close modal
  closeBtn.addEventListener("click", () => {
    modal.style.display = "none"
  })

  // Close modal when clicking outside
  window.addEventListener("click", (event) => {
    if (event.target === modal) {
      modal.style.display = "none"
    }
  })

  // Speak button in modal
  modalSpeakBtn.addEventListener("click", () => {
    const text = modalTitle.textContent
    if (text) {
      speakText(text)
    }
  })

  // Function to speak text using the Web Speech API
  function speakText(text) {
    // Check if speech synthesis is supported
    if ("speechSynthesis" in window) {
      const utterance = new SpeechSynthesisUtterance(text)

      // Try to find a Bangla voice
      const voices = window.speechSynthesis.getVoices()
      const banglaVoice = voices.find((voice) => voice.lang === "bn-BD")

      if (banglaVoice) {
        utterance.voice = banglaVoice
      }

      utterance.lang = "bn-BD"
      utterance.rate = 0.9

      window.speechSynthesis.speak(utterance)
    } else {
      alert("Sorry, your browser does not support text-to-speech!")
    }
  }
})
