"""
Nifty 500 Screener — Flask Backend (Fixed)
===========================================
Run:
    pip install flask yfinance flask-cors pandas numpy
    python app.py
Then open screener.html in Chrome.
"""

from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
import os
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime
import threading, time, logging
from curl_cffi import requests as cffi_requests

# Shared session that impersonates a real browser's TLS fingerprint —
# bypasses Yahoo Finance's Cloudflare bot challenge that returns empty
# responses to plain requests from cloud/datacenter IPs.
YF_SESSION = cffi_requests.Session(impersonate="chrome")

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
log = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# ══════════════════════════════════════════════
# Universe
# ══════════════════════════════════════════════
UNIVERSE = [
    ("HDFCBANK","Banking"),("ICICIBANK","Banking"),("SBIN","Banking"),
    ("KOTAKBANK","Banking"),("AXISBANK","Banking"),("INDUSINDBK","Banking"),
    ("BANDHANBNK","Banking"),("FEDERALBNK","Banking"),("IDFCFIRSTB","Banking"),
    ("RBLBANK","Banking"),("PNB","Banking"),("CANBK","Banking"),
    ("BANKBARODA","Banking"),("UNIONBANK","Banking"),("INDIANB","Banking"),
    ("YESBANK","Banking"),("DCBBANK","Banking"),("AUBANK","Banking"),
    ("EQUITASBNK","Banking"),("UJJIVANSFB","Banking"),("IDBI","Banking"),
    ("MAHABANK","Banking"),("KARURVYSYA","Banking"),("CSBBANK","Banking"),
    ("TCS","IT"),("INFY","IT"),("WIPRO","IT"),("HCLTECH","IT"),
    ("TECHM","IT"),("MPHASIS","IT"),("LTIM","IT"),("PERSISTENT","IT"),
    ("COFORGE","IT"),("OFSS","IT"),("CYIENT","IT"),("KPITTECH","IT"),
    ("TATAELXSI","IT"),("LTTS","IT"),("NEWGEN","IT"),("HAPPSTMNDS","IT"),
    ("NAUKRI","IT"),("PAYTM","IT"),("RAILTEL","IT"),("TANLA","IT"),
    ("INTELLECT","IT"),("MASTEK","IT"),
    ("MARUTI","Auto"),("TATAMOTORS","Auto"),("M&M","Auto"),
    ("BAJAJ-AUTO","Auto"),("HEROMOTOCO","Auto"),("EICHERMOT","Auto"),
    ("ASHOKLEY","Auto"),("TVSMOTOR","Auto"),("MOTHERSON","Auto"),
    ("BOSCHLTD","Auto"),("BHARATFORG","Auto"),("EXIDEIND","Auto"),
    ("APOLLOTYRE","Auto"),("CEATLTD","Auto"),("MRF","Auto"),
    ("BALKRISIND","Auto"),("ENDURANCE","Auto"),("MINDAIND","Auto"),
    ("SUNPHARMA","Pharma"),("DRREDDY","Pharma"),("CIPLA","Pharma"),
    ("DIVISLAB","Pharma"),("AUROPHARMA","Pharma"),("BIOCON","Pharma"),
    ("ALKEM","Pharma"),("TORNTPHARM","Pharma"),("GLENMARK","Pharma"),
    ("IPCALAB","Pharma"),("LAURUSLABS","Pharma"),("GRANULES","Pharma"),
    ("AJANTPHARM","Pharma"),("ZYDUSLIFE","Pharma"),("APOLLOHOSP","Pharma"),
    ("FORTIS","Pharma"),("MAXHEALTH","Pharma"),("LALPATHLAB","Pharma"),
    ("METROPOLIS","Pharma"),("NATCOPHARM","Pharma"),("ERIS","Pharma"),
    ("HINDUNILVR","FMCG"),("ITC","FMCG"),("NESTLEIND","FMCG"),
    ("BRITANNIA","FMCG"),("DABUR","FMCG"),("MARICO","FMCG"),
    ("COLPAL","FMCG"),("GODREJCP","FMCG"),("EMAMILTD","FMCG"),
    ("VBL","FMCG"),("RADICO","FMCG"),("UBL","FMCG"),
    ("TATACONSUM","FMCG"),("BIKAJI","FMCG"),("MCDOWELL-N","FMCG"),
    ("RELIANCE","Oil & Gas"),("ONGC","Oil & Gas"),("IOC","Oil & Gas"),
    ("BPCL","Oil & Gas"),("HPCL","Oil & Gas"),("GAIL","Oil & Gas"),
    ("OIL","Oil & Gas"),("PETRONET","Oil & Gas"),("IGL","Oil & Gas"),
    ("MGL","Oil & Gas"),("GUJGASLTD","Oil & Gas"),("CASTROLIND","Oil & Gas"),
    ("TATASTEEL","Metals"),("JSWSTEEL","Metals"),("HINDALCO","Metals"),
    ("VEDL","Metals"),("SAIL","Metals"),("NMDC","Metals"),
    ("COALINDIA","Metals"),("NATIONALUM","Metals"),("HINDCOPPER","Metals"),
    ("MOIL","Metals"),("JINDALSAW","Metals"),("RATNAMANI","Metals"),("APLAPOLLO","Metals"),
    ("LT","Infra"),("NTPC","Infra"),("POWERGRID","Infra"),
    ("ADANIPORTS","Infra"),("ADANIENT","Infra"),("SIEMENS","Infra"),
    ("ABB","Infra"),("HAVELLS","Infra"),("BHEL","Infra"),
    ("HAL","Infra"),("BEL","Infra"),("THERMAX","Infra"),
    ("KEC","Infra"),("NBCC","Infra"),("RVNL","Infra"),
    ("CUMMINSIND","Infra"),("DELHIVERY","Infra"),("KALPATPOWR","Infra"),
    ("BAJFINANCE","NBFC"),("BAJAJFINSV","NBFC"),("HDFCAMC","NBFC"),
    ("SBILIFE","NBFC"),("HDFCLIFE","NBFC"),("ICICIGI","NBFC"),
    ("LICI","NBFC"),("MUTHOOTFIN","NBFC"),("MANAPPURAM","NBFC"),
    ("CHOLAFIN","NBFC"),("SHRIRAMFIN","NBFC"),("LICHSGFIN","NBFC"),
    ("RECLTD","NBFC"),("PFC","NBFC"),("IRFC","NBFC"),
    ("CANFINHOME","NBFC"),("CDSL","NBFC"),("MCX","NBFC"),("BSE","NBFC"),
    ("DLF","Realty"),("GODREJPROP","Realty"),("OBEROIRLTY","Realty"),
    ("PRESTIGE","Realty"),("PHOENIXLTD","Realty"),("BRIGADE","Realty"),
    ("SOBHA","Realty"),("LODHA","Realty"),("ANANTRAJ","Realty"),
    ("KOLTEPATIL","Realty"),("SUNTECK","Realty"),
    ("PIDILITIND","Chemicals"),("SRF","Chemicals"),("DEEPAKNTR","Chemicals"),
    ("NAVINFLUOR","Chemicals"),("ATUL","Chemicals"),("NOCIL","Chemicals"),
    ("FINEORG","Chemicals"),("TATACHEM","Chemicals"),("GNFC","Chemicals"),
    ("VINATI","Chemicals"),("ROSSARI","Chemicals"),("PCBL","Chemicals"),
    ("DCMSHRIRAM","Chemicals"),
    ("TITAN","Consumer"),("ASIANPAINT","Consumer"),("BERGEPAINT","Consumer"),
    ("PAGEIND","Consumer"),("BATAINDIA","Consumer"),("TRENT","Consumer"),
    ("VEDANT","Consumer"),("KALYANKJIL","Consumer"),("MANYAVAR","Consumer"),
    ("IRCTC","Consumer"),("ZOMATO","Consumer"),("NYKAA","Consumer"),
    ("WHIRLPOOL","Consumer"),("BLUESTARCO","Consumer"),("KANSAINER","Consumer"),
    ("TATAPOWER","Power"),("ADANIGREEN","Power"),("ADANIPOWER","Power"),
    ("CESC","Power"),("TORNTPOWER","Power"),("JSWENERGY","Power"),
    ("SJVN","Power"),("NHPC","Power"),("SUZLON","Power"),("INOXWIND","Power"),
    ("BHARTIARTL","Telecom"),("IDEA","Telecom"),("TATACOMM","Telecom"),
    ("HFCL","Telecom"),("INDIAMART","Telecom"),("JUSTDIAL","Telecom"),
    ("ZEEL","Media"),("PVRINOX","Media"),("SUNTV","Media"),
    ("SAREGAMA","Media"),("NETWORK18","Media"),

    # ── Smallcap ──
    # Smallcap Banking & Finance
    ("SURYODAY","Smallcap-Banking"),("ESAFSFB","Smallcap-Banking"),
    ("FINPIPE","Smallcap-Banking"),("CREDITACC","Smallcap-Banking"),
    ("SPANDANA","Smallcap-Banking"),("AROHAN","Smallcap-Banking"),
    ("AAVAS","Smallcap-Banking"),("APTUS","Smallcap-Banking"),
    ("HOMEFIRST","Smallcap-Banking"),("REPCO","Smallcap-Banking"),
    ("FUSION","Smallcap-Banking"),("SATIN","Smallcap-Banking"),

    # Smallcap IT & Tech
    ("BSOFT","Smallcap-IT"),("ROUTE","Smallcap-IT"),
    ("LATENTVIEW","Smallcap-IT"),("NUCLEUS","Smallcap-IT"),
    ("DATAMATICS","Smallcap-IT"),("SAKSOFT","Smallcap-IT"),
    ("NIITLTD","Smallcap-IT"),("XCHANGING","Smallcap-IT"),
    ("ZENSAR","Smallcap-IT"),("RATEGAIN","Smallcap-IT"),
    ("MAPMYINDIA","Smallcap-IT"),("ZAGGLE","Smallcap-IT"),
    ("INFIBEAM","Smallcap-IT"),("NETSOL","Smallcap-IT"),

    # Smallcap Pharma & Healthcare
    ("SUVEN","Smallcap-Pharma"),("WINDLAS","Smallcap-Pharma"),
    ("MARKSANS","Smallcap-Pharma"),("SOLARA","Smallcap-Pharma"),
    ("SEQUENT","Smallcap-Pharma"),("VIOVI","Smallcap-Pharma"),
    ("JBCHEPHARM","Smallcap-Pharma"),("GLAND","Smallcap-Pharma"),
    ("STRIDES","Smallcap-Pharma"),("SHILPAMED","Smallcap-Pharma"),
    ("IOLCP","Smallcap-Pharma"),("NEULANDLAB","Smallcap-Pharma"),
    ("PGHL","Smallcap-Pharma"),("MEDANTA","Smallcap-Pharma"),
    ("KRSNAA","Smallcap-Pharma"),("SUVENPHAR","Smallcap-Pharma"),

    # Smallcap Chemicals
    ("AARTI","Smallcap-Chemicals"),("CLEAN","Smallcap-Chemicals"),
    ("HOCL","Smallcap-Chemicals"),("BALAMINES","Smallcap-Chemicals"),
    ("ALKYLAMINE","Smallcap-Chemicals"),("DMCC","Smallcap-Chemicals"),
    ("JAYAGROGN","Smallcap-Chemicals"),("NEOGEN","Smallcap-Chemicals"),
    ("LXCHEM","Smallcap-Chemicals"),("NIACL","Smallcap-Chemicals"),
    ("TITAGARH","Smallcap-Chemicals"),
    ("IGPL","Smallcap-Chemicals"),("PAUSHAKLTD","Smallcap-Chemicals"),

    # Smallcap Auto & Auto Ancillaries
    ("SUBROS","Smallcap-Auto"),("SUPRAJIT","Smallcap-Auto"),
    ("GABRIEL","Smallcap-Auto"),("MINDA","Smallcap-Auto"),
    ("SUNDRM","Smallcap-Auto"),("SETCO","Smallcap-Auto"),
    ("JAYIND","Smallcap-Auto"),("SHARDAMOTR","Smallcap-Auto"),
    ("UCAL","Smallcap-Auto"),("STEELCAS","Smallcap-Auto"),
    ("FIEM","Smallcap-Auto"),("ALPA","Smallcap-Auto"),

    # Smallcap Consumer & Retail
    ("VMART","Smallcap-Consumer"),("SHOPERSTOP","Smallcap-Consumer"),
    ("INOXLEISUR","Smallcap-Consumer"),("RUSTOMJEE","Smallcap-Consumer"),
    ("SAPPHIRE","Smallcap-Consumer"),("TIPSINDLTD","Smallcap-Consumer"),
    ("BARBEQUE","Smallcap-Consumer"),("WESTLIFE","Smallcap-Consumer"),
    ("DEVYANI","Smallcap-Consumer"),("JUBLFOOD","Smallcap-Consumer"),
    ("EASEMYTRIP","Smallcap-Consumer"),("IXIGO","Smallcap-Consumer"),
    ("CARTRADE","Smallcap-Consumer"),

    # Smallcap Infra & Capital Goods
    ("AHLUCONT","Smallcap-Infra"),("HLE","Smallcap-Infra"),
    ("ISGEC","Smallcap-Infra"),("TEXMOPIPES","Smallcap-Infra"),
    ("DBCORP","Smallcap-Infra"),("HGINFRA","Smallcap-Infra"),
    ("IRB","Smallcap-Infra"),("PNCINFRA","Smallcap-Infra"),
    ("RITES","Smallcap-Infra"),("IRCON","Smallcap-Infra"),
    ("RAILVIKAS","Smallcap-Infra"),("WABAG","Smallcap-Infra"),
    ("ELECON","Smallcap-Infra"),("JYOTISTRUC","Smallcap-Infra"),
    ("GREENPANEL","Smallcap-Infra"),("CENTURYPLY","Smallcap-Infra"),

    # Smallcap Metals & Mining
    ("TINPLATE","Smallcap-Metals"),("WELCORP","Smallcap-Metals"),
    ("MAHASTEEL","Smallcap-Metals"),("SSWL","Smallcap-Metals"),
    ("MANAKSIA","Smallcap-Metals"),("PRAKASHSTL","Smallcap-Metals"),
    ("JSLHISAR","Smallcap-Metals"),("MAITHANALL","Smallcap-Metals"),

    # Smallcap Textiles & Apparel
    ("NITIN","Smallcap-Textiles"),("RUPA","Smallcap-Textiles"),
    ("RAYMOND","Smallcap-Textiles"),("GOKEX","Smallcap-Textiles"),
    ("KITEX","Smallcap-Textiles"),
    ("SPORTKING","Smallcap-Textiles"),("NIRAJ","Smallcap-Textiles"),
    ("GRASIM","Smallcap-Textiles"),("VARDHMAN","Smallcap-Textiles"),

    # Smallcap Realty
    ("MAHLIFE","Smallcap-Realty"),("ARVSMART","Smallcap-Realty"),
    ("ELDEHSG","Smallcap-Realty"),("TARC","Smallcap-Realty"),
    ("WPIL","Smallcap-Realty"),("PENINLAND","Smallcap-Realty"),
    ("NESCO","Smallcap-Realty"),("MAHINDCIE","Smallcap-Realty"),

    # Smallcap Power & Renewables
    ("KENNAMETAL","Smallcap-Power"),("AMRPL","Smallcap-Power"),
    ("WEBSOL","Smallcap-Power"),("BOROSIL","Smallcap-Power"),
    ("PREMIER","Smallcap-Power"),
    ("GPIL","Smallcap-Power"),("ORIENTELEC","Smallcap-Power"),
    ("EIHOTEL","Smallcap-Power"),

    # Smallcap FMCG & Agri
    ("JUBLPHARMA","Smallcap-FMCG"),("ANNAPURNA","Smallcap-FMCG"),
    ("BAJAJCON","Smallcap-FMCG"),("TASTYBIT","Smallcap-FMCG"),
    ("VENKEYS","Smallcap-FMCG"),("AVANTIFEED","Smallcap-FMCG"),
    ("WATERBASE","Smallcap-FMCG"),("SATIA","Smallcap-FMCG"),
    ("GFLLIMITED","Smallcap-FMCG"),("KRITI","Smallcap-FMCG"),

    # ── NIFTY Total Market additions (broad-market top ~750 by mcap) ──
    ("MTARTECH","TotalMkt-Other"),("AEGISLOG","TotalMkt-Other"),("NETWEB","TotalMkt-Other"),("IFCI","TotalMkt-Other"),
    ("DATAPATTNS","TotalMkt-Other"),("INDIGO","TotalMkt-Other"),("HSCL","TotalMkt-Other"),("AIIL","TotalMkt-Other"),
    ("APOLLO","TotalMkt-Other"),("GROWW","TotalMkt-Other"),("OLAELEC","TotalMkt-Other"),("TMCV","TotalMkt-Other"),
    ("TEJASNET","TotalMkt-Other"),("PARAS","TotalMkt-Other"),("MMTC","TotalMkt-Other"),("ETERNAL","TotalMkt-Other"),
    ("HINDPETRO","TotalMkt-Other"),("APARINDS","TotalMkt-Other"),("POWERINDIA","TotalMkt-Other"),("AMBER","TotalMkt-Other"),
    ("CUPID","TotalMkt-Other"),("DIXON","TotalMkt-Other"),("NLCINDIA","TotalMkt-Other"),("JBMA","TotalMkt-Other"),
    ("SWIGGY","TotalMkt-Other"),("TMPV","TotalMkt-Other"),("JIOFIN","TotalMkt-Other"),("ATHERENERG","TotalMkt-Other"),
    ("PGEL","TotalMkt-Other"),("CAPILLARY","TotalMkt-Other"),("MOTILALOFS","TotalMkt-Other"),("PINELABS","TotalMkt-Other"),
    ("CGPOWER","TotalMkt-Other"),("TTML","TotalMkt-Other"),("WOCKPHARMA","TotalMkt-Other"),("ANGELONE","TotalMkt-Other"),
    ("ENRIN","TotalMkt-Other"),("ADANIENSOL","TotalMkt-Other"),("HYUNDAI","TotalMkt-Other"),("ATGL","TotalMkt-Other"),
    ("ICICIAMC","TotalMkt-Other"),("SAMMAANCAP","TotalMkt-Other"),("GVT&D","TotalMkt-Other"),("ULTRACEMCO","TotalMkt-Other"),
    ("GRSE","TotalMkt-Other"),("PNBHOUSING","TotalMkt-Other"),("GMRAIRPORT","TotalMkt-Other"),("LTF","TotalMkt-Other"),
    ("KAYNES","TotalMkt-Other"),("MEESHO","TotalMkt-Other"),("INDUSTOWER","TotalMkt-Other"),("JYOTICNC","TotalMkt-Other"),
    ("SOLARINDS","TotalMkt-Other"),("INDHOTEL","TotalMkt-Other"),("FORCEMOT","TotalMkt-Other"),("LENSKART","TotalMkt-Other"),
    ("EMMVEE","TotalMkt-Other"),("WAAREEENER","TotalMkt-Other"),("SPARC","TotalMkt-Other"),("SOUTHBANK","TotalMkt-Other"),
    ("HINDZINC","TotalMkt-Other"),("JAINREC","TotalMkt-Other"),("ZENTEC","TotalMkt-Other"),("POWERMECH","TotalMkt-Other"),
    ("POLYCAB","TotalMkt-Other"),("UNOMINDA","TotalMkt-Other"),("DMART","TotalMkt-Other"),("JPPOWER","TotalMkt-Other"),
    ("LUPIN","TotalMkt-Other"),("POLICYBZR","TotalMkt-Other"),("CUB","TotalMkt-Other"),("LTM","TotalMkt-Other"),
    ("JSWINFRA","TotalMkt-Other"),("MAZDOCK","TotalMkt-Other"),("BANKINDIA","TotalMkt-Other"),("INOXINDIA","TotalMkt-Other"),
    ("STLTECH","TotalMkt-Other"),("ABDL","TotalMkt-Other"),("ASTRAL","TotalMkt-Other"),("MRPL","TotalMkt-Other"),
    ("CROMPTON","TotalMkt-Other"),("HCC","TotalMkt-Other"),("TDPOWERSYS","TotalMkt-Other"),("AMBUJACEM","TotalMkt-Other"),
    ("KEI","TotalMkt-Other"),("ACUTAAS","TotalMkt-Other"),("PREMIERENE","TotalMkt-Other"),("COCHINSHIP","TotalMkt-Other"),
    ("PIIND","TotalMkt-Other"),("GMDCLTD","TotalMkt-Other"),("JSWCEMENT","TotalMkt-Other"),("IIFL","TotalMkt-Other"),
    ("DEEPAKFERT","TotalMkt-Other"),("TATATECH","TotalMkt-Other"),("CHENNPETRO","TotalMkt-Other"),("SCI","TotalMkt-Other"),
    ("ABCAPITAL","TotalMkt-Other"),("GODFRYPHLP","TotalMkt-Other"),("SYRMA","TotalMkt-Other"),("CHOICEIN","TotalMkt-Other"),
    ("AZAD","TotalMkt-Other"),("PATANJALI","TotalMkt-Other"),("MSUMI","TotalMkt-Other"),("RRKABEL","TotalMkt-Other"),
    ("LLOYDSME","TotalMkt-Other"),("PRIVISCL","TotalMkt-Other"),("DALBHARAT","TotalMkt-Other"),("ASTERDM","TotalMkt-Other"),
    ("RPOWER","TotalMkt-Other"),("NAM-INDIA","TotalMkt-Other"),("TATAINVEST","TotalMkt-Other"),("OLECTRA","TotalMkt-Other"),
    ("DIACABS","TotalMkt-Other"),("AEGISVOPAK","TotalMkt-Other"),("ABSLAMC","TotalMkt-Other"),("MIDHANI","TotalMkt-Other"),
    ("RUBICON","TotalMkt-Other"),("ENGINERSIN","TotalMkt-Other"),("CEMPRO","TotalMkt-Other"),("SHYAMMETL","TotalMkt-Other"),
    ("UPL","TotalMkt-Other"),("KTKBANK","TotalMkt-Other"),("MFSL","TotalMkt-Other"),("ASTRAMICRO","TotalMkt-Other"),
    ("TIINDIA","TotalMkt-Other"),("POONAWALLA","TotalMkt-Other"),("CGCL","TotalMkt-Other"),("PIRAMALFIN","TotalMkt-Other"),
    ("SHAILY","TotalMkt-Other"),("CONCOR","TotalMkt-Other"),("SWSOLAR","TotalMkt-Other"),("TIMETECHNO","TotalMkt-Other"),
    ("AVALON","TotalMkt-Other"),("INOXGREEN","TotalMkt-Other"),("HUDCO","TotalMkt-Other"),("RAIN","TotalMkt-Other"),
    ("360ONE","TotalMkt-Other"),("GLAXO","TotalMkt-Other"),("BDL","TotalMkt-Other"),("NUVAMA","TotalMkt-Other"),
    ("HONASA","TotalMkt-Other"),("MEDPLUS","TotalMkt-Other"),("AWL","TotalMkt-Other"),("GESHIP","TotalMkt-Other"),
    ("BLUEJET","TotalMkt-Other"),("VOLTAS","TotalMkt-Other"),("SUPRIYA","TotalMkt-Other"),("CPPLUS","TotalMkt-Other"),
    ("BORORENEW","TotalMkt-Other"),("THANGAMAYL","TotalMkt-Other"),("PWL","TotalMkt-Other"),("MANKIND","TotalMkt-Other"),
    ("SANSERA","TotalMkt-Other"),("HBLENGINE","TotalMkt-Other"),("CAMS","TotalMkt-Other"),("BELRISE","TotalMkt-Other"),
    ("LGEINDIA","TotalMkt-Other"),("ANURAS","TotalMkt-Other"),("JAYNECOIND","TotalMkt-Other"),("M&MFIN","TotalMkt-Other"),
    ("SAGILITY","TotalMkt-Other"),("ACE","TotalMkt-Other"),("UNITDSPR","TotalMkt-Other"),("JKTYRE","TotalMkt-Other"),
    ("VIYASH","TotalMkt-Other"),("J&KBANK","TotalMkt-Other"),("ONESOURCE","TotalMkt-Other"),("BBOX","TotalMkt-Other"),
    ("KFINTECH","TotalMkt-Other"),("VIKRAMSOLR","TotalMkt-Other"),("VMM","TotalMkt-Other"),("STAR","TotalMkt-Other"),
    ("CRAFTSMAN","TotalMkt-Other"),("CAPLIPOINT","TotalMkt-Other"),("COROMANDEL","TotalMkt-Other"),("IREDA","TotalMkt-Other"),
    ("AKUMS","TotalMkt-Other"),("MSTCLTD","TotalMkt-Other"),("BANCOINDIA","TotalMkt-Other"),("SHAKTIPUMP","TotalMkt-Other"),
    ("JINDALSTEL","TotalMkt-Other"),("INDIASHLTR","TotalMkt-Other"),("REDINGTON","TotalMkt-Other"),("NH","TotalMkt-Other"),
    ("AEQUS","TotalMkt-Other"),("LEMONTREE","TotalMkt-Other"),("LLOYDSENGG","TotalMkt-Other"),("CHOLAHLDNG","TotalMkt-Other"),
    ("JMFINANCIL","TotalMkt-Other"),("CONCORDBIO","TotalMkt-Other"),("TATACAP","TotalMkt-Other"),("FIVESTAR","TotalMkt-Other"),
    ("SHREECEM","TotalMkt-Other"),("CCL","TotalMkt-Other"),("HEXT","TotalMkt-Other"),("ACMESOLAR","TotalMkt-Other"),
    ("HEG","TotalMkt-Other"),("RKFORGE","TotalMkt-Other"),("AFFLE","TotalMkt-Other"),("IEX","TotalMkt-Other"),
    ("SONACOMS","TotalMkt-Other"),("TRITURBINE","TotalMkt-Other"),("KIRLOSENG","TotalMkt-Other"),("KPRMILL","TotalMkt-Other"),
    ("GRAPHITE","TotalMkt-Other"),("ANTHEM","TotalMkt-Other"),("TARIL","TotalMkt-Other"),("VOLTAMP","TotalMkt-Other"),
    ("PPLPHARMA","TotalMkt-Other"),("ICICIPRULI","TotalMkt-Other"),("SAILIFE","TotalMkt-Other"),("CHALET","TotalMkt-Other"),
    ("SKIPPER","TotalMkt-Other"),("JSLL","TotalMkt-Other"),("SARDAEN","TotalMkt-Other"),("JKCEMENT","TotalMkt-Other"),
    ("SURYAROSNI","TotalMkt-Other"),("SUPREMEIND","TotalMkt-Other"),("DOMS","TotalMkt-Other"),("PRAJIND","TotalMkt-Other"),
    ("STARCEMENT","TotalMkt-Other"),("KIMS","TotalMkt-Other"),("NCC","TotalMkt-Other"),("CARBORUNIV","TotalMkt-Other"),
    ("PRICOLLTD","TotalMkt-Other"),("TENNIND","TotalMkt-Other"),("JSFB","TotalMkt-Other"),("JSL","TotalMkt-Other"),
    ("KRBL","TotalMkt-Other"),("VIJAYA","TotalMkt-Other"),("SHARDACROP","TotalMkt-Other"),("POLYMED","TotalMkt-Other"),
    ("ARE&M","TotalMkt-Other"),("V2RETAIL","TotalMkt-Other"),("IIFLCAPS","TotalMkt-Other"),("IFBIND","TotalMkt-Other"),
    ("CENTRALBK","TotalMkt-Other"),("NTPCGREEN","TotalMkt-Other"),("ITCHOTELS","TotalMkt-Other"),("GRWRHITECH","TotalMkt-Other"),
    ("BLS","TotalMkt-Other"),("SCHNEIDER","TotalMkt-Other"),("SIGNATURE","TotalMkt-Other"),("TRANSRAILL","TotalMkt-Other"),
    ("FINCABLES","TotalMkt-Other"),("ABREL","TotalMkt-Other"),("STARHEALTH","TotalMkt-Other"),("SBICARD","TotalMkt-Other"),
    ("DBREALTY","TotalMkt-Other"),("THOMASCOOK","TotalMkt-Other"),("HDBFS","TotalMkt-Other"),("SMLMAH","TotalMkt-Other"),
    ("SKYGOLD","TotalMkt-Other"),("ANANDRATHI","TotalMkt-Other"),("QPOWER","TotalMkt-Other"),("NSLNISP","TotalMkt-Other"),
    ("SHRIPISTON","TotalMkt-Other"),("JAMNAAUTO","TotalMkt-Other"),("BAJAJHLDNG","TotalMkt-Other"),("PARADEEP","TotalMkt-Other"),
    ("SYNGENE","TotalMkt-Other"),("URBANCO","TotalMkt-Other"),("TBOTEK","TotalMkt-Other"),("EDELWEISS","TotalMkt-Other"),
    ("SUNDARMFIN","TotalMkt-Other"),("RAMCOCEM","TotalMkt-Other"),("ACC","TotalMkt-Other"),("BAJAJHFL","TotalMkt-Other"),
    ("PCJEWELLER","TotalMkt-Other"),("SONATSOFTW","TotalMkt-Other"),("SANDUMA","TotalMkt-Other"),("GRAVITA","TotalMkt-Other"),
    ("CHAMBLFERT","TotalMkt-Other"),("ABBOTINDIA","TotalMkt-Other"),("AADHARHFC","TotalMkt-Other"),("ALIVUS","TotalMkt-Other"),
    ("BHARTIHEXA","TotalMkt-Other"),("AETHER","TotalMkt-Other"),("AXISCADES","TotalMkt-Other"),("PARKHOSPS","TotalMkt-Other"),
    ("KNRCON","TotalMkt-Other"),("SCHAEFFLER","TotalMkt-Other"),("KIRLPNU","TotalMkt-Other"),("AFCONS","TotalMkt-Other"),
    ("ARVIND","TotalMkt-Other"),("KPIGREEN","TotalMkt-Other"),("PTC","TotalMkt-Other"),("BALUFORGE","TotalMkt-Other"),
    ("OSWALPUMPS","TotalMkt-Other"),("ITI","TotalMkt-Other"),("CERA","TotalMkt-Other"),("FACT","TotalMkt-Other"),
    ("NAZARA","TotalMkt-Other"),("ASHAPURMIN","TotalMkt-Other"),("ATLANTAELE","TotalMkt-Other"),("TECHNOE","TotalMkt-Other"),
    ("SUDEEPPHRM","TotalMkt-Other"),("LTFOODS","TotalMkt-Other"),("FSL","TotalMkt-Other"),("ELGIEQUIP","TotalMkt-Other"),
    ("AIAENG","TotalMkt-Other"),("EIDPARRY","TotalMkt-Other"),("AARTIIND","TotalMkt-Other"),("WEBELSOLAR","TotalMkt-Other"),
    ("MANORAMA","TotalMkt-Other"),("FLUOROCHEM","TotalMkt-Other"),("BEML","TotalMkt-Other"),("BALRAMCHIN","TotalMkt-Other"),
    ("ZENSARTECH","TotalMkt-Other"),("GILLETTE","TotalMkt-Other"),("TVSSCS","TotalMkt-Other"),("GHCL","TotalMkt-Other"),
    ("JWL","TotalMkt-Other"),("HONAUT","TotalMkt-Other"),("BLACKBUCK","TotalMkt-Other"),("GREAVESCOT","TotalMkt-Other"),
    ("EMCURE","TotalMkt-Other"),("TRAVELFOOD","TotalMkt-Other"),("GODREJIND","TotalMkt-Other"),("YATHARTH","TotalMkt-Other"),
    ("ICIL","TotalMkt-Other"),("RBA","TotalMkt-Other"),("TEXRAIL","TotalMkt-Other"),("KSB","TotalMkt-Other"),
    ("REFEX","TotalMkt-Other"),("SFL","TotalMkt-Other"),("KRN","TotalMkt-Other"),("LUMAXTECH","TotalMkt-Other"),
    ("PTCIL","TotalMkt-Other"),("LLOYDSENT","TotalMkt-Other"),("NAVA","TotalMkt-Other"),("RAYMONDLSL","TotalMkt-Other"),
    ("VIPIND","TotalMkt-Other"),("EPL","TotalMkt-Other"),("KPIL","TotalMkt-Other"),("CRISIL","TotalMkt-Other"),
    ("BLUESTONE","TotalMkt-Other"),("THYROCARE","TotalMkt-Other"),("LINDEINDIA","TotalMkt-Other"),("MINDACORP","TotalMkt-Other"),
    ("NUVOCO","TotalMkt-Other"),("GPPL","TotalMkt-Other"),("CMSINFO","TotalMkt-Other"),("AVL","TotalMkt-Other"),
    ("ECLERX","TotalMkt-Other"),("RELIGARE","TotalMkt-Other"),("TMB","TotalMkt-Other"),("EMIL","TotalMkt-Other"),
    ("RCF","TotalMkt-Other"),("WAAREERTL","TotalMkt-Other"),("ESCORTS","TotalMkt-Other"),("SWANCORP","TotalMkt-Other"),
    ("AURIONPRO","TotalMkt-Other"),("UCOBANK","TotalMkt-Other"),("COHANCE","TotalMkt-Other"),("MAHSCOOTER","TotalMkt-Other"),
    ("JSWDULUX","TotalMkt-Other"),("TI","TotalMkt-Other"),("TIMKEN","TotalMkt-Other"),("ZFCVINDIA","TotalMkt-Other"),
    ("IMFA","TotalMkt-Other"),("IOB","TotalMkt-Other"),("VTL","TotalMkt-Other"),("ASHOKA","TotalMkt-Other"),
    ("FIRSTCRY","TotalMkt-Other"),("IKS","TotalMkt-Other"),("GMRP&UI","TotalMkt-Other"),("TIPSMUSIC","TotalMkt-Other"),
    ("TRIVENI","TotalMkt-Other"),("PNGJL","TotalMkt-Other"),("WELENT","TotalMkt-Other"),("THELEELA","TotalMkt-Other"),
    ("DYNAMATECH","TotalMkt-Other"),("IONEXCHANG","TotalMkt-Other"),("EIEL","TotalMkt-Other"),("RENUKA","TotalMkt-Other"),
    ("KIRLOSBROS","TotalMkt-Other"),("WELSPUNLIV","TotalMkt-Other"),("ELECTCAST","TotalMkt-Other"),("ABFRL","TotalMkt-Other"),
    ("INDIGOPNTS","TotalMkt-Other"),("WEWORK","TotalMkt-Other"),("QUESS","TotalMkt-Other"),("JUBLINGREA","TotalMkt-Other"),
    ("RTNPOWER","TotalMkt-Other"),("BLUEDART","TotalMkt-Other"),("SENCO","TotalMkt-Other"),("FEDFINA","TotalMkt-Other"),
    ("EMBDL","TotalMkt-Other"),("TEGA","TotalMkt-Other"),("FIEMIND","TotalMkt-Other"),("SAMHI","TotalMkt-Other"),
    ("STYL","TotalMkt-Other"),("ELLEN","TotalMkt-Other"),("JYOTHYLAB","TotalMkt-Other"),("SAFARI","TotalMkt-Other"),
    ("HERITGFOOD","TotalMkt-Other"),("AWFIS","TotalMkt-Other"),("RAINBOW","TotalMkt-Other"),("CIEINDIA","TotalMkt-Other"),
    ("BECTORFOOD","TotalMkt-Other"),("NFL","TotalMkt-Other"),("JKLAKSHMI","TotalMkt-Other"),("USHAMART","TotalMkt-Other"),
    ("WAKEFIT","TotalMkt-Other"),("SBFC","TotalMkt-Other"),("SHAREINDIA","TotalMkt-Other"),("CCAVENUE","TotalMkt-Other"),
    ("AARTIPHARM","TotalMkt-Other"),("PGIL","TotalMkt-Other"),("GODIGIT","TotalMkt-Other"),("PRUDENT","TotalMkt-Other"),
    ("ACI","TotalMkt-Other"),("HCG","TotalMkt-Other"),("TRIDENT","TotalMkt-Other"),("INDGN","TotalMkt-Other"),
    ("GALLANTT","TotalMkt-Other"),("ALOKINDS","TotalMkt-Other"),("GICRE","TotalMkt-Other"),("KAJARIACER","TotalMkt-Other"),
    ("CRAMC","TotalMkt-Other"),("SUDARSCHEM","TotalMkt-Other"),("GOKULAGRO","TotalMkt-Other"),("CRIZAC","TotalMkt-Other"),
    ("GAEL","TotalMkt-Other"),("VAIBHAVGBL","TotalMkt-Other"),("IGIL","TotalMkt-Other"),("BAJAJELEC","TotalMkt-Other"),
    ("PFIZER","TotalMkt-Other"),("UTIAMC","TotalMkt-Other"),("ZYDUSWELL","TotalMkt-Other"),("GSFC","TotalMkt-Other"),
    ("INDIAGLYCO","TotalMkt-Other"),("REDTAPE","TotalMkt-Other"),("ANUP","TotalMkt-Other"),("NIVABUPA","TotalMkt-Other"),
    ("SAATVIKGL","TotalMkt-Other"),("GMMPFAUDLR","TotalMkt-Other"),("INDIACEM","TotalMkt-Other"),("APLLTD","TotalMkt-Other"),
    ("SPLPETRO","TotalMkt-Other"),("ENTERO","TotalMkt-Other"),("SUMICHEM","TotalMkt-Other"),("JKPAPER","TotalMkt-Other"),
    ("RELAXO","TotalMkt-Other"),("ASKAUTOLTD","TotalMkt-Other"),("RALLIS","TotalMkt-Other"),("HEMIPROP","TotalMkt-Other"),
    ("AARTIDRUGS","TotalMkt-Other"),("SKFINDUS","TotalMkt-Other"),("CAMPUS","TotalMkt-Other"),("RTNINDIA","TotalMkt-Other"),
    ("MAHSEAMLES","TotalMkt-Other"),("CELLO","TotalMkt-Other"),("EUREKAFORB","TotalMkt-Other"),("BBTC","TotalMkt-Other"),
    ("PRSMJOHNSN","TotalMkt-Other"),("STYRENIX","TotalMkt-Other"),("BAYERCROP","TotalMkt-Other"),("RHIM","TotalMkt-Other"),
    ("LOTUSDEV","TotalMkt-Other"),("CANHLIFE","TotalMkt-Other"),("PFOCUS","TotalMkt-Other"),("UTLSOLAR","TotalMkt-Other"),
    ("JAIBALAJI","TotalMkt-Other"),("GODREJAGRO","TotalMkt-Other"),("OPTIEMUS","TotalMkt-Other"),("PICCADIL","TotalMkt-Other"),
    ("3MINDIA","TotalMkt-Other"),("ORIENTCEM","TotalMkt-Other"),("ARVINDFASN","TotalMkt-Other"),("DBL","TotalMkt-Other"),
    ("ABLBL","TotalMkt-Other"),("ASAHIINDIA","TotalMkt-Other"),("KSCL","TotalMkt-Other"),("VGUARD","TotalMkt-Other"),
    ("VARROC","TotalMkt-Other"),("BIRLACORPN","TotalMkt-Other"),("ADVENZYMES","TotalMkt-Other"),("AGARWALEYE","TotalMkt-Other"),
    ("SKFINDIA","TotalMkt-Other"),("TSFINV","TotalMkt-Other"),("PURVA","TotalMkt-Other"),("SANOFICONR","TotalMkt-Other"),
    ("ORKLAINDIA","TotalMkt-Other"),("CORONA","TotalMkt-Other"),("ETHOSLTD","TotalMkt-Other"),("JLHL","TotalMkt-Other"),
    ("SMARTWORKS","TotalMkt-Other"),
]

