import streamlit as st
import requests
import os
from dotenv import load_dotenv
import pandas as pd
from datetime import datetime
import time
import re
from collections import Counter
import plotly.express as px
import plotly.graph_objects as go

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="AI News Automator | Teslim Adeyanju",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for enhanced styling
st.markdown("""
<style>
    .main-header {
        font-size: 3.5rem;
        font-weight: bold;
        background: linear-gradient(45deg, #1f77b4, #ff6b6b, #4ecdc4);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        text-align: center;
        margin-bottom: 1rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
        animation: glow 2s ease-in-out infinite alternate;
    }
    
    @keyframes glow {
        from { filter: drop-shadow(0 0 5px #1f77b4); }
        to { filter: drop-shadow(0 0 20px #4ecdc4); }
    }
    
    .author-signature {
        text-align: center;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 15px;
        margin: 2rem 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }
    
    .ai-highlight {
        background: linear-gradient(135deg, #ff9a9e 0%, #fecfef 50%, #fecfef 100%);
        border: 2px solid #ff6b6b;
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        animation: pulse 2s infinite;
        box-shadow: 0 0 20px rgba(255, 107, 107, 0.3);
    }
    
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.02); }
        100% { transform: scale(1); }
    }
    
    .trending-badge {
        background: linear-gradient(45deg, #ff4757, #ff6b7a);
        color: white;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: bold;
        display: inline-block;
        margin: 0.2rem;
        animation: bounce 1s infinite;
    }
    
    @keyframes bounce {
        0%, 20%, 50%, 80%, 100% { transform: translateY(0); }
        40% { transform: translateY(-5px); }
        60% { transform: translateY(-3px); }
    }
    
    .news-card {
        background: white;
        padding: 1.5rem;
        border-radius: 15px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        margin-bottom: 1.5rem;
        border-left: 5px solid #1f77b4;
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    
    .news-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 30px rgba(0,0,0,0.2);
        border-left-color: #ff6b6b;
    }
    
    .news-title {
        font-size: 1.2rem;
        font-weight: bold;
        color: #333;
        margin-bottom: 0.8rem;
        line-height: 1.4;
    }
    
    .news-meta {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 1rem;
        font-size: 0.9rem;
        color: #666;
    }
    
    .source-badge {
        background: #f8f9fa;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        border: 1px solid #dee2e6;
        font-weight: 500;
    }
    
    .stats-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 2rem;
        border-radius: 15px;
        text-align: center;
        margin: 0.5rem 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        transition: transform 0.3s ease;
    }
    
    .stats-card:hover {
        transform: scale(1.05);
    }
    
    .stats-number {
        font-size: 2.5rem;
        font-weight: bold;
        margin-bottom: 0.5rem;
    }
    
    .interactive-filters {
        background: #f8f9fa;
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1rem 0;
        border: 1px solid #dee2e6;
    }
    
    .sidebar-header {
        color: #1f77b4;
        font-weight: bold;
        font-size: 1.3rem;
        margin-bottom: 1rem;
        text-align: center;
    }
    
    .ai-keywords {
        background: linear-gradient(45deg, #84fab0 0%, #8fd3f4 100%);
        color: #333;
        padding: 0.3rem 0.6rem;
        border-radius: 15px;
        font-size: 0.8rem;
        margin: 0.2rem;
        display: inline-block;
        font-weight: 500;
    }
    
    .breaking-news {
        background: linear-gradient(45deg, #ff512f 0%, #dd2476 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
        text-align: center;
        font-weight: bold;
        animation: flashRed 2s infinite;
    }
    
    @keyframes flashRed {
        0%, 50%, 100% { opacity: 1; }
        25%, 75% { opacity: 0.7; }
    }
    
    .footer-signature {
        background: linear-gradient(135deg, #2c3e50 0%, #3498db 100%);
        color: white;
        padding: 2rem;
        border-radius: 15px;
        text-align: center;
        margin-top: 3rem;
    }
</style>
""", unsafe_allow_html=True)


