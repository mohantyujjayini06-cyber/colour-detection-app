import streamlit as st
import cv2
import numpy as np
from PIL import Image
import io
import tempfile
import os

st.set_page_config(page_title="Color Detection App", layout="wide")

st.title("🎨 Color Detection using HSV")
st.markdown("Detect Red, Blue, Green, and other colors using OpenCV HSV color space.")

# Sidebar controls
st.sidebar.header("Settings")

input_source = st.sidebar.radio("Select Input Source", ["Webcam Snapshot", "Upload Image", "Upload Video", "Live Webcam Stream"])

mode = st.sidebar.selectbox(
    "Detection Mode",
    [
        "All Colors",
        "Red",
        "Blue",
        "Green",
        "Every Color Except White",
        "Custom HSV",
    ],
)

# Default HSV ranges (from original project)
DEFAULT_RANGES = {
    "Red": {"low": [161, 155, 84], "high": [179, 255, 255]},
    "Blue": {"low": [94, 80, 2], "high": [126, 255, 255]},
    "Green": {"low": [40, 100, 100], "high": [102, 255, 255]},
    "Every Color Except White": {"low": [0, 42, 0], "high": [179, 255, 255]},
}


def apply_hsv_mask(frame_bgr, low, high):
    hsv = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, np.array(low), np.array(high))
    result = cv2.bitwise_and(frame_bgr, frame_bgr, mask=mask)
    return mask, result


def process_frame(frame_bgr, mode_name, custom_low=None, custom_high=None):
    if mode_name == "All Colors":
        results = {}
        for color_name in ["Red", "Blue", "Green", "Every Color Except White"]:
            low = DEFAULT_RANGES[color_name]["low"]
            high = DEFAULT_RANGES[color_name]["high"]
            mask, result = apply_hsv_mask(frame_bgr, low, high)
            results[color_name] = {"mask": mask, "result": result}
        return results
    elif mode_name == "Custom HSV":
        mask, result = apply_hsv_mask(frame_bgr, custom_low, custom_high)
        return {"Custom": {"mask": mask, "result": result}}
    else:
        low = DEFAULT_RANGES[mode_name]["low"]
        high = DEFAULT_RANGES[mode_name]["high"]
        mask, result = apply_hsv_mask(frame_bgr, low, high)
        return {mode_name: {"mask": mask, "result": result}}


def bgr_to_rgb(img):
    return cv2.cvtColor(img, cv2.COLOR_BGR2RGB)


def get_input_frame():
    if input_source == "Webcam Snapshot":
        camera_image = st.camera_input("Take a picture")
        if camera_image is not None:
            pil_img = Image.open(camera_image)
            frame = np.array(pil_img)
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            return frame
    elif input_source == "Upload Image":
        uploaded_file = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png", "bmp"])
        if uploaded_file is not None:
            pil_img = Image.open(uploaded_file)
            frame = np.array(pil_img)
            if len(frame.shape) == 2:
                frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)
            elif frame.shape[2] == 4:
                frame = cv2.cvtColor(frame, cv2.COLOR_RGBA2BGR)
            else:
                frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            return frame
    return None


def process_video_stream(frame_bgr, mode_name, custom_low=None, custom_high=None):
    """Process a single frame and return images for display."""
    if mode_name == "All Colors":
        results = {}
        for color_name in ["Red", "Blue", "Green", "Every Color Except White"]:
            low = DEFAULT_RANGES[color_name]["low"]
            high = DEFAULT_RANGES[color_name]["high"]
            mask, result = apply_hsv_mask(frame_bgr, low, high)
            results[color_name] = (mask, bgr_to_rgb(result))
        return bgr_to_rgb(frame_bgr), results
    elif mode_name == "Custom HSV":
        mask, result = apply_hsv_mask(frame_bgr, custom_low, custom_high)
        return bgr_to_rgb(frame_bgr), {"Custom": (mask, bgr_to_rgb(result))}
    else:
        low = DEFAULT_RANGES[mode_name]["low"]
        high = DEFAULT_RANGES[mode_name]["high"]
        mask, result = apply_hsv_mask(frame_bgr, low, high)
        return bgr_to_rgb(frame_bgr), {mode_name: (mask, bgr_to_rgb(result))}


