# Save this as: dashboard.py
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import joblib

# Page config
st.set_page_config(
    page_title="Rent → Home Price Causal Analysis",
    page_icon="🏠",
    layout="wide"
)

# Load data
@st.cache_data
def load_data():
    results = pd.read_csv('Resources/causal_forest_results.csv')
    states = pd.read_csv('Resources/state_mapping.csv')
    importance = pd.read_csv('Resources/feature_importance.csv')
    summary = joblib.load('Resources/summary_stats.joblib')
    return results, states, importance, summary

@st.cache_resource
def load_model():
    return joblib.load('Model/causal_forest_model.joblib')

results_df, state_mapping, importance_df, summary_stats = load_data()
cf_model = load_model()

# Header
st.title("🏠 Rent → Home Price Transmission")
st.markdown("**Causal Forest Analysis** | Conditional Average Treatment Effects by State")

# Tabs
tab1, tab2, tab3 = st.tabs(["📊 State Explorer", "🔬 Effect Simulator", "📈 Summary"])

# =============================================================================
# TAB 1: State Explorer
# =============================================================================
with tab1:
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("Select State")
        
        # State selector - aggregate by state
        state_avg = results_df.groupby('StateFullName').agg({
            'cate': 'mean',
            'cate_lower': 'mean',
            'cate_upper': 'mean',
            'elasticity': 'mean'
        }).reset_index().sort_values('cate', ascending=False)
        
        # Add state abbreviations for map
        state_abbrev_map = {
            'Alabama': 'AL', 'Alaska': 'AK', 'Arizona': 'AZ', 'Arkansas': 'AR', 'California': 'CA',
            'Colorado': 'CO', 'Connecticut': 'CT', 'Delaware': 'DE', 'Florida': 'FL', 'Georgia': 'GA',
            'Hawaii': 'HI', 'Idaho': 'ID', 'Illinois': 'IL', 'Indiana': 'IN', 'Iowa': 'IA',
            'Kansas': 'KS', 'Kentucky': 'KY', 'Louisiana': 'LA', 'Maine': 'ME', 'Maryland': 'MD',
            'Massachusetts': 'MA', 'Michigan': 'MI', 'Minnesota': 'MN', 'Mississippi': 'MS', 'Missouri': 'MO',
            'Montana': 'MT', 'Nebraska': 'NE', 'Nevada': 'NV', 'New Hampshire': 'NH', 'New Jersey': 'NJ',
            'New Mexico': 'NM', 'New York': 'NY', 'North Carolina': 'NC', 'North Dakota': 'ND', 'Ohio': 'OH',
            'Oklahoma': 'OK', 'Oregon': 'OR', 'Pennsylvania': 'PA', 'Rhode Island': 'RI', 'South Carolina': 'SC',
            'South Dakota': 'SD', 'Tennessee': 'TN', 'Texas': 'TX', 'Utah': 'UT', 'Vermont': 'VT',
            'Virginia': 'VA', 'Washington': 'WA', 'West Virginia': 'WV', 'Wisconsin': 'WI', 'Wyoming': 'WY'
        }
        state_avg['StateAbbrev'] = state_avg['StateFullName'].map(state_abbrev_map)
        
        selected_state = st.selectbox(
            "Choose a state:",
            state_avg['StateFullName'].tolist()
        )
        
        # State stats
        state_data = state_avg[state_avg['StateFullName'] == selected_state].iloc[0]
        
        st.metric(
            label="Average Treatment Effect",
            value=f"{state_data['cate']:.4f}",
            delta=f"{state_data['cate'] - summary_stats['ate']:.4f} vs national avg"
        )
        
        st.metric(
            label="95% Confidence Interval",
            value=f"[{state_data['cate_lower']:.4f}, {state_data['cate_upper']:.4f}]"
        )
        
        st.metric(
            label="Supply Elasticity",
            value=f"{state_data['elasticity']:.2f}"
        )
        
        # Interpretation
        if state_data['cate'] > summary_stats['ate']:
            st.info(f"📈 **{selected_state}** shows above-average rent→price transmission, likely due to supply constraints.")
        else:
            st.success(f"📉 **{selected_state}** shows below-average transmission, suggesting more elastic housing supply.")
    
    with col2:
        st.subheader("State-Level Treatment Effects")
        
        # Choropleth map
        fig_map = px.choropleth(
            state_avg,
            locations='StateAbbrev',
            locationmode='USA-states',
            color='cate',
            color_continuous_scale='RdYlBu_r',
            scope='usa',
            labels={'cate': 'CATE', 'StateAbbrev': 'State'},
            hover_name='StateFullName',
            hover_data={'cate': ':.4f', 'elasticity': ':.2f', 'StateAbbrev': False}
        )
        fig_map.update_layout(
            geo=dict(bgcolor='rgba(0,0,0,0)', lakecolor='lightblue'),
            paper_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=0, r=0, t=0, b=0)
        )
        st.plotly_chart(fig_map, use_container_width=True)

        # Bar chart
        fig_bar = px.bar(
            state_avg.head(15),
            x='cate',
            y='StateFullName',
            orientation='h',
            color='cate',
            color_continuous_scale='RdYlBu_r',
            labels={'cate': 'Treatment Effect', 'StateFullName': 'State'}
        )
        fig_bar.update_layout(
            title='Top 15 States by Treatment Effect',
            yaxis={'categoryorder': 'total ascending'},
            showlegend=False,
            height=400
        )
        st.plotly_chart(fig_bar, use_container_width=True)

