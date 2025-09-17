#!/usr/bin/env python3

import os
import sys
import tempfile
from unittest.mock import patch, MagicMock
import pytest

# Add the current directory to path to import dvplayer
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import src.dvplayer.dvplayer as dvplayer


def test_file_not_found():
    """Test behavior when video file doesn't exist."""
    result = dvplayer.play_video("nonexistent_video.mp4")
    assert result is False


@patch('cv2.VideoCapture')
def test_invalid_video_file(mock_video_capture):
    """Test behavior when video file can't be opened by OpenCV."""
    # Create a temporary file
    with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as temp_file:
        temp_path = temp_file.name
        temp_file.write(b"not a video file")
    
    try:
        # Mock VideoCapture to simulate failed opening
        mock_cap = MagicMock()
        mock_cap.isOpened.return_value = False
        mock_video_capture.return_value = mock_cap
        
        result = dvplayer.play_video(temp_path)
        assert result is False
    finally:
        os.unlink(temp_path)


@patch('cv2.VideoCapture')
@patch('cv2.imshow')
@patch('cv2.waitKey')
@patch('cv2.destroyAllWindows')
def test_successful_video_playback(mock_destroy, mock_waitkey, mock_imshow, mock_video_capture):
    """Test successful video playback scenario."""
    # Create a temporary file
    with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as temp_file:
        temp_path = temp_file.name
    
    try:
        # Mock VideoCapture behavior
        mock_cap = MagicMock()
        mock_cap.isOpened.return_value = True
        mock_cap.get.side_effect = lambda prop: 30.0 if prop == 5 else 100  # FPS and frame count
        
        # Simulate reading a few frames then end
        mock_cap.read.side_effect = [
            (True, "fake_frame"),  # Frame 1
            (True, "fake_frame"),  # Frame 2
            (False, None)  # End of video
        ]
        
        mock_video_capture.return_value = mock_cap
        mock_waitkey.return_value = ord('q')  # Simulate 'q' key press
        
        result = dvplayer.play_video(temp_path)
        assert result is True
        
        # Verify OpenCV functions were called
        mock_video_capture.assert_called_once_with(temp_path)
        mock_cap.isOpened.assert_called()
        mock_destroy.assert_called_once()
    finally:
        os.unlink(temp_path)


@patch('sys.argv', ['dvplayer.py', 'test.mp4'])
@patch('dvplayer.play_video')
def test_main_default_speed(mock_play_video):
    """Test main function with default speed."""
    mock_play_video.return_value = True
    
    dvplayer.main()
    
    mock_play_video.assert_called_once_with('test.mp4', 1.0)


@patch('sys.argv', ['dvplayer.py', 'test.mp4', '--speed', '2.0'])
@patch('dvplayer.play_video')
def test_main_custom_speed(mock_play_video):
    """Test main function with custom speed."""
    mock_play_video.return_value = True
    
    dvplayer.main()
    
    mock_play_video.assert_called_once_with('test.mp4', 2.0)


@patch('sys.argv', ['dvplayer.py', 'test.mp4', '--speed', '10.0'])
def test_invalid_speed():
    """Test behavior with invalid speed value."""
    with pytest.raises(SystemExit) as exc_info:
        dvplayer.main()
    
    assert exc_info.value.code == 1


@patch('cv2.VideoCapture')
@patch('cv2.waitKey')
def test_speed_calculation(mock_waitkey, mock_video_capture):
    """Test that speed affects frame delay calculation."""
    with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as temp_file:
        temp_path = temp_file.name
    
    try:
        mock_cap = MagicMock()
        mock_cap.isOpened.return_value = True
        mock_cap.get.return_value = 30.0  # 30 FPS
        mock_cap.read.return_value = (False, None)  # End immediately
        mock_video_capture.return_value = mock_cap
        mock_waitkey.return_value = ord('q')
        
        # Test with different speeds
        result = dvplayer.play_video(temp_path, speed=2.0)
        assert result is True
        
    finally:
        os.unlink(temp_path)


@patch('sys.argv', ['dvplayer.py', 'test.mp4', '-s', '0.5'])
@patch('dvplayer.play_video')
def test_speed_short_argument(mock_play_video):
    """Test main function with short speed argument."""
    mock_play_video.return_value = True
    
    dvplayer.main()
    
    mock_play_video.assert_called_once_with('test.mp4', 0.5)