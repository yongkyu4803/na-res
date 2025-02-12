import streamlit as st
import pandas as pd
import requests
from io import StringIO
from urllib.parse import quote
from feedback import SheetManager
import time

# CSS 스타일 추가 (폰트, 정렬 등)
st.markdown("""
    <style>
    .title {
        text-align: center;
        font-size: 3em;
        font-weight: bold;
        margin-bottom: 0;
    }
    .subtitle {
        text-align: center;
        font-size: 1.2em;
        color: #555;
        margin-top: 0;
    }
    .footer {
        text-align: center;
        font-size: 0.9em;
        color: #888;
    }
    /* 테이블 스타일 추가 */
    table {
        font-size: 0.9rem;  /* 테이블 내용 글자 크기를 0.9rem으로 변경 */
    }
    th {
        font-size: 1em;  /* 헤더는 그대로 유지 */
        text-align: left;  /* 헤더 왼쪽 정렬 */
    }
    /* 링크 스타일 추가 */
    a {
        text-decoration: none;  /* 링크 밑줄 제거 */
    }
    </style>
""", unsafe_allow_html=True)

# 페이지 제목 및 서브타이틀 설정
st.markdown("<div class='title'>국회앞 식당정보 🍽️</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>맛있는 한 끼, 즐거운 하루 😊</div>", unsafe_allow_html=True)

# 구글 시트 URL 구성 부분 수정
base_url = "https://docs.google.com/spreadsheets/d/"
sheet_id = "12xZfClkzATbByAZDYtM5KV2THzVvg2cV3KvVAZ621PQ"
encoded_sheet_id = quote(sheet_id, safe='')
restaurants_url = f"{base_url}{encoded_sheet_id}/export?format=csv"
feedback_url = f"{base_url}{encoded_sheet_id}/export?format=csv&gid=406210046"  # gid=1은 두 번째 시트의 ID입니다

@st.cache_data(show_spinner=False)
def load_data(url):
    try:
        # requests로 데이터 요청
        response = requests.get(url)
        # 응답 인코딩을 명시적으로 UTF-8로 지정
        response.encoding = 'utf-8'
        data = StringIO(response.text)
        df = pd.read_csv(data)
        return df
    except Exception as e:
        st.error("데이터를 불러오는 데 실패했습니다.")
        st.error(e)
        return pd.DataFrame()

df = load_data(restaurants_url)

if df.empty:
    st.stop()  # 데이터가 없으면 앱 실행 중지

# 데이터프레임을 HTML 형식으로 변환하여 링크 추가
if not df.empty:
    # 상호명과 장소에 링크 추가
    df['상호명'] = df.apply(
        lambda row: f"<a href='{row['링크']}'>{row['상호명']}</a>" if pd.notna(row['링크']) and row['링크'] else row['상호명'],
        axis=1
    )
    df['장소'] = df.apply(
        lambda row: f"<a href='{row['링크']}'>{row['장소']}</a>" if pd.notna(row['링크']) and row['링크'] else row['장소'],
        axis=1
    )
    
    # '링크' 열을 제외하고 표시
    display_columns = [col for col in df.columns if col != '링크']
    st.markdown(df[display_columns].to_html(escape=False, index=False), unsafe_allow_html=True)

# 검색 기능 구현: 모든 열에서 검색어가 포함된 행 반환 (부분 일치)
# (기능은 그대로 유지)
search_term = st.text_input("검색어를 입력하세요 🔍")

if search_term:
    # 모든 열의 값을 문자열로 변환한 후, 검색어가 포함되어 있는지 확인
    mask = df.apply(
        lambda row: row.astype(str).str.contains(search_term, case=False, na=False).any(),
        axis=1
    )
    filtered_df = df[mask]
    
    st.write(f"**검색 결과 ({len(filtered_df)}건):**")
    st.dataframe(filtered_df)
else:
    st.write("")

# 피드백 섹션
st.markdown("---")
st.markdown("### 📝 피드백을 남겨주세요!")

# SheetManager 인스턴스 생성
sheet_manager = SheetManager()

with st.form("feedback_form", clear_on_submit=True):
    col1, col2 = st.columns(2)
    
    with col1:
        rating = st.slider("전반적인 만족도", 1, 5, 3)
        user_name = st.text_input("이름 (선택사항)")
    
    with col2:
        feedback_type = st.selectbox(
            "피드백 유형",
            ["일반 의견", "새로운 식당 제보", "정보 수정 요청", "기능 개선 제안"]
        )
    
    feedback_text = st.text_area("상세 의견을 적어주세요")
    
    submitted = st.form_submit_button("피드백 제출")
    
    if submitted and feedback_text:
        success, message = sheet_manager.submit_feedback(
            user_name,
            rating,
            feedback_type,
            feedback_text
        )
        if success:
            st.success(message)
            time.sleep(3)  # 3초 동안 성공 메시지 표시
            st.rerun()
        else:
            st.error(message)
    elif submitted:
        st.warning("피드백 내용을 입력해주세요.")

# 푸터 추가 (푸터 메시지는 영어, 이모지 추가)
st.markdown("---")
st.markdown("<p class='footer'>Made by GQ 💡</p>", unsafe_allow_html=True)
