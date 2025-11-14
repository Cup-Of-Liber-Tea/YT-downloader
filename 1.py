import yt_dlp
import time
import os
import glob
import subtitle_parser
import comment_collector

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

ydl_opts = {
    'format': 'best',
    'ffmpeg_location': r'C:\Users\hangy\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.WinGet.Source_8wekyb3d8bbwe\ffmpeg-8.0-full_build\bin\ffmpeg.exe',
    'concurrent_fragment_downloads': 16,
    'http_headers': {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36',
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
    # 'sleep_interval_requests': 5,  # 매 요청마다 5초 대기
    # 'writeinfojson': False,   # 영상 정보 JSON으로 남기기(실무 분석) - 비활성화
    # 'verbose': True,             # 상세 로그(디버그 필요시)
    'progress_hooks': [my_hook],  # 다운로드 진행 상황 표시를 위한 훅 활성화

}

while True: # 연속 다운로드를 위한 루프 시작
    url = input("다운로드할 YouTube URL을 입력하세요 (종료하려면 'q' 또는 'quit' 입력): ")
    if url.lower() in ['q', 'quit']:
        print("스크립트를 종료합니다.")
        break

    downloaded_filepaths.clear() # 다음 다운로드를 위해 리스트 초기화
    
    start_time = time.time()

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=False) # 다운로드 전에 정보 추출
            ydl.download([url])

            # 자막 파일 경로 결정 로직
            vtt_filepath = None
            download_dir = None

            if downloaded_filepaths:
                # 비디오가 실제로 다운로드된 경우, 해당 디렉토리를 사용
                first_downloaded_file = downloaded_filepaths[0]
                download_dir = os.path.dirname(first_downloaded_file)
            else:
                # 비디오가 이미 존재하여 downloaded_filepaths가 비어있는 경우,
                # info_dict와 outtmpl을 사용하여 예상 자막 경로를 생성
                if info_dict and (ydl_opts.get('writesubtitles') or ydl_opts.get('writeautomaticsub')):
                    subtitle_info = info_dict.copy()
                    if ydl_opts.get('subtitleslangs') and 'ko' in ydl_opts['subtitleslangs']:
                        subtitle_info['ext'] = 'ko.vtt'
                        # 예상되는 전체 자막 파일 경로 생성
                        predicted_vtt_filepath = ydl.prepare_filename(subtitle_info, outtmpl=ydl_opts['outtmpl'])
                        download_dir = os.path.dirname(predicted_vtt_filepath)
            
            if download_dir:
                # 해당 디렉토리에서 .ko.vtt 파일 찾기 (glob 사용)
                vtt_files = glob.glob(os.path.join(download_dir, '*.ko.vtt'))
                if vtt_files:
                    vtt_filepath = max(vtt_files, key=os.path.getmtime)

            # 자막 텍스트 파싱 및 저장 로직
            if vtt_filepath and os.path.exists(vtt_filepath):
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
                print("한글 자막 파일(.ko.vtt)을 찾을 수 없습니다 (자막 다운로드 옵션이 활성화되었는지 확인). ")

            # 댓글 수집 및 저장 로직
            if download_dir and info_dict:
                video_id = info_dict.get('id')
                video_title = str(info_dict.get('title', 'Unknown'))
                print(f"비디오 ID: {video_id}, 제목: {video_title}")
                try:
                    comments = comment_collector.collect_youtube_comments(video_id, max_results=30)
                    if comments:
                        comment_collector.save_comments_to_file(comments, download_dir, video_title, video_id)
                except Exception as e:
                    print(f"댓글 수집 중 오류 발생: {e}")

    except Exception as e:
        print(f"다운로드 중 오류 발생: {e}")
        pass # 다운로드 오류 발생 시 자막 처리 로직은 스킵

    end_time = time.time()
    total_time = end_time - start_time
    print(f"총 다운로드 소요 시간: {total_time:.2f}초")

    # 다운로드된 영상 디렉토리 열기 (Windows 전용)
    target_dir_to_open = download_dir # 이제 download_dir이 항상 설정될 것입니다.

    if target_dir_to_open:
        print(f"다운로드 디렉토리 열기: {target_dir_to_open}")
        try:
            os.startfile(target_dir_to_open) # Windows에서 폴더 열기
        except AttributeError:
            print("경고: os.startfile은 Windows 전용입니다. 다른 OS에서는 수동으로 폴더를 열어야 합니다.")
        except Exception as e:
            print(f"디렉토리를 여는 중 오류 발생: {e}")
