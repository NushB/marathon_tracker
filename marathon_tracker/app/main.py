from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import subprocess
import os
import datetime

app = FastAPI()

# ChromeDriver 설정
def create_driver():
    options = Options()
    options.add_argument("--headless")  # 브라우저를 보이지 않게 실행
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# 비디오 시작 시간 (예: 12시 55분 00초)
VIDEO_START_TIME = datetime.datetime.strptime("12:01:36", "%H:%M:%S")

# 비디오 파일 경로
VIDEO_FILE = "../data/00004.MTS"
OUTPUT_CLIP = "../output/clip.mp4"

@app.get("/find_clip")
def find_clip(bib_number: str = Query(..., description="배번호를 입력하세요")):
    """
    배번호를 기준으로 통과 시간을 크롤링하고, 해당 비디오 클립을 반환합니다.
    """
    # Selenium으로 통과 시간 크롤링
    url = f"http://myresult.co.kr/92/{bib_number}"
    driver = create_driver()
    pass_time = None

    try:
        driver.get(url)

        # 명시적 대기: '도착' 텍스트가 포함된 div 요소가 나타날 때까지 대기
        wait = WebDriverWait(driver, 5)
        section_name_element = wait.until(
            EC.presence_of_element_located((By.XPATH, "//div[text()='도착']"))
        )

        # 통과 시간 가져오기
        pass_time_element = section_name_element.find_element(By.XPATH, "following-sibling::div")
        pass_time = pass_time_element.text.strip()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"크롤링 중 오류 발생: {str(e)}")
    finally:
        driver.quit()

    if not pass_time:
        raise HTTPException(status_code=404, detail="배번호에 해당하는 통과 시간을 찾을 수 없습니다.")

    # 통과 시간을 datetime으로 변환
    try:
        pass_time_obj = datetime.datetime.strptime(pass_time, "%H:%M:%S")
    except ValueError:
        raise HTTPException(status_code=400, detail="통과 시간 형식이 잘못되었습니다.")

    # 비디오 시간 계산
    video_time = (pass_time_obj - VIDEO_START_TIME).total_seconds()
    if video_time < 0:
        raise HTTPException(status_code=400, detail="통과 시간이 비디오 시작 시간보다 빠릅니다.")

    # 앞뒤 5초 계산
    start_time = max(0, video_time - 5)
    end_time = video_time + 5

    # FFmpeg 명령어로 비디오 클립 생성
    try:
        command = [
            "ffmpeg",
            "-y",
            "-i", VIDEO_FILE,
            "-ss", str(datetime.timedelta(seconds=start_time)),
            "-to", str(datetime.timedelta(seconds=end_time)),
            "-c:v", "copy",
            "-c:a", "copy",
            OUTPUT_CLIP
        ]
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=500, detail=f"FFmpeg 처리 중 오류 발생: {str(e)}")

    # 결과 클립 반환
    if not os.path.exists(OUTPUT_CLIP):
        raise HTTPException(status_code=500, detail="클립 생성에 실패했습니다.")
    return FileResponse(OUTPUT_CLIP, media_type="video/mp4", filename="clip.mp4")
