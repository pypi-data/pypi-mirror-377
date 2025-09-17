#!/usr/bin/env python3

import cv2
import argparse
import sys
import os
from tqdm import tqdm


def play_video(video_path, speed=1.0):
    """Play video using OpenCV with specified speed."""
    
    # Check if file exists
    if not os.path.exists(video_path):
        print(f"Error: File '{video_path}' not found")
        return False
    
    # Open video capture
    cap = cv2.VideoCapture(video_path)
    
    if not cap.isOpened():
        print(f"Error: Could not open video file '{video_path}'")
        return False
    
    # Get video properties
    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    print(f"Playing: {video_path}")
    print(f"FPS: {fps}, Total frames: {total_frames}")
    print(f"Speed: {speed}x")
    print("Controls: 'q' to quit, 'SPACE' to pause, ← → arrows to seek ±5 seconds")
    
    # Calculate delay between frames based on speed
    delay = int((1000 / fps) / speed) if fps > 0 else 33
    
    paused = False
    
    # Initialize progress bar
    pbar = tqdm(total=total_frames, desc="Playing", unit="frames", 
                bar_format="{desc}: {percentage:3.0f}%|{bar}| {n_fmt}/{total_fmt} frames [{elapsed}<{remaining}]")
    
    while True:
        if not paused:
            ret, frame = cap.read()
            
            # If we've reached the end, break
            if not ret:
                break
            
            # Display the frame
            cv2.imshow('DaVinci Video Player', frame)
            
            # Check if window was closed
            if cv2.getWindowProperty('DaVinci Video Player', cv2.WND_PROP_VISIBLE) < 1:
                break
            
            # Update progress bar
            current_frame = int(cap.get(cv2.CAP_PROP_POS_FRAMES))
            pbar.n = current_frame
            pbar.refresh()
        
        # Handle key presses
        key = cv2.waitKey(delay if not paused else 1) & 0xFF
        
        if key == ord('q'):
            break
        elif key == ord(' '):  # Space bar
            paused = not paused
            if paused:
                pbar.set_description("Paused")
            else:
                pbar.set_description("Playing")
        elif key == 83:  # Right arrow key
            # Seek forward 5 seconds
            current_frame = cap.get(cv2.CAP_PROP_POS_FRAMES)
            seek_frames = int(fps * 5)  # 5 seconds worth of frames
            new_frame = min(current_frame + seek_frames, total_frames - 1)
            cap.set(cv2.CAP_PROP_POS_FRAMES, new_frame)
            pbar.n = int(new_frame)
            pbar.refresh()
        elif key == 81:  # Left arrow key
            # Seek backward 5 seconds
            current_frame = cap.get(cv2.CAP_PROP_POS_FRAMES)
            seek_frames = int(fps * 5)  # 5 seconds worth of frames
            new_frame = max(current_frame - seek_frames, 0)
            cap.set(cv2.CAP_PROP_POS_FRAMES, new_frame)
            pbar.n = int(new_frame)
            pbar.refresh()
    
    # Clean up
    pbar.close()
    cap.release()
    cv2.destroyAllWindows()
    return True


def main():
    parser = argparse.ArgumentParser(description='Simple video player for remote clusters')
    parser.add_argument('video', help='Path to video file')
    parser.add_argument('--speed', '-s', type=float, default=1.0, 
                       help='Playback speed (0.1 to 5.0, default: 1.0)')
    
    args = parser.parse_args()
    
    # Validate speed
    if args.speed < 0.1 or args.speed > 5.0:
        print("Error: Speed must be between 0.1 and 5.0")
        sys.exit(1)
    
    # Play the video
    success = play_video(args.video, args.speed)
    
    if not success:
        sys.exit(1)


if __name__ == "__main__":
    main()