INDICES_LIST = [
    ("^NSEI","NIFTY 50"),("^NSEBANK","BANKNIFTY"),
    ("^CNXIT","NIFTY IT"),("^NSMIDCP","MIDCAP 50"),
    ("^CNXSC","SMALLCAP 100"),
]

# ══════════════════════════════════════════════
# Cache — single source of truth
# ══════════════════════════════════════════════
cache = {
    "cpr":      [],   # CPR scanner results
    "brk":      [],   # Breakout scanner results
    "dbl":      [],   # Double Bottom scanner results
    "bof":      [],   # Breakout Finder (BF) results
    "indices":  [],   # Index ticker data
    "nifty_ret":{"1m":0,"3m":0},
    "status":   "idle",   # idle | scanning | done | error
    "progress": 0,
    "message":  "",
    "total":    len(UNIVERSE),
    "done":     0,
    "ok":       0,
    "failed":   0,
    "last_scan":  None,
    "last_quote": None,
}
lock = threading.Lock()

# ══════════════════════════════════════════════
# Indicator helpers
# ══════════════════════════════════════════════
def ema(s, n): return s.ewm(span=n, adjust=False).mean()

def rsi(close, n=14):
    d = close.diff()
    g = d.clip(lower=0).ewm(alpha=1/n, adjust=False).mean()
    l = (-d.clip(upper=0)).ewm(alpha=1/n, adjust=False).mean()
    return (100 - 100/(1 + g/l.replace(0,np.nan))).fillna(50)

