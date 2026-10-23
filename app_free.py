"""
SngLib: tra cứu tài liệu học thuật nhiều tab (MIỄN PHÍ, không AI, không cần API key).
Nguồn: OpenAlex + Crossref.
Chạy:  python -m streamlit run app_free.py
Cần:   pip install streamlit requests pypdf pandas
"""
import datetime
import html
import io
import math
import os
import re
import sys
import threading
import time
import types
import base64
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from itertools import zip_longest
from urllib.parse import quote_plus

import pandas as pd
import requests
import streamlit as st
from PIL import Image
from pypdf import PdfReader

HEADERS = {"User-Agent": "Mozilla/5.0 (research-assistant; mailto:you@example.com)"}
OPENALEX = "https://api.openalex.org"
CROSSREF = "https://api.crossref.org/works"
ICON_S = Image.open(io.BytesIO(base64.b64decode(
    "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")))   # biểu tượng tab trình duyệt: chữ S
NOT_FOUND = "Chưa tìm đủ tài liệu hợp lệ"
MISSING = "Không nêu rõ trong tài liệu"
MAX_PDF_MB = 25
VI_CHARS = re.compile(r"[ăâđêôơưàáạảãằắặẳẵầấậẩẫèéẹẻẽềếệểễìíịỉĩòóọỏõồốộổỗờớợởỡùúụủũừứựửữỳýỵỷỹ]", re.I)
LOAI_VI = {"dissertation": "Luận văn/luận án", "book": "Sách", "book-chapter": "Chương sách",
           "monograph": "Sách chuyên khảo", "edited-book": "Sách biên tập", "report": "Báo cáo",
           "article": "Bài báo", "journal-article": "Bài báo", "preprint": "Bản thảo",
           "posted-content": "Bản thảo", "review": "Tổng quan", "proceedings-article": "Bài hội thảo"}

METHOD_KW = re.compile(
    r"cross-sectional|survey|questionnaire|participants|respondents|sample|regression|structural equation|"
    r"interview|scale|longitudinal|experiment|systematic review|meta-analysis|"
    r"cắt ngang|khảo sát|bộ câu hỏi|thang đo|cỡ mẫu|phỏng vấn|hồi quy", re.I)
RESULT_KW = re.compile(
    r"results? (?:show|indicate|reveal|suggest)|found that|we found|significant|associated|correlat|"
    r"prevalence|predict|\d+(?:[.,]\d+)?\s?%|"
    r"kết quả|liên quan|tương quan|tỷ lệ|có ý nghĩa", re.I)
SAMPLE_RE = re.compile(
    r"\b[nN]\s*=\s*[\d.,]+|"
    r"\b\d[\d.,]*\s+(?:\w+\s+){0,2}(?:students|participants|respondents|adults|sinh viên|người)", re.I)

DESIGN_KW = re.compile(
    r"cross-sectional|longitudinal|randomi[sz]ed|quasi-experiment|experiment|systematic review|meta-analysis|"
    r"qualitative|quantitative|mixed[- ]methods?|case study|cohort|survey|interview|focus group|"
    r"structural equation|regression|"
    r"cắt ngang|nghiên cứu dọc|thực nghiệm|định tính|định lượng|hỗn hợp|khảo sát|phỏng vấn|hồi quy", re.I)
INSTR_KW = re.compile(
    r"\bscales?\b|questionnaire|inventory|instrument|measured (?:by|using|with)|assessed (?:by|using|with)|"
    r"Cronbach|checklist|thang đo|bộ câu hỏi|bảng hỏi|công cụ đo", re.I)
SCALE_NAME = re.compile(
    r"\b(?:[A-Z][\w\-]*\s){1,5}(?:Scale|Questionnaire|Inventory|Index|Survey|Checklist|Test)\b(?:\s\([A-Z][\w\-]*\))?")
KEYS_TRICH = ("mau", "thiet_ke", "cong_cu", "ket_qua")


# ================= PDF =================
def kiem_tra_nhanh(url):
    if not url:
        return False
    try:
        with requests.get(url, headers=HEADERS, timeout=(4, 6), stream=True) as r:
            if r.status_code != 200:
                return False
            ctype = r.headers.get("Content-Type", "").lower()
            if not ("application/pdf" in ctype or r.url.lower().split("?")[0].endswith(".pdf")):
                return False
            return next(r.iter_content(1024), b"").startswith(b"%PDF")
    except requests.RequestException:
        return False


def tai_pdf(url):
    try:
        r = requests.get(url, headers=HEADERS, timeout=(5, 20), stream=True)
    except requests.RequestException:
        return None
    if r.status_code != 200:
        return None
    data = b""
    for chunk in r.iter_content(1 << 16):
        data += chunk
        if len(data) > MAX_PDF_MB * 1024 * 1024:
            return None
    return data if data.startswith(b"%PDF") else None


def pdf_info(data):
    reader = PdfReader(io.BytesIO(data))
    text = "\n".join((p.extract_text() or "") for p in reader.pages[:8])
    meta = reader.metadata or {}
    return text, (meta.title or "").strip(), (meta.author or "").strip()


# ================= Trích xuất bằng quy tắc =================
def tach_cau(text):
    text = re.sub(r"\s+", " ", text)
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+(?=[A-ZÀ-Ỹ0-9])", text) if 40 < len(s) < 400]


def cat(x, n=260):
    return x if len(x) <= n else x[:n].rsplit(" ", 1)[0] + "…"


def trich_xuat(text):
    """Tách 4 trường bằng quy tắc: đối tượng và cỡ mẫu, thiết kế, công cụ đo, kết quả. Không có thì ghi MISSING."""
    text = re.sub(r"\s+", " ", text)
    cau = tach_cau(text)
    dung = set()

    def lay(pattern, toi_da):
        out = [x for x in cau if pattern.search(x) and x not in dung][:toi_da]
        dung.update(out)
        return out

    mau_txt = ""
    m = SAMPLE_RE.search(text)
    if m:
        mau_txt = m.group(0).strip()

    ten = list(dict.fromkeys(re.sub(r"^(?:The|A|An)\s+", "", x) for x in SCALE_NAME.findall(text)))[:3]
    cc = lay(INSTR_KW, 2) if not ten else []
    cong_cu = "; ".join(ten) if ten else " ".join(cc)

    return {"mau": mau_txt or MISSING,
            "thiet_ke": " ".join(lay(DESIGN_KW, 2)) or MISSING,
            "cong_cu": cong_cu or MISSING,
            "ket_qua": " ".join(lay(RESULT_KW, 3)) or MISSING}


# ================= OpenAlex =================
OA_KEY = "NHgQ4B8bYjGAbie6YsbymT"   # khóa OpenAlex gán cứng
_S = sys.modules.get("_snglib_store") or sys.modules.setdefault(
    "_snglib_store", types.SimpleNamespace(loi=[], cache={}))   # sống qua các lần Streamlit chạy lại script
OA_LOI = _S.loi                                     # mã lỗi OpenAlex gặp trong lần chạy hiện tại
OA_TTL = 6 * 3600                                   # nhớ kết quả 6 giờ để không tốn hạn mức khi xem lại
OA_SEM = threading.Semaphore(3)                     # tối đa 3 yêu cầu OpenAlex cùng lúc


def oa_get(path, params, tries=3):
    """Gọi OpenAlex. Nhớ kết quả thành công 6 giờ, thử lại khi bị giới hạn, ghi lại mã lỗi để giao diện báo."""
    if OA_KEY:
        params = {**params, "api_key": OA_KEY}
    khoa_nho = (path, tuple(sorted((k, str(v)) for k, v in params.items())))
    hit = _S.cache.get(khoa_nho)
    if hit and time.time() - hit[0] < OA_TTL:
        return hit[1]
    if time.time() < getattr(_S, "tam_ngung", 0):   # vừa bị từ chối: bỏ qua OpenAlex một lúc, dùng Crossref
        OA_LOI.append(429)
        return {}
    for i in range(tries):
        try:
            with OA_SEM:
                r = requests.get(f"{OPENALEX}/{path}", params=params, headers=HEADERS, timeout=30)
            if r.status_code == 200:
                data = r.json()
                _S.cache[khoa_nho] = (time.time(), data)
                return data
            OA_LOI.append(r.status_code)
            if r.status_code == 429:
                _S.tam_ngung = time.time() + 60
                return {}
            if r.status_code in (500, 502, 503, 504):
                time.sleep(1.0 * (i + 1))
                continue
            return {}
        except Exception:
            OA_LOI.append(0)
            time.sleep(0.8 * (i + 1))
    return {}


