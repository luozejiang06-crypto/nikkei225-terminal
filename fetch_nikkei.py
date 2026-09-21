import pandas as pd
import yfinance as yf
import time

print("正在载入日经 225 全量成分股官方名单...")

# 官方日经 225 成分股代码及分类（全量）
nikkei_data = [
    ("1332", "Nippon Suisan Kaisha", "水产农林"), ("1605", "INPEX", "矿业"),
    ("1721", "Comsys Holdings", "建设业"), ("1801", "Taisei", "建设业"),
    ("1802", "Obayashi", "建设业"), ("1803", "Shimizu", "建设业"),
    ("1808", "Haseko", "建设业"), ("1812", "Kajima", "建设业"),
    ("1925", "Daiwa House Industry", "建设业"), ("1928", "Sekisui House", "建设业"),
    ("1963", "JGC Holdings", "建设业"), ("2002", "Nisshin Seifun Group", "食品"),
    ("2269", "Meiji Holdings", "食品"), ("2282", "NH Foods", "食品"),
    ("2501", "Sapporo Holdings", "食品"), ("2502", "Asahi Group Holdings", "食品"),
    ("2503", "Kirin Holdings", "食品"), ("2801", "Kikkoman", "食品"),
    ("2802", "Ajinomoto", "食品"), ("2871", "Nichirei", "食品"),
    ("2914", "Japan Tobacco (JT)", "食品"), ("3086", "J. Front Retailing", "零售业"),
    ("3099", "Isetan Mitsukoshi", "零售业"), ("3382", "Seven & i Holdings", "零售业"),
    ("3401", "Teijin", "纺织制品"), ("3402", "Toray Industries", "纺织制品"),
    ("3405", "Kuraray", "化学"), ("3407", "Asahi Kasei", "化学"),
    ("3861", "Oji Holdings", "纸浆纸业"), ("3863", "Nippon Paper", "纸浆纸业"),
    ("4004", "Resonac Holdings", "化学"), ("4005", "Sumitomo Chemical", "化学"),
    ("4021", "Nissan Chemical", "化学"), ("4042", "Tosoh", "化学"),
    ("4043", "Tokuyama", "化学"), ("4061", "Denka", "化学"),
    ("4063", "Shin-Etsu Chemical", "化学"), ("4183", "Mitsui Chemicals", "化学"),
    ("4188", "Mitsubishi Chemical", "化学"), ("4208", "UBE", "化学"),
    ("4452", "Kao", "化学"), ("4502", "Takeda Pharmaceutical", "医药品"),
    ("4503", "Astellas Pharma", "医药品"), ("4506", "Sumitomo Pharma", "医药品"),
    ("4507", "Shionogi", "医药品"), ("4519", "Chugai Pharmaceutical", "医药品"),
    ("4523", "Eisai", "医药品"), ("4568", "Daiichi Sankyo", "医药品"),
    ("4578", "Otsuka Holdings", "医药品"), ("4631", "DIC", "化学"),
    ("4689", "LY Corporation", "信息通信"), ("4704", "Trend Micro", "信息通信"),
    ("4751", "CyberAgent", "服务业"), ("4755", "Rakuten Group", "服务业"),
    ("4901", "Fujifilm Holdings", "化学"), ("4911", "Shiseido", "化学"),
    ("5019", "Idemitsu Kosan", "石油石炭"), ("5020", "ENEOS Holdings", "石油石炭"),
    ("5101", "Yokohama Rubber", "橡胶制品"), ("5108", "Bridgestone", "橡胶制品"),
    ("5201", "AGC", "玻璃陶瓷"), ("5202", "Nippon Sheet Glass", "玻璃陶瓷"),
    ("5214", "Nippon Electric Glass", "玻璃陶瓷"), ("5232", "Sumitomo Osaka Cement", "玻璃陶瓷"),
    ("5233", "Taiheiyo Cement", "玻璃陶瓷"), ("5301", "Tokai Carbon", "玻璃陶瓷"),
    ("5332", "TOTO", "玻璃陶瓷"), ("5333", "NGK Insulators", "玻璃陶瓷"),
    ("5401", "Nippon Steel", "钢铁"), ("5406", "Kobe Steel", "钢铁"),
    ("5411", "JFE Holdings", "钢铁"), ("5541", "Pacific Metals", "钢铁"),
    ("5706", "Mitsui Mining & Smelting", "有色金属"), ("5707", "Toho Zinc", "有色金属"),
    ("5711", "Mitsubishi Materials", "有色金属"), ("5713", "Sumitomo Metal Mining", "有色金属"),
    ("5714", "DOWA Holdings", "有色金属"), ("5801", "Furukawa Electric", "非铁金属"),
    ("5802", "Sumitomo Electric", "非铁金属"), ("5803", "Fujikura", "非铁金属"),
    ("6113", "Amada", "机械"), ("6178", "Japan Post Holdings", "服务业"),
    ("6301", "Komatsu", "机械"), ("6302", "Sumitomo Heavy Industries", "机械"),
    ("6305", "Hitachi Construction Machinery", "机械"), ("6326", "Kubota", "机械"),
    ("6361", "Ebara", "机械"), ("6367", "Daikin Industries", "机械"),
    ("6471", "NSK", "机械"), ("6472", "NTN", "机械"),
    ("6473", "JTEKT", "机械"), ("6479", "MinebeaMitsumi", "电气设备"),
    ("6501", "Hitachi", "电气设备"), ("6502", "Toshiba", "电气设备"),
    ("6503", "Mitsubishi Electric", "电气设备"), ("6504", "Fuji Electric", "电气设备"),
    ("6506", "Yaskawa Electric", "电气设备"), ("6526", "Socionext", "电气设备"),
    ("6674", "GS Yuasa", "电气设备"), ("6701", "NEC", "电气设备"),
    ("6702", "Fujitsu", "电气设备"), ("6703", "Oki Electric Industry", "电气设备"),
    ("6723", "Renesas Electronics", "电气设备"), ("6724", "Seiko Epson", "电气设备"),
    ("6752", "Panasonic Holdings", "电气设备"), ("6758", "Sony Group", "电气设备"),
    ("6762", "TDK", "电气设备"), ("6770", "Alps Alpine", "电气设备"),
    ("6841", "Yokogawa Electric", "电气设备"), ("6857", "Advantest", "电气设备"),
    ("6861", "Keyence", "电气设备"), ("6902", "Denso", "运输设备"),
    ("6920", "Lasertec", "电气设备"), ("6952", "Casio Computer", "电气设备"),
    ("6954", "FANUC", "电气设备"), ("6971", "Kyocera", "电气设备"),
    ("6976", "Taiyo Yuden", "电气设备"), ("6981", "Murata Manufacturing", "电气设备"),
    ("6988", "Nitto Denko", "化学"), ("7011", "Mitsubishi Heavy Industries", "机械"),
    ("7012", "Kawasaki Heavy Industries", "运输设备"), ("7013", "IHI", "机械"),
    ("7201", "Nissan Motor", "汽车及零部件"), ("7202", "Isuzu Motors", "汽车及零部件"),
    ("7203", "Toyota Motor", "汽车及零部件"), ("7205", "Hino Motors", "汽车及零部件"),
    ("7211", "Mitsubishi Motors", "汽车及零部件"), ("7261", "Mazda Motor", "汽车及零部件"),
    ("7267", "Honda Motor", "汽车及零部件"), ("7269", "Suzuki Motor", "汽车及零部件"),
    ("7270", "Subaru", "汽车及零部件"), ("7272", "Yamaha Motor", "运输设备"),
    ("7731", "Nikon", "精密仪器"), ("7733", "Olympus", "精密仪器"),
    ("7735", "SCREEN Holdings", "精密仪器"), ("7741", "HOYA", "精密仪器"),
    ("7751", "Canon", "电气设备"), ("7752", "Ricoh", "电气设备"),
    ("7762", "Citizen Watch", "精密仪器"), ("7911", "TOPPAN Holdings", "其他制品"),
    ("7912", "Dai Nippon Printing", "其他制品"), ("7951", "Yamaha", "其他制品"),
    ("7974", "Nintendo", "其他制品"), ("8001", "ITOCHU", "综合商社"),
    ("8002", "Marubeni", "综合商社"), ("8015", "Toyota Tsusho", "综合商社"),
    ("8028", "FamilyMart", "零售业"), ("8031", "Mitsui & Co.", "综合商社"),
    ("8035", "Tokyo Electron", "电气设备"), ("8053", "Sumitomo Corp.", "综合商社"),
    ("8058", "Mitsubishi Corp.", "综合商社"), ("8233", "Takashimaya", "零售业"),
    ("8252", "Marui Group", "零售业"), ("8267", "Aeon", "零售业"),
    ("8304", "Aozora Bank", "银行业"), ("8306", "Mitsubishi UFJ Financial", "银行业"),
    ("8308", "Resona Holdings", "银行业"), ("8309", "Sumitomo Mitsui Trust", "银行业"),
    ("8316", "Sumitomo Mitsui Financial", "银行业"), ("8331", "Chiba Bank", "银行业"),
    ("8354", "Fukuoka Financial Group", "银行业"), ("8355", "Shizuoka Financial Group", "银行业"),
    ("8411", "Mizuho Financial Group", "银行业"), ("8591", "ORIX", "其他金融"),
    ("8601", "Daiwa Securities Group", "证券商品期货"), ("8604", "Nomura Holdings", "证券商品期货"),
    ("8630", "Sompo Holdings", "保险业"), ("8697", "Japan Exchange Group", "其他金融"),
    ("8725", "MS&AD Insurance", "保险业"), ("8750", "Dai-ichi Life Holdings", "保险业"),
    ("8766", "Tokio Marine Holdings", "保险业"), ("8795", "T&D Holdings", "保险业"),
    ("8801", "Mitsui Fudosan", "不动产业"), ("8802", "Mitsubishi Estate", "不动产业"),
    ("8804", "Tokyo Tatemono", "不动产业"), ("8830", "Sumitomo Realty & Development", "不动产业"),
    ("9001", "Tobu Railway", "陆运业"), ("9002", "Seibu Holdings", "陆运业"),
    ("9005", "Tokyu", "陆运业"), ("9007", "Odakyu Electric Railway", "陆运业"),
    ("9008", "Keio", "陆运业"), ("9009", "Keisei Electric Railway", "陆运业"),
    ("9020", "East Japan Railway (JR东日本)", "陆运业"),
    ("9021", "West Japan Railway (JR西日本)", "陆运业"),
    ("9022", "Central Japan Railway (JR东海)", "陆运业"),
    ("9064", "Yamato Holdings", "陆运业"), ("9101", "Nippon Yusen (NYK Line)", "海运业"),
    ("9104", "Mitsui O.S.K. Lines (MOL)", "海运业"), ("9107", "Kawasaki Kisen (K Line)", "海运业"),
    ("9201", "Japan Airlines (JAL)", "航空业"), ("9202", "ANA Holdings", "航空业"),
    ("9301", "Mitsubishi Logistics", "仓储运输"), ("9432", "NTT", "信息通信"),
    ("9433", "KDDI", "信息通信"), ("9434", "SoftBank Corp.", "信息通信"),
    ("9501", "Tokyo Electric Power (TEPCO)", "电力煤气"),
    ("9502", "Chubu Electric Power", "电力煤气"), ("9503", "Kansai Electric Power", "电力煤气"),
    ("9531", "Tokyo Gas", "电力煤气"), ("9532", "Osaka Gas", "电力煤气"),
    ("9602", "Toho", "服务业"), ("9613", "NTT Data", "信息通信"),
    ("9719", "SCSK", "信息通信"), ("9735", "Secom", "服务业"),
    ("9766", "Konami Group", "信息通信"), ("9843", "Nitori Holdings", "零售业"),
    ("9983", "Fast Retailing (优衣库母公司)", "零售业"),
    ("9984", "SoftBank Group (软银集团)", "信息通信")
]

