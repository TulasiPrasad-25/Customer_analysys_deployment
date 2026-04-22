import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ─── Page Config ────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Customer Behavior Dashboard",
    page_icon="🛍️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── Custom CSS ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:wght@300;400;500&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}

/* Background */
.stApp {
    background-color: #0d0d0f;
    color: #f0ede8;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background-color: #131316;
    border-right: 1px solid #222228;
}
section[data-testid="stSidebar"] * {
    color: #c8c4bc !important;
}
section[data-testid="stSidebar"] .stMultiSelect [data-baseweb="tag"] {
    background-color: #e85d26 !important;
}

/* Header */
.dash-header {
    padding: 2rem 0 1.5rem 0;
    border-bottom: 1px solid #222228;
    margin-bottom: 2rem;
}
.dash-title {
    font-family: 'Syne', sans-serif;
    font-size: 2.4rem;
    font-weight: 800;
    color: #f0ede8;
    letter-spacing: -0.02em;
    line-height: 1;
}
.dash-subtitle {
    font-size: 0.9rem;
    color: #6b6860;
    margin-top: 0.4rem;
    font-weight: 300;
    letter-spacing: 0.08em;
    text-transform: uppercase;
}

/* KPI Cards */
.kpi-card {
    background: #131316;
    border: 1px solid #222228;
    border-radius: 12px;
    padding: 1.4rem 1.6rem;
    position: relative;
    overflow: hidden;
    transition: border-color 0.2s;
}
.kpi-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, #e85d26, #f5a623);
}
.kpi-label {
    font-size: 0.72rem;
    color: #6b6860;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    font-weight: 500;
    margin-bottom: 0.5rem;
}
.kpi-value {
    font-family: 'Syne', sans-serif;
    font-size: 2rem;
    font-weight: 700;
    color: #f0ede8;
    line-height: 1;
}
.kpi-delta {
    font-size: 0.78rem;
    color: #5dbe8a;
    margin-top: 0.4rem;
}

/* Section labels */
.section-label {
    font-family: 'Syne', sans-serif;
    font-size: 0.72rem;
    text-transform: uppercase;
    letter-spacing: 0.14em;
    color: #6b6860;
    margin-bottom: 0.8rem;
    margin-top: 2rem;
    font-weight: 600;
}

/* Divider */
hr {
    border-color: #222228 !important;
    margin: 1.5rem 0;
}

/* Remove streamlit branding */
#MainMenu, footer, header { visibility: hidden; }