def abstract_tu_index(idx):
    if not idx:
        return ""
    pos = {p: w for w, places in idx.items() for p in places}
    return " ".join(pos[i] for i in sorted(pos))


def tach_ten(name):
    """'John Michael Smith' -> ('Smith', 'John Michael'). Chỉ là quy tắc đơn giản, tên Việt Nam cần xem lại."""
    parts = (name or "").split()
    return (parts[-1], " ".join(parts[:-1])) if len(parts) > 1 else (name or "", "")


def w_to_cand(w):
    locs = [w.get("best_oa_location") or {}] + (w.get("locations") or [])
    pdf = next((l["pdf_url"] for l in locs if l.get("pdf_url")), "")
    landing = w.get("doi") or next((l["landing_page_url"] for l in locs if l.get("landing_page_url")), "") or w.get("id", "")
    ten = [a["author"]["display_name"] for a in w.get("authorships", [])]
    tg = (", ".join(ten[:3]) + (" và cộng sự" if len(ten) > 3 else "")) if ten else MISSING
    nguon = ((w.get("primary_location") or {}).get("source") or {}).get("display_name") or ""
    return {"pdf": pdf, "trang": landing, "tg": f"{tg}, {w.get('publication_year', '')}",
            "tieu_de": w.get("title") or "", "tap_chi": nguon, "ten": f"{w.get('title', '')}; {nguon}".strip("; "),
            "abstract": abstract_tu_index(w.get("abstract_inverted_index")),
            "doi": (w.get("doi") or "").lower(), "cites": w.get("cited_by_count", 0),
            "loai": w.get("type", ""), "related": w.get("related_works", []),
            "tac_gia": tg, "nam": w.get("publication_year") or "", "ds_tg": [tach_ten(n) for n in ten],
            "nguon_loai": ((w.get("primary_location") or {}).get("source") or {}).get("type") or ""}


def tim_openalex(q, y1, y2, chi_oa=False, extra="", sort="", per=50, page=1):
    flt = f"publication_year:{y1}-{y2}" + (",open_access.is_oa:true" if chi_oa else "") + (f",{extra}" if extra else "")
    params = {"search": q, "filter": flt, "per-page": per, "page": page}
    if sort:
        params["sort"] = sort
    return [w_to_cand(w) for w in oa_get("works", params).get("results", [])]


def oa_group(q, y1, y2, field, n=15, extra=""):
    flt = f"publication_year:{y1}-{y2}" + (f",{extra}" if extra else "")
    d = oa_get("works", {"search": q, "filter": flt, "group_by": field})
    gs = [g for g in d.get("group_by", []) if g.get("key") and g["key"] != "unknown"]
    if not gs and extra:  # bộ lọc phụ quá chặt thì bỏ đi để vẫn có kết quả
        return oa_group(q, y1, y2, field, n)
    return gs[:n]


def lay_lien_quan(cands):
    ids = []
    for c in [c for c in cands if c.get("related")][:3]:
        ids += [i.split("/")[-1] for i in c["related"][:8]]
    ids = list(dict.fromkeys(ids))[:25]
    if not ids:
        return []
    d = oa_get("works", {"filter": "openalex:" + "|".join(ids), "per-page": 25})
    return [w_to_cand(w) for w in d.get("results", [])]


def lam_giau_tap_chi(groups):
    if not groups:
        return []
    ids = "|".join(g["key"].split("/")[-1] for g in groups)
    chi_tiet = {s["id"]: s for s in oa_get("sources", {"filter": f"openalex:{ids}", "per-page": 50}).get("results", [])}
    rows = []
    for g in groups:
        s = chi_tiet.get(g["key"], {})
        rows.append({"Tên tạp chí": g["key_display_name"], "Số bài về chủ đề này": g["count"],
                     "Nhà xuất bản": s.get("host_organization_name") or "", "Quốc gia": s.get("country_code") or "",
                     "Truy cập mở": "Có" if s.get("is_oa") else "Không",
                     "Chỉ số h": int((s.get("summary_stats") or {}).get("h_index") or 0),
                     "Trang chủ tạp chí": s.get("homepage_url") or None, "Trang OpenAlex": g["key"]})
    return rows


def lam_giau_tac_gia(groups):
    if not groups:
        return []
    ids = "|".join(g["key"].split("/")[-1] for g in groups)
    ct = {a["id"]: a for a in oa_get("authors", {"filter": f"openalex:{ids}", "per-page": 50}).get("results", [])}
    rows = []
    for g in groups:
        a = ct.get(g["key"], {})
        insts = a.get("last_known_institutions") or ([a["last_known_institution"]] if a.get("last_known_institution") else [])
        inst = (insts[0] if insts else {}) or {}
        rows.append({"Tác giả": g["key_display_name"], "Số bài về chủ đề này": g["count"],
                     "Cơ quan": inst.get("display_name") or "", "Quốc gia": inst.get("country_code") or "",
                     "Tổng số bài": int(a.get("works_count") or 0), "Tổng trích dẫn": int(a.get("cited_by_count") or 0),
                     "Trang tác giả": a.get("orcid") or g["key"]})
    return rows


def lam_giau_chu_de(groups):
    if not groups:
        return []
    ids = "|".join(g["key"].split("/")[-1] for g in groups)
    ct = {t["id"]: t for t in oa_get("topics", {"filter": f"openalex:{ids}", "per-page": 50}).get("results", [])}
    rows = []
    for g in groups:
        t = ct.get(g["key"], {})
        rows.append({"Chủ đề liên quan": g["key_display_name"],
                     "Lĩnh vực": (t.get("field") or {}).get("display_name") or "",
                     "Nhóm ngành": (t.get("subfield") or {}).get("display_name") or "",
                     "Số bài": g["count"], "Trang OpenAlex": g["key"]})
    return rows


# Mỗi nhóm tài liệu: (tên hiển thị, type của OpenAlex, type của Crossref)
LOAI_TL = [("Luận văn, luận án", "dissertation", ["dissertation"]),
           ("Sách và chương sách", "book|book-chapter", ["book", "monograph", "edited-book", "book-chapter"]),
           ("Báo cáo", "report", ["report"])]


# ================= Crossref =================
def tim_crossref(q, y1, y2, loai=(), offset=0, rows=50, sort=""):
    flt = f"from-pub-date:{y1},until-pub-date:{y2}" + "".join(f",type:{t}" for t in loai)
    params = {"query.bibliographic": q, "rows": rows, "offset": offset, "filter": flt,
              "select": "DOI,title,author,issued,container-title,abstract,link,URL,is-referenced-by-count,type"}
    if sort:
        params["sort"], params["order"] = sort, "desc"
    try:
        items = requests.get(CROSSREF, params=params, headers=HEADERS, timeout=30).json()["message"]["items"]
    except Exception:
        return []
    out = []
    for it in items:
        title = (it.get("title") or [""])[0]
        if not title:
            continue
        au = [f"{a.get('given', '')} {a.get('family', '')}".strip() for a in it.get("author", [])]
        tg = (", ".join(au[:3]) + (" và cộng sự" if len(au) > 3 else "")) if au else MISSING
        try:
            nam = it["issued"]["date-parts"][0][0]
        except Exception:
            nam = ""
        tap_chi = (it.get("container-title") or [""])[0]
        pdf = next((l["URL"] for l in it.get("link", []) if "pdf" in l.get("content-type", "")), "")
        abstract = html.unescape(re.sub(r"<[^>]+>", " ", it.get("abstract", "")))
        out.append({"pdf": pdf, "trang": it.get("URL", ""), "tg": f"{tg}, {nam}", "tieu_de": title,
                    "tap_chi": tap_chi, "ten": f"{title}; {tap_chi}".strip("; "), "abstract": abstract,
                    "doi": f"https://doi.org/{it['DOI']}".lower() if it.get("DOI") else "",
                    "cites": it.get("is-referenced-by-count", 0), "loai": it.get("type", ""), "related": [],
                    "tac_gia": tg, "nam": nam or "",
                    "ds_tg": [(a.get("family") or a.get("name") or "", a.get("given") or "") for a in it.get("author", [])],
                    "nguon_loai": "journal" if it.get("type") == "journal-article" else ""})
    return out


