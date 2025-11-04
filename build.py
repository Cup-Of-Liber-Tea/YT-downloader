import PyInstaller.__main__
import os
import shutil

def build_exe():
    print("PyInstaller를 사용하여 .exe 빌드를 시작합니다...")

    # 빌드 전, 이전 빌드 흔적 제거
    if os.path.exists('build'):
        shutil.rmtree('build')
    if os.path.exists('dist'):
        shutil.rmtree('dist')
    
    spec_file_name = "1.spec" # 1.spec 파일 사용
    if os.path.exists(spec_file_name):
        os.remove(spec_file_name)

    pyinstaller_args = [
        '1.py', # 1.py 파일 사용
        '--noconfirm',
        '--onefile',
        '--name=1', # 실행 파일 이름 1로 설정
    ]

    # 현재 프로젝트에 필요 없는 옵션들은 제거합니다.
    # '--windowed' 옵션은 GUI 애플리케이션에 사용되므로, 이 프로젝트가 콘솔 애플리케이션인 경우 제거합니다.

    icon_path = 'app_icon.ico' # 현재 프로젝트에 app_icon.ico 파일이 없는 것으로 보입니다.
    if os.path.exists(icon_path):
        print(f"아이콘 파일 '{icon_path}'을(를) 빌드에 포함합니다.")
        pyinstaller_args.append(f'--icon={icon_path}')
    else:
        print(f"아이콘 파일 '{icon_path}'을(를) 찾을 수 없습니다. 아이콘 없이 빌드를 진행합니다.")

    PyInstaller.__main__.run(pyinstaller_args)

    print("빌드가 완료되었습니다. dist 폴더에서 실행 파일을 확인하세요.")

if __name__ == '__main__':
    build_exe()
