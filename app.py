import streamlit as st
import psycopg2
import pandas as pd
import matplotlib.pyplot as plt
import folium
from streamlit_folium import folium_static
from groq import Groq
import re
from datetime import datetime

# Set page configuration
st.set_page_config(
    page_title="Marinex - ARGO Data Explorer",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Cool CSS styles
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        background-attachment: fixed;
    }
    
    .main .block-container {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(10px);
        border-radius: 20px;
        padding: 2rem;
        margin-top: 2rem;
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background: linear-gradient(180deg, #1e3c72 0%, #2a5298 100%);
        border-radius: 0 20px 20px 0;
    }
    
    .sidebar .block-container {
        background: transparent;
        padding: 1rem;
    }
    
    /* Sidebar text styling */
    .css-1d391kg .stMarkdown h1,
    .css-1d391kg .stMarkdown h3,
    .css-1d391kg .stMarkdown p,
    .css-1d391kg .stMarkdown div {
        color: white !important;
    }
    
    /* Title styling */
    .main h1 {
        background: linear-gradient(90deg, #667eea, #764ba2);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-weight: 700;
        font-size: 3rem;
        text-align: center;
        margin-bottom: 2rem;
        text-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    }
    
    /* Subheader styling */
    .main h2, .main h3 {
        color: #2a5298;
        font-weight: 600;
        margin: 1.5rem 0 1rem 0;
    }
    
    /* Text area styling */
    .stTextArea textarea {
        border-radius: 15px !important;
        border: 2px solid #e0e7ff !important;
        background: rgba(255, 255, 255, 0.9) !important;
        color: #1e3c72 !important;
        font-family: 'Inter', sans-serif !important;
        transition: all 0.3s ease !important;
    }
    
    .stTextArea textarea:focus {
        border-color: #667eea !important;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1) !important;
        transform: translateY(-2px) !important;
    }
    
    /* Button styling */
    .stButton button {
        background: linear-gradient(45deg, #667eea, #764ba2) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 0.75rem 2rem !important;
        font-weight: 600 !important;
        font-family: 'Inter', sans-serif !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3) !important;
    }
    
    .stButton button:hover {
        transform: translateY(-3px) !important;
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4) !important;
    }
    
    /* Example button styling */
    .css-1d391kg .stButton button {
        background: rgba(255, 255, 255, 0.2) !important;
        color: white !important;
        border: 1px solid rgba(255, 255, 255, 0.3) !important;
        backdrop-filter: blur(10px) !important;
    }
    
    .css-1d391kg .stButton button:hover {
        background: rgba(255, 255, 255, 0.3) !important;
        transform: translateY(-2px) !important;
    }
    
    /* Code block styling */
    .stCode {
        border-radius: 12px !important;
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%) !important;
        border: 1px solid #667eea !important;
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.2) !important;
    }
    
    /* Dataframe styling */
    .stDataFrame {
        border-radius: 12px !important;
        overflow: hidden !important;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1) !important;
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: rgba(102, 126, 234, 0.1);
        padding: 8px;
        border-radius: 12px;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        padding: 0px 24px;
        border-radius: 8px;
        background: transparent;
        border: none;
        color: #667eea;
        font-weight: 500;
        transition: all 0.3s ease;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background: rgba(102, 126, 234, 0.1);
        transform: translateY(-2px);
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(45deg, #667eea, #764ba2) !important;
        color: white !important;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
    }
    
    /* Metrics styling */
    .css-1xarl3l {
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white;
        border-radius: 12px;
        padding: 1rem;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.2);
        transition: transform 0.3s ease;
    }
    
    .css-1xarl3l:hover {
        transform: translateY(-5px);
    }
    
    /* Expander styling */
    .streamlit-expander {
        border-radius: 12px !important;
        border: 1px solid rgba(102, 126, 234, 0.2) !important;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05) !important;
    }
    
    .streamlit-expander summary {
        background: linear-gradient(90deg, rgba(102, 126, 234, 0.1), rgba(118, 75, 162, 0.1)) !important;
        border-radius: 12px 12px 0 0 !important;
        color: #2a5298 !important;
        font-weight: 600 !important;
        padding: 1rem !important;
    }
    
    /* Warning and info styling */
    .stAlert {
        border-radius: 12px !important;
        border: none !important;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1) !important;
    }
    
    .stAlert > div {
        border-radius: 12px !important;
    }
    
    /* Success message styling */
    .stSuccess {
        background: linear-gradient(45deg, #4CAF50, #45a049) !important;
        color: white !important;
    }
    
    /* Error message styling */
    .stError {
        background: linear-gradient(45deg, #f44336, #d32f2f) !important;
        color: white !important;
    }
    
    /* Info message styling */
    .stInfo {
        background: linear-gradient(45deg, #2196F3, #1976D2) !important;
        color: white !important;
    }
    
    /* Warning message styling */
    .stWarning {
        background: linear-gradient(45deg, #ff9800, #f57c00) !important;
        color: white !important;
    }
    
    /* Spinner styling */
    .stSpinner > div {
        border-top-color: #667eea !important;
    }
    
    /* Download button styling */
    .stDownloadButton button {
        background: linear-gradient(45deg, #4CAF50, #45a049) !important;
        color: white !important;
        border-radius: 12px !important;
        border: none !important;
        padding: 0.5rem 1rem !important;
        font-weight: 500 !important;
        transition: all 0.3s ease !important;
    }
    
    .stDownloadButton button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(76, 175, 80, 0.3) !important;
    }
    
    /* Sidebar title enhancement */
    .css-1d391kg .stMarkdown h1 {
        text-align: center;
        font-size: 2.5rem;
        margin-bottom: 1rem;
        text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
    }
    
    /* Cool animation for the main container */
    @keyframes slideInUp {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .main .block-container {
        animation: slideInUp 0.6s ease-out;
    }
    
    /* Hover effects for dataframes */
    .stDataFrame:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 30px rgba(0, 0, 0, 0.15) !important;
        transition: all 0.3s ease;
    }
    
    /* Cool gradient borders */
    .gradient-border {
        border: 2px solid transparent;
        border-radius: 12px;
        background: linear-gradient(45deg, #667eea, #764ba2) border-box;
        -webkit-mask: linear-gradient(#fff 0 0) padding-box, linear-gradient(#fff 0 0);
        -webkit-mask-composite: destination-out;
        mask: linear-gradient(#fff 0 0) padding-box, linear-gradient(#fff 0 0);
        mask-composite: exclude;
    }
    
    /* Make the folium map container look cooler */
    .folium-map {
        border-radius: 12px !important;
        overflow: hidden !important;
        box-shadow: 0 8px 30px rgba(0, 0, 0, 0.2) !important;
    }
    
    /* Custom scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: rgba(102, 126, 234, 0.1);
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(45deg, #667eea, #764ba2);
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(45deg, #5a67d8, #6b46c1);
    }
</style>
""", unsafe_allow_html=True)

# Initialize the Groq client
client = Groq(api_key="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")

# Database connection function
def get_db_connection():
    try:
        conn = psycopg2.connect(
            "postgresql://neondb_owner:npg_qV9a3dQRAeBm@ep-still-field-a17hi4xm-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"
        )
        return conn
    except Exception as e:
        st.error(f"Error connecting to database: {e}")
        return None

# System prompt for the LLM
system_prompt = """
You are FloatChat, an AI-powered conversational agent for ARGO ocean data exploration and visualization. 
You are connected to a PostgreSQL database with the schema:

Table: argo_floats
Columns:
- id (int, primary key)
- platform_number (varchar): unique float identifier
- cycle_number (int): profile cycle number
- measurement_time (timestamp): date & time of observation
- latitude (double precision)
- longitude (double precision)
- pressure (double precision): depth in decibars
- temperature (double precision): temperature (°C)
- salinity (double precision): salinity (PSU)
- data_quality (varchar)
- region (varchar, default 'Indian Ocean')
- data_source (varchar)
- created_at (timestamp)

Your role:
1. Take user questions in natural language.
2. Translate them into valid SQL queries on the argo_floats table.
3. If the query requires spatial/temporal filtering, use latitude, longitude, and measurement_time.
4. Always limit results for readability (e.g., LIMIT 100) unless the user requests full output.
5. Provide the answer in natural language, followed by tabular results. 
6. If the question asks for visualization:
   - For trends over time → return a line plot (time vs variable).
   - For spatial patterns → return a map scatter (lat vs lon).
   - For vertical profiles (pressure vs temperature/salinity) → return depth plots.
7. If the user asks vague questions, guide them by suggesting possible queries.

Always stay grounded in the database content. Do not hallucinate.

Output your response in the following format:
<thinking>
[Your reasoning about the query and what SQL to generate]
</thinking>

<sql>
[Your SQL query here]
</sql>

<response>
[Your natural language response to the user]
</response>
"""

# Function to extract SQL from LLM response
def extract_sql(response):
    sql_match = re.search(r'<sql>(.*?)</sql>', response, re.DOTALL)
    if sql_match:
        return sql_match.group(1).strip()
    return None

# Function to execute SQL query and return results as DataFrame
def execute_sql_query(sql_query):
    conn = get_db_connection()
    if conn is None:
        return None
    
    try:
        df = pd.read_sql_query(sql_query, conn)
        conn.close()
        return df
    except Exception as e:
        st.error(f"Error executing SQL query: {e}")
        conn.close()
        return None

# Function to create a map visualization
def create_map(df):
    if df is None or df.empty or 'latitude' not in df.columns or 'longitude' not in df.columns:
        return None
    
    # Calculate center of the map
    center_lat = df['latitude'].mean()
    center_lon = df['longitude'].mean()
    
    # Create map
    m = folium.Map(location=[center_lat, center_lon], zoom_start=3)
    
    # Add markers for each data point
    for _, row in df.iterrows():
        # Create popup content
        popup_content = f"""
        <b>Float:</b> {row.get('platform_number', 'N/A')}<br>
        <b>Time:</b> {row.get('measurement_time', 'N/A')}<br>
        <b>Temp:</b> {row.get('temperature', 'N/A')}°C<br>
        <b>Salinity:</b> {row.get('salinity', 'N/A')} PSU<br>
        <b>Pressure:</b> {row.get('pressure', 'N/A')} dbar
        """
        
        # Color code by temperature if available
        if 'temperature' in df.columns:
            temp = row.get('temperature', 20)
            if temp < 10:
                color = 'blue'
            elif temp < 20:
                color = 'green'
            elif temp < 25:
                color = 'orange'
            else:
                color = 'red'
        else:
            color = 'blue'
        
        folium.Marker(
            [row['latitude'], row['longitude']],
            popup=folium.Popup(popup_content, max_width=300),
            tooltip=f"Float: {row.get('platform_number', 'N/A')}",
            icon=folium.Icon(color=color, icon='tint', prefix='fa')
        ).add_to(m)
    
    return m

# Function to generate profile plot
def create_profile_plot(df):
    if df is None or df.empty or 'pressure' not in df.columns:
        return None
    
    # Set the style for cooler plots
    plt.style.use('dark_background')
    fig, ax1 = plt.subplots(figsize=(8, 10))
    fig.patch.set_facecolor('#1e1e1e')
    ax1.set_facecolor('#2a2a2a')
    
    # Plot temperature if available
    if 'temperature' in df.columns:
        color = '#ff6b6b'
        ax1.set_xlabel('Temperature (°C)', color=color, fontweight='bold')
        ax1.plot(df['temperature'], df['pressure'], color=color, marker='o', linestyle='-', 
                label='Temperature', linewidth=2, markersize=6, alpha=0.8)
        ax1.tick_params(axis='x', labelcolor=color)
        ax1.invert_yaxis()  # Invert y-axis for depth
    
    # Create second axis for salinity if available
    if 'salinity' in df.columns:
        ax2 = ax1.twiny()
        color = '#4ecdc4'
        ax2.set_xlabel('Salinity (PSU)', color=color, fontweight='bold')
        ax2.plot(df['salinity'], df['pressure'], color=color, marker='s', linestyle='--', 
                label='Salinity', linewidth=2, markersize=6, alpha=0.8)
        ax2.tick_params(axis='x', labelcolor=color)
    
    ax1.set_ylabel('Pressure (dbar)', color='white', fontweight='bold')
    ax1.grid(True, alpha=0.3, color='white')
    plt.title('Vertical Profile', color='white', fontsize=16, fontweight='bold', pad=20)
    
    # Combine legends
    lines1, labels1 = ax1.get_legend_handles_labels()
    if 'salinity' in df.columns:
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper right', 
                  facecolor='#3a3a3a', edgecolor='white', framealpha=0.9)
    else:
        ax1.legend(loc='upper right', facecolor='#3a3a3a', edgecolor='white', framealpha=0.9)
    
    plt.tight_layout()
    return fig

# Function to generate time series plot
def create_time_series(df):
    if df is None or df.empty or 'measurement_time' not in df.columns:
        return None
    
    # Convert to datetime if needed
    if df['measurement_time'].dtype == 'object':
        df['measurement_time'] = pd.to_datetime(df['measurement_time'])
    
    # Set the style for cooler plots
    plt.style.use('dark_background')
    fig, ax1 = plt.subplots(figsize=(12, 6))
    fig.patch.set_facecolor('#1e1e1e')
    ax1.set_facecolor('#2a2a2a')
    
    # Plot temperature if available
    if 'temperature' in df.columns:
        color = '#ff6b6b'
        ax1.set_xlabel('Time', color='white', fontweight='bold')
        ax1.set_ylabel('Temperature (°C)', color=color, fontweight='bold')
        ax1.plot(df['measurement_time'], df['temperature'], color=color, marker='o', 
                linestyle='-', label='Temperature', linewidth=2, markersize=4, alpha=0.8)
        ax1.tick_params(axis='y', labelcolor=color)
    
    # Create second axis for salinity if available
    if 'salinity' in df.columns:
        ax2 = ax1.twinx()
        color = '#4ecdc4'
        ax2.set_ylabel('Salinity (PSU)', color=color, fontweight='bold')
        ax2.plot(df['measurement_time'], df['salinity'], color=color, marker='s', 
                linestyle='--', label='Salinity', linewidth=2, markersize=4, alpha=0.8)
        ax2.tick_params(axis='y', labelcolor=color)
    
    plt.title('Time Series', color='white', fontsize=16, fontweight='bold', pad=20)
    ax1.grid(True, alpha=0.3, color='white')
    plt.xticks(rotation=45, color='white')
    ax1.tick_params(axis='x', colors='white')
    
    # Combine legends
    lines1, labels1 = ax1.get_legend_handles_labels()
    if 'salinity' in df.columns:
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left',
                  facecolor='#3a3a3a', edgecolor='white', framealpha=0.9)
    else:
        ax1.legend(loc='upper left', facecolor='#3a3a3a', edgecolor='white', framealpha=0.9)
    
    plt.tight_layout()
    return fig

# Main function to process user queries
def process_user_query(user_query):
    # Prepare messages for the LLM
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_query}
    ]
    
    # Get response from LLM
    try:
        with st.spinner("✨ Generating SQL query..."):
            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=messages,
                temperature=0.1,
                max_tokens=1024
            )
        
        llm_response = completion.choices[0].message.content
        
        # Extract SQL from response
        sql_query = extract_sql(llm_response)
        
        if not sql_query:
            st.error("I couldn't generate a valid SQL query for your request. Please try rephrasing.")
            return None, None, None
        
        st.code(sql_query, language="sql")
        
        # Execute the SQL query
        with st.spinner("🔍 Executing query..."):
            df = execute_sql_query(sql_query)
        
        if df is None or df.empty:
            st.warning("No data found for your query. Please try different parameters.")
            return None, None, None
        
        # Extract the natural language response from LLM
        response_match = re.search(r'<response>(.*?)</response>', llm_response, re.DOTALL)
        natural_response = response_match.group(1).strip() if response_match else "Here are the results of your query:"
        
        return natural_response, df, sql_query
        
    except Exception as e:
        st.error(f"Error processing your request: {str(e)}")
        return None, None, None

# Main app
def main():
    # Sidebar
    with st.sidebar:
        st.title("Marinex ")
        st.markdown("**ARGO Data Explorer**")
        
        # Query input
        user_query = st.text_area(
            "Enter your query about ARGO data:",
            height=100,
            placeholder="e.g., Show me temperature profiles for floats near the equator in the last month"
        )
        
        # Process button
        process_btn = st.button(" Process Query", type="primary")
        
        # Example queries
        st.markdown("###  Example Queries")
        examples = [
            "Show me a map of all float measurements with salinity above 36 PSU",
            "Show me one float which is farthest from chennai",
            "show me float having highest temperature among all other floats"
        ]
        
        for example in examples:
            if st.button(example, key=example):
                user_query = example
                process_btn = True
    
    # Main content
    st.title(" Marinex Data Dashboard")
    
    # Initialize session state
    if 'results' not in st.session_state:
        st.session_state.results = None
    if 'df' not in st.session_state:
        st.session_state.df = None
    if 'sql' not in st.session_state:
        st.session_state.sql = None
    
    # Process query if button is clicked
    if process_btn and user_query:
        natural_response, df, sql_query = process_user_query(user_query)
        if df is not None:
            st.session_state.results = natural_response
            st.session_state.df = df
            st.session_state.sql = sql_query
    
    # Display results if available
    if st.session_state.df is not None:
        # Display natural language response
        st.markdown("### Results")
        st.success(st.session_state.results)
        
        # Display data
        st.dataframe(st.session_state.df, use_container_width=True)
        
        # Create tabs for different visualizations
        tab1, tab2, tab3, tab4 = st.tabs(["🗺️ Map", "📈 Profile", "⏰ Time Series", "📋 Raw Data"])
        
        with tab1:
            # Create map
            st.subheader("🌍 Float Locations")
            map_obj = create_map(st.session_state.df)
            if map_obj:
                # Add custom CSS class to the map container
                st.markdown('<div class="folium-map">', unsafe_allow_html=True)
                folium_static(map_obj, width=1000, height=600)
                st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.info("📍 No location data available for mapping.")
        
        with tab2:
            # Create profile plot
            st.subheader("🌊 Vertical Profile")
            profile_fig = create_profile_plot(st.session_state.df)
            if profile_fig:
                st.pyplot(profile_fig)
            else:
                st.info("📏 No pressure data available for profile plot.")
        
        with tab3:
            # Create time series
            st.subheader("📊 Time Series")
            time_fig = create_time_series(st.session_state.df)
            if time_fig:
                st.pyplot(time_fig)
            else:
                st.info("⏰ No time data available for time series plot.")
        
        with tab4:
            # Show raw data
            st.subheader("📋 Raw Data")
            st.dataframe(st.session_state.df, use_container_width=True)
            st.download_button(
                label="📥 Download data as CSV",
                data=st.session_state.df.to_csv(index=False),
                file_name="argo_data.csv",
                mime="text/csv",
            )
    
    # Display database info
    with st.expander("🗄️ Database Information"):
        conn = get_db_connection()
        if conn:
            try:
                # Get table info
                table_info = pd.read_sql("""
                    SELECT column_name, data_type, is_nullable 
                    FROM information_schema.columns 
                    WHERE table_name = 'argo_floats'
                    ORDER BY ordinal_position;
                """, conn)
                
                st.write("**Table Schema:**")
                st.dataframe(table_info)
                
                # Get some stats
                row_count = pd.read_sql("SELECT COUNT(*) as count FROM argo_floats;", conn)
                min_date = pd.read_sql("SELECT MIN(measurement_time) as min_date FROM argo_floats;", conn)
                max_date = pd.read_sql("SELECT MAX(measurement_time) as max_date FROM argo_floats;", conn)
                
                st.write("**Database Statistics:**")
                col1, col2, col3 = st.columns(3)
                col1.metric("📊 Total Records", f"{row_count['count'].iloc[0]:,}")
                col2.metric("📅 Earliest Measurement", min_date['min_date'].iloc[0].strftime('%Y-%m-%d'))
                col3.metric("🕐 Latest Measurement", max_date['max_date'].iloc[0].strftime('%Y-%m-%d'))
                
                conn.close()
            except Exception as e:
                st.error(f"Error retrieving database info: {e}")

if __name__ == "__main__":
    main()
