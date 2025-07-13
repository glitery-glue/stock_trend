# streamlit_app.py
import sys
import pandas as pd
import streamlit as st
from src.predict import Predict
from src.get_reddit_data import YfData
from src.logger import logging
from src.exception import CustomException


# Initialize analyzers
sentiment_result = Predict()
stock_data = YfData()

# Streamlit page title
st.title("Reddit Stock Sentiment Analyzer")

# User Inputs
stock_symbol = st.text_input("Enter Stock Symbol (e.g., AAPL, TCS):").upper()
stock_type = st.selectbox("Select Stock Type:", ["US", "India"])

# Submit button
if st.button("🔍 Analyze", type="primary"):
    if stock_symbol:
        try:
            # Show progress
            with st.spinner("Analyzing sentiment... This may take a moment."):
                # Get sentiment analysis result
                result = sentiment_result.predict(stock_symbol, stock_type)
                
                # Get stock data
                stock_info = stock_data.get_yf_data(stock_symbol)

            # Display results
            st.success("✅ Sentiment analysis completed successfully!")
            
            # Extract data safely
            sentiment_data = result.get('Sentiment', {})
            symbol = result.get('stock_symbol', stock_symbol)
            
            # Main results section
            st.markdown(f"## 📊 Sentiment Analysis Summary for `{symbol}`")
            
            # Create metrics columns
            col1, col2, col3 = st.columns(3)
            
            with col1:
                sentiment_score = sentiment_data.get('Sentiment', 0) if isinstance(sentiment_data, dict) else result.get('Sentiment', 0)
                st.metric("Overall Sentiment Score", f"{sentiment_score:.4f}")
            
            with col2:
                tendency = result.get('Tendency', {})
                if tendency:
                    main_tendency = list(tendency.keys())[0].title()
                    tendency_count = list(tendency.values())[0]
                    st.metric("General Tendency", f"{main_tendency} ({tendency_count} posts)")
                else:
                    st.metric("General Tendency", "N/A")
            
            with col3:
                post_count = result.get('post count', 0)
                st.metric("Total Posts Analyzed", post_count)
            
            # Trend analysis section
            trend_data = result.get('Trend', {})
            if trend_data:
                st.subheader("📈 Trend Analysis")
                
                trend_col1, trend_col2 = st.columns(2)
                
                with trend_col1:
                    current_sentiment = trend_data.get('current_sentiment', 0)
                    st.metric("Current Sentiment", f"{current_sentiment:.4f}")
                
                with trend_col2:
                    trend_direction = trend_data.get('trend', 'N/A')
                    st.metric("Trend Direction", trend_direction)
                
                # Moving average data (if available)
                moving_avg = trend_data.get('moving_avg')
                if moving_avg is not None and len(moving_avg) > 0:
                    st.subheader("📊 Sentiment Trend Chart")
                    try:
                        # Create a simple line chart
                        chart_data = pd.DataFrame({
                            'Moving Average': moving_avg
                        })
                        st.line_chart(chart_data)
                    except Exception as chart_error:
                        st.warning(f"Could not display trend chart: {chart_error}")
            
            # Top posts section
            top_posts = result.get('Top Post', [])
            if top_posts:
                st.subheader("🔥 Top Reddit Posts")
                
                try:
                    # Convert to DataFrame
                    posts_df = pd.DataFrame(top_posts)
                    
                    # Ensure required columns exist
                    required_columns = ['title', 'score', 'sentiment', 'subreddit']
                    for col in required_columns:
                        if col not in posts_df.columns:
                            posts_df[col] = 'N/A'
                    
                    # Select and reorder columns
                    display_columns = ['title', 'score', 'sentiment', 'subreddit']
                    posts_df = posts_df[display_columns]
                    
                    # Format columns
                    posts_df['score'] = posts_df['score'].astype(str)
                    posts_df['sentiment'] = pd.to_numeric(posts_df['sentiment'], errors='coerce').round(4)
                    
                    # Rename columns for better display
                    posts_df.columns = ['Title', 'Score', 'Sentiment', 'Subreddit']
                    
                    # Display as interactive table
                    st.dataframe(
                        posts_df,
                        use_container_width=True,
                        hide_index=True,
                        column_config={
                            "Title": st.column_config.TextColumn(
                                "Title",
                                width="large",
                            ),
                            "Score": st.column_config.NumberColumn(
                                "Score",
                                help="Reddit post score",
                                format="%d",
                            ),
                            "Sentiment": st.column_config.NumberColumn(
                                "Sentiment",
                                help="Sentiment score",
                                format="%.4f",
                            ),
                            "Subreddit": st.column_config.TextColumn(
                                "Subreddit",
                                width="medium",
                            ),
                        }
                    )
                    
                    # If URLs are available, show them as expandable section
                    if 'url' in pd.DataFrame(top_posts).columns:
                        with st.expander("🔗 View Post URLs"):
                            url_df = pd.DataFrame(top_posts)[['title', 'url']]
                            for idx, row in url_df.iterrows():
                                st.markdown(f"**{row['title'][:50]}...** - [{row['url']}]({row['url']})")
                
                except Exception as posts_error:
                    st.error(f"Error displaying top posts: {posts_error}")
                    # Fallback display
                    st.json(top_posts)
            else:
                st.info("No top posts available to display.")
            
            # Stock data section
            if stock_info:
                st.subheader("📈 Stock Information")
                
                if isinstance(stock_info, dict):
                    # Display stock info in columns
                    info_items = list(stock_info.items())
                    
                    # Create columns for stock info
                    num_cols = min(3, len(info_items))
                    if num_cols > 0:
                        cols = st.columns(num_cols)
                        
                        for i, (key, value) in enumerate(info_items):
                            col_idx = i % num_cols
                            with cols[col_idx]:
                                st.metric(key.replace('_', ' ').title(), str(value))
                
                elif isinstance(stock_info, pd.DataFrame):
                    st.dataframe(stock_info, use_container_width=True)
                else:
                    st.write(stock_info)
            else:
                st.warning("⚠️ Stock data could not be retrieved.")
            
        except Exception as e:
            st.error(f"❌ An error occurred during analysis: {str(e)}")
            logging.error(f"Analysis error: {e}")
            
            # Show error details in expander for debugging
            with st.expander("🔍 Error Details (for debugging)"):
                st.code(str(e))
                
    else:
        st.warning("⚠️ Please enter a valid stock symbol.")

# Sidebar with additional information
with st.sidebar:
    st.markdown("## ℹ️ About")
    st.markdown("""
    This app analyzes Reddit sentiment for stock symbols using:
    - Reddit post analysis
    - Sentiment scoring
    - Trend analysis
    - Top post identification
    """)
    
    st.markdown("## 📊 Sentiment Scale")
    st.markdown("""
    - **Positive**: > 0.1
    - **Neutral**: -0.1 to 0.1  
    - **Negative**: < -0.1
    """)
    
    st.markdown("## 🔧 Tips")
    st.markdown("""
    - Use standard stock symbols (AAPL, TSLA, etc.)
    - Analysis may take 30-60 seconds
    - Results based on recent Reddit posts
    """)