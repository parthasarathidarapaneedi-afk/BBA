import json
import os
import hashlib
import random
import string
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
DATA_FILE = "bb_data.json"
USERS_FILE = "bb_users.json"
ADMIN_USER = "Ballbadminton"
ADMIN_PASS = "partha@2025"

st.set_page_config(page_title="🏸 Ball Badminton Live", page_icon="🏸", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
#MainMenu,header,footer,[data-testid="stToolbar"],[data-testid="stDecoration"],[data-testid="stStatusWidget"],.stDeployButton,section[data-testid="stSidebar"],[data-testid="stSidebarNav"],a[href*="streamlit.io"],a[href*="github.com"]{display:none!important;}
:root{--bg:#07101f;--surf:#0d1a2e;--card:#112038;--bdr:rgba(255,255,255,.07);--acc:#f97316;--blue:#3b82f6;--txt:#f0f4f8;--muted:#7b90b1;}
html,body,.stApp{background:var(--bg)!important;color:var(--txt)!important;}
.block-container{max-width:100%!important;padding:.45rem .55rem 1rem!important;}
.stButton>button{width:100%!important;border:none!important;border-radius:14px!important;color:#fff!important;font-weight:800!important;padding:12px 14px!important;background:linear-gradient(135deg,#f97316,#c2410c)!important;box-shadow:0 4px 14px rgba(249,115,22,.22)!important;}
.stTextInput input,.stSelectbox>div>div,.stMultiSelect>div>div,.stNumberInput input{background:var(--card)!important;color:var(--txt)!important;border:1px solid var(--bdr)!important;border-radius:10px!important;}
[data-testid="stContainer"]{background:var(--card)!important;border:1px solid var(--bdr)!important;border-radius:14px!important;padding:12px!important;}
.scoreboard{background:linear-gradient(135deg,var(--surf),var(--card));border:1px solid rgba(249,115,22,.18);border-radius:20px;padding:18px 14px 12px;position:relative;overflow:hidden;}
.scoreboard:before{content:'';position:absolute;left:0;right:0;top:0;height:3px;background:linear-gradient(90deg,#f97316,#f59e0b,#f97316);}
.score-no{font-size:88px;line-height:1;font-weight:900;color:#fff;letter-spacing:-2px;}
.score-hot{color:#f97316;text-shadow:0 0 28px rgba(249,115,22,.35);}
.t-name{font-size:16px;font-weight:800;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;}
.t-meta{font-size:12px;color:var(--muted);}
.banner{border-radius:16px;padding:13px 15px;font-weight:800;border:1px solid rgba(249,115,22,.32);background:linear-gradient(135deg,#3a1c06,#6b3407);color:#ffd6b0;margin-bottom:10px;}
.winner{border-radius:16px;padding:14px 16px;font-weight:900;text-align:center;background:linear-gradient(135deg,#f59e0b,#d97706);color:#fff;margin-bottom:10px;}
.pbig .stButton>button{min-height:84px!important;font-size:24px!important;border-radius:16px!important;}
.pbigb .stButton>button{background:linear-gradient(135deg,#3b82f6,#1d4ed8)!important;box-shadow:0 4px 14px rgba(59,130,246,.22)!important;}
.ev{font-size:12px;padding:6px 4px;border-bottom:1px solid var(--bdr);color:var(--muted);}
.ev:first-child{color:var(--txt);font-weight:700;}
.setcard,.sbox{background:var(--surf);border:1px solid var(--bdr);border-radius:10px;padding:10px;text-align:center;}
.sboxn{font-size:30px;font-weight:900;color:#f97316;}
.pill{display:inline-block;padding:3px 9px;border-radius:999px;font-size:10px;font-weight:800;text-transform:uppercase;letter-spacing:.5px;}
.po{background:rgba(249,115,22,.15);border:1px solid rgba(249,115,22,.25);color:#fdba74;}
.pb{background:rgba(59,130,246,.15);border:1px solid rgba(59,130,246,.25);color:#93c5fd;}
.pg{background:rgba(34,197,94,.15);border:1px solid rgba(34,197,94,.25);color:#86efac;}
.pr{background:rgba(239,68,68,.15);border:1px solid rgba(239,68,68,.25);color:#fca5a5;}
@media(max-width:768px){.block-container{padding:.3rem .4rem 4rem!important;}.score-no{font-size:62px!important;}.t-name{font-size:14px!important;}.pbig .stButton>button{min-height:76px!important;font-size:19px!important;}}
</style>
""", unsafe_allow_html=True)


@st.cache_resource
def get_supabase():
    if not SUPABASE_OK:
        return None
    try:
        url = st.secrets["SUPABASE_URL"]
        key = st.secrets["SUPABASE_KEY"]
        if not url or not key:
            return None
        return create_client(url, key)
    except Exception:
        return None


def use_supabase() -> bool:
    return get_supabase() is not None


def auto_refresh(ms: int = 1200):
    components.html(f"<script>setTimeout(function(){{window.parent.location.reload();}},{ms});</script>", height=0)


def hpw(pw: str) -> str:
    return hashlib.sha256(pw.encode()).hexdigest()


def current_target(score_a: int, score_b: int) -> int:
    """Win targets: normal 35, deuce at 34-34 goes to 36, 36-36 goes to 39, and 39 is the hard cap."""
    score_a = max(0, min(39, int(score_a)))
    score_b = max(0, min(39, int(score_b)))
    if score_a >= 36 and score_b >= 36:
        return 39
    if score_a >= 34 and score_b >= 34:
        return 36
    return 35


def has_winner(score_a: int, score_b: int) -> bool:
    score_a = max(0, min(39, int(score_a)))
    score_b = max(0, min(39, int(score_b)))
    tgt = current_target(score_a, score_b)
    return (score_a >= tgt or score_b >= tgt) and abs(score_a - score_b) >= 1


def safe(v: str, fb: str) -> str:
    v = (v or "").strip()
    return v if v else fb


def cyc(i: int, n: int) -> int:
    return (i + 1) % n


def build_order(players: List[str], idxs: List[int]) -> List[str]:
    out = []
    for idx in idxs:
        if idx < 1 or idx > len(players):
            return []
        out.append(players[idx - 1])
    return out


def first_court_change_hit(sc_a: int, sc_b: int, done: Dict[int, bool]) -> Optional[int]:
    for p in COURT_CHG:
        if not done.get(p, False) and (sc_a == p or sc_b == p):
            return p
    return None


def default_store() -> dict:
    return {"match": None, "setup_done": False, "history": [], "tournament": [], "t_info": {}, "updated_at": ""}


def load_store() -> dict:
    sb = get_supabase()
    if sb:
        try:
            res = sb.table("matches").select("*").eq("id", "app_state").execute()
            if res.data:
                base = default_store()
                base.update(res.data[0].get("data") or {})
                return base
        except Exception:
            pass
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                base = default_store()
                base.update(json.load(f))
                return base
        except Exception:
            pass
    return default_store()


def save_store(data: dict):
    data["updated_at"] = datetime.now().strftime("%d %b %Y %H:%M:%S")
    sb = get_supabase()
    if sb:
        try:
            sb.table("matches").upsert({"id": "app_state", "data": data, "updated_at": datetime.now().isoformat()}).execute()
            return
        except Exception:
            pass
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False)


def load_users() -> dict:
    sb = get_supabase()
    if sb:
        try:
            res = sb.table("viewers").select("*").execute()
            out = {}
            for r in (res.data or []):
                out[r["username"]] = {
                    "name": r.get("name", ""),
                    "contact": r.get("contact", ""),
                    "pw_hash": r.get("pw_hash", ""),
                    "created": r.get("created_at", ""),
                    "created_by_admin": bool(r.get("created_by_admin", False)),
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


def save_users(users: dict):
    sb = get_supabase()
    if sb:
        try:
            rows = []
            for uname, u in users.items():
                rows.append({
                    "username": uname,
                    "name": u.get("name", ""),
                    "contact": u.get("contact", ""),
                    "pw_hash": u.get("pw_hash", ""),
                    "created_at": u.get("created", ""),
                    "created_by_admin": bool(u.get("created_by_admin", False)),
                })
            if rows:
                sb.table("viewers").upsert(rows).execute()
            return
        except Exception:
            pass
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, ensure_ascii=False, indent=2)


def add_user(name: str, contact: str, username: str, password: str, by_admin: bool = False) -> Tuple[bool, str]:
    users = load_users()
    uname = username.strip().lower()
    if not uname or not name.strip() or not password.strip():
        return False, "Name, username and password are required"
    if len(password) < 4:
        return False, "Password must be at least 4 characters"
    if uname in users:
        return False, "Username already exists"
    if contact.strip():
        for u in users.values():
            if u.get("contact", "").strip().lower() == contact.strip().lower():
                return False, "Contact already registered"
    users[uname] = {
        "name": name.strip(),
        "contact": contact.strip(),
        "pw_hash": hpw(password),
        "created": datetime.now().strftime("%d %b %Y %H:%M"),
        "created_by_admin": by_admin,
    }
    save_users(users)
    return True, f"User created: {uname}"


def validate_user(username: str, password: str) -> Tuple[bool, dict]:
    users = load_users()
    uname = username.strip().lower()
    if uname not in users:
        return False, {}
    u = users[uname]
    return u.get("pw_hash") == hpw(password), u


@dataclass
class Match:
    tA: str
    tB: str
    allA: List[str]
    allB: List[str]
    onA: List[str]
    onB: List[str]
    ordA: List[str]
    ordB: List[str]
    setno: int
    sA: int
    sB: int
    scA: int
    scB: int
    srv: str
    swapped: bool
    curA: Optional[str]
    curB: Optional[str]
    nxtA: int
    nxtB: int
    subA: int
    subB: int
    toA: int
    toB: int
    ms: Dict[int, bool]
    history: List[Dict]
    events: List[str]
    over: bool
    winner: Optional[str]
    psA: List[int]
    psB: List[int]
    ppA: Dict[str, int]
    ppB: Dict[str, int]
    started: str
    ended: Optional[str]
    mid: str
    tnm: Optional[str]
    trd: Optional[str]
    pending_cc: Optional[int] = None
    updated_at: Optional[str] = None


def restore_match(d: Optional[dict]) -> Optional[Match]:
    if not d:
        return None
    try:
        return Match(**d)
    except Exception:
        return None


def snap(m: Match) -> Dict:
    d = asdict(m)
    d["history"] = []
    return d


def server_name(m: Match) -> str:
    return (m.curA if m.srv == "A" else m.curB) or "—"


def new_match(tA, tB, allA, allB, pA, pB, oA, oB, first, tnm=None, trd=None):
    cA, cB, nA, nB = (oA[0], None, 1, 0) if first == "A" else (None, oB[0], 0, 1)
    now = datetime.now()
    return Match(
        tA=tA, tB=tB, allA=allA, allB=allB, onA=pA, onB=pB, ordA=oA, ordB=oB,
        setno=1, sA=0, sB=0, scA=0, scB=0, srv=first, swapped=False,
        curA=cA, curB=cB, nxtA=nA, nxtB=nB, subA=3, subB=3, toA=1, toB=1,
        ms={9: False, 18: False, 27: False}, history=[],
        events=[f"Match started · {tA if first=='A' else tB} serves first"],
        over=False, winner=None, psA=[], psB=[],
        ppA={p: 0 for p in pA}, ppB={p: 0 for p in pB},
        started=now.strftime("%d %b %Y %H:%M"), ended=None, mid=now.strftime("%Y%m%d%H%M%S"),
        tnm=tnm, trd=trd, pending_cc=None, updated_at=now.strftime("%d %b %Y %H:%M:%S")
    )


def push_event(m: Match, txt: str):
    m.events.insert(0, txt)
    m.events = m.events[:60]
    m.updated_at = datetime.now().strftime("%d %b %Y %H:%M:%S")


def save_match_to_store(m: Optional[Match], data: dict):
    data["match"] = asdict(m) if m else None
    data["setup_done"] = bool(m)
    save_store(data)


def add_point(winner: str):
    data = load_store()
    m = restore_match(data.get("match"))
    if not m or m.over:
        return
    m.history.append(snap(m))
    m.history = m.history[-25:]

    if winner == "A":
        if m.scA >= 39:
            return
        m.scA += 1
        if m.curA:
            m.ppA[m.curA] = m.ppA.get(m.curA, 0) + 1
    else:
        if m.scB >= 39:
            return
        m.scB += 1
        if m.curB:
            m.ppB[m.curB] = m.ppB.get(m.curB, 0) + 1

    if winner != m.srv:
        m.srv = winner
        if winner == "A":
            m.curA = m.ordA[m.nxtA]
            m.nxtA = cyc(m.nxtA, PLAYERS)
        else:
            m.curB = m.ordB[m.nxtB]
            m.nxtB = cyc(m.nxtB, PLAYERS)

    push_event(m, f"▸ {m.tA if winner=='A' else m.tB}  {m.scA}–{m.scB}  srv:{server_name(m)}")

    hit = first_court_change_hit(m.scA, m.scB, m.ms)
    if hit:
        m.ms[hit] = True
        m.pending_cc = hit
        leader = m.tA if (m.scA == hit and m.scB != hit) or (m.scA == hit and m.scB == hit and winner == 'A') else m.tB
        push_event(m, f"🔄 Court change pop at {hit} · first reached by {leader}")

    if has_winner(m.scA, m.scB):
        sw = "A" if m.scA > m.scB else "B"
        if sw == "A":
            m.sA += 1
        else:
            m.sB += 1
        m.psA.append(m.scA)
        m.psB.append(m.scB)
        push_event(m, f"✅ Set {m.setno} → {m.tA if sw=='A' else m.tB} ({m.scA}–{m.scB})")
        if m.sA == 2 or m.sB == 2:
            m.over = True
            m.winner = "A" if m.sA == 2 else "B"
            m.ended = datetime.now().strftime("%d %b %Y %H:%M")
            push_event(m, f"🏆 {m.tA if m.winner=='A' else m.tB} wins!")
            hist = data.get("history", [])
            hist.append({
                "id": m.mid, "date": m.started, "tA": m.tA, "tB": m.tB,
                "sA": m.sA, "sB": m.sB, "sets": list(zip(m.psA, m.psB)),
                "winner": m.tA if m.winner == "A" else m.tB,
                "tnm": m.tnm, "trd": m.trd, "ppA": dict(m.ppA), "ppB": dict(m.ppB),
            })
            data["history"] = hist
            save_match_to_store(m, data)
            return
        m.setno += 1
        m.scA = 0
        m.scB = 0
        m.subA = 3
        m.subB = 3
        m.toA = 1
        m.toB = 1
        m.ms = {9: False, 18: False, 27: False}
        m.pending_cc = None
        push_event(m, f"▶️ Set {m.setno} begins")

    save_match_to_store(m, data)


def undo_point():
    data = load_store()
    m = restore_match(data.get("match"))
    if not m or not m.history:
        return
    prev = m.history.pop()
    data["match"] = prev
    save_store(data)


def toggle_court():
    data = load_store()
    m = restore_match(data.get("match"))
    if not m:
        return
    m.swapped = not m.swapped
    m.pending_cc = None
    push_event(m, "🔄 Court sides changed")
    save_match_to_store(m, data)


def set_score_direct(score_a: int, score_b: int):
    data = load_store()
    m = restore_match(data.get("match"))
    if not m or m.over:
        return
    m.scA = max(0, min(39, int(score_a)))
    m.scB = max(0, min(39, int(score_b)))
    push_event(m, f"✏️ Score adjusted to {m.scA}–{m.scB}")
    save_match_to_store(m, data)


def do_timeout(team: str):
    data = load_store()
    m = restore_match(data.get("match"))
    if not m:
        return
    if team == "A" and m.toA > 0:
        m.toA -= 1
        push_event(m, f"⏱️ Timeout: {m.tA}")
    elif team == "B" and m.toB > 0:
        m.toB -= 1
        push_event(m, f"⏱️ Timeout: {m.tB}")
    save_match_to_store(m, data)


def do_sub(team: str, on: str, off: str):
    data = load_store()
    m = restore_match(data.get("match"))
    if not m or not on or not off or on == off:
        return
    if team == "A":
        if m.subA <= 0 or on in m.onA or off not in m.onA:
            return
        m.onA[m.onA.index(off)] = on
        m.ppA.setdefault(on, 0)
        m.subA -= 1
        push_event(m, f"🔁 {m.tA}: {off} → {on}")
    else:
        if m.subB <= 0 or on in m.onB or off not in m.onB:
            return
        m.onB[m.onB.index(off)] = on
        m.ppB.setdefault(on, 0)
        m.subB -= 1
        push_event(m, f"🔁 {m.tB}: {off} → {on}")
    save_match_to_store(m, data)


for k, v in [
    ("role", None), ("user_name", ""), ("tab", "score"),
    ("setup", {"tA": "", "tB": "", "allA": [""]*ALL_PLAYERS, "allB": [""]*ALL_PLAYERS, "ordA": [1,2,3,4,5], "ordB": [1,2,3,4,5], "first": "A", "tnm": "", "trd": ""}),
]:
    if k not in st.session_state:
        st.session_state[k] = v

store = load_store()
match = restore_match(store.get("match"))
is_admin = st.session_state.role == "admin"

if st.session_state.role is None:
    st.markdown("<div style='text-align:center;padding:18px 0 10px'><div style='font-size:58px'>🏸</div><div style='font-size:36px;font-weight:900;letter-spacing:2px'>BALL BADMINTON LIVE</div><div style='color:var(--muted);font-size:12px;margin-top:4px'>Admin + Viewer + Supabase</div></div>", unsafe_allow_html=True)
    t1, t2, t3 = st.tabs(["🔑 Viewer Login", "📝 Register", "🔐 Admin"])
    with t1:
        vu = st.text_input("Username", key="viewer_login_u")
        vp = st.text_input("Password", type="password", key="viewer_login_p")
        if st.button("Open Live Score", key="viewer_login_btn", use_container_width=True):
            ok, u = validate_user(vu, vp)
            if ok:
                st.session_state.role = "viewer"
                st.session_state.user_name = u.get("name", vu)
                st.rerun()
            st.error("Invalid viewer credentials")
    with t2:
        rn = st.text_input("Full Name", key="reg_name")
        rc = st.text_input("Mobile / Email", key="reg_contact")
        ru = st.text_input("Choose Username", key="reg_user")
        rp = st.text_input("Create Password", key="reg_pass", type="password")
        rp2 = st.text_input("Confirm Password", key="reg_pass2", type="password")
        if st.button("Create Account", key="reg_btn", use_container_width=True):
            if rp != rp2:
                st.error("Passwords do not match")
            else:
                ok, msg = add_user(rn, rc, ru, rp, by_admin=False)
                (st.success if ok else st.error)(msg)
    with t3:
        au = st.text_input("Admin Username", key="admin_login_u")
        ap = st.text_input("Admin Password", type="password", key="admin_login_p")
        if st.button("Login as Admin", key="admin_login_btn", use_container_width=True):
            if au == ADMIN_USER and ap == ADMIN_PASS:
                st.session_state.role = "admin"
                st.session_state.user_name = "Admin"
                st.rerun()
            st.error("Invalid admin credentials")
    st.stop()

nav = [("score", "🏸 Score"), ("stats", "📊 Stats"), ("history", "📜 History")]
if is_admin:
    nav += [("tournament", "🏆 Tournament"), ("users", "👥 Users"), ("admin", "⚙️ Admin")]
cols = st.columns(len(nav) + 1)
for i, (k, lbl) in enumerate(nav):
    with cols[i]:
        if st.button(lbl, key=f"nav_{k}", use_container_width=True):
            st.session_state.tab = k
            st.rerun()
with cols[-1]:
    if st.button("🚪 Logout", use_container_width=True):
        st.session_state.role = None
        st.session_state.user_name = ""
        st.rerun()

match = restore_match(load_store().get("match"))
if not is_admin and st.session_state.tab not in ("score", "stats", "history"):
    st.session_state.tab = "score"

if not match and st.session_state.tab == "score" and is_admin:
    setup = st.session_state.setup
    st.markdown("## Match Setup")
    with st.expander("🏆 Tournament (optional)"):
        tnm = st.text_input("Tournament Name", value=setup.get("tnm", ""))
        trd = st.text_input("Round", value=setup.get("trd", ""))
    c1, c2 = st.columns(2)
    with c1:
        tA = st.text_input("Team A", value=setup.get("tA", ""))
    with c2:
        tB = st.text_input("Team B", value=setup.get("tB", ""))
    st.markdown("### Players")
    ca, cb = st.columns(2)
    allA, allB = [], []
    with ca:
        st.markdown(f"**{tA or 'Team A'}**")
        for i in range(ALL_PLAYERS):
            allA.append(st.text_input(f"A Player {i+1}", value=setup['allA'][i], key=f"A{i}"))
    with cb:
        st.markdown(f"**{tB or 'Team B'}**")
        for i in range(ALL_PLAYERS):
            allB.append(st.text_input(f"B Player {i+1}", value=setup['allB'][i], key=f"B{i}"))
    allA_f = [safe(v, f"A{i+1}") for i, v in enumerate(allA)]
    allB_f = [safe(v, f"B{i+1}") for i, v in enumerate(allB)]
    st.markdown("### Select 5 starters")
    s1, s2 = st.columns(2)
    with s1:
        mpA = st.multiselect(f"{tA or 'Team A'}", allA_f, default=allA_f[:PLAYERS], max_selections=PLAYERS)
    with s2:
        mpB = st.multiselect(f"{tB or 'Team B'}", allB_f, default=allB_f[:PLAYERS], max_selections=PLAYERS)
    errs, oA2, oB2, oAi, oBi = [], [], [], [], []
    if len(mpA) == PLAYERS and len(mpB) == PLAYERS:
        st.markdown("### Service Order")
        o1, o2 = st.columns(2)
        with o1:
            for k in range(PLAYERS):
                opts = [f"{i+1}. {mpA[i]}" for i in range(PLAYERS)]
                sel = st.selectbox(f"A Serve {k+1}", opts, index=max(0, min(setup['ordA'][k]-1, PLAYERS-1)), key=f"oA{k}")
                oAi.append(int(sel.split('.')[0]))
        with o2:
            for k in range(PLAYERS):
                opts = [f"{i+1}. {mpB[i]}" for i in range(PLAYERS)]
                sel = st.selectbox(f"B Serve {k+1}", opts, index=max(0, min(setup['ordB'][k]-1, PLAYERS-1)), key=f"oB{k}")
                oBi.append(int(sel.split('.')[0]))
        if len(set(oAi)) != 5:
            errs.append("Team A service order must be unique")
        if len(set(oBi)) != 5:
            errs.append("Team B service order must be unique")
        oA2 = build_order(list(mpA), oAi)
        oB2 = build_order(list(mpB), oBi)
        if not oA2 or not oB2:
            errs.append("Invalid service order")
        first_label = st.radio("First serve", [tA or 'Team A', tB or 'Team B'], horizontal=True)
        first = "A" if first_label == (tA or 'Team A') else "B"
    else:
        first = "A"
        errs.append("Select exactly 5 players per team")
    for e in errs:
        st.error(e)
    if st.button("Start Match", use_container_width=True, disabled=bool(errs)):
        nm = new_match(safe(tA, "Team A"), safe(tB, "Team B"), allA_f, allB_f, list(mpA), list(mpB), oA2, oB2, first, tnm or None, trd or None)
        store = load_store()
        save_match_to_store(nm, store)
        st.session_state.setup.update({"tA": tA, "tB": tB, "allA": allA, "allB": allB, "ordA": oAi, "ordB": oBi, "first": first, "tnm": tnm, "trd": trd})
        st.rerun()
    st.stop()

if not match and not is_admin:
    st.info("⏳ No active match right now")
    auto_refresh(2500)
    st.stop()
if not match:
    st.info("Start a match first")
    st.stop()

m = match

if st.session_state.tab == "score":
    if not is_admin:
        auto_refresh(1000)
        st.caption(f"Live auto refresh on · Last update: {m.updated_at or load_store().get('updated_at', '-')}")
    if m.pending_cc:
        st.markdown(f"<div class='banner'>🔄 Court change point reached first at {m.pending_cc}. Other team reaching later will not trigger again.</div>", unsafe_allow_html=True)
    if m.over:
        st.markdown(f"<div class='winner'>🏆 {m.tA if m.winner=='A' else m.tB} wins the match</div>", unsafe_allow_html=True)
    if m.tnm:
        st.caption(f"🏆 {m.tnm}{(' · ' + m.trd) if m.trd else ''}")
    lt = "B" if m.swapped else "A"
    rt = "A" if m.swapped else "B"
    tn = lambda t: m.tA if t == 'A' else m.tB
    sc = lambda t: m.scA if t == 'A' else m.scB
    ss = lambda t: m.sA if t == 'A' else m.sB
    st.markdown(f"""
    <div class='scoreboard'>
      <div style='display:flex;justify-content:space-between;align-items:flex-end;gap:10px'>
        <div style='flex:1;min-width:0'>
          <div class='t-name'>{'🟠 ' if m.srv==lt else ''}{tn(lt)}</div>
          <div class='score-no {'score-hot' if m.srv==lt else ''}'>{sc(lt)}</div>
          <div class='t-meta'>Sets: {ss(lt)} · Left</div>
        </div>
        <div style='opacity:.35;font-weight:800;font-size:20px;padding:0 8px'>vs</div>
        <div style='flex:1;min-width:0;text-align:right'>
          <div class='t-name'>{'🟠 ' if m.srv==rt else ''}{tn(rt)}</div>
          <div class='score-no {'score-hot' if m.srv==rt else ''}'>{sc(rt)}</div>
          <div class='t-meta'>Sets: {ss(rt)} · Right</div>
        </div>
      </div>
      <div style='text-align:center;color:var(--muted);font-size:11px;margin-top:8px'>Set {m.setno}/3 · Current target {current_target(m.scA,m.scB)} · Court change 9 · 18 · 27</div>
    </div>
    """, unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("Serving", m.tA if m.srv == 'A' else m.tB)
    with c2:
        st.metric("Server", server_name(m))
    with c3:
        st.metric("Target", current_target(m.scA, m.scB))
    if m.psA:
        cols = st.columns(len(m.psA))
        for i, (a, b) in enumerate(zip(m.psA, m.psB)):
            with cols[i]:
                st.markdown(f"<div class='setcard'><div style='font-size:10px;color:var(--muted)'>SET {i+1}</div><div style='font-size:20px;font-weight:800'>{a}–{b}</div></div>", unsafe_allow_html=True)
    if is_admin:
        pb1, pb2 = st.columns(2)
        with pb1:
            st.markdown("<div class='pbig'>", unsafe_allow_html=True)
            if st.button(f"＋ {m.tA}", key="ptA", use_container_width=True, disabled=m.over):
                add_point("A")
            st.markdown("</div>", unsafe_allow_html=True)
        with pb2:
            st.markdown("<div class='pbig pbigb'>", unsafe_allow_html=True)
            if st.button(f"＋ {m.tB}", key="ptB", use_container_width=True, disabled=m.over):
                add_point("B")
            st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("### Score Slider / Adjust")
        s1, s2, s3 = st.columns(3)
        with s1:
            new_a = st.number_input(f"{m.tA} score", min_value=0, max_value=39, value=int(m.scA), step=1)
        with s2:
            new_b = st.number_input(f"{m.tB} score", min_value=0, max_value=39, value=int(m.scB), step=1)
        with s3:
            st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
            if st.button("Apply Score", use_container_width=True):
                set_score_direct(new_a, new_b)
                st.rerun()
        a1, a2 = st.columns(2)
        with a1:
            if st.button("🔄 Court Changed", use_container_width=True):
                toggle_court(); st.rerun()
        with a2:
            if st.button("↩️ Undo", use_container_width=True, disabled=not m.history):
                undo_point(); st.rerun()
        with st.container(border=True):
            st.markdown("**Substitutions & Timeouts**")
            sc1, sc2 = st.columns(2)
            for team, col in [("A", sc1), ("B", sc2)]:
                fresh = restore_match(load_store().get("match")) or m
                tname = fresh.tA if team == 'A' else fresh.tB
                subs = fresh.subA if team == 'A' else fresh.subB
                tos = fresh.toA if team == 'A' else fresh.toB
                on_players = fresh.onA if team == 'A' else fresh.onB
                all_players = fresh.allA if team == 'A' else fresh.allB
                with col:
                    st.markdown(f"**{tname}** <span class='pill {'pg' if subs>0 else 'pr'}'>Subs {subs}</span> <span class='pill {'pb' if tos>0 else 'pr'}'>T/O {tos}</span>", unsafe_allow_html=True)
                    bench = [p for p in all_players if p and p not in on_players]
                    if subs > 0 and bench:
                        on_p = st.selectbox("In", bench, key=f"in_{team}")
                        off_p = st.selectbox("Out", on_players, key=f"out_{team}")
                        if st.button(f"Sub {tname}", key=f"sub_{team}", use_container_width=True):
                            do_sub(team, on_p, off_p); st.rerun()
                    if tos > 0 and st.button(f"Timeout {tname}", key=f"to_{team}", use_container_width=True):
                        do_timeout(team); st.rerun()
    with st.container(border=True):
        st.markdown("**Live Events**")
        for e in m.events[:14]:
            st.markdown(f"<div class='ev'>{e}</div>", unsafe_allow_html=True)

elif st.session_state.tab == "stats":
    total = m.scA + m.scB + sum(m.psA) + sum(m.psB)
    c1, c2, c3, c4 = st.columns(4)
    for col, val, lbl in [(c1, f"Set {m.setno}", "Set"), (c2, f"{m.sA}–{m.sB}", "Sets"), (c3, f"{m.scA}–{m.scB}", "Score"), (c4, total, "Total Pts")]:
        with col:
            st.markdown(f"<div class='sbox'><div class='sboxn'>{val}</div><div>{lbl}</div></div>", unsafe_allow_html=True)
    p1, p2 = st.columns(2)
    with p1:
        st.markdown(f"**{m.tA}**")
        for p, pts in sorted(m.ppA.items(), key=lambda x: -x[1]):
            st.write(f"{p}: {pts}")
    with p2:
        st.markdown(f"**{m.tB}**")
        for p, pts in sorted(m.ppB.items(), key=lambda x: -x[1]):
            st.write(f"{p}: {pts}")

elif st.session_state.tab == "history":
    hist = load_store().get("history", [])
    if not hist:
        st.info("No completed matches yet.")
    else:
        for h in reversed(hist):
            with st.container(border=True):
                st.markdown(f"### {h['tA']} vs {h['tB']}")
                st.caption(h['date'])
                st.write(f"Sets: **{h['sA']}–{h['sB']}** · Winner: **{h['winner']}**")
        if is_admin and st.button("Clear History", use_container_width=True):
            s = load_store()
            s["history"] = []
            save_store(s)
            st.rerun()

elif st.session_state.tab == "tournament" and is_admin:
    st.markdown("## Tournament")
    with st.container(border=True):
        tn2 = st.text_input("Tournament Name", key="tn2")
        ntm = st.selectbox("Teams", [4, 8, 16], key="ntm")
        tcols = st.columns(2)
        tnames = []
        for i in range(ntm):
            with tcols[i % 2]:
                tnames.append(st.text_input(f"Team {i+1}", key=f"brt{i}"))
        if st.button("Generate Bracket", use_container_width=True):
            filled = [safe(t, f"Team {i+1}") for i, t in enumerate(tnames)]
            random.shuffle(filled)
            s = load_store()
            s["tournament"] = [{"r": "Round 1", "tA": filled[i], "tB": filled[i+1], "w": None} for i in range(0, len(filled)-1, 2)]
            s["t_info"] = {"name": tn2, "teams": filled}
            save_store(s)
            st.rerun()
    s = load_store()
    if s.get("tournament"):
        st.markdown(f"### {s.get('t_info', {}).get('name', 'Tournament')}")
        for i, mb in enumerate(s["tournament"]):
            with st.container(border=True):
                c1, c2, c3 = st.columns([2,.4,2])
                with c1: st.write(f"**{mb['tA']}**")
                with c2: st.write("vs")
                with c3: st.write(f"**{mb['tB']}**")
                if not mb.get("w"):
                    w = st.radio("Winner", [mb["tA"], mb["tB"]], key=f"bw{i}", horizontal=True)
                    if st.button("Confirm", key=f"bc{i}"):
                        s["tournament"][i]["w"] = w
                        save_store(s)
                        st.rerun()
                else:
                    st.markdown(f"<span class='pill po'>🏆 {mb['w']}</span>", unsafe_allow_html=True)

elif st.session_state.tab == "users" and is_admin:
    st.markdown("## Viewer Access")
    with st.container(border=True):
        st.markdown("### Admin Create User")
        c1, c2 = st.columns(2)
        with c1:
            an = st.text_input("Name", key="admin_add_name")
            ac = st.text_input("Mobile / Email", key="admin_add_contact")
        with c2:
            au = st.text_input("Username", key="admin_add_user")
            ap = st.text_input("Password", key="admin_add_pass")
        if st.button("Create Viewer", use_container_width=True):
            ok, msg = add_user(an, ac, au, ap, by_admin=True)
            (st.success if ok else st.error)(msg)
    users = load_users()
    st.markdown("### Registered Users")
    if not users:
        st.info("No registered users")
    else:
        for uname, u in users.items():
            with st.container(border=True):
                c1, c2, c3 = st.columns([2,2,1])
                with c1:
                    st.markdown(f"**{u.get('name','—')}**")
                    st.caption(f"@{uname}")
                with c2:
                    st.write(u.get("contact", "—"))
                    st.caption(f"Created: {u.get('created','—')}")
                with c3:
                    if st.button("Remove", key=f"del_{uname}", use_container_width=True):
                        users.pop(uname, None)
                        save_users(users)
                        st.rerun()

elif st.session_state.tab == "admin" and is_admin:
    st.markdown("## Admin Panel")
    with st.container(border=True):
        c1, c2, c3, c4 = st.columns(4)
        with c1: st.metric("Match", f"{m.tA} vs {m.tB}")
        with c2: st.metric("Set", f"{m.setno}/3")
        with c3: st.metric("Score", f"{m.scA}–{m.scB}")
        with c4: st.metric("Saved In", "Supabase" if use_supabase() else "JSON")
    export = {"match": load_store().get("match"), "history": load_store().get("history", []), "tournament": load_store().get("tournament", []), "t_info": load_store().get("t_info", {}), "exported": datetime.now().strftime("%Y-%m-%d %H:%M")}
    st.download_button("Download Match Data (JSON)", data=json.dumps(export, indent=2), file_name=f"bb_{datetime.now().strftime('%Y%m%d')}.json", mime="application/json", use_container_width=True)
