# -*- coding: utf-8 -*-
"""GitHub 이슈(라벨 '공지') → 알림마당 목록·홈 알림 3건·공지 상세 페이지 생성.

- 목록 삽입 자리: index.html / news.html / en/index.html / en/news.html 의
  <!--NOTICES:start:3--> 또는 <!--NOTICES:start:all--> ... <!--NOTICES:end--> 사이
- 상세 페이지: news/<이슈번호>.html, en/news/<이슈번호>.html (본문이 있을 때만)
- 실행: GITHUB_TOKEN, GITHUB_REPOSITORY 환경변수 (Actions 기본 제공)
- 로컬 테스트: python scripts/build_notices.py --sample sample.json --out /tmp/site
"""
import io, os, re, sys, json, html, shutil, argparse, datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIELDS = {"날짜": "date", "분류": "category", "영문 제목 (선택)": "title_en", "본문 (선택)": "body_ko",
          "영문 본문 (선택)": "body_en", "외부 링크 (선택)": "link"}
CAT_EN = {"공지": "NOTICE", "모집": "OPEN", "행사": "EVENT", "소식": "UPDATE", "자료": "RESOURCE"}

def parse_form(body):
    out = {}
    for m in re.finditer(r"^### (.+?)\s*\n\n(.*?)(?=\n### |\Z)", body or "", re.S | re.M):
        key = FIELDS.get(m.group(1).strip())
        if not key: continue
        val = m.group(2).strip()
        if val == "_No response_": val = ""
        out[key] = val
    return out

def fetch_issues():
    import requests
    repo = os.environ["GITHUB_REPOSITORY"]; tok = os.environ["GITHUB_TOKEN"]
    items, page = [], 1
    while True:
        r = requests.get(f"https://api.github.com/repos/{repo}/issues",
                         params={"state": "open", "labels": "공지", "per_page": 100, "page": page},
                         headers={"Authorization": f"Bearer {tok}", "Accept": "application/vnd.github+json"}, timeout=30)
        r.raise_for_status(); batch = r.json()
        items += [i for i in batch if "pull_request" not in i]
        if len(batch) < 100: break
        page += 1
    return items

def normalize(issues):
    out = []
    for i in issues:
        f = parse_form(i.get("body", ""))
        title = re.sub(r"^\[공지\]\s*", "", i["title"]).strip()
        date = f.get("date") or i["created_at"][:10]
        try: datetime.date.fromisoformat(date)
        except ValueError: date = i["created_at"][:10]
        out.append({"n": i["number"], "title": title, "title_en": f.get("title_en") or title,
                    "date": date, "category": f.get("category") or "공지",
                    "body_ko": f.get("body_ko", ""), "body_en": f.get("body_en", "") or f.get("body_ko", ""),
                    "link": f.get("link", "")})
    out.sort(key=lambda x: (x["date"], x["n"]), reverse=True)
    return out

IMG_MD = re.compile(r"!\[([^\]]*)\]\((https?://[^)\s]+)\)")
IMG_HTML = re.compile(r'(<img[^>]+src=")(https?://[^"]+)(")', re.I)

def localize_images(text, issue_no, root):
    """이슈 본문의 이미지(드래그 업로드 포함)를 news/img/ 에 저장하고 상대 경로로 바꾼다. 반환: (KO용 텍스트, EN용 텍스트)"""
    import requests
    img_dir = os.path.join(root, "news", "img"); os.makedirs(img_dir, exist_ok=True)
    tok = os.environ.get("GITHUB_TOKEN", "")
    cache, counter = {}, [0]
    def fetch(url):
        if url in cache: return cache[url]
        counter[0] += 1
        try:
            h = {"Authorization": f"Bearer {tok}"} if tok and "github" in url else {}
            r = requests.get(url, headers=h, timeout=60, allow_redirects=True); r.raise_for_status()
            ct = r.headers.get("content-type", "").split(";")[0].strip()
            ext = {"image/png": ".png", "image/jpeg": ".jpg", "image/gif": ".gif", "image/webp": ".webp", "image/svg+xml": ".svg"}.get(ct)
            if not ext:
                m = re.search(r"\.(png|jpe?g|gif|webp)(?:$|\?)", url, re.I); ext = "." + (m.group(1).lower().replace("jpeg", "jpg") if m else "png")
            name = f"{issue_no}-{counter[0]}{ext}"
            io.open(os.path.join(img_dir, name), "wb").write(r.content)
            cache[url] = name
        except Exception as e:
            print("image skipped:", url, e); cache[url] = None
        return cache[url]
    def sub_md(m, prefix):
        name = fetch(m.group(2)); return f"![{m.group(1)}]({prefix}{name})" if name else m.group(0)
    def sub_html(m, prefix):
        name = fetch(m.group(2)); return f'{m.group(1)}{prefix}{name}{m.group(3)}' if name else m.group(0)
    ko = IMG_HTML.sub(lambda m: sub_html(m, "img/"), IMG_MD.sub(lambda m: sub_md(m, "img/"), text))
    en = IMG_HTML.sub(lambda m: sub_html(m, "../../news/img/"), IMG_MD.sub(lambda m: sub_md(m, "../../news/img/"), text))
    return ko, en

def md(text):
    try:
        import markdown
        return markdown.markdown(text, extensions=["extra", "nl2br"])
    except ImportError:
        paras = [f"<p>{html.escape(p).replace(chr(10), '<br>')}</p>" for p in re.split(r"\n\s*\n", text.strip()) if p.strip()]
        return "\n".join(paras)

