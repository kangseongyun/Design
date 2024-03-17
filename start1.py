import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.graph_objects as go
from PIL import Image
import os
import matplotlib.pyplot as plt
from plotly.subplots import make_subplots

# with st.expander("**전기요금제**(2024.01.01 기준):"):
#     select_option5 = st.selectbox('대분류:', ['일반용전력(갑)Ⅰ', '일반용전력(갑)Ⅱ', '일반용전력(을)', '산업용전력(갑)Ⅰ', '산업용전력(갑)Ⅱ','산업용전력(을)','교육용전력(갑)','교육용전력(을)','교육용전력(갑)'], key='select2')
#     select_option6 = st.selectbox('중분류:', ['저압', '고압A(선택Ⅰ)', '고압A(선택Ⅱ)', '고압B(선택Ⅰ)', '고압B(선택Ⅱ)'], key='select3')
#     # HTML을 사용한 글자 크기 조절
#     st.markdown("""
#     <style>
#     .small-font {
#         font-size:12px !important;
#     }
#     </style>
#     <div class='small-font'>전력량요금만 입력했음.</div>
#     """, unsafe_allow_html=True)
plt.rcParams['axes.unicode_minus'] = False
plt.rc('font', family= 'Malgun Gothic')


st.set_page_config(
    page_title="건물탄소발자국 플래너",
    page_icon=":bar_chart:",
    layout='wide'
)
os.chdir(os.path.dirname(__file__))
image_path = 'image/star.jpg'  # 수정된 부분
# 이미지 로드
image = Image.open(image_path)
# 사이드바에 이미지 표시
st.sidebar.image(image, caption='당신의 작은 고동이 큰 파란으로 이어지길...')
st.sidebar.write("당신의 작은 고동이 큰 파란으로 이어지길...")

# 사이드바 설정
with st.sidebar:
    selected = st.radio("Menu", ["플래너 입력창", "용도별 패턴 분석", "탄소포인트 추천"])
    menu_options = ["플래너 입력창", "용도별 패턴 분석", "탄소포인트 추천"]


if selected == "플래너 입력창":
    csv_file = st.file_uploader('CSV 파일 업로드:', type=['csv'])


    currentDateTime = datetime.now()
    currentMonth = currentDateTime.month


    # 현재 월을 기반으로 계절 결정 함수
    def get_season(month):
        if month in [3, 4, 5]:
            return '봄'
        elif month in [6, 7, 8]:
            return '여름'
        elif month in [9, 10, 11]:
            return '가을'
        else:  # 12, 1, 2 겨울
            return '겨울'


    current_season = get_season(currentMonth)
    st.write(f"현재 계절은 {current_season}입니다.")
    if csv_file is not None:
        # 파일 업로드 후 데이터프레임 생성
        csv_edit = pd.read_csv(csv_file)
        csv_edit = csv_edit.set_index(csv_edit.columns[0])


        def Combine(season, file):
            season_months = {'봄': [3, 4, 5], '여름': [6, 7, 8], '가을': [9, 10, 11], '겨울': [12, 1, 2]}
            months = season_months[season]
            file.index = pd.to_datetime(file.index)
            filtered = file[file.index.month.isin(months)]
            filtered.index = filtered.index.hour
            filtered[filtered.columns[0]] = pd.to_numeric(filtered[filtered.columns[0]], errors='coerce')
            result = filtered.groupby(filtered.index)[filtered.columns[0]].mean()
            return result


        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.05)

        # 현재 계절에 해당하는 데이터 처리
        data = Combine(current_season, csv_edit)
        fig.add_trace(go.Scatter(x=data.index, y=data, mode='lines+markers', name=current_season), row=1, col=1)
        fig.update_xaxes(range=[0, 24])  # x축 범위 설정 (예: 0에서 24까지)

        # 최저점 구하기
        min_value = min(data)
        min_index = data.idxmin()  # 최소값의 인덱스

        # 윗부분 색으로 칠하기 (다른 색상)
        fig.add_trace(go.Scatter(x=data.index, y=data.where(data > min_value).fillna(min_value), mode='lines',
                                 line=dict(color='lightblue'), fill='tozeroy', name='첨두부하'), row=1, col=1)

        # 전체적인 한계를 나타내는 부분 색으로 칠하기
        fig.add_trace(go.Scatter(x=data.index, y=[min(data)] * len(data), mode='lines', fill='tozeroy',
                                 fillcolor='lightcoral', line=dict(color='red'), name='기저부하'), row=1, col=1)
        fig.update_xaxes(tickmode='array', tickvals=data.index)
        st.plotly_chart(fig, use_container_width=True)
    left_column, right_column = st.columns([1, 1])  # 비율을 조정하여 좌우 크기를 변경할 수 있습니다.

    # 파일 업로더 설정
    with left_column:
        st.header("좌측 열")
        if csv_file is not None:
            # 사용자로부터 조정하고 싶은 시간대 선택 받기
            hours_to_adjust = st.multiselect('조정할 시간대를 선택하세요 (0-23시):', options=range(24), default=[8, 12])
            hours_to_adjust.sort()  # 시간대를 순서대로 정렬합니다.

            # 시간대별 증감값 입력 부분
            adjustments = {}
            with st.form("adjustments"):
                st.write("선택된 시간대별 증감값 입력:")
                for hour in hours_to_adjust:
                    adjustments[hour] = st.number_input(f"{hour}시 증감값:", value=0.0, key=hour, format="%.2f")
                submitted = st.form_submit_button("적용")

        with right_column:
            st.header("우측 열")
            if csv_file is not None and submitted:
                original_data = data.copy()  # 증감값 적용 전 데이터의 복사본

                # 증감값 적용
                for hour, adjustment in adjustments.items():
                    if hour in data.index:
                        data.at[hour] += adjustment

                    # 업데이트된 데이터와 원본 데이터를 포함한 그래프 생성
                fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.05)

                fig.add_trace(go.Scatter(x=original_data.index, y=original_data, mode='lines+markers', name='기존 데이터'), row=1, col=1)
                fig.update_xaxes(tickmode='array', tickvals=data.index)

                    # 수정된 데이터 플롯
                fig.add_trace(go.Scatter(x=data.index, y=data, mode='lines+markers', name='조정된 데이터', line=dict(color='red')),row=1, col=1)

                    # x축 범위와 tick 설정
                fig.update_layout(legend_title_text='데이터 유형')
                st.plotly_chart(fig, use_container_width=True)

