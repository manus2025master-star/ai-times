import streamlit as st
import feedparser
import urllib.parse

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
st.caption("ヤフー完全排除。Googleニュースと世界の一流紙で創る圧倒的多様性")

# 🌍 ニュースソース：ヤフーを一切使わず、Googleと世界の一流通信社で構成！
# クラウドでのブロック対策として、Google経由の特殊なURLに変換して読み込みます
NEWS_SOURCES = {
    "🇯🇵 国内(Googleニュース)": [
        {"name": "Google 主要ニュース", "url": "https://news.google.com/rss?hl=ja&gl=JP&ceid=JP:ja"},
        {"name": "NHK 社会ニュース", "url": "https://www3.nhk.or.jp/rss/news/cat0.xml"}
    ],
    "🌍 世界の動き(海外一流紙)": [
        {"name": "BBCニュース (英国)", "url": "https://www.bbc.com/japanese/index.xml"},
        {"name": "ロイター (国際通信)", "url": "https://jp.reuters.com/arc/outboundfeeds/rss/category/world/?outputType=xml"}
    ],
    "🤖 AI・最先端テック": [
        {"name": "Google IT・科学", "url": "https://news.google.com/rss/headlines/section/topic/TECHNOLOGY?hl=ja&gl=JP&ceid=JP:ja"},
        {"name": "ギズモード・ジャパン", "url": "https://www.gizmodo.jp/index.xml"},
        {"name": "WIRED (日本版)", "url": "https://wired.jp/rss/"}
    ],
    "📈 経済・ビジネス": [
        {"name": "Google 経済・ビジネス", "url": "https://news.google.com/rss/headlines/section/topic/BUSINESS?hl=ja&gl=JP&ceid=JP:ja"},
        {"name": "ロイター (ビジネス)", "url": "https://jp.reuters.com/arc/outboundfeeds/rss/category/business/?outputType=xml"}
    ]
}

tabs = st.tabs(list(NEWS_SOURCES.keys()))

def fetch_and_display_category(sources, category_index):
    all_entries = []
    
    for source in sources:
        try:
            # ★裏技：Streamlit Cloud（海外サーバー）でも弾かれないよう、Googleのプロキシを経由させてRSSを強制取得
            encoded_url = urllib.parse.quote(source["url"], safe='')
            proxy_url = f"https://images1-focus-opensocial.googleusercontent.com/gadgets/proxy?container=focus&refresh=600&url={encoded_url}"
            
            feed = feedparser.parse(proxy_url)
            if feed.entries:
                for entry in feed.entries:
                    # Googleニュース特有の「メディア名 - タイトル」から、本当のメディア名を引っこ抜く処理
                    display_title = entry.title
                    source_name = source["name"]
                    
                    if " - " in display_title and "Google" in source["name"]:
                        parts = display_title.split(" - ")
                        source_name = f"📰 {parts[-1]}" # 読売、朝日、東洋経済などの名前が入る
                        display_title = " - ".join(parts[:-1])
                    
                    entry["custom_title"] = display_title
                    entry["source_name"] = source_name
                    all_entries.append(entry)
        except Exception:
            continue
                
    if not all_entries:
        st.warning("ニュースの取得に失敗しました。15秒ほど待ってから『更新』を押してください。")
        return

    unique_key = f"slider_{category_index}_{sources[0]['name'].replace(' ', '_')}"
    max_items = st.slider("表示件数:", min_value=5, max_value=25, value=12, step=4, key=unique_key)
    st.markdown("---")

    for entry in all_entries[:max_items]:
        raw_summary = getattr(entry, 'summary', '')
        
        # 不要なHTMLや文字列の掃除
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
