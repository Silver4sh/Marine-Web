import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from back.query.queries import get_financial_metrics, get_revenue_analysis, get_order_stats

def render_analytics_page():
    st.markdown("## 📈 Performance Analytics")
    
    # --- Load Data ---
    fin = get_financial_metrics()
    rev_df = get_revenue_analysis()
    orders = get_order_stats()
    
    # --- Top KPIs ---
    c1, c2, c3 = st.columns(3)
    c1.metric("Total Revenue", f"IDR {fin.get('total_revenue', 0):,.0f}", f"{fin.get('delta_revenue', 0):.1f}%")
    c2.metric("Total Orders", orders.get('total_orders', 0), f"Fail Rate: {(orders.get('failed',0)/max(orders.get('total_orders',1),1))*100:.1f}%", delta_color="inverse")
    c3.metric("Completed Missions", orders.get('completed', 0), "100% Success")
    
    st.divider()
    
    # --- Charts ---
    c_left, c_right = st.columns([2, 1])
    
    with c_left:
        st.subheader("Revenue Trend")
        if not rev_df.empty:
            fig = px.area(
                rev_df, x='month', y='revenue',
                template="plotly_dark",
                color_discrete_sequence=['#38bdf8']
            )
            fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)', 
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(family="Outfit", color="#8b9bb4"),
                xaxis=dict(showgrid=False),
                yaxis=dict(showgrid=True, gridcolor="rgba(148, 163, 184, 0.1)")
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No revenue data available.")
            
    with c_right:
        st.subheader("Order Status")
        labels = ["Completed", "Failed", "In Progress", "Open"]
        values = [orders.get('completed',0), orders.get('failed',0), orders.get('on_progress',0), orders.get('open',0)]
        
        fig = go.Figure(data=[go.Pie(labels=labels, values=values, hole=.6)])
        fig.update_layout(
             paper_bgcolor='rgba(0,0,0,0)',
             font=dict(family="Plus Jakarta Sans", color="#94a3b8"),
             showlegend=True,
             legend=dict(orientation="h", y=-0.2),
             colorway=['#2dd4bf', '#ef4444', '#fbbf24', '#94a3b8']
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # --- Detailed Table ---
    st.subheader("Monthly Breakdown")
    if not rev_df.empty:
        st.dataframe(
            rev_df, 
            use_container_width=True, 
            hide_index=True,
            column_config={
                "month": st.column_config.DateColumn("Month", format="MMMM YYYY"),
                "revenue": st.column_config.NumberColumn("Revenue (IDR)", format="IDR %d")
            }
        )
