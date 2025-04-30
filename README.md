# Bangla Sign Language Translator

A web-based application that translates Bangla sign language gestures into Bangla text in real-time using computer vision and deep learning.

## Features

- Real-time sign language detection and translation
- 45 different Bangla signs supported
- Text-to-speech functionality for Bangla text
- Comprehensive sign language gallery
- Learning resources for Bangla sign language
- Responsive design for all devices

## Tech Stack

- **Backend**: Flask, Python
- **Computer Vision**: OpenCV, CVZone
- **Deep Learning**: TensorFlow/Keras
- **Frontend**: HTML, CSS, JavaScript
- **Text-to-Speech**: Web Speech API

## Installation

### Prerequisites

- Python 3.8 or higher
- Webcam

### Setup

1. Clone the repository:
   \`\`\`
   git clone https://github.com/yourusername/bangla-sign-translator.git
   cd bangla-sign-translator
   \`\`\`

2. Create a virtual environment:
   \`\`\`
   python -m venv venv
   \`\`\`

3. Activate the virtual environment:
   - On Windows:
     \`\`\`
     venv\Scripts\activate
     \`\`\`
   - On macOS/Linux:
     \`\`\`
     source venv/bin/activate
     \`\`\`

4. Install the required packages:
   \`\`\`
   pip install -r requirements.txt
   \`\`\`

5. Create necessary directories:
   \`\`\`
   mkdir -p static/images/signs
   mkdir -p static/data
   \`\`\`

6. Add your model files:
   - Place your trained model file at `Model/keras_model.h5`
   - Place your labels file at `Model/labels.txt`

7. Add sign images:
   - Place images of each sign in `static/images/signs/` directory
   - Name them according to their label (e.g., `a.jpg`, `b.jpg`, etc.)

8. Add the Bangla font:
   - Create a `fonts` directory
   - Place the SolaimanLipi font file in the `fonts` directory

### Running the Application

1. Start the Flask server:
   \`\`\`
   python app.py
   \`\`\`

2. Open your web browser and navigate to:
   \`\`\`
   http://127.0.0.1:5000
   \`\`\`

## Project Structure

\`\`\`
bangla-sign-translator/
├── app.py                  # Main Flask application
├── Model/                  # ML model files
│   ├── keras_model.h5      # Trained model
│   └── labels.txt          # Labels file
├── fonts/                  # Font files
│   └── SolaimanLipi_22-02-2012.ttf  # Bangla font
├── static/                 # Static files
│   ├── css/                # CSS files
│   │   └── style.css       # Main stylesheet
│   ├── js/                 # JavaScript files
│   │   ├── main.js         # Main JavaScript file
│   │   ├── translator.js   # Translator functionality
│   │   └── sign-gallery.js # Sign gallery functionality
│   ├── images/             # Image files
│   │   ├── signs/          # Sign language images
│   │   ├── logo.png        # Logo image
│   │   └── hero-image.jpg  # Hero section image
│   └── data/               # Data files
│       └── sign_data.json  # Sign data
└── templates/              # HTML templates
    ├── base.html           # Base template
    ├── index.html          # Home page
    ├── sign.html           # Sign gallery page
    ├── learn.html          # Learning resources page
    └── about.html          # About page
\`\`\`

## Customization

### Adding New Signs

1. Add the sign image to `static/images/signs/` directory
2. Update the `sign_data.json` file with the new sign information
3. Update the `labels` list in `app.py`
4. Update the `bn_sign` dictionary in `app.py`

### Changing the Model

1. Replace the model file at `Model/keras_model.h5`
2. Update the labels file at `Model/labels.txt`
3. Make sure the labels match the ones in `app.py`

## Notes

- The application uses the Web Speech API for text-to-speech, which may not support Bangla in all browsers. For better Bangla speech support, consider using a dedicated TTS service.
- For optimal performance, use the application in a well-lit environment with a clear background.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgements

- [CVZone](https://github.com/cvzone/cvzone) for the hand tracking module
- [TensorFlow](https://www.tensorflow.org/) for the deep learning framework
- [Flask](https://flask.palletsprojects.com/) for the web framework
- [SolaimanLipi](https://www.omicronlab.com/bangla-fonts.html) for the Bangla font