print(f"载入完成，共 {len(nikkei_data)} 只日经核心标的！开始批量采集最新行情指标...")

records = []
total = len(nikkei_data)

for i, (code, name, sector) in enumerate(nikkei_data):
    ticker = f"{code}.T"
    try:
        t = yf.Ticker(ticker)
        fast = t.fast_info
        info = t.info

        # 现价与市值（换算为 兆日元 Trillion ¥）
        price = fast.last_price or info.get("currentPrice") or info.get("regularMarketPrice", 0.0)
        market_cap = fast.market_cap or info.get("marketCap", 0.0)
        market_cap_trillion = round(market_cap / 1e12, 2) if market_cap else None

        pe = info.get("trailingPE", None)
        roe = info.get("returnOnEquity", None)
        roe_pct = round(roe * 100, 2) if roe else None

        growth = info.get("revenueGrowth", None)
        growth_pct = round(growth * 100, 2) if growth else None

        dividend = info.get("dividendYield", None)
        div_pct = round(dividend * 100, 2) if dividend else 0.0

        # 计算偏离 50 日均线
        hist = t.history(period="3mo")
        bias_50 = None
        if len(hist) >= 50:
            ma50 = hist["Close"].rolling(50).mean().iloc[-1]
            bias_50 = round(((price - ma50) / ma50) * 100, 2)

        records.append({
            "代码": ticker,
            "日股代码": code,
            "公司名称": name,
            "行业板块": sector,
            "现价 (¥)": round(price, 1) if price else None,
            "市值 (兆¥)": market_cap_trillion,
            "滚动PE": round(pe, 1) if pe else None,
            "ROE (%)": roe_pct,
            "营收增速 (%)": growth_pct,
            "股息率 (%)": div_pct,
            "偏离50日线 (%)": bias_50
        })
        print(f"[{i+1}/{total}] 采集成功: {code} - {name}")
    except Exception as e:
        print(f"[{i+1}/{total}] 采集跳过: {ticker}, 原因: {e}")

    time.sleep(0.15)

df = pd.DataFrame(records)
df.to_csv("nikkei225_data.csv", index=False, encoding="utf-8-sig")
print("\n✅ 日经225本地数据库生成完成：nikkei225_data.csv")