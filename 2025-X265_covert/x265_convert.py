# /// script
# requires-python = ">=3.13"
# dependencies = []
# ///

import argparse
import subprocess
from pathlib import Path

def list_mp4_files(directory):
    """지정된 디렉토리에서 mp4 파일 목록을 반환"""
    return [file for file in directory.iterdir() if file.suffix == ".mp4"]

def process_files(directory):
    """디렉토리 내 mp4 파일 처리"""
    mp4_files = list_mp4_files(directory)

    for file in mp4_files:
        base_name = file.stem  # 파일명 (확장자 제외)
        new_file = directory / f"{base_name}_X265.mp4"

        # 새 파일이 이미 존재하는지 확인
        if not new_file.exists():
            command = [
                "ffmpeg",
                "-i", str(file),
                "-c:v", "libx265",
                "-preset", "slow",
                "-c:a", "copy",
                str(new_file)
            ]
            try:
                print(f"Processing: {file.name} -> {new_file.name}")
                subprocess.run(command, check=True)
            except subprocess.CalledProcessError as e:
                print(f"Error processing {file.name}: {e}")
        else:
            print(f"Skipping: {new_file.name} already exists.")

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