def macd(close, f=12, s=26, sig=9):
    ml = ema(close,f) - ema(close,s)
    sl = ema(ml, sig)
    return ml, sl, ml-sl

def bollinger(close, n=20, k=2):
    mid = close.rolling(n).mean()
    std = close.rolling(n).std()
    bw  = ((k*2*std)/mid).fillna(0)
    return mid+k*std, mid, mid-k*std, bw

def calc_atr(high, low, close, n=14):
    tr = pd.concat([high-low,
                    (high-close.shift()).abs(),
                    (low-close.shift()).abs()], axis=1).max(axis=1)
    return tr.ewm(span=n, adjust=False).mean()

def calc_adx(high, low, close, n=14):
    atr = calc_atr(high, low, close, n)
    up, dn = high.diff(), -low.diff()
    pdm = up.where((up>dn)&(up>0), 0)
    ndm = dn.where((dn>up)&(dn>0), 0)
    pdi = 100*pdm.ewm(span=n,adjust=False).mean()/atr.replace(0,np.nan)
    ndi = 100*ndm.ewm(span=n,adjust=False).mean()/atr.replace(0,np.nan)
    dx  = (100*(pdi-ndi).abs()/(pdi+ndi).replace(0,np.nan)).fillna(0)
    return dx.ewm(span=n,adjust=False).mean(), pdi, ndi

