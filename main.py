import streamlit as st
import pandas as pd
import json
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np

# Page configuration
st.set_page_config(
    page_title="Legal Skills Analytics Dashboard",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

@st.cache_data
def load_and_process_data():
    """Load and process the skills data"""
    # Sample data - replace this with your actual data loading
    data = """Name	Skill Matrix Reuslts
Adrian Dirassar	{"M&A (Skill 120)": 10, "Oil and Gas Regulation (Skill 134)": 9, "Mining (Skill 126)": 8, "Commercial Contracts (Skill 19)": 8, "Debt & Equity Financing (Skill 39)": 7, "Securities and Capital Markets (Skill 157)": 7, "Corporate Bylaws, Records and Governance (Skill 29)": 6, "Purchase and Sale Agreements (Skill 154)": 6, "Joint Ventures and Strategic Alliances (Skill 107)": 6, "Corporate Reorganization (Skill 30)": 5}
Adrian Roomes	{"Technology Licensing—Software/SaaS (Skill 164)": 8, "Commercial Contracts (Skill 19)": 7, "Privacy Compliance (Skill 143)": 6, "Master Services Agreements (Skill 121)": 7, "Professional Services Agreements and related SOWs (Skill 151)": 6, "Corporate Bylaws, Records and Governance (Skill 29)": 5, "Employment Agreements (Skill 57)": 5, "Securities and Capital Markets (Skill 157)": 5, "M&A (Skill 120)": 4, "Technology Licensing—Hardware (Skill 163)": 4}"""
    
    # For demo purposes, I'll create a sample dataset based on the structure you provided
    # In practice, you would load this from your actual file
    attorneys_data = []
    
    # Sample data based on your format - you'll replace this with actual file reading
    sample_attorneys = [
        ("Adrian Dirassar", {"M&A (Skill 120)": 10, "Oil and Gas Regulation (Skill 134)": 9, "Mining (Skill 126)": 8, "Commercial Contracts (Skill 19)": 8, "Debt & Equity Financing (Skill 39)": 7}),
        ("Adrian Roomes", {"Technology Licensing—Software/SaaS (Skill 164)": 8, "Commercial Contracts (Skill 19)": 7, "Privacy Compliance (Skill 143)": 6, "Master Services Agreements (Skill 121)": 7}),
        ("Alan Sless", {"Technology Licensing—Software/SaaS (Skill 164)": 9, "Commercial Contracts (Skill 19)": 8, "Procurement (private) & RFPs (Skill 147)": 8, "Litigation (Civil) (Skill 114)": 6}),
        ("Alex Stack", {"Intellectual Property Protection (Skill 100)": 9, "Patent Prosecution (Skill 137)": 8, "Pharmaceutical Licensing (Skill 140)": 8, "Commercial Contracts (Skill 19)": 7}),
        ("Aliza Dason", {"Technology Licensing—Software/SaaS (Skill 164)": 10, "Commercial Contracts (Skill 19)": 9, "Master Services Agreements (Skill 121)": 9, "Procurement (private) & RFPs (Skill 147)": 8})
    ]
    
    # Process the data
    all_skills = {}
    for name, skills in sample_attorneys:
        for skill, score in skills.items():
            if skill not in all_skills:
                all_skills[skill] = []
            all_skills[skill].append(score)
            attorneys_data.append({
                'Attorney': name,
                'Skill': skill,
                'Score': score
            })
    
    df = pd.DataFrame(attorneys_data)
    
    # Calculate firm-level statistics
    firm_stats = {}
    for skill in all_skills:
        scores = all_skills[skill]
        firm_stats[skill] = {
            'avg_score': np.mean(scores),
            'max_score': max(scores),
            'min_score': min(scores),
            'count': len(scores)
        }
    
    return df, firm_stats

def create_skill_overview(firm_stats):
    """Create firm-level skill overview"""
    skills_df = pd.DataFrame(firm_stats).T
    skills_df = skills_df.sort_values('avg_score', ascending=False)
    
    # Top skills chart
    fig_top = px.bar(
        x=skills_df.head(10)['avg_score'],
        y=skills_df.head(10).index,
        orientation='h',
        title="Top 10 Skills by Average Score",
        labels={'x': 'Average Score', 'y': 'Skill'},
        color=skills_df.head(10)['avg_score'],
        color_continuous_scale='Viridis'
    )
    fig_top.update_layout(height=500, showlegend=False)
    
    # Bottom skills chart
    fig_bottom = px.bar(
        x=skills_df.tail(10)['avg_score'],
        y=skills_df.tail(10).index,
        orientation='h',
        title="Bottom 10 Skills by Average Score",
        labels={'x': 'Average Score', 'y': 'Skill'},
        color=skills_df.tail(10)['avg_score'],
        color_continuous_scale='Reds'
    )
    fig_bottom.update_layout(height=500, showlegend=False)
    
    return fig_top, fig_bottom, skills_df

def create_attorney_profile(df, attorney_name):
    """Create individual attorney skill profile"""
    attorney_data = df[df['Attorney'] == attorney_name].copy()
    attorney_data = attorney_data.sort_values('Score', ascending=False)
    
    # Radar chart for top skills
    top_skills = attorney_data.head(10)
    
    fig_radar = go.Figure()
    fig_radar.add_trace(go.Scatterpolar(
        r=top_skills['Score'],
        theta=top_skills['Skill'],
        fill='toself',
        name=attorney_name,
        line_color='rgb(0, 100, 200)'
    ))
    
    fig_radar.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 10]
            )),
        showlegend=True,
        title=f"{attorney_name} - Top 10 Skills Profile"
    )
    
    # Bar chart of all skills
    fig_bar = px.bar(
        attorney_data,
        x='Score',
        y='Skill',
        orientation='h',
        title=f"{attorney_name} - All Skills",
        color='Score',
        color_continuous_scale='Blues'
    )
    fig_bar.update_layout(height=600, showlegend=False)
    
    return fig_radar, fig_bar, attorney_data

