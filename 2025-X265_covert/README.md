## 동영상 X265 로 재인코딩 스크립트

해당 디렉토리의 .mp4 파일들을 ffmpeg 로 x265 로 다시 인코딩한다. 

slow 로 인코딩하므로 cpu 로 동작하지만 매우 느림

새 파일명은 _X265.mp4 가 됨

[FFMPEG의 H.265 옵션 설명](https://trac.ffmpeg.org/wiki/Encode/H.265)


```bash
uv run x265_convert.py -d /storage/dj/movie/202302-newyork-family-trip
```

## intel iGPU 사용법

from https://nelsonslog.wordpress.com/2022/08/09/ubuntu-ffmpeg-and-intel-gpu-acceleration/

n100 alder lake 의 IGPU 를 사용하게 해야한다. 

설치는 여기서 받아서 한다. https://github.com/jellyfin/jellyfin-ffmpeg 

```bash
$ apt install onevpl-tools vainfo intel-media-va-driver-non-free intel-gpu-tools
$ sudo vainfo
vainfo: Driver version: Intel iHD driver for Intel(R) Gen Graphics - 22.3.1 ()
$ intel_gpu_top # for monitoring
```

```bash
/usr/lib/jellyfin-ffmpeg/ffmpeg \
 -c:v h264_qsv \
 -i INPUT.mp4 \
 -c:v hevc_qsv \
 -preset veryslow \
 -preset slow \
 -c:a copy \
 OUTPUT.mp4
```

디코딩과 인코딩 https://stackoverflow.com/a/73238755


## 추후 개선점

- [ ] jellyfin-ffmpeg 적용  
        https://nelsonslog.wordpress.com/2022/08/09/ubuntu-ffmpeg-and-intel-gpu-acceleration/
- [x] _X265.mp4 로 끝나면 skip
- [x] 컨버팅된 파일이 있으면 있는 파일의 duration 을 읽어서 현재 파일과 같은지 확인 필요 
- [ ] 잘 컨버텅이 되었는지 확인, VMAF 를 이용해서 퀄러티를 측정하면 될듯함. 그러나 n100 머신에게는 멀다.  
      https://github.com/Netflix/vmaf/blob/master/resource/doc/ffmpeg.md
- [ ] ffmpeg 설치되었는지 확인 
- [ ] cuda 등 디텍트해서 자동 설정
- [ ] recursive 가능하게 

## 참고

- https://transloadit.com/devtips/reducing-video-file-size-with-ffmpeg-for-web-optimization/
- https://www.tauceti.blog/posts/linux-ffmpeg-amd-5700xt-hardware-video-encoding-hevc-h265-vaapi/
- https://www.fastpix.io/blog/video-streaming-with-capped-crf
- https://www.muvi.com/blogs/optimize-ffmpeg-for-fast-video-encoding/
- VMAF 를 이용해서 퀄러티를 measure https://stackoverflow.com/a/78234869
- https://www.gumlet.com/learn/ffmpeg-compress-video/