if selected == "용도별 패턴 분석":

    # st.set_page_config(layout="wide")
    st.title('포인트 좀 챙겨줄까?')



    # 특수 이모티콘 삽입 예시
    # emoji: https://streamlit-emoji-shortcodes-streamlit-app-gwckff.streamlit.app/
    st.title('가이드라인 사용법 :sunglasses:')
    left_column, right_column = st.columns([2, 1])  # 비율을 조정하여 좌우 크기를 변경할 수 있습니다.
    filename = 'start2.py'
    with open(filename, 'r', encoding='utf-8') as file:  # 'utf-8'로 인코딩 지정
        exec(file.read())

    # 좌측 열에 컨텐츠를 추가합니다.
    with left_column:
        st.header("좌측 열")
        st.write("이 곳은 좌측 열입니다.")
        fig = go.Figure()

        # 각 계절별로 라인 추가
        fig.add_trace(go.Scatter(x=df1['Hour'], y=df1['봄'], mode='lines+markers',
                                 name='봄', marker=dict(symbol='circle', size=10), line=dict(color='blue', width=2)))

        fig.add_trace(go.Scatter(x=df1['Hour'], y=df1['여름'], mode='lines+markers',
                                 name='여름', marker=dict(symbol='x', size=10), line=dict(color='orange', width=2)))

        fig.add_trace(go.Scatter(x=df1['Hour'], y=df1['가을'], mode='lines+markers',
                                 name='가을', marker=dict(symbol='square', size=10), line=dict(color='green', width=2)))

        fig.add_trace(go.Scatter(x=df1['Hour'], y=df1['겨울'], mode='lines+markers',
                                 name='겨울', marker=dict(symbol='triangle-up', size=10),
                                 line=dict(color='red', width=2)))

        # 그래프 제목 및 축 레이블 설정
        fig.update_layout(
            title='계절별 데이터 비교',
            xaxis_title='Hour',
            yaxis_title='Values',
            legend_title='계절'
        )

        # Streamlit에서 그래프 표시
        st.plotly_chart(fig, use_container_width=True)

    # 우측 열을 다시 두 개의 행으로 나눕니다.
    with right_column:
        # 우측 열의 상단 부분에 컨텐츠를 추가합니다.
        st.subheader("우측 상단")
        st.write("이 곳은 우측 열의 상단 부분입니다.")

if selected == "탄소포인트 추천":
    st.title('포인트 좀 챙겨줄까?')
    backgroundColor = "#000000"
    import streamlit as st
    from streamlit.components.v1 import html

    # HTML 및 JavaScript 코드를 정의합니다.
    js = """
    <button onclick="getLocation()">Get My Location</button>

    <script>
    function getLocation() {
      if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(showPosition, showError);
      } else { 
        alert("Geolocation is not supported by this browser.");
      }
    }

    function showPosition(position) {
      // 위치 정보를 가져오고, Streamlit 앱의 URL에 파라미터로 추가합니다.
      const url = new URL(window.location.href);
      const params = new URLSearchParams(window.location.search);
      params.set('lat', position.coords.latitude);
      params.set('lon', position.coords.longitude);
      window.history.replaceState({}, '', `${location.pathname}?${params}`);
      window.location.reload(); // 페이지를 새로고침하여 파라미터를 전달합니다.
    }

    function showError(error) {
      switch(error.code) {
        case error.PERMISSION_DENIED:
          alert("User denied the request for Geolocation.");
          break;
        case error.POSITION_UNAVAILABLE:
          alert("Location information is unavailable.");
          break;
        case error.TIMEOUT:
          alert("The request to get user location timed out.");
          break;
        case error.UNKNOWN_ERROR:
          alert("An unknown error occurred.");
          break;
      }
    }
    </script>
    """

    # Streamlit 앱에 HTML과 JavaScript 코드를 삽입합니다.
    html(js)

    # URL에서 위치 파라미터를 가져옵니다.
    params = st.query_params
    lat = params.get("lat", [None])[0]
    lon = params.get("lon", [None])[0]

    if lat and lon:
        st.write(f"Latitude: {lat}, Longitude: {lon}")
    else:
        st.write("Click the button to get your location.")