/* Plotly chart backgrounds */
.js-plotly-plot { border-radius: 12px; }
</style>
""", unsafe_allow_html=True)

# ─── Load & Prep Data ────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_csv("customer_shopping_behavior.csv")
    df.columns = df.columns.str.lower().str.replace(' ', '_').str.replace('(', '').str.replace(')', '')
    df = df.rename(columns={'purchase_amount_usd': 'purchase_amount'})
    df['review_rating'] = df.groupby('category')['review_rating'].transform(
        lambda x: x.fillna(x.median())
    )
    labels = ['Young Adult', 'Adult', 'Middle-aged', 'Senior']
    df['age_group'] = pd.qcut(df['age'], q=4, labels=labels)
    freq_map = {
        'Fortnightly': 14, 'Weekly': 7, 'Monthly': 30,
        'Quarterly': 90, 'Bi-Weekly': 14, 'Annually': 365, 'Every 3 Months': 90
    }
    df['purchase_frequency_days'] = df['frequency_of_purchases'].map(freq_map)
    return df

df = load_data()

# ─── Plotly Theme ────────────────────────────────────────────────────────────
DARK_BG = "#0d0d0f"
CARD_BG = "#131316"
GRID_COLOR = "#1e1e24"
TEXT_COLOR = "#f0ede8"
MUTED = "#6b6860"
ACCENT = "#e85d26"
PALETTE = ["#e85d26", "#f5a623", "#5dbe8a", "#4a9eff", "#b87cfc", "#f06292"]

def base_layout(title="", height=300):
    return dict(
        title=dict(text=title, font=dict(family="Syne", size=13, color=TEXT_COLOR), x=0, pad=dict(l=4)),
        paper_bgcolor=CARD_BG,
        plot_bgcolor=CARD_BG,
        font=dict(family="DM Sans", color=TEXT_COLOR, size=11),
        height=height,
        margin=dict(l=16, r=16, t=40, b=16),
        xaxis=dict(gridcolor=GRID_COLOR, linecolor=GRID_COLOR, tickfont=dict(color=MUTED)),
        yaxis=dict(gridcolor=GRID_COLOR, linecolor=GRID_COLOR, tickfont=dict(color=MUTED)),
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color=MUTED, size=10)),
        hoverlabel=dict(bgcolor="#1e1e24", font_color=TEXT_COLOR, bordercolor="#333"),
    )

# ─── Sidebar Filters ─────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🔍 Filters")
    st.markdown("---")

    gender_opts = df['gender'].unique().tolist()
    sel_gender = st.multiselect("Gender", gender_opts, default=gender_opts)

    cat_opts = df['category'].unique().tolist()
    sel_cat = st.multiselect("Category", cat_opts, default=cat_opts)

    sub_opts = df['subscription_status'].unique().tolist()
    sel_sub = st.multiselect("Subscription Status", sub_opts, default=sub_opts)

    season_opts = df['season'].unique().tolist()
    sel_season = st.multiselect("Season", season_opts, default=season_opts)

    st.markdown("---")
    st.markdown("<span style='font-size:0.75rem;color:#6b6860'>Customer Behavior Analysis · 2024</span>", unsafe_allow_html=True)

# ─── Filter Data ─────────────────────────────────────────────────────────────
fdf = df[
    df['gender'].isin(sel_gender) &
    df['category'].isin(sel_cat) &
    df['subscription_status'].isin(sel_sub) &
    df['season'].isin(sel_season)
]

# ─── Header ──────────────────────────────────────────────────────────────────
st.markdown("""
<div class="dash-header">
  <div class="dash-title">🛍️ Customer Behavior Dashboard</div>
  <div class="dash-subtitle">Retail Analytics · 3,900 Transactions · Python + Plotly</div>
