# J-SCC 제주형 반도체 융합센터 홈페이지

정적 사이트(GitHub Pages). 한글은 루트, 영문은 `en/`. 스타일은 `assets/style.css`, 로고는 `assets/logo/`.

- 공지 추가: `news.html` / `en/news.html` 의 `<ul>` 맨 위에 `<li>` 한 줄 추가 (홈 `index.html` 의 알림 3건도 같이 갱신)
- 신청 폼: `apply.html` / `en/apply.html` 의 `GOOGLE_FORM_EMBED_URL` 을 Google Forms 삽입 주소로 교체
- 도메인 연결 후: 루트에 `CNAME` 파일(내용 `j-scc.org`) 추가, `build_site.py` 의 base_url 을 https://j-scc.org 로 재빌드
