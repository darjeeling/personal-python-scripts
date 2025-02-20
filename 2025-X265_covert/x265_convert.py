# /// script
# requires-python = ">=3.13"
# dependencies = []
# ///

import argparse
import subprocess
from pathlib import Path
import os


def get_video_duration(file_path):
    """ffmpeg를 사용하여 비디오 파일의 duration(초 단위)을 반환"""
    try:
        result = subprocess.run(
            ["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
             "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", str(file_path)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True,
        )
        return float(result.stdout.strip())
    except subprocess.CalledProcessError:
        print(f"Failed to get duration for {file_path}")
        return None


def list_mp4_files(directory):
    """지정된 디렉토리에서 _X265로 끝나지 않는 mp4 파일 목록을 반환"""
    return [
        file for file in directory.iterdir()
        if file.suffix == ".mp4" and not file.stem.endswith("_X265")
    ]


def process_files(directory):
    """디렉토리 내 mp4 파일 처리"""
    mp4_files = list_mp4_files(directory)
    
    for file in mp4_files:
        base_name = file.stem  # 파일명 (확장자 제외)
        new_file = directory / f"{base_name}_X265.mp4"

        
        # 새 파일이 이미 존재하는 경우 duration 비교
        if new_file.exists():
            original_duration = get_video_duration(file)
            new_duration = get_video_duration(new_file)
            
            if new_duration is not None and original_duration is not None and new_duration < original_duration:
                print(f"Removing corrupted file: {new_file}")
                new_file.unlink()  # 기존 파일 삭제
            elif new_duration is None:
                print(f"Removing corrupted file: {new_file}")
                new_file.unlink()  # 기존 파일 삭제
            else:
                print(f"Skipping: {new_file.name} (duration matches or exceeds original)")
                continue

        # testing commands...
        # https://gist.github.com/nico-lab/58ac62e359bd63feed36af64db3e4406
        # -hwaccel qsv -c:v hevc_qsv -extbrc 1 -look_ahead_depth 100
        #  Using the constant quantization parameter (CQP) by default.
        #  Please use the global_quality option and other options for a quality-based mode or
        #  the b option and other options for a bitrate-based mode if the default is not the desired choice.

        #  https://forum.videohelp.com/threads/410216-ffmpeg-newbie-QSV-command#post2696281
        # "G:\program files\ffmpeg64\bin\ffmpeg.exe" -y -benchmark -init_hw_device qsv=hw -filter_hw_device hw -v verbose ^
        # -i %1 -pix_fmt nv12 ^
        # -load_plugin h264_hw -c:v h264_qsv -preset veryslow -global_quality 21 -look_ahead 1 -look_ahead_depth 30 ^
        # -profile:v high -level:v 4.2 -adaptive_b 1 -rdo 1 -g 30 -colorspace bt709 -color_range tv ^
        #-acodec copy ^"%~dpn1.h264.qsv.mkv"
        # ffmpeg 명령 실행
        # /usr/lib/jellyfin-ffmpeg/ffmpeg -hwaccel qsv -c:v hevc_qsv -hwaccel_output_format qsv \
        #   -global_quality 22 -look_ahead 1 -extbrc -look_ahead_depth 99 -preset veryslow -c:a copy \
        #  -i input
        command = [
            "/usr/lib/jellyfin-ffmpeg/ffmpeg",
            "-hwaccel", "qsv",
            "-c:v", "hevc_qsv",
            "-hwaccel_output_format", "qsv",
            "-i", str(file),
            "-global_quality","22",
            "-look_ahead","1",
            "-preset", "slow",
            "-tag:v", "hvc1",
            "-movflags", "+faststart",
            "-c:a", "copy",
            str(new_file)
        ]
        try:
            print(f"Processing: {file.name} -> {new_file.name}")
            subprocess.run(command, check=True)
            # 원본 파일의 수정일 가져오기
            original_mtime = file.stat().st_mtime
            # 새 파일의 수정일을 원본 파일의 수정일로 설정
            os.utime(new_file, (original_mtime, original_mtime))
        except subprocess.CalledProcessError as e:
            print(f"Error processing {file.name}: {e}")


def main():
    parser = argparse.ArgumentParser(description="Process MP4 files in a directory.")
    parser.add_argument("-d", "--directory", required=True, help="Target directory containing MP4 files.")
    args = parser.parse_args()
    
    directory = Path(args.directory)
    
    if not directory.is_dir():
        print(f"Error: {directory} is not a valid directory.")
        return
    process_files(directory)

if __name__ == "__main__":
    main()