</div>
""", unsafe_allow_html=True)

# ─── KPI Row ─────────────────────────────────────────────────────────────────
k1, k2, k3, k4, k5 = st.columns(5)

total_customers = len(fdf)
total_revenue = fdf['purchase_amount'].sum()
avg_purchase = fdf['purchase_amount'].mean()
avg_rating = fdf['review_rating'].mean()
sub_rate = (fdf['subscription_status'] == 'Yes').mean() * 100

kpis = [
    (k1, "Total Customers", f"{total_customers:,}", "3,900 transactions"),
    (k2, "Total Revenue", f"${total_revenue:,.0f}", "Across all categories"),
    (k3, "Avg Purchase", f"${avg_purchase:.2f}", "Per transaction"),
    (k4, "Avg Review Rating", f"{avg_rating:.2f} ★", "Out of 5.0"),
    (k5, "Subscription Rate", f"{sub_rate:.1f}%", "Subscribed customers"),
]

for col, label, value, delta in kpis:
    with col:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">{label}</div>
            <div class="kpi-value">{value}</div>
            <div class="kpi-delta">{delta}</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ─── Row 1: Revenue by Category + Subscription Donut ────────────────────────
st.markdown('<div class="section-label">Revenue Breakdown</div>', unsafe_allow_html=True)
col1, col2, col3 = st.columns([2, 1.5, 1.5])

with col1:
    cat_rev = fdf.groupby('category')['purchase_amount'].sum().reset_index().sort_values('purchase_amount', ascending=True)
    fig = go.Figure(go.Bar(
        x=cat_rev['purchase_amount'], y=cat_rev['category'],
        orientation='h',
        marker=dict(color=PALETTE[:len(cat_rev)], line=dict(width=0)),
        text=[f"${v:,.0f}" for v in cat_rev['purchase_amount']],
        textposition='outside', textfont=dict(color=MUTED, size=10),
        hovertemplate="<b>%{y}</b><br>Revenue: $%{x:,.0f}<extra></extra>"
    ))
    layout = base_layout("Revenue by Category", 280)
    layout['xaxis']['showgrid'] = False
    layout['yaxis']['showgrid'] = False
    fig.update_layout(**layout)
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

with col2:
    sub_counts = fdf['subscription_status'].value_counts().reset_index()
    fig2 = go.Figure(go.Pie(
        labels=sub_counts['subscription_status'],
        values=sub_counts['count'],
        hole=0.65,
        marker=dict(colors=[ACCENT, "#2a2a32"], line=dict(color=CARD_BG, width=2)),
        textinfo='percent',
        textfont=dict(color=TEXT_COLOR, size=11),
        hovertemplate="<b>%{label}</b><br>%{value} customers<extra></extra>"
    ))
    fig2.add_annotation(text=f"{sub_rate:.0f}%<br><span style='font-size:9px'>Subscribed</span>",
                        x=0.5, y=0.5, showarrow=False,
                        font=dict(size=18, color=TEXT_COLOR, family="Syne"))
    layout2 = base_layout("Subscription Split", 280)
    layout2.pop('xaxis', None); layout2.pop('yaxis', None)
    fig2.update_layout(**layout2)
    st.plotly_chart(fig2, use_container_width=True, config={'displayModeBar': False})

with col3:
    gender_rev = fdf.groupby('gender')['purchase_amount'].sum().reset_index()
    fig3 = go.Figure(go.Bar(
        x=gender_rev['gender'], y=gender_rev['purchase_amount'],
        marker=dict(color=[PALETTE[3], PALETTE[0]], line=dict(width=0)),
        text=[f"${v:,.0f}" for v in gender_rev['purchase_amount']],
        textposition='outside', textfont=dict(color=MUTED, size=10),
        hovertemplate="<b>%{x}</b><br>Revenue: $%{y:,.0f}<extra></extra>"
    ))
    layout3 = base_layout("Revenue by Gender", 280)
    layout3['yaxis']['showgrid'] = True
    fig3.update_layout(**layout3)
    st.plotly_chart(fig3, use_container_width=True, config={'displayModeBar': False})

# ─── Row 2: Age Group + Season + Shipping ────────────────────────────────────
st.markdown('<div class="section-label">Demographics & Patterns</div>', unsafe_allow_html=True)
col4, col5, col6 = st.columns([1.5, 1.5, 2])

with col4:
    age_rev = fdf.groupby('age_group', observed=True)['purchase_amount'].sum().reset_index()
    age_rev.columns = ['age_group', 'revenue']
    fig4 = go.Figure(go.Bar(
        x=age_rev['revenue'], y=age_rev['age_group'].astype(str),
        orientation='h',
        marker=dict(color=PALETTE[1], opacity=0.85, line=dict(width=0)),
        text=[f"${v:,.0f}" for v in age_rev['revenue']],
        textposition='outside', textfont=dict(color=MUTED, size=10),
        hovertemplate="<b>%{y}</b><br>$%{x:,.0f}<extra></extra>"
    ))
    layout4 = base_layout("Revenue by Age Group", 280)
    layout4['xaxis']['showgrid'] = False
    layout4['yaxis']['showgrid'] = False
    fig4.update_layout(**layout4)
    st.plotly_chart(fig4, use_container_width=True, config={'displayModeBar': False})

with col5:
    season_rev = fdf.groupby('season')['purchase_amount'].sum().reset_index().sort_values('purchase_amount', ascending=False)
    fig5 = go.Figure(go.Bar(
        x=season_rev['season'], y=season_rev['purchase_amount'],
        marker=dict(color=PALETTE[2], opacity=0.85, line=dict(width=0)),
        text=[f"${v:,.0f}" for v in season_rev['purchase_amount']],
        textposition='outside', textfont=dict(color=MUTED, size=10),
        hovertemplate="<b>%{x}</b><br>$%{y:,.0f}<extra></extra>"
    ))
    layout5 = base_layout("Revenue by Season", 280)
    fig5.update_layout(**layout5)
    st.plotly_chart(fig5, use_container_width=True, config={'displayModeBar': False})

with col6:
    ship_counts = fdf['shipping_type'].value_counts().reset_index()
    ship_avg = fdf.groupby('shipping_type')['purchase_amount'].mean().reset_index()
    ship_avg.columns = ['shipping_type', 'avg_amount']
    ship_data = ship_counts.merge(ship_avg, on='shipping_type').sort_values('count', ascending=False)

    fig6 = make_subplots(specs=[[{"secondary_y": True}]])
    fig6.add_trace(go.Bar(
        x=ship_data['shipping_type'], y=ship_data['count'],
        name="# Orders", marker=dict(color=PALETTE[4], opacity=0.8, line=dict(width=0)),
        hovertemplate="<b>%{x}</b><br>Orders: %{y}<extra></extra>"
    ), secondary_y=False)
    fig6.add_trace(go.Scatter(
        x=ship_data['shipping_type'], y=ship_data['avg_amount'],
        name="Avg $", mode='lines+markers',
        line=dict(color=ACCENT, width=2),
        marker=dict(size=7, color=ACCENT),
        hovertemplate="<b>%{x}</b><br>Avg: $%{y:.2f}<extra></extra>"
    ), secondary_y=True)
    layout6 = base_layout("Shipping Type — Orders vs Avg Spend", 280)
    layout6['legend'] = dict(bgcolor="rgba(0,0,0,0)", font=dict(color=MUTED, size=10), x=0.75, y=1.1, orientation='h')
    fig6.update_layout(**layout6)
    fig6.update_yaxes(gridcolor=GRID_COLOR, tickfont=dict(color=MUTED), secondary_y=False)
    fig6.update_yaxes(gridcolor="rgba(0,0,0,0)", tickfont=dict(color=ACCENT), secondary_y=True)
    st.plotly_chart(fig6, use_container_width=True, config={'displayModeBar': False})

# ─── Row 3: Top Products + Payment Methods + Discount ────────────────────────
st.markdown('<div class="section-label">Products & Payments</div>', unsafe_allow_html=True)
col7, col8, col9 = st.columns([2, 1.5, 1.5])

with col7:
    top_items = fdf['item_purchased'].value_counts().head(10).reset_index()
    top_items.columns = ['item', 'count']
    top_items = top_items.sort_values('count', ascending=True)
    fig7 = go.Figure(go.Bar(
        x=top_items['count'], y=top_items['item'],
        orientation='h',
        marker=dict(
            color=top_items['count'],
            colorscale=[[0, "#2a2a32"], [1, ACCENT]],
            line=dict(width=0)
        ),
        text=top_items['count'],
        textposition='outside', textfont=dict(color=MUTED, size=10),
        hovertemplate="<b>%{y}</b><br>%{x} purchases<extra></extra>"
    ))
    layout7 = base_layout("Top 10 Most Purchased Items", 340)
    layout7['xaxis']['showgrid'] = False
    layout7['yaxis']['showgrid'] = False
    fig7.update_layout(**layout7)
    st.plotly_chart(fig7, use_container_width=True, config={'displayModeBar': False})

with col8:
    pay_counts = fdf['payment_method'].value_counts().reset_index()
    pay_counts.columns = ['method', 'count']
    fig8 = go.Figure(go.Pie(
        labels=pay_counts['method'], values=pay_counts['count'],
        hole=0.5,
        marker=dict(colors=PALETTE, line=dict(color=CARD_BG, width=2)),
        textinfo='label+percent',
        textfont=dict(size=9, color=TEXT_COLOR),
        hovertemplate="<b>%{label}</b><br>%{value} users (%{percent})<extra></extra>"
    ))
    layout8 = base_layout("Payment Methods", 340)
    layout8.pop('xaxis', None); layout8.pop('yaxis', None)
    layout8['legend'] = dict(bgcolor="rgba(0,0,0,0)", font=dict(color=MUTED, size=9))
    fig8.update_layout(**layout8)
    st.plotly_chart(fig8, use_container_width=True, config={'displayModeBar': False})

with col9:
    disc_rev = fdf.groupby('discount_applied')['purchase_amount'].agg(['sum','mean','count']).reset_index()
    disc_rev.columns = ['discount', 'total', 'avg', 'count']
    disc_rev['discount'] = disc_rev['discount'].map({'Yes': 'Discounted', 'No': 'Full Price'})

    fig9 = go.Figure()
    fig9.add_trace(go.Bar(
        name='Total Revenue', x=disc_rev['discount'], y=disc_rev['total'],
        marker=dict(color=[PALETTE[2], PALETTE[3]], line=dict(width=0)),
        text=[f"${v:,.0f}" for v in disc_rev['total']],
        textposition='outside', textfont=dict(color=MUTED, size=10),
        hovertemplate="<b>%{x}</b><br>Total: $%{y:,.0f}<extra></extra>"
    ))
    layout9 = base_layout("Discount Impact on Revenue", 340)
    fig9.update_layout(**layout9)
    st.plotly_chart(fig9, use_container_width=True, config={'displayModeBar': False})

# ─── Row 4: Customer Segmentation + Review Ratings ──────────────────────────
st.markdown('<div class="section-label">Customer Segments & Ratings</div>', unsafe_allow_html=True)
col10, col11 = st.columns([1, 2])

with col10:
    fdf2 = fdf.copy()
    fdf2['segment'] = fdf2['previous_purchases'].apply(
        lambda x: 'New' if x == 1 else ('Returning' if x <= 10 else 'Loyal')
    )
    seg_counts = fdf2['segment'].value_counts().reset_index()
    seg_counts.columns = ['segment', 'count']
    colors_seg = {'Loyal': PALETTE[0], 'Returning': PALETTE[1], 'New': PALETTE[3]}
    fig10 = go.Figure(go.Pie(
        labels=seg_counts['segment'],
        values=seg_counts['count'],
        hole=0.6,
        marker=dict(colors=[colors_seg.get(s, ACCENT) for s in seg_counts['segment']], line=dict(color=CARD_BG, width=3)),
        textinfo='label+value',
        textfont=dict(size=10, color=TEXT_COLOR),
        hovertemplate="<b>%{label}</b><br>%{value} customers<extra></extra>"
    ))
    fig10.add_annotation(text="Segments", x=0.5, y=0.5, showarrow=False,
                         font=dict(size=12, color=MUTED, family="Syne"))
    layout10 = base_layout("Customer Segmentation", 300)
    layout10.pop('xaxis', None); layout10.pop('yaxis', None)
    fig10.update_layout(**layout10)
    st.plotly_chart(fig10, use_container_width=True, config={'displayModeBar': False})

with col11:
    item_ratings = fdf.groupby('item_purchased')['review_rating'].mean().reset_index()
    item_ratings.columns = ['item', 'avg_rating']
    item_ratings = item_ratings.sort_values('avg_rating', ascending=False).head(12)
    item_ratings = item_ratings.sort_values('avg_rating', ascending=True)

    fig11 = go.Figure(go.Bar(
        x=item_ratings['avg_rating'], y=item_ratings['item'],
        orientation='h',
        marker=dict(
            color=item_ratings['avg_rating'],
            colorscale=[[0, "#2a2a32"], [0.5, PALETTE[1]], [1, PALETTE[2]]],
            line=dict(width=0)
        ),
        text=[f"{v:.2f} ★" for v in item_ratings['avg_rating']],
        textposition='outside', textfont=dict(color=MUTED, size=10),
        hovertemplate="<b>%{y}</b><br>Rating: %{x:.2f}<extra></extra>"
    ))
    layout11 = base_layout("Top 12 Products by Average Review Rating", 300)
    layout11['xaxis']['range'] = [3.5, 4.1]
    layout11['xaxis']['showgrid'] = False
    layout11['yaxis']['showgrid'] = False
    fig11.update_layout(**layout11)
    st.plotly_chart(fig11, use_container_width=True, config={'displayModeBar': False})

# ─── Footer ──────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("""
<div style="text-align:center; color:#6b6860; font-size:0.78rem; padding: 0.5rem 0 1rem 0;">
    Built with Python · Streamlit · Plotly &nbsp;|&nbsp; 
    Dataset: 3,900 retail transactions &nbsp;|&nbsp;
    <a href="https://github.com/TulasiPrasad-25" style="color:#e85d26; text-decoration:none;">TulasiPrasad-25</a>
</div>
""", unsafe_allow_html=True)