def calc_supertrend(high, low, close, n=10, m=3):
    atr  = calc_atr(high, low, close, n)
    hl2  = (high+low)/2
    ub   = hl2 + m*atr
    lb   = hl2 - m*atr
    fub  = ub.copy(); flb = lb.copy()
    st   = pd.Series(np.nan, index=close.index)
    dire = pd.Series(1, index=close.index)
    for i in range(1, len(close)):
        fub.iloc[i] = ub.iloc[i] if ub.iloc[i]<fub.iloc[i-1] or close.iloc[i-1]>fub.iloc[i-1] else fub.iloc[i-1]
        flb.iloc[i] = lb.iloc[i] if lb.iloc[i]>flb.iloc[i-1] or close.iloc[i-1]<flb.iloc[i-1] else flb.iloc[i-1]
        if close.iloc[i] > fub.iloc[i-1]:   dire.iloc[i] = 1
        elif close.iloc[i] < flb.iloc[i-1]: dire.iloc[i] = -1
        else:                                dire.iloc[i] = dire.iloc[i-1]
        st.iloc[i] = flb.iloc[i] if dire.iloc[i]==1 else fub.iloc[i]
    return st, dire

def hh_hl(close, lb=10):
    if len(close)<lb*2: return False
    h = len(close)//2
    old = close.iloc[-lb*2:-lb]; new = close.iloc[-lb:]
    return float(new.max())>float(old.max()) and float(new.min())>float(old.min())

