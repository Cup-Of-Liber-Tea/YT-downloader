import os
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import json
from datetime import datetime

# YouTube API 키를 환경변수에서 가져오기 (보안을 위해)
# 또는 직접 설정: API_KEY = "your_api_key_here"
API_KEY = REMOVED

def get_video_id_from_url(url):
    """YouTube URL에서 video ID 추출"""
    import re
    
    # 다양한 YouTube URL 패턴 매칭 (YouTube Shorts 포함)
    patterns = [
        r'(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/|youtube\.com\/shorts\/)([a-zA-Z0-9_-]{11})',
        r'youtube\.com\/watch\?.*v=([a-zA-Z0-9_-]{11})',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None

def collect_youtube_comments(video_id, max_results=30, api_key=None):
    """
    YouTube API를 사용하여 댓글 수집
    
    Args:
        video_id (str): YouTube 비디오 ID
        max_results (int): 수집할 댓글 수 (기본 30개)
        api_key (str): YouTube API 키 (선택사항)
    
    Returns:
        list: 댓글 데이터 리스트
    """
    if not api_key:
        api_key = API_KEY
    
    if not api_key:
        print("오류: YouTube API 키가 설정되지 않았습니다.")
        print("환경변수 YOUTUBE_API_KEY를 설정하거나 comment_collector.py에서 API_KEY를 직접 설정하세요.")
        return []
    
    try:
        # YouTube API 클라이언트 생성
        youtube = build('youtube', 'v3', developerKey=api_key)
        
        # 댓글 스레드 요청
        request = youtube.commentThreads().list(
            part='snippet',
            videoId=video_id,
            maxResults=max_results,
            order='relevance'  # 관련성 순 (인기순), 'time'으로 하면 최신순
        )
        
        response = request.execute()
        
        comments = []
        for item in response['items']:
            comment_data = item['snippet']['topLevelComment']['snippet']
            
            comment = {
                'author': comment_data['authorDisplayName'],
                'text': comment_data['textDisplay'],
                'like_count': comment_data['likeCount'],
                'published_at': comment_data['publishedAt'],
                'updated_at': comment_data.get('updatedAt', comment_data['publishedAt'])
            }
            comments.append(comment)
        
        print(f"댓글 {len(comments)}개 수집 완료")
        return comments
        
    except HttpError as e:
        print(f"YouTube API 오류: {e}")
        return []
    except Exception as e:
        print(f"댓글 수집 중 오류 발생: {e}")
        return []

def save_comments_to_file(comments, output_dir, video_title, video_id):
    """
    수집한 댓글을 텍스트 파일로 저장
    
    Args:
        comments (list): 댓글 데이터 리스트
        output_dir (str): 저장할 디렉토리
        video_title (str): 비디오 제목
        video_id (str): 비디오 ID
    """
    if not comments:
        print("저장할 댓글이 없습니다.")
        return
    
    try:
        # 파일명에 사용할 수 없는 문자들을 안전한 문자로 대체
        safe_title = str(video_title).replace('/', '_').replace('\\', '_').replace(':', '_').replace('*', '_').replace('?', '_').replace('"', '_').replace('<', '_').replace('>', '_').replace('|', '_').replace('#', '_')
        
        # 텍스트 파일로 저장
        txt_filename = f"{safe_title} [{video_id}].comments.txt"
        txt_filepath = os.path.join(output_dir, txt_filename)
        
        with open(txt_filepath, 'w', encoding='utf-8') as f:
            f.write(f"YouTube 댓글 모음 - {video_title}\n")
            f.write(f"비디오 ID: {video_id}\n")
            f.write(f"수집 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"총 댓글 수: {len(comments)}개\n")
            f.write("=" * 50 + "\n\n")
            
            for i, comment in enumerate(comments, 1):
                f.write(f"[{i}] {comment['author']}\n")
                f.write(f"좋아요: {comment['like_count']}개\n")
                f.write(f"작성일: {comment['published_at']}\n")
                f.write(f"내용: {comment['text']}\n")
                f.write("-" * 30 + "\n\n")
        
        print(f"댓글이 저장되었습니다: {txt_filepath}")
        
        # JSON 파일로도 저장 (데이터 분석용)
        json_filename = f"{safe_title} [{video_id}].comments.json"
        json_filepath = os.path.join(output_dir, json_filename)
        
        with open(json_filepath, 'w', encoding='utf-8') as f:
            json.dump({
                'video_title': video_title,
                'video_id': video_id,
                'collection_time': datetime.now().isoformat(),
                'total_comments': len(comments),
                'comments': comments
            }, f, ensure_ascii=False, indent=2)
        
        print(f"댓글 JSON 파일이 저장되었습니다: {json_filepath}")
        
    except Exception as e:
        print(f"댓글 저장 중 오류 발생: {e}")

def collect_and_save_comments(video_url, output_dir, video_title, max_results=30):
    """
    YouTube URL로부터 댓글을 수집하고 저장하는 통합 함수
    
    Args:
        video_url (str): YouTube URL
        output_dir (str): 저장할 디렉토리
        video_title (str): 비디오 제목
        max_results (int): 수집할 댓글 수
    """
    video_id = get_video_id_from_url(video_url)
    if not video_id:
        print("유효한 YouTube URL이 아닙니다.")
        return
    
    print(f"댓글 수집 중... (상위 {max_results}개)")
    comments = collect_youtube_comments(video_id, max_results)
    
    if comments:
        save_comments_to_file(comments, output_dir, video_title, video_id)
    else:
        print("댓글을 수집할 수 없습니다.")

if __name__ == '__main__':
    # 테스트용 코드
    test_url = "https://www.youtube.com/watch?v=qZfWf0BvhaQ"  # 예시 URL
    test_output_dir = "videos"
    test_title = "테스트 비디오"
    
    collect_and_save_comments(test_url, test_output_dir, test_title, 10)