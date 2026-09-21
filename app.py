import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os
import urllib.parse
from deep_translator import MyMemoryTranslator, GoogleTranslator

st.set_page_config(
    page_title="NIKKEI 225 QUANT TERMINAL",
    layout="wide",
    initial_sidebar_state="expanded"
)

if "watchlist" not in st.session_state:
    st.session_state.watchlist = []

# 日经225 核心企业官方日文名与企业官方主站域名
JP_COMPANIES = {
    "1332": ("ニッスイ", "nissui.co.jp"),
    "1605": ("INPEX", "inpex.co.jp"),
    "1721": ("コムシスHD", "comsys.co.jp"),
    "1801": ("大成建設", "taisei.co.jp"),
    "1802": ("大林組", "obayashi.co.jp"),
    "1803": ("清水建設", "shimz.co.jp"),
    "1808": ("長谷工コーポレーション", "haseko.co.jp"),
    "1812": ("鹿島建設", "kajima.co.jp"),
    "1925": ("大和ハウス工業", "daiwahouse.co.jp"),
    "1928": ("積水ハウス", "sekisuihouse.co.jp"),
    "1963": ("日揮HD", "jgc.com"),
    "2002": ("日清製粉グループ本社", "nisshin.com"),
    "2269": ("明治HD", "meiji.com"),
    "2282": ("日本ハム", "nipponham.co.jp"),
    "2501": ("サッポロHD", "sapporoholdings.jp"),
    "2502": ("アサヒグループHD", "asahigroup-holdings.com"),
    "2503": ("キリンHD", "kirinholdings.com"),
    "2801": ("キッコーマン", "kikkoman.co.jp"),
    "2802": ("味の素", "ajinomoto.co.jp"),
    "2871": ("ニチレイ", "nichirei.co.jp"),
    "2914": ("日本たばこ産業 (JT)", "jti.com"),
    "3086": ("J.フロント リテイリング", "j-front-retailing.com"),
    "3099": ("三越伊勢丹HD", "imhds.co.jp"),
    "3382": ("セブン＆アイ・HD", "7andi.com"),
    "3401": ("帝人", "teijin.co.jp"),
    "3402": ("東レ", "toray.co.jp"),
    "3405": ("クラレ", "kuraray.co.jp"),
    "3407": ("旭化成", "asahi-kasei.com"),
    "3861": ("王子HD", "ojiholdings.co.jp"),
    "3863": ("日本製紙", "nipponpapergroup.com"),
    "4004": ("レゾナック・HD", "resonac.com"),
    "4005": ("住友化学", "sumitomo-chem.co.jp"),
    "4021": ("日産化学", "nissanchem.co.jp"),
    "4042": ("東ソー", "tosoh.co.jp"),
    "4043": ("トクヤマ", "tokuyama.co.jp"),
    "4061": ("デンカ", "denka.co.jp"),
    "4063": ("信越化学工業", "shinetsu.co.jp"),
    "4183": ("三井化学", "mitsuichemicals.com"),
    "4188": ("三菱ケミカルグループ", "mcgc.com"),
    "4208": ("UBE", "ube.com"),
    "4452": ("花王", "kao.com"),
    "4502": ("武田薬品工業", "takeda.com"),
    "4503": ("アステラス製薬", "astellas.com"),
    "4506": ("住友ファーマ", "sumitomo-pharma.co.jp"),
    "4507": ("塩野義製薬", "shionogi.com"),
    "4519": ("中外製薬", "chugai-pharm.co.jp"),
    "4523": ("エーザイ", "eisai.co.jp"),
    "4568": ("第一三共", "daiichisankyo.co.jp"),
    "4578": ("大塚HD", "otsuka.com"),
    "4631": ("DIC", "dic-global.com"),
    "4689": ("LINEヤフー", "lycorp.co.jp"),
    "4704": ("トレンドマイクロ", "trendmicro.com"),
    "4751": ("サイバーエージェント", "cyberagent.co.jp"),
    "4755": ("楽天グループ", "rakuten.co.jp"),
    "4901": ("富士フイルムHD", "fujifilm.com"),
    "4911": ("資生堂", "shiseido.com"),
    "5019": ("出光興産", "idemitsu.com"),
    "5020": ("ENEOS HD", "eneos.co.jp"),
    "5101": ("横浜ゴム", "y-yokohama.com"),
    "5108": ("ブリヂストン", "bridgestone.co.jp"),
    "5201": ("AGC", "agc.com"),
    "5202": ("日本板硝子", "nsg.com"),
    "5214": ("日本電気硝子", "neg.co.jp"),
    "5232": ("住友大阪セメント", "soc.co.jp"),
    "5233": ("太平洋セメント", "taiheiyo-cement.co.jp"),
    "5301": ("東海カーボン", "tokaicarbon.co.jp"),
    "5332": ("TOTO", "toto.com"),
    "5333": ("日本ガイシ", "ngk.co.jp"),
    "5401": ("日本製鉄", "nipponsteel.com"),
    "5406": ("神戸製鋼所", "kobelco.co.jp"),
    "5411": ("JFE HD", "jfe-holdings.co.jp"),
    "5541": ("大平洋金属", "pacific-metals.co.jp"),
    "5706": ("三井金属鉱業", "mitsui-kinzoku.co.jp"),
    "5707": ("東邦亜鉛", "toho-zinc.co.jp"),
    "5711": ("三菱マテリアル", "mmc.co.jp"),
    "5713": ("住友金属鉱山", "smm.co.jp"),
    "5714": ("DOWA HD", "dowa.co.jp"),
    "5801": ("古河電気工業", "furukawa.co.jp"),
    "5802": ("住友電気工業", "sei.co.jp"),
    "5803": ("フジクラ", "fujikura.co.jp"),
    "6113": ("アマダ", "amada.co.jp"),
    "6178": ("日本郵政", "japanpost.jp"),
    "6301": ("小松製作所 (コマツ)", "komatsu.jp"),
    "6302": ("住友重機械工業", "shi.co.jp"),
    "6305": ("日立建機", "hitachicm.com"),
    "6326": ("クボタ", "kubota.co.jp"),
    "6361": ("荏原製作所", "ebara.co.jp"),
    "6367": ("ダイキン工業", "daikin.co.jp"),
    "6471": ("日本精工", "nsk.com"),
    "6472": ("NTN", "ntn.co.jp"),
    "6473": ("ジェイテクト", "jtekt.co.jp"),
    "6479": ("ミネベアミツミ", "minebeamitsumi.com"),
    "6501": ("日立製作所", "hitachi.co.jp"),
    "6502": ("東芝", "global.toshiba"),
    "6503": ("三菱電機", "mitsubishielectric.co.jp"),
    "6504": ("富士電機", "fujielectric.co.jp"),
    "6506": ("安川電機", "yaskawa.co.jp"),
    "6526": ("ソシオネクスト", "socionext.com"),
    "6674": ("GSユアサ", "gs-yuasa.com"),
    "6701": ("日本電気 (NEC)", "nec.com"),
    "6702": ("富士通", "fujitsu.com"),
    "6703": ("沖電気工業", "oki.com"),
    "6723": ("ルネサス エレクトロニクス", "renesas.com"),
    "6724": ("セイコーエプソン", "epson.jp"),
    "6752": ("パナソニック HD", "panasonic.com"),
    "6758": ("ソニーグループ", "sony.com"),
    "6762": ("TDK", "tdk.com"),
    "6770": ("アルプスアルパイン", "alpsalpine.com"),
    "6841": ("横河電機", "yokogawa.co.jp"),
    "6857": ("アドバンテスト", "advantest.com"),
    "6861": ("キーエンス", "keyence.co.jp"),
    "6902": ("デンソー", "denso.com"),
    "6920": ("レーザーテック", "lasertec.co.jp"),
    "6952": ("カシオ計算機", "casio.com"),
    "6954": ("ファナック", "fanuc.co.jp"),
    "6971": ("京セラ", "kyocera.co.jp"),
    "6976": ("太陽誘電", "yuden.co.jp"),
    "6981": ("村田製作所", "murata.com"),
    "6988": ("日東電工", "nitto.com"),
    "7011": ("三菱重工業", "mhi.com"),
    "7012": ("川崎重工業", "khi.co.jp"),
    "7013": ("IHI", "ihi.co.jp"),
    "7201": ("日産自動車", "nissan-global.com"),
    "7202": ("いすゞ自動車", "isuzu.co.jp"),
    "7203": ("トヨタ自動車", "toyota.jp"),
    "7205": ("日野自動車", "hino.co.jp"),
    "7211": ("三菱自動車工業", "mitsubishi-motors.com"),
    "7261": ("マツダ", "mazda.co.jp"),
    "7267": ("本田技研工業 (ホンダ)", "honda.co.jp"),
    "7269": ("スズキ", "suzuki.co.jp"),
    "7270": ("SUBARU", "subaru.co.jp"),
    "7272": ("ヤマハ発動機", "yamaha-motor.co.jp"),
    "7731": ("ニコン", "nikon.co.jp"),
    "7733": ("オリンパス", "olympus.co.jp"),
    "7735": ("SCREEN HD", "screen.co.jp"),
    "7741": ("HOYA", "hoya.co.jp"),
    "7751": ("キヤノン", "canon.jp"),
    "7752": ("リコー", "ricoh.co.jp"),
    "7762": ("シチズン時計", "citizen.co.jp"),
    "7911": ("TOPPAN HD", "holdings.toppan.com"),
    "7912": ("大日本印刷", "dnp.co.jp"),
    "7951": ("ヤマハ", "yamaha.com"),
    "7974": ("任天堂", "nintendo.co.jp"),
    "8001": ("伊藤忠商事", "itochu.co.jp"),
    "8002": ("丸紅", "marubeni.com"),
    "8015": ("豊田通商", "toyota-tsusho.com"),
    "8031": ("三井物産", "mitsui.com"),
    "8035": ("東京エレクトロン", "tel.co.jp"),
    "8053": ("住友商事", "sumitomocorp.com"),
    "8058": ("三菱商事", "mitsubishicorp.com"),
    "8233": ("高島屋", "takashimaya.co.jp"),
    "8252": ("丸井グループ", "0101maruigroup.co.jp"),
    "8267": ("イオン", "aeon.info"),
    "8304": ("あおぞら銀行", "aozorabank.co.jp"),
    "8306": ("三菱UFJフィナンシャルG", "mufg.jp"),
    "8308": ("りそなHD", "resona-gr.co.jp"),
    "8309": ("三井住友トラストHD", "smth.jp"),
    "8316": ("三井住友フィナンシャルG", "smfg.co.jp"),
    "8331": ("千葉銀行", "chibabank.co.jp"),
    "8354": ("ふくおかフィナンシャルG", "fukuoka-fg.com"),
    "8355": ("静岡フィナンシャルG", "shizuoka-fg.co.jp"),
    "8411": ("みずほフィナンシャルG", "mizuho-fg.co.jp"),
    "8591": ("オリックス", "orix.co.jp"),
    "8601": ("大和証券グループ本社", "daiwa-grp.jp"),
    "8604": ("野村HD", "nomuraholdings.com"),
    "8630": ("SOMPO HD", "sompo-hd.com"),
    "8697": ("日本取引所グループ", "jpx.co.jp"),
    "8725": ("MS&ADインシュアランスG", "ms-ad-hd.com"),
    "8750": ("第一生命HD", "dai-ichi-life-hd.com"),
    "8766": ("東京海上HD", "tokiomarinehd.com"),
    "8795": ("T&D HD", "td-hd.co.jp"),
    "8801": ("三井不動産", "mitsuifudosan.co.jp"),
    "8802": ("三菱地所", "mec.co.jp"),
    "8804": ("東京建物", "tatemono.com"),
    "8830": ("住友不動産", "sumitomo-rd.co.jp"),
    "9001": ("東武鉄道", "tobu.co.jp"),
    "9002": ("西武HD", "seibu-holdings.co.jp"),
    "9005": ("東急", "tokyu.co.jp"),
    "9007": ("小田急電鉄", "odakyu.jp"),
    "9008": ("京王電鉄", "keio.co.jp"),
    "9009": ("京成電鉄", "keisei.co.jp"),
    "9020": ("東日本旅客鉄道 (JR東日本)", "jreast.co.jp"),
    "9021": ("西日本旅客鉄道 (JR西日本)", "westjr.co.jp"),
    "9022": ("東海旅客鉄道 (JR東海)", "jr-central.co.jp"),
    "9064": ("ヤマトHD", "yamato-hd.co.jp"),
    "9101": ("日本郵船", "nyk.com"),
    "9104": ("商船三井", "mol.co.jp"),
    "9107": ("川崎汽船", "kline.co.jp"),
    "9201": ("日本航空 (JAL)", "jal.com"),
    "9202": ("ANA HD", "ana.co.jp"),
    "9301": ("三菱倉庫", "mitsubishi-logistics.co.jp"),
    "9432": ("日本電信電話 (NTT)", "group.ntt"),
    "9433": ("KDDI", "kddi.com"),
    "9434": ("ソフトバンク", "softbank.jp"),
    "9501": ("東京電力HD", "tepco.co.jp"),
    "9502": ("中部電力", "chuden.co.jp"),
    "9503": ("関西電力", "kepco.co.jp"),
    "9531": ("東京瓦斯 (東京ガス)", "tokyo-gas.co.jp"),
    "9532": ("大阪瓦斯 (大阪ガス)", "osakagas.co.jp"),
    "9602": ("東宝", "toho.co.jp"),
    "9613": ("NTTデータグループ", "nttdata.com"),
    "9719": ("SCSK", "scsk.jp"),
    "9735": ("セコム", "secom.co.jp"),
    "9766": ("コナミグループ", "konami.com"),
    "9843": ("ニトリHD", "nitorihd.co.jp"),
    "9983": ("ファーストリテイリング (ユニクロ)", "fastretailing.com"),
    "9984": ("ソフトバンクグループ", "group.softbank")
}

