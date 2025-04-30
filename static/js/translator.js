document.addEventListener("DOMContentLoaded", () => {
  const startBtn = document.getElementById("start-btn")
  const stopBtn = document.getElementById("stop-btn")
  const speakBtn = document.getElementById("speak-btn")
  const predictionText = document.getElementById("prediction-text")
  const predictionDisplay = document.getElementById("prediction-display")
  const predictionHistoryList = document.getElementById("prediction-history-list")
  const signImage = document.getElementById("sign-image")
  const videoFeed = document.getElementById("video-feed")

  let isRunning = false
  let predictionInterval = null
  const predictionHistory = []

  // Add error handling for video feed
  videoFeed.onerror = () => {
    console.error("Error loading video feed")
    videoFeed.src =
      "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk+A8AAQUBAScY42YAAAAASUVORK5CYII="
    alert("Video feed error. Please check your camera connection.")
  }

  // Start camera button
  startBtn.addEventListener("click", () => {
    console.log("Starting camera...")
    fetch("/start", {
      method: "POST",
    })
      .then((response) => response.json())
      .then((data) => {
        console.log("Camera start response:", data)
        if (data.status === "success") {
          isRunning = true
          startBtn.disabled = true
          stopBtn.disabled = false
          speakBtn.disabled = false

          // Force reload the video feed
          const timestamp = new Date().getTime()
          videoFeed.src = `/video_feed?t=${timestamp}`

          // Start polling for predictions
          predictionInterval = setInterval(getPrediction, 500)
        } else {
          alert("Error: " + data.message)
        }
      })
      .catch((error) => {
        console.error("Error:", error)
        alert("Failed to start camera. Please check browser console for details.")
      })
  })

  // Stop camera button
  stopBtn.addEventListener("click", () => {
    fetch("/stop", {
      method: "POST",
    })
      .then((response) => response.json())
      .then((data) => {
        if (data.status === "success") {
          isRunning = false
          startBtn.disabled = false
          stopBtn.disabled = true
          speakBtn.disabled = true

          // Stop polling for predictions
          clearInterval(predictionInterval)
          predictionText.textContent = "এখনো কোন অনুবাদ নেই"
          predictionDisplay.textContent = ""
        }
      })
      .catch((error) => {
        console.error("Error:", error)
        alert("Failed to stop camera")
      })
  })

  // Speak button
  speakBtn.addEventListener("click", () => {
    const text = predictionText.textContent
    if (text && text !== "এখনো কোন অনুবাদ নেই") {
      speakText(text)
    }
  })

  // Function to get the current prediction
  function getPrediction() {
    fetch("/get_prediction")
      .then((response) => response.json())
      .then((data) => {
        const prediction = data.prediction

        if (prediction && prediction !== "") {
          // Set font size based on whether it's Bangla or English
          if (/[\u0980-\u09FF]/.test(prediction)) {
            // Bangla Unicode range
            predictionText.style.fontSize = "2.5rem"
          } else {
            predictionText.style.fontSize = "2rem"
          }

          predictionText.textContent = prediction
          predictionDisplay.textContent = prediction

          // Update sign image if available
          if (data.sign_image && data.sign_image !== "") {
            signImage.src = data.sign_image
            signImage.alt = prediction
            console.log("Updated sign image:", data.sign_image)
          }

          // Add to history if it's different from the last prediction
          if (predictionHistory.length === 0 || predictionHistory[predictionHistory.length - 1] !== prediction) {
            predictionHistory.push(prediction)

            // Keep only the last 10 predictions
            if (predictionHistory.length > 10) {
              predictionHistory.shift()
            }

            // Update the history list
            updatePredictionHistory()
          }
        }
      })
      .catch((error) => {
        console.error("Error getting prediction:", error)
      })
  }

  // Function to update the prediction history list
  function updatePredictionHistory() {
    predictionHistoryList.innerHTML = ""

    // Display in reverse order (newest first)
    for (let i = predictionHistory.length - 1; i >= 0; i--) {
      const listItem = document.createElement("li")
      listItem.textContent = predictionHistory[i]
      predictionHistoryList.appendChild(listItem)
    }
  }

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

  // Load voices when they are available
  if ("speechSynthesis" in window) {
    window.speechSynthesis.onvoiceschanged = () => {
      window.speechSynthesis.getVoices()
    }
  }
})
