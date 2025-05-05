import plotly.express as px
import pandas as pd
import streamlit as st

def show_threat_vector_analysis(df: pd.DataFrame) -> None:
    """Visualize threat vector distribution and risk scores"""
    st.subheader("Threat Vector Analysis")
    
    # Threat distribution pie chart
    threat_counts = df['Threat_Vector'].value_counts().reset_index()
    threat_counts.columns = ['Threat_Vector', 'Count']
    
    fig1 = px.pie(threat_counts, 
                 values='Count', 
                 names='Threat_Vector',
                 title='Threat Vector Distribution',
                 hole=0.3)
    st.plotly_chart(fig1, use_container_width=True)
    
    # Threat vs Score box plot
    fig2 = px.box(df, 
                 x='Threat_Vector', 
                 y='Score',
                 title='Risk Scores by Threat Type',
                 color='Threat_Vector')
    st.plotly_chart(fig2, use_container_width=True)

def show_mitigation_analysis(df: pd.DataFrame) -> None:
    """Visualize mitigation control usage and effectiveness"""
    st.subheader("Mitigation Control Analysis")
    
    # Control usage bar chart
    control_counts = df['Mitigation_Control'].value_counts().reset_index()
    control_counts.columns = ['Mitigation_Control', 'Count']
    
    fig3 = px.bar(control_counts, 
                 x='Count', 
                 y='Mitigation_Control',
                 title='Top Mitigation Controls',
                 orientation='h')
    st.plotly_chart(fig3, use_container_width=True)
    
    # Control effectiveness scatter plot
    fig4 = px.scatter(df,
                     x='Mitigation_Control',
                     y='Score',
                     color='Threat_Vector',
                     title='Control Effectiveness by Threat',
                     hover_data=['Asset_Name'],
                     size='Score')
    st.plotly_chart(fig4, use_container_width=True)

def show_temporal_trends(df: pd.DataFrame) -> None:
    """Show risk trends over time"""
    st.subheader("Temporal Risk Trends")
    
    if 'Timestamp' not in df.columns:
        st.warning("No timestamp data available")
        return
    
    try:
        # Convert to datetime and set as index
        time_df = df.copy()
        time_df['Timestamp'] = pd.to_datetime(time_df['Timestamp'])
        time_df = time_df.set_index('Timestamp').resample('ME').agg({
            'Score': 'mean',
            'TRA_ID': 'count'
        }).reset_index()
        
        # Create visualization
        fig = px.line(time_df, 
                     x='Timestamp', 
                     y=['Score', 'TRA_ID'],
                     title='Monthly Risk Trends',
                     labels={'value': 'Metric', 'variable': 'Legend'},
                     height=400)
        st.plotly_chart(fig, use_container_width=True)
        
    except Exception as e:
        st.error(f"Could not process temporal trends: {str(e)}")

def show_summary_stats(df: pd.DataFrame) -> None:
    """Display numerical summary statistics"""
    st.markdown("### 📊 Summary Statistics")
    stats = df.select_dtypes(include=['number']).describe()
    st.dataframe(stats.style.format("{:.2f}").background_gradient(cmap='Blues'))