def main():
    st.title("⚖️ Legal Skills Analytics Dashboard")
    st.markdown("---")
    
    # Load data
    df, firm_stats = load_and_process_data()
    
    # Sidebar
    st.sidebar.title("Navigation")
    
    # Main navigation
    page = st.sidebar.selectbox(
        "Choose Analysis Type",
        ["Firm Overview", "Attorney Profile", "Skill Comparison"]
    )
    
    if page == "Firm Overview":
        st.header("📊 Firm-Level Skills Analysis")
        
        # Create two columns for top and bottom skills
        col1, col2 = st.columns(2)
        
        fig_top, fig_bottom, skills_df = create_skill_overview(firm_stats)
        
        with col1:
            st.plotly_chart(fig_top, use_container_width=True)
            
        with col2:
            st.plotly_chart(fig_bottom, use_container_width=True)
        
        # Skills statistics table
        st.subheader("📈 Detailed Skill Statistics")
        
        # Format the dataframe for display
        display_df = skills_df.copy()
        display_df['avg_score'] = display_df['avg_score'].round(2)
        display_df.columns = ['Average Score', 'Max Score', 'Min Score', 'Attorney Count']
        
        st.dataframe(
            display_df,
            use_container_width=True,
            height=400
        )
        
        # Summary metrics
        st.subheader("📋 Summary Metrics")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Skills", len(skills_df))
        with col2:
            st.metric("Highest Avg Score", f"{skills_df['avg_score'].max():.2f}")
        with col3:
            st.metric("Lowest Avg Score", f"{skills_df['avg_score'].min():.2f}")
        with col4:
            st.metric("Total Attorneys", df['Attorney'].nunique())
    
    elif page == "Attorney Profile":
        st.header("👤 Individual Attorney Analysis")
        
        # Attorney selection
        attorney_list = sorted(df['Attorney'].unique())
        selected_attorney = st.selectbox(
            "Select Attorney",
            attorney_list
        )
        
        if selected_attorney:
            fig_radar, fig_bar, attorney_data = create_attorney_profile(df, selected_attorney)
            
            # Display charts
            col1, col2 = st.columns([1, 1])
            
            with col1:
                st.plotly_chart(fig_radar, use_container_width=True)
                
            with col2:
                # Attorney statistics
                st.subheader("📊 Attorney Statistics")
                total_skills = len(attorney_data)
                avg_score = attorney_data['Score'].mean()
                max_score = attorney_data['Score'].max()
                top_skill = attorney_data.iloc[0]['Skill']
                
                st.metric("Total Skills", total_skills)
                st.metric("Average Score", f"{avg_score:.2f}")
                st.metric("Highest Score", max_score)
                st.metric("Top Skill", top_skill.split(" (")[0] if "(" in top_skill else top_skill)
            
            # Full skills table
            st.plotly_chart(fig_bar, use_container_width=True)
            
            # Skills table
            st.subheader(f"📋 {selected_attorney} - Complete Skill Set")
            display_attorney_data = attorney_data.copy()
            display_attorney_data['Skill_Clean'] = display_attorney_data['Skill'].apply(
                lambda x: x.split(" (")[0] if "(" in x else x
            )
            display_attorney_data = display_attorney_data[['Skill_Clean', 'Score']].rename(
                columns={'Skill_Clean': 'Skill Area', 'Score': 'Proficiency Score'}
            )
            
            st.dataframe(
                display_attorney_data,
                use_container_width=True,
                height=400,
                hide_index=True
            )
    
    elif page == "Skill Comparison":
        st.header("🔍 Skill Comparison Analysis")
        
        # Skill selection
        all_skills = sorted(df['Skill'].unique())
        selected_skill = st.selectbox(
            "Select Skill to Analyze",
            all_skills,
            format_func=lambda x: x.split(" (")[0] if "(" in x else x
        )
        
        if selected_skill:
            skill_data = df[df['Skill'] == selected_skill].copy()
            skill_data = skill_data.sort_values('Score', ascending=False)
            
            # Skill distribution chart
            fig_dist = px.bar(
                skill_data,
                x='Attorney',
                y='Score',
                title=f"Skill Distribution: {selected_skill.split(' (')[0] if '(' in selected_skill else selected_skill}",
                color='Score',
                color_continuous_scale='Viridis'
            )
            fig_dist.update_xaxes(tickangle=45)
            fig_dist.update_layout(height=500)
            
            st.plotly_chart(fig_dist, use_container_width=True)
            
            # Statistics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Attorneys with this skill", len(skill_data))
            with col2:
                st.metric("Average Score", f"{skill_data['Score'].mean():.2f}")
            with col3:
                st.metric("Highest Score", skill_data['Score'].max())
            with col4:
                st.metric("Top Attorney", skill_data.iloc[0]['Attorney'])
            
            # Detailed table
            st.subheader("📊 Detailed Rankings")
            skill_data['Rank'] = range(1, len(skill_data) + 1)
            display_skill_data = skill_data[['Rank', 'Attorney', 'Score']].rename(
                columns={'Score': 'Proficiency Score'}
            )
            
            st.dataframe(
                display_skill_data,
                use_container_width=True,
                hide_index=True
            )

    # Footer
    st.markdown("---")
    st.markdown("*Legal Skills Analytics Dashboard - Built with Streamlit*")

if __name__ == "__main__":
    main()