# AI/ML Keywords for highlighting
AI_KEYWORDS = [
    'artificial intelligence', 'ai', 'machine learning', 'ml', 'deep learning',
    'neural network', 'chatgpt', 'openai', 'anthropic', 'claude', 'llm',
    'large language model', 'transformer', 'bert', 'gpt', 'natural language',
    'computer vision', 'reinforcement learning', 'automation', 'robot',
    'algorithm', 'data science', 'predictive', 'recommendation', 'classification'
]


def is_ai_related(text):
    """Check if article contains AI/ML keywords"""
    text_lower = text.lower()
    return any(keyword in text_lower for keyword in AI_KEYWORDS)


def get_ai_keywords_in_text(text):
    """Extract AI keywords found in text"""
    text_lower = text.lower()
    found_keywords = [keyword for keyword in AI_KEYWORDS if keyword in text_lower]
    return found_keywords


def get_articles_by_category(category, max_articles=30):
    """Fetch news articles by category with enhanced processing"""
    API_KEY = os.getenv("API_KEY")
    URL = 'https://newsapi.org/v2/top-headlines?'
    
    query_parameters = {
        "category": category,
        "country": "us",
        "apiKey": API_KEY,
        "pageSize": max_articles
    }
    
    try:
        response = requests.get(URL, params=query_parameters)
        
        if response.status_code != 200:
            return {"error": f"API returned status code {response.status_code}"}
        
        data = response.json()
        
        if data['status'] != 'ok':
            return {"error": f"API returned status '{data['status']}'"}
        
        articles = data['articles']
        
        if not articles:
            return {"error": "No articles found for this category."}
        
        # Enhanced processing with AI detection
        processed_articles = []
        ai_articles = []
        
        for article in articles:
            if article['title'] and article['url']:
                full_text = f"{article['title']} {article.get('description', '')}"
                is_ai = is_ai_related(full_text)
                ai_keywords = get_ai_keywords_in_text(full_text) if is_ai else []
                
                processed_article = {
                    "title": article["title"],
                    "url": article["url"],
                    "description": article.get("description", "No description available"),
                    "source": article.get("source", {}).get("name", "Unknown"),
                    "publishedAt": article.get("publishedAt", ""),
                    "urlToImage": article.get("urlToImage", ""),
                    "is_ai_related": is_ai,
                    "ai_keywords": ai_keywords,
                    "content": article.get("content", "")
                }
                
                processed_articles.append(processed_article)
                if is_ai:
                    ai_articles.append(processed_article)
        
        return {
            "articles": processed_articles,
            "ai_articles": ai_articles,
            "total_results": data.get('totalResults', len(processed_articles)),
            "ai_count": len(ai_articles)
        }
        
    except Exception as e:
        return {"error": f"Error fetching articles: {str(e)}"}


def get_articles_by_query(query, max_articles=30):
    """Fetch news articles by search query with enhanced processing"""
    API_KEY = os.getenv("API_KEY")
    URL = 'https://newsapi.org/v2/everything?'
    
    query_parameters = {
        "q": query,
        "sortBy": "publishedAt",
        "language": "en",
        "apiKey": API_KEY,
        "pageSize": max_articles
    }
    
    try:
        response = requests.get(URL, params=query_parameters)
        
        if response.status_code != 200:
            return {"error": f"API returned status code {response.status_code}"}
        
        data = response.json()
        
        if data['status'] != 'ok':
            return {"error": f"API returned status '{data['status']}'"}
        
        articles = data['articles']
        
        if not articles:
            return {"error": "No articles found for this query."}
        
        # Enhanced processing
        processed_articles = []
        ai_articles = []
        
        for article in articles:
            if article['title'] and article['url']:
                full_text = f"{article['title']} {article.get('description', '')}"
                is_ai = is_ai_related(full_text)
                ai_keywords = get_ai_keywords_in_text(full_text) if is_ai else []
                
                processed_article = {
                    "title": article["title"],
                    "url": article["url"],
                    "description": article.get("description", "No description available"),
                    "source": article.get("source", {}).get("name", "Unknown"),
                    "publishedAt": article.get("publishedAt", ""),
                    "urlToImage": article.get("urlToImage", ""),
                    "is_ai_related": is_ai,
                    "ai_keywords": ai_keywords,
                    "content": article.get("content", "")
                }
                
                processed_articles.append(processed_article)
                if is_ai:
                    ai_articles.append(processed_article)
        
        return {
            "articles": processed_articles,
            "ai_articles": ai_articles,
            "total_results": data.get('totalResults', len(processed_articles)),
            "ai_count": len(ai_articles)
        }
        
    except Exception as e:
        return {"error": f"Error fetching articles: {str(e)}"}