# 提取日企官方矢量极简 Logo
def get_clean_company_logo(code):
    item = JP_COMPANIES.get(str(code))
    domain = item[1] if item else f"{code}.co.jp"
    return f"https://www.google.com/s2/favicons?domain={domain}&sz=128"

# 翻译至中文
@st.cache_data(ttl=604800)
def translate_to_zh(text):
    if not text or not text.strip():
        return ""
    trimmed = text[:380]
    try:
        res = GoogleTranslator(source='en', target='zh-CN').translate(trimmed)
        if res: return res
    except Exception:
        pass
    try:
        res = MyMemoryTranslator(source='en-US', target='zh-CN').translate(trimmed)
        if res and "MYMEMORY" not in str(res).upper(): return res
    except Exception:
        pass
    return ""

# 翻译至日文
@st.cache_data(ttl=604800)
def translate_to_ja(text):
    if not text or not text.strip():
        return ""
    trimmed = text[:380]
    try:
        res = GoogleTranslator(source='en', target='ja').translate(trimmed)
        if res: return res
    except Exception:
        pass
    try:
        res = MyMemoryTranslator(source='en-US', target='ja-JP').translate(trimmed)
        if res and "MYMEMORY" not in str(res).upper(): return res
    except Exception:
        pass
    return ""