def diem_uy_tin(c):
    """Điểm xếp hạng: nhiều trích dẫn lên trước, bài báo tạp chí có DOI cộng điểm, bản thảo và kho lưu trữ bị trừ điểm."""
    loai, nl = c.get("loai") or "", c.get("nguon_loai") or ""
    d = 0.0
    if loai in ("article", "journal-article", "review") and nl in ("journal", ""):
        d += 2
    if nl in ("repository", "ebook platform"):
        d -= 1
    if loai in ("preprint", "posted-content"):
        d -= 3
    if c.get("doi"):
        d += 1
    return d + math.log1p(c.get("cites") or 0)


def xep_hang(cands):
    return sorted(cands, key=diem_uy_tin, reverse=True)  # sort ổn định: điểm bằng nhau giữ thứ tự liên quan


def gop(*nguon):
    seen, out = set(), []
    for nhom in zip_longest(*nguon):
        for c in nhom:
            if not c:
                continue
            key = c["doi"] or re.sub(r"\W+", "", c["tieu_de"].lower())
            if key and key not in seen:
                seen.add(key)
                out.append(c)
    return out


# ================= Dựng bảng =================
def doi_sach(doi):
    return re.sub(r"^https?://(?:dx\.)?doi\.org/", "", doi or "", flags=re.I)


def dong(stt, tac_gia, nam, ten, tap_chi, text, nguon, doi, pdf, trang, cites=0, ds_tg=None):
    t = trich_xuat(text) if text else {k: MISSING for k in KEYS_TRICH}
    pp = []
    if t["mau"] != MISSING:
        pp.append(f"[Cỡ mẫu: {t['mau']}]")
    if t["thiet_ke"] != MISSING:
        pp.append(t["thiet_ke"])
    if t["cong_cu"] != MISSING:
        pp.append(f"[Công cụ: {t['cong_cu']}]")
    return {"STT": stt, "Tác giả, năm": f"{tac_gia or MISSING}, {nam or MISSING}",
            "Tên bài, tạp chí": f"{ten or MISSING}; {tap_chi}".strip("; "),
            "Phương pháp và cỡ mẫu": " ".join(pp) or MISSING, "Kết quả chính": t["ket_qua"],
            "Link PDF": pdf or None, "Link bài viết": trang or None,
            "_tieu_de": ten, "_tap_chi": tap_chi, "_cites": cites,
            "_ds_tg": ds_tg or [], "_nam": nam, "_doi": doi_sach(doi)}


def xu_ly(cands, so_bai, chi_pdf, n0=0):
    cands = cands[: so_bai * (6 if chi_pdf else 2)]
    with ThreadPoolExecutor(max_workers=10) as ex:
        pdf_ok = list(ex.map(kiem_tra_nhanh, [c["pdf"] for c in cands]))
    rows = []
    for c, ok in zip(cands, pdf_ok):
        if len(rows) >= so_bai:
            break
        if chi_pdf and not ok:
            continue
        text, nguon = c["abstract"], "Abstract (OpenAlex/Crossref)"
        if not text and ok:
            data = tai_pdf(c["pdf"])
            text, nguon = (pdf_info(data)[0] if data else ""), "PDF (8 trang đầu)"
        rows.append(dong(n0 + len(rows) + 1, c["tac_gia"], c["nam"], c["tieu_de"], c["tap_chi"], text, nguon,
                         c["doi"], c["pdf"] if ok else None, c["trang"], c["cites"], c["ds_tg"]))
    return rows


def bang_don(cands, so=20, n0=0):
    return [{"STT": n0 + i + 1, "Tác giả, năm": c["tg"], "Tên bài, tạp chí": c["ten"], "Trích dẫn": c["cites"],
             "Loại": LOAI_VI.get(c["loai"], c["loai"]), "Link bài viết": c["trang"] or None,
             "Link PDF (chưa kiểm tra)": c["pdf"] or None,
             "_tieu_de": c["tieu_de"], "_tap_chi": c["tap_chi"], "_cites": c["cites"]} for i, c in enumerate(cands[:so])]


def phan_tich_link(u, stt):
    if kiem_tra_nhanh(u):
        data = tai_pdf(u)
        if data:
            text, title, author = pdf_info(data)
            nam = re.search(r"\b(?:19|20)\d{2}\b", text[:3000])
            doi = re.search(r"10\.\d{4,9}/[^\s\"<>]+", text[:6000])
            return dong(stt, author, nam.group(0) if nam else "", title, "", text, "PDF (8 trang đầu)",
                        doi.group(0).rstrip(".,;)") if doi else "", u, None, ds_tg=[author] if author else [])
    try:
        page = requests.get(u, headers=HEADERS, timeout=(5, 15)).text[:300000]
    except requests.RequestException:
        return None

    def meta(*names):
        for n in names:
            m = re.search(rf'<meta[^>]+name=["\']{n}["\'][^>]+content=["\']([^"\']+)', page, re.I)
            if m:
                return html.unescape(m.group(1))
        return ""
    t = meta("citation_title", "og:title") or (re.search(r"<title>(.*?)</title>", page, re.I | re.S) or [None, ""])[1]
    t = html.unescape(re.sub(r"\s+", " ", t)).strip()
    ab = meta("citation_abstract", "description")
    return dong(stt, meta("citation_author", "author"), meta("citation_publication_date", "citation_date")[:4], t,
                meta("citation_journal_title"), ab, "Abstract/meta của trang web", meta("citation_doi"),
                meta("citation_pdf_url"), u, ds_tg=[meta("citation_author", "author")] if meta("citation_author", "author") else [])



