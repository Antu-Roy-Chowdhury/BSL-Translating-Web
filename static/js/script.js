document.addEventListener("DOMContentLoaded", () => {
  const startBtn = document.getElementById("start-btn")
  const stopBtn = document.getElementById("stop-btn")
  const predictionText = document.getElementById("prediction-text")
  const predictionDisplay = document.getElementById("prediction-display")
  const predictionHistoryList = document.getElementById("prediction-history-list")

  let isRunning = false
  let predictionInterval = null
  const predictionHistory = []

  // Start camera button
  startBtn.addEventListener("click", () => {
    console.log("Starting camera...");
    startBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> লোড হচ্ছে...';
    startBtn.disabled = true;
    fetch("/start", {
      method: "POST",
    })
      .then((response) => response.json())
      .then((data) => {
        console.log("Camera start response:", data)
        startBtn.innerHTML = '<i class="fas fa-play"></i> শুরু করুন';
        if (data.status === "success") {
          isRunning = true
          startBtn.disabled = true
          stopBtn.disabled = false

          // Start polling for predictions
          predictionInterval = setInterval(getPrediction, 500)
        } else {
          alert("Error: " + data.message)
        }
      })
      .catch((error) => {
        console.error("Error:", error)
        alert("Failed to start camera")
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

          // Stop polling for predictions
          clearInterval(predictionInterval)
          predictionText.textContent = "No prediction yet"
          predictionDisplay.textContent = ""
        }
      })
      .catch((error) => {
        console.error("Error:", error)
        alert("Failed to stop camera")
      })
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
        console.error("Error:", error)
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
})
