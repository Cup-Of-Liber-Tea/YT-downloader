import re

def parse_vtt_to_text(vtt_filepath):
    """
    VTT 파일에서 시간 정보와 태그를 제거하고 순수 텍스트만 추출합니다.
    """
    with open(vtt_filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # WEBVTT 헤더 제거
    content = re.sub(r'WEBVTT.*\n', '', content)
    # Kind: captions, Language: ko 등 헤더 제거
    content = re.sub(r'Kind:.*\n', '', content)
    content = re.sub(r'Language:.*\n', '', content)
    # 빈 줄 제거
    content = re.sub(r'^\s*$\n', '', content, flags=re.MULTILINE)
    # 시간 정보 (예: 00:00:08.040 --> 00:00:10.549) 제거
    content = re.sub(r'\d{2}:\d{2}:\d{2}\.\d{3} --> \d{2}:\d{2}:\d{2}\.\d{3}.*\n', '', content)
    # 태그 (<c>, align:start position:0% 등) 제거
    content = re.sub(r'<[^>]+>', '', content)
    # 연속된 빈 줄 하나로 줄이기
    content = re.sub(r'\n\s*\n', '\n', content)

    lines = [line.strip() for line in content.splitlines() if line.strip()]

    # 인접한 중복 라인 제거 (순서 유지)
    cleaned_lines = []
    if lines:
        cleaned_lines.append(lines[0])
        for i in range(1, len(lines)):
            if lines[i] != lines[i-1]:
                cleaned_lines.append(lines[i])

    return '\n'.join(cleaned_lines)

if __name__ == '__main__':
    # 테스트 코드 (실제 사용 시에는 1.py에서 호출)
    test_vtt_file = 'videos/커서(Cursor)+GPT로 17분 만에 랜딩 페이지 만들기 [qZfWf0BvhaQ].ko.vtt' # 예시 경로
    parsed_text = parse_vtt_to_text(test_vtt_file)
    print(parsed_text)

    # 파싱된 텍스트를 .txt 파일로 저장하는 예시
    output_text_file = test_vtt_file.replace('.ko.vtt', '.ko.txt')
    with open(output_text_file, 'w', encoding='utf-8') as f:
        f.write(parsed_text)
    print(f"Parsed text saved to: {output_text_file}")