# Custom HSV sliders
if mode == "Custom HSV":
    st.sidebar.markdown("### Custom HSV Range")
    h_low = st.sidebar.slider("Hue Low", 0, 179, 0)
    s_low = st.sidebar.slider("Saturation Low", 0, 255, 42)
    v_low = st.sidebar.slider("Value Low", 0, 255, 0)
    h_high = st.sidebar.slider("Hue High", 0, 179, 179)
    s_high = st.sidebar.slider("Saturation High", 0, 255, 255)
    v_high = st.sidebar.slider("Value High", 0, 255, 255)
    custom_low = [h_low, s_low, v_low]
    custom_high = [h_high, s_high, v_high]
else:
    custom_low = None
    custom_high = None


# Handle input sources
if input_source in ["Webcam Snapshot", "Upload Image"]:
    frame = get_input_frame()

    if frame is not None:
        results = process_frame(frame, mode, custom_low, custom_high)

        st.markdown("---")
        st.subheader("Results")

        if mode == "All Colors":
            col1, col2, col3 = st.columns(3)
            with col1:
                st.image(bgr_to_rgb(frame), caption="Original", use_container_width=True)
            with col2:
                st.image(results["Red"]["mask"], caption="Red Mask", use_container_width=True)
                st.image(bgr_to_rgb(results["Red"]["result"]), caption="Red Detection", use_container_width=True)
            with col3:
                st.image(results["Blue"]["mask"], caption="Blue Mask", use_container_width=True)
                st.image(bgr_to_rgb(results["Blue"]["result"]), caption="Blue Detection", use_container_width=True)

            col4, col5, col6 = st.columns(3)
            with col4:
                st.image(results["Green"]["mask"], caption="Green Mask", use_container_width=True)
                st.image(bgr_to_rgb(results["Green"]["result"]), caption="Green Detection", use_container_width=True)
            with col5:
                st.image(results["Every Color Except White"]["mask"], caption="Non-White Mask", use_container_width=True)
                st.image(
                    bgr_to_rgb(results["Every Color Except White"]["result"]),
                    caption="Every Color Except White",
                    use_container_width=True,
                )
            with col6:
                st.empty()

        elif mode == "Custom HSV":
            col1, col2, col3 = st.columns(3)
            with col1:
                st.image(bgr_to_rgb(frame), caption="Original", use_container_width=True)
            with col2:
                st.image(results["Custom"]["mask"], caption="Custom Mask", use_container_width=True)
            with col3:
                st.image(bgr_to_rgb(results["Custom"]["result"]), caption="Custom Result", use_container_width=True)
            st.info(f"HSV Range: Low = {custom_low}, High = {custom_high}")

        else:
            col1, col2, col3 = st.columns(3)
            with col1:
                st.image(bgr_to_rgb(frame), caption="Original", use_container_width=True)
            with col2:
                st.image(results[mode]["mask"], caption=f"{mode} Mask", use_container_width=True)
            with col3:
                st.image(bgr_to_rgb(results[mode]["result"]), caption=f"{mode} Detection", use_container_width=True)

        # Download buttons
        st.markdown("---")
        st.subheader("Download Results")
        for key, val in results.items():
            result_rgb = cv2.cvtColor(val["result"], cv2.COLOR_BGR2RGB)
            result_pil = Image.fromarray(result_rgb)
            buf = io.BytesIO()
            result_pil.save(buf, format="PNG")
            byte_im = buf.getvalue()
            st.download_button(
                label=f"Download {key} Result",
                data=byte_im,
                file_name=f"{key.lower().replace(' ', '_')}_result.png",
                mime="image/png",
            )

    else:
        st.info("👈 Please select an input source and capture/upload an image to begin.")

