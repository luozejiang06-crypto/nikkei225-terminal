code = '''import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os
from deep_translator import MyMemoryTranslator, GoogleTranslator

st.set_page_config(page_title="NIKKEI 225 QUANTITATIVE TERMINAL", layout="wide", initial_sidebar_state="expanded")

if "watchlist" not in st.session_state:
    st.session_state.watchlist = []

def get_stock_logo_url(ticker, code):
    return f"https://ui-avatars.com/api/?name={code}&background=181c26&color=38bdf8&rounded=true&bold=true"

@st.cache_data(ttl=604800)
def translate_text_zh(text):
    if not text or not text.strip():
        return ""
    trimmed = text[:350]
    translated = ""
    try:
        translated = MyMemoryTranslator(source='auto', target='zh-CN').translate(trimmed)
    except Exception:
        pass
    if not translated:
        try:
            translated = GoogleTranslator(source='auto', target='zh-CN').translate(trimmed)
        except Exception:
            pass
    return translated if translated else text

@st.cache_data(ttl=604800)
def get_company_summary_zh(ticker):
    try:
        t = yf.Ticker(ticker)
        raw_summary = t.info.get("longBusinessSummary", "")
        if not raw_summary:
            return "暂无该公司业务详细介绍。"
        translated = translate_text_zh(raw_summary)
        if translated and translated != raw_summary[:350]:
            return f"【中文业务速览】\\n{translated}\\n\\n---\\n【官方完整介绍 (原文)】\\n{raw_summary}"
        else:
            return f"【官方主营业务简介 (原文)】\\n\\n{raw_summary}"
    except Exception:
        return "暂无该公司业务详细介绍。"

def calculate_rsi(series, period=14):
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

st.markdown("""
<style>
    .stApp {
        background-color: #080a0f !important;
        background-image: 
            radial-gradient(circle at 15% 20%, rgba(20, 24, 45, 0.85) 0%, transparent 45%),
            radial-gradient(circle at 85% 75%, rgba(10, 30, 45, 0.7) 0%, transparent 50%),
            radial-gradient(circle at 50% 50%, rgba(13, 16, 26, 0.95) 0%, #05070a 100%),
            linear-gradient(rgba(255, 255, 255, 0.015) 1px, transparent 1px),
            linear-gradient(90deg, rgba(255, 255, 255, 0.015) 1px, transparent 1px) !important;
        background-size: 100% 100%, 100% 100%, 100% 100%, 35px 35px, 35px 35px !important;
        color: #e2e8f0;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, monospace;
    }
    section[data-testid="stSidebar"] {
        background-color: #0b0d13 !important;
        border-right: 1px solid rgba(255, 255, 255, 0.08) !important;
    }
    .cyber-title {
        font-size: 2.1rem; font-weight: 800; letter-spacing: 1.5px;
        background: linear-gradient(90deg, #ffffff 0%, #7dd3fc 60%, #38bdf8 100%);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    }
    .cyber-caption { color: #64748b; font-size: 0.82rem; letter-spacing: 1px; text-transform: uppercase; margin-bottom: 22px; }
    .author-badge {
        display: inline-block; padding: 2px 10px; border-radius: 20px; font-size: 0.75rem;
        color: #38bdf8; background: rgba(56, 189, 248, 0.1); border: 1px solid rgba(56, 189, 248, 0.3);
        margin-left: 12px; vertical-align: middle;
    }
    .company-desc-card {
        background: rgba(16, 20, 30, 0.6); border: 1px solid rgba(56, 189, 248, 0.15);
        border-radius: 8px; padding: 14px 18px; color: #cbd5e1; font-size: 0.88rem; line-height: 1.7; white-space: pre-line;
    }
    .signal-box {
        background: rgba(16, 20, 30, 0.65); border-radius: 8px; padding: 12px 16px;
        border: 1px solid rgba(56, 189, 248, 0.2); margin-bottom: 12px;
    }
    div[data-testid="stMetric"] {
        background: rgba(16, 20, 30, 0.65) !important; border: 1px solid rgba(56, 189, 248, 0.2) !important;
        border-radius: 8px; padding: 10px 14px;
    }
    div[data-testid="stMetricValue"] { color: #38bdf8 !important; font-size: 1.35rem !important; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div>
    <span class="cyber-title">⚡ NIKKEI 225 QUANTITATIVE TERMINAL</span>
    <span class="author-badge">DEV: lzjppy</span>
</div>
<div class="cyber-caption">日经平均指数（日経225）智能量化终端 // 深度指标雷达与技术走势穿透</div>
""", unsafe_allow_html=True)

CSV_PATH = 'nikkei225_data.csv'
if not os.path.exists(CSV_PATH):
    st.error('SYSTEM ERROR: 数据库未挂载，请先运行数据抓取脚本！')
    st.stop()

@st.cache_data
def load_data():
    df = pd.read_csv(CSV_PATH)
    df['日股代码'] = df['日股代码'].astype(str)
    return df

df_raw = load_data()

st.sidebar.markdown("<h4 style='color: #f1f5f9;'>⚡ 因子控制矩阵 (日股)</h4>", unsafe_allow_html=True)
all_sectors = sorted([str(s) for s in df_raw['行业板块'].dropna().unique()])
selected_sectors = st.sidebar.multiselect('行业板块 (SECTOR)', options=all_sectors, default=all_sectors)

max_cap = float(df_raw['市值 (兆¥)'].max(skipna=True) or 50.0)
selected_cap = st.sidebar.slider('最低市值 (兆円 / 兆¥)', 0.0, max_cap, 0.5, 0.5)
max_pe = st.sidebar.slider('最高滚动市盈率 (PER)', 5.0, 80.0, 40.0, 1.0)
min_roe = st.sidebar.slider('最低 ROE (%)', -20.0, 40.0, 5.0, 1.0)
min_growth = st.sidebar.slider('最低营收增长率 (%)', -20.0, 40.0, 0.0, 2.0)
min_dividend = st.sidebar.slider('最低股息率 (%)', 0.0, 6.0, 0.0, 0.2)
above_50ma = st.sidebar.checkbox('仅筛选站在 50 日均线之上')

filtered = df_raw.copy()
if selected_sectors:
    filtered = filtered[filtered['行业板块'].isin(selected_sectors)]
filtered = filtered[(filtered['市值 (兆¥)'].notnull()) & (filtered['市值 (兆¥)'] >= selected_cap)]
filtered = filtered[(filtered['滚动PE'].isnull()) | (filtered['滚动PE'] <= max_pe)]
filtered = filtered[(filtered['ROE (%)'].isnull()) | (filtered['ROE (%)'] >= min_roe)]
filtered = filtered[(filtered['营收增速 (%)'].isnull()) | (filtered['营收增速 (%)'] >= min_growth)]
if min_dividend > 0:
    filtered = filtered[filtered['股息率 (%)'] >= min_dividend]
if above_50ma:
    filtered = filtered[(filtered['偏离50日线 (%)'].notnull()) & (filtered['偏离50日线 (%)'] > 0)]

tab_screener, tab_watchlist = st.tabs(['⚡ 日经量化筛选矩阵与单票穿透', '⭐ 我的专属日股自选池'])

with tab_screener:
    c1, c2, c3 = st.columns(3)
    c1.metric('日经225 总量池', f'{len(df_raw)} 标的')
    c2.metric('当前符合条件', f'{len(filtered)} 标的')
    c3.metric('有效收敛率', f'{round(len(filtered) / len(df_raw) * 100, 1) if len(df_raw) > 0 else 0}%')

    display_df = filtered.copy().reset_index(drop=True)
    display_df['标的'] = display_df.apply(lambda r: get_stock_logo_url(r['代码'], r['日股代码']), axis=1)
    cols = ['标的', '日股代码', '公司名称', '行业板块', '现价 (¥)', '市值 (兆¥)', '滚动PE', 'ROE (%)', '营收增速 (%)', '股息率 (%)', '偏离50日线 (%)']
    final_cols = [c for c in cols if c in display_df.columns]
    display_df = display_df[final_cols]

    st.dataframe(
        display_df.style.format({
            '现价 (¥)': '¥{:.1f}', '市值 (兆¥)': '¥{:.2f} 兆', '滚动PE': '{:.1f}',
            'ROE (%)': '{:.1f}%', '营收增速 (%)': '{:.1f}%', '股息率 (%)': '{:.2f}%', '偏离50日线 (%)': '{:+.2f}%'
        }),
        column_config={'标的': st.column_config.ImageColumn(label='标识', width='small')},
        use_container_width=True, height=380, hide_index=True
    )

    available_codes = filtered['日股代码'].tolist() if len(filtered) > 0 else df_raw['日股代码'].tolist()
    col_sel, col_p, col_fav = st.columns([2, 1, 1])
    with col_sel:
        code_map = {c: f"{c} - {df_raw[df_raw['日股代码']==c].iloc[0]['公司名称']}" for c in available_codes}
        sel_code = st.selectbox('选择日股标的：', options=available_codes, format_func=lambda x: code_map.get(x, x), index=0)
        sel_ticker = f"{sel_code}.T"
    with col_p:
        sel_p = st.selectbox('走势周期：', ['1mo', '3mo', '6mo', '1y', '2y', '5y'], index=3)
    with col_fav:
        st.markdown("<div style='margin-top: 28px;'></div>", unsafe_allow_html=True)
        is_fav = sel_code in st.session_state.watchlist
        if st.button('⭐ 移出自选' if is_fav else '➕ 加入自选', use_container_width=True):
            if is_fav:
                st.session_state.watchlist.remove(sel_code)
            else:
                st.session_state.watchlist.append(sel_code)
            st.rerun()

    if sel_ticker:
        t = yf.Ticker(sel_ticker)
        hist = t.history(period='max' if sel_p == '5y' else '2y')
        stock_info = t.info
        s_row = df_raw[df_raw['日股代码'] == sel_code].iloc[0]
        
        st.markdown(f'''
        <div style="background: rgba(16, 20, 30, 0.7); padding: 12px 18px; border-radius: 8px; border: 1px solid rgba(56, 189, 248, 0.2); margin-bottom: 12px;">
            <span style="font-size: 1.4rem; font-weight: 700; color: #f1f5f9;">{sel_code} {s_row['公司名称']}</span>
            <span style="color: #38bdf8; margin-left: 12px; font-size: 0.85rem;">{s_row['行业板块']} // NIKKEI 225</span>
        </div>
        ''', unsafe_allow_html=True)

        k1, k2, k3, k4, k5 = st.columns(5)
        k1.metric('最新股价', f"¥{s_row['现价 (¥)']:.1f}" if pd.notnull(s_row['现价 (¥)']) else '--')
        k2.metric('总市值', f"¥{s_row['市值 (兆¥)']:.2f} 兆" if pd.notnull(s_row['市值 (兆¥)']) else '--')
        k3.metric('滚动 PER', f"{s_row['滚动PE']}" if pd.notnull(s_row['滚动PE']) else '--')
        k4.metric('ROE', f"{s_row['ROE (%)']}%" if pd.notnull(s_row['ROE (%)']) else '--')
        k5.metric('股息率', f"{s_row['股息率 (%)']:.2f}%" if pd.notnull(s_row['股息率 (%)']) else '--')

        with st.expander(f"📖 查看 {sel_code} ({s_row['公司名称']}) 业务概况与主营介绍", expanded=False):
            summary_zh = get_company_summary_zh(sel_ticker)
            st.markdown(f'<div class="company-desc-card">{summary_zh}</div>', unsafe_allow_html=True)

        if not hist.empty:
            hist['MA20'] = hist['Close'].rolling(20).mean()
            hist['MA50'] = hist['Close'].rolling(50).mean()
            p_map = {'1mo': 30, '3mo': 90, '6mo': 180, '1y': 365, '2y': 730, '5y': 1825}
            sub_hist = hist.tail(p_map.get(sel_p, 365))
            
            fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.03, row_heights=[0.75, 0.25])
            fig.add_trace(go.Candlestick(x=sub_hist.index, open=sub_hist['Open'], high=sub_hist['High'], low=sub_hist['Low'], close=sub_hist['Close'], name='K线'), row=1, col=1)
            fig.add_trace(go.Scatter(x=sub_hist.index, y=sub_hist['MA20'], line=dict(color='#fadb14', width=1.5), name='MA20'), row=1, col=1)
            fig.add_trace(go.Scatter(x=sub_hist.index, y=sub_hist['MA50'], line=dict(color='#38bdf8', width=1.5), name='MA50'), row=1, col=1)
            colors = ['rgba(0, 230, 118, 0.55)' if c >= o else 'rgba(255, 82, 82, 0.55)' for c, o in zip(sub_hist['Close'], sub_hist['Open'])]
            fig.add_trace(go.Bar(x=sub_hist.index, y=sub_hist['Volume'], marker_color=colors, name='成交量', showlegend=False), row=2, col=1)
            fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(11, 14, 23, 0.75)', height=520, margin=dict(l=10, r=20, t=20, b=10), xaxis_rangeslider_visible=False)
            st.plotly_chart(fig, use_container_width=True)

with tab_watchlist:
    st.markdown("<h4 style='color: #f1f5f9;'>⭐ 个人日股量化自选池</h4>", unsafe_allow_html=True)
    if not st.session_state.watchlist:
        st.info('自选池暂为空白。可点击【➕ 加入自选】进行添加。')
    else:
        w_df = df_raw[df_raw['日股代码'].isin(st.session_state.watchlist)].copy().reset_index(drop=True)
        st.dataframe(w_df, use_container_width=True, hide_index=True)
'''

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(code)
print("app.py 创建成功！")