# ══════════════════════════════════════════════
# ══════════════════════════════════════════════
# Double Bottom Detection (Weekly timeframe)
# ══════════════════════════════════════════════
def detect_double_bottom(sym, sec, df_w):
    """
    Detects a double bottom pattern on weekly OHLC data.
    Rules:
      1. Find two troughs (local lows) within the last 52 weeks.
      2. Troughs must be separated by at least 4 weeks and at most 40 weeks.
      3. Second trough within ±5% of first trough (similar lows).
      4. A peak (neckline) between the two troughs must be at least 5% above troughs.
      5. Current price must be above or approaching the neckline (within 3% below).
      6. Volume on second trough week >= average volume (accumulation signal).
      7. RSI on weekly not overbought (<= 65).
    Returns a dict row or None.
    """
    if df_w is None or len(df_w) < 20:
        return None

    df_w   = df_w.copy().sort_index(ascending=True)
    close  = df_w["Close"]
    low_w  = df_w["Low"]
    high_w = df_w["High"]
    vol_w  = df_w["Volume"]
    n      = len(df_w)

    cmp       = float(close.iloc[-1])
    prev_c    = float(close.iloc[-2])
    day_chg   = (cmp - prev_c) / prev_c * 100 if prev_c else 0

    lows  = low_w.values
    highs = high_w.values
    vols  = vol_w.values
    closes= close.values

    # Find local trough: a bar lower than the 2 bars on each side
    def is_trough(i, window=2):
        left  = lows[max(0,i-window):i]
        right = lows[i+1:min(n,i+window+1)]
        return len(left)>0 and len(right)>0 and lows[i] <= min(left) and lows[i] <= min(right)

    troughs = [i for i in range(2, n-2) if is_trough(i)]

    best = None
    best_score = 0

    for ti in range(len(troughs)-1):
        t1 = troughs[ti]
        for tj in range(ti+1, len(troughs)):
            t2 = troughs[tj]
            gap = t2 - t1

            # Gap between troughs: 4–40 weeks
            if gap < 4 or gap > 40:
                continue

            low1 = lows[t1]
            low2 = lows[t2]

            # Both troughs within ±5% of each other
            if abs(low1 - low2) / max(low1, 0.01) > 0.05:
                continue

            # Find neckline peak between the two troughs
            peak_idx = int(np.argmax(highs[t1:t2+1])) + t1
            neckline = float(highs[peak_idx])

            # Neckline must be at least 5% above the troughs
            avg_trough = (low1 + low2) / 2
            if (neckline - avg_trough) / avg_trough < 0.05:
                continue

            # Current price: at or above neckline, OR approaching (within 3% below)
            neck_pct = (cmp - neckline) / neckline * 100
            if neck_pct < -3.0:
                continue

            # Volume check: vol at t2 >= 80% of 20-week avg
            vol_avg = float(np.mean(vols[max(0,t2-20):t2])) if t2 >= 2 else float(np.mean(vols))
            vol_ratio = vols[t2] / vol_avg if vol_avg > 0 else 1.0

            # Weekly RSI
            rsi_w = float(rsi(close, 14).iloc[-1])
            if rsi_w > 65:
                continue

            # Depth of pattern (% drop from neckline to trough)
            depth_pct = (neckline - avg_trough) / neckline * 100

            # Score: deeper pattern + volume + price near neckline = better
            score = 0
            score += min(depth_pct * 2, 30)          # pattern depth
            score += min(vol_ratio * 10, 20)          # volume confirmation
            score += 15 if neck_pct >= 0 else 10      # breakout vs approaching
            score += 10 if gap >= 8 else 5            # longer base = stronger
            score += 5 if rsi_w >= 45 else 0          # RSI momentum

            if score > best_score:
                best_score = score
                # Project target = neckline + depth
                target = neckline + (neckline - avg_trough)
                sl     = avg_trough * 0.98            # just below both troughs
                upside = (target - cmp) / cmp * 100 if cmp > 0 else 0

                best = {
                    "symbol":      sym,
                    "sector":      sec,
                    "cmp":         round(cmp, 2),
                    "dayChg":      round(day_chg, 2),
                    "trough1":     round(float(low1), 2),
                    "trough2":     round(float(low2), 2),
                    "neckline":    round(neckline, 2),
                    "neckPct":     round(neck_pct, 1),   # % above/below neckline
                    "target":      round(float(target), 2),
                    "sl":          round(float(sl), 2),
                    "upside":      round(upside, 1),
                    "depthPct":    round(depth_pct, 1),
                    "gapWeeks":    int(gap),
                    "volRatio":    round(float(vol_ratio), 2),
                    "rsiWeekly":   round(rsi_w, 1),
                    "score":       round(min(score, 100), 1),
                    "status":      "Breakout" if neck_pct >= 0 else "Approaching Neckline",
                }

    return best


