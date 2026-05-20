import streamlit as st
import feedparser

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
st.caption("日本・世界・AIトレンドを毎日のルーティンに")

# ニュースソース（RSS）
NEWS_SOURCES = {
    "🇯🇵 国内主要": [
        {"name": "国内トピックス", "url": "https://news.yahoo.co.jp/rss/topics/domestic.xml"},
        {"name": "主要トップ", "url": "https://news.yahoo.co.jp/rss/topics/top-picks.xml"}
    ],
    "🌍 世界の動き": [
        {"name": "国際トピックス", "url": "https://news.yahoo.co.jp/rss/topics/world.xml"},
        {"name": "ロイター世界", "url": "https://news.yahoo.co.jp/rss/categories/world.xml"}
    ],
    "🤖 AI・最先端技術": [
        {"name": "ITトピックス", "url": "https://news.yahoo.co.jp/rss/topics/it.xml"},
        {"name": "サイエンス最新", "url": "https://news.yahoo.co.jp/rss/categories/science.xml"}
    ],
    "📈 経済・ビジネス": [
        {"name": "経済トピックス", "url": "https://news.yahoo.co.jp/rss/topics/business.xml"}
    ]
}

tabs = st.tabs(list(NEWS_SOURCES.keys()))

def fetch_and_display_category(sources):
    all_entries = []
    for source in sources:
        feed = feedparser.parse(source["url"])
        if feed.entries:
            for entry in feed.entries:
                entry["source_name"] = source["name"]
                all_entries.append(entry)
                
    if not all_entries:
        st.warning("ニュースの取得に失敗しました。")
        return

    unique_key = f"slider_{sources[0]['name']}"
    max_items = st.slider("表示件数:", min_value=5, max_value=25, value=10, step=5, key=unique_key)
    st.markdown("---")

    for entry in all_entries[:max_items]:
        raw_summary = getattr(entry, 'summary', '').split('（')[0]
        
        # カードの中に「タイトル」と「記事の概要」を綺麗にまとめて表示
        st.markdown(f"""
            <div class="news-card">
                <span class="source-badge">{entry['source_name']}</span>
                <div class="news-title">
                    <a href="{entry.link}" target="_blank">🔗 {entry.title}</a>
                </div>
                <div style="margin-top: 10px; font-size: 0.9rem; color: #B0BEC5;">
                    💡 {raw_summary}...
                </div>
            </div>
        """, unsafe_allow_html=True)

for i, category_name in enumerate(NEWS_SOURCES.keys()):
    with tabs[i]:
        fetch_and_display_category(NEWS_SOURCES[category_name])

st.markdown("---")
if st.button("🔄 最新ニュースに更新"):
    st.rerun()