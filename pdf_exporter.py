import io
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics.charts.piecharts import Pie
from reportlab.lib.colors import HexColor
import base64
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

class PDFExporter:
    """
    Class untuk mengexport laporan analisis sales ke format PDF.
    
    Fitur:
    - Export comprehensive sales report
    - Include charts dan visualizations
    - Professional formatting
    - Summary executive dan detailed analysis
    """
    
    def __init__(self, analyzer, data):
        """
        Inisialisasi PDF exporter.
        
        Args:
            analyzer: Instance SalesDataAnalyzer
            data: DataFrame yang sudah difilter
        """
        self.analyzer = analyzer
        self.data = data
        self.doc_buffer = io.BytesIO()
        self.styles = getSampleStyleSheet()
        
        # Custom styles
        self.title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            alignment=1,  # Center alignment
            textColor=HexColor('#2E86AB')
        )
        
        self.heading_style = ParagraphStyle(
            'CustomHeading',
            parent=self.styles['Heading2'],
            fontSize=16,
            spaceAfter=12,
            textColor=HexColor('#A23B72'),
            borderWidth=1,
            borderColor=HexColor('#A23B72'),
            borderPadding=5
        )
        
        self.subheading_style = ParagraphStyle(
            'CustomSubHeading',
            parent=self.styles['Heading3'],
            fontSize=14,
            spaceAfter=8,
            textColor=HexColor('#F18F01')
        )
        
        self.body_style = ParagraphStyle(
            'CustomBody',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceAfter=6
        )
        
        self.metric_style = ParagraphStyle(
            'MetricStyle',
            parent=self.styles['Normal'],
            fontSize=12,
            textColor=HexColor('#2E86AB'),
            alignment=1,
            spaceAfter=10
        )
    
    def generate_report(self):
        """
        Generate comprehensive PDF report.
        
        Returns:
            io.BytesIO: Buffer containing PDF data
        """
        # Create document
        doc = SimpleDocTemplate(
            self.doc_buffer,
            pagesize=A4,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72
        )
        
        # Build story (content)
        story = []
        
        # Title page
        story.extend(self._create_title_page())
        story.append(PageBreak())
        
        # Executive summary
        story.extend(self._create_executive_summary())
        story.append(PageBreak())
        
        # Financial analysis
        story.extend(self._create_financial_analysis())
        story.append(PageBreak())
        
        # Menu performance analysis
        story.extend(self._create_menu_analysis())
        story.append(PageBreak())
        
        # COGS analysis
        story.extend(self._create_cogs_analysis())
        story.append(PageBreak())
        
        # Recommendations
        story.extend(self._create_recommendations())
        
        # Build PDF
        doc.build(story)
        
        # Return buffer
        self.doc_buffer.seek(0)
        return self.doc_buffer
    
    def _create_title_page(self):
        """Create title page content."""
        story = []
        
        # Title
        story.append(Paragraph("📊 SALES MENU COGS", self.title_style))
        story.append(Paragraph("ANALYTICS REPORT", self.title_style))
        story.append(Spacer(1, 50))
        
        # Restaurant info
        if 'Branch' in self.data.columns and not self.data['Branch'].empty:
            branch_name = self.data['Branch'].iloc[0]
            story.append(Paragraph(f"<b>{branch_name}</b>", self.heading_style))
        
        story.append(Spacer(1, 30))
        
        # Period info
        period = self.analyzer.get_date_range()
        story.append(Paragraph(f"<b>Periode Analisis:</b> {period}", self.subheading_style))
        
        # Generation info
        generated_date = datetime.now().strftime("%d %B %Y, %H:%M")
        story.append(Paragraph(f"<b>Tanggal Generate:</b> {generated_date}", self.subheading_style))
        
        story.append(Spacer(1, 50))
        
        # Key metrics overview
        total_revenue = self.data['Total'].sum()
        total_margin = self.data['Margin'].sum()
        total_transactions = len(self.data)
        avg_cogs_pct = self.data['COGS Total (%)'].mean()
        
        metrics_data = [
            ['Metric', 'Nilai'],
            ['Total Revenue', f'Rp {total_revenue:,.0f}'],
            ['Total Margin', f'Rp {total_margin:,.0f}'],
            ['Gross Margin %', f'{(total_margin/total_revenue*100):.1f}%'],
            ['Total Transaksi', f'{total_transactions:,}'],
            ['Rata-rata COGS %', f'{avg_cogs_pct:.1f}%']
        ]
        
        metrics_table = Table(metrics_data, colWidths=[2*inch, 2*inch])
        metrics_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), HexColor('#2E86AB')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), HexColor('#F8F9FA')),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(Paragraph("<b>Key Metrics Overview</b>", self.heading_style))
        story.append(metrics_table)
        
        return story
    
    def _create_executive_summary(self):
        """Create executive summary section."""
        story = []
        
        story.append(Paragraph("📋 RINGKASAN EKSEKUTIF", self.heading_style))
        
        # Calculate key insights
        total_revenue = self.data['Total'].sum()
        total_margin = self.data['Margin'].sum()
        gross_margin_pct = (total_margin / total_revenue) * 100
        avg_cogs_pct = self.data['COGS Total (%)'].mean()
        
        # Top performing menu
        top_menu = self.analyzer.get_top_performing_menus(self.data, 1)
        most_profitable = self.analyzer.get_most_profitable_menus(self.data, 1)
        
        # Summary text
        summary_text = f"""
        <b>Performa Bisnis Periode {self.analyzer.get_date_range()}</b><br/><br/>
        
        Analisis menunjukkan total revenue sebesar Rp {total_revenue:,.0f} dengan gross margin {gross_margin_pct:.1f}%. 
        Rata-rata COGS sebesar {avg_cogs_pct:.1f}% menunjukkan {'efisiensi yang baik' if avg_cogs_pct < 30 else 'area yang perlu optimasi'}.<br/><br/>
        
        <b>Highlight Utama:</b><br/>
        • Menu terlaris: {top_menu.iloc[0]['Menu'] if not top_menu.empty else 'N/A'} 
        ({top_menu.iloc[0]['Total_Qty'] if not top_menu.empty else 0} unit terjual)<br/>
        • Menu paling menguntungkan: {most_profitable.iloc[0]['Menu'] if not most_profitable.empty else 'N/A'} 
        (margin {most_profitable.iloc[0]['Margin_Percentage'] if not most_profitable.empty else 0:.1f}%)<br/>
        • Kategori terkuat: {self._get_top_category()}<br/><br/>
        
        <b>Area Fokus:</b><br/>
        • {'Optimasi COGS untuk meningkatkan margin' if avg_cogs_pct > 25 else 'Mempertahankan efisiensi COGS'}<br/>
        • Pengembangan menu dengan performa tinggi<br/>
        • Analisis pricing strategy untuk menu underperform
        """
        
        story.append(Paragraph(summary_text, self.body_style))
        story.append(Spacer(1, 20))
        
        return story
    
    def _create_financial_analysis(self):
        """Create financial analysis section."""
        story = []
        
        story.append(Paragraph("💰 ANALISIS FINANSIAL", self.heading_style))
        
        # Revenue breakdown by category
        category_revenue = self.data.groupby('Menu Category').agg({
            'Total': 'sum',
            'Margin': 'sum',
            'COGS Total': 'sum',
            'Qty': 'sum'
        }).reset_index()
        
        category_revenue['Margin_Pct'] = (category_revenue['Margin'] / category_revenue['Total']) * 100
        category_revenue['COGS_Pct'] = (category_revenue['COGS Total'] / category_revenue['Total']) * 100
        
        # Create table
        table_data = [['Kategori', 'Revenue (Rp)', 'Margin (%)', 'COGS (%)', 'Qty Terjual']]
        
        for _, row in category_revenue.iterrows():
            table_data.append([
                row['Menu Category'],
                f"{row['Total']:,.0f}",
                f"{row['Margin_Pct']:.1f}%",
                f"{row['COGS_Pct']:.1f}%",
                f"{row['Qty']:,.0f}"
            ])
        
        # Add total row
        total_revenue = self.data['Total'].sum()
        total_margin = self.data['Margin'].sum()
        total_cogs = self.data['COGS Total'].sum()
        total_qty = self.data['Qty'].sum()
        
        table_data.append([
            'TOTAL',
            f"{total_revenue:,.0f}",
            f"{(total_margin/total_revenue*100):.1f}%",
            f"{(total_cogs/total_revenue*100):.1f}%",
            f"{total_qty:,.0f}"
        ])
        
        revenue_table = Table(table_data, colWidths=[1.5*inch, 1.2*inch, 0.8*inch, 0.8*inch, 1*inch])
        revenue_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), HexColor('#2E86AB')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BACKGROUND', (0, -1), (-1, -1), HexColor('#A23B72')),
            ('TEXTCOLOR', (0, -1), (-1, -1), colors.whitesmoke),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(Paragraph("Revenue dan Margin per Kategori", self.subheading_style))
        story.append(revenue_table)
        story.append(Spacer(1, 20))
        
        # Daily performance trend
        daily_trend = self.analyzer.get_daily_sales_trend(self.data)
        
        story.append(Paragraph("Tren Performa Harian", self.subheading_style))
        
        # Performance insights
        avg_daily_revenue = daily_trend['Daily_Revenue'].mean()
        best_day_revenue = daily_trend['Daily_Revenue'].max()
        worst_day_revenue = daily_trend['Daily_Revenue'].min()
        
        performance_text = f"""
        <b>Analisis Performa Harian:</b><br/>
        • Rata-rata revenue harian: Rp {avg_daily_revenue:,.0f}<br/>
        • Revenue tertinggi: Rp {best_day_revenue:,.0f}<br/>
        • Revenue terendah: Rp {worst_day_revenue:,.0f}<br/>
        • Volatilitas: {((best_day_revenue - worst_day_revenue) / avg_daily_revenue * 100):.1f}%<br/>
        """
        
        story.append(Paragraph(performance_text, self.body_style))
        
        return story
    
    def _create_menu_analysis(self):
        """Create menu performance analysis section."""
        story = []
        
        story.append(Paragraph("🍜 ANALISIS PERFORMA MENU", self.heading_style))
        
        # Top performing menus
        story.append(Paragraph("Top 10 Menu Terlaris", self.subheading_style))
        
        top_menus = self.analyzer.get_top_performing_menus(self.data, 10)
        
        menu_table_data = [['Rank', 'Menu', 'Qty Terjual', 'Revenue (Rp)', 'Margin (%)']]
        
        for i, (_, row) in enumerate(top_menus.iterrows(), 1):
            menu_table_data.append([
                str(i),
                row['Menu'][:30] + '...' if len(row['Menu']) > 30 else row['Menu'],
                f"{row['Total_Qty']:,.0f}",
                f"{row['Total_Revenue']:,.0f}",
                f"{row['Margin_Percentage']:.1f}%"
            ])
        
        menu_table = Table(menu_table_data, colWidths=[0.5*inch, 2.5*inch, 0.8*inch, 1.2*inch, 0.8*inch])
        menu_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), HexColor('#2E86AB')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, HexColor('#F8F9FA')])
        ]))
        
        story.append(menu_table)
        story.append(Spacer(1, 15))
        
        # Most profitable menus
        story.append(Paragraph("Top 10 Menu Paling Menguntungkan", self.subheading_style))
        
        profitable_menus = self.analyzer.get_most_profitable_menus(self.data, 10)
        
        profit_table_data = [['Rank', 'Menu', 'Margin/Unit (Rp)', 'Margin (%)', 'Total Qty']]
        
        for i, (_, row) in enumerate(profitable_menus.iterrows(), 1):
            profit_table_data.append([
                str(i),
                row['Menu'][:30] + '...' if len(row['Menu']) > 30 else row['Menu'],
                f"{row['Avg_Margin']:,.0f}",
                f"{row['Margin_Percentage']:.1f}%",
                f"{row['Total_Qty']:,.0f}"
            ])
        
        profit_table = Table(profit_table_data, colWidths=[0.5*inch, 2.5*inch, 1*inch, 0.8*inch, 0.8*inch])
        profit_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), HexColor('#A23B72')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, HexColor('#F8F9FA')])
        ]))
        
        story.append(profit_table)
        
        return story
    
    def _create_cogs_analysis(self):
        """Create COGS analysis section."""
        story = []
        
        story.append(Paragraph("📦 ANALISIS COGS (COST OF GOODS SOLD)", self.heading_style))
        
        # COGS overview
        total_cogs = self.data['COGS Total'].sum()
        total_revenue = self.data['Total'].sum()
        avg_cogs_pct = self.data['COGS Total (%)'].mean()
        cogs_efficiency = self.analyzer.calculate_cogs_efficiency(self.data)
        
        cogs_text = f"""
        <b>Overview COGS:</b><br/>
        • Total COGS: Rp {total_cogs:,.0f}<br/>
        • COGS Percentage: {(total_cogs/total_revenue*100):.1f}% dari total revenue<br/>
        • Rata-rata COGS per transaksi: {avg_cogs_pct:.1f}%<br/>
        • Efisiensi COGS: {cogs_efficiency:.1f}%<br/><br/>
        
        <b>Interpretasi:</b><br/>
        • COGS {avg_cogs_pct:.1f}% {'berada dalam range ideal (20-30%)' if 20 <= avg_cogs_pct <= 30 else 'perlu optimasi' if avg_cogs_pct > 30 else 'sangat efisien'}<br/>
        • {'Fokus pada optimasi supplier dan porsi' if avg_cogs_pct > 25 else 'Pertahankan efisiensi saat ini'}
        """
        
        story.append(Paragraph(cogs_text, self.body_style))
        story.append(Spacer(1, 15))
        
        # High COGS menus
        story.append(Paragraph("Menu dengan COGS Tertinggi", self.subheading_style))
        
        high_cogs = self.analyzer.get_high_cogs_menus(self.data, 10)
        
        cogs_table_data = [['Menu', 'COGS (%)', 'Total Revenue (Rp)', 'Potensi Optimasi']]
        
        for _, row in high_cogs.iterrows():
            potential_saving = row['Total_Revenue'] * 0.05  # Estimasi 5% saving
            cogs_table_data.append([
                row['Menu'][:35] + '...' if len(row['Menu']) > 35 else row['Menu'],
                f"{row['Avg_COGS_Pct']:.1f}%",
                f"{row['Total_Revenue']:,.0f}",
                f"Rp {potential_saving:,.0f}"
            ])
        
        cogs_table = Table(cogs_table_data, colWidths=[2.2*inch, 0.8*inch, 1.2*inch, 1.2*inch])
        cogs_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), HexColor('#F18F01')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, HexColor('#FFF3E0')])
        ]))
        
        story.append(cogs_table)
        
        return story
    
    def _create_recommendations(self):
        """Create recommendations section."""
        story = []
        
        story.append(Paragraph("💡 REKOMENDASI STRATEGIS", self.heading_style))
        
        # Get recommendations from analyzer
        recommendations = self.analyzer.get_cogs_optimization_recommendations(self.data)
        
        # Add general business recommendations
        general_recommendations = self._generate_business_recommendations()
        
        all_recommendations = recommendations + general_recommendations
        
        for i, rec in enumerate(all_recommendations, 1):
            rec_text = f"""
            <b>{i}. {rec['title']}</b><br/>
            {rec['description']}<br/>
            <i>Potensi Impact: {rec['potential_saving']}</i><br/>
            """
            
            story.append(Paragraph(rec_text, self.body_style))
            story.append(Spacer(1, 10))
        
        # Action plan summary
        story.append(Spacer(1, 20))
        story.append(Paragraph("📋 RENCANA AKSI PRIORITAS", self.subheading_style))
        
        action_plan = """
        <b>Immediate Actions (1-2 minggu):</b><br/>
        • Review pricing menu dengan COGS tinggi<br/>
        • Analisis supplier costs untuk item high-volume<br/>
        • Implementasi portion control yang lebih ketat<br/><br/>
        
        <b>Short-term (1-3 bulan):</b><br/>
        • Negosiasi kontrak supplier utama<br/>
        • Menu engineering untuk items underperform<br/>
        • Training staff untuk waste reduction<br/><br/>
        
        <b>Long-term (3-6 bulan):</b><br/>
        • Evaluasi menu portfolio secara komprehensif<br/>
        • Implementasi sistem inventory management yang lebih baik<br/>
        • Pengembangan strategic partnerships dengan supplier
        """
        
        story.append(Paragraph(action_plan, self.body_style))
        
        return story
    
    def _get_top_category(self):
        """Get top performing category."""
        category_revenue = self.data.groupby('Menu Category')['Total'].sum()
        if not category_revenue.empty:
            return category_revenue.idxmax()
        return "N/A"
    
    def _generate_business_recommendations(self):
        """Generate general business recommendations."""
        recommendations = []
        
        # Analyze menu performance
        menu_analysis = self.analyzer.get_comprehensive_menu_analysis(self.data)
        
        # Revenue concentration
        total_revenue = self.data['Total'].sum()
        top_5_revenue = menu_analysis.head(5)['Total_Revenue'].sum()
        concentration = (top_5_revenue / total_revenue) * 100
        
        if concentration > 60:
            recommendations.append({
                'title': 'Diversifikasi Menu Portfolio',
                'description': f'{concentration:.1f}% revenue berasal dari 5 menu teratas. Kembangkan menu lain untuk mengurangi risiko dependency.',
                'potential_saving': 'Stabilitas revenue jangka panjang'
            })
        
        # Low performers
        low_performers = menu_analysis[menu_analysis['Total_Qty'] < menu_analysis['Total_Qty'].quantile(0.2)]
        
        if len(low_performers) > 0:
            recommendations.append({
                'title': 'Optimasi Menu Underperform',
                'description': f'{len(low_performers)} menu memiliki penjualan rendah. Pertimbangkan redesign, repricing, atau discontinue.',
                'potential_saving': 'Efisiensi operasional dan inventory'
            })
        
        # Pricing opportunities
        high_margin_low_volume = menu_analysis[
            (menu_analysis['Margin_Percentage'] > menu_analysis['Margin_Percentage'].quantile(0.8)) &
            (menu_analysis['Total_Qty'] < menu_analysis['Total_Qty'].median())
        ]
        
        if len(high_margin_low_volume) > 0:
            recommendations.append({
                'title': 'Marketing Focus Menu High-Margin',
                'description': f'{len(high_margin_low_volume)} menu memiliki margin tinggi tapi volume rendah. Tingkatkan visibility dan promosi.',
                'potential_saving': f'Potensi peningkatan margin Rp {high_margin_low_volume["Total_Margin"].sum() * 2:,.0f}'
            })
        
        return recommendations