# ══════════════════════════════════════════════
# Breakout Finder (port of LonesomeTheBlue's "BF" Pine Script)
# Detects fresh breakouts/breakdowns from multi-tested
# horizontal resistance/support zones on the LATEST candle.
# ══════════════════════════════════════════════
def detect_breakout_finder(sym, sec, df):
    prd      = 5      # pivot period (left/right bars)
    bo_len   = 200    # max lookback for pivots
    cwidthu  = 0.03   # zone width threshold (3%)
    mintest  = 2      # minimum number of tests of the level

    df = df.copy().sort_index(ascending=True)
    n  = len(df)
    if n < prd*2 + 5:
        return None

    high  = df["High"].values
    low   = df["Low"].values
    close = df["Close"].values
    open_ = df["Open"].values

    cur = n - 1  # current (latest) bar index

    # ── chwidth: zone tolerance based on recent range ──
    lll = max(min(cur, 300), 1)
    h_  = float(high[cur-lll+1:cur+1].max())
    l_  = float(low[cur-lll+1:cur+1].min())
    chwidth = (h_ - l_) * cwidthu
    if chwidth <= 0:
        return None

    # ── collect confirmed pivot highs/lows (most recent first) ──
    phval=[]; phloc=[]
    plval=[]; plloc=[]
    for i in range(cur-prd, prd-1, -1):
        if cur - i > bo_len:
            break
        lh, rh = high[i-prd:i], high[i+1:i+prd+1]
        if high[i] > lh.max() and high[i] > rh.max():
            phval.append(float(high[i])); phloc.append(i)
        ll_, rl = low[i-prd:i], low[i+1:i+prd+1]
        if low[i] < ll_.min() and low[i] < rl.min():
            plval.append(float(low[i])); plloc.append(i)

    direction=None; level=None; tests=0; bostart=cur

    # ── Bullish breakout: close>open, close breaks above prior-prd-bar high,
    #     and clears a resistance shelf tested >= mintest times ──
    hgst = float(high[max(0,cur-prd):cur].max()) if cur>0 else float(high[cur])
    if len(phval) >= mintest and close[cur] > open_[cur] and close[cur] > hgst:
        bomax = phval[0]; xx = 0
        for x in range(len(phval)):
            if phval[x] >= close[cur]:
                break
            xx = x
            bomax = max(bomax, phval[x])
        if xx >= mintest and open_[cur] <= bomax:
            num = 0
            for x in range(xx+1):
                if phval[x] <= bomax and phval[x] >= bomax - chwidth:
                    num += 1
                    bostart = phloc[x]
            if num >= mintest and hgst < bomax:
                direction="Bullish Breakout"; level=bomax; tests=num

    # ── Bearish breakdown: close<open, close breaks below prior-prd-bar low,
    #     and breaks a support shelf tested >= mintest times ──
    if direction is None:
        lwst = float(low[max(0,cur-prd):cur].min()) if cur>0 else float(low[cur])
        if len(plval) >= mintest and close[cur] < open_[cur] and close[cur] < lwst:
            bomin = plval[0]; xx = 0
            for x in range(len(plval)):
                if plval[x] <= close[cur]:
                    break
                xx = x
                bomin = min(bomin, plval[x])
            if xx >= mintest and open_[cur] >= bomin:
                num = 0
                for x in range(xx+1):
                    if plval[x] >= bomin and plval[x] <= bomin + chwidth:
                        num += 1
                        bostart = plloc[x]
                if num >= mintest and lwst > bomin:
                    direction="Bearish Breakdown"; level=bomin; tests=num

    if direction is None:
        return None

    cmp_    = float(close[cur])
    prev_c  = float(close[cur-1])
    day_chg = (cmp_-prev_c)/prev_c*100 if prev_c else 0
    base_age= cur - bostart

    if direction=="Bullish Breakout":
        sl     = level - chwidth
        target = cmp_ + (cmp_-level) if cmp_>level else cmp_ + chwidth
        upside = (target-cmp_)/cmp_*100
    else:
        sl     = level + chwidth
        target = cmp_ - (level-cmp_) if level>cmp_ else cmp_ - chwidth
        upside = (cmp_-target)/cmp_*100

    return {
        "symbol":      sym,
        "sector":      sec,
        "direction":   direction,
        "cmp":         round(cmp_,2),
        "dayChg":      round(day_chg,2),
        "level":       round(level,2),
        "tests":       int(tests),
        "baseAge":     int(base_age),
        "zoneWidth":   round(chwidth,2),
        "target":      round(target,2),
        "sl":          round(sl,2),
        "upside":      round(upside,2),
    }



