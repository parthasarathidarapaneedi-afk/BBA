import json
import os
import random
import string
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Dict, List, Optional

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
DATA_FILE = "bb_save.json"
ADMIN_USER = "Ballbadminton"
ADMIN_PASS = "partha@2025"
VIEWER_USER = "viewer"
VIEWER_PASS = "viewer@2025"

st.set_page_config(
    page_title="Ball Badminton Live",
    page_icon="🏸",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
<style>
:root {
  --bg: #f4f7fb;
  --surface: #ffffff;
  --surface-2: #edf2f7;
  --border: #d9e2ec;
  --text: #0f172a;
  --muted: #475569;
  --orange: #f97316;
  --orange-2: #ea580c;
  --blue: #2563eb;
  --blue-2: #1d4ed8;
  --green: #16a34a;
  --red: #dc2626;
  --gold: #d97706;
  --shadow: 0 10px 28px rgba(15, 23, 42, 0.08);
  --radius: 18px;
}
html, body, .stApp {
  background: linear-gradient(180deg, #f8fbff 0%, #eef4fb 100%) !important;
  color: var(--text) !important;
}
#MainMenu, header, footer, [data-testid="stToolbar"], [data-testid="stDecoration"],
[data-testid="stStatusWidget"], .stDeployButton, section[data-testid="stSidebar"] {
  display: none !important;
}
.block-container {
  max-width: 1200px !important;
  padding: 0.9rem 0.8rem 1.2rem !important;
}
[data-testid="stMetricValue"] { color: var(--text) !important; }
[data-testid="stMetricLabel"] { color: var(--muted) !important; }
.stTextInput input, .stSelectbox > div > div, .stMultiSelect > div > div {
  background: #fff !important;
  color: var(--text) !important;
  border: 1px solid var(--border) !important;
  border-radius: 12px !important;
}
.stButton > button {
  width: 100% !important;
  border: 0 !important;
  border-radius: 14px !important;
  font-weight: 700 !important;
  padding: 0.85rem 1rem !important;
  background: linear-gradient(135deg, var(--orange), var(--orange-2)) !important;
  color: #fff !important;
  box-shadow: 0 8px 18px rgba(249, 115, 22, 0.22) !important;
}
.stButton > button:hover {
  transform: translateY(-1px);
}
.stDownloadButton > button {
  width: 100% !important;
  border-radius: 14px !important;
}
.card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  box-shadow: var(--shadow);
  padding: 1rem;
}
.hero {
  background: linear-gradient(135deg, #fff7ed, #ffffff);
  border: 1px solid #fed7aa;
  border-radius: 22px;
  box-shadow: var(--shadow);
  padding: 1rem 1rem 0.9rem;
}
.navwrap {
  background: rgba(255,255,255,.9);
  border: 1px solid var(--border);
  border-radius: 18px;
  padding: 0.45rem;
  box-shadow: var(--shadow);
}
.muted { color: var(--muted); }
.center { text-align: center; }
.pill {
  display: inline-block;
  padding: 0.28rem 0.65rem;
  border-radius: 999px;
  font-size: 0.8rem;
  font-weight: 700;
  border: 1px solid transparent;
}
.pill-orange { background: #fff7ed; color: #c2410c; border-color: #fdba74; }
.pill-blue { background: #eff6ff; color: #1d4ed8; border-color: #93c5fd; }
.pill-green { background: #f0fdf4; color: #166534; border-color: #86efac; }
.pill-red { background: #fef2f2; color: #991b1b; border-color: #fca5a5; }
.banner {
  border-radius: 18px;
  padding: 0.9rem 1rem;
  font-weight: 800;
  border: 1px solid #fdba74;
  background: linear-gradient(135deg, #fff7ed, #ffedd5);
  color: #9a3412;
  margin-bottom: 0.9rem;
}
.winner {
  border-radius: 18px;
  padding: 0.9rem 1rem;
  background: linear-gradient(135deg, #f59e0b, #d97706);
  color: white;
  font-weight: 800;
  text-align: center;
  box-shadow: 0 10px 28px rgba(217, 119, 6, 0.3);
  margin-bottom: 0.9rem;
}
.score-shell {
  background: linear-gradient(135deg, #ffffff, #f8fafc);
  border: 1px solid var(--border);
  border-radius: 24px;
  box-shadow: var(--shadow);
  padding: 1rem;
}
.score-row {
  display: grid;
  grid-template-columns: 1fr auto 1fr;
  gap: 0.75rem;
  align-items: center;
}
.score-team {
  min-width: 0;
}
.score-team.right { text-align: right; }
.team-name {
  font-size: 1.15rem;
  font-weight: 800;
  color: var(--text);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.team-meta {
  font-size: 0.9rem;
  color: var(--muted);
  margin-top: 0.15rem;
}
.score-no {
  font-size: 5.8rem;
  line-height: 0.9;
  font-weight: 900;
  color: var(--text);
  letter-spacing: -2px;
}
.score-no.active { color: var(--orange-2); }
.vs {
  font-size: 1.15rem;
  color: #94a3b8;
  font-weight: 800;
}
.point-btn .stButton > button {
  min-height: 92px !important;
  font-size: 1.35rem !important;
  font-weight: 800 !important;
}
.point-btn-blue .stButton > button {
  background: linear-gradient(135deg, var(--blue), var(--blue-2)) !important;
  box-shadow: 0 8px 18px rgba(37, 99, 235, 0.22) !important;
}
.event-item {
  padding: 0.45rem 0;
  border-bottom: 1px solid #e2e8f0;
  color: var(--muted);
  font-size: 0.92rem;
}
.event-item:first-child {
  color: var(--text);
  font-weight: 700;
}
.set-card {
  border: 1px solid var(--border);
  border-radius: 14px;
  background: #fff;
  padding: 0.7rem;
  text-align: center;
}
.loginbox {
  background: rgba(255,255,255,.94);
  border: 1px solid var(--border);
  border-radius: 24px;
  box-shadow: var(--shadow);
  padding: 1.2rem;
}
.small-note {
  font-size: 0.86rem;
  color: var(--muted);
}
@media (max-width: 768px) {
  .block-container { padding: 0.55rem 0.45rem 1rem !important; }
  .score-row { grid-template-columns: 1fr auto 1fr; gap: 0.35rem; }
  .team-name { font-size: 0.96rem; }
  .team-meta { font-size: 0.78rem; }
  .score-no { font-size: 3.8rem; }
  .point-btn .stButton > button { min-height: 78px !important; font-size: 1.15rem !important; }
}
</style>
""",
    unsafe_allow_html=True,
)


def auto_refresh(ms: int = 2500):
    components.html(
        f"""
        <script>
        setTimeout(function() {{
            const parentDoc = window.parent.document;
            const buttons = parentDoc.querySelectorAll('button[kind="header"]');
            window.parent.location.reload();
        }}, {ms});
        </script>
        """,
        height=0,
    )


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
    hand: str
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
    pending_court_change: Optional[int] = None
    updated_at: Optional[str] = None


def default_data() -> dict:
    return {
        "match": None,
        "setup_done": False,
        "history": [],
        "tournament": [],
        "t_info": {},
        "updated_at": datetime.now().isoformat(),
    }


def disk_load() -> dict:
    if not os.path.exists(DATA_FILE):
        return default_data()
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        base = default_data()
        base.update(data)
        return base
    except Exception:
        return default_data()


def disk_save(match: Optional[Match], history: List[dict], tournament: List[dict], t_info: dict, setup_done: bool):
    data = {
        "match": asdict(match) if match else None,
        "setup_done": setup_done,
        "history": history,
        "tournament": tournament,
        "t_info": t_info,
        "updated_at": datetime.now().isoformat(),
    }
    tmp = DATA_FILE + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False)
    os.replace(tmp, DATA_FILE)


if "role" not in st.session_state:
    st.session_state.role = None
if "tab" not in st.session_state:
    st.session_state.tab = "score"
if "setup" not in st.session_state:
    st.session_state.setup = {
        "tA": "",
        "tB": "",
        "allA": [""] * ALL_PLAYERS,
        "allB": [""] * ALL_PLAYERS,
        "ordA": [1, 2, 3, 4, 5],
        "ordB": [1, 2, 3, 4, 5],
        "first": "A",
        "tnm": "",
        "trd": "",
    }


def safe_name(v: str, fb: str) -> str:
    v = (v or "").strip()
    return v if v else fb


def nxt(i: int, n: int) -> int:
    return (i + 1) % n


def build_ord(players: List[str], indexes: List[int]) -> List[str]:
    out = []
    for idx in indexes:
        if idx < 1 or idx > len(players):
            return []
        out.append(players[idx - 1])
    return out


def restore_match(data: Optional[dict]) -> Optional[Match]:
    if not data:
        return None
    return Match(**data)


def snapshot(m: Match) -> Dict:
    d = asdict(m)
    d["history"] = []
    return d


def current_server(m: Match) -> str:
    return (m.curA if m.srv == "A" else m.curB) or "—"


def change_hit(scA: int, scB: int, done: Dict[int, bool]) -> Optional[int]:
    for p in COURT_CHG:
        if not done.get(p, False) and (scA == p or scB == p):
            return p
    return None


def new_match(tA, tB, allA, allB, pA, pB, oA, oB, first, tnm=None, trd=None) -> Match:
    cA, cB, nA, nB = (oA[0], None, 1, 0) if first == "A" else (None, oB[0], 0, 1)
    now = datetime.now()
    return Match(
        tA=tA,
        tB=tB,
        allA=allA,
        allB=allB,
        onA=pA,
        onB=pB,
        ordA=oA,
        ordB=oB,
        setno=1,
        sA=0,
        sB=0,
        scA=0,
        scB=0,
        srv=first,
        hand="R",
        swapped=False,
        curA=cA,
        curB=cB,
        nxtA=nA,
        nxtB=nB,
        subA=3,
        subB=3,
        toA=1,
        toB=1,
        ms={9: False, 18: False, 27: False},
        history=[],
        events=[f"Match started · {(tA if first == 'A' else tB)} serves first"],
        over=False,
        winner=None,
        psA=[],
        psB=[],
        ppA={p: 0 for p in pA},
        ppB={p: 0 for p in pB},
        started=now.strftime("%d %b %Y %H:%M:%S"),
        ended=None,
        mid=now.strftime("%Y%m%d%H%M%S"),
        tnm=tnm,
        trd=trd,
        pending_court_change=None,
        updated_at=now.strftime("%d %b %Y %H:%M:%S"),
    )


def persist_state(match: Optional[Match], data: dict):
    disk_save(match, data.get("history", []), data.get("tournament", []), data.get("t_info", {}), bool(match))


def push_event(m: Match, text: str):
    m.events.insert(0, text)
    m.events = m.events[:60]
    m.updated_at = datetime.now().strftime("%d %b %Y %H:%M:%S")


def do_point(winner: str, data: dict):
    m = restore_match(data.get("match"))
    if not m or m.over:
        return
    m.history.append(snapshot(m))
    m.history = m.history[-20:]

    if winner == "A":
        m.scA += 1
        if m.curA:
            m.ppA[m.curA] = m.ppA.get(m.curA, 0) + 1
    else:
        m.scB += 1
        if m.curB:
            m.ppB[m.curB] = m.ppB.get(m.curB, 0) + 1

    if winner != m.srv:
        m.srv = winner
        if winner == "A":
            m.curA = m.ordA[m.nxtA]
            m.nxtA = nxt(m.nxtA, PLAYERS)
        else:
            m.curB = m.ordB[m.nxtB]
            m.nxtB = nxt(m.nxtB, PLAYERS)

    push_event(m, f"▸ {(m.tA if winner == 'A' else m.tB)}  {m.scA}–{m.scB}  srv:{current_server(m)}")

    hit = change_hit(m.scA, m.scB, m.ms)
    if hit:
        m.ms[hit] = True
        m.pending_court_change = hit
        push_event(m, f"🔄 Court change required at {hit}")

    if max(m.scA, m.scB) >= SET_POINTS and abs(m.scA - m.scB) >= 2:
        sw = "A" if m.scA > m.scB else "B"
        if sw == "A":
            m.sA += 1
        else:
            m.sB += 1
        m.psA.append(m.scA)
        m.psB.append(m.scB)
        push_event(m, f"✅ Set {m.setno} → {(m.tA if sw == 'A' else m.tB)} ({m.scA}–{m.scB})")

        if m.sA == 2 or m.sB == 2:
            m.over = True
            m.winner = "A" if m.sA == 2 else "B"
            m.ended = datetime.now().strftime("%d %b %Y %H:%M:%S")
            push_event(m, f"🏆 {(m.tA if m.winner == 'A' else m.tB)} wins the match")
            hist = data.get("history", [])
            hist.append(
                {
                    "id": m.mid,
                    "date": m.started,
                    "tA": m.tA,
                    "tB": m.tB,
                    "sA": m.sA,
                    "sB": m.sB,
                    "sets": list(zip(m.psA, m.psB)),
                    "winner": m.tA if m.winner == "A" else m.tB,
                    "tnm": m.tnm,
                    "trd": m.trd,
                    "ppA": dict(m.ppA),
                    "ppB": dict(m.ppB),
                }
            )
            data["history"] = hist
            data["match"] = asdict(m)
            persist_state(m, data)
            return

        m.setno += 1
        m.scA = 0
        m.scB = 0
        m.subA = 3
        m.subB = 3
        m.toA = 1
        m.toB = 1
        m.ms = {9: False, 18: False, 27: False}
        m.pending_court_change = None
        push_event(m, f"▶️ Set {m.setno} begins")

    data["match"] = asdict(m)
    persist_state(m, data)


def do_undo(data: dict):
    m = restore_match(data.get("match"))
    if not m or not m.history:
        return
    prev = m.history.pop()
    restored = restore_match(prev)
    data["match"] = asdict(restored)
    persist_state(restored, data)


def do_hand(data: dict):
    m = restore_match(data.get("match"))
    if not m:
        return
    m.hand = "L" if m.hand == "R" else "R"
    push_event(m, f"✋ Hand → {'Left' if m.hand == 'L' else 'Right'}")
    data["match"] = asdict(m)
    persist_state(m, data)


def do_court_toggle(data: dict):
    m = restore_match(data.get("match"))
    if not m:
        return
    m.swapped = not m.swapped
    m.pending_court_change = None
    push_event(m, "🔄 Court sides changed")
    data["match"] = asdict(m)
    persist_state(m, data)


def do_timeout(team: str, data: dict):
    m = restore_match(data.get("match"))
    if not m:
        return
    if team == "A":
        if m.toA <= 0:
            return
        m.toA -= 1
        push_event(m, f"⏱️ Timeout: {m.tA}")
    else:
        if m.toB <= 0:
            return
        m.toB -= 1
        push_event(m, f"⏱️ Timeout: {m.tB}")
    data["match"] = asdict(m)
    persist_state(m, data)


def do_sub(team: str, on: str, off: str, data: dict):
    m = restore_match(data.get("match"))
    if not m or not on or not off or on == off:
        return
    if team == "A":
        if m.subA <= 0 or on in m.onA or off not in m.onA:
            return
        idx = m.onA.index(off)
        m.onA[idx] = on
        m.ppA.setdefault(on, 0)
        m.subA -= 1
        push_event(m, f"🔁 {m.tA}: {off} → {on}")
    else:
        if m.subB <= 0 or on in m.onB or off not in m.onB:
            return
        idx = m.onB.index(off)
        m.onB[idx] = on
        m.ppB.setdefault(on, 0)
        m.subB -= 1
        push_event(m, f"🔁 {m.tB}: {off} → {on}")
    data["match"] = asdict(m)
    persist_state(m, data)


def reset_match(data: dict):
    data["match"] = None
    persist_state(None, data)


def render_login():
    st.markdown(
        """
        <div class='hero center'>
          <div style='font-size:3rem'>🏸</div>
          <div style='font-size:2rem;font-weight:900;color:#0f172a'>Ball Badminton Live</div>
          <div class='muted'>Admin scoring and viewer live scoreboard</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("<div class='loginbox'>", unsafe_allow_html=True)
        st.markdown("### Viewer Login")
        vu = st.text_input("Viewer username", key="viewer_u", placeholder="viewer")
        vp = st.text_input("Viewer password", key="viewer_p", placeholder="viewer password", type="password")
        if st.button("Open Live Score", key="viewer_login"):
            if vu == VIEWER_USER and vp == VIEWER_PASS:
                st.session_state.role = "viewer"
                st.rerun()
            else:
                st.error("Invalid viewer credentials")
        st.markdown("<div class='small-note'>Viewer can only watch live score and match stats.</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    with c2:
        st.markdown("<div class='loginbox'>", unsafe_allow_html=True)
        st.markdown("### Admin Login")
        au = st.text_input("Admin username", key="admin_u", placeholder="admin username")
        ap = st.text_input("Admin password", key="admin_p", placeholder="admin password", type="password")
        if st.button("Login as Admin", key="admin_login"):
            if au == ADMIN_USER and ap == ADMIN_PASS:
                st.session_state.role = "admin"
                st.rerun()
            else:
                st.error("Invalid admin credentials")
        st.markdown("<div class='small-note'>Admin controls setup, score entry, undo, subs, and timeout.</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)


def render_topbar(role: str, setup_done: bool):
    st.markdown("<div class='navwrap'>", unsafe_allow_html=True)
    labels = [("score", "🏸 Score"), ("stats", "📊 Stats"), ("history", "📜 History")]
    if role == "admin":
        labels.insert(2, ("tournament", "🏆 Tournament"))
        labels.append(("admin", "⚙️ Admin"))
    cols = st.columns(len(labels) + 2)
    for i, (key, label) in enumerate(labels):
        with cols[i]:
            if st.button(label, key=f"nav_{key}"):
                st.session_state.tab = key
                st.rerun()
    with cols[-2]:
        if role == "admin" and setup_done:
            if st.button("🔄 New Match", key="new_match"):
                d = disk_load()
                reset_match(d)
                st.session_state.tab = "score"
                st.rerun()
        else:
            st.empty()
    with cols[-1]:
        if st.button("🚪 Logout", key="logout"):
            st.session_state.role = None
            st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)


def render_setup(data: dict):
    st.markdown("## Match Setup")
    setup = st.session_state.setup
    with st.expander("Tournament details (optional)"):
        tnm = st.text_input("Tournament name", value=setup.get("tnm", ""))
        trd = st.text_input("Round", value=setup.get("trd", ""))

    c1, c2 = st.columns(2)
    with c1:
        tA = st.text_input("Team A name", value=setup.get("tA", ""), placeholder="Enter Team A")
    with c2:
        tB = st.text_input("Team B name", value=setup.get("tB", ""), placeholder="Enter Team B")

    st.markdown("### Players")
    ca, cb = st.columns(2)
    allA, allB = [], []
    with ca:
        st.markdown(f"**{tA or 'Team A'}**")
        for i in range(ALL_PLAYERS):
            allA.append(st.text_input(f"A Player {i+1}", value=setup["allA"][i], key=f"A{i}"))
    with cb:
        st.markdown(f"**{tB or 'Team B'}**")
        for i in range(ALL_PLAYERS):
            allB.append(st.text_input(f"B Player {i+1}", value=setup["allB"][i], key=f"B{i}"))

    allA_f = [safe_name(v, f"A{i+1}") for i, v in enumerate(allA)]
    allB_f = [safe_name(v, f"B{i+1}") for i, v in enumerate(allB)]

    st.markdown("### Select 5 starting players")
    s1, s2 = st.columns(2)
    with s1:
        mpA = st.multiselect(f"{tA or 'Team A'} starters", allA_f, default=allA_f[:5], max_selections=5)
    with s2:
        mpB = st.multiselect(f"{tB or 'Team B'} starters", allB_f, default=allB_f[:5], max_selections=5)

    errs = []
    oA2, oB2 = [], []
    if len(mpA) == 5 and len(mpB) == 5:
        st.markdown("### Service order")
        o1, o2 = st.columns(2)
        oAi, oBi = [], []
        with o1:
            for k in range(PLAYERS):
                opts = [f"{i+1}. {mpA[i]}" for i in range(PLAYERS)]
                sel = st.selectbox(f"{tA or 'A'} serve {k+1}", opts, key=f"oA{k}")
                oAi.append(int(sel.split(".")[0]))
        with o2:
            for k in range(PLAYERS):
                opts = [f"{i+1}. {mpB[i]}" for i in range(PLAYERS)]
                sel = st.selectbox(f"{tB or 'B'} serve {k+1}", opts, key=f"oB{k}")
                oBi.append(int(sel.split(".")[0]))
        if len(set(oAi)) != 5:
            errs.append("Team A service order must be unique")
        if len(set(oBi)) != 5:
            errs.append("Team B service order must be unique")
        oA2 = build_ord(list(mpA), oAi)
        oB2 = build_ord(list(mpB), oBi)
        if not oA2 or not oB2:
            errs.append("Invalid service order")
        first = st.radio("First serve", [tA or "Team A", tB or "Team B"], horizontal=True)
        first_side = "A" if first == (tA or "Team A") else "B"
    else:
        first_side = "A"
        errs.append("Select exactly 5 players in each team")

    for e in errs:
        st.error(e)

    if st.button("Start Match", disabled=bool(errs)):
        match = new_match(
            safe_name(tA, "Team A"),
            safe_name(tB, "Team B"),
            allA_f,
            allB_f,
            list(mpA),
            list(mpB),
            oA2,
            oB2,
            first_side,
            tnm or None,
            trd or None,
        )
        data["match"] = asdict(match)
        persist_state(match, data)
        st.rerun()


def render_score(m: Match, role: str, data: dict):
    if role == "viewer":
        auto_refresh(2500)
        st.caption(f"Live auto-refresh is ON · Last update: {m.updated_at or data.get('updated_at', '-')}")

    if m.pending_court_change:
        st.markdown(
            f"<div class='banner'>🔄 Court change required now at score point {m.pending_court_change}. Use the Court button after players switch sides.</div>",
            unsafe_allow_html=True,
        )

    if m.over:
        st.markdown(
            f"<div class='winner'>🏆 {(m.tA if m.winner == 'A' else m.tB)} wins the match</div>",
            unsafe_allow_html=True,
        )

    if m.tnm:
        st.markdown(
            f"<div class='muted' style='margin-bottom:0.5rem'>🏆 {m.tnm}{(' · ' + m.trd) if m.trd else ''}</div>",
            unsafe_allow_html=True,
        )

    left, right = st.columns([2.35, 1], gap="medium")
    lt = "B" if m.swapped else "A"
    rt = "A" if m.swapped else "B"
    tn = lambda t: m.tA if t == "A" else m.tB
    sc = lambda t: m.scA if t == "A" else m.scB
    ss = lambda t: m.sA if t == "A" else m.sB

    with left:
        st.markdown(
            f"""
            <div class='score-shell'>
              <div class='score-row'>
                <div class='score-team'>
                  <div class='team-name'>{'🟠 ' if m.srv == lt else ''}{tn(lt)}</div>
                  <div class='score-no {'active' if m.srv == lt else ''}'>{sc(lt)}</div>
                  <div class='team-meta'>Sets: {ss(lt)} · {'Left' if not m.swapped and lt == 'A' or m.swapped and lt == 'B' else 'Right'}</div>
                </div>
                <div class='vs'>VS</div>
                <div class='score-team right'>
                  <div class='team-name'>{'🟠 ' if m.srv == rt else ''}{tn(rt)}</div>
                  <div class='score-no {'active' if m.srv == rt else ''}'>{sc(rt)}</div>
                  <div class='team-meta'>Sets: {ss(rt)} · {'Right' if not m.swapped and rt == 'B' or m.swapped and rt == 'A' else 'Left'}</div>
                </div>
              </div>
              <div class='center muted' style='margin-top:0.65rem;font-weight:700'>Set {m.setno}/3 · Target {SET_POINTS} · Court change at 9 · 18 · 27</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if m.psA:
            cols = st.columns(len(m.psA))
            for i, (a, b) in enumerate(zip(m.psA, m.psB)):
                with cols[i]:
                    st.markdown(
                        f"<div class='set-card'><div class='muted'>Set {i+1}</div><div style='font-size:1.3rem;font-weight:800'>{a}–{b}</div><div style='font-size:0.9rem;color:#c2410c'>{m.tA if a > b else m.tB}</div></div>",
                        unsafe_allow_html=True,
                    )

        with st.container(border=False):
            c1, c2, c3, c4 = st.columns(4)
            with c1:
                st.metric("Serving", m.tA if m.srv == "A" else m.tB)
            with c2:
                st.metric("Server", current_server(m))
            with c3:
                st.metric("Hand", "Right" if m.hand == "R" else "Left")
            with c4:
                st.metric("Updated", m.updated_at or "-")

        if role == "admin":
            p1, p2 = st.columns(2)
            with p1:
                st.markdown("<div class='point-btn'>", unsafe_allow_html=True)
                if st.button(f"+1 {m.tA}", key="ptA", disabled=m.over):
                    do_point("A", disk_load())
                    st.rerun()
                st.markdown("</div>", unsafe_allow_html=True)
            with p2:
                st.markdown("<div class='point-btn point-btn-blue'>", unsafe_allow_html=True)
                if st.button(f"+1 {m.tB}", key="ptB", disabled=m.over):
                    do_point("B", disk_load())
                    st.rerun()
                st.markdown("</div>", unsafe_allow_html=True)

            a1, a2, a3 = st.columns(3)
            with a1:
                if st.button("↩️ Undo", disabled=not m.history):
                    do_undo(disk_load())
                    st.rerun()
            with a2:
                if st.button("✋ Change Hand"):
                    do_hand(disk_load())
                    st.rerun()
            with a3:
                if st.button("🔄 Court Changed"):
                    do_court_toggle(disk_load())
                    st.rerun()

            st.markdown("### Subs and timeout")
            s1, s2 = st.columns(2)
            for team, col in [("A", s1), ("B", s2)]:
                tm = restore_match(disk_load().get("match")) or m
                tname = tm.tA if team == "A" else tm.tB
                on = tm.onA if team == "A" else tm.onB
                allp = tm.allA if team == "A" else tm.allB
                subs = tm.subA if team == "A" else tm.subB
                to_left = tm.toA if team == "A" else tm.toB
                with col:
                    st.markdown(f"**{tname}**")
                    st.markdown(
                        f"<span class='pill pill-green'>Subs left: {subs}</span> <span class='pill pill-blue'>Timeouts left: {to_left}</span>",
                        unsafe_allow_html=True,
                    )
                    bench = [p for p in allp if p and p not in on]
                    if bench and subs > 0:
                        on_p = st.selectbox("Player in", bench, key=f"in_{team}")
                        off_p = st.selectbox("Player out", on, key=f"out_{team}")
                        if st.button(f"Confirm Sub {tname}", key=f"sub_{team}"):
                            do_sub(team, on_p, off_p, disk_load())
                            st.rerun()
                    if to_left > 0:
                        if st.button(f"Timeout {tname}", key=f"to_{team}_{m.setno}"):
                            do_timeout(team, disk_load())
                            st.rerun()

    with right:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("**Service order**")
        st.markdown(f"<div class='muted' style='margin-top:0.4rem'>{m.tA}</div>", unsafe_allow_html=True)
        for i, p in enumerate(m.ordA, 1):
            prefix = "🟠" if m.srv == "A" and m.curA == p else f"{i}."
            st.markdown(f"{prefix} {p}")
        st.markdown(f"<div class='muted' style='margin-top:0.8rem'>{m.tB}</div>", unsafe_allow_html=True)
        for i, p in enumerate(m.ordB, 1):
            prefix = "🟠" if m.srv == "B" and m.curB == p else f"{i}."
            st.markdown(f"{prefix} {p}")
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<div class='card' style='margin-top:0.8rem'>", unsafe_allow_html=True)
        st.markdown("**On court**")
        st.markdown(f"<div class='muted'>{m.tA}</div>", unsafe_allow_html=True)
        st.markdown(", ".join(m.onA))
        st.markdown(f"<div class='muted' style='margin-top:0.7rem'>{m.tB}</div>", unsafe_allow_html=True)
        st.markdown(", ".join(m.onB))
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<div class='card' style='margin-top:0.8rem'>", unsafe_allow_html=True)
        st.markdown("**Live events**")
        for e in m.events[:16]:
            st.markdown(f"<div class='event-item'>{e}</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)


def render_stats(m: Match):
    st.markdown("## Match Statistics")
    total = m.scA + m.scB + sum(m.psA) + sum(m.psB)
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Current set", f"Set {m.setno}")
    with c2:
        st.metric("Sets", f"{m.sA}–{m.sB}")
    with c3:
        st.metric("Current score", f"{m.scA}–{m.scB}")
    with c4:
        st.metric("Total points", total)

    st.markdown("### Points by player")
    p1, p2 = st.columns(2)
    with p1:
        st.markdown(f"**{m.tA}**")
        for p, pts in sorted(m.ppA.items(), key=lambda x: -x[1]):
            st.write(f"{p}: {pts}")
    with p2:
        st.markdown(f"**{m.tB}**")
        for p, pts in sorted(m.ppB.items(), key=lambda x: -x[1]):
            st.write(f"{p}: {pts}")

    with st.expander("Full event log"):
        for e in m.events:
            st.write(e)


def render_history(data: dict):
    st.markdown("## Match History")
    hist = data.get("history", [])
    if not hist:
        st.info("No completed matches yet.")
        return
    for h in reversed(hist):
        with st.container(border=True):
            st.markdown(f"### {h['tA']} vs {h['tB']}")
            st.caption(h["date"])
            if h.get("tnm"):
                st.caption(f"🏆 {h['tnm']} {h.get('trd', '')}")
            st.write(f"Sets: {h['sA']}–{h['sB']}")
            st.write(f"Winner: {h['winner']}")
            if h.get("sets"):
                st.write(" | ".join([f"Set {i+1}: {a}-{b}" for i, (a, b) in enumerate(h["sets"])]))


def render_tournament(data: dict):
    st.markdown("## Tournament Bracket")
    with st.container(border=True):
        tn = st.text_input("Tournament name", key="br_name")
        n = st.selectbox("No. of teams", [4, 8, 16], key="br_n")
        team_names = []
        cols = st.columns(2)
        for i in range(n):
            with cols[i % 2]:
                team_names.append(st.text_input(f"Team {i+1}", key=f"br_team_{i}", value=f"Team {i+1}"))
        if st.button("Generate bracket"):
            shuffled = team_names[:]
            random.shuffle(shuffled)
            data["tournament"] = [{"r": "Round 1", "tA": shuffled[i], "tB": shuffled[i+1], "w": None} for i in range(0, len(shuffled), 2)]
            data["t_info"] = {"name": tn, "teams": team_names}
            persist_state(restore_match(data.get("match")), data)
            st.rerun()
    if data.get("tournament"):
        st.subheader(data.get("t_info", {}).get("name", "Tournament"))
        for i, mb in enumerate(data["tournament"]):
            with st.container(border=True):
                st.write(f"{mb['tA']} vs {mb['tB']}")
                if not mb["w"]:
                    w = st.radio("Winner", [mb["tA"], mb["tB"]], key=f"bw_{i}", horizontal=True)
                    if st.button("Confirm", key=f"bc_{i}"):
                        data["tournament"][i]["w"] = w
                        persist_state(restore_match(data.get("match")), data)
                        st.rerun()
                else:
                    st.success(f"Winner: {mb['w']}")


def render_admin(data: dict, m: Optional[Match]):
    st.markdown("## Admin Panel")
    with st.container(border=True):
        if m:
            c1, c2, c3 = st.columns(3)
            with c1:
                st.metric("Match", f"{m.tA} vs {m.tB}")
            with c2:
                st.metric("Set", f"{m.setno}/3")
            with c3:
                st.metric("Score", f"{m.scA}–{m.scB}")
        else:
            st.info("No active match")
    with st.container(border=True):
        export = {
            "match": data.get("match"),
            "history": data.get("history", []),
            "tournament": data.get("tournament", []),
            "t_info": data.get("t_info", {}),
            "exported": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
        st.download_button(
            "Export JSON",
            data=json.dumps(export, indent=2),
            file_name=f"ballbadminton_{datetime.now().strftime('%Y%m%d')}.json",
            mime="application/json",
        )
    with st.container(border=True):
        st.markdown("### Notes")
        st.write("Viewer screen auto-refreshes and reads the shared save file on every refresh.")
        st.write("For 100 simultaneous users, deploy on a server with enough CPU/RAM. The app now supports multi-session viewing, but hosting capacity depends on where you deploy it.")


def main():
    data = disk_load()
    match = restore_match(data.get("match"))
    role = st.session_state.role

    if role is None:
        render_login()
        return

    render_topbar(role, bool(match))

    if role == "viewer":
        st.info("Viewer mode: read-only live score. This screen refreshes automatically.")
        if not match:
            st.warning("No active match right now.")
            auto_refresh(3000)
            return
        if st.session_state.tab not in {"score", "stats", "history"}:
            st.session_state.tab = "score"
        if st.session_state.tab == "score":
            render_score(match, role, data)
        elif st.session_state.tab == "stats":
            render_stats(match)
        else:
            render_history(data)
        return

    if not match and st.session_state.tab == "score":
        render_setup(data)
        return

    if not match:
        st.warning("No active match. Open Score tab and start a match.")
        return

    tab = st.session_state.tab
    if tab == "score":
        render_score(match, role, data)
    elif tab == "stats":
        render_stats(match)
    elif tab == "history":
        render_history(data)
    elif tab == "tournament":
        render_tournament(data)
    elif tab == "admin":
        render_admin(data, match)


main()
