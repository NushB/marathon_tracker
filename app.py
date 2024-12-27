import streamlit as st
import base64
import os
import requests
import time

FASTAPI_URL = "https://76ab-1-235-14-106.ngrok-free.app/find_clip"  # ngrok URL

# 로컬 이미지 파일을 Base64로 변환
def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

# 현재 경로 위치를 출력
current_path = os.getcwd()
print(f"현재 경로: {current_path}")


# 로컬 이미지 경로 설정
background_image_path = "/nushb/marathon_tracker/main/marathon_tracker/marathon.jpg"

# Base64로 변환한 이미지 가져오기
if os.path.exists(background_image_path):
    base64_image = get_base64_of_bin_file(background_image_path)
    page_bg_img = f"""
    <style>
    [data-testid="stAppViewContainer"] {{
        background: url("data:image/jpg;base64,{base64_image}");
        background-size: cover;
        background-position: center;
    }}
    [data-testid="stHeader"], [data-testid="stToolbar"] {{
        visibility: hidden;
        height: 0;
    }}
    h1, h2, h3, h4, h5, h6, p, label {{
        color: white;
        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.7);
    }}
    </style>
    """
    st.markdown(page_bg_img, unsafe_allow_html=True)
else:
    st.error(f"Background image not found at {background_image_path}")

# 제목 섹션
st.markdown("""
<h1 style='text-align: center;'>Marathon Tracker</h1>
""", unsafe_allow_html=True)
st.subheader("Find and track marathon runners by their bib numbers")
st.write("📹 Enter the bib number of the participant to view their video clip.")

# 사용자 입력 섹션
st.markdown("### Enter Bib Number:")
bib_number = st.text_input("Example: 12345", max_chars=10)

# 상태 메시지 변수
status_message = st.empty()  # 상태 메시지를 동적으로 업데이트하기 위한 공간
animation_placeholder = st.empty()  # 애니메이션 공간

# 버튼 및 결과 표시
if st.button("🔍 Search"):
    if bib_number:
        with st.spinner("Processing..."):
            # 로딩 애니메이션 및 메시지
            animation_placeholder.markdown("""
            <div style="display: flex; align-items: center; justify-content: center;">
                <svg xmlns="http://www.w3.org/2000/svg" style="margin: auto; background: transparent; display: block; shape-rendering: auto;" width="100px" height="100px" viewBox="0 0 100 100" preserveAspectRatio="xMidYMid">
                  <circle cx="50" cy="50" r="32" stroke-width="8" stroke="#ffffff" stroke-dasharray="50.26548245743669 50.26548245743669" fill="none" stroke-linecap="round">
                    <animateTransform attributeName="transform" type="rotate" repeatCount="indefinite" dur="1s" values="0 50 50;360 50 50" keyTimes="0;1"></animateTransform>
                  </circle>
                </svg>
            </div>
            """, unsafe_allow_html=True)
            status_message.markdown("<p style='text-align: center; font-size: 20px; color: white;'>러너분의 영상을 향해 달려가고 있어요!</p>", unsafe_allow_html=True)

            # 비디오 생성 요청
            response = requests.get(FASTAPI_URL, params={"bib_number": bib_number})
            time.sleep(3)  # 실제 로딩 시간 (테스트용)

            # 처리 완료
            animation_placeholder.empty()  # 애니메이션 제거
            if response.status_code == 200:
                clip_path = "/nushb/marathon_tracker/main/marathon_tracker/output/clip.mp4"
                with open(clip_path, "wb") as f:
                    f.write(response.content)
                # 비디오 출력
                st.video(clip_path)
                status_message.markdown("<p style='text-align: center; font-size: 20px; color: white;'>🎉 골인!</p>", unsafe_allow_html=True)
                # 다운로드 버튼 추가
                with open(clip_path, "rb") as f:
                    video_data = f.read()
                st.download_button(
                    label="⬇️ Download Video",
                    data=video_data,
                    file_name="clip.mp4",
                    mime="video/mp4"
                )
            else:
                status_message.markdown("<p style='text-align: center; font-size: 20px; color: red;'>❌ Bib number not found. Please try again.</p>", unsafe_allow_html=True)
    else:
        st.error("⚠️ Please enter a valid bib number!")

# 하단 주석
st.markdown("---")
st.markdown("**Developed by [Sport IT Korea]** | Marathon Tracker v1.0")