def analyse(sym, sec, df, nifty_ret, rr):
    if df is None or len(df)<30: return None, None
    df   = df.copy().sort_index(ascending=True)
    close= df["Close"]; high=df["High"]; low=df["Low"]; vol=df["Volume"]
    n    = len(df)

    cmp       = float(close.iloc[-1])
    prev_close= float(close.iloc[-2])
    day_chg   = (cmp-prev_close)/prev_close*100 if prev_close else 0

    # CPR
    ph,pl,pc  = float(high.iloc[-2]),float(low.iloc[-2]),float(close.iloc[-2])
    pivot     = (ph+pl+pc)/3
    bc        = (ph+pl)/2
    tc        = (pivot-bc)+pivot
    cpr_top   = max(tc,bc); cpr_bot=min(tc,bc)
    narrow_cpr= (cpr_top-cpr_bot)<(pivot*0.005)

    # ATR
    atr_s = calc_atr(high,low,close,14)
    atr14 = float(atr_s.iloc[-1])
    atr_sma = float(atr_s.iloc[-20:].mean()) if n>=20 else atr14
    atr_comp= float(atr_s.iloc[-2])<atr_sma*0.8

    # EMA
    e20 = calc_ema = ema(close,20); e50=ema(close,50); e200=ema(close,200) if n>=200 else ema(close,n)
    ema20,ema50,ema200 = float(e20.iloc[-1]),float(e50.iloc[-1]),float(e200.iloc[-1])
    ema20p,ema50p      = float(e20.iloc[-2]),float(e50.iloc[-2])
    ema_cross_bull = ema20p<=ema50p and ema20>ema50
    ema_cross_bear = ema20p>=ema50p and ema20<ema50
    above_ema50    = cmp>ema50

    # RSI
    rsi_s  = rsi(close,14)
    rsi_v  = float(rsi_s.iloc[-1])
    rsi_p  = float(rsi_s.iloc[-2])
    rsi_rising = rsi_v>rsi_p

    # MACD
    ml,sl_m,hist = macd(close)
    macd_hist  = float(hist.iloc[-1])
    macd_histp = float(hist.iloc[-2])
    macd_bull      = macd_hist>0 and macd_hist>macd_histp
    macd_cross_bull= macd_histp<0 and macd_hist>0
    macd_cross_bear= macd_histp>0 and macd_hist<0

    # BB
    bbu,bbm,bbl,bw = bollinger(close)
    bbu_v,bbl_v,bw_v = float(bbu.iloc[-1]),float(bbl.iloc[-1]),float(bw.iloc[-1])
    bbu_p,bbl_p      = float(bbu.iloc[-2]),float(bbl.iloc[-2])
    bw_avg = float(bw.iloc[-20:].mean()) if n>=20 else bw_v
    bb_squeeze     = bw_v<bw_avg*0.75
    bb_break_up    = cmp>bbu_v and float(close.iloc[-2])<=bbu_p
    bb_break_down  = cmp<bbl_v and float(close.iloc[-2])>=bbl_p

    # ADX
    adx_s,pdi,ndi = calc_adx(high,low,close,14)
    adx_v  = float(adx_s.iloc[-1])
    pdi_v  = float(pdi.iloc[-1])
    ndi_v  = float(ndi.iloc[-1])
    trending = adx_v>25

    # Supertrend
    st_line,st_dir = calc_supertrend(high,low,close,10,3)
    st_bull  = int(st_dir.iloc[-1])==1
    st_bullp = int(st_dir.iloc[-2])==1 if n>1 else True
    st_flip_bull = not st_bullp and st_bull
    st_flip_bear = st_bullp and not st_bull

    # Volume
    vol20 = float(vol.iloc[-21:-1].mean()) if n>21 else float(vol.mean())
    vol_t = float(vol.iloc[-1])
    vol_surge = vol_t/vol20 if vol20>0 else 0

    # 52-week
    wk52h = float(high.iloc[-252:].max()) if n>=252 else float(high.max())
    wk52l = float(low.iloc[-252:].min())  if n>=252 else float(low.min())
    pct_52wk  = (cmp-wk52h)/wk52h*100
    # FIX: approaching 52wk high from below (85–97% of high) — catches run-up BEFORE breakout
    approaching52h = wk52h*0.85 <= cmp < wk52h*0.97
    # Old near52h kept for breakout label logic only (actual breakout above 97%)
    near52h = cmp >= wk52h*0.97

    # HH/HL — FIX: tighter 5-bar lookback to catch fresh patterns, not mid-trend
    hhhl = hh_hl(close, 5)

    # RS vs Nifty
    stock_ret = (cmp-float(close.iloc[-21]))/float(close.iloc[-21])*100 if n>=21 else 0
    rs_nifty  = stock_ret - nifty_ret.get("1m",0)

    above_cpr = cmp>cpr_top
    below_cpr = cmp<cpr_bot
    vol_ok    = vol_surge>=1.5

    # FIX: guard against chased entries — stock already up 3%+ today is late
    not_chased = day_chg <= 3.0

    # FIX: Supertrend flip freshness — only reward st_bull if flip happened within last 7 candles
    st_flip_age = 0
    for k in range(1, min(8, n)):
        if int(st_dir.iloc[-(k+1)]) != int(st_dir.iloc[-k]):
            st_flip_age = k
            break
    st_fresh_bull = st_bull and (st_flip_age > 0)   # flipped within last 7 bars
    st_fresh_bear = not st_bull and (st_flip_age > 0)

    # FIX: tighter BB squeeze — only genuine compression (60% of avg, was 75%)
    bb_squeeze = bw_v < bw_avg * 0.60

    # ── CPR Signal ──
    cpr_conds = {
        "narrowCPR":      bool(narrow_cpr),
        "volSurge":       bool(vol_ok),
        "atrCompressed":  bool(atr_comp),
        "aboveCPR":       bool(above_cpr),
        "belowCPR":       bool(below_cpr),
        "aboveEMA50":     bool(above_ema50),
        "supertrendBull": bool(st_bull),
        "stFresh":        bool(st_fresh_bull or st_fresh_bear),
        "rsiOk":          bool(40<=rsi_v<=60),   # FIX: tightened from 70 to 60
        "macdBull":       bool(macd_bull),
        "trending":       bool(trending),
        "hhhl":           bool(hhhl),
        "rsPositive":     bool(rs_nifty>0),
        "notChased":      bool(not_chased),
        "approaching52h": bool(approaching52h),
    }

    # FIX: added not_chased and RSI cap at 60 to CPR long condition
    if above_cpr and vol_ok and (narrow_cpr or atr_comp) and above_ema50 and st_bull and rsi_v<=60 and not_chased:
        sig = "long"
    elif below_cpr and vol_ok and (narrow_cpr or atr_comp) and not above_ema50 and not st_bull and rsi_v>=40:
        sig = "short"
    else:
        sig = "watch"

    sl_d = 2*atr14; tp_d = rr*sl_d
    if sig=="long":   cpr_sl=cmp-sl_d; cpr_tgt=cmp+tp_d
    elif sig=="short":cpr_sl=cmp+sl_d; cpr_tgt=cmp-tp_d
    else:             cpr_sl=cmp-sl_d; cpr_tgt=cmp+1.5*sl_d

    cpr_up  = (cpr_tgt-cmp)/cmp*100
    cpr_rr  = abs(cpr_tgt-cmp)/max(abs(cmp-cpr_sl),0.01)
    cpr_qty = int(5000/max(abs(cmp-cpr_sl),0.01))

    conf=30
    if narrow_cpr:   conf+=10
    if vol_ok:       conf+=15
    if atr_comp:     conf+=10
    if above_ema50:  conf+=10
    if st_fresh_bull and sig=="long":  conf+=15  # FIX: fresh flip worth more
    elif st_bull and sig=="long":      conf+=5   # old bullish ST, less credit
    if st_fresh_bear and sig=="short": conf+=15
    elif not st_bull and sig=="short": conf+=5
    if 40<=rsi_v<=60: conf+=8   # FIX: tighter RSI range rewarded more
    if macd_bull:    conf+=5
    if trending:     conf+=5
    if hhhl and sig=="long":   conf+=5
    if rs_nifty>0:   conf+=5
    # FIX: approaching 52wk high (not already at it) rewarded; AT 52wk high penalised
    if approaching52h and sig=="long": conf+=8
    if near52h and sig=="long":        conf-=5   # already ran, penalise
    if above_cpr or below_cpr: conf+=5
    if not not_chased: conf-=15  # FIX: chased entry penalty
    conf=min(max(conf,0),98)

    cpr_row = {
        "symbol":sym,"sector":sec,"signal":sig,
        "cmp":round(cmp,2),"prevClose":round(prev_close,2),
        "dayOpen":round(float(df["Open"].iloc[-1]),2),
        "dayHigh":round(float(high.iloc[-1]),2),
        "dayLow":round(float(low.iloc[-1]),2),
        "dayChg":round(day_chg,2),
        "pivot":round(pivot,2),"cprTop":round(cpr_top,2),"cprBot":round(cpr_bot,2),
        "target":round(cpr_tgt,2),"sl":round(cpr_sl,2),
        "upside":round(cpr_up,2),"rr":round(cpr_rr,2),"qty":cpr_qty,
        "volSurge":round(vol_surge,2),"todayVol":int(vol_t),
        "atr14":round(atr14,2),"rsi":round(rsi_v,1),
        "macdHist":round(macd_hist,2),"adx":round(adx_v,1),
        "ema20":round(ema20,2),"ema50":round(ema50,2),"ema200":round(ema200,2),
        "stBull":bool(st_bull),"pct52wk":round(pct_52wk,1),
        "rsNifty":round(rs_nifty,1),"conditions":cpr_conds,"confidence":conf,
    }

    # ── Breakout Signal ──
    brk_conds = {
        "emaCrossBull":  bool(ema_cross_bull),"emaCrossBear":bool(ema_cross_bear),
        "bbBreakoutUp":  bool(bb_break_up),"bbBreakoutDown":bool(bb_break_down),
        "bbSqueeze":     bool(bb_squeeze),"macdCrossBull":bool(macd_cross_bull),
        "macdCrossBear": bool(macd_cross_bear),"stFlipBull":bool(st_flip_bull),
        "stFlipBear":    bool(st_flip_bear),"stFreshBull":bool(st_fresh_bull),
        "approaching52h":bool(approaching52h),"near52wkHigh":bool(near52h),
        "volSurge":      bool(vol_ok),"rsiMomentum":bool(40<rsi_v<=60 and rsi_rising),  # FIX: capped at 60
        "adxTrending":   bool(trending),"hhhl":bool(hhhl),"rsPositive":bool(rs_nifty>0),
        "notChased":     bool(not_chased),
    }

    bull=0; bear=0
    if ema_cross_bull:  bull+=20
    if bb_break_up:     bull+=18
    if macd_cross_bull: bull+=15
    if st_flip_bull:    bull+=20
    if st_fresh_bull:   bull+=10   # FIX: extra reward for fresh ST flip
    # FIX: approaching 52wk high scores well; at/above 52wk high scores less (already ran)
    if approaching52h and vol_ok:  bull+=18
    if near52h and vol_ok:         bull+=6   # was 15, reduced significantly
    if bb_squeeze and vol_ok:      bull+=12
    # FIX: RSI momentum only rewarded when not overbought (<=60)
    if 40<rsi_v<=60 and rsi_rising: bull+=10
    if rsi_v>60 and rsi_rising:     bull+=2   # extended momentum, minor credit only
    if hhhl:            bull+=8
    if rs_nifty>2:      bull+=6
    if trending and pdi_v>ndi_v: bull+=8
    # FIX: penalise chased entries
    if not not_chased:  bull-=15

    if ema_cross_bear:  bear+=20
    if bb_break_down:   bear+=18
    if macd_cross_bear: bear+=15
    if st_flip_bear:    bear+=20
    if st_fresh_bear:   bear+=10
    if rsi_v<50 and not rsi_rising: bear+=8
    if rs_nifty<-2:     bear+=6
    if trending and ndi_v>pdi_v: bear+=8

    bull=max(bull,0); bear=max(bear,0)
    if bull>=20:   drxn="bullish"; score=min(bull,100)
    elif bear>=20: drxn="bearish"; score=min(bear,100)
    else:          drxn="neutral"; score=max(bull,bear)

    if drxn=="bullish": b_sl=cmp-2*atr14; b_tgt=cmp+rr*2*atr14
    elif drxn=="bearish":b_sl=cmp+2*atr14; b_tgt=cmp-rr*2*atr14
    else:               b_sl=cmp-2*atr14; b_tgt=cmp+1.5*2*atr14

    b_up  = (b_tgt-cmp)/cmp*100
    b_rr  = abs(b_tgt-cmp)/max(abs(cmp-b_sl),0.01)
    b_qty = int(5000/max(abs(cmp-b_sl),0.01))

    if drxn=="bullish":
        if ema_cross_bull and st_flip_bull: rec="Strong Breakout — EMA Golden Cross + Supertrend flip"
        elif bb_break_up and vol_ok:        rec="BB Breakout — Price broke upper band with volume"
        elif macd_cross_bull and rsi_v<=60: rec="MACD Bull Cross — Momentum turning positive"
        elif approaching52h and vol_ok:     rec="Approaching 52-Week High — Pre-breakout setup"
        elif near52h and vol_ok:            rec="52-Week High Breakout — Watch for exhaustion"
        elif bb_squeeze and vol_ok:         rec="BB Squeeze Breakout — Volatility expansion starting"
        else:                               rec="Bullish Setup — Multiple indicators aligning"
    elif drxn=="bearish":
        if ema_cross_bear and st_flip_bear: rec="Strong Breakdown — EMA Death Cross + Supertrend flip"
        elif bb_break_down and vol_ok:      rec="BB Breakdown — Price broke lower band with volume"
        elif macd_cross_bear:               rec="MACD Bear Cross — Momentum turning negative"
        else:                               rec="Bearish Setup — Multiple indicators aligning"
    else:
        rec="Consolidating — No clear breakout signal yet"

    brk_row = {
        "symbol":sym,"sector":sec,"direction":drxn,"score":score,
        "recommendation":rec,"cmp":round(cmp,2),"dayChg":round(day_chg,2),
        "target":round(b_tgt,2),"sl":round(b_sl,2),
        "upside":round(b_up,2),"rr":round(b_rr,2),"qty":b_qty,
        "rsi":round(rsi_v,1),"macdHist":round(macd_hist,2),"adx":round(adx_v,1),
        "bbBW":round(bw_v*100,1),"volSurge":round(vol_surge,2),
        "ema20":round(ema20,2),"ema50":round(ema50,2),"stBull":bool(st_bull),
        "pct52wk":round(pct_52wk,1),"rsNifty":round(rs_nifty,1),
        "conditions":brk_conds,
    }

    return cpr_row, brk_row