# =============================================================================
# TAB 2: Effect Simulator
# =============================================================================
with tab2:
    st.subheader("Simulate Treatment Effects Under Different Conditions")
    st.markdown("Adjust market conditions to see how they affect the rent→price transmission.")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown("### Market Conditions")
        
        # State selector for simulator
        state_avg_sim = results_df.groupby('StateFullName').agg({
            'elasticity': 'mean',
            'wage_growth': 'mean',
            'inventory_growth': 'mean',
            'permits_growth': 'mean',
            'mortgage_change': 'mean',
            'emp_pop_ratio': 'mean'
        }).reset_index()
        
        sim_state = st.selectbox(
            "Select State",
            state_avg_sim['StateFullName'].tolist(),
            key='sim_state'
        )
        
        # Get state defaults
        state_defaults = state_avg_sim[state_avg_sim['StateFullName'] == sim_state].iloc[0]
        
        st.markdown("---")
        
        # Housing Supply Elasticity
        st.markdown("**Housing Supply Elasticity**")
        st.caption("Measures how responsive housing supply is to price changes. Lower values indicate constrained markets (e.g., San Francisco) where new construction is difficult.")
        sim_elasticity = st.slider(
            "Elasticity Value",
            min_value=float(results_df['elasticity'].min()),
            max_value=float(results_df['elasticity'].max()),
            value=float(state_defaults['elasticity']),
            step=0.1,
            label_visibility="collapsed"
        )
        
        st.markdown("---")
        
        # Wage Growth
        st.markdown("**Wage Growth (12-month lag)**")
        st.caption("Year-over-year percentage change in average wages.")
        sim_wage = st.slider(
            "Wage Growth (%)",
            min_value=float(results_df['wage_growth'].min()),
            max_value=float(results_df['wage_growth'].max()),
            value=float(state_defaults['wage_growth']),
            step=0.5,
            label_visibility="collapsed"
        )
        
        st.markdown("---")
        
        # Inventory Growth
        st.markdown("**Housing Inventory Growth (12-month lag)**")
        st.caption("Change in the number of homes available for sale.")
        sim_inventory = st.slider(
            "Inventory Growth (%)",
            min_value=float(results_df['inventory_growth'].min()),
            max_value=float(results_df['inventory_growth'].max()),
            value=float(state_defaults['inventory_growth']),
            step=1.0,
            label_visibility="collapsed"
        )
        
        st.markdown("---")
        
        # Permits Growth
        st.markdown("**Building Permits Growth (12-month lag)**")
        st.caption("Year-over-year change in new residential building permits issued.")
        sim_permits = st.slider(
            "Permits Growth (%)",
            min_value=float(results_df['permits_growth'].min()),
            max_value=float(results_df['permits_growth'].max()),
            value=float(state_defaults['permits_growth']),
            step=1.0,
            label_visibility="collapsed"
        )
        
        st.markdown("---")
        
        # Mortgage Rate Change
        st.markdown("**Mortgage Rate Change (12-month lag)**")
        st.caption("Change in average 30-year fixed mortgage rates in percentage points.")
        sim_mortgage = st.slider(
            "Mortgage Change (pp)",
            min_value=float(results_df['mortgage_change'].min()),
            max_value=float(results_df['mortgage_change'].max()),
            value=float(state_defaults['mortgage_change']),
            step=0.1,
            label_visibility="collapsed"
        )
        
        st.markdown("---")
        
        # Employment-Population Ratio
        st.markdown("**Employment-Population Ratio Change (12-month lag)**")
        st.caption("Change in the percentage of working-age population that is employed.")
        sim_emp = st.slider(
            "Emp-Pop Ratio Change",
            min_value=float(results_df['emp_pop_ratio'].min()),
            max_value=float(results_df['emp_pop_ratio'].max()),
            value=float(state_defaults['emp_pop_ratio']),
            step=0.1,
            label_visibility="collapsed"
        )
    
    with col2:
        # Create input for prediction (6 features, no state_code)
        X_sim = np.array([[
            sim_elasticity,
            sim_wage,
            sim_inventory,
            sim_permits,
            sim_mortgage,
            sim_emp
        ]])
        
        # Predict effect
        sim_effect = cf_model.effect(X_sim)[0]
        sim_lower, sim_upper = cf_model.effect_interval(X_sim, alpha=0.05)
        
        st.markdown(f"### Predicted Treatment Effect for {sim_state}")
        
        # Display result
        col_a, col_b, col_c = st.columns(3)
        col_a.metric("CATE", f"{sim_effect:.4f}")
        col_b.metric("95% CI Lower", f"{sim_lower[0]:.4f}")
        col_c.metric("95% CI Upper", f"{sim_upper[0]:.4f}")
        
        # Interpretation
        st.markdown("---")
        st.markdown("### Interpretation")
        
        rent_increase = st.number_input(
            "Hypothetical Rent Increase (%)", 
            min_value=1.0, 
            max_value=20.0, 
            value=5.0, 
            step=1.0
        )
        price_effect = rent_increase * sim_effect
        
        st.markdown(f"""
        Under these market conditions in **{sim_state}**:
        - A **{rent_increase:.1f}% rent increase** would cause approximately a **{price_effect:.2f}% increase in home values** after 12 months.
        - This effect is **{'above' if sim_effect > summary_stats['ate'] else 'below'}** the national average ({summary_stats['ate']:.4f}).
        """)
        
        # Comparison gauge
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=sim_effect,
            delta={'reference': summary_stats['ate'], 'relative': False},
            gauge={
                'axis': {'range': [results_df['cate'].min(), results_df['cate'].max()]},
                'bar': {'color': "#3b82f6"},
                'steps': [
                    {'range': [results_df['cate'].min(), summary_stats['ate']], 'color': "#22c55e"},
                    {'range': [summary_stats['ate'], results_df['cate'].max()], 'color': "#ef4444"}
                ],
                'threshold': {
                    'line': {'color': "black", 'width': 4},
                    'thickness': 0.75,
                    'value': summary_stats['ate']
                }
            },
            title={'text': f"Simulated CATE for {sim_state} vs National Average"}
        ))
        fig_gauge.update_layout(height=300)
        st.plotly_chart(fig_gauge, use_container_width=True)
        
        # Elasticity effect visualization
        st.markdown("### Effect Across Elasticity Spectrum")
        elasticity_range = np.linspace(
            results_df['elasticity'].min(),
            results_df['elasticity'].max(),
            50
        )
        
        effects_range = []
        for e in elasticity_range:
            X_temp = np.array([[e, sim_wage, sim_inventory, sim_permits, sim_mortgage, sim_emp]])
            effects_range.append(cf_model.effect(X_temp)[0])
        
        fig_line = px.line(
            x=elasticity_range,
            y=effects_range,
            labels={'x': 'Housing Supply Elasticity', 'y': 'Treatment Effect'}
        )
        fig_line.add_vline(x=sim_elasticity, line_dash="dash", line_color="red",
                          annotation_text=f"{sim_state}")
        fig_line.update_layout(title="How Elasticity Affects Treatment Effect (Other Conditions Held Constant)")
        st.plotly_chart(fig_line, use_container_width=True)

    st.markdown("---")
    st.markdown("### 💰 Real-World Impact Calculator")

    calc_col1, calc_col2 = st.columns(2)

    with calc_col1:
        home_value = st.number_input(
            "Current Home Value ($)",
            min_value=50000,
            max_value=10000000,
            value=500000,
            step=50000,
            format="%d"
        )
        
        observed_rent_change = st.number_input(
            "Observed Rent Change (%)",
            min_value=-20.0,
            max_value=30.0,
            value=5.0,
            step=0.5
        )

    with calc_col2:
        causal_price_effect_pct = observed_rent_change * sim_effect
        causal_price_effect_dollar = home_value * (causal_price_effect_pct / 100)
        counterfactual_value = home_value - causal_price_effect_dollar
        
        st.markdown("#### Results")
        
        st.metric(
            label="Current Home Value (Factual)",
            value=f"${home_value:,.0f}"
        )
        
        st.metric(
            label="Price Change Due to Rent Increase",
            value=f"${causal_price_effect_dollar:,.0f}",
            delta=f"{causal_price_effect_pct:.2f}%"
        )
        
        st.metric(
            label="Value if Rent Had NOT Increased (Counterfactual)",
            value=f"${counterfactual_value:,.0f}",
            delta=f"-${causal_price_effect_dollar:,.0f}",
            delta_color="inverse"
        )

    # Visual comparison
    fig_comparison = go.Figure()
    fig_comparison.add_trace(go.Bar(
        name='Counterfactual (No Rent Change)',
        x=['Home Value'],
        y=[counterfactual_value],
        marker_color='#3b82f6',
        text=[f'${counterfactual_value:,.0f}'],
        textposition='inside'
    ))
    fig_comparison.add_trace(go.Bar(
        name='Causal Effect of Rent',
        x=['Home Value'],
        y=[causal_price_effect_dollar],
        marker_color='#ef4444' if causal_price_effect_dollar > 0 else '#22c55e',
        text=[f'+${causal_price_effect_dollar:,.0f}' if causal_price_effect_dollar > 0 else f'${causal_price_effect_dollar:,.0f}'],
        textposition='inside'
    ))
    fig_comparison.update_layout(
        barmode='stack',
        title=f'Home Value Decomposition in {sim_state}',
        yaxis_title='Value ($)',
        showlegend=True,
        height=350
    )
    st.plotly_chart(fig_comparison, use_container_width=True)

    with st.expander("⚠️ Important Caveats"):
        st.markdown("""
        - This calculation isolates only the **causal effect of rent changes** on home prices.
        - Actual home price changes include many other factors (interest rates, local economy, etc.).
        - The CATE represents an *average* effect for this state — individual properties may vary.
        - The 12-month lag means this effect materializes over the following year.
        """)

