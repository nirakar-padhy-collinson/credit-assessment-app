CUSTOM_CSS = """
<style>
:root {
    --bg-top: #f8f4ee;
    --bg-bottom: #efe6d9;
    --surface: rgba(255, 251, 247, 0.82);
    --surface-strong: rgba(255, 252, 248, 0.94);
    --surface-dark: #13202d;
    --ink-strong: #182230;
    --ink-soft: #5b6778;
    --accent: #b07a3f;
    --accent-deep: #8d5f2d;
    --line: rgba(34, 45, 60, 0.10);
    --shadow-lg: 0 28px 60px rgba(20, 34, 50, 0.10);
    --shadow-md: 0 18px 36px rgba(20, 34, 50, 0.08);
}

html, body, [class*="css"] {
    font-family: "Source Sans Pro", "Segoe UI", sans-serif;
}

.stApp {
    background:
        radial-gradient(circle at top left, rgba(190, 153, 102, 0.18), transparent 25%),
        radial-gradient(circle at top right, rgba(24, 40, 59, 0.10), transparent 22%),
        linear-gradient(180deg, var(--bg-top) 0%, #f4ede3 44%, var(--bg-bottom) 100%);
}

.block-container {
    padding-top: 1.2rem;
    padding-right: 2rem;
    padding-bottom: 2.25rem;
    padding-left: 2rem;
    max-width: none;
}

[data-testid="stHeader"] {
    background: rgba(248, 244, 238, 0.72);
    backdrop-filter: blur(14px);
}

section[data-testid="stSidebar"] {
    background:
        linear-gradient(180deg, rgba(22, 34, 49, 0.98) 0%, rgba(29, 46, 65, 0.98) 100%);
    border-right: 1px solid rgba(255, 255, 255, 0.08);
}

.hero {
    position: relative;
    overflow: hidden;
    background:
        linear-gradient(130deg, rgba(255, 251, 247, 0.96) 0%, rgba(244, 236, 225, 0.94) 55%, rgba(230, 217, 198, 0.88) 100%);
    border: 1px solid rgba(34, 45, 60, 0.08);
    border-radius: 32px;
    padding: 2.25rem 2.25rem 2rem;
    box-shadow: var(--shadow-lg);
    margin-bottom: 1.4rem;
}

.hero::after {
    content: "";
    position: absolute;
    inset: auto -10% -45% 42%;
    height: 260px;
    background: radial-gradient(circle, rgba(176, 122, 63, 0.20) 0%, rgba(176, 122, 63, 0) 72%);
    pointer-events: none;
}

.hero-grid {
    display: grid;
    grid-template-columns: minmax(0, 1.7fr) minmax(260px, 0.9fr);
    gap: 1.25rem;
    align-items: stretch;
}

.hero-eyebrow {
    display: inline-flex;
    align-items: center;
    gap: 0.45rem;
    padding: 0.38rem 0.72rem;
    margin-bottom: 1rem;
    border-radius: 999px;
    background: rgba(17, 29, 43, 0.05);
    border: 1px solid rgba(17, 29, 43, 0.08);
    color: #5b6674;
    font-size: 0.8rem;
    font-weight: 700;
    letter-spacing: 0.12em;
    text-transform: uppercase;
}

.hero h1 {
    margin: 0;
    color: var(--ink-strong);
    font-family: "Georgia", "Times New Roman", serif;
    font-size: 3.15rem;
    line-height: 0.98;
    font-weight: 700;
    letter-spacing: -0.05em;
}

.hero p {
    margin: 0.9rem 0 0 0;
    max-width: 46rem;
    color: var(--ink-soft);
    font-size: 1.06rem;
    line-height: 1.7;
}

.hero-panel {
    position: relative;
    z-index: 1;
    align-self: end;
    background: linear-gradient(180deg, rgba(19, 32, 45, 0.96) 0%, rgba(26, 44, 62, 0.98) 100%);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 28px;
    padding: 1.2rem 1.2rem 1.1rem;
    box-shadow: 0 24px 50px rgba(17, 27, 39, 0.24);
}

.hero-panel-label {
    color: rgba(242, 228, 208, 0.78);
    font-size: 0.78rem;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    margin-bottom: 0.55rem;
}

.hero-panel-value {
    color: #fff7ef;
    font-size: 1.55rem;
    font-weight: 700;
    letter-spacing: -0.03em;
}

.hero-panel-copy {
    color: rgba(240, 230, 217, 0.82);
    font-size: 0.95rem;
    line-height: 1.6;
    margin-top: 0.6rem;
}

.glass-card {
    background: var(--surface);
    backdrop-filter: blur(16px);
    border: 1px solid var(--line);
    border-radius: 24px;
    padding: 1.2rem 1.2rem;
    box-shadow: var(--shadow-md);
}

.section-gap {
    height: 0.65rem;
}

.metric-card {
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    background: linear-gradient(180deg, rgba(255, 252, 248, 0.92) 0%, rgba(248, 242, 234, 0.88) 100%);
    border: 1px solid rgba(34, 45, 60, 0.09);
    border-radius: 22px;
    padding: 1rem 1.1rem;
    min-height: 180px;
    box-shadow: 0 12px 26px rgba(20, 34, 50, 0.06);
}

.metric-label {
    color: #6f7986;
    font-size: 0.86rem;
    margin-bottom: 0.25rem;
    min-height: 2.8rem;
    text-transform: uppercase;
    letter-spacing: 0.1em;
}

.metric-value {
    font-size: 1.7rem;
    font-weight: 700;
    color: var(--ink-strong);
}

.metric-sub {
    color: #7a8593;
    font-size: 0.85rem;
    margin-top: auto;
}

.section-title {
    color: var(--ink-strong);
    font-size: 1.08rem;
    font-weight: 700;
    margin-bottom: 0.45rem;
    letter-spacing: -0.02em;
}

.section-banner {
    display: inline-flex;
    align-items: center;
    padding: 0.52rem 0.82rem;
    margin: 0.2rem 0 1rem;
    border-radius: 999px;
    background: rgba(176, 122, 63, 0.10);
    border: 1px solid rgba(176, 122, 63, 0.16);
    color: #6c5639;
    font-size: 0.9rem;
}

.stat-card {
    height: 100%;
    margin-top: 0.8rem;
    padding: 0.95rem 1rem 0.9rem;
    border-radius: 20px;
    background: rgba(255, 252, 248, 0.74);
    border: 1px solid rgba(34, 45, 60, 0.08);
    display: flex;
    flex-direction: column;
}

.stat-card:first-child {
    margin-top: 0.5rem;
}

.stat-card-compact {
    min-height: 158px;
    margin-top: 0.35rem;
    padding: 0.9rem 0.95rem 0.85rem;
}

.stat-card.risk-low {
    border-color: rgba(52, 120, 71, 0.20);
    background: rgba(226, 244, 230, 0.82);
}

.stat-card.risk-moderate,
.stat-card.risk-elevated {
    border-color: rgba(196, 142, 43, 0.20);
    background: rgba(251, 241, 212, 0.86);
}

.stat-card.risk-high {
    border-color: rgba(179, 67, 54, 0.22);
    background: rgba(251, 226, 223, 0.88);
}

.stat-card-label {
    color: #617083;
    font-size: 0.82rem;
    font-weight: 700;
    letter-spacing: 0.1em;
    text-transform: uppercase;
}

.stat-card-value {
    margin-top: 0.45rem;
    color: var(--ink-strong);
    font-size: clamp(1.55rem, 2.1vw, 2.75rem);
    line-height: 1.06;
    font-weight: 700;
    letter-spacing: -0.04em;
    word-break: break-word;
}

.stat-card-compact .stat-card-value {
    font-size: clamp(1.45rem, 1.9vw, 2.3rem);
}

.stat-card-description {
    margin-top: 0.5rem;
    color: #6c7786;
    font-size: 0.9rem;
    line-height: 1.5;
    margin-top: auto;
    padding-top: 0.75rem;
}

.stat-card-compact .stat-card-description {
    font-size: 0.86rem;
    line-height: 1.45;
    padding-top: 0.55rem;
}

.driver-item {
    margin-top: 0.55rem;
    padding: 0.85rem 0.95rem;
    border-radius: 18px;
    font-size: 0.93rem;
    line-height: 1.4;
    border: 1px solid transparent;
}

.driver-supportive {
    background: linear-gradient(90deg, rgba(231, 240, 230, 0.95), rgba(223, 236, 205, 0.8));
    border-color: rgba(68, 99, 74, 0.10);
    color: #405046;
}

.driver-adverse {
    background: linear-gradient(90deg, rgba(248, 226, 222, 0.96), rgba(246, 235, 214, 0.82));
    border-color: rgba(140, 69, 60, 0.10);
    color: #5f4944;
}

.decision-badge {
    display: inline-flex;
    padding: 0.48rem 0.9rem;
    border-radius: 999px;
    font-weight: 600;
    font-size: 0.86rem;
    border: 1px solid transparent;
}
.badge-approve { background: #dff2e3; color: #24623a; border-color: rgba(36, 98, 58, 0.16); }
.badge-conditional { background: #f8edcb; color: #8d6117; border-color: rgba(141, 97, 23, 0.18); }
.badge-review { background: #e7edf6; color: #365a7a; border-color: rgba(54, 90, 122, 0.16); }
.badge-decline { background: #f8dedd; color: #a2352d; border-color: rgba(162, 53, 45, 0.18); }
.risk-low { color: #44634a; }
.risk-moderate { color: #8b6125; }
.risk-elevated { color: #9a5c36; }
.risk-high { color: #8b453c; }
.small-note { color: #7a6653; font-size: 0.84rem; }

.table-wrap {
    background: rgba(248, 244, 237, 0.82);
    border-radius: 18px;
    padding: 0.5rem;
    border: 1px solid rgba(111, 91, 73, 0.10);
}

[data-testid="stDataFrame"] {
    border-radius: 18px;
    overflow: hidden;
    border: 1px solid rgba(34, 45, 60, 0.08);
}

[data-testid="stDataFrame"] [role="grid"] {
    background: rgba(255, 252, 248, 0.82);
}

.stTabs [data-baseweb="tab-list"] {
    gap: 10px;
    background: rgba(19, 32, 45, 0.07);
    border: 1px solid rgba(19, 32, 45, 0.07);
    border-radius: 20px;
    padding: 6px;
}

.stTabs [data-baseweb="tab"] {
    border-radius: 16px;
    padding: 11px 18px;
    color: #5b6674;
    font-weight: 700;
}

.stTabs [aria-selected="true"] {
    background: var(--surface-strong);
    color: var(--ink-strong);
    box-shadow: 0 1px 0 rgba(34, 45, 60, 0.05), 0 8px 20px rgba(20, 34, 50, 0.08);
}

div[data-testid="stForm"] {
    background: linear-gradient(180deg, rgba(255, 252, 248, 0.92) 0%, rgba(249, 244, 236, 0.88) 100%);
    padding: 1.15rem;
    border: 1px solid rgba(34, 45, 60, 0.09);
    border-radius: 24px;
    box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.72), 0 18px 34px rgba(20, 34, 50, 0.05);
}

div[data-testid="stForm"] button[kind="formSubmit"] {
    min-height: 3rem;
    margin-top: 0.35rem;
}

.form-intro {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    gap: 1rem;
    margin-bottom: 1rem;
    padding-bottom: 0.95rem;
    border-bottom: 1px solid rgba(34, 45, 60, 0.08);
}

.form-intro p {
    margin: 0.25rem 0 0;
}

.form-chip {
    white-space: nowrap;
    padding: 0.45rem 0.75rem;
    border-radius: 999px;
    background: rgba(19, 32, 45, 0.08);
    color: #415061;
    font-size: 0.84rem;
    font-weight: 700;
}

.form-section-label {
    margin: 0 0 0.65rem;
    color: #344253;
    font-size: 0.84rem;
    font-weight: 700;
    letter-spacing: 0.1em;
    text-transform: uppercase;
}

[data-testid="stMetricValue"] {
    color: var(--ink-strong);
}

[data-testid="stMetricLabel"] {
    color: #6c7786;
}

.stExpander {
    border-radius: 20px;
    border: 1px solid rgba(34, 45, 60, 0.08);
    background: rgba(255, 252, 248, 0.72);
    overflow: hidden;
}

.stAlert {
    border-radius: 18px;
}

h3 {
    color: var(--ink-strong);
    letter-spacing: -0.03em;
}

p, label, .stCaption {
    color: var(--ink-soft);
}

.glass-card p {
    margin: 0.35rem 0;
    line-height: 1.6;
}

.workflow-grid {
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 0.95rem;
}

.workflow-step {
    padding: 1rem;
    border-radius: 20px;
    background: rgba(255, 252, 248, 0.74);
    border: 1px solid rgba(34, 45, 60, 0.08);
}

.workflow-step-number {
    color: var(--accent);
    font-size: 0.82rem;
    font-weight: 700;
    letter-spacing: 0.12em;
    text-transform: uppercase;
}

.workflow-step-title {
    margin-top: 0.45rem;
    color: var(--ink-strong);
    font-size: 1rem;
    font-weight: 700;
}

.sidebar-brand {
    margin-bottom: 1rem;
    padding: 1rem 0.95rem;
    border-radius: 22px;
    background: linear-gradient(180deg, rgba(255, 251, 246, 0.12) 0%, rgba(255, 251, 246, 0.05) 100%);
    border: 1px solid rgba(255, 255, 255, 0.10);
}

.sidebar-brand-eyebrow {
    color: rgba(230, 214, 194, 0.70);
    font-size: 0.76rem;
    font-weight: 700;
    letter-spacing: 0.12em;
    text-transform: uppercase;
}

.sidebar-brand-title {
    margin-top: 0.35rem;
    color: #fff7ef;
    font-family: "Georgia", "Times New Roman", serif;
    font-size: 1.4rem;
    font-weight: 700;
    line-height: 1.1;
}

.sidebar-brand-copy {
    margin-top: 0.45rem;
    color: rgba(241, 231, 219, 0.76);
    font-size: 0.9rem;
    line-height: 1.5;
}

section[data-testid="stSidebar"] .stMarkdown,
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] .stCaption,
section[data-testid="stSidebar"] p {
    color: rgba(247, 239, 229, 0.92);
}

section[data-testid="stSidebar"] [data-baseweb="radio"] label,
section[data-testid="stSidebar"] [data-baseweb="checkbox"] label {
    color: rgba(247, 239, 229, 0.92) !important;
}

section[data-testid="stSidebar"] [data-testid="stButton"] button,
section[data-testid="stSidebar"] [data-testid="stDownloadButton"] button,
div[data-testid="stForm"] button[kind="formSubmit"],
[data-testid="stFormSubmitButton"] button {
    background: linear-gradient(135deg, #b9884f 0%, #9f6c34 100%);
    color: #fffaf3 !important;
    border: none;
    box-shadow: 0 12px 24px rgba(159, 108, 52, 0.24);
}

section[data-testid="stSidebar"] [data-testid="stButton"] button:hover,
section[data-testid="stSidebar"] [data-testid="stDownloadButton"] button:hover,
div[data-testid="stForm"] button[kind="formSubmit"]:hover,
[data-testid="stFormSubmitButton"] button:hover {
    background: linear-gradient(135deg, #c5965f 0%, #ab7539 100%);
}

[data-testid="stFormSubmitButton"] button {
    min-height: 3.1rem;
    font-weight: 700;
}

div[data-testid="stForm"] button[kind="formSubmit"] *,
[data-testid="stFormSubmitButton"] button * {
    color: #fffaf3 !important;
    font-weight: 700 !important;
}

[data-baseweb="input"] input,
[data-baseweb="select"] > div,
textarea {
    border-radius: 14px !important;
}

[data-testid="stNumberInput"] [data-baseweb="input"] > div,
[data-testid="stTextInput"] [data-baseweb="input"] > div,
[data-testid="stSelectbox"] [data-baseweb="select"] > div,
[data-testid="stMultiSelect"] [data-baseweb="select"] > div {
    min-height: 58px !important;
    height: 58px !important;
    box-sizing: border-box;
}

[data-testid="stNumberInput"] input,
[data-testid="stTextInput"] input,
[data-testid="stSelectbox"] [role="combobox"],
[data-testid="stMultiSelect"] [role="combobox"] {
    min-height: 24px;
    line-height: 1.3 !important;
}

[data-testid="stNumberInput"],
[data-testid="stTextInput"],
[data-testid="stSelectbox"],
[data-testid="stMultiSelect"] {
    margin-bottom: 0.15rem;
}

[data-baseweb="select"] {
    overflow: visible !important;
}

[data-testid="stMultiSelect"] [data-baseweb="select"] input {
    opacity: 1 !important;
    min-width: 1px !important;
}

[data-testid="column"] {
    display: flex;
    flex-direction: column;
}

[data-testid="column"] > div {
    width: 100%;
}

[data-testid="stHorizontalBlock"] {
    align-items: flex-start;
}

[data-testid="stMultiSelect"] [data-baseweb="select"] > div,
[data-testid="stSelectbox"] [data-baseweb="select"] > div {
    align-items: center;
    padding-top: 0 !important;
    padding-bottom: 0 !important;
}

[data-testid="stMultiSelect"] label[data-testid="stWidgetLabel"],
[data-testid="stSelectbox"] label[data-testid="stWidgetLabel"],
[data-testid="stNumberInput"] label[data-testid="stWidgetLabel"],
[data-testid="stTextInput"] label[data-testid="stWidgetLabel"] {
    min-height: 2rem;
    margin-bottom: 0.2rem;
}

[data-testid="stMultiSelect"] [data-baseweb="select"] [role="combobox"],
[data-testid="stSelectbox"] [data-baseweb="select"] [role="combobox"] {
    line-height: 1.35 !important;
    min-height: 28px;
}

[data-testid="stMultiSelect"] [data-baseweb="select"] span {
    display: inline-flex;
    align-items: center;
    min-height: 24px;
}

label[data-testid="stWidgetLabel"] p {
    color: var(--ink-strong);
    font-weight: 600;
}

[data-testid="stDataFrame"] {
    width: 100%;
}

[data-testid="stDataFrame"] [role="gridcell"],
[data-testid="stDataFrame"] [role="columnheader"] {
    align-items: center;
}

[data-testid="stAltairChart"],
[data-testid="stDataFrame"] {
    margin-top: 0.35rem;
}

.stTabs [data-testid="stVerticalBlock"] > [data-testid="stHorizontalBlock"] {
    width: 100%;
}

@media (max-width: 900px) {
    .hero {
        padding: 1.4rem 1.2rem;
        border-radius: 24px;
    }

    .hero-grid,
    .workflow-grid,
    .form-intro {
        grid-template-columns: 1fr;
        display: grid;
    }

    .hero h1 {
        font-size: 2.25rem;
    }
}
</style>
"""
