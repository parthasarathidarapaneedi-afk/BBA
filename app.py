
import json
import os
import hashlib
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Dict, List, Optional, Tuple

import streamlit as st
import streamlit.components.v1 as components

SUPABASE_OK = False
try:
    from supabase import create_client
    SUPABASE_OK = True
except Exception:
    create_client = None

SET_POINTS = 35
COURT_CHG = [9, 18, 27]
PLAYERS = 5
ALL_PLAYERS = 10
MAX_SCORE_CAP = 39
DATA_FILE = "bb_data.json"
USERS_FILE = "bb_users.json"
ADMIN_USER = "Ballbadminton"
ADMIN_PASS = "partha@2025"

st.set_page_config(
    page_title="🏸 Ball Badminton Live",
    page_icon="🏸",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Inter:wght@400;500;600;700;800&display=swap');
#MainMenu,header,footer,[data-testid="stToolbar"],[data-testid="stDecoration"],[data-testid="stStatusWidget"],.stDeployButton,section[data-testid="stSidebar"],[data-testid="stSidebarNav"],.viewerBadge_container__1QSob,a[href*="streamlit.io"],a[href*="github.com"]{display:none!important;}
:root{--bg:#07101f;--surf:#0d1a2e;--card:#112038;--bdr:rgba(255,255,255,.07);--acc:#f97316;--blue:#3b82f6;--grn:#22c55e;--red:#ef4444;--gold:#f59e0b;--txt:#f0f4f8;--muted:#5a7090;--r:14px;}
html,body,.stApp{background:var(--bg)!important;color:var(--txt)!important;font-family:'Inter',sans-serif!important;}
.block-container{max-width:100%!important;padding:.5rem .65rem 4.6rem!important;}
.stButton>button{background:linear-gradient(135deg,#f97316,#c2410c)!important;color:#fff!important;border:none!important;font-weight:800!important;font-size:13px!important;padding:10px 12px!important;border-radius:12px!important;width:100%!important;box-shadow:0 4px 14px rgba(249,115,22,.24)!important;}
.stButton>button:disabled{opacity:.45!important;}
.stTextInput input,.stSelectbox>div>div,.stMultiSelect>div>div,.stNumberInput input{background:var(--card)!important;color:var(--txt)!important;border:1px solid var(--bdr)!important;border-radius:10px!important;}
[data-testid="stContainer"]{background:var(--card)!important;border:1px solid var(--bdr)!important;border-radius:var(--r)!important;padding:12px!important;}
.stTabs [data-baseweb="tab-list"]{background:var(--surf)!important;border-radius:10px!important;padding:4px!important;gap:4px!important;}
.stTabs [data-baseweb="tab"]{color:var(--muted)!important;border-radius:8px!important;font-weight:700!important;padding:8px 12px!important;font-size:12px!important;}
.stTabs [aria-selected="true"]{background:var(--acc)!important;color:#fff!important;}
[data-testid="stMetricValue"]{color:var(--txt)!important;font-weight:800!important;}
[data-testid="stMetricLabel"]{color:var(--muted)!important;}
.scoreboard{background:linear-gradient(135deg,var(--surf),var(--card));border:1px solid rgba(249,115,22,.15);border-radius:18px;padding:18px 14px 14px;position:relative;overflow:hidden;}
.scoreboard::before{content:'';position:absolute;left:0;right:0;top:0;height:3px;background:linear-gradient(90deg,var(--acc),var(--gold),var(--acc));}
.score-num{font-family:'Bebas Neue',sans-serif;font-size:92px;line-height:1;color:#fff;}
.score-num.hot{color:var(--acc);text-shadow:0 0 30px rgba(249,115,22,.4);}
.tname{font-size:17px;font-weight:800;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;}
.tmeta{font-size:12px;color:var(--muted);margin-top:2px;}
.badge{display:inline-block;padding:2px 9px;border-radius:12px;font-size:10px;font-weight:700;letter-spacing:.4px;text-transform:uppercase;}
.b-o{background:rgba(249,115,22,.15);color:#fdba74;border:1px solid rgba(249,115,22,.25);}
.b-b{background:rgba(59,130,246,.15);color:#93c5fd;border:1px solid rgba(59,130,246,.25);}
.b-g{background:rgba(34,197,94,.15);color:#86efac;border:1px solid rgba(34,197,94,.25);}
.b-r{background:rgba(239,68,68,.15);color:#fca5a5;border:1px solid rgba(239,68,68,.25);}
.b-gold{background:rgba(245,158,11,.15);color:#fbbf24;border:1px solid rgba(245,158,11,.25);}
.winner-wrap{background:linear-gradient(135deg,#f59e0b,#d97706);border-radius:16px;padding:16px;text-align:center;font-family:'Bebas Neue',sans-serif;font-size:26px;letter-spacing:2px;box-shadow:0 6px 24px rgba(245,158,11,.4);margin-bottom:12px;}
.court-alert{background:rgba(249,115,22,.10);border:1px solid rgba(249,115,22,.3);border-radius:12px;padding:12px;margin-bottom:10px;font-weight:800;color:#fdba74;}
.ev{font-size:11px;padding:5px 6px;border-bottom:1px solid var(--bdr);color:var(--muted);}
.ev:first-child{color:var(--txt);font-weight:700;}
.set-card,.sbox{background:var(--surf);border:1px solid var(--bdr);border-radius:10px;padding:10px;text-align:center;}
.sbox-n{font-family:'Bebas Neue',sans-serif;font-size:32px;color:var(--acc);}
.sbox-l{font-size:10px;color:var(--muted);text-transform:uppercase;letter-spacing:1px;}
.pbig .stButton>button{font-size:20px!important;padding:22px 10px!important;border-radius:15px!important;}
.pbig-b .stButton>button{background:linear-gradient(135deg,#3b82f6,#1d4ed8)!important;box-shadow:0 4px 14px rgba(59,130,246,.24)!important;}
.mob-nav-wrap{position:fixed;left:0;right:0;bottom:0;z-index:999;background:rgba(7,16,31,.97);border-top:1px solid rgba(255,255,255,.08);padding:8px 8px calc(8px + env(safe-area-inset-bottom));backdrop-filter:blur(8px);}
.mob-nav-grid{display:grid;grid-template-columns:repeat(5,1fr);gap:8px;}
.mob-nav-btn{background:var(--card);color:#fff;border:1px solid rgba(255,255,255,.08);border-radius:14px;padding:10px 6px;text-align:center;font-size:12px;font-weight:800;}
.mob-nav-btn.active{background:linear-gradient(135deg,#ff7a18,#d9480f);}
@media(max-width:768px){
  .block-container{padding:.35rem .45rem 4.7rem!important;}
  .score-num{font-size:72px!important;}
  .tname{font-size:14px!important;}
  .pbig .stButton>button{font-size:17px!important;padding:18px 8px!important;}
}
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def get_supabase():
    if not SUPABASE_OK:
        return None
    try:
        return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
    except Exception:
        return None

def using_supabase() -> bool:
    return get_supabase() is not None

def _hash(pw: str) -> str:
    return hashlib.sha256(pw.encode()).hexdigest()

def _safe(s: str, fb: str) -> str:
    s = (s or "").strip()
    return s if s else fb

def _nxt(i: int, n: int) -> int:
    return (i + 1) % n

def _build_ord(p5, idxs):
    out = []
    for idx in idxs:
        if not (1 <= idx <= len(p5)):
            return []
        out.append(p5[idx-1])
    return out

def _snap(m):
    d = asdict(m)
    d["history"] = []
    return d

def _auto_refresh(ms=1000):
    components.html(f"<script>setTimeout(()=>window.parent.location.reload(),{ms});</script>", height=0)

def users_load() -> dict:
    sb = get_supabase()
    if sb:
        try:
            res = sb.table("viewers").select("*").execute()
            out = {}
            for row in (res.data or []):
                out[row["username"]] = {
                    "name": row.get("name",""),
                    "contact": row.get("contact",""),
                    "pw_hash": row.get("pw_hash",""),
                    "created": row.get("created_at",""),
                    "created_by_admin": row.get("created_by_admin", False),
                    "role": "viewer",
                }
            return out
        except Exception:
            pass
    if os.path.exists(USERS_FILE):
        try:
            with open(USERS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}

def users_save(users: dict):
    sb = get_supabase()
    if sb:
        try:
            rows = []
            for uname, u in users.items():
                rows.append({
                    "username": uname,
                    "name": u.get("name",""),
                    "contact": u.get("contact",""),
                    "pw_hash": u.get("pw_hash",""),
                    "created_at": u.get("created",""),
                    "created_by_admin": u.get("created_by_admin", False),
                })
            if rows:
                sb.table("viewers").upsert(rows).execute()
            return
        except Exception:
            pass
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, indent=2)

def user_register(name: str, contact: str, username: str, password: str, created_by_admin: bool = False) -> Tuple[bool, str]:
    users = users_load()
    uname = (username or "").strip().lower()
    if not uname or not password or not name or not contact:
        return False, "All fields are required"
    if len(password) < 6:
        return False, "Password must be at least 6 characters"
    if uname in users:
        return False, "Username already taken"
    for u in users.values():
        if u.get("contact","").strip().lower() == contact.strip().lower():
            return False, "This mobile/email is already registered"
    users[uname] = {
        "name": name.strip(),
        "contact": contact.strip(),
        "pw_hash": _hash(password),
        "created": datetime.now().strftime("%d %b %Y %H:%M"),
        "created_by_admin": created_by_admin,
        "role": "viewer",
    }
    users_save(users)
    return True, f"Registered! Login as '{uname}'"

def user_login(username: str, password: str) -> Tuple[bool, str, dict]:
    users = users_load()
    uname = (username or "").strip().lower()
    if uname not in users:
        return False, "Username not found", {}
    u = users[uname]
    if u["pw_hash"] != _hash(password):
        return False, "Wrong password", {}
    return True, "OK", u

def data_default() -> dict:
    return {"match": None, "setup_done": False, "history": [], "tournament": [], "t_info": {}, "updated_at": ""}

def data_load() -> dict:
    sb = get_supabase()
    if sb:
        try:
            res = sb.table("matches").select("*").eq("id","app_state").execute()
            if res.data:
                payload = res.data[0].get("data") or {}
                base = data_default()
                base.update(payload)
                return base
        except Exception:
            pass
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                d = json.load(f)
            base = data_default()
            base.update(d)
            return base
        except Exception:
            pass
    return data_default()

def data_save(data: dict):
    data["updated_at"] = datetime.now().strftime("%d %b %Y %H:%M:%S")
    sb = get_supabase()
    if sb:
        try:
            sb.table("matches").upsert({
                "id": "app_state",
                "data": data,
                "updated_at": datetime.now().isoformat()
            }).execute()
            return
        except Exception:
            pass
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False)

@dataclass
class Match:
    tA: str; tB: str
    allA: List[str]; allB: List[str]
    onA: List[str]; onB: List[str]
    ordA: List[str]; ordB: List[str]
    setno: int; sA: int; sB: int; scA: int; scB: int
    srv: str; swapped: bool
    curA: Optional[str]; curB: Optional[str]
    nxtA: int; nxtB: int
    subA: int; subB: int; toA: int; toB: int
    ms: Dict[int,bool]; first_court_popup_point: Optional[int]
    history: List[Dict]; events: List[str]
    over: bool; winner: Optional[str]
    psA: List[int]; psB: List[int]
    ppA: Dict[str,int]; ppB: Dict[str,int]
    started: str; ended: Optional[str]; mid: str
    tnm: Optional[str]; trd: Optional[str]
    target: int = SET_POINTS
    updated_at: Optional[str] = None

def _restore(d):
    if not d:
        return None
    try:
        return Match(**d)
    except Exception:
        return None

def _push_event(m: Match, txt: str):
    m.events.insert(0, txt)
    m.events = m.events[:60]
    m.updated_at = datetime.now().strftime("%d %b %Y %H:%M:%S")

def current_server(m: Match) -> str:
    return (m.curA if m.srv == "A" else m.curB) or "—"

def equal_target(score: int) -> int:
    if score < 34:
        return SET_POINTS
    if score == 34:
        return 36
    if score == 36:
        return 39
    return 39

def maybe_update_target(m: Match):
    if m.scA == m.scB:
        if m.scA >= 36:
            m.target = 39
        elif m.scA >= 34:
            m.target = 36
        else:
            m.target = 35

def score_cap_reached(m: Match, team: str) -> bool:
    score = m.scA if team == "A" else m.scB
    return score >= MAX_SCORE_CAP or m.over

def new_match(tA,tB,allA,allB,pA,pB,oA,oB,first,tnm=None,trd=None) -> Match:
    cA,cB,nA,nB = (oA[0],None,1,0) if first=="A" else (None,oB[0],0,1)
    now = datetime.now()
    return Match(
        tA=tA,tB=tB,allA=allA,allB=allB,onA=pA,onB=pB,ordA=oA,ordB=oB,
        setno=1,sA=0,sB=0,scA=0,scB=0,srv=first,swapped=False,
        curA=cA,curB=cB,nxtA=nA,nxtB=nB,subA=3,subB=3,toA=1,toB=1,
        ms={9:False,18:False,27:False}, first_court_popup_point=None,
        history=[],events=[f"Match started · {tA if first=='A' else tB} serves first"],
        over=False,winner=None,psA=[],psB=[],
        ppA={p:0 for p in pA}, ppB={p:0 for p in pB},
        started=now.strftime("%d %b %Y %H:%M"), ended=None,
        mid=now.strftime("%Y%m%d%H%M%S"), tnm=tnm, trd=trd, target=35,
        updated_at=now.strftime("%d %b %Y %H:%M:%S")
    )

def do_point(winner: str):
    data = data_load()
    m = _restore(data.get("match"))
    if not m or m.over or score_cap_reached(m, winner):
        return
    m.history.append(_snap(m))
    m.history = m.history[-20:]

    if winner == "A":
        if m.scA >= MAX_SCORE_CAP:
            return
        m.scA += 1
        if m.curA:
            m.ppA[m.curA] = m.ppA.get(m.curA, 0) + 1
    else:
        if m.scB >= MAX_SCORE_CAP:
            return
        m.scB += 1
        if m.curB:
            m.ppB[m.curB] = m.ppB.get(m.curB, 0) + 1

    if winner != m.srv:
        m.srv = winner
        if winner == "A":
            m.curA = m.ordA[m.nxtA]
            m.nxtA = _nxt(m.nxtA, PLAYERS)
        else:
            m.curB = m.ordB[m.nxtB]
            m.nxtB = _nxt(m.nxtB, PLAYERS)

    _push_event(m, f"▸ {m.tA if winner=='A' else m.tB}  {m.scA}–{m.scB}  srv:{current_server(m)}")

    if m.first_court_popup_point is None:
        for p in COURT_CHG:
            if not m.ms.get(p, False) and (m.scA == p or m.scB == p):
                m.ms[p] = True
                m.first_court_popup_point = p
                _push_event(m, f"🔄 First to {p} reached by {m.tA if m.scA==p else m.tB}")
                break

    maybe_update_target(m)

    if m.first_court_popup_point and not (m.scA == m.first_court_popup_point or m.scB == m.first_court_popup_point):
        # hide popup after the exact trigger point has passed
        m.first_court_popup_point = None

    if m.target == 39 and (m.scA == 39 or m.scB == 39):
        m.over = True
        m.winner = "A" if m.scA == 39 else "B"
    elif max(m.scA, m.scB) >= m.target and abs(m.scA - m.scB) >= 2:
        set_winner = "A" if m.scA > m.scB else "B"
        if set_winner == "A":
            m.sA += 1
        else:
            m.sB += 1
        m.psA.append(m.scA); m.psB.append(m.scB)
        _push_event(m, f"✅ Set {m.setno} → {m.tA if set_winner=='A' else m.tB} ({m.scA}–{m.scB})")

        if m.sA == 2 or m.sB == 2:
            m.over = True
            m.winner = "A" if m.sA == 2 else "B"
        else:
            m.setno += 1
            m.scA = 0; m.scB = 0
            m.subA = 3; m.subB = 3; m.toA = 1; m.toB = 1
            m.ms = {9:False,18:False,27:False}
            m.first_court_popup_point = None
            m.target = 35
            _push_event(m, f"▶️ Set {m.setno} begins")

    if m.over:
        if not m.ended:
            m.ended = datetime.now().strftime("%d %b %Y %H:%M")
        if m.winner in ("A","B"):
            _push_event(m, f"🏆 {m.tA if m.winner=='A' else m.tB} wins!")
        hist = data.get("history", [])
        hist.append({
            "id": m.mid, "date": m.started, "tA": m.tA, "tB": m.tB,
            "sA": m.sA, "sB": m.sB, "sets": list(zip(m.psA, m.psB)),
            "winner": m.tA if m.winner == "A" else m.tB,
            "tnm": m.tnm, "trd": m.trd,
            "ppA": dict(m.ppA), "ppB": dict(m.ppB),
        })
        data["history"] = hist

    data["match"] = asdict(m)
    data["setup_done"] = True
    data_save(data)

def do_undo():
    data = data_load()
    m = _restore(data.get("match"))
    if not m or not m.history:
        return
    data["match"] = m.history.pop()
    data_save(data)

def do_court():
    data = data_load()
    m = _restore(data.get("match"))
    if not m:
        return
    m.swapped = not m.swapped
    m.first_court_popup_point = None
    _push_event(m, "🔄 Court sides changed")
    data["match"] = asdict(m)
    data_save(data)

def do_timeout(team: str):
    data = data_load()
    m = _restore(data.get("match"))
    if not m:
        return
    if team == "A" and m.toA > 0:
        m.toA -= 1
        _push_event(m, f"⏱️ Timeout: {m.tA}")
    elif team == "B" and m.toB > 0:
        m.toB -= 1
        _push_event(m, f"⏱️ Timeout: {m.tB}")
    data["match"] = asdict(m)
    data_save(data)

def do_sub(team: str, on: str, off: str):
    data = data_load()
    m = _restore(data.get("match"))
    if not m or not on or not off or on == off:
        return
    if team == "A":
        if m.subA <= 0 or on in m.onA or off not in m.onA:
            return
        m.onA[m.onA.index(off)] = on
        m.ppA.setdefault(on, 0)
        m.subA -= 1
        _push_event(m, f"🔁 {m.tA}: {off}→{on}")
    else:
        if m.subB <= 0 or on in m.onB or off not in m.onB:
            return
        m.onB[m.onB.index(off)] = on
        m.ppB.setdefault(on, 0)
        m.subB -= 1
        _push_event(m, f"🔁 {m.tB}: {off}→{on}")
    data["match"] = asdict(m)
    data_save(data)

def admin_adjust_score(team: str, value: int):
    data = data_load()
    m = _restore(data.get("match"))
    if not m or m.over:
        return
    value = max(0, min(MAX_SCORE_CAP, int(value)))
    if team == "A":
        m.scA = value
    else:
        m.scB = value
    maybe_update_target(m)
    _push_event(m, f"✏️ Score adjusted → {m.tA} {m.scA} · {m.tB} {m.scB}")
    data["match"] = asdict(m)
    data_save(data)

for k, v in [
    ("role", None), ("username", ""), ("user_name", ""), ("tab", "score"),
    ("show_score_adjust", False),
    ("setup", {
        "tA":"", "tB":"", "allA":[""]*ALL_PLAYERS, "allB":[""]*ALL_PLAYERS,
        "ordA":[1,2,3,4,5], "ordB":[1,2,3,4,5], "first":"A", "tnm":"", "trd":""
    }),
]:
    if k not in st.session_state:
        st.session_state[k] = v

# persist lightweight auth across browser reloads for viewer mode
try:
    qp_role = st.query_params.get("role")
    qp_user = st.query_params.get("user")
    if st.session_state.role is None and qp_role == "viewer":
        st.session_state.role = "viewer"
        st.session_state.username = qp_user or ""
        st.session_state.user_name = qp_user or "Viewer"
except Exception:
    pass

if st.session_state.role is None:
    st.markdown("""
    <div style='text-align:center;padding:24px 0 12px'>
      <div style='font-size:58px'>🏸</div>
      <div style='font-family:Bebas Neue,sans-serif;font-size:38px;letter-spacing:3px;margin-top:4px'>BALL BADMINTON LIVE</div>
      <div style='color:#5a7090;font-size:12px;margin-top:3px'>Mobile Scoreboard</div>
    </div>
    """, unsafe_allow_html=True)
    login_tab, reg_tab, admin_tab = st.tabs(["🔑 Viewer Login", "📝 Register", "🔐 Admin"])
    with login_tab:
        vu = st.text_input("Username", placeholder="viewer username", key="vl_u")
        vp = st.text_input("Password", placeholder="password", type="password", key="vl_p")
        if st.button("▶️ Open Live Score", key="viewer_login_btn", use_container_width=True):
            ok, msg, udata = user_login(vu, vp)
            if ok:
                st.session_state.role = "viewer"
                st.session_state.username = vu.strip().lower()
                st.session_state.user_name = udata.get("name","Viewer")
                try:
                    st.query_params["role"] = "viewer"
                    st.query_params["user"] = st.session_state.user_name
                except Exception:
                    pass
                st.rerun()
            st.error(f"❌ {msg}")
    with reg_tab:
        rn = st.text_input("Full Name", placeholder="Your name", key="reg_name")
        rc = st.text_input("Mobile / Email", placeholder="9876543210 or email", key="reg_contact")
        ru = st.text_input("Choose Username", placeholder="viewer username", key="reg_user")
        rp = st.text_input("Create Password", placeholder="Min 6 characters", type="password", key="reg_pass")
        rp2 = st.text_input("Confirm Password", placeholder="Re-enter password", type="password", key="reg_pass2")
        if st.button("✅ Create Account", key="reg_btn", use_container_width=True):
            if rp != rp2:
                st.error("❌ Passwords don't match")
            else:
                ok, msg = user_register(rn, rc, ru, rp, created_by_admin=False)
                if ok:
                    st.success(f"✅ {msg}")
                else:
                    st.error(f"❌ {msg}")
    with admin_tab:
        au = st.text_input("Username", placeholder="Admin username", key="al_u")
        ap = st.text_input("Password", placeholder="Admin password", type="password", key="al_p")
        if st.button("🔐 Admin Login", key="admin_login_btn", use_container_width=True):
            if au == ADMIN_USER and ap == ADMIN_PASS:
                st.session_state.role = "admin"
                st.session_state.username = ADMIN_USER
                st.session_state.user_name = "Admin"
                st.rerun()
            else:
                st.error("❌ Invalid admin credentials")
    st.stop()

is_admin = st.session_state.role == "admin"
data = data_load()
match = _restore(data.get("match"))

nav_items = [("score","🏸 Score"),("stats","📊 Stats"),("history","📜 History")]
if is_admin:
    nav_items += [("tournament","🏆 Tournament"),("users","👥 Users"),("admin","⚙️ Admin")]
nav_cols = st.columns(len(nav_items)+1)
for i,(k,lbl) in enumerate(nav_items):
    with nav_cols[i]:
        if st.button(lbl, key=f"nav_{k}", use_container_width=True):
            st.session_state.tab = k
            st.rerun()
with nav_cols[-1]:
    if st.button("🚪 Exit", key="logout_btn_top", use_container_width=True):
        st.session_state.role = None
        st.session_state.username = ""
        st.session_state.user_name = ""
        try:
            st.query_params.clear()
        except Exception:
            pass
        st.rerun()
st.markdown("<hr style='border-color:rgba(255,255,255,.06);margin:4px 0 8px'>", unsafe_allow_html=True)
tab = st.session_state.tab

if not is_admin:
    if tab not in ("score","stats","history"):
        st.session_state.tab = "score"
        tab = "score"
    if not match:
        st.info("⏳ No active match right now")
        _auto_refresh(1500)
        st.stop()
    _auto_refresh(1000)

    m = match
    if tab == "score":
        if m.first_court_popup_point and (m.scA == m.first_court_popup_point or m.scB == m.first_court_popup_point):
            st.markdown(f"<div class='court-alert'>🔄 Court change at {m.first_court_popup_point} — shown only when first reached</div>", unsafe_allow_html=True)
        if m.over:
            st.markdown(f"<div class='winner-wrap'>🏆 {m.tA if m.winner=='A' else m.tB} WINS!</div>", unsafe_allow_html=True)
        lt = "B" if m.swapped else "A"
        rt = "A" if m.swapped else "B"
        tn = lambda t:m.tA if t=="A" else m.tB
        sc = lambda t:m.scA if t=="A" else m.scB
        ss = lambda t:m.sA if t=="A" else m.sB
        st.markdown(f"""
        <div class='scoreboard'>
          <div style='display:flex;justify-content:space-between;align-items:flex-end;gap:10px'>
            <div style='flex:1;min-width:0'>
              <div class='tname'>{'🟠 ' if m.srv==lt else ''}{tn(lt)}</div>
              <div class='score-num {'hot' if m.srv==lt else ''}'>{sc(lt)}</div>
              <div class='tmeta'>Sets: {ss(lt)} · Left</div>
            </div>
            <div style='opacity:.32;font-size:18px;font-weight:700'>vs</div>
            <div style='flex:1;min-width:0;text-align:right'>
              <div class='tname'>{'🟠 ' if m.srv==rt else ''}{tn(rt)}</div>
              <div class='score-num {'hot' if m.srv==rt else ''}'>{sc(rt)}</div>
              <div class='tmeta'>Sets: {ss(rt)} · Right</div>
            </div>
          </div>
          <div style='text-align:center;color:#5a7090;font-size:10px;margin-top:8px'>
            SET {m.setno}/3 · TARGET {m.target} · FINAL CAP {MAX_SCORE_CAP}
          </div>
        </div>
        """, unsafe_allow_html=True)
        c1,c2,c3 = st.columns(3)
        with c1: st.metric("Serving", m.tA if m.srv=="A" else m.tB)
        with c2: st.metric("Server", current_server(m))
        with c3: st.metric("Target", m.target)
        with st.container(border=True):
            st.markdown("**Live Events**")
            for e in m.events[:12]:
                st.markdown(f"<div class='ev'>{e}</div>", unsafe_allow_html=True)

    elif tab == "stats":
        total = m.scA + m.scB + sum(m.psA) + sum(m.psB)
        c1,c2,c3,c4 = st.columns(4)
        for col,val,lbl in [(c1,f"Set {m.setno}","Set"),(c2,f"{m.sA}–{m.sB}","Sets"),(c3,f"{m.scA}–{m.scB}","Score"),(c4,total,"Total")]:
            with col:
                st.markdown(f"<div class='sbox'><div class='sbox-n'>{val}</div><div class='sbox-l'>{lbl}</div></div>", unsafe_allow_html=True)
        p1,p2 = st.columns(2)
        with p1:
            st.markdown(f"**{m.tA}**")
            for p,pts in sorted(m.ppA.items(), key=lambda x:-x[1]):
                st.write(f"{p}: {pts}")
        with p2:
            st.markdown(f"**{m.tB}**")
            for p,pts in sorted(m.ppB.items(), key=lambda x:-x[1]):
                st.write(f"{p}: {pts}")

    elif tab == "history":
        hist = data.get("history",[])
        if not hist:
            st.info("No completed matches yet.")
        else:
            for h in reversed(hist):
                with st.container(border=True):
                    st.markdown(f"### {h['tA']} vs {h['tB']}")
                    st.caption(h["date"])
                    st.write(f"Sets: **{h['sA']}–{h['sB']}** · Winner: **{h['winner']}**")

    active = st.session_state.tab
    st.markdown(f"""
    <div class='mob-nav-wrap'>
      <div class='mob-nav-grid'>
        <div class='mob-nav-btn {'active' if active=='score' else ''}'>🏸<br>Score</div>
        <div class='mob-nav-btn {'active' if active=='stats' else ''}'>📊<br>Stats</div>
        <div class='mob-nav-btn {'active' if active=='history' else ''}'>📜<br>History</div>
        <div class='mob-nav-btn'>👤<br>User</div>
        <div class='mob-nav-btn'>🔄<br>Live</div>
      </div>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

if tab in ("users","admin","history","tournament") and not match and tab != "users" and tab != "admin" and tab != "history" and tab != "tournament":
    pass

if not match and tab == "score":
    st.markdown("<div style='font-family:Bebas Neue,sans-serif;font-size:28px;letter-spacing:2px;margin-bottom:12px'>MATCH SETUP</div>", unsafe_allow_html=True)
    setup = st.session_state.setup
    with st.expander("🏆 Tournament (optional)"):
        tnm = st.text_input("Tournament Name", value=setup.get("tnm",""))
        trd = st.text_input("Round", value=setup.get("trd",""))
    c1,c2 = st.columns(2)
    with c1: tA = st.text_input("Team A", value=setup.get("tA",""))
    with c2: tB = st.text_input("Team B", value=setup.get("tB",""))
    st.markdown("### 👥 Enter All Players")
    ca,cb = st.columns(2)
    allA,allB = [],[]
    with ca:
        st.markdown(f"**{tA or 'Team A'}**")
        for i in range(ALL_PLAYERS):
            allA.append(st.text_input(f"Player {i+1}", value=setup["allA"][i], key=f"pA{i}"))
    with cb:
        st.markdown(f"**{tB or 'Team B'}**")
        for i in range(ALL_PLAYERS):
            allB.append(st.text_input(f"Player {i+1}", value=setup["allB"][i], key=f"pB{i}"))
    allA_f = [_safe(v, f"A{i+1}") for i,v in enumerate(allA)]
    allB_f = [_safe(v, f"B{i+1}") for i,v in enumerate(allB)]
    st.markdown("### ⭐ Select 5 Starters")
    s1,s2 = st.columns(2)
    with s1: mpA = st.multiselect(f"{tA or 'Team A'}", allA_f, default=allA_f[:PLAYERS], max_selections=PLAYERS, key="mpA")
    with s2: mpB = st.multiselect(f"{tB or 'Team B'}", allB_f, default=allB_f[:PLAYERS], max_selections=PLAYERS, key="mpB")
    errs = []; oA2=[]; oB2=[]
    if len(mpA) == PLAYERS and len(mpB) == PLAYERS:
        st.markdown("### 🔁 Service Order")
        o1,o2 = st.columns(2)
        oAi,oBi = [],[]
        with o1:
            for k in range(PLAYERS):
                opts = [f"{i+1}. {mpA[i]}" for i in range(PLAYERS)]
                sel = st.selectbox(f"Serve {k+1}", opts, index=setup["ordA"][k]-1, key=f"oA{k}")
                oAi.append(int(sel.split(".")[0]))
        with o2:
            for k in range(PLAYERS):
                opts = [f"{i+1}. {mpB[i]}" for i in range(PLAYERS)]
                sel = st.selectbox(f"Serve {k+1}", opts, index=setup["ordB"][k]-1, key=f"oB{k}")
                oBi.append(int(sel.split(".")[0]))
        if len(set(oAi)) != 5: errs.append("Team A service order must be unique")
        if len(set(oBi)) != 5: errs.append("Team B service order must be unique")
        oA2 = _build_ord(list(mpA), oAi)
        oB2 = _build_ord(list(mpB), oBi)
        if not oA2 or not oB2: errs.append("Invalid service order")
        fs_label = st.radio("First serve", [tA or "Team A", tB or "Team B"], horizontal=True)
        fs = "A" if fs_label == (tA or "Team A") else "B"
    else:
        fs = "A"; errs.append("Select exactly 5 players per team")
    for e in errs:
        st.error(e)
    if st.button("▶️ START MATCH", use_container_width=True, disabled=bool(errs)):
        m = new_match(_safe(tA,"Team A"), _safe(tB,"Team B"), allA_f, allB_f, list(mpA), list(mpB), oA2, oB2, fs, tnm or None, trd or None)
        data["match"] = asdict(m)
        data["setup_done"] = True
        data_save(data)
        st.rerun()

elif tab == "score":
    m = match
    if not m:
        st.info("No active match. Use Score tab to start a new match.")
    else:
        if m.first_court_popup_point and (m.scA == m.first_court_popup_point or m.scB == m.first_court_popup_point):
            st.markdown(f"<div class='court-alert'>🔄 Court change popup shown only when {m.first_court_popup_point} is first reached</div>", unsafe_allow_html=True)
        if m.over:
            st.markdown(f"<div class='winner-wrap'>🏆 {m.tA if m.winner=='A' else m.tB} WINS THE MATCH!</div>", unsafe_allow_html=True)
        lt = "B" if m.swapped else "A"
        rt = "A" if m.swapped else "B"
        tn = lambda t:m.tA if t=="A" else m.tB
        sc = lambda t:m.scA if t=="A" else m.scB
        ss = lambda t:m.sA if t=="A" else m.sB
        st.markdown(f"""
        <div class='scoreboard'>
          <div style='display:flex;justify-content:space-between;align-items:flex-end;gap:10px'>
            <div style='flex:1;min-width:0'>
              <div class='tname'>{'🟠 ' if m.srv==lt else ''}{tn(lt)}</div>
              <div class='score-num {'hot' if m.srv==lt else ''}'>{sc(lt)}</div>
              <div class='tmeta'>Sets: {ss(lt)} · Left</div>
            </div>
            <div style='opacity:.32;font-size:18px;font-weight:700'>vs</div>
            <div style='flex:1;min-width:0;text-align:right'>
              <div class='tname'>{'🟠 ' if m.srv==rt else ''}{tn(rt)}</div>
              <div class='score-num {'hot' if m.srv==rt else ''}'>{sc(rt)}</div>
              <div class='tmeta'>Sets: {ss(rt)} · Right</div>
            </div>
          </div>
          <div style='text-align:center;color:#5a7090;font-size:10px;margin-top:8px'>
            SET {m.setno}/3 · TARGET {m.target} · FINAL CAP {MAX_SCORE_CAP}
          </div>
        </div>
        """, unsafe_allow_html=True)
        c1,c2,c3,c4 = st.columns(4)
        with c1: st.metric("Serving", m.tA if m.srv=="A" else m.tB)
        with c2: st.metric("Server", current_server(m))
        with c3: st.metric("Target", m.target)
        with c4: st.metric("Max", MAX_SCORE_CAP)

        pb1,pb2 = st.columns(2)
        with pb1:
            st.markdown("<div class='pbig'>", unsafe_allow_html=True)
            if st.button(f"＋ {m.tA}", key="ptA", use_container_width=True, disabled=(m.over or m.scA>=MAX_SCORE_CAP)):
                do_point("A"); st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)
        with pb2:
            st.markdown("<div class='pbig pbig-b'>", unsafe_allow_html=True)
            if st.button(f"＋ {m.tB}", key="ptB", use_container_width=True, disabled=(m.over or m.scB>=MAX_SCORE_CAP)):
                do_point("B"); st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

        row1 = st.columns(3)
        with row1[0]:
            if st.button("🔄 Court", use_container_width=True):
                do_court(); st.rerun()
        with row1[1]:
            if st.button("↩️ Undo", use_container_width=True, disabled=not m.history):
                do_undo(); st.rerun()
        with row1[2]:
            if st.button("⚙️ Score Adjust", use_container_width=True):
                st.session_state.show_score_adjust = not st.session_state.show_score_adjust
                st.rerun()

        if st.session_state.show_score_adjust:
            with st.container(border=True):
                st.markdown("### Manual Score Adjust")
                a1,a2 = st.columns(2)
                with a1:
                    new_a = st.number_input(f"{m.tA} Score", min_value=0, max_value=MAX_SCORE_CAP, value=int(m.scA), step=1, key="adjA")
                    if st.button(f"Set {m.tA}", key="set_adj_a", use_container_width=True):
                        admin_adjust_score("A", new_a); st.rerun()
                with a2:
                    new_b = st.number_input(f"{m.tB} Score", min_value=0, max_value=MAX_SCORE_CAP, value=int(m.scB), step=1, key="adjB")
                    if st.button(f"Set {m.tB}", key="set_adj_b", use_container_width=True):
                        admin_adjust_score("B", new_b); st.rerun()

        with st.container(border=True):
            st.markdown("### Substitutions & Timeouts")
            sc1,sc2 = st.columns(2)
            for team,col in [("A",sc1),("B",sc2)]:
                fm = _restore(data_load().get("match")) or m
                tname = fm.tA if team=="A" else fm.tB
                subs = fm.subA if team=="A" else fm.subB
                tos = fm.toA if team=="A" else fm.toB
                p_on = fm.onA if team=="A" else fm.onB
                all_p = fm.allA if team=="A" else fm.allB
                with col:
                    st.markdown(f"**{tname}** <span class='badge {'b-g' if subs>0 else 'b-r'}'>Subs {subs}</span> <span class='badge {'b-b' if tos>0 else 'b-r'}'>T/O {tos}</span>", unsafe_allow_html=True)
                    bench = [p for p in all_p if p and p not in p_on]
                    if subs > 0 and bench:
                        on_p = st.selectbox("In", bench, key=f"in_{team}")
                        off_p = st.selectbox("Out", p_on, key=f"out_{team}")
                        if st.button(f"Sub {tname}", key=f"sub_{team}", use_container_width=True):
                            do_sub(team, on_p, off_p); st.rerun()
                    if tos > 0:
                        if st.button(f"Timeout {tname}", key=f"to_{team}", use_container_width=True):
                            do_timeout(team); st.rerun()

        with st.container(border=True):
            st.markdown("**Live Events**")
            for e in m.events[:16]:
                st.markdown(f"<div class='ev'>{e}</div>", unsafe_allow_html=True)

elif tab == "stats":
    if not match:
        st.info("No active match yet.")
    else:
        m = match
        total = m.scA + m.scB + sum(m.psA) + sum(m.psB)
        c1,c2,c3,c4 = st.columns(4)
        for col,val,lbl in [(c1,f"Set {m.setno}","Set"),(c2,f"{m.sA}–{m.sB}","Sets"),(c3,f"{m.scA}–{m.scB}","Score"),(c4,total,"Total Pts")]:
            with col:
                st.markdown(f"<div class='sbox'><div class='sbox-n'>{val}</div><div class='sbox-l'>{lbl}</div></div>", unsafe_allow_html=True)
        p1,p2 = st.columns(2)
        with p1:
            st.markdown(f"**{m.tA}**")
            for p,pts in sorted(m.ppA.items(), key=lambda x:-x[1]):
                st.write(f"{p}: {pts}")
        with p2:
            st.markdown(f"**{m.tB}**")
            for p,pts in sorted(m.ppB.items(), key=lambda x:-x[1]):
                st.write(f"{p}: {pts}")

elif tab == "history":
    hist = data.get("history",[])
    if not hist:
        st.info("No completed matches yet.")
    else:
        for h in reversed(hist):
            with st.container(border=True):
                st.markdown(f"### {h['tA']} vs {h['tB']}")
                st.caption(h["date"])
                st.write(f"Sets: **{h['sA']}–{h['sB']}** · Winner: **{h['winner']}**")

elif tab == "tournament":
    st.markdown("## Tournament")
    with st.container(border=True):
        tn2 = st.text_input("Tournament Name", placeholder="e.g. District Championship", key="tn2")
        ntm = st.selectbox("Teams", [4,8,16], key="ntm")
        cols = st.columns(2)
        tnames = []
        for i in range(ntm):
            with cols[i % 2]:
                tnames.append(st.text_input(f"Team {i+1}", key=f"brt{i}"))
        if st.button("🎯 Generate Bracket", use_container_width=True):
            names = [_safe(t, f"Team {i+1}") for i,t in enumerate(tnames)]
            import random
            random.shuffle(names)
            data["tournament"] = [{"r":"Round 1","tA":names[i],"tB":names[i+1],"w":None} for i in range(0,len(names)-1,2)]
            data["t_info"] = {"name": tn2, "teams": names}
            data_save(data)
            st.rerun()
    if data.get("tournament"):
        st.markdown(f"### 🎯 {data.get('t_info',{}).get('name','Tournament')}")
        for i,mb in enumerate(data["tournament"]):
            with st.container(border=True):
                c1,c2,c3 = st.columns([2,.4,2])
                with c1: st.write(f"**{mb['tA']}**")
                with c2: st.write("vs")
                with c3: st.write(f"**{mb['tB']}**")
                if not mb["w"]:
                    w = st.radio("Winner", [mb["tA"],mb["tB"]], key=f"bw{i}", horizontal=True)
                    if st.button("✅ Confirm", key=f"bc{i}"):
                        data["tournament"][i]["w"] = w
                        data_save(data)
                        st.rerun()
                else:
                    st.markdown(f"<span class='badge b-gold'>🏆 {mb['w']}</span>", unsafe_allow_html=True)

elif tab == "users":
    st.markdown("## Users")
    users = users_load()
    st.markdown("### Registered Viewers")
    if not users:
        st.info("No viewers registered yet.")
    else:
        st.write(f"**{len(users)} registered viewer(s)**")
        for uname,ud in users.items():
            with st.container(border=True):
                c1,c2,c3 = st.columns([2,2,1])
                with c1:
                    st.markdown(f"**{ud.get('name','—')}**")
                    st.caption(f"@{uname}")
                with c2:
                    st.write(ud.get("contact","—"))
                    st.caption(f"Joined: {ud.get('created','—')}")
                with c3:
                    st.write("Admin" if ud.get("created_by_admin") else "Self")
    st.markdown("---")
    st.markdown("### ➕ Add Viewer Manually")
    with st.container(border=True):
        mn = st.text_input("Name", placeholder="Full name", key="mu_n")
        mc = st.text_input("Mobile/Email", placeholder="Contact", key="mu_c")
        muu = st.text_input("Username", placeholder="username", key="mu_u")
        mp = st.text_input("Password", placeholder="Min 6 chars", type="password", key="mu_p")
        if st.button("✅ Add Viewer", use_container_width=True, key="mu_btn"):
            ok,msg = user_register(mn,mc,muu,mp,created_by_admin=True)
            if ok: st.success(f"✅ {msg}")
            else: st.error(f"❌ {msg}")

elif tab == "admin":
    st.markdown("## Admin Panel")
    with st.container(border=True):
        if match:
            m = match
            c1,c2,c3,c4 = st.columns(4)
            with c1: st.metric("Match", f"{m.tA} vs {m.tB}")
            with c2: st.metric("Set", f"{m.setno}/3")
            with c3: st.metric("Score", f"{m.scA}–{m.scB}")
            with c4: st.metric("Saved In", "Supabase" if using_supabase() else "JSON")
        else:
            st.info("No active match.")
    with st.container(border=True):
        st.write(f"**Registered viewers:** {len(users_load())}")
        st.write(f"**Matches played:** {len(data.get('history',[]))}")
        st.write(f"**Storage:** {'Supabase with JSON fallback' if using_supabase() else 'JSON only'}")
        st.write("**Rules:** Court popup once for first reach · Manual score adjust hidden until opened · Max score 39")
