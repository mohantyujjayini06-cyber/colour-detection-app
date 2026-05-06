# Color Detection using OpenCV + Streamlit

This project detects colors (Red, Blue, Green, and non-white colors) using OpenCV's HSV color space, now wrapped in an interactive Streamlit web application.

## Features

- **Webcam Snapshot**: Capture a single frame from your camera for detection
- **Image Upload**: Detect colors in uploaded images
- **Video Upload**: Process and detect colors in uploaded video files (MP4, AVI, MOV, MKV)
- **Live Webcam Stream**: Real-time continuous color detection from your webcam
- **Multiple Modes**:
  - Red Detection
  - Blue Detection
  - Green Detection
  - Every Color Except White
  - All Colors (shows all masks simultaneously)
  - Custom HSV (adjust your own HSV ranges with sliders)
- **Interactive Sliders**: Fine-tune HSV thresholds in real-time
- **Side-by-side Display**: Original image/video next to the masked output

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the Streamlit app:
```bash
streamlit run app.py
```

## File Structure

- `app.py` — Streamlit application
- `test_Hsv_color.py` — Original OpenCV webcam script (all colors)
- `cv2_Red color mask.py` — Original red-only script
- `cv2_Blue color mask.py` — Original blue-only script
- `cv2_green color mask.py` — Original green-only script
- `every colour except white.py` — Original non-white script
- `requirements.txt` — Python dependencies