BATCH_SIZE = 50  # number of tickers per yf.download batch call

def fetch_batch(symbols, period, interval):
    """
    Fetch OHLCV for multiple symbols in one yf.download call.
    Returns dict: symbol -> DataFrame (ascending, NaN-cleaned) or None.
    Much faster + far fewer requests than one-ticker-at-a-time history().
    """
    out = {s: None for s in symbols}
    if not symbols:
        return out
    yf_syms = [s + ".NS" for s in symbols]
    try:
        data = yf.download(
            yf_syms, period=period, interval=interval,
            group_by="ticker", auto_adjust=True,
            threads=True, progress=False, session=YF_SESSION
        )
    except Exception as e:
        log.warning(f"Batch download failed ({period}/{interval}): {e}")
        return out

    if data is None or data.empty:
        return out

    multi = isinstance(data.columns, pd.MultiIndex)
    for sym, ysym in zip(symbols, yf_syms):
        try:
            if multi:
                if ysym not in data.columns.get_level_values(0):
                    continue
                df = data[ysym].dropna(how="all")
            else:
                # single-ticker fallback (no MultiIndex)
                df = data.dropna(how="all")
            if df is None or df.empty or len(df) < 5:
                continue
            df = df.dropna(subset=["Close"])
            if len(df) < 5:
                continue
            out[sym] = df.sort_index(ascending=True)
        except Exception:
            continue
    return out

# ══════════════════════════════════════════════
# Nifty returns for RS
# ══════════════════════════════════════════════
def fetch_nifty_ret():
    try:
        df = yf.Ticker("^NSEI", session=YF_SESSION).history(period="3mo",interval="1d",auto_adjust=True)
        if df is not None and len(df)>=21:
            df=df.sort_index(ascending=True); c=df["Close"]
            return {"1m":(c.iloc[-1]-c.iloc[-21])/c.iloc[-21]*100,
                    "3m":(c.iloc[-1]-c.iloc[0])/c.iloc[0]*100}
    except: pass
    return {"1m":0,"3m":0}

# ══════════════════════════════════════════════
# Background scan thread
# ══════════════════════════════════════════════
def run_scan(rr=3.0):
    with lock:
        if cache["status"]=="scanning": return
        cache.update({"status":"scanning","progress":0,"done":0,"ok":0,"failed":0,
                      "cpr":[],"brk":[],"dbl":[],"bof":[],"message":""})

    nifty_ret = fetch_nifty_ret()
    with lock: cache["nifty_ret"]=nifty_ret

    cpr_list=[]; brk_list=[]; dbl_list=[]; bof_list=[]
    total=len(UNIVERSE)

    for batch_start in range(0, total, BATCH_SIZE):
        batch     = UNIVERSE[batch_start:batch_start+BATCH_SIZE]
        batch_end = min(batch_start+BATCH_SIZE, total)
        syms      = [s for s,_ in batch]

        with lock:
            cache["message"]=f"Fetching daily data ({batch_start+1}-{batch_end}/{total})"
        daily_data = fetch_batch(syms, period="1y", interval="1d")

        with lock:
            cache["message"]=f"Fetching weekly data ({batch_start+1}-{batch_end}/{total})"
        weekly_data = fetch_batch(syms, period="2y", interval="1wk")

        for i,(sym,sec) in enumerate(batch):
            try:
                df = daily_data.get(sym)
                if df is not None and len(df)>=30:
                    c,b=analyse(sym,sec,df,nifty_ret,rr)
                    if c: cpr_list.append(c)
                    if b: brk_list.append(b)
                    with lock: cache["ok"]+=1

                    bf=detect_breakout_finder(sym,sec,df)
                    if bf: bof_list.append(bf)
                else:
                    with lock: cache["failed"]+=1

                df_w = weekly_data.get(sym)
                if df_w is not None and len(df_w)>=20:
                    d=detect_double_bottom(sym,sec,df_w)
                    if d: dbl_list.append(d)

            except Exception as e:
                log.warning(f"  {sym}: {e}")
                with lock: cache["failed"]+=1

            with lock:
                idx=batch_start+i
                cache["done"]    =idx+1
                cache["progress"]=int((idx+1)/total*100)

        with lock:
            cache["cpr"]    =cpr_list.copy()
            cache["brk"]    =brk_list.copy()
            cache["dbl"]    =dbl_list.copy()
            cache["bof"]    =bof_list.copy()
            cache["message"]=f"Processed {batch_end}/{total}"

        time.sleep(1.0)  # brief pause between batches to ease rate limits

    with lock:
        cache["status"]    ="done"
        cache["last_scan"] =datetime.now().isoformat()
        cache["last_quote"]=datetime.now().isoformat()
        log.info(f"Scan done: {cache['ok']} ok, {cache['failed']} failed")

    # Kick off quote refresh loop
    threading.Thread(target=bg_refresh_loop, daemon=True).start()

def bg_refresh_loop():
    """Refresh quotes every 60s after scan completes."""
    while True:
        time.sleep(60)
        with lock:
            if cache["status"]!="done": break
            rr=cache.get("rr",3.0)
        refresh_quotes(rr)

def refresh_quotes(rr=3.0):
    with lock:
        syms_secs=[(r["symbol"],r["sector"]) for r in cache["cpr"]]
        nifty_ret=cache["nifty_ret"]
    if not syms_secs: return
    log.info(f"Refreshing {len(syms_secs)} quotes…")

    cpr_list=[]; brk_list=[]; bof_list=[]
    for batch_start in range(0, len(syms_secs), BATCH_SIZE):
        batch = syms_secs[batch_start:batch_start+BATCH_SIZE]
        syms  = [s for s,_ in batch]
        daily_data = fetch_batch(syms, period="1y", interval="1d")

        for sym,sec in batch:
            try:
                df = daily_data.get(sym)
                if df is not None and len(df)>=30:
                    c,b=analyse(sym,sec,df,nifty_ret,rr)
                    if c: cpr_list.append(c)
                    if b: brk_list.append(b)
                    bf=detect_breakout_finder(sym,sec,df)
                    if bf: bof_list.append(bf)
            except: pass

    with lock:
        cache["cpr"]=cpr_list; cache["brk"]=brk_list; cache["bof"]=bof_list
        cache["last_quote"]=datetime.now().isoformat()
    log.info("Quote refresh done")

def fetch_indices():
    data=[]
    for sym,label in INDICES_LIST:
        try:
            df=yf.Ticker(sym, session=YF_SESSION).history(period="5d",interval="1d",auto_adjust=True)
            if df is not None and len(df)>=2:
                df=df.sort_index(ascending=False)
                p=float(df["Close"].iloc[0]); pv=float(df["Close"].iloc[1])
                data.append({"label":label,"price":round(p,2),"chg":round((p-pv)/pv*100,2)})
        except: pass
    with lock: cache["indices"]=data

# ══════════════════════════════════════════════
# Routes
# ══════════════════════════════════════════════
@app.route("/api/status")
def api_status():
    with lock:
        return jsonify({k:cache[k] for k in
            ["status","progress","message","total","done","ok","failed","last_scan","last_quote"]})

@app.route("/api/scan", methods=["POST"])
def api_scan():
    data=request.get_json(silent=True) or {}
    rr=float(data.get("rr_ratio",3.0))
    with lock:
        if cache["status"]=="scanning":
            return jsonify({"error":"Scan already running"}),409
        cache["rr"]=rr
    threading.Thread(target=run_scan,args=(rr,),daemon=True).start()
    return jsonify({"started":True,"rr_ratio":rr})

@app.route("/api/results")
def api_results():
    with lock:
        return jsonify({
            "status":    cache["status"],
            "cpr":       cache["cpr"],
            "brk":       cache["brk"],
            "dbl":       cache["dbl"],
            "bof":       cache["bof"],
            "last_quote":cache["last_quote"],
        })

@app.route("/api/refresh", methods=["POST"])
def api_refresh():
    data=request.get_json(silent=True) or {}
    rr=float(data.get("rr_ratio",3.0))
    threading.Thread(target=refresh_quotes,args=(rr,),daemon=True).start()
    return jsonify({"started":True})

@app.route("/api/indices")
def api_indices():
    with lock: return jsonify(cache["indices"])

@app.route("/api/refresh-indices",methods=["POST"])
def api_refresh_indices():
    threading.Thread(target=fetch_indices,daemon=True).start()
    return jsonify({"started":True})

@app.route("/")
def index():
    return send_file(os.path.join(os.path.dirname(os.path.abspath(__file__)), "screener.html"))

if __name__=="__main__":
    threading.Thread(target=fetch_indices,daemon=True).start()
    print("\n"+"="*55)
    print("  NSE Screener — Flask + yfinance (Top ~850 by Mcap, Batched)")
    print("="*55)
    print(f"  Universe : {len(UNIVERSE)} stocks")
    print(f"  Server   : http://localhost:5000")
    print(f"  Open     : http://localhost:5000  (single URL, frontend + API)")
    print("="*55+"\n")
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0",port=port,debug=False,threaded=True)