def item_html(n, lang, in_en_dir, at_root):
    title = n["title"] if lang == "ko" else n["title_en"]
    cat = n["category"] if lang == "ko" else CAT_EN.get(n["category"], "NOTICE")
    has_page = bool(n["body_ko"].strip())
    if n["link"]:
        href = n["link"]; extra = ' target="_blank" rel="noopener"'
    elif has_page:
        href = ("" if in_en_dir else "") + f"news/{n['n']}.html"; extra = ""
    else:
        href = None
    t = html.escape(title)
    inner = f'<a href="{href}"{extra}>{t}</a>' if href else t
    return f'<li><span class="d">{n["date"]}</span><span>{inner}</span><span class="c">{html.escape(cat)}</span></li>'

def inject(path, notices, lang, in_en_dir):
    s = io.open(path, encoding="utf-8").read()
    m = re.search(r"<!--NOTICES:start:(\w+)-->.*?<!--NOTICES:end-->", s, re.S)
    if not m: return False
    limit = m.group(1)
    sel = notices if limit == "all" else notices[:int(limit)]
    if sel:
        lis = "\n      ".join(item_html(n, lang, in_en_dir, True) for n in sel)
    else:
        lis = '<li><span class="d">—</span><span>' + ("등록된 공지가 없습니다." if lang == "ko" else "No notices yet.") + '</span><span class="c"></span></li>'
    new = f"<!--NOTICES:start:{limit}--><ul>\n      {lis}\n    </ul><!--NOTICES:end-->"
    s = s[:m.start()] + new + s[m.end():]
    io.open(path, "w", encoding="utf-8", newline="\n").write(s)
    return True

def shell_from(news_path):
    """news.html 에서 <main ...> 앞뒤를 템플릿으로 사용."""
    s = io.open(news_path, encoding="utf-8").read()
    pre, rest = s.split("<main", 1)
    _, post = rest.split("</main>", 1)
    return pre, post

def write_article(n, lang, out_dir, pre, post, in_en_dir):
    title = n["title"] if lang == "ko" else n["title_en"]
    body = n["body_ko"] if lang == "ko" else n["body_en"]
    cat = n["category"] if lang == "ko" else CAT_EN.get(n["category"], "NOTICE")
    back = ("../news.html", "알림마당으로") if lang == "ko" else ("../news.html", "Back to News")
    # 상세 페이지는 한 단계 아래 폴더라 자산 경로 보정
    pre2 = pre.replace('href="assets/', 'href="../assets/').replace('href="favicon.ico"', 'href="../favicon.ico"').replace('href="../assets/', 'href="../assets/')
    if in_en_dir:
        pre2 = pre2.replace('href="../assets/', 'href="../../assets/').replace('href="../favicon.ico"', 'href="../../favicon.ico"')
    # 헤더 내비 링크 보정 (상대경로 한 단계 위로): 먼저 ../x.html → ../../x.html, 그다음 x.html → ../x.html
    pre2 = re.sub(r'href="\.\./([\w\-]+\.html)"', r'href="../../\1"', pre2)
    pre2 = re.sub(r'href="(?!https?://|\.\./|#|mailto:)([\w\-]+\.html)"', r'href="../\1"', pre2)
    pre2 = re.sub(r'href="en/([\w\-]+\.html)"', r'href="../en/\1"', pre2)
    pre2 = re.sub(r"<title>.*?</title>", f"<title>{html.escape(title)} · J-SCC</title>", pre2, flags=re.S)
    main = f'''<main class="page" lang="{lang}"><section><div class="wrap"><article class="article">
  <span class="eyebrow">{html.escape(cat)}</span>
  <h2 style="margin-top:8px">{html.escape(title)}</h2>
  <div class="meta">{n["date"]}</div>
  <div class="body">{md(body)}</div>
  <a class="back" href="{back[0]}">← {back[1]}</a>
</article></div></section></main>'''
    io.open(os.path.join(out_dir, f"{n['n']}.html"), "w", encoding="utf-8", newline="\n").write(pre2 + main + post)

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--sample"); ap.add_argument("--out", default=ROOT)
    a = ap.parse_args()
    root = a.out
    issues = json.load(io.open(a.sample, encoding="utf-8")) if a.sample else fetch_issues()
    notices = normalize(issues)
    for path, lang, en in (("index.html", "ko", False), ("news.html", "ko", False), ("en/index.html", "en", True), ("en/news.html", "en", True)):
        ok = inject(os.path.join(root, path), notices, lang, en)
        print(("updated " if ok else "no marker ") + path)
    for lang, sub in (("ko", "news"), ("en", os.path.join("en", "news"))):
        d = os.path.join(root, sub)
        if os.path.isdir(d):
            for f in os.listdir(d):
                if re.fullmatch(r"\d+\.html", f): os.remove(os.path.join(d, f))
        os.makedirs(d, exist_ok=True)
        pre, post = shell_from(os.path.join(root, "news.html" if lang == "ko" else os.path.join("en", "news.html")))
        for n in notices:
            if not n["body_ko"].strip(): continue
            if "_img" not in n:
                n["_img"] = {"ko": localize_images(n["body_ko"], n["n"], root), "en": localize_images(n["body_en"], n["n"], root)}
            n2 = dict(n); n2["body_ko"] = n["_img"]["ko"][0]; n2["body_en"] = n["_img"]["en"][1]
            write_article(n2, lang, d, pre, post, lang == "en")
    img_dir = os.path.join(root, "news", "img")
    if os.path.isdir(img_dir):
        keep = {str(x["n"]) for x in notices}
        for f in os.listdir(img_dir):
            if f.split("-")[0] not in keep: os.remove(os.path.join(img_dir, f))
    for x in notices: x.pop("_img", None)
    io.open(os.path.join(root, "notices.json"), "w", encoding="utf-8", newline="\n").write(json.dumps(notices, ensure_ascii=False, indent=1))
    print(f"{len(notices)} notices")

if __name__ == "__main__":
    main()
