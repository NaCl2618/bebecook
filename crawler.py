import json
import time
import os
import xml.etree.ElementTree as ET
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

def get_diet_data():
    """
    베베쿡 사이트에서 식단 데이터를 가져와 JSON으로 저장합니다.
    """
    options = Options()
    options.add_argument("--headless")  # GitHub Actions 환경을 위해 헤드리스 모드 필수
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    
    # 드라이버 설정
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    
    # 결과 저장용 딕셔너리
    # key: category_id, value: { "title": "...", "data": [...] }
    result_data = {}
    
    # 베베쿡 카테고리 정보 (기존 index.html의 categoryData 참조)
    categories = {
        "1": "초기1 (4-5M)", "2": "초기2 (5-6M)", "76": "초기1.5 (5-6M)",
        "39": "중기1 (6-7M)", "3": "중기2 (7-9M)", "86": "오트이유식 (9-24M)",
        "9": "후기1 (9-10M)", "4": "후기2 (10-11M)", "35": "후기3 (11-12M)", "8": "완료기 (12-14M)",
        "6": "완료기밥 (12-14M)","96":"블랙아보카도한우페이스트(7-24M)",
        "84":"한우페이스트철분(6-60M)","99":"파테(7-12M)",
        "52":"오트 베이스죽(7-24M)","49":"트러블 한우페이스트(6-60M)",
        "10": "반찬준비기SET", "42": "영양찬찬국SET", "45": "소스찬국", 
        "37": "영양반찬", "25": "영양밥", "11": "영양국", "50": "올특찬",
        "94":"순 한우소보로","74":"한우소보로","88":"궁중배숙","57":"푸룬비책",
        "59":"베베 베이커리","46":"영양볶음밥","16":"올특찬국"
    }
    
    now = datetime.now()
    # 이번 달과 다음 달 데이터 수집
    target_months = [
        (now.year, now.month),
        (now.year if now.month < 12 else now.year + 1, now.month + 1 if now.month < 12 else 1)
    ]
    
    try:
        # API를 통한 데이터 수집 시도 (웹 드라이버를 사용하여 쿠키 등 우회)
        # 실제로는 웹 페이지에 접속 후 API endpoint에 직접 요청을 날리는 것이 효율적임
        driver.get("https://www.bebecook.com/page/service/schedule-nutri")
        time.sleep(2) # 페이지 로드 대기
        
        for step_seq, name in categories.items():
            print(f"[{name}] 데이터 수집 중...")
            result_data[step_seq] = {
                "name": name,
                "monthly": {}
            }
            
            for year, month in target_months:
                month_str = str(month).zfill(2)
                key = f"{year}-{month_str}"
                
                # API 호출 스크립트 실행 (텍스트로 받아와서 파이썬에서 파싱)
                script = f"""
                return fetch('/api/schedule/list', {{
                    method: 'POST',
                    headers: {{ 
                        'Content-Type': 'application/json',
                        'X-Requested-With': 'XMLHttpRequest'
                    }},
                    body: JSON.stringify({{
                        stepSeq: {step_seq},
                        year: {year},
                        month: {month}
                    }})
                }}).then(res => res.text());
                """
                
                try:
                    response_text = driver.execute_script(script)
                    menu_list = []
                    
                    if response_text.strip().startswith('<'):
                        # XML 파싱
                        root = ET.fromstring(response_text)
                        # <List><item><date>년</date><date>월</date><date>일</date><menuList><menuList><name>메뉴명</name>...</menuList></menuList></item></List> 구조
                        for item in root.findall('.//item'):
                            # date 태그 3개를 조합하여 날짜 생성 (년, 월, 일)
                            date_elements = item.findall('date')
                            if len(date_elements) >= 3:
                                year = date_elements[0].text
                                month = date_elements[1].text.zfill(2)
                                day = date_elements[2].text.zfill(2)
                                date_str = f"{year}-{month}-{day}"
                            else:
                                date_str = ""
                            
                            # menuList 내부의 menuList에서 메뉴명 추출
                            menu_items = item.findall('.//menuList/menuList')
                            for menu_item in menu_items:
                                name_elem = menu_item.find('name')
                                if name_elem is not None and name_elem.text:
                                    menu_list.append({
                                        "menuNm": name_elem.text,
                                        "day": date_str
                                    })
                    else:
                        # JSON 파싱
                        data = json.loads(response_text)
                        menu_list = data.get("menuList", [])
                    
                    result_data[step_seq]["monthly"][key] = menu_list
                    print(f"  - {key} 완료 ({len(menu_list)}건)")
                except Exception as e:
                    print(f"  - {key} 실패: {e}")
                
                time.sleep(0.5) # 간격 조절
        
        # 데이터 폴더 생성
        if not os.path.exists('data'):
            os.makedirs('data')
            
        # JSON 저장
        with open('data/diet_data.json', 'w', encoding='utf-8') as f:
            json.dump(result_data, f, ensure_ascii=False, indent=2)
            
        print("\n모든 데이터 수집이 완료되었습니다. (data/diet_data.json 저장됨)")
        
    finally:
        driver.quit()

if __name__ == "__main__":
    get_diet_data()
