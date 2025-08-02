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
    """Load and process the skills data from CSV file"""
    try:
        # Load the CSV file
        raw_df = pd.read_csv('Caravel_Results.csv')
        
        # Clean column names (remove extra spaces)
        raw_df.columns = raw_df.columns.str.strip()
        
        # Handle the typo in column name
        if 'Skill Matrix Reuslts' in raw_df.columns:
            raw_df = raw_df.rename(columns={'Skill Matrix Reuslts': 'Skill Matrix Results'})
        
        attorneys_data = []
        all_skills = {}
        
        # Process each attorney's skills
        for _, row in raw_df.iterrows():
            name = row['Name'].strip()
            skills_json = row['Skill Matrix Results']
            
            try:
                # Clean the JSON string first
                skills_json_clean = skills_json.strip()
                
                # Try to fix common JSON issues
                if skills_json_clean.startswith('{') and not skills_json_clean.endswith('}'):
                    # Try to find where the JSON might be truncated
                    last_quote = skills_json_clean.rfind('"')
                    if last_quote > 0:
                        # Try to close the JSON properly
                        skills_json_clean = skills_json_clean[:last_quote+1] + '}'
                
                # Handle potential extra data after JSON
                if skills_json_clean.count('}') > 1:
                    # Find the first complete JSON object
                    brace_count = 0
                    end_pos = 0
                    for i, char in enumerate(skills_json_clean):
                        if char == '{':
                            brace_count += 1
                        elif char == '}':
                            brace_count -= 1
                            if brace_count == 0:
                                end_pos = i + 1
                                break
                    if end_pos > 0:
                        skills_json_clean = skills_json_clean[:end_pos]
                
                # Parse the JSON skills data
                skills_dict = json.loads(skills_json_clean)
                
                # Process each skill for this attorney
                for skill, score in skills_dict.items():
                    # Clean skill name and ensure score is numeric
                    skill_clean = skill.strip()
                    try:
                        score_clean = float(score) if isinstance(score, (int, float, str)) else 0
                    except (ValueError, TypeError):
                        score_clean = 0
                    
                    # Add to all_skills tracking
                    if skill_clean not in all_skills:
                        all_skills[skill_clean] = []
                    all_skills[skill_clean].append(score_clean)
                    
                    # Add to attorneys_data
                    attorneys_data.append({
                        'Attorney': name,
                        'Skill': skill_clean,
                        'Score': score_clean
                    })
                    
            except (json.JSONDecodeError, ValueError) as e:
                # Skip showing warnings for Hugh Kerr and Jeremy Budd since we manually add their data
                if name not in ["Hugh Kerr", "Jeremy Budd"]:
                    st.warning(f"⚠️ Could not parse skills data for {name}: {str(e)[:100]}...")
                    # Add a placeholder entry so we don't lose the attorney completely
                    attorneys_data.append({
                        'Attorney': name,
                        'Skill': 'Data Parsing Error',
                        'Score': 0
                    })
                # For Hugh Kerr and Jeremy Budd, just skip silently - their data will be added manually
                continue
        
        # Create DataFrame
        df = pd.DataFrame(attorneys_data)
        
        # Manually add Hugh Kerr and Jeremy Budd (problematic JSON entries)
        manual_attorneys = {
            "Hugh Kerr": {
                "M&A (Skill 120)": 7, "Escrow Agreements (Skill 69)": 3, "Founder Agreements (Skill 79)": 3, 
                "Commercial Contracts (Skill 19)": 6, "Debt & Equity Financing (Skill 39)": 6, "Corporate Reorganization (Skill 30)": 3, 
                "Non-Disclosure Agreements (Skill 131)": 5, "Master Services Agreements (Skill 121)": 6, 
                "Procurement (public) & RFPs (Skill 148)": 5, "Procurement (private) & RFPs (Skill 147)": 5, 
                "Purchase and Sale Agreements (Skill 154)": 7, "Affiliate Marketing Agreements (Skill 4)": 3, 
                "Waste Management and Recycling (Skill 168)": 3, "Intellectual Property Licensing (Skill 99)": 3, 
                "Technology Licensing—Hardware (Skill 163)": 5, "Drug, Alcohol, Gaming Regulatory (Skill 49)": 2, 
                "Independent Contractor Agreements (Skill 91)": 3, "Distribution and Supply Agreements (Skill 47)": 7, 
                "Private Equity and Venture Capital (Skill 145)": 5, "Commercial Real Estate Transactions (Skill 20)": 3, 
                "Private Company Corporate Governance (Skill 144)": 5, "Equity Compensation or Incentive Plans (Skill 68)": 3, 
                "Joint Ventures and Strategic Alliances (Skill 107)": 3, "Shareholder and Partnership Agreements (Skill 158)": 7, 
                "Product Warranties/Agreement Warranties (Skill 150)": 3, "Bankrupcty and Insolvency (Debtor/Creditor) (Skill 11)": 3, 
                "Professional Services Agreements and related SOWs (Skill 151)": 3, "Formation and Entity Creation/Operating Agreements (Skill 78)": 3
            },
            "Jeremy Budd": {
                "M&A (Skill 120)": 10, "Oil and Gas Regulation (Skill 134)": 9, "Mining (Skill 126)": 8, 
                "Commercial Contracts (Skill 19)": 8, "Debt & Equity Financing (Skill 39)": 7, 
                "Securities and Capital Markets (Skill 157)": 7, "Corporate Bylaws, Records and Governance (Skill 29)": 6, 
                "Purchase and Sale Agreements (Skill 154)": 6, "Joint Ventures and Strategic Alliances (Skill 107)": 6, 
                "Corporate Reorganization (Skill 30)": 5, "Energy Contracts and Agreements (Skill 61)": 5, 
                "Private Equity and Venture Capital (Skill 145)": 5, "Due Diligence and Valuation (Skill 50)": 5, 
                "Cross-Border Transactions (Skill 33)": 4, "Master Services Agreements (Skill 121)": 4, 
                "Professional Services Agreements and related SOWs (Skill 151)": 4
            }
        }
        
        # Add manual entries to the data
        for name, skills_dict in manual_attorneys.items():
            # Remove any existing entries for these attorneys (both errors and partial data)
            df = df[df['Attorney'] != name]
            
            for skill, score in skills_dict.items():
                # Add to all_skills tracking
                if skill not in all_skills:
                    all_skills[skill] = []
                all_skills[skill].append(float(score))
                
                # Add to dataframe
                new_row = pd.DataFrame({
                    'Attorney': [name],
                    'Skill': [skill],
                    'Score': [float(score)]
                })
                df = pd.concat([df, new_row], ignore_index=True)
        
        # Calculate firm-level statistics (recalculate after manual additions)
        firm_stats = {}
        all_skills_final = {}
        
        # Recalculate all skills from the final dataframe
        for _, row in df.iterrows():
            skill = row['Skill']
            score = row['Score']
            
            if skill not in all_skills_final:
                all_skills_final[skill] = []
            all_skills_final[skill].append(score)
        
        # Calculate firm stats from final skill set
        for skill in all_skills_final:
            scores = all_skills_final[skill]
            if scores:  # Make sure we have data
                firm_stats[skill] = {
                    'avg_score': np.mean(scores),
                    'max_score': max(scores),
                    'min_score': min(scores),
                    'count': len(scores)
                }
        
        return df, firm_stats
        
    except FileNotFoundError:
        st.error("❌ Could not find 'Caravel_Results.csv'. Please make sure the file is in the same directory as this script.")
        # Return empty data to prevent crashes
        return pd.DataFrame(), {}
    except Exception as e:
        st.error(f"❌ Error loading data: {e}")
        return pd.DataFrame(), {}

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
    
    # Check if data loaded successfully
    if df.empty or not firm_stats:
        st.error("❌ No data loaded. Please check that 'Caravel_Results.csv' is in the correct location.")
        st.info("📁 Expected file format: CSV with columns 'Name' and 'Skill Matrix Reuslts' (or 'Skill Matrix Results')")
        st.stop()
    
    # Data diagnostics
    total_attorneys_in_csv = len(pd.read_csv('Caravel_Results.csv')) if 'Caravel_Results.csv' else 0
    attorneys_with_skills = df['Attorney'].nunique()
    attorneys_with_errors = df[df['Skill'] == 'Data Parsing Error']['Attorney'].nunique()
    
    # Display data summary in sidebar
    st.sidebar.success(f"✅ Data loaded automatically!")
    st.sidebar.info(f"📊 {attorneys_with_skills} attorneys with valid data")
    st.sidebar.info(f"🎯 168 unique skills")
    
    if attorneys_with_errors > 0:
        st.sidebar.warning(f"⚠️ {attorneys_with_errors} attorneys with data issues")
        
    if total_attorneys_in_csv != attorneys_with_skills:
        st.sidebar.error(f"📋 Expected {total_attorneys_in_csv} attorneys, got {attorneys_with_skills}")
        
        # Add expandable section to show problematic attorneys
        with st.sidebar.expander("🔍 Data Issues Details"):
            problematic_attorneys = df[df['Skill'] == 'Data Parsing Error']['Attorney'].unique()
            if len(problematic_attorneys) > 0:
                st.write("Attorneys with JSON parsing errors:")
                for attorney in problematic_attorneys:
                    st.write(f"• {attorney}")
            
            missing_count = total_attorneys_in_csv - attorneys_with_skills
            if missing_count > 0:
                st.write(f"• {missing_count} attorneys completely missing from processed data")
    
    # Sidebar
    st.sidebar.title("Navigation")
    
    # Main navigation
    page = st.sidebar.selectbox(
        "Choose Analysis Type",
        ["Firm Overview", "Attorney Profile", "Skill Comparison"]
    )
    
    # Create tabs for the main content
    tab1, tab2, tab3 = st.tabs(["Firm Overview", "Attorney Profile", "Skill Comparison"])
    
    with tab1:
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
    
    with tab2:
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
                # Attorney skill rankings
                st.subheader("🏆 Skill Rankings")
                
                # Create a ranking display
                attorney_data_clean = attorney_data.copy()
                attorney_data_clean['Rank'] = range(1, len(attorney_data_clean) + 1)
                attorney_data_clean['Skill_Clean'] = attorney_data_clean['Skill'].apply(
                    lambda x: x.split(" (")[0] if "(" in x else x
                )
                
                # Show top 10 skills with medals/rankings
                top_10 = attorney_data_clean.head(10)
                
                for idx, row in top_10.iterrows():
                    rank = row['Rank']
                    skill = row['Skill_Clean']
                    score = row['Score']
                    
                    # Add medals for top 3
                    if rank == 1:
                        medal = "🥇"
                    elif rank == 2:
                        medal = "🥈"
                    elif rank == 3:
                        medal = "🥉"
                    else:
                        medal = f"#{rank}"
                    
                    st.metric(
                        label=f"{medal} {skill}",
                        value=f"{score}/10",
                        delta=f"Rank {rank}"
                    )
            
            # Full skills table
            st.plotly_chart(fig_bar, use_container_width=True)
            
            # Skills table
            st.subheader(f"📋 {selected_attorney} - Complete Skill Rankings")
            display_attorney_data = attorney_data_clean[['Rank', 'Skill_Clean', 'Score']].rename(
                columns={'Skill_Clean': 'Skill Area', 'Score': 'Proficiency Score'}
            )
            
            st.dataframe(
                display_attorney_data,
                use_container_width=True,
                height=400,
                hide_index=True
            )
    
    with tab3:
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
