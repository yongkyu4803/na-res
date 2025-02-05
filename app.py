import streamlit as st
import pandas as pd
import requests
from io import StringIO
from urllib.parse import quote

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
    </style>
""", unsafe_allow_html=True)

# 페이지 제목 및 서브타이틀 설정
st.markdown("<div class='title'>국회앞 식당정보 🍽️</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>맛있는 한 끼, 즐거운 하루 😊</div>", unsafe_allow_html=True)

# 구글 시트 기본 URL 구성
base_url = "https://docs.google.com/spreadsheets/d/"
sheet_id = "12xZfClkzATbByAZDYtM5KV2THzVvg2cV3KvVAZ621PQ"  # 실제 시트 ID를 입력하세요.
# 만약 시트ID에 한글 등 비ASCII 문자가 있다면, 퍼센트 인코딩 적용
encoded_sheet_id = quote(sheet_id, safe='')
sheet_url = f"{base_url}{encoded_sheet_id}/export?format=csv"

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
        return pd.DataFrame()  # 빈 데이터프레임 반환

df = load_data(sheet_url)

if df.empty:
    st.stop()  # 데이터가 없으면 앱 실행 중지

st.dataframe(df)

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

# 푸터 추가 (푸터 메시지는 영어, 이모지 추가)
st.markdown("---")
st.markdown("<p class='footer'>Made by GQ 💡</p>", unsafe_allow_html=True)