# =============================================================================
# TAB 3: Summary
# =============================================================================
with tab3:
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Overall Results")
        
        metrics_col1, metrics_col2 = st.columns(2)
        metrics_col1.metric("Average Treatment Effect", f"{summary_stats['ate']:.4f}")
        metrics_col2.metric("Effect Std Dev", f"{summary_stats['ate_std']:.4f}")
        
        metrics_col1.metric("95% CI", f"[{summary_stats['ate_lower']:.3f}, {summary_stats['ate_upper']:.3f}]")
        metrics_col2.metric("Observations", f"{summary_stats['n_obs']:,}")
        
        fig_hist = px.histogram(
            results_df, x='cate', nbins=30,
            labels={'cate': 'Treatment Effect'},
            title='Distribution of Treatment Effects'
        )
        fig_hist.add_vline(x=summary_stats['ate'], line_dash="dash", line_color="red",
                          annotation_text=f"Mean: {summary_stats['ate']:.4f}")
        st.plotly_chart(fig_hist, use_container_width=True)
    
    with col2:
        st.subheader("Heterogeneity Drivers")
        
        fig_importance = px.bar(
            importance_df.sort_values('importance'),
            x='importance',
            y='feature',
            orientation='h',
            labels={'importance': 'Importance', 'feature': 'Feature'},
            title='What Drives Treatment Effect Heterogeneity?'
        )
        st.plotly_chart(fig_importance, use_container_width=True)
        
        results_df['elasticity_quartile'] = pd.qcut(
            results_df['elasticity'], q=4,
            labels=['Q1 (Constrained)', 'Q2', 'Q3', 'Q4 (Elastic)']
        )
        
        quartile_stats = results_df.groupby('elasticity_quartile')['cate'].agg(['mean', 'std']).reset_index()
        
        fig_quartile = px.bar(
            quartile_stats,
            x='elasticity_quartile',
            y='mean',
            error_y='std',
            labels={'mean': 'Average Treatment Effect', 'elasticity_quartile': 'Elasticity Quartile'},
            title='Effect by Supply Elasticity Quartile',
            color='mean',
            color_continuous_scale='RdYlBu_r'
        )
        st.plotly_chart(fig_quartile, use_container_width=True)

# Footer
st.markdown("---")
st.markdown("""
**Estimation of State-Level Causal Effects of Rental Prices on Home Values in the United States Using Causal Machine Learning**

*Romand Lansangan* | Far Eastern University | Machine Learning Final Project
""")