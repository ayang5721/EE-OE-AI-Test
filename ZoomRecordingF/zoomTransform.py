from fpdf import FPDF
import os
import imagehash
from PIL import Image
from moviepy.editor import VideoFileClip
import webvtt


def extract_slide_timestamps(video_path, threshold=10):
    clip = VideoFileClip(video_path)
    duration = int(clip.duration)
    slide_changes = [0]
    prev_hash = None
    for t in range(1, duration, 1):
        frame = clip.get_frame(t)
        image = Image.fromarray(frame)
        curr_hash = imagehash.phash(image)
        if prev_hash is not None and abs(prev_hash - curr_hash) > threshold:
            slide_changes.append(t)
        prev_hash = curr_hash
    slide_changes.append(duration)
    return slide_changes


def parse_vtt(vtt_path):
    segments = []
    for caption in webvtt.read(vtt_path):
        start = convert_to_seconds(caption.start)
        end = convert_to_seconds(caption.end)
        segments.append({"start": start, "end": end, "text": caption.text})
    return segments


def convert_to_seconds(timestamp):
    h, m, s = timestamp.split(":")
    s, ms = s.split(".")
    return int(h) * 3600 + int(m) * 60 + int(s) + int(ms) / 1000


def group_transcript_by_slide(slide_times, transcript_segments):
    grouped = []
    for i in range(len(slide_times) - 1):
        start = slide_times[i]
        end = slide_times[i + 1]
        text = " ".join([seg["text"] for seg in transcript_segments if start <= seg["start"] < end])
        grouped.append({
            "start": start,
            "end": end,
            "text": text,
            "slide_index": i
        })
    return grouped


def save_pdf_with_slides_and_text(video_path, grouped_data, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    clip = VideoFileClip(video_path)
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)

    for item in grouped_data:
        frame = clip.get_frame((item["start"] + item["end"]) / 2)
        img_path = os.path.join(output_dir, f"slide_{item['slide_index']}.png")
        Image.fromarray(frame).save(img_path)

        pdf.add_page()
        pdf.image(img_path, x=10, w=180)
        pdf.set_font("Arial", size=12)
        pdf.ln(100)
        pdf.multi_cell(0, 10, item["text"])

    pdf_path = os.path.join(output_dir, "slides_with_transcript.pdf")
    pdf.output(pdf_path)
    return pdf_path


def process_zoom_folder(meeting_folder):
    base_folder = os.path.abspath(meeting_folder).rstrip("/\\")
    output_folder = f"{base_folder}_output"
    os.makedirs(output_folder, exist_ok=True)

    for meeting in os.listdir(meeting_folder):
        meeting_path = os.path.join(meeting_folder, meeting)
        if os.path.isdir(meeting_path):
            video_file = None
            vtt_file = None
            for file in os.listdir(meeting_path):
                if file.endswith(".mp4"):
                    video_file = os.path.join(meeting_path, file)
                elif file.endswith(".vtt"):
                    vtt_file = os.path.join(meeting_path, file)
            if video_file and vtt_file:
                print(f"Processing {meeting}")
                slide_times = extract_slide_timestamps(video_file)
                transcript_segments = parse_vtt(vtt_file)
                grouped = group_transcript_by_slide(slide_times, transcript_segments)
                output_path = os.path.join(output_folder, meeting)
                save_pdf_with_slides_and_text(video_file, grouped, output_path)


if __name__ == "__main__":
    import tkinter as tk
    from tkinter import filedialog

    print("Please select your Zoom recordings folder...")

    root = tk.Tk()
    root.withdraw()  # Hide the tkinter window

    selected_folder = filedialog.askdirectory(title="Select Zoom Meeting Folder")

    if selected_folder:
        print(f"✅ Folder selected: {selected_folder}")
        process_zoom_folder(selected_folder)
    else:
        print("❌ No folder selected. Exiting.")
