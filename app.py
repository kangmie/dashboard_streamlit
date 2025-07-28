import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import warnings
warnings.filterwarnings('ignore')

# Import modules
from data_analyzer import SalesDataAnalyzer
from chatbot import GroqChatbot
from pdf_exporter import PDFExporter

# Konfigurasi halaman
st.set_page_config(
    page_title="📊 Sales Menu COGS Analytics Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS untuk styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        text-align: center;
        background: linear-gradient(90deg, #ff6b6b, #4ecdc4);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 2rem;
    }
    
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin: 0.5rem 0;
    }
    
    .insight-box {
        background: #f8f9fa;
        border-left: 4px solid #28a745;
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 5px;
    }
    
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
    }
</style>
""", unsafe_allow_html=True)

# Header utama
st.markdown('<h1 class="main-header">📊 Sales Menu COGS Analytics Dashboard</h1>', unsafe_allow_html=True)

def main():
    # Sidebar untuk upload file dan konfigurasi
    with st.sidebar:
        st.markdown("### 🔧 Konfigurasi Analisis")
        
        # Upload file
        uploaded_file = st.file_uploader(
            "📁 Upload File Excel Sales Data",
            type=['xlsx', 'xls'],
            help="Upload file Excel yang berisi data sales menu COGS report"
        )
        
        if uploaded_file is not None:
            # Load data
            try:
                analyzer = SalesDataAnalyzer(uploaded_file)
                st.success("✅ File berhasil dimuat!")
                
                # Info data
                st.markdown("#### 📋 Informasi Data")
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Total Transaksi", f"{analyzer.total_records:,}")
                with col2:
                    st.metric("Periode Data", f"{analyzer.get_date_range()}")
                
                # Filter data
                st.markdown("#### 🔍 Filter Data")
                
                # Filter tanggal
                date_range = st.date_input(
                    "Pilih Rentang Tanggal",
                    value=(analyzer.min_date.date(), analyzer.max_date.date()),
                    min_value=analyzer.min_date.date(),
                    max_value=analyzer.max_date.date()
                )
                
                # Filter kategori menu
                categories = st.multiselect(
                    "Pilih Kategori Menu",
                    options=analyzer.get_unique_categories(),
                    default=analyzer.get_unique_categories()
                )
                
                # Filter cabang (jika ada lebih dari satu)
                branches = analyzer.get_unique_branches()
                if len(branches) > 1:
                    selected_branch = st.selectbox("Pilih Cabang", branches)
                else:
                    selected_branch = branches[0] if branches else None
                
                # Apply filters
                filtered_data = analyzer.apply_filters(date_range, categories, selected_branch)
                
            except Exception as e:
                st.error(f"❌ Error loading file: {str(e)}")
                return
        else:
            st.info("👆 Silahkan upload file Excel untuk memulai analisis")
            return
    
    # Main content area
    if uploaded_file is not None and 'analyzer' in locals():
        
        # Tab layout
        tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
            "📈 Overview", "🎯 Analisis Profitabilitas", "📊 Analisis Menu", 
            "⏰ Analisis Temporal", "💰 Analisis COGS", "🤖 Chat AI"
        ])
        
        with tab1:
            display_overview(analyzer, filtered_data)
        
        with tab2:
            display_profitability_analysis(analyzer, filtered_data)
        
        with tab3:
            display_menu_analysis(analyzer, filtered_data)
        
        with tab4:
            display_temporal_analysis(analyzer, filtered_data)
        
        with tab5:
            display_cogs_analysis(analyzer, filtered_data)
        
        with tab6:
            display_chatbot(analyzer, filtered_data)
        
        # Export button
        st.markdown("---")
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            if st.button("📄 Export Laporan PDF", use_container_width=True):
                pdf_exporter = PDFExporter(analyzer, filtered_data)
                pdf_buffer = pdf_exporter.generate_report()
                
                st.download_button(
                    label="💾 Download PDF Report",
                    data=pdf_buffer.getvalue(),
                    file_name=f"sales_cogs_report_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )

def display_overview(analyzer, data):
    st.markdown("## 📈 Ringkasan Eksekutif")
    
    # Key metrics dalam cards
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_revenue = data['Total'].sum()
        st.markdown(f"""
        <div class="metric-card">
            <h3>💰 Total Revenue</h3>
            <h2>Rp {total_revenue:,.0f}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        total_cogs = data['COGS Total'].sum()
        st.markdown(f"""
        <div class="metric-card">
            <h3>📦 Total COGS</h3>
            <h2>Rp {total_cogs:,.0f}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        total_margin = data['Margin'].sum()
        st.markdown(f"""
        <div class="metric-card">
            <h3>📊 Total Margin</h3>
            <h2>Rp {total_margin:,.0f}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        avg_margin_pct = (total_margin / total_revenue) * 100 if total_revenue > 0 else 0
        st.markdown(f"""
        <div class="metric-card">
            <h3>📈 Margin %</h3>
            <h2>{avg_margin_pct:.1f}%</h2>
        </div>
        """, unsafe_allow_html=True)
    
    # # Insight boxes
    # st.markdown("### 🔍 Insight Utama")
    
    # col1, col2 = st.columns(2)
    
    # with col1:
    #     # Top performing menu
    #     top_menu = analyzer.get_top_performing_menus(data, 5)
    #     st.markdown(f"""
    #     <div class="insight-box">
    #         <h4>🏆 Menu Terlaris</h4>
    #         <p><strong>{top_menu.iloc[0]['Menu']}</strong></p>
    #         <p>Total Terjual: {top_menu.iloc[0]['Total_Qty']} unit</p>
    #         <p>Revenue: Rp {top_menu.iloc[0]['Total_Revenue']:,.0f}</p>
    #     </div>
    #     """, unsafe_allow_html=True)
    
    # with col2:
    #     # Most profitable menu
    #     most_profitable = analyzer.get_most_profitable_menus(data, 5)
    #     st.markdown(f"""
    #     <div class="insight-box">
    #         <h4>💎 Menu Paling Menguntungkan</h4>
    #         <p><strong>{most_profitable.iloc[0]['Menu']}</strong></p>
    #         <p>Margin per Unit: Rp {most_profitable.iloc[0]['Avg_Margin']:.0f}</p>
    #         <p>Margin %: {most_profitable.iloc[0]['Margin_Percentage']:.1f}%</p>
    #     </div>
    #     """, unsafe_allow_html=True)
    
    # Insight boxes
    st.markdown("### 🔍 Insight Utama")

    col1, col2 = st.columns(2)

    with col1:
        # Top performing menu
        top_menu = analyzer.get_top_performing_menus(data, 5)
        st.markdown(f"""
        <div class="insight-box">
            <h4 style="color: black;">🏆 Menu Terlaris</h4>
            <p style="color: black;"><strong style="color: black;">{top_menu.iloc[0]['Menu']}</strong></p>
            <p style="color: black;">Total Terjual: {top_menu.iloc[0]['Total_Qty']} unit</p>
            <p style="color: black;">Revenue: Rp {top_menu.iloc[0]['Total_Revenue']:,.0f}</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        # Most profitable menu
        most_profitable = analyzer.get_most_profitable_menus(data, 5)
        st.markdown(f"""
        <div class="insight-box">
            <h4 style="color: black;">💎 Menu Paling Menguntungkan</h4>
            <p style="color: black;"><strong style="color: black;">{most_profitable.iloc[0]['Menu']}</strong></p>
            <p style="color: black;">Margin per Unit: Rp {most_profitable.iloc[0]['Avg_Margin']:.0f}</p>
            <p style="color: black;">Margin %: {most_profitable.iloc[0]['Margin_Percentage']:.1f}%</p>
        </div>
        """, unsafe_allow_html=True)

    # Charts overview
    col1, col2 = st.columns(2)
    
    with col1:
        # Revenue by category
        category_revenue = data.groupby('Menu Category')['Total'].sum().reset_index()
        fig = px.pie(
            category_revenue, 
            values='Total', 
            names='Menu Category',
            title="📊 Distribusi Revenue per Kategori",
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        fig.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Daily sales trend
        daily_sales = analyzer.get_daily_sales_trend(data)
        fig = px.line(
            daily_sales, 
            x='Sales Date', 
            y='Daily_Revenue',
            title="📈 Tren Penjualan Harian",
            line_shape='spline'
        )
        fig.update_layout(
            xaxis_title="Tanggal",
            yaxis_title="Revenue (Rp)",
            hovermode='x unified'
        )
        st.plotly_chart(fig, use_container_width=True)

def display_profitability_analysis(analyzer, data):
    st.markdown("## 🎯 Analisis Profitabilitas Mendalam")
    
    # Profitability metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        avg_cogs_pct = data['COGS Total (%)'].mean()
        st.metric("📦 Rata-rata COGS %", f"{avg_cogs_pct:.1f}%")
    
    with col2:
        gross_margin = ((data['Total'].sum() - data['COGS Total'].sum()) / data['Total'].sum()) * 100
        st.metric("📊 Gross Margin %", f"{gross_margin:.1f}%")
    
    with col3:
        avg_transaction = data['Total'].mean()
        st.metric("💰 Rata-rata Transaksi", f"Rp {avg_transaction:,.0f}")
    
    # Profitability analysis charts
    col1, col2 = st.columns(2)
    
    with col1:
        # Menu profitability scatter plot
        menu_profit = analyzer.get_menu_profitability_analysis(data)
        fig = px.scatter(
            menu_profit,
            x='Avg_COGS_Pct',
            y='Total_Margin',
            size='Total_Qty',
            color='Menu Category',
            hover_data=['Menu'],
            title="🎯 Analisis Profitabilitas Menu",
            labels={'Avg_COGS_Pct': 'COGS % Rata-rata', 'Total_Margin': 'Total Margin (Rp)'}
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Top profitable menus
        top_profitable = analyzer.get_most_profitable_menus(data, 10)
        fig = px.bar(
            top_profitable,
            x='Avg_Margin',
            y='Menu',
            orientation='h',
            title="💎 Top 10 Menu Paling Menguntungkan",
            color='Margin_Percentage',
            color_continuous_scale='Viridis'
        )
        fig.update_layout(yaxis={'categoryorder': 'total ascending'})
        st.plotly_chart(fig, use_container_width=True)
    
    # COGS distribution analysis
    st.markdown("### 📦 Analisis Distribusi COGS")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # COGS percentage distribution
        fig = px.histogram(
            data,
            x='COGS Total (%)',
            nbins=20,
            title="📊 Distribusi COGS Percentage",
            labels={'COGS Total (%)': 'COGS %', 'count': 'Frekuensi'}
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Category-wise COGS analysis
        cogs_by_category = data.groupby('Menu Category').agg({
            'COGS Total (%)': 'mean',
            'Total': 'sum'
        }).reset_index()
        
        fig = px.bar(
            cogs_by_category,
            x='Menu Category',
            y='COGS Total (%)',
            title="📦 Rata-rata COGS % per Kategori",
            color='Total',
            color_continuous_scale='RdYlBu_r'
        )
        st.plotly_chart(fig, use_container_width=True)

def display_menu_analysis(analyzer, data):
    st.markdown("## 📊 Analisis Menu Mendalam")
    
    # Menu performance metrics
    menu_performance = analyzer.get_comprehensive_menu_analysis(data)
    
    # Top performers table
    st.markdown("### 🏆 Top Performing Menus")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 📈 Berdasarkan Volume Penjualan")
        top_volume = menu_performance.nlargest(10, 'Total_Qty')[['Menu', 'Total_Qty', 'Total_Revenue', 'Avg_Margin']]
        st.dataframe(top_volume, use_container_width=True)
    
    with col2:
        st.markdown("#### 💰 Berdasarkan Revenue")
        top_revenue = menu_performance.nlargest(10, 'Total_Revenue')[['Menu', 'Total_Revenue', 'Total_Qty', 'Margin_Percentage']]
        st.dataframe(top_revenue, use_container_width=True)
    
    # Menu analysis charts
    col1, col2 = st.columns(2)
    
    with col1:
        # Menu category performance
        category_performance = data.groupby('Menu Category').agg({
            'Qty': 'sum',
            'Total': 'sum',
            'Margin': 'sum'
        }).reset_index()
        
        fig = px.bar(
            category_performance,
            x='Menu Category',
            y=['Total', 'Margin'],
            title="📊 Performa Kategori Menu",
            barmode='group'
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Price vs Quantity correlation
        fig = px.scatter(
            data,
            x='Price',
            y='Qty',
            color='Menu Category',
            title="💰 Korelasi Harga vs Kuantitas",
            hover_data=['Menu']
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Menu detail analysis
    st.markdown("### 🔍 Analisis Detail Menu")
    
    # Menu selector
    selected_menu = st.selectbox(
        "Pilih menu untuk analisis detail:",
        options=data['Menu'].unique()
    )
    
    if selected_menu:
        menu_data = data[data['Menu'] == selected_menu]
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("📦 Total Terjual", f"{menu_data['Qty'].sum()} unit")
        
        with col2:
            st.metric("💰 Total Revenue", f"Rp {menu_data['Total'].sum():,.0f}")
        
        with col3:
            st.metric("📊 Rata-rata COGS %", f"{menu_data['COGS Total (%)'].mean():.1f}%")
        
        with col4:
            st.metric("💎 Total Margin", f"Rp {menu_data['Margin'].sum():,.0f}")
        
        # Menu trend
        menu_daily = menu_data.groupby(menu_data['Sales Date'].dt.date).agg({
            'Qty': 'sum',
            'Total': 'sum'
        }).reset_index()
        
        fig = px.line(
            menu_daily,
            x='Sales Date',
            y=['Qty', 'Total'],
            title=f"📈 Tren Penjualan {selected_menu}",
            labels={'value': 'Nilai', 'Sales Date': 'Tanggal'}
        )
        st.plotly_chart(fig, use_container_width=True)

def display_temporal_analysis(analyzer, data):
    st.markdown("## ⏰ Analisis Temporal")
    
    # Time-based analysis
    col1, col2 = st.columns(2)
    
    with col1:
        # Hourly sales pattern
        hourly_sales = analyzer.get_hourly_sales_pattern(data)
        fig = px.bar(
            hourly_sales,
            x='Hour',
            y='Total_Revenue',
            title="🕐 Pola Penjualan per Jam",
            color='Total_Revenue',
            color_continuous_scale='Viridis'
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Daily sales pattern
        daily_pattern = analyzer.get_daily_sales_pattern(data)
        fig = px.bar(
            daily_pattern,
            x='Day_Name',
            y='Avg_Revenue',
            title="📅 Pola Penjualan per Hari",
            color='Avg_Revenue',
            color_continuous_scale='Plasma'
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Weekly and monthly trends
    col1, col2 = st.columns(2)
    
    with col1:
        # Weekly trend
        weekly_trend = analyzer.get_weekly_trend(data)
        fig = px.line(
            weekly_trend,
            x='Week',
            y='Weekly_Revenue',
            title="📊 Tren Penjualan Mingguan",
            markers=True
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Sales heatmap by hour and day
        heatmap_data = analyzer.get_sales_heatmap_data(data)
        fig = px.imshow(
            heatmap_data,
            title="🔥 Heatmap Penjualan (Jam vs Hari)",
            aspect="auto",
            color_continuous_scale='YlOrRd'
        )
        st.plotly_chart(fig, use_container_width=True)

def display_cogs_analysis(analyzer, data):
    st.markdown("## 💰 Analisis COGS Mendalam")
    
    # COGS overview
    col1, col2, col3 = st.columns(3)
    
    with col1:
        total_cogs = data['COGS Total'].sum()
        st.metric("📦 Total COGS", f"Rp {total_cogs:,.0f}")
    
    with col2:
        avg_cogs_pct = data['COGS Total (%)'].mean()
        st.metric("📊 Rata-rata COGS %", f"{avg_cogs_pct:.1f}%")
    
    with col3:
        cogs_efficiency = analyzer.calculate_cogs_efficiency(data)
        st.metric("⚡ Efisiensi COGS", f"{cogs_efficiency:.1f}%")
    
    # COGS analysis charts
    col1, col2 = st.columns(2)
    
    with col1:
        # COGS by menu category
        cogs_by_category = data.groupby('Menu Category').agg({
            'COGS Total': 'sum',
            'COGS Total (%)': 'mean'
        }).reset_index()
        
        fig = px.treemap(
            cogs_by_category,
            path=['Menu Category'],
            values='COGS Total',
            color='COGS Total (%)',
            title="🌳 COGS per Kategori (Treemap)",
            color_continuous_scale='RdYlBu_r'
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # COGS trend over time
        cogs_trend = analyzer.get_cogs_trend(data)
        fig = px.line(
            cogs_trend,
            x='Sales Date',
            y=['Daily_COGS', 'Daily_Revenue'],
            title="📈 Tren COGS vs Revenue Harian"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # High/Low COGS analysis
    st.markdown("### 🔍 Analisis Menu dengan COGS Tinggi/Rendah")
    
    col1, col2 = st.columns(2)
    
    with col1:
        high_cogs = analyzer.get_high_cogs_menus(data, 10)
        st.markdown("#### ⚠️ Menu dengan COGS Tinggi")
        st.dataframe(high_cogs, use_container_width=True)
    
    with col2:
        low_cogs = analyzer.get_low_cogs_menus(data, 10)
        st.markdown("#### ✅ Menu dengan COGS Rendah")
        st.dataframe(low_cogs, use_container_width=True)
    
    # COGS optimization recommendations
    st.markdown("### 💡 Rekomendasi Optimasi COGS")
    recommendations = analyzer.get_cogs_optimization_recommendations(data)
    
    for i, rec in enumerate(recommendations, 1):
        st.markdown(f"""
        <div class="insight-box">
            <h4>{i}. {rec['title']}</h4>
            <p>{rec['description']}</p>
            <p><strong>Potensi Penghematan:</strong> {rec['potential_saving']}</p>
        </div>
        """, unsafe_allow_html=True)

def display_chatbot(analyzer, data):
    st.markdown("## 🤖 Chat dengan AI Data Analyst")
    
    # Initialize chatbot
    if 'chatbot' not in st.session_state:
        st.session_state.chatbot = GroqChatbot()
    
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    
    # Chat interface
    st.markdown("### 💬 Tanya AI tentang Data Anda")
    
    # Display chat history
    for message in st.session_state.chat_history:
        if message['role'] == 'user':
            st.markdown(f"**🧑‍💼 Anda:** {message['content']}")
        else:
            st.markdown(f"**🤖 AI Analyst:** {message['content']}")
    
    # Input for new question
    user_question = st.text_input(
        "Tanyakan sesuatu tentang data penjualan Anda:",
        placeholder="Contoh: Berapa total penjualan bulan ini? Menu mana yang paling menguntungkan?"
    )
    
    if st.button("🚀 Kirim Pertanyaan") and user_question:
        # Add user message to history
        st.session_state.chat_history.append({
            'role': 'user',
            'content': user_question
        })
        
        # Get response from AI
        with st.spinner("🤔 AI sedang menganalisis data..."):
            try:
                # Prepare data context for AI
                data_context = analyzer.prepare_data_summary_for_ai(data)
                ai_response = st.session_state.chatbot.get_response(user_question, data_context)
                
                # Add AI response to history
                st.session_state.chat_history.append({
                    'role': 'assistant',
                    'content': ai_response
                })
                
                # Rerun to update chat display
                st.rerun()
                
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
    
    # Suggested questions
    st.markdown("### 💡 Pertanyaan yang Disarankan")
    
    suggested_questions = [
        "Berapa total revenue dan margin bulan ini?",
        "Menu mana yang memiliki COGS paling tinggi?",
        "Apa tren penjualan dalam 7 hari terakhir?",
        "Kategori menu mana yang paling menguntungkan?",
        "Berikan rekomendasi untuk meningkatkan profitabilitas",
        "Analisis performa menu terlaris vs margin tertinggi",
        "Kapan waktu penjualan paling ramai?",
        "Menu mana yang perlu dioptimasi COGS-nya?"
    ]
    
    cols = st.columns(2)
    for i, question in enumerate(suggested_questions):
        col = cols[i % 2]
        if col.button(f"💭 {question}", key=f"suggested_{i}"):
            # Add to chat and get response
            st.session_state.chat_history.append({
                'role': 'user',
                'content': question
            })
            
            with st.spinner("🤔 AI sedang menganalisis data..."):
                try:
                    data_context = analyzer.prepare_data_summary_for_ai(data)
                    ai_response = st.session_state.chatbot.get_response(question, data_context)
                    
                    st.session_state.chat_history.append({
                        'role': 'assistant',
                        'content': ai_response
                    })
                    
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
    
    # Clear chat button
    if st.button("🗑️ Hapus Riwayat Chat"):
        st.session_state.chat_history = []
        st.rerun()

if __name__ == "__main__":
    main()