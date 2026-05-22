import streamlit as st
import feedparser
import urllib.request

# スマホの画面設定
st.set_page_config(page_title="AI TIMES", page_icon="✨", layout="centered")

# --- ✨ インターフェースを美しくする魔法（カスタムCSS） ---
st.markdown("""
    <style>
    html, body, [data-testid="stAppViewContainer"] {
        font-family: 'Helvetica Neue', Arial, 'Hiragino Kaku Gothic ProN', Meiryo, sans-serif;
    }
    .news-card {
        background-color: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 18px;
        border-radius: 12px;
        margin-bottom: 16px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .news-title a {
        color: #64B5F6 !important; 
        text-decoration: none !important;
        font-weight: 700 !important;
        font-size: 1.15rem !important;
        line-height: 1.4;
    }
    .source-badge {
        background-color: #37474F;
        color: #ECEFF1;
        padding: 3px 8px;
        border-radius: 6px;
        font-size: 0.75rem;
        font-weight: bold;
        display: inline-block;
        margin-bottom: 8px;
    }
    </style>
""", unsafe_allow_html=True)

st.title("✨ AI TIMES")
st.caption("Googleニュース＆世界の一流紙をエラーなしで完全網羅")

# 📊 ニュースソース：ヤフー完全排除、Googleと世界の一流通信社で固定
NEWS_SOURCES = {
    "🇯🇵 国内(Googleニュース)": [
        {"name": "Google主要", "url": "https://news.google.com/rss?hl=ja&gl=JP&ceid=JP:ja"}
    ],
    "🌍 世界の動き(海外一流紙)": [
        {"name": "BBCニュース", "url": "https://www.bbc.com/japanese/index.xml"},
        {"name": "ロイター通信", "url": "https://jp.reuters.com/arc/outboundfeeds/rss/category/world/?outputType=xml"}
    ],
    "🤖 AI・最先端テック": [
        {"name": "Google IT科学", "url": "https://news.google.com/rss/headlines/section/topic/TECHNOLOGY?hl=ja&gl=JP&ceid=JP:ja"},
        {"name": "ギズモード", "url": "https://www.gizmodo.jp/index.xml"},
        {"name": "WIRED", "url": "https://wired.jp/rss/"}
    ],
    "📈 経済・ビジネス": [
        {"name": "Google経済", "url": "https://news.google.com/rss/headlines/section/topic/BUSINESS?hl=ja&gl=JP&ceid=JP:ja"},
        {"name": "ロイター経済", "url": "https://jp.reuters.com/arc/outboundfeeds/rss/category/business/?outputType=xml"}
    ]
}

tabs = st.tabs(list(NEWS_SOURCES.keys()))

def fetch_and_display_category(sources, category_index):
    all_entries = []
    
    for source in sources:
        try:
            # ★今度こその大本命対策：一般的なMacのブラウザ（Safari/Chrome）のふりをする
            req = urllib.request.Request(
                source["url"], 
                headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
            )
            
            # ブラウザのふりをしてデータをダウンロード
            with urllib.request.urlopen(req, timeout=8) as response:
                html_data = response.read()
            
            # ダウンロードしたデータを解析
            feed = feedparser.parse(html_data)
            
            if feed.entries:
                for entry in feed.entries:
                    display_title = entry.title
                    source_name = source["name"]
                    
                    # Googleニュース特有の「メディア名 - タイトル」から、本当のメディア名を引っこ抜く
                    if " - " in display_title and "Google" in source["name"]:
                        parts = display_title.split(" - ")
                        source_name = f"📰 {parts[-1]}" # 読売、朝日、文春などの名前が入る
                        display_title = " - ".join(parts[:-1])
                    
                    entry["custom_title"] = display_title
                    entry["source_name"] = source_name
                    all_entries.append(entry)
        except Exception:
            # 万が一1つのメディアが死んでいても、他を絶対に巻き添えにしない
            continue
                
    if not all_entries:
        st.warning("ニュースの取得に失敗しました。最下部の更新ボタンを押してみてください。")
        return

    unique_key = f"slider_{category_index}_{sources[0]['name'].replace(' ', '_')}"
    max_items = st.slider("表示件数:", min_value=5, max_value=25, value=12, step=4, key=unique_key)
    st.markdown("---")

    for entry in all_entries[:max_items]:
        raw_summary = getattr(entry, 'summary', '')
        
        if '<' in raw_summary:
            raw_summary = raw_summary.split('<')[0]
        raw_summary = raw_summary.split('（')[0].strip()
        
        if not raw_summary or len(raw_summary) < 5:
            raw_summary = "タップして配信元の本文をご確認ください。"

        st.markdown(f"""
            <div class="news-card">
                <span class="source-badge">{entry['source_name']}</span>
                <div class="news-title">
                    <a href="{entry.link}" target="_blank">🔗 {entry['custom_title']}</a>
                </div>
                <div style="margin-top: 10px; font-size: 0.9rem; color: #B0BEC5;">
                    💡 {raw_summary}
                </div>
            </div>
        """, unsafe_allow_html=True)

# 各タブの処理
for i, category_name in enumerate(NEWS_SOURCES.keys()):
    with tabs[i]:
        fetch_and_display_category(NEWS_SOURCES[category_name], i)

st.markdown("---")
if st.button("🔄 最新ニュースに更新"):
    st.rerun()
