# J-SCC 제주형 반도체 융합센터 홈페이지

정적 사이트(GitHub Pages). 한글은 루트, 영문은 `en/`. 스타일은 `assets/style.css`, 로고는 `assets/logo/`.

- 공지 추가: `news.html` / `en/news.html` 의 `<ul>` 맨 위에 `<li>` 한 줄 추가 (홈 `index.html` 의 알림 3건도 같이 갱신)
- 신청 폼: `apply.html` / `en/apply.html` 의 `GOOGLE_FORM_EMBED_URL` 을 Google Forms 삽입 주소로 교체
- 도메인 연결 후: 루트에 `CNAME` 파일(내용 `j-scc.org`) 추가, `build_site.py` 의 base_url 을 https://j-scc.org 로 재빌드

## 공지 올리기 (담당자용)
1. 저장소 **Issues → New issue → 「공지 등록」** 양식 선택
2. 제목(`[공지] ` 뒤에 이어 쓰기)·날짜·분류·(선택) 영문 제목·본문·링크 입력 → Submit
3. 1~2분 뒤 홈페이지 알림마당과 홈 알림 3건에 자동 반영 (`.github/workflows/notices.yml` → `scripts/build_notices.py`)
4. 수정은 이슈 편집, 내리기는 이슈 닫기. 본문을 쓰면 `news/<번호>.html` 상세 페이지가 생기고, 외부 링크를 넣으면 목록에서 그 주소로 바로 연결됩니다.
