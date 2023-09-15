import os

# git config --global core.autocrlf true

# 특정 경로 내 존재하는 디렉토리 및 파일 리스트 검색

file_path = './ui'

for file in os.listdir(file_path):
    print(file)

# 추가적으로 모든 하위 디렉토리 구조를 전부 검색
# 출력 형식 : 튜플 - (경로, 경로 내 디렉토리 리스트, 경로 내 파일 리스트)
count = 0

for file in os.walk(file_path):
    print(type(file))
    print(file)
    count += 1

print(count)

for (path, dir, file) in os.walk(file_path):
    print("path:", path)
    print("dir:", dir)
    print("file:", file)
    print("------------------------")