# 强力层级 CSS：彻底消除侧边栏及所有输入组件的白块
st.markdown("""
<style>
    /* 全局强制定调 */
    html, body, [class*="css"], .stApp {
        font-family: "Meiryo", "メイリオ", "Meiryo UI", sans-serif !important;
        background-color: #080a0f !important;
        color: #f1f5f9 !important;
    }
    
    /* 彻底消灭左侧栏白底 */
    section[data-testid="stSidebar"] {
        background-color: #0b0f19 !important;
        border-right: 1px solid rgba(255, 255, 255, 0.06) !important;
    }
    
    /* 强制多选下拉框与单选框暗黑化 */
    div[data-baseweb="select"] {
        background-color: #0f172a !important;
        border-radius: 6px !important;
    }
    div[data-baseweb="select"] > div {
        background-color: #0f172a !important;
        border: 1px solid rgba(56, 189, 248, 0.3) !important;
        color: #f1f5f9 !important;
    }
    
    /* 标签药丸 */
    div[data-baseweb="select"] span[data-baseweb="tag"],
    span[data-baseweb="tag"] {
        background-color: #1e293b !important;
        border: 1px solid #38bdf8 !important;
        border-radius: 4px !important;
    }
    div[data-baseweb="select"] span[data-baseweb="tag"] span {
        color: #38bdf8 !important;
        font-family: "Meiryo", sans-serif !important;
        font-weight: 600 !important;
    }

    /* 下拉弹窗列表彻底去白 */
    div[data-baseweb="popover"],
    div[data-baseweb="menu"],
    ul[role="listbox"] {
        background-color: #0f172a !important;
        color: #f1f5f9 !important;
    }

    .cyber-title {
        font-size: 2.0rem;
        font-weight: 800;
        letter-spacing: 1.5px;
        background: linear-gradient(90deg, #ffffff 0%, #7dd3fc 60%, #38bdf8 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-family: "Meiryo", sans-serif !important;
    }
    .cyber-caption {
        color: #64748b;
        font-size: 0.82rem;
        letter-spacing: 1px;
        margin-bottom: 20px;
    }
    .author-badge {
        display: inline-block;
        padding: 2px 10px;
        border-radius: 20px;
        font-size: 0.75rem;
        color: #38bdf8;
        background: rgba(56, 189, 248, 0.1);
        border: 1px solid rgba(56, 189, 248, 0.3);
        margin-left: 12px;
        vertical-align: middle;
    }
    .compact-desc-box {
        background: rgba(16, 21, 36, 0.6);
        border: 1px solid rgba(56, 189, 248, 0.2);
        border-radius: 6px;
        padding: 12px 16px;
        color: #cbd5e1;
        font-size: 0.88rem;
        line-height: 1.65;
        min-height: 90px;
    }
    .desc-header {
        font-size: 0.82rem;
        color: #38bdf8;
        font-weight: bold;
        margin-bottom: 6px;
        letter-spacing: 0.5px;
    }
    div[data-testid="stMetric"] {
        background: rgba(16, 21, 36, 0.8) !important;
        border: 1px solid rgba(56, 189, 248, 0.2) !important;
        border-radius: 8px;
        padding: 10px 14px;
    }
    div[data-testid="stMetricValue"] {
        color: #38bdf8 !important;
        font-size: 1.35rem !important;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div>
    <span class="cyber-title">⚡ NIKKEI 225 QUANTITATIVE TERMINAL</span>
    <span class="author-badge">DEV: lzjppy</span>
</div>
<div class="cyber-caption">日経平均株価（日経225）スマートクオンツターミナル // 深度指標レーダー＆テクニカルトレンド</div>
""", unsafe_allow_html=True)