def display_article_card(article, index, highlight_ai=False):
    """Display enhanced article card"""
    card_class = "ai-highlight" if highlight_ai and article.get('is_ai_related') else "news-card"
    
    # Format published date
    pub_date = ""
    if article.get('publishedAt'):
        try:
            dt = datetime.fromisoformat(article['publishedAt'].replace('Z', '+00:00'))
            pub_date = dt.strftime("%B %d, %Y at %I:%M %p")
        except:
            pub_date = article['publishedAt']
    
    # AI keywords badges
    ai_badges = ""
    if article.get('ai_keywords'):
        ai_badges = "".join([f'<span class="ai-keywords">{keyword.title()}</span>' 
                           for keyword in article['ai_keywords'][:5]])
    
    # Trending badge for AI articles
    trending = '<span class="trending-badge">🔥 AI/ML TRENDING</span>' if article.get('is_ai_related') else ''
    
    st.markdown(f"""
    <div class="{card_class}">
        <div class="news-meta">
            <span class="source-badge">📰 {article['source']}</span>
            <span style="color: #888;">{pub_date}</span>
        </div>
        <div class="news-title">
            {trending}
            {index}. {article['title']}
        </div>
        {ai_badges}
        <p style="color: #666; margin: 1rem 0; line-height: 1.5;">
            {article['description'][:250]}...
        </p>
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <a href="{article['url']}" target="_blank" 
               style="background: linear-gradient(45deg, #1f77b4, #4ecdc4); 
                      color: white; padding: 0.5rem 1rem; border-radius: 25px; 
                      text-decoration: none; font-weight: 500;">
                📖 Read Full Article
            </a>
            {f'<span style="color: #ff6b6b; font-weight: bold;">🤖 AI Related</span>' if article.get('is_ai_related') else ''}
        </div>
    </div>
    """, unsafe_allow_html=True)


