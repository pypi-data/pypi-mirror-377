import httpx
from defusedxml.ElementTree import fromstring
from fastmcp import FastMCP
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time

# You can also add instructions for how to interact with the server
mcp = FastMCP(
    name="Devflux Stock MCP",
    instructions="""
        주시 시세 정보 서버
        Call gwt_stock(code: str): 코드별로 시세 정보 확인
        Call search_news(search: str): google 한국 뉴스 정보 
        Call daum_my_stock(my_stock_category: str): daum 로그인하여 특정 화면 카테고리 선택하여 정보 조회
    """,
)

# 주식
@mcp.tool
async def get_stock(code: str):
    """
    code: 종목 코드, 예: 005930
    """
    url = f"https://polling.finance.naver.com/api/realtime?query=SERVICE_ITEM:{code}"

    async with httpx.AsyncClient() as client:
        resp = await client.get(url)
        resp.encoding = 'euc-kr'  # 또는 'cp949'
        data_text = resp.text
        data = json.loads(data_text)

    # 필요하면 요약 형태로 변환 가능
    if "result" in data and "areas" in data["result"]:
        stock_data = data["result"]["areas"][0]["datas"][0]
        summary = {
            "ticker_code": stock_data.get("cd"),            # 종목코드
            "stock_name": stock_data.get("nm"),             # 종목명
            "current_price": stock_data.get("nv"),          # 현재가
            "previous_close": stock_data.get("sv"),         # 전일종가
            "price_change": stock_data.get("cv"),           # 변동폭
            "percent_change": stock_data.get("cr"),         # 변동률(%)
            "rate_flag": stock_data.get("rf"),              # 등락구분코드
            "market_type": stock_data.get("mt"),            # 시장유형코드
            "market_status": stock_data.get("ms"),          # 시장상태(Open/Closed)
            "trading_status": stock_data.get("tyn"),        # 거래정지 여부
            "previous_closing_price": stock_data.get("pcv"), # 전일종가 (실제 기록)
            "opening_price": stock_data.get("ov"),          # 시가
            "highest_price": stock_data.get("hv"),          # 고가
            "lowest_price": stock_data.get("lv"),           # 저가
            "upper_limit": stock_data.get("ul"),             # 52주 최고가 혹은 상한가
            "lower_limit": stock_data.get("ll"),             # 52주 최저가 혹은 하한가
            "trading_volume": stock_data.get("aq"),         # 거래량
            "trading_value": stock_data.get("aa"),          # 거래대금
            "net_asset_value": stock_data.get("nav"),       # 순자산가치(NAV) - null일 수 있음
            "kaeps": stock_data.get("keps"),                 # K-EPS (추정 주당순이익)
            "eps": stock_data.get("eps"),                    # EPS (주당순이익)
            "bps": stock_data.get("bps"),                    # BPS (주당순자산)
            "consensus_eps": stock_data.get("cnsEps"),      # 컨센서스 EPS
            "dividend": stock_data.get("dv"),                # 배당금
            "next_over_market_price_info": stock_data.get("nxtOverMarketPriceInfo") # 시간외 단일가 정보 및 상태
        }

        return summary

    return data

# 뉴스
@mcp.tool
async def search_news(search: str):
    """
    search: 검색어, 예: 경제, 주도주, 매매기법, 삼성전자주가
    """

    url =f"https://news.google.com/rss/search?q={search}&hl=ko&gl=KR&ceid=KR:ko";

    async with httpx.AsyncClient() as client:
        resp = await client.get(url)
        resp.encoding = 'utf-8'  # 대부분 Google RSS는 UTF-8
        xml_text = resp.text

    root = fromstring(xml_text)

    news_list = []
    # RSS -> channel -> item
    for item in root.findall('./channel/item'):
        title = item.find('title').text if item.find('title') is not None else ''
        link = item.find('link').text if item.find('link') is not None else ''
        image = item.find('image').text if item.find('image') is not None else ''
        pub_date = item.find('pubDate').text if item.find('pubDate') is not None else ''
        news_list.append({
            'title': title,
            'link': link,
            'image': image,
            'pubDate': pub_date
        })

    return news_list


# Daum
async def daum_login(driver: webdriver.Chrome):
    # 마이페이지 접속
    driver.get("https://finance.daum.net/my")
    time.sleep(3)  # 페이지 로딩 대기

    # 로그인 여부 확인
    # 예시: 로그인 버튼이 존재하면 로그인 안된 상태
    login_buttons = driver.find_elements(By.CLASS_NAME, 'btn_login')  # 로그인 버튼 클래스 확인 필요

    if login_buttons:
        print("로그인이 필요합니다. 로그인 페이지를 표시합니다.")
        # 사용자가 직접 로그인하도록 브라우저를 열어둠

        # 로그인 버튼 클릭해서 로그인 페이지 열기
        login_buttons[0].click()

        input("로그인 후 Enter를 눌러 계속 진행하세요...")
    else:
        print("로그인 상태입니다. 데이터 처리 시작.")

    time.sleep(60)  # 페이지 로딩 대기



@mcp.tool
async def daum_my_stock(my_stock_category: str):
    """
    Daum 로그인 하여 현재 보유 중인 종목 정보 가져오기
    my_stock_category: 화면 카테고리 선택, 예: 보유주, 관심주, 급등주
    """

    chrome_options = Options()
    chrome_options.binary_location = r"C:\Program Files\Google\Chrome\Application\chrome.exe"  # 설치 경로 확인

    # Chrome 드라이버 설정
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=chrome_options
    )
    await daum_login(driver)

    # 페이지 소스 가져오기
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')

    # 테이블 데이터 추출 예시
    box = soup.find('div', {'class': 'box_contents'})
    table = box.find('table')
    data = []
    if table:
        # 헤더 추출
        headers = [th.get_text(strip=True) for th in table.find('thead').find_all('th')] if table.find('thead') else []
        
        # 데이터 추출
        for row in table.find('tbody').find_all('tr') if table.find('tbody') else table.find_all('tr'):
            cols = row.find_all('td')
            if cols:
                row_data = {}
                for i, col in enumerate(cols):
                    if i < len(headers):
                        row_data[headers[i]] = col.get_text(strip=True)
                    else:
                        # 헤더보다 많은 열이 있을 경우, 인덱스로 추가
                        row_data[f"col_{i+1}"] = col.get_text(strip=True)
                data.append(row_data)

    result = {"category": my_stock_category, "data": data}
    driver.quit()
    return result

# 서버 실행
if __name__ == "__main__":
    mcp.run()