CSV_PATH = 'nikkei225_data.csv'
if not os.path.exists(CSV_PATH):
    st.error('SYSTEM ERROR: データベースが見つかりません。nikkei225_data.csv を確認してください。')
    st.stop()

def clean_dividend(val):
    if pd.isna(val) or val is None or val <= 0:
        return 0.0
    if val >= 50.0:
        return round(float(val) / 100.0, 2)
    return round(float(val), 2)

@st.cache_data
def load_data():
    df = pd.read_csv(CSV_PATH)
    df['日股代码'] = df['日股代码'].astype(str)
    df['会社名'] = df['日股代码'].map(lambda c: JP_COMPANIES.get(c, (df.loc[df['日股代码']==c, '公司名称'].values[0], ''))[0])
    if "股息率 (%)" in df.columns:
        df["股息率 (%)"] = df["股息率 (%)"].apply(clean_dividend)
    return df

df_raw = load_data()

# 侧边栏：因子控制矩阵
st.sidebar.markdown("<h4 style='color: #f1f5f9;'>⚡ ファクター制御マトリクス (日股)</h4>", unsafe_allow_html=True)
all_sectors = sorted([str(s) for s in df_raw['行业板块'].dropna().unique()])
selected_sectors = st.sidebar.multiselect('業種セクター (SECTOR)', options=all_sectors, default=all_sectors)