elif input_source == "Upload Video":
    uploaded_video = st.file_uploader("Upload a video", type=["mp4", "avi", "mov", "mkv"])
    if uploaded_video is not None:
        # Save uploaded video to a temp file
        tfile = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
        tfile.write(uploaded_video.read())
        tfile.close()

        cap = cv2.VideoCapture(tfile.name)
        if not cap.isOpened():
            st.error("Could not open video file.")
        else:
            st.markdown("---")
            st.subheader("Video Processing")
            col_orig, col_mask, col_res = st.columns(3)
            orig_placeholder = col_orig.empty()
            mask_placeholder = col_mask.empty()
            res_placeholder = col_res.empty()

            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            fps = cap.get(cv2.CAP_PROP_FPS)
            progress_bar = st.progress(0)
            stop_btn = st.button("Stop Processing")
            frame_idx = 0

            while cap.isOpened():
                ret, frame = cap.read()
                if not ret or stop_btn:
                    break
                frame_idx += 1
                progress_bar.progress(min(frame_idx / max(frame_count, 1), 1.0))

                orig_rgb, results = process_video_stream(frame, mode, custom_low, custom_high)
                orig_placeholder.image(orig_rgb, caption="Original", use_container_width=True)

                if mode == "All Colors":
                    # Stack results vertically for display
                    mask_imgs = [v[0] for v in results.values()]
                    res_imgs = [v[1] for v in results.values()]
                    mask_combined = np.vstack([cv2.resize(m, (320, 240)) for m in mask_imgs])
                    res_combined = np.vstack([cv2.resize(r, (320, 240)) for r in res_imgs])
                    mask_placeholder.image(mask_combined, caption="Masks", use_container_width=True)
                    res_placeholder.image(res_combined, caption="Detections", use_container_width=True)
                else:
                    key = list(results.keys())[0]
                    mask, res = results[key]
                    mask_placeholder.image(mask, caption=f"{key} Mask", use_container_width=True)
                    res_placeholder.image(res, caption=f"{key} Detection", use_container_width=True)

            cap.release()
            os.unlink(tfile.name)
            st.success("Video processing complete!")
    else:
        st.info("👈 Please upload a video file to begin.")

elif input_source == "Live Webcam Stream":
    st.markdown("---")
    st.subheader("Live Webcam Stream")
    st.warning("Press 'Stop Stream' to end the webcam feed.")

    stop_stream = st.button("Stop Stream")
    col_orig, col_mask, col_res = st.columns(3)
    orig_placeholder = col_orig.empty()
    mask_placeholder = col_mask.empty()
    res_placeholder = col_res.empty()

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        st.error("Could not open webcam. Please check your camera.")
    else:
        while not stop_stream:
            ret, frame = cap.read()
            if not ret:
                st.error("Failed to read from webcam.")
                break
            orig_rgb, results = process_video_stream(frame, mode, custom_low, custom_high)
            orig_placeholder.image(orig_rgb, caption="Original", use_container_width=True)

            if mode == "All Colors":
                mask_imgs = [v[0] for v in results.values()]
                res_imgs = [v[1] for v in results.values()]
                mask_combined = np.vstack([cv2.resize(m, (320, 240)) for m in mask_imgs])
                res_combined = np.vstack([cv2.resize(r, (320, 240)) for r in res_imgs])
                mask_placeholder.image(mask_combined, caption="Masks", use_container_width=True)
                res_placeholder.image(res_combined, caption="Detections", use_container_width=True)
            else:
                key = list(results.keys())[0]
                mask, res = results[key]
                mask_placeholder.image(mask, caption=f"{key} Mask", use_container_width=True)
                res_placeholder.image(res, caption=f"{key} Detection", use_container_width=True)
        cap.release()
        st.info("Webcam stream stopped.")

st.markdown("---")
st.markdown("Made by **UJJAYINI**")