def main():
    # Header with author signature
    st.markdown('''
    <div class="author-signature">
        <h1 class="main-header">🤖 AI News Automator</h1>
        <p style="font-size: 1.3rem; margin-bottom: 1rem;">
            Real-time AI & Tech News Aggregator
        </p>
        <div style="display: flex; justify-content: center; gap: 2rem; flex-wrap: wrap;">
            <span>👨‍💻 <strong>Teslim Uthman Adeyanju</strong></span>
            <span>📧 <a href="mailto:info@adeyanjuteslim.co.uk" style="color: white;">info@adeyanjuteslim.co.uk</a></span>
            <span>🔗 <a href="https://linkedin.com/in/adeyanjuteslimuthman" style="color: white;">LinkedIn</a></span>
            <span>🌐 <a href="https://adeyanjuteslim.co.uk" style="color: white;">Portfolio</a></span>
        </div>
    </div>
    ''', unsafe_allow_html=True)
    
    # Breaking news banner
    if st.session_state.get('show_breaking', True):
        st.markdown('''
        <div class="breaking-news">
            🚨 LIVE: Real-time AI & Technology News Feed | Last Updated: ''' + 
            datetime.now().strftime("%Y-%m-%d %H:%M:%S") + '''
        </div>
        ''', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.markdown('<p class="sidebar-header">⚙️ Interactive Controls</p>', unsafe_allow_html=True)
        
        # Mode selection
        mode = st.radio(
            "🎯 Select News Mode:",
            ["🤖 AI/ML Focus", "📂 Browse by Category", "🔍 Custom Search", "📊 Analytics Dashboard"],
            index=0
        )
        
        # Interactive filters
        st.markdown('<div class="interactive-filters">', unsafe_allow_html=True)
        st.markdown("**🎛️ Filters & Options**")
        
        max_articles = st.slider("📰 Articles to Load", 10, 50, 25)
        highlight_ai = st.checkbox("🌟 Highlight AI/ML News", value=True)
        auto_refresh = st.checkbox("🔄 Auto-refresh (30s)", value=False)
        
        # AI keyword filter
        selected_ai_keywords = st.multiselect(
            "🎯 Focus on AI Topics:",
            ['machine learning', 'chatgpt', 'openai', 'neural network', 'automation', 'robotics'],
            default=['machine learning', 'chatgpt']
        )
        st.markdown('</div>', unsafe_allow_html=True)
        
        # API status
        API_KEY = os.getenv("API_KEY")
        if API_KEY:
            st.success("🔑 API Connected")
        else:
            st.error("❌ API Key Missing")
        
        # Live stats
        if 'last_stats' in st.session_state:
            stats = st.session_state.last_stats
            st.markdown("**📊 Live Stats**")
            st.metric("Total Articles", stats.get('total', 0))
            st.metric("AI/ML Articles", stats.get('ai_count', 0))
            st.metric("Success Rate", f"{stats.get('success_rate', 0):.1f}%")
    
    # Auto-refresh logic
    if auto_refresh:
        time.sleep(30)
        st.rerun()
    
    # Main content based on mode
    if mode == "🤖 AI/ML Focus":
        st.subheader("🤖 AI & Machine Learning News Spotlight")
        
        # Quick AI search buttons
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            if st.button("🧠 Machine Learning", use_container_width=True):
                st.session_state.ai_query = "machine learning"
        with col2:
            if st.button("🤖 ChatGPT & LLMs", use_container_width=True):
                st.session_state.ai_query = "ChatGPT OR OpenAI OR Claude"
        with col3:
            if st.button("🚀 AI Startups", use_container_width=True):
                st.session_state.ai_query = "AI startup OR artificial intelligence funding"
        with col4:
            if st.button("🏭 AI in Business", use_container_width=True):
                st.session_state.ai_query = "AI business OR enterprise AI"
        
        # Use session state query or default
        ai_query = st.session_state.get('ai_query', 'artificial intelligence OR machine learning')
        
        if st.button("🔄 Get Latest AI News", type="primary", use_container_width=True):
            with st.spinner("🤖 Fetching cutting-edge AI news..."):
                result = get_articles_by_query(ai_query, max_articles)
                
                if "error" in result:
                    st.error(f"Error: {result['error']}")
                else:
                    articles = result["articles"]
                    ai_articles = result["ai_articles"]
                    
                    # Store stats
                    st.session_state.last_stats = {
                        'total': len(articles),
                        'ai_count': len(ai_articles),
                        'success_rate': (len(ai_articles) / len(articles) * 100) if articles else 0
                    }
                    
                    # AI-focused stats
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.markdown(f"""
                        <div class="stats-card">
                            <div class="stats-number">{len(articles)}</div>
                            <p>Total Articles</p>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col2:
                        st.markdown(f"""
                        <div class="stats-card">
                            <div class="stats-number">{len(ai_articles)}</div>
                            <p>AI/ML Articles</p>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col3:
                        ai_percentage = (len(ai_articles) / len(articles) * 100) if articles else 0
                        st.markdown(f"""
                        <div class="stats-card">
                            <div class="stats-number">{ai_percentage:.0f}%</div>
                            <p>AI Relevance</p>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col4:
                        st.markdown(f"""
                        <div class="stats-card">
                            <div class="stats-number">🔥</div>
                            <p>Trending Now</p>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    # Priority display: AI articles first
                    if ai_articles:
                        st.markdown("### 🌟 AI/ML Headlines")
                        for i, article in enumerate(ai_articles, 1):
                            display_article_card(article, i, highlight_ai=True)
                    
                    # Other tech articles
                    other_articles = [a for a in articles if not a.get('is_ai_related')]
                    if other_articles:
                        st.markdown("### 📰 Related Tech News")
                        for i, article in enumerate(other_articles, len(ai_articles) + 1):
                            display_article_card(article, i, highlight_ai=False)
    
    elif mode == "📂 Browse by Category":
        st.subheader("📂 Browse News by Category")
        
        categories = {
            "🤖 Technology": "technology",
            "💼 Business": "business", 
            "🏥 Health": "health",
            "🔬 Science": "science",
            "⚽ Sports": "sports",
            "🎭 Entertainment": "entertainment",
            "📰 General": "general"
        }
        
        selected_category_display = st.selectbox(
            "Choose a category:",
            list(categories.keys()),
            index=0
        )
        selected_category = categories[selected_category_display]
        
        if st.button("🔄 Fetch News", type="primary", use_container_width=True):
            with st.spinner(f"📡 Loading {selected_category_display} news..."):
                result = get_articles_by_category(selected_category, max_articles)
                
                if "error" in result:
                    st.error(f"Error: {result['error']}")
                else:
                    articles = result["articles"]
                    ai_articles = result["ai_articles"]
                    
                    # Enhanced stats display
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.markdown(f"""
                        <div class="stats-card">
                            <div class="stats-number">{len(articles)}</div>
                            <p>Articles Found</p>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col2:
                        st.markdown(f"""
                        <div class="stats-card">
                            <div class="stats-number">{len(ai_articles)}</div>
                            <p>AI/ML Related</p>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col3:
                        st.markdown(f"""
                        <div class="stats-card">
                            <div class="stats-number">{selected_category_display}</div>
                            <p>Category</p>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    st.markdown("---")
                    
                    # Display articles with AI priority
                    if highlight_ai and ai_articles:
                        st.markdown("### 🌟 AI/ML Highlights")
                        for i, article in enumerate(ai_articles, 1):
                            display_article_card(article, i, highlight_ai=True)
                        
                        other_articles = [a for a in articles if not a.get('is_ai_related')]
                        if other_articles:
                            st.markdown("### 📰 Other News")
                            for i, article in enumerate(other_articles, len(ai_articles) + 1):
                                display_article_card(article, i, highlight_ai=False)
                    else:
                        for i, article in enumerate(articles, 1):
                            display_article_card(article, i, highlight_ai=highlight_ai)
    
    elif mode == "🔍 Custom Search":
        st.subheader("🔍 Custom News Search")
        
        # Search suggestions
        search_suggestions = [
            "artificial intelligence", "machine learning", "ChatGPT", "OpenAI",
            "neural networks", "deep learning", "robotics", "automation",
            "data science", "blockchain", "cryptocurrency", "startup"
        ]
        
        col1, col2 = st.columns([3, 1])
        with col1:
            search_query = st.text_input(
                "🔍 Enter your search terms:",
                placeholder="e.g., AI, machine learning, robotics...",
                help="Search across all news sources"
            )
        
        with col2:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("🎲 Random AI Topic"):
                import random
                search_query = random.choice(search_suggestions)
                st.session_state.search_query = search_query
        
        # Quick search buttons
        st.markdown("**🚀 Quick Searches:**")
        cols = st.columns(4)
        quick_searches = ["AI breakthrough", "machine learning news", "tech startup", "robotics"]
        for i, query in enumerate(quick_searches):
            with cols[i]:
                if st.button(query, use_container_width=True):
                    search_query = query
                    st.session_state.search_query = query
        
        if search_query and st.button("🔍 Search News", type="primary", use_container_width=True):
            with st.spinner(f"🔍 Searching for '{search_query}'..."):
                result = get_articles_by_query(search_query, max_articles)
                
                if "error" in result:
                    st.error(f"Error: {result['error']}")
                else:
                    articles = result["articles"]
                    ai_articles = result["ai_articles"]
                    
                    # Search results stats
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.markdown(f"""
                        <div class="stats-card">
                            <div class="stats-number">{len(articles)}</div>
                            <p>Search Results</p>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col2:
                        st.markdown(f"""
                        <div class="stats-card">
                            <div class="stats-number">{len(ai_articles)}</div>
                            <p>AI/ML Results</p>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col3:
                        relevance = (len(ai_articles) / len(articles) * 100) if articles else 0
                        st.markdown(f"""
                        <div class="stats-card">
                            <div class="stats-number">{relevance:.0f}%</div>
                            <p>AI Relevance</p>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    st.markdown("---")
                    
                    # Display results
                    for i, article in enumerate(articles, 1):
                        display_article_card(article, i, highlight_ai=highlight_ai)
    
    elif mode == "📊 Analytics Dashboard":
        st.subheader("📊 News Analytics Dashboard")
        
        if st.button("📈 Generate Analytics", type="primary"):
            with st.spinner("📊 Analyzing news trends..."):
                # Get data from multiple sources
                tech_result = get_articles_by_category("technology", 30)
                business_result = get_articles_by_category("business", 30)
                
                if "error" not in tech_result and "error" not in business_result:
                    all_articles = tech_result["articles"] + business_result["articles"]
                    
                    # AI trend analysis
                    ai_count = len([a for a in all_articles if a.get('is_ai_related')])
                    total_count = len(all_articles)
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        # AI vs Non-AI pie chart
                        fig_pie = px.pie(
                            values=[ai_count, total_count - ai_count],
                            names=['AI/ML Related', 'Other Tech'],
                            title="AI/ML News Distribution",
                            color_discrete_map={'AI/ML Related': '#ff6b6b', 'Other Tech': '#4ecdc4'}
                        )
                        st.plotly_chart(fig_pie, use_container_width=True)
                    
                    with col2:
                        # Source analysis
                        sources = [a['source'] for a in all_articles]
                        source_counts = Counter(sources)
                        top_sources = dict(source_counts.most_common(5))
                        
                        fig_bar = px.bar(
                            x=list(top_sources.keys()),
                            y=list(top_sources.values()),
                            title="Top News Sources",
                            color=list(top_sources.values()),
                            color_continuous_scale="viridis"
                        )
                        st.plotly_chart(fig_bar, use_container_width=True)
                    
                    # AI keyword trends
                    all_keywords = []
                    for article in all_articles:
                        if article.get('ai_keywords'):
                            all_keywords.extend(article['ai_keywords'])
                    
                    if all_keywords:
                        keyword_counts = Counter(all_keywords)
                        top_keywords = dict(keyword_counts.most_common(10))
                        
                        fig_keywords = px.bar(
                            x=list(top_keywords.values()),
                            y=list(top_keywords.keys()),
                            orientation='h',
                            title="Trending AI/ML Keywords",
                            color=list(top_keywords.values()),
                            color_continuous_scale="plasma"
                        )
                        st.plotly_chart(fig_keywords, use_container_width=True)
    
    # Footer with enhanced signature
    st.markdown('''
    <div class="footer-signature">
        <h3>💼 About the Developer</h3>
        <p style="font-size: 1.1rem; margin-bottom: 1.5rem;">
            This AI News Automator showcases advanced web development, API integration, 
            and AI-powered content analysis capabilities.
        </p>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 1rem; margin: 1.5rem 0;">
            <div>
                <h4>👨‍💻 Teslim Uthman Adeyanju</h4>
                <p>Full-Stack Developer & AI Enthusiast</p>
            </div>
            <div>
                <h4>📧 Contact</h4>
                <p><a href="mailto:info@adeyanjuteslim.co.uk" style="color: #4ecdc4;">info@adeyanjuteslim.co.uk</a></p>
            </div>
            <div>
                <h4>🔗 Connect</h4>
                <p><a href="https://linkedin.com/in/adeyanjuteslimuthman" style="color: #4ecdc4;">LinkedIn Profile</a></p>
            </div>
            <div>
                <h4>🌐 Portfolio</h4>
                <p><a href="https://adeyanjuteslim.co.uk" style="color: #4ecdc4;">adeyanjuteslim.co.uk</a></p>
            </div>
        </div>
        <p style="margin-top: 2rem; padding-top: 1rem; border-top: 1px solid rgba(255,255,255,0.2);">
            🤖 Built with Python, Streamlit & News API | Featuring AI-powered content analysis
        </p>
    </div>
    ''', unsafe_allow_html=True)


if __name__ == "__main__":
    main()