# ================= Giao diện: kiểu dáng =================
CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Be+Vietnam+Pro:wght@400;500;600&family=Source+Serif+4:ital,opsz,wght@0,8..60,400;0,8..60,600;1,8..60,400&display=swap');
:root{--acc:#1B7F66;--link:#1E6FD9;--line:rgba(128,128,128,.26);--soft:rgba(128,128,128,.07);--mute:.66}
.stApp{font-family:'Be Vietnam Pro',system-ui,sans-serif}
button,input,textarea{font-family:inherit}
.block-container{max-width:1240px;padding-top:2.2rem;padding-bottom:4rem}
header[data-testid="stHeader"]{background:transparent}
a:focus-visible,button:not([data-baseweb="tab"]):focus-visible,summary:focus-visible{outline:2px solid var(--acc);outline-offset:2px}
[role="tab"],[role="tab"]:focus,[role="tab"]:focus-visible,[role="tab"]:active{outline:none!important;box-shadow:none!important}
[role="tab"]::before,[role="tab"]::after{display:none!important}
[role="tab"]{border-radius:6px 6px 0 0;font-weight:500;font-size:.95rem}
[role="tab"]:focus-visible{background:var(--soft)}
[role="tab"][aria-selected="true"]{color:var(--acc)!important}
[role="tablist"]{gap:.5rem}
[data-baseweb="tab-highlight"]{background:var(--acc)!important}

/* Đầu trang */
.top{margin:0 0 1.1rem}
.mark{color:var(--acc);font-family:'Source Serif 4',Georgia,serif;font-weight:600;font-size:2.6rem;letter-spacing:-.025em;line-height:1.1}
.sub{opacity:var(--mute);margin-top:.35rem;max-width:62ch;line-height:1.5}

/* Ô tìm kiếm */
[data-testid="stForm"]{border:0;padding:0}
[data-testid="stTextInput"] input{font-size:1.12rem;padding:.8rem 1rem;border-radius:10px}
[data-testid="stForm"] button{min-height:3.05rem;font-weight:600;border-radius:10px}

/* Thanh thống kê */
.strip{display:flex;flex-wrap:wrap;gap:.4rem 0;margin:1.1rem 0 .4rem;font-size:.92rem}
.strip span{padding:0 1.1rem;border-left:1px solid var(--line)}
.strip span:first-child{padding-left:0;border-left:0}
.strip b{color:var(--acc);font-family:'Source Serif 4',Georgia,serif;font-size:1.35rem;font-weight:600;margin-right:.3rem}

/* Tiêu đề từng mục */
.sec{font-family:'Source Serif 4',Georgia,serif;font-size:1.3rem;font-weight:600;margin:1.6rem 0 .6rem;letter-spacing:-.01em}
.sec small{font-family:'Be Vietnam Pro',sans-serif;font-weight:400;font-size:.85rem;opacity:var(--mute);margin-left:.6rem}

/* Một mục tài liệu: cột trái là năm, thanh dọc xanh khi có PDF mở được */
.ent{display:grid;grid-template-columns:4.2rem 1fr;gap:0 1rem;max-width:980px;
     padding:1rem 0 1rem;border-bottom:1px solid var(--line)}
.ent .yr{font-family:'Source Serif 4',Georgia,serif;font-size:1.15rem;font-variant-numeric:tabular-nums;
         opacity:var(--mute);padding-top:.1rem;border-top:3px solid var(--line);padding-top:.45rem}
.ent.ok .yr{border-top-color:var(--acc);opacity:1}
.ent .ti{font-family:'Source Serif 4',Georgia,serif;font-size:1.18rem;font-weight:600;line-height:1.35;margin-bottom:.25rem}
.ent .au{font-size:.9rem;opacity:.85;margin:0}
.ent .jr{font-family:'Source Serif 4',Georgia,serif;font-style:italic;font-size:.95rem;opacity:var(--mute);margin:.1rem 0 0}
.tags{margin:.6rem 0 0}
.tag{display:inline-block;font-size:.76rem;padding:1px 9px;border-radius:6px;margin:0 6px 4px 0;border:1px solid rgba(27,127,102,.3);background:rgba(27,127,102,.08)}
.tag.ok{background:var(--acc);border-color:var(--acc);color:#fff}
.acts{margin:.55rem 0 0}
.lk{display:inline-block;font-size:.85rem;font-weight:500;padding:5px 14px;border-radius:8px;margin:0 8px 4px 0;
    text-decoration:none!important;background:var(--acc);color:#fff!important;border:1px solid var(--acc)}
.lk.sec{background:transparent;color:var(--link)!important;border-color:var(--link)}
.ent details{margin-top:.6rem;font-size:.9rem}
.ent summary{cursor:pointer;opacity:.85;font-weight:500}
.ent details p{margin:.5rem 0 0;line-height:1.55}
.ent details b{font-weight:600}

/* Bảng */
.tw{overflow-x:auto;margin:.4rem 0 1rem}
.tb{width:100%;border-collapse:collapse;font-size:.88rem;line-height:1.5}
.tb th,.tb td{padding:10px 12px;vertical-align:top;word-break:break-word;overflow-wrap:anywhere;text-align:left;
    border-bottom:1px solid var(--line)}
.tb th{font-weight:600;white-space:nowrap;border-bottom:2px solid currentColor;font-size:.82rem}
.tb td{min-width:90px}
.tb td.w{min-width:320px}
.tb td.n{white-space:nowrap;text-align:right;width:1%;font-variant-numeric:tabular-nums}
.tb td.l{white-space:nowrap;width:1%}
.tb a{color:var(--link);text-decoration:none;font-weight:500}
.tb a:hover{text-decoration:underline}

/* Dòng trống đầu trang */
.hint{opacity:var(--mute);max-width:68ch;line-height:1.55;margin:.4rem 0 0}
/* Popover OpenAlex: gọn khi đóng, chỉ rộng ra khi mở Hướng dẫn để ảnh không bị mờ */
div[data-testid="stPopoverBody"]{width:min(420px,94vw)!important;max-width:94vw!important}
div[data-testid="stPopoverBody"]:has(details[open]){width:min(1180px,96vw)!important;max-width:96vw!important}
div[data-testid="stPopoverBody"] img{image-rendering:-webkit-optimize-contrast;image-rendering:high-quality}
div[data-testid="stPopover"] button [data-testid="stIconMaterial"],
div[data-testid="stPopover"] button span[class*="Icon"]{font-size:.9rem!important;width:.9rem!important;height:.9rem!important}

/* ===== Tối ưu điện thoại ===== */
html{-webkit-text-size-adjust:100%}
.stApp{overflow-x:hidden}
.tw{-webkit-overflow-scrolling:touch}
/* Thanh mục: cuộn ngang bằng ngón tay, không bị bẻ dòng */
[data-testid="stSegmentedControl"] > div,[data-testid="stSegmentedControl"] [role="group"]{max-width:100%}
@media (max-width:768px){
  .block-container{padding:1rem .8rem 3rem!important;max-width:100%}
  header[data-testid="stHeader"]{height:2.6rem}
  .mark{font-size:2rem}
  .sub{font-size:.92rem}
  div.sec{font-size:1.15rem;margin:1.2rem 0 .5rem}
  div.sec small{display:block;margin:.1rem 0 0}

  /* Ô tìm kiếm: ô nhập và nút Tìm nằm cùng một hàng; chữ 16px để iOS không tự phóng to */
  [data-testid="stForm"] [data-testid="stHorizontalBlock"]{flex-wrap:nowrap!important;gap:.5rem!important}
  [data-testid="stForm"] [data-testid="stColumn"]{min-width:0!important}
  [data-testid="stForm"] [data-testid="stColumn"]:last-child{flex:0 0 auto!important;width:auto!important}
  [data-testid="stTextInput"] input{font-size:16px;padding:.7rem .85rem}
  input,textarea,select{font-size:16px!important}
  [data-testid="stForm"] button{min-height:2.9rem;padding:0 1.1rem}

  /* Nút bấm đủ lớn để chạm */
  .stButton button,.stDownloadButton button,[data-testid="stLinkButton"] a,[data-testid="stPopover"] button{min-height:2.75rem}

  /* Thanh mục và bộ lọc thời gian: một hàng, vuốt ngang */
  [data-testid="stSegmentedControl"]{overflow-x:auto;-webkit-overflow-scrolling:touch;scrollbar-width:none;max-width:100%}
  [data-testid="stSegmentedControl"]::-webkit-scrollbar{display:none}
  [data-testid="stSegmentedControl"] [role="group"],[data-testid="stSegmentedControl"] > div > div{flex-wrap:nowrap!important}
  [data-testid="stSegmentedControl"] button{white-space:nowrap;flex:0 0 auto;min-height:2.6rem}

  /* Thống kê gọn lại */
  .strip{margin:.8rem 0 .3rem;font-size:.85rem}
  .strip span{padding:0 .8rem}
  .strip b{font-size:1.2rem}

  /* Thẻ tài liệu: năm nằm trên đầu, nút Tải PDF / Mở bài chia đều chiều ngang */
  .ent{grid-template-columns:1fr;gap:0;padding:.9rem 0}
  .ent .yr{width:3.6rem;margin-bottom:.45rem;font-size:1.05rem}
  .ent .ti{font-size:1.08rem}
  .ent .au{font-size:.86rem}
  .acts{display:flex;gap:.5rem;flex-wrap:wrap}
  a.lk,a.lk.sec{flex:1 1 40%;text-align:center;margin:0;padding:10px 12px;font-size:.9rem}
  .ent summary{padding:.5rem 0}

  /* Bảng thành thẻ xếp dọc: mỗi dòng là một thẻ, mỗi ô có nhãn cột */
  .tw{overflow-x:visible}
  .tb,.tb tbody,.tb tr,.tb td{display:block;width:100%}
  .tb thead{display:none}
  .tb tr{border:1px solid var(--line);border-radius:10px;padding:.35rem .8rem;margin:0 0 .7rem;background:var(--soft)}
  .tb td,.tb td.n,.tb td.l,.tb td.w{display:flex;gap:.8rem;justify-content:space-between;align-items:baseline;
       width:100%;min-width:0;text-align:right;white-space:normal;padding:7px 0;border-bottom:1px dashed var(--line);font-size:.9rem}
  .tb td:last-child{border-bottom:0}
  .tb td::before{content:attr(data-label);flex:0 0 36%;max-width:36%;text-align:left;font-size:.76rem;font-weight:600;opacity:var(--mute)}
  .tb td:empty{display:none}
  .tb td.w{display:block;text-align:left}
  .tb td.w::before{display:block;max-width:none;margin-bottom:.2rem}
  .tb td > a{padding:4px 0}

  /* Hàng nút Trước / Sau: giữ trên một hàng, caption xuống dòng dưới */
  [class*="st-key-nav_"] [data-testid="stHorizontalBlock"]{flex-wrap:wrap!important;gap:.5rem!important}
  [class*="st-key-nav_"] [data-testid="stColumn"]{min-width:0!important}
  [class*="st-key-nav_"] [data-testid="stColumn"]:nth-child(-n+2){flex:1 1 calc(50% - .5rem)!important;width:calc(50% - .5rem)!important}
  [class*="st-key-nav_"] [data-testid="stColumn"]:nth-child(3){flex:1 1 100%!important;width:100%!important}

  /* Hàng công cụ (kiểu hiển thị, APA, CSV): 2 cột gọn */
  [class*="st-key-tools"] [data-testid="stHorizontalBlock"]{flex-wrap:wrap!important;gap:.5rem!important}
  [class*="st-key-tools"] [data-testid="stColumn"]{flex:1 1 calc(50% - .5rem)!important;width:calc(50% - .5rem)!important;min-width:0!important}
  [class*="st-key-tools"] [data-testid="stColumn"]:first-child{flex:1 1 100%!important;width:100%!important}

  /* Hàng bộ lọc: thanh thời gian một hàng riêng, Có PDF và OpenAlex chia đôi hàng dưới */
  [class*="st-key-filters"] [data-testid="stHorizontalBlock"]{flex-wrap:wrap!important;gap:.5rem!important}
  [class*="st-key-filters"] [data-testid="stColumn"]{flex:1 1 calc(50% - .5rem)!important;width:calc(50% - .5rem)!important;min-width:0!important}
  [class*="st-key-filters"] [data-testid="stColumn"]:first-child{flex:1 1 100%!important;width:100%!important}

  /* Khung năm tùy chọn và các nút gợi ý chủ đề: 2 cột / xếp dọc */
  [class*="st-key-years"] [data-testid="stHorizontalBlock"]{flex-wrap:nowrap!important;gap:.5rem!important}
  [class*="st-key-years"] [data-testid="stColumn"]{min-width:0!important}
  [class*="st-key-years"] [data-testid="stColumn"]:nth-child(3){display:none}

  /* Link tìm ở nơi khác: 2 nút một hàng */
  [class*="st-key-links"] [data-testid="stHorizontalBlock"]{flex-wrap:wrap!important;gap:.5rem!important}
  [class*="st-key-links"] [data-testid="stColumn"]{flex:1 1 calc(50% - .5rem)!important;width:calc(50% - .5rem)!important;min-width:0!important}

  /* Popover OpenAlex: gần full màn hình, ảnh hướng dẫn đủ rộng để đọc */
  div[data-testid="stPopoverBody"],div[data-testid="stPopoverBody"]:has(details[open]){width:calc(100vw - 1.6rem)!important;max-width:calc(100vw - 1.6rem)!important}
}
@media (max-width:380px){
  .mark{font-size:1.75rem}
  a.lk,a.lk.sec{flex:1 1 100%}
  .tb td::before{flex-basis:42%;max-width:42%}
}

[data-testid="stSpinner"]{padding:.6rem 0;font-weight:500}

/* Ô khóa OpenAlex: nút lưu sát ô nhập, icon nằm giữa nút */
div[data-testid="stPopoverBody"] [data-testid="stHorizontalBlock"]{gap:.4rem!important}
/* Ẩn nút Deploy, giữ menu ba chấm đã đổi nội dung */
[data-testid="stAppDeployButton"],.stAppDeployButton,.stDeployButton{display:none!important}
</style>
"""


def esc(x):
    return html.escape(str(x or ""), quote=True)


def lk(url, nhan, phu=False):
    return f'<a class="lk{" sec" if phu else ""}" href="{esc(url)}" target="_blank" rel="noopener">{esc(nhan)}</a>' \
        if url and str(url).startswith("http") else ""


def tieu_de(ten, ghi_chu=""):
    st.markdown(f'<div class="sec">{esc(ten)}' + (f'<small>{esc(ghi_chu)}</small>' if ghi_chu else "") + '</div>',
                unsafe_allow_html=True)


def the(r, chi_tiet=False):
    tieu = r.get("_tieu_de") or r.get("Tên bài") or r.get("Tên bài, tạp chí") or "(không có tên)"
    tg_nam = str(r.get("Tác giả, năm") or ", ".join(str(x) for x in [r.get("Tác giả"), r.get("Năm")] if x))
    m = re.search(r"\b(?:19|20)\d{2}\b", tg_nam)
    nam = r.get("_nam") or (m.group(0) if m else "")
    tg = re.sub(r",\s*(?:\d{4})?\s*$", "", tg_nam)
    pdf = r.get("Link PDF") or r.get("Link PDF (chưa kiểm tra)")
    tags = ""
    if r.get("Link PDF"):
        tags += '<span class="tag ok">PDF mở được</span>'
    if r.get("_cites"):
        tags += f'<span class="tag">{int(r["_cites"]):,} trích dẫn</span>'
    if r.get("Loại"):
        tags += f'<span class="tag">{esc(r["Loại"])}</span>'
    links = lk(pdf, "Tải PDF") + lk(r.get("Link bài viết"), "Mở bài viết", phu=bool(pdf))
    detail = ""
    if chi_tiet:
        detail = ('<details><summary>Phương pháp, cỡ mẫu và kết quả chính</summary>'
                  f'<p><b>Phương pháp, cỡ mẫu:</b> {esc(r.get("Phương pháp và cỡ mẫu"))}</p>'
                  f'<p><b>Kết quả chính:</b> {esc(r.get("Kết quả chính"))}</p>'
                  + (f'<p><b>APA:</b> {r["APA"]}</p>' if r.get("APA") else "")
                  + '</details>')
    st.markdown(
        f'<article class="ent{" ok" if r.get("Link PDF") else ""}"><div class="yr">{esc(nam) or "&ndash;"}</div>'
        f'<div class="bd"><div class="ti">{esc(tieu)}</div>'
        + (f'<p class="au">{esc(tg)}</p>' if tg else "")
        + (f'<p class="jr">{esc(r.get("_tap_chi"))}</p>' if r.get("_tap_chi") else "")
        + f'<div class="tags">{tags}</div><div class="acts">{links}</div>{detail}</div></article>',
        unsafe_allow_html=True)


def sach(rows):
    df = pd.DataFrame(rows)
    return df.drop(columns=[c for c in df.columns if c.startswith("_")])


LINK_NHAN = {"Link PDF": "PDF", "Link PDF (chưa kiểm tra)": "PDF", "Link bài viết": "Mở bài",
             "Trang chủ tạp chí": "Mở trang", "Trang OpenAlex": "Mở", "Trang tác giả": "Mở hồ sơ",
             "Tra cứu tạp chí": "Mở", "Tra cứu tác giả": "Mở"}


def lk_text(url, nhan):
    return f'<a href="{esc(url)}" target="_blank" rel="noopener">{esc(nhan)}</a>'


def bang(rows, rong="Không có kết quả."):
    """Bảng đầy đủ: chữ tự xuống dòng, hiện hết cột và hết dòng, không phải lướt ngang."""
    if not rows:
        st.info(rong)
        return
    df = sach(rows)
    head = "".join(f"<th>{esc(c)}</th>" for c in df.columns)
    body = []
    for _, r in df.iterrows():
        tds = []
        for c in df.columns:
            v = r[c]
            lb = esc(c)
            if c in LINK_NHAN:
                ok = isinstance(v, str) and v.startswith("http")
                tds.append(f'<td class="l" data-label="{lb}">{lk_text(v, LINK_NHAN[c]) if ok else ""}</td>')
            elif c == "APA":
                tds.append(f'<td class="w" data-label="{lb}">{v if isinstance(v, str) else ""}</td>')
            elif c in ("STT", "Trích dẫn", "Năm") or isinstance(v, (int, float)) and not pd.isna(v):
                tds.append(f'<td class="n" data-label="{lb}">{esc(v)}</td>')
            else:
                tds.append(f'<td data-label="{lb}">{esc(v if isinstance(v, str) else "")}</td>')
        body.append("<tr>" + "".join(tds) + "</tr>")
    st.markdown(f'<div class="tw"><table class="tb"><thead><tr>{head}</tr></thead>'
                f'<tbody>{"".join(body)}</tbody></table></div>', unsafe_allow_html=True)


def danh_sach_the(rows, rong="Không có kết quả."):
    if not rows:
        st.info(rong)
    for r in rows:
        the(r)


# ================= Trích dẫn APA =================
def viet_tat(given):
    out = []
    for tok in (given or "").replace(".", " ").split():
        out.append("-".join(p[0].upper() + "." for p in tok.split("-") if p))
    return " ".join(out)


def ten_apa(a):
    if isinstance(a, str):
        return a.strip()
    f, g = a
    v = viet_tat(g)
    return f"{f}, {v}" if v else f


def ds_tac_gia_apa(ds):
    n = [x for x in (ten_apa(a) for a in ds if a) if x]
    if not n:
        return ""
    if len(n) == 1:
        return n[0]
    if len(n) <= 20:
        return ", ".join(n[:-1]) + ", & " + n[-1]
    return ", ".join(n[:19]) + ", ... " + n[-1]


def trich_dan_apa(r, md=True):
    """APA 7 cho bài báo tạp chí. md=True: dùng *nghiêng*; md=False: HTML <i>."""
    e = (lambda x: x) if md else esc
    tg = ds_tac_gia_apa(r.get("_ds_tg") or [])
    nam = str(r["_nam"]) if r.get("_nam") else "n.d."
    tieu = (r.get("_tieu_de") or "").strip().rstrip(".")
    tc = (r.get("_tap_chi") or "").strip()
    link = f"https://doi.org/{r['_doi']}" if r.get("_doi") else (r.get("Link bài viết") or r.get("Link PDF") or "")
    if tg:
        out = f"{e(tg if tg.endswith('.') else tg + '.')} ({nam}). {e(tieu)}."
    else:
        out = f"{e(tieu)}. ({nam})."
    if tc:
        out += f" *{tc}*." if md else f" <i>{esc(tc)}</i>."
    if link:
        out += f" {link}" if md else f' <a href="{esc(link)}">{esc(link)}</a>'
    return out


def danh_sach_apa(rows, md=True):
    def khoa_xep(r):
        ds = r.get("_ds_tg") or []
        return ((ten_apa(ds[0]) if ds else (r.get("_tieu_de") or "")).lower(), str(r.get("_nam") or ""))
    return [trich_dan_apa(r, md) for r in sorted(rows, key=khoa_xep)]


def them_apa(rows, thuan_van=False):
    """Gắn cột 'Trích dẫn APA' vào các dòng. thuan_van=True: bỏ thẻ HTML (dùng cho CSV)."""
    out = []
    for r in rows:
        x = trich_dan_apa(r, md=False)
        out.append({**r, "APA": html.unescape(re.sub(r"<[^>]+>", "", x)) if thuan_van else x})
    return out


def file_apa_html(rows):
    ps = "".join(f'<p style="margin-left:36pt;text-indent:-36pt">{x}</p>' for x in danh_sach_apa(rows, md=False))
    return ('<html><head><meta charset="utf-8"><title>Tài liệu tham khảo</title></head>'
            '<body style="font-family:\'Times New Roman\',serif;font-size:12pt;line-height:2">'
            f'<h3>Tài liệu tham khảo</h3>{ps}</body></html>').encode("utf-8")


# ================= Tải dần và phân trang (không giới hạn số lượng, mỗi trang 15) =================
PAGE = 15
BATCH = 50


def khoa(c):
    return c.get("doi") or c.get("key") or re.sub(r"\W+", "", (c.get("tieu_de") or "").lower())


def moi_nguon(fetch, xl):
    """fetch(b) trả về lô thứ b (rỗng khi hết); xl(chunk, n0) biến một lô thô thành các dòng hiển thị."""
    return {"fetch": fetch, "xl": xl, "items": [], "queue": [], "seen": set(), "batch": 0, "het": False}


def tai_den(nguon, can):
    """Tải thêm cho tới khi đủ `can` mục hoặc hết dữ liệu. Mỗi lần chỉ xử lý đúng phần cần hiển thị."""
    for _ in range(40):
        if len(nguon["items"]) >= can:
            return
        if not nguon["queue"]:
            if nguon["het"]:
                return
            nguon["batch"] += 1
            lo = nguon["fetch"](nguon["batch"])
            if not lo:
                nguon["het"] = True
                return
            for c in lo:
                k = khoa(c)
                if k and k in nguon["seen"]:
                    continue
                if k:
                    nguon["seen"].add(k)
                nguon["queue"].append(c)
            continue
        chunk, nguon["queue"] = nguon["queue"][:PAGE], nguon["queue"][PAGE:]
        nguon["items"] += nguon["xl"](chunk, len(nguon["items"]))


def so_luong(nguon):
    return len(nguon["items"]) + len(nguon["queue"])


def doi_trang(key, d):
    st.session_state[f"tr_{key}"] = max(1, st.session_state.get(f"tr_{key}", 1) + d)


def lay_trang(nguon, key):
    tr = st.session_state.get(f"tr_{key}", 1)
    can = PAGE * tr + 1
    if len(nguon["items"]) < can and not nguon["het"]:
        with st.spinner("Đang tải kết quả, bạn chờ chút nhé..."):
            tai_den(nguon, can)
    else:
        tai_den(nguon, can)
    tong = len(nguon["items"])
    if tr > 1 and tong <= PAGE * (tr - 1):
        tr = max(1, -(-tong // PAGE))
        st.session_state[f"tr_{key}"] = tr
    return tr, nguon["items"][PAGE * (tr - 1): PAGE * tr], tong > PAGE * tr



def dieu_huong(key, tr, n_ds, has_next, pos):
    c = st.container(key=f"nav_{key}_{pos}").columns([1, 1, 6], vertical_alignment="center")
    c[0].button("Trước", key=f"p_{key}_{pos}", icon=":material/chevron_left:", disabled=tr <= 1,
                on_click=doi_trang, args=(key, -1), width="stretch")
    c[1].button("Sau", key=f"n_{key}_{pos}", icon=":material/chevron_right:", disabled=not has_next,
                on_click=doi_trang, args=(key, 1), width="stretch")
    a = PAGE * (tr - 1) + 1
    c[2].caption(f"Trang {tr}, kết quả {a} đến {a + n_ds - 1}" + ("" if has_next else ", đã hết kết quả"))


def hien_nguon(nguon, key, rong, hien=None):
    hien = hien or (lambda ds: danh_sach_the(ds))
    tr, ds, has_next = lay_trang(nguon, key)
    if not ds:
        st.info(rong)
        return
    hien(ds)
    dieu_huong(key, tr, len(ds), has_next, "d")


def nguon_bai(q, y1, y2, chi_pdf):
    def fetch(b):
        return xep_hang(gop(tim_openalex(q, y1, y2, chi_pdf, "", "", BATCH, b),
                            tim_crossref(q, y1, y2, (), (b - 1) * BATCH, BATCH)))
    return moi_nguon(fetch, lambda ch, n0: xu_ly(ch, len(ch), chi_pdf, n0))


def nguon_trich_dan(q, y1, y2):
    def fetch(b):  # OpenAlex hết hạn mức thì dùng Crossref xếp theo số trích dẫn
        return (tim_openalex(q, y1, y2, False, "", "cited_by_count:desc", BATCH, b)
                or tim_crossref(q, y1, y2, (), (b - 1) * BATCH, BATCH, "is-referenced-by-count"))
    return moi_nguon(fetch, lambda ch, n0: bang_don(ch, len(ch), n0))


def nguon_lien_quan(q, y1, y2, chi_pdf):
    """Chỉ gọi khi mở tab. Cùng tham số với trang đầu của tab Bài báo nên được dùng lại từ bộ nhớ đệm."""
    return moi_nguon(lambda b: lay_lien_quan(tim_openalex(q, y1, y2, chi_pdf)) if b == 1 else [],
                     lambda ch, n0: bang_don(ch, len(ch), n0))


def nguon_loai(q, y2, oa_type, cr_types):
    def fetch(b):
        return xep_hang(gop(tim_openalex(q, 1990, y2, False, f"type:{oa_type}", "", BATCH, b),
                            tim_crossref(q, 1990, y2, cr_types, (b - 1) * BATCH, BATCH)))
    return moi_nguon(fetch, lambda ch, n0: bang_don(ch, len(ch), n0))


def cr_tong_hop(q, y1, y2):
    """Dự phòng không cần khóa: đếm tạp chí và tác giả từ khoảng 200 bài đầu trên Crossref."""
    khoa_nho = ("cr_tong_hop", q, y1, y2)
    hit = _S.cache.get(khoa_nho)
    if hit:
        return hit
    ds = tim_crossref(q, y1, y2, (), 0, 100) + tim_crossref(q, y1, y2, (), 100, 100)
    tc = Counter(c["tap_chi"] for c in ds if c["tap_chi"])
    tg = Counter(f"{g} {f}".strip() for c in ds for f, g in c["ds_tg"] if f or g)
    kq_ = ([{"Tên tạp chí": k, "Số bài về chủ đề này": v,
             "Tra cứu tạp chí": "https://www.google.com/search?q=" + quote_plus(f'"{k}" tạp chí')}
            for k, v in tc.most_common(50)],
           [{"Tác giả": k, "Số bài về chủ đề này": v,
             "Tra cứu tác giả": "https://scholar.google.com/scholar?q=" + quote_plus(f'author:"{k}"')}
            for k, v in tg.most_common(50)])
    if ds:
        _S.cache[khoa_nho] = kq_
    return kq_


def nguon_nhom(layg, giau, cot, du_phong, ten, dp):
    """Tải khi mở tab. layg() lấy nhóm từ OpenAlex; trống thì dùng du_phong() từ Crossref và ghi vào dp."""
    def fetch(b):
        if b != 1:
            return []
        g = layg()
        if g:
            return g
        rows = du_phong()
        if rows:
            dp.add(ten)
        return rows
    return moi_nguon(fetch, lambda ch, n0: ch if ch and cot in ch[0] else giau(ch))



# ================= Trang chính =================
st.set_page_config(
    page_title="SngLib", page_icon=ICON_S, layout="wide", initial_sidebar_state="collapsed",
    menu_items={
        "Get help": None,
        "Report a bug": None,
        "About": ("### SngLib\n"
                  "Kho tài liệu học thuật, tìm nhanh bài báo và PDF miễn phí.\n\n"
                  "Dữ liệu lấy từ OpenAlex và Crossref."),
    })
st.markdown(CSS, unsafe_allow_html=True)
st.markdown('<div class="top"><div class="mark">SngLib</div>'
            '<div class="sub">Kho tài liệu học thuật, tìm nhanh bài báo và PDF miễn phí</div></div>', unsafe_allow_html=True)

with st.form("tim_kiem"):
    c1, c2 = st.columns([6, 1], vertical_alignment="bottom")
    dau_vao = c1.text_input("Tìm kiếm", key="q", label_visibility="collapsed",
                            placeholder="Ví dụ: academic stress university students")
    bam = c2.form_submit_button("Tìm", type="primary", width="stretch")

NAM_NAY = datetime.date.today().year
KHOANG = {"Tất cả": None, "3 năm qua": 3, "5 năm qua": 5, "10 năm qua": 10}
VI_DU = ["academic stress university students", "online learning engagement", "sleep quality adolescents"]


def kich_tim():
    """Đổi bộ lọc thì tự tìm lại với từ khóa hiện tại."""
    st.session_state["chay"] = True


def dung_mau(t):
    st.session_state["q"] = t
    st.session_state["chay"] = True


b1, b2 = st.container(key="filters").columns([3.6, 1.2], vertical_alignment="bottom")
kt = b1.segmented_control("Thời gian xuất bản", [*KHOANG, "Tùy chọn"], default="Tất cả", key="kt",
                          on_change=kich_tim) or "Tất cả"
chi_pdf = b2.toggle("Có PDF", key="chi_pdf", on_change=kich_tim,
                    help="Chỉ giữ các bài có link PDF mở được trực tiếp")
if kt == "Tùy chọn":
    n1, n2, _ = st.container(key="years").columns([1, 1, 4])
    y1 = int(n1.number_input("Từ năm", 1900, NAM_NAY, 2018, 1, key="nam_tu", on_change=kich_tim, format="%d"))
    y2 = int(n2.number_input("Đến năm", 1900, NAM_NAY, NAM_NAY, 1, key="nam_den", on_change=kich_tim, format="%d"))
    if y1 > y2:
        st.caption("Năm bắt đầu lớn hơn năm kết thúc, app tự đổi chỗ hai năm này.")
        y1, y2 = y2, y1
else:
    y2 = NAM_NAY
    y1 = 1990 if KHOANG[kt] is None else NAM_NAY - KHOANG[kt]

OA_LOI.clear()   # nhật ký lỗi chỉ tính cho lần chạy này
chay = bam or st.session_state.pop("chay", False)

if chay and (dau_vao or "").strip():
    for k in [k for k in st.session_state if str(k).startswith("tr_")]:
        del st.session_state[k]
    urls = [u.rstrip(".,;)") for u in re.findall(r"https?://[^\s<>\"']+", dau_vao)]
    chu_de = re.sub(r"https?://[^\s<>\"']+", "", dau_vao).strip()
    kq = {"chu_de": chu_de, "urls": bool(urls), "loi": [], "rows": [], "oa_loi": []}

    with st.status("Đang tìm kiếm...", expanded=False) as tt:
        if urls:
            for u in urls:
                r = phan_tich_link(u, len(kq["rows"]) + 1)
                (kq["rows"].append(r) if r else kq["loi"].append(u))
        else:
            dp = set()
            kq["dp"] = dp
            kq["bai"] = nguon_bai(chu_de, y1, y2, chi_pdf)
            kq["trich_dan"] = nguon_trich_dan(chu_de, y1, y2)
            kq["lien_quan"] = nguon_lien_quan(chu_de, y1, y2, chi_pdf)
            kq["luan_van"] = [(ten, nguon_loai(chu_de, y2, o, c)) for ten, o, c in LOAI_TL]
            kq["tap_chi"] = nguon_nhom(
                lambda: oa_group(chu_de, y1, y2, "primary_location.source.id", 200, "primary_location.source.type:journal"),
                lam_giau_tap_chi, "Tên tạp chí", lambda: cr_tong_hop(chu_de, y1, y2)[0], "tap_chi", dp)
            kq["tac_gia"] = nguon_nhom(
                lambda: oa_group(chu_de, y1, y2, "authorships.author.id", 200),
                lam_giau_tac_gia, "Tác giả", lambda: cr_tong_hop(chu_de, y1, y2)[1], "tac_gia", dp)
            kq["chu_de_lq"] = nguon_nhom(
                lambda: oa_group(chu_de, y1, y2, "primary_topic.id", 200),
                lam_giau_chu_de, "Chủ đề liên quan", lambda: [], "chu_de", dp)
            tai_den(kq["bai"], PAGE + 1)  # chỉ nạp trang đầu của tab Bài báo, các tab khác nạp khi mở
        kq["oa_loi"] = sorted(set(OA_LOI) - {200})
        tt.update(label="Đã tìm xong", state="complete")
    st.session_state["kq"] = kq

kq = st.session_state.get("kq")

if not kq:
    tieu_de("Thử một chủ đề")
    cs = st.container(key="links_vidu").columns([1.4, 1.2, 1.3, 2])
    for c, t in zip(cs, VI_DU):
        c.button(t, key=f"vd_{t}", on_click=dung_mau, args=(t,), width="stretch")
    st.markdown('<p class="hint">Gõ từ khóa tiếng Anh để ra nhiều bài hơn. Hoặc dán link bài báo hoặc PDF để xem phương pháp và kết quả của bài đó.</p>',
                unsafe_allow_html=True)
else:
    if kq["urls"]:
        rows_all = rows_page = kq["rows"]
    else:
        tr_bai, rows_page, co_tiep_bai = lay_trang(kq["bai"], "bai")
        rows_all = kq["bai"]["items"]

    n_pdf = sum(1 for r in rows_all if r.get("Link PDF"))
    chi_so = [(len(rows_all), "bài đã tải"), (n_pdf, "có PDF mở được")]
    st.markdown('<div class="strip">' + "".join(f"<span><b>{n:,}</b>{esc(t)}</span>" for n, t in chi_so) + "</div>",
                unsafe_allow_html=True)

    canh_bao = st.container()
    if not kq["urls"] and VI_CHARS.search(kq["chu_de"]):
        st.info("Từ khóa tiếng Việt có thể ra ít bài, bạn thử gõ tiếng Anh xem.")

    TEN_TAB = ["Bài báo", "Bài liên quan", "Tạp chí", "Luận văn, sách, báo cáo", "Tác giả và chủ đề", "Tìm ở nơi khác"]
    tab_hien = st.segmented_control("Mục", TEN_TAB, default=TEN_TAB[0], key="tab_hien",
                                    label_visibility="collapsed") or TEN_TAB[0]  # chỉ nạp mục đang xem
    chi_link = "Tab này chỉ có khi tìm theo chủ đề, không phải khi dán link."

    if tab_hien == TEN_TAB[0]:
        if rows_page:
            top = st.container(key="tools").columns([1.6, 0.9, 1.1, 1.5, 3], vertical_alignment="center")
            kieu = top[0].segmented_control("Kiểu hiển thị", ["Bảng", "Danh sách"], default="Bảng",
                                            key="kieu", label_visibility="collapsed") or "Bảng"
            apa = top[1].toggle("APA", value=False, help="Thêm cột trích dẫn APA vào bảng, danh sách và file CSV")
            rows_csv = them_apa(rows_all, thuan_van=True) if apa else rows_all
            top[2].download_button("CSV", sach(rows_csv).to_csv(index=False).encode("utf-8-sig"),
                                   "danh_muc_tai_lieu.csv", "text/csv", icon=":material/download:", width="stretch")
            if apa:
                top[3].download_button("APA (Word)", file_apa_html(rows_all), "tai_lieu_tham_khao_APA.html",
                                       "text/html", icon=":material/download:", width="stretch")
            rows_hien = them_apa(rows_page) if apa else rows_page
            if kieu == "Danh sách":
                for r in rows_hien:
                    the(r, chi_tiet=True)
            else:
                bang(rows_hien)
            if not kq["urls"]:
                dieu_huong("bai", tr_bai, len(rows_page), co_tiep_bai, "d")
        else:
            st.warning(NOT_FOUND)
        if kq["loi"]:
            with st.expander(f"{len(kq['loi'])} link không mở được"):
                for u in kq["loi"]:
                    st.write("- " + u)

    if tab_hien == TEN_TAB[1]:
        if kq["urls"]:
            st.info(chi_link)
        else:
            tieu_de("Được trích dẫn nhiều nhất", "về chủ đề này")
            hien_nguon(kq["trich_dan"], "cite", "Không thấy bài nào cho chủ đề này.")
            tieu_de("Bài liên quan", "tới các kết quả đầu tiên")
            hien_nguon(kq["lien_quan"], "lq", "OpenAlex chưa có gợi ý bài liên quan cho chủ đề này.")

    if tab_hien == TEN_TAB[2]:
        if kq["urls"]:
            st.info(chi_link)
        else:
            tieu_de("Tạp chí đăng nhiều bài", "về chủ đề này")
            hien_nguon(kq["tap_chi"], "tc", "Không có kết quả.", bang)
            if "tap_chi" in kq.get("dp", ()):
                st.caption("Số liệu tạm tính từ khoảng 200 bài đầu trên Crossref, chưa có nhà xuất bản và chỉ số h.")

    if tab_hien == TEN_TAB[3]:
        if kq["urls"]:
            st.info(chi_link)
        else:
            st.caption("Tìm riêng từng loại tài liệu (từ 1990) trên OpenAlex và Crossref. "
                       "Luận văn tiếng Việt xem thêm ở tab “Tìm ở nơi khác”.")
            for i, (ten, nguon) in enumerate(kq["luan_van"]):
                tieu_de(ten)
                hien_nguon(nguon, f"lv{i}", f"Không thấy {ten.lower()} cho chủ đề này. "
                                            "Thử từ khóa tiếng Anh hoặc mở tab “Tìm ở nơi khác”.")

    if tab_hien == TEN_TAB[4]:
        if kq["urls"]:
            st.info(chi_link)
        else:
            tieu_de("Tác giả nổi bật")
            hien_nguon(kq["tac_gia"], "ta", "Không có kết quả.", bang)
            if "tac_gia" in kq.get("dp", ()):
                st.caption("Số liệu tạm tính từ khoảng 200 bài đầu trên Crossref, chưa có cơ quan và số trích dẫn.")
            tieu_de("Chủ đề liên quan")
            hien_nguon(kq["chu_de_lq"], "cd", "Không có kết quả.", bang)

    if tab_hien == TEN_TAB[5]:
        tu_khoa = kq["chu_de"] or (rows_all[0].get("_tieu_de") if rows_all else "") or ""
        q = quote_plus(tu_khoa)
        if not q:
            st.info("Nhập chủ đề để có link tìm kiếm ở các trang khác.")
        else:
            if kq["urls"]:
                st.caption(f"Dùng tiêu đề bài vừa phân tích làm từ khóa: {tu_khoa}")
            st.caption("Xếp từ nguồn đáng tin nhất xuống nguồn cần tự kiểm tra.")
            nhom = {
                "Cơ sở dữ liệu học thuật uy tín": [
                    ("PubMed (y học)", f"https://pubmed.ncbi.nlm.nih.gov/?term={q}"),
                    ("ERIC (giáo dục)", f"https://eric.ed.gov/?q={q}"),
                    ("Google Scholar", f"https://scholar.google.com/scholar?q={q}"),
                    ("Semantic Scholar", f"https://www.semanticscholar.org/search?q={q}"),
                ],
                "Kho học thuật mở của trường, viện": [
                    ("CORE (kho PDF mở)", f"https://core.ac.uk/search?q={q}"),
                    ("BASE (kho học thuật mở)", f"https://www.base-search.net/Search/Results?lookfor={q}"),
                    ("OATD (luận văn truy cập mở)", f"https://oatd.org/oatd/search?q={q}&form=basic"),
                ],
                "Tiếng Việt": [
                    ("Google Scholar tiếng Việt", f"https://scholar.google.com/scholar?q={q}&hl=vi&lr=lang_vi"),
                    ("Tạp chí VJOL", f"https://www.google.com/search?q={q}+site%3Avjol.info.vn"),
                    ("Luận văn .edu.vn (PDF)", f"https://www.google.com/search?q={q}+luận+văn+site%3Aedu.vn+filetype%3Apdf"),
                ],
                "Sách": [
                    ("Google Books", f"https://www.google.com/search?tbm=bks&q={q}"),
                    ("Open Library", f"https://openlibrary.org/search?q={q}"),
                ],
                "Tìm rộng trên web, cần tự kiểm tra nguồn": [
                    ("Google: tìm file PDF", f"https://www.google.com/search?q={q}+filetype%3Apdf"),
                    ("Google: luận văn PDF", f"https://www.google.com/search?q={q}+thesis+OR+dissertation+filetype%3Apdf"),
                    ("ResearchGate (qua Google)", f"https://www.google.com/search?q={q}+site%3Aresearchgate.net"),
                ],
            }
            for i_nhom, (ten_nhom, ds) in enumerate(nhom.items()):
                tieu_de(ten_nhom)
                cols = st.container(key=f"links_nhom{i_nhom}").columns(4)
                for i, (ten, link) in enumerate(ds):
                    cols[i % 4].link_button(ten, link, width="stretch")

    if OA_LOI and not kq["urls"]:
        if not OA_KEY:
            canh_bao.warning("OpenAlex đang giới hạn lượt tra cứu (mã " + ", ".join(str(c) for c in sorted(set(OA_LOI))) + "), "
                             "nên mình đã lấy kết quả từ Crossref thay thế. Phần chủ đề và bài liên quan có thể chưa hiện đủ.")
        elif set(OA_LOI) & {401, 403}:
            canh_bao.warning("Khóa OpenAlex không hợp lệ, mình đã lấy kết quả từ Crossref thay thế.")