max_cap = float(df_raw['市值 (兆¥)'].max(skipna=True) or 50.0)
selected_cap = st.sidebar.slider('最低時価総額 (兆円 / 兆¥)', 0.0, max_cap, 0.5, 0.5)
max_pe = st.sidebar.slider('最高予想・実績 PER', 5.0, 80.0, 40.0, 1.0)
min_roe = st.sidebar.slider('最低 ROE (%)', -20.0, 40.0, 5.0, 1.0)
min_growth = st.sidebar.slider('最低売上高成長率 (%)', -20.0, 40.0, 0.0, 2.0)
min_dividend = st.sidebar.slider('最低配当利回り (%)', 0.0, 6.0, 0.0, 0.2)
above_50ma = st.sidebar.checkbox('50日移動平均線上のみ抽出')

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

tab_screener, tab_watchlist = st.tabs(['⚡ 日経クオンツスクリーナー＆チャート分析', '⭐ マイポートフォリオ（自選銘柄）'])

with tab_screener:
    c1, c2, c3 = st.columns(3)
    c1.metric('日経225 銘柄プール', f'{len(df_raw)} 銘柄')
    c2.metric('条件合致銘柄', f'{len(filtered)} 銘柄')
    c3.metric('絞り込み収束率', f'{round(len(filtered) / len(df_raw) * 100, 1) if len(df_raw) > 0 else 0}%')

    display_df = filtered.copy().reset_index(drop=True)
    display_df['ロゴ'] = display_df['日股代码'].apply(get_clean_company_logo)
    
    cols = ['ロゴ', '日股代码', '会社名', '行业板块', '现价 (¥)', '市值 (兆¥)', '滚动PE', 'ROE (%)', '营收增速 (%)', '股息率 (%)', '偏离50日线 (%)']
    final_cols = [c for c in cols if c in display_df.columns]
    display_df = display_df[final_cols]

    st.dataframe(
        display_df.style.format({
            '现价 (¥)': '¥{:.1f}',
            '市值 (兆¥)': '¥{:.2f} 兆',
            '滚动PE': '{:.1f}',
            'ROE (%)': '{:.1f}%',
            '营收增速 (%)': '{:.1f}%',
            '股息率 (%)': '{:.2f}%',
            '偏离50日线 (%)': '{:+.2f}%'
        }),
        column_config={
            'ロゴ': st.column_config.ImageColumn(label="LOGO", width="small"),
            '日股代码': st.column_config.TextColumn(label='コード', width="small"),
            '会社名': st.column_config.TextColumn(label='会社名', width="medium"),
            '行业板块': st.column_config.TextColumn(label='セクター', width="small"),
            '市值 (兆¥)': st.column_config.NumberColumn(label='時価総額 (兆円)', width="small")
        },
        use_container_width=True,
        height=420,
        hide_index=True
    )

    available_codes = filtered['日股代码'].tolist() if len(filtered) > 0 else df_raw['日股代码'].tolist()
    col_sel, col_p, col_fav = st.columns([2, 1, 1])
    with col_sel:
        code_map = {c: f"{c} - {df_raw[df_raw['日股代码']==c].iloc[0]['会社名']}" for c in available_codes}
        sel_code = st.selectbox('個別銘柄を選択：', options=available_codes, format_func=lambda x: code_map.get(x, x), index=0)
        sel_ticker = f"{sel_code}.T"
    with col_p:
        sel_p = st.selectbox('トレンド期間：', ['1mo', '3mo', '6mo', '1y', '2y', '5y'], index=3)
    with col_fav:
        st.markdown("<div style='margin-top: 28px;'></div>", unsafe_allow_html=True)
        is_fav = sel_code in st.session_state.watchlist
        if st.button('⭐ お気に入り解除' if is_fav else '➕ お気に入り登録', use_container_width=True):
            if is_fav:
                st.session_state.watchlist.remove(sel_code)
            else:
                st.session_state.watchlist.append(sel_code)
            st.rerun()

    if sel_ticker:
        t = yf.Ticker(sel_ticker)
        hist = t.history(period='max' if sel_p == '5y' else '2y')
        s_row = df_raw[df_raw['日股代码'] == sel_code].iloc[0]
        logo_url = get_clean_company_logo(sel_code)
        
        st.markdown(f"""
        <div style="display: flex; align-items: center; gap: 16px; background: rgba(15, 23, 42, 0.85); padding: 12px 18px; border-radius: 8px; border: 1px solid rgba(56, 189, 248, 0.25); margin-bottom: 14px;">
            <div style="background: #0f172a; border: 1px solid rgba(56, 189, 248, 0.3); border-radius: 8px; padding: 6px; display: flex; align-items: center; justify-content: center; width: 48px; height: 48px;">
                <img src="{logo_url}" style="width: 32px; height: 32px; object-fit: contain;">
            </div>
            <div>
                <div style="font-size: 1.45rem; font-weight: 700; color: #f1f5f9;">
                    {sel_code} <span style="margin-left: 6px; color: #ffffff;">{s_row['会社名']}</span>
                </div>
                <div style="color: #38bdf8; font-size: 0.82rem; margin-top: 1px;">{s_row['行业板块']} // NIKKEI 225 構成銘柄</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        k1, k2, k3, k4, k5 = st.columns(5)
        k1.metric('現在株価', f"¥{s_row['现价 (¥)']:.1f}" if pd.notnull(s_row['现价 (¥)']) else '--')
        k2.metric('時価総額', f"¥{s_row['市值 (兆¥)']:.2f} 兆" if pd.notnull(s_row['市值 (兆¥)']) else '--')
        k3.metric('実績 PER', f"{s_row['滚动PE']:.1f}" if pd.notnull(s_row['滚动PE']) else '--')
        k4.metric('ROE (自己資本利益率)', f"{s_row['ROE (%)']:.1f}%" if pd.notnull(s_row['ROE (%)']) else '--')
        k5.metric('配当利回り', f"{s_row['股息率 (%)']:.2f}%" if pd.notnull(s_row['股息率 (%)']) else '--')

        stock_info = t.info
        raw_sum = stock_info.get("longBusinessSummary", "")
        if raw_sum:
            zh_text = translate_to_zh(raw_sum)
            ja_text = translate_to_ja(raw_sum)
            
            c_zh, c_ja = st.columns(2)
            with c_zh:
                st.markdown(f"""
                <div class="compact-desc-box">
                    <div class="desc-header">🇨🇳 中文业务速览</div>
                    {zh_text if zh_text else '暂无翻译内容'}
                </div>
                """, unsafe_allow_html=True)
            with c_ja:
                st.markdown(f"""
                <div class="compact-desc-box">
                    <div class="desc-header">🇯🇵 事業概要 (日本語)</div>
                    {ja_text if ja_text else '概要情報なし'}
                </div>
                """, unsafe_allow_html=True)
            st.markdown("<div style='margin-bottom: 15px;'></div>", unsafe_allow_html=True)

        if not hist.empty:
            hist['MA20'] = hist['Close'].rolling(20).mean()
            hist['MA50'] = hist['Close'].rolling(50).mean()
            p_map = {'1mo': 30, '3mo': 90, '6mo': 180, '1y': 365, '2y': 730, '5y': 1825}
            sub_hist = hist.tail(p_map.get(sel_p, 365))
            
            fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.03, row_heights=[0.75, 0.25])
            fig.add_trace(go.Candlestick(x=sub_hist.index, open=sub_hist['Open'], high=sub_hist['High'], low=sub_hist['Low'], close=sub_hist['Close'], name='ローソク足', increasing_line_color="#00e676", decreasing_line_color="#ff5252"), row=1, col=1)
            fig.add_trace(go.Scatter(x=sub_hist.index, y=sub_hist['MA20'], line=dict(color='#fadb14', width=1.5), name='MA20 (20日線)'), row=1, col=1)
            fig.add_trace(go.Scatter(x=sub_hist.index, y=sub_hist['MA50'], line=dict(color='#38bdf8', width=1.5), name='MA50 (50日線)'), row=1, col=1)
            colors = ['rgba(0, 230, 118, 0.55)' if c >= o else 'rgba(255, 82, 82, 0.55)' for c, o in zip(sub_hist['Close'], sub_hist['Open'])]
            fig.add_trace(go.Bar(x=sub_hist.index, y=sub_hist['Volume'], marker_color=colors, name='出来高', showlegend=False), row=2, col=1)
            fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(15, 23, 42, 0.65)', height=520, margin=dict(l=10, r=20, t=20, b=10), xaxis_rangeslider_visible=False, font=dict(color="#94a3b8", family="Meiryo, monospace"))
            st.plotly_chart(fig, use_container_width=True)

with tab_watchlist:
    st.markdown("<h4 style='color: #f1f5f9;'>⭐ お気に入りポートフォリオ</h4>", unsafe_allow_html=True)
    if not st.session_state.watchlist:
        st.info('お気に入り銘柄がありません。「日経クオンツスクリーナー」タブから【➕ お気に入り登録】で追加できます。')
    else:
        w_df = df_raw[df_raw['日股代码'].isin(st.session_state.watchlist)].copy().reset_index(drop=True)
        w_df['ロゴ'] = w_df['日股代码'].apply(get_clean_company_logo)
        watch_cols = ['ロゴ', '日股代码', '会社名', '行业板块', '现价 (¥)', '市值 (兆¥)', '滚动PE', 'ROE (%)', '股息率 (%)', '偏离50日线 (%)']
        st.dataframe(
            w_df[watch_cols],
            column_config={'ロゴ': st.column_config.ImageColumn(label="LOGO", width="small")},
            use_container_width=True,
            hide_index=True
        )

st.markdown("<br><hr style='border: 1px solid rgba(255,255,255,0.06);'>", unsafe_allow_html=True)
st.markdown("<div style='text-align: center; color: #475569; font-size: 0.8rem;'>DESIGNED & ENGINEERED BY <span style='color: #38bdf8;'>LZJPPY</span> // NIKKEI 225 QUANT TERMINAL</div><br>", unsafe_allow_html=True)
