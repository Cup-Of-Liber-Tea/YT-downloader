import yt_dlp
import time
import os
import glob
import subtitle_parser

# 다운로드된 파일 경로를 저장할 리스트
downloaded_filepaths = []

def my_hook(d):
    if d['status'] == 'finished':
        # 다운로드 완료 시 파일 경로 저장
        if 'filepath' in d:
            downloaded_filepaths.append(d['filepath'])
        elif 'filename' in d:
            downloaded_filepaths.append(d['filename'])
        elif 'info_dict' in d and 'filepath' in d['info_dict']:
            downloaded_filepaths.append(d['info_dict']['filepath'])

url = input("다운로드할 YouTube URL을 입력하세요: ")

ydl_opts = {
    'format': 'bv+ba/best',
    'ffmpeg_location': r'C:\Users\hangy\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-8.0-full_build\bin\ffmpeg.exe',
    'concurrent_fragment_downloads': 16,
    'http_headers': {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Referer': 'https://www.youtube.com/',
                    },
    'ratelimit': 100 * 1024 * 1024,  # 초당 100MB 이하 속도로 설정 (선택)
    # 'cookiefile': 'cookies.txt', # 로그인 쿠키사용  (계정 정지 위험)
    'retries': 10,                     # 실패 시 조각 재시도 횟수
    'fragment_retries': 20,            # 프래그먼트(조각) 단위 추가 재시도
    'continuedl': True,                # 이어받기(Resume) 항상 시도
    'nooverwrites': True,              # 이미 있는 파일은 덮어쓰기X (충돌 방지)
    'ignoreerrors': True,              # 개별 오류 발생해도 계속(배치다운시 필수)
    'writesubtitles': True,       # 자막(있는 경우) 자동 다운
    'writeautomaticsub': True,    # 자동생성 자막도 시도
    'subtitleslangs': ['ko'],    # 한글 자막 우선 다운로드 (자동 생성 포함)
    # 'writethumbnail': True,       # 썸네일 자동 저장
    'outtmpl': 'videos/%(title)s/%(title)s [%(id)s].%(ext)s', # 영상 제목 기반의 하위 폴더에 저장
    'overwrites': False,           # 이미 받을 때는 실패 방지용
    'sleep_interval_requests': 5,  # 매 요청마다 5초 대기
    # 'writeinfojson': False,   # 영상 정보 JSON으로 남기기(실무 분석) - 비활성화
    # 'verbose': True,             # 상세 로그(디버그 필요시)
    'progress_hooks': [my_hook],  # 다운로드 진행 상황 표시를 위한 훅 활성화

}

start_time = time.time()

with yt_dlp.YoutubeDL(ydl_opts) as ydl:
    ydl.download([url])

end_time = time.time()
total_time = end_time - start_time
print(f"총 다운로드 소요 시간: {total_time:.2f}초")

# 자막 텍스트 파싱 및 저장 로직
if downloaded_filepaths:
    # 다운로드된 파일들 중 .ko.vtt 파일 찾기
    vtt_filepath = None
    for fpath in downloaded_filepaths:
        if fpath.endswith('.ko.vtt'):
            vtt_filepath = fpath
            break

    if vtt_filepath and (ydl_opts.get('writesubtitles') or ydl_opts.get('writeautomaticsub')):
        print(f"다운로드된 자막 파일 발견: {vtt_filepath}")
        try:
            parsed_text = subtitle_parser.parse_vtt_to_text(vtt_filepath)
            output_text_file = vtt_filepath.replace('.ko.vtt', '.ko.txt')
            with open(output_text_file, 'w', encoding='utf-8') as f:
                f.write(parsed_text)
            print(f"자막 텍스트가 다음 파일에 저장되었습니다: {output_text_file}")
        except Exception as e:
            print(f"자막 파싱 중 오류 발생: {e}")
    else:
        print("한글 자막 파일(.ko.vtt)을 찾을 수 없습니다 (자막 다운로드 옵션이 활성화되었는지 확인).")
else:
    print("다운로드된 파일 경로를 찾을 수 없습니다.")
