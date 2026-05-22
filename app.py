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
st.caption("ヤフー完全排除。Googleニュースが厳選する日本と世界の多角的な視点")

# 📊 ニュースソース：並び順を元に戻し、死なない公式URLだけで再構築
NEWS_SOURCES = {
    "🇯🇵 国内(Googleニュース)": [
        {"name": "Google主要", "url": "https://news.google.com/rss?hl=ja&gl=JP&ceid=JP:ja"}
    ],
    "🌍 世界の動き": [
        # ★エラー原因だった中継URLを全廃し、絶対に弾かれないGoogleの国際ニュースRSSに一本化
        {"name": "Google国際", "url": "https://news.google.com/rss/headlines/section/topic/WORLD?hl=ja&gl=JP&ceid=JP:ja"}
    ],
    "🤖 AI・最先端テック": [
        {"name": "Google IT科学", "url": "https://news.google.com/rss/headlines/section/topic/TECHNOLOGY?hl=ja&gl=JP&ceid=JP:ja"},
        {"name": "ギズモード", "url": "https://www.gizmodo.jp/index.xml"},
        {"name": "WIRED", "url": "https://wired.jp/rss/"}
    ],
    "📈 経済・ビジネス": [
        {"name": "Google経済", "url": "https://news.google.com/rss/headlines/section/topic/BUSINESS?hl=ja&gl=JP&ceid=JP:ja"}
    ]
}

tabs = st.tabs(list(NEWS_SOURCES.keys()))

def fetch_and_display_category(sources, category_index):
    all_entries = []
    
    for source in sources:
        try:
            # 標準のブラウザ偽装で直接クリーンに取得
            req = urllib.request.Request(
                source["url"], 
                headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
            )
            
            with urllib.request.urlopen(req, timeout=8) as response:
                html_data = response.read()
            
            feed = feedparser.parse(html_data)
            
            if feed.entries:
                for entry in feed.entries:
                    display_title = entry.title
                    source_name = source["name"]
                    
                    # Googleニュースのタイトルから発信元の新聞社・メディア名を自動抽出
                    if " - " in display_title and "Google" in source["name"]:
                        parts = display_title.split(" - ")
                        source_name = f"📰 {parts[-1]}"
                        display_title = " - ".join(parts[:-1])
                    
                    entry["custom_title"] = display_title
                    entry["source_name"] = source_name
                    all_entries.append(entry)
        except Exception:
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
