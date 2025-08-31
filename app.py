import streamlit as st
import psycopg2
import pandas as pd
import matplotlib.pyplot as plt
import folium
from streamlit_folium import folium_static
from groq import Groq
import re
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import requests
import json
import numpy as np
import streamlit.components.v1 as components
import logging
from psycopg2.pool import SimpleConnectionPool
from functools import lru_cache
import time
import html
from st_aggrid import AgGrid, GridOptionsBuilder

# Set page configuration
st.set_page_config(
    page_title="Marinex - ARGO Data Explorer",
    page_icon="🌊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Enhanced CSS with the original styling plus improvements
st.markdown("""
<style>
    /* Hide Streamlit UI elements */
    #MainMenu {visibility: hidden;}
    .stDeployButton {display: none;}
    footer {visibility: hidden;}
    .stActionButton {display: none;}
    header {visibility: hidden;}
    .viewerBadge_container__1QSob {display: none;}
    .stAppViewContainer > .main > div {padding-top: 1rem;}
    
    /* Import fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500&display=swap');
    
    /* Global styles matching the original HTML */
    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        box-sizing: border-box;
    }
    
    /* Enhanced main header */
    .main-header {
        background: linear-gradient(135deg, #ff8c42 0%, #ff6b35 50%, #ff5500 100%);
        padding: 2.5rem;
        border-radius: 16px;
        margin-bottom: 2rem;
        color: white;
        box-shadow: 0 8px 32px rgba(255, 140, 66, 0.25);
        position: relative;
        overflow: hidden;
        border: none;
    }
    
    .main-header::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: url("data:image/svg+xml,%3Csvg width='100' height='100' viewBox='0 0 100 100' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath d='M11 18c3.866 0 7-3.134 7-7s-3.134-7-7-7-7 3.134-7 7 3.134 7 7 7zm48 25c3.866 0 7-3.134 7-7s-3.134-7-7-7-7 3.134-7 7 3.134 7 7 7zm-43-7c1.657 0 3-1.343 3-3s-1.343-3-3-3-3 1.343-3 3 1.343 3 3 3zm63 31c1.657 0 3-1.343 3-3s-1.343-3-3-3-3 1.343-3 3 1.343 3 3 3zM34 90c1.657 0 3-1.343 3-3s-1.343-3-3-3-3 1.343-3 3 1.343 3 3 3zm56-76c1.657 0 3-1.343 3-3s-1.343-3-3-3-3 1.343-3 3 1.343 3 3 3zM12 86c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm28-65c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm23-11c2.76 0 5-2.24 5-5s-2.24-5-5-5-5 2.24-5 5 2.24 5 5 5zm-6 60c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm29 22c2.76 0 5-2.24 5-5s-2.24-5-5-5-5 2.24-5 5 2.24 5 5 5zM32 63c2.76 0 5-2.24 5-5s-2.24-5-5-5-5 2.24-5 5 2.24 5 5 5zm57-13c2.76 0 5-2.24 5-5s-2.24-5-5-5-5 2.24-5 5 2.24 5 5 5zm-9-21c1.105 0 2-.895 2-2s-.895-2-2-2-2 .895-2 2 .895 2 2 2zM60 91c1.105 0 2-.895 2-2s-.895-2-2-2-2 .895-2 2 .895 2 2 2zM35 41c1.105 0 2-.895 2-2s-.895-2-2-2-2 .895-2 2 .895 2 2 2zM12 60c1.105 0 2-.895 2-2s-.895-2-2-2-2 .895-2 2 .895 2 2 2z' fill='%23ffffff' fill-opacity='0.05' fill-rule='evenodd'/%3E%3C/svg%3E");
        opacity: 0.1;
    }
    
    .header-title {
        font-size: 2.8rem;
        font-weight: 800;
        margin: 0 0 0.5rem 0;
        letter-spacing: -0.02em;
        text-shadow: 0 2px 4px rgba(0,0,0,0.2);
        position: relative;
    }
    
    .header-subtitle {
        font-size: 1.2rem;
        font-weight: 400;
        opacity: 0.95;
        margin: 0;
        text-shadow: 0 1px 2px rgba(0,0,0,0.1);
    }
    
    /* Enhanced stats grid */
    .stats-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
        gap: 1.8rem;
        margin: 2.5rem 0;
    }
    
    .metric-card {
        background: linear-gradient(145deg, #2d2d2d, #252525);
        border-radius: 16px;
        padding: 2rem;
        color: white;
        border: 1px solid #404040;
        transition: all 0.3s ease;
        box-shadow: 0 8px 24px rgba(0,0,0,0.12);
        position: relative;
        overflow: hidden;
    }
    
    .metric-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, #ff8c42, #ff6b35);
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 16px 40px rgba(255, 140, 66, 0.25);
        border-color: #ff8c42;
    }
    
    .metric-label {
        font-size: 0.875rem;
        font-weight: 600;
        color: #aaa;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin-bottom: 0.75rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .metric-value {
        font-size: 2.5rem;
        font-weight: 800;
        color: #ff8c42;
        line-height: 1;
        margin-bottom: 0.5rem;
        text-shadow: 0 2px 4px rgba(0,0,0,0.2);
    }
    
    .metric-description {
        font-size: 0.9rem;
        color: #999;
        margin: 0;
        line-height: 1.5;
    }
    
    .live-indicator {
        display: inline-block;
        width: 10px;
        height: 10px;
        background: linear-gradient(135deg, #10b981, #059669);
        border-radius: 50%;
        margin-right: 8px;
        animation: pulse 1.5s infinite;
        box-shadow: 0 0 0 rgba(16, 185, 129, 0.4);
    }
    
    @keyframes pulse {
        0% {
            transform: scale(0.95);
            box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7);
        }
        70% {
            transform: scale(1);
            box-shadow: 0 0 0 10px rgba(16, 185, 129, 0);
        }
        100% {
            transform: scale(0.95);
            box-shadow: 0 0 0 0 rgba(16, 185, 129, 0);
        }
    }
    
    /* Enhanced Cesium container */
    .cesium-container {
        height: 600px;
        border-radius: 16px;
        overflow: hidden;
        box-shadow: 0 12px 36px rgba(0,0,0,0.2);
        border: 1px solid #404040;
        background: #1a1a1a;
        margin: 1.5rem 0;
    }
    
    /* Enhanced chat interface */
    .chat-interface {
        background: linear-gradient(145deg, #2d2d2d, #252525);
        border-radius: 16px;
        padding: 2rem;
        margin: 2.5rem 0;
        border: 1px solid #404040;
        color: white;
        box-shadow: 0 8px 32px rgba(0,0,0,0.15);
    }
    
    .query-input {
        background: #3a3a3a;
        border: 1px solid #555;
        border-radius: 12px;
        padding: 1.2rem;
        color: white;
        width: 100%;
        margin-bottom: 1.2rem;
        font-size: 1rem;
        transition: all 0.3s ease;
        box-shadow: inset 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .query-input:focus {
        outline: none;
        border-color: #ff8c42;
        box-shadow: 0 0 0 3px rgba(255, 140, 66, 0.2), inset 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .query-button {
        background: linear-gradient(135deg, #ff8c42, #ff6b35);
        border: none;
        border-radius: 12px;
        padding: 1rem 2rem;
        color: white;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.3s;
        box-shadow: 0 4px 14px rgba(255, 140, 66, 0.4);
        font-size: 1rem;
        letter-spacing: 0.02em;
    }
    
    .query-button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(255, 140, 66, 0.5);
    }
    
    .query-button:active {
        transform: translateY(0);
        box-shadow: 0 2px 10px rgba(255, 140, 66, 0.4);
    }
    
    .sample-queries {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
        gap: 1.2rem;
        margin-top: 1.5rem;
    }
    
    .sample-query {
        background: linear-gradient(145deg, #3a3a3a, #323232);
        padding: 1rem;
        border-radius: 12px;
        cursor: pointer;
        transition: all 0.3s;
        color: #f5f5f5;
        text-align: center;
        border: 1px solid #555;
        font-size: 0.95rem;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }
    
    .sample-query:hover {
        background: linear-gradient(145deg, #4a4a4a, #3a3a3a);
        color: #ff8c42;
        border-color: #ff8c42;
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(255, 140, 66, 0.2);
    }
    
    /* Enhanced data panels */
    .data-panel {
        background: linear-gradient(145deg, #2d2d2d, #252525);
        border-radius: 16px;
        padding: 2rem;
        color: white;
        border: 1px solid #404040;
        margin: 1.5rem 0;
        box-shadow: 0 8px 32px rgba(0,0,0,0.12);
    }
    
    .panel-title {
        color: #ff8c42;
        font-size: 1.4rem;
        font-weight: 700;
        margin-bottom: 1.5rem;
        border-bottom: 2px solid #404040;
        padding-bottom: 0.8rem;
        display: flex;
        align-items: center;
        gap: 0.75rem;
    }
    
    /* Enhanced tabs */
    .stTab {
        background: #2d2d2d;
        color: white;
    }
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: #2d2d2d;
        border-bottom: 1px solid #404040;
        padding: 0 0.5rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: #2d2d2d;
        color: #888;
        border-radius: 8px 8px 0 0;
        border: 1px solid transparent;
        padding: 0.75rem 1.5rem;
        font-weight: 500;
        transition: all 0.3s;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background: #3a3a3a;
        color: #ff8c42;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(145deg, #3a3a3a, #323232);
        color: #ff8c42;
        border-color: #404040;
        border-bottom-color: #2d2d2d;
        box-shadow: 0 -4px 12px rgba(0,0,0,0.1);
    }
    
    /* Enhanced data tables */
    .stDataFrame {
        background: #2d2d2d;
        border-radius: 12px;
        border: 1px solid #404040;
    }
    
    /* NASA panel enhancement */
    .nasa-panel {
        background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 50%, #60a5fa 100%);
        border-radius: 16px;
        padding: 2rem;
        color: white;
        margin: 1.5rem 0;
        box-shadow: 0 8px 32px rgba(59, 130, 246, 0.25);
        border: none;
        position: relative;
        overflow: hidden;
    }
    
    .nasa-panel::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='0.05'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E");
        opacity: 0.1;
    }
    
    .api-status {
        display: inline-flex;
        align-items: center;
        padding: 6px 12px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        gap: 0.5rem;
    }
    
    .status-active {
        background: rgba(16, 185, 129, 0.2);
        color: #10b981;
        border: 1px solid rgba(16, 185, 129, 0.3);
    }
    
    .status-inactive {
        background: rgba(245, 158, 11, 0.2);
        color: #f59e0b;
        border: 1px solid rgba(245, 158, 11, 0.3);
    }
    
    /* Enhanced code blocks */
    .stCodeBlock {
        border-radius: 12px;
        border: 1px solid #404040;
    }
    
    code {
        font-family: 'JetBrains Mono', monospace;
        background: #2d2d2d;
        padding: 2px 6px;
        border-radius: 4px;
        color: #ff8c42;
        font-size: 0.9em;
    }
    
    pre {
        background: #1e1e1e;
        border-radius: 8px;
        padding: 1.5rem;
        border: 1px solid #404040;
        overflow-x: auto;
    }
    
    /* Enhanced sidebar */
    .css-1d391kg {
        background: linear-gradient(145deg, #252525, #1e1e1e);
        border-right: 1px solid #404040;
    }
    
    /* Enhanced buttons */
    .stButton > button {
        border-radius: 12px;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        transition: all 0.3s;
    }
    
    /* Enhanced select boxes */
    .stSelectbox > div > div {
        background: #3a3a3a;
        border: 1px solid #555;
        border-radius: 12px;
        color: white;
    }
    
    /* Enhanced multiselect */
    .stMultiSelect > div > div {
        background: #3a3a3a;
        border: 1px solid #555;
        border-radius: 12px;
        color: white;
    }
    
    /* Enhanced download button */
    .stDownloadButton > button {
        background: linear-gradient(135deg, #10b981, #059669);
        border: none;
        border-radius: 12px;
        color: white;
        font-weight: 600;
        transition: all 0.3s;
    }
    
    .stDownloadButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(16, 185, 129, 0.3);
    }
    
    /* Enhanced expander */
    .streamlit-expanderHeader {
        background: #3a3a3a;
        border-radius: 12px;
        padding: 1rem;
        border: 1px solid #555;
        font-weight: 600;
    }
    
    .streamlit-expanderContent {
        background: #2d2d2d;
        border-radius: 0 0 12px 12px;
        padding: 1.5rem;
        border: 1px solid #555;
        border-top: none;
    }
    
    /* Mobile responsiveness */
    @media (max-width: 768px) {
        .stats-grid {
            grid-template-columns: 1fr;
            gap: 1.2rem;
        }
        
        .cesium-container {
            height: 400px;
            border-radius: 12px;
        }
        
        .main-header {
            padding: 1.8rem;
            border-radius: 12px;
        }
        
        .header-title {
            font-size: 2.2rem;
        }
        
        .header-subtitle {
            font-size: 1rem;
        }
        
        .metric-card {
            padding: 1.5rem;
        }
        
        .metric-value {
            font-size: 2rem;
        }
        
        .sample-queries {
            grid-template-columns: 1fr;
        }
        
        .data-panel, .chat-interface {
            padding: 1.5rem;
        }
    }
    
    /* Tooltip styles */
    .tooltip {
        position: relative;
        display: inline-block;
        cursor: pointer;
    }
    
    .tooltip .tooltiptext {
        visibility: hidden;
        width: 220px;
        background: #2d2d2d;
        color: white;
        text-align: center;
        border-radius: 8px;
        padding: 10px;
        position: absolute;
        z-index: 1;
        bottom: 125%;
        left: 50%;
        margin-left: -110px;
        opacity: 0;
        transition: opacity 0.3s;
        border: 1px solid #404040;
        box-shadow: 0 8px 24px rgba(0,0,0,0.15);
        font-size: 0.9rem;
        line-height: 1.5;
    }
    
    .tooltip .tooltiptext::after {
        content: "";
        position: absolute;
        top: 100%;
        left: 50%;
        margin-left: -5px;
        border-width: 5px;
        border-style: solid;
        border-color: #2d2d2d transparent transparent transparent;
    }
    
    .tooltip:hover .tooltiptext {
        visibility: visible;
        opacity: 1;
    }
    
    /* Accessibility improvements */
    @media (prefers-reduced-motion: reduce) {
        * {
            animation-duration: 0.01ms !important;
            animation-iteration-count: 1 !important;
            transition-duration: 0.01ms !important;
        }
    }
    
    /* Focus indicators for accessibility */
    button:focus, input:focus, select:focus, textarea:focus {
        outline: 2px solid #ff8c42;
        outline-offset: 2px;
    }
    
    /* Custom scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: #2d2d2d;
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: #555;
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #ff8c42;
    }
    
    /* Loading animation */
    @keyframes shimmer {
        0% {
            background-position: -468px 0;
        }
        100% {
            background-position: 468px 0;
        }
    }
    
    .shimmer {
        animation-duration: 1.5s;
        animation-fill-mode: forwards;
        animation-iteration-count: infinite;
        animation-name: shimmer;
        animation-timing-function: linear;
        background: #3a3a3a;
        background: linear-gradient(to right, #3a3a3a 8%, #404040 18%, #3a3a3a 33%);
        background-size: 800px 104px;
        position: relative;
    }
    
    /* Enhanced ag-grid styling */
    .ag-theme-alpine-dark {
        --ag-background-color: #2d2d2d;
        --ag-border-color: #404040;
        --ag-header-background-color: #3a3a3a;
        --ag-odd-row-background-color: #2d2d2d;
        --ag-row-hover-color: #3a3a3a;
        --ag-header-column-separator-color: #ff8c42;
        border-radius: 12px;
        border: 1px solid #404040;
    }
</style>""", unsafe_allow_html=True)

# Initialize the Groq client
@st.cache_resource
def init_groq_client():
    return Groq(api_key="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")

# Database connection pool
@st.cache_resource
def init_db_pool():
    try:
        return SimpleConnectionPool(
            1, 10,
            "postgresql://neondb_owner:npg_qV9a3dQRAeBm@ep-still-field-a17hi4xm-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"
        )
    except Exception as e:
        logger.error(f"Database connection pool failed: {e}")
        st.warning(f"Database connection pool failed: {e}. Using sample data.")
        return None

# Sample ARGO float data (enhanced from the original HTML)
@st.cache_data
def get_sample_argo_data():
    np.random.seed(42)
    
    # Indian Ocean focused data
    indian_ocean_floats = [
        {'id': '2902755', 'lat': 15.234, 'lon': 68.456, 'temp': 28.5, 'salinity': 35.2, 'depth': 1847, 'status': 'Active'},
        {'id': '2902756', 'lat': 12.891, 'lon': 72.123, 'temp': 29.1, 'salinity': 34.8, 'depth': 1923, 'status': 'Active'},
        {'id': '2902757', 'lat': 8.567, 'lon': 76.789, 'temp': 30.2, 'salinity': 34.5, 'depth': 1756, 'status': 'Active'},
        {'id': '2902758', 'lat': 18.234, 'lon': 84.567, 'temp': 27.8, 'salinity': 35.6, 'depth': 1998, 'status': 'Active'},
        {'id': '2902759', 'lat': 5.789, 'lon': 80.123, 'temp': 31.1, 'salinity': 34.2, 'depth': 1678, 'status': 'Active'},
        {'id': '2902760', 'lat': 22.456, 'lon': 88.789, 'temp': 26.5, 'salinity': 35.8, 'depth': 2034, 'status': 'Active'},
        {'id': '2902761', 'lat': 13.678, 'lon': 65.234, 'temp': 28.9, 'salinity': 35.1, 'depth': 1845, 'status': 'Active'},
        {'id': '2902762', 'lat': 9.345, 'lon': 79.567, 'temp': 29.8, 'salinity': 34.6, 'depth': 1712, 'status': 'Active'},
    ]
    
    # Create expanded dataset
    all_floats = []
    base_time = datetime.now()
    
    for i, float_data in enumerate(indian_ocean_floats):
        for cycle in range(1, 51):  # 50 cycles per float
            measurement_time = base_time - timedelta(days=np.random.randint(0, 365))
            
            all_floats.append({
                'platform_number': float_data['id'],
                'cycle_number': cycle,
                'measurement_time': measurement_time,
                'latitude': float_data['lat'] + np.random.normal(0, 0.1),
                'longitude': float_data['lon'] + np.random.normal(0, 0.1),
                'pressure': np.random.uniform(0, float_data['depth']),
                'temperature': float_data['temp'] + np.random.normal(0, 2),
                'salinity': float_data['salinity'] + np.random.normal(0, 0.5),
                'region': 'Indian Ocean'
            })
    
    return pd.DataFrame(all_floats)

# Database connection function with connection pool
def get_db_connection():
    pool = init_db_pool()
    if pool is None:
        return None
    
    try:
        conn = pool.getconn()
        return conn
    except Exception as e:
        logger.error(f"Failed to get connection from pool: {e}")
        st.warning(f"Database connection failed: {e}. Using sample data.")
        return None

# Enhanced Cesium component with proper configuration
def create_enhanced_cesium_map(float_data):
    cesium_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <script src="https://cesium.com/downloads/cesiumjs/releases/1.95/Build/Cesium/Cesium.js"></script>
        <link href="https://cesium.com/downloads/cesiumjs/releases/1.95/Build/Cesium/Widgets/widgets.css" rel="stylesheet">
        <style>
            html, body, #cesiumContainer {{
                width: 100%; height: 100%; margin: 0; padding: 0; overflow: hidden;
                font-family: 'Inter', sans-serif;
                background: #1a1a1a;
            }}
            
            .cesium-widget-credits {{ display: none !important; }}
            
            .metrics-overlay {{
                position: absolute;
                top: 20px;
                right: 20px;
                background: rgba(45, 45, 45, 0.95);
                padding: 15px;
                border-radius: 10px;
                border: 1px solid #404040;
                color: white;
                font-size: 12px;
                min-width: 200px;
            }}
            
            .metric {{
                display: flex;
                justify-content: space-between;
                margin-bottom: 8px;
            }}
            
            .metric-label {{ color: #888; }}
            .metric-value {{ color: #ff8c42; font-weight: 600; }}
            
            .sample-queries {{
                position: absolute;
                bottom: 20px;
                left: 20px;
                background: rgba(45, 45, 45, 0.95);
                padding: 15px;
                border-radius: 10px;
                border: 1px solid #404040;
                max-width: 300px;
                color: white;
            }}
            
            .sample-query {{
                background: #3a3a3a;
                padding: 8px 12px;
                margin: 5px 0;
                border-radius: 6px;
                cursor: pointer;
                font-size: 12px;
                transition: all 0.2s;
            }}
            
            .sample-query:hover {{
                background: #4a4a4a;
                color: #ff8c42;
            }}
        </style>
    </head>
    <body>
        <div id="cesiumContainer"></div>
        
        
        
        
        
        <script>
            // Set your Cesium Ion token
            Cesium.Ion.defaultAccessToken = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJqdGkiOiI3YTEzNTA0Yy0zYTQ5LTRiNDktYjNlOC03Y2ZkMTVkZDYyZjgiLCJpZCI6MzM2ODU4LCJpYXQiOjE3NTY2MTYxMjZ9.0vZQSC8KBvZBEHEleN_4V7T4CMYcyRQz4M5dZm4bARo';
            
            // Initialize the Cesium Viewer
            const viewer = new Cesium.Viewer('cesiumContainer', {{
                terrainProvider: Cesium.createWorldTerrain(),
                baseLayerPicker: true,
                geocoder: true,
                homeButton: true,
                sceneModePicker: true,
                navigationHelpButton: false,
                animation: false,
                timeline: false,
                fullscreenButton: true,
                vrButton: false,
                infoBox: true,
                selectionIndicator: true
            }});
            
            // Set initial view to India with proper coordinates
            viewer.camera.setView({{
                destination: Cesium.Rectangle.fromDegrees(65.0, 5.0, 95.0, 35.0), // India bounding box
                orientation: {{
                    heading: Cesium.Math.toRadians(0.0),
                    pitch: Cesium.Math.toRadians(-90.0),
                    roll: 0.0
                }}
            }});
            
            // Ensure the globe is visible
            viewer.scene.globe.show = true;
            viewer.scene.globe.enableLighting = true;
            
            // Float data from Python
            const floatData = {json.dumps(float_data)};
            
            // Add float markers
            floatData.forEach(float => {{
                // Color based on temperature
                let color;
                if (float.temp > 30) color = Cesium.Color.RED;
                else if (float.temp > 28) color = Cesium.Color.ORANGE;
                else if (float.temp > 26) color = Cesium.Color.YELLOW;
                else if (float.temp > 24) color = Cesium.Color.LIGHTGREEN;
                else color = Cesium.Color.LIGHTBLUE;
                
                const entity = viewer.entities.add({{
                    position: Cesium.Cartesian3.fromDegrees(float.lon, float.lat),
                    point: {{
                        pixelSize: 12,
                        color: color,
                        outlineColor: Cesium.Color.WHITE,
                        outlineWidth: 2,
                        heightReference: Cesium.HeightReference.CLAMP_TO_GROUND,
                        scaleByDistance: new Cesium.NearFarScalar(1.5e2, 1.5, 1.5e7, 0.5)
                    }},
                    label: {{
                        text: `Float ${{float.id}}`,
                        font: '12px sans-serif',
                        fillColor: Cesium.Color.WHITE,
                        outlineColor: Cesium.Color.BLACK,
                        outlineWidth: 2,
                        style: Cesium.LabelStyle.FILL_AND_OUTLINE,
                        verticalOrigin: Cesium.VerticalOrigin.BOTTOM,
                        pixelOffset: new Cesium.Cartesian2(0, -32),
                        show: false
                    }},
                    description: `
                        <div style="background: #2d2d2d; padding: 15px; border-radius: 8px; color: white; font-family: 'Inter', sans-serif;">
                            <h3 style="color: #ff8c42; margin-bottom: 10px;">ARGO Float ${{float.id}}</h3>
                            <p><strong>Temperature:</strong> ${{float.temp}}°C</p>
                            <p><strong>Salinity:</strong> ${{float.salinity}} PSU</p>
                            <p><strong>Max Depth:</strong> ${{float.depth}}m</p>
                            <p><strong>Status:</strong> ${{float.status}}</p>
                            <p><strong>Location:</strong> ${{float.lat.toFixed(3)}}°N, ${{float.lon.toFixed(3)}}°E</p>
                        </div>
                    `
                }});
            }});
            
            // Handle entity selection
            viewer.selectedEntityChanged.addEventListener((entity) => {{
                if (entity && entity.label) {{
                    entity.label.show = true;
                }}
            }});
            
            // Update metrics periodically
            setInterval(() => {{
                const hours = Math.floor(Math.random() * 12) + 1;
                document.getElementById('lastUpdate').textContent = hours + ' hours ago';
            }}, 30000);
        </script>
    </body>
    </html>
    """
    return cesium_html

# System prompt for LLM (from the original code)
system_prompt = """
You are FloatChat, an AI assistant for querying an ARGO ocean database. Your purpose is to translate natural language queries into precise PostgreSQL queries.

Database Schema for table 'argo_floats':
- platform_number (TEXT): The unique ID of the float (e.g., '2902743')
- cycle_number (INTEGER): The profile number from the float
- measurement_time (TIMESTAMP): UTC time of the observation. Use for all time filters
- latitude (FLOAT), longitude (FLOAT): Use for all location filters
- pressure (FLOAT): Depth in decibars (~meters). Lower values are shallower
- temperature (FLOAT): in °C
- salinity (FLOAT): Practical Salinity Units (PSU)
- region (TEXT): Pre-set region like 'Indian Ocean'

IMPORTANT LOCATIONS (latitude, longitude):
- Chennai, India: (13.0825, 80.2707)
- Mumbai, India: (19.0760, 72.8777)
- Kochi, India: (9.9312, 76.2673)
- Andaman Islands: (11.7401, 92.6586)
- Lakshadweep Islands: (10.5667, 72.6417)

RULES:
1. Your output MUST be structured as:
   <response>[Natural language explanation of the query]</response>
   <sql>[Valid PostgreSQL SELECT query]</sql>

2. For ALL queries:
   - Include a LIMIT clause (default LIMIT 100 unless user specifies "all" or similar)
   - Use appropriate WHERE clauses for filtering
   - Select only necessary columns (use * only when specifically requested)

Now, generate the appropriate response and SQL query for the following request:
"""

def extract_sql(response):
    sql_match = re.search(r'<sql>(.*?)</sql>', response, re.DOTALL)
    if sql_match:
        return sql_match.group(1).strip()
    return None

# Input sanitization function
def sanitize_input(user_input):
    return html.escape(user_input.strip())

# Enhanced execute_sql_query with better error handling
def execute_sql_query(sql_query):
    conn = get_db_connection()
    if conn is None:
        # Use sample data and simulate query execution
        df = get_sample_argo_data()
        try:
            # Simple query simulation for common patterns
            if "temperature" in sql_query.lower() and ">" in sql_query:
                temp_threshold = float(re.findall(r'temperature\s*>\s*(\d+(?:\.\d+)?)', sql_query.lower())[0])
                df = df[df['temperature'] > temp_threshold]
            elif "salinity" in sql_query.lower() and ">" in sql_query:
                sal_threshold = float(re.findall(r'salinity\s*>\s*(\d+(?:\.\d+)?)', sql_query.lower())[0])
                df = df[df['salinity'] > sal_threshold]
            elif "recent" in sql_query.lower() or "last" in sql_query.lower():
                df = df[df['measurement_time'] > (datetime.now() - timedelta(days=7))]
            
            return df.head(100)
        except Exception as e:
            logger.error(f"Error simulating query: {e}")
            return df.head(100)
    
    try:
        df = pd.read_sql_query(sql_query, conn)
        # Return connection to pool
        pool = init_db_pool()
        if pool:
            pool.putconn(conn)
        return df
    except Exception as e:
        logger.error(f"Error executing SQL query: {e}")
        st.error(f"Error executing SQL query: {e}")
        # Provide helpful suggestions based on error type
        if "syntax" in str(e).lower():
            st.info("Try simplifying your query or check for syntax errors")
        
        # Return connection to pool in case of error
        pool = init_db_pool()
        if pool:
            pool.putconn(conn)
        return get_sample_argo_data().head(100)

# Cached and rate-limited version of process_user_query
@lru_cache(maxsize=100)
@st.cache_data(ttl=300)  # Cache for 5 minutes
def process_user_query_cached(user_query):
    # Add a small delay to prevent rate limiting
    time.sleep(0.5)
    return process_user_query(user_query)

def process_user_query(user_query):
    try:
        groq_client = init_groq_client()
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_query}
        ]
        
        with st.spinner("Generating SQL query..."):
            completion = groq_client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=messages,
                temperature=0.1,
                max_tokens=1024
            )
        
        llm_response = completion.choices[0].message.content
        sql_query = extract_sql(llm_response)
        
        if not sql_query:
            st.error("Could not generate a valid SQL query for your request.")
            return None, None, None
        
        with st.spinner("Executing query..."):
            df = execute_sql_query(sql_query)
        
        if df is None or df.empty:
            st.warning("No data found for your query.")
            return None, None, None
        
        response_match = re.search(r'<response>(.*?)</response>', llm_response, re.DOTALL)
        natural_response = response_match.group(1).strip() if response_match else "Here are the results:"
        
        return natural_response, df, sql_query
        
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        st.error(f"Error processing request: {str(e)}")
        return None, None, None

# NASA PODAAC API Integration
def get_nasa_datasets():
    """Fetch available NASA PODAAC datasets"""
    try:
        url = "https://cmr.earthdata.nasa.gov/search/collections.json"
        params = {
            'provider': 'PODAAC',
            'has_granules': 'true',
            'page_size': 10,
            'sort_key': 'start_date'
        }
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            return response.json().get('feed', {}).get('entry', [])
    except Exception as e:
        logger.error(f"Error fetching NASA datasets: {e}")
        st.error(f"Error fetching NASA datasets: {e}")
    return []

def search_satellite_data(dataset_id, bbox=None, temporal=None):
    """Search for satellite data granules"""
    try:
        url = "https://cmr.earthdata.nasa.gov/search/granules.json"
        params = {
            'collection_concept_id': dataset_id,
            'page_size': 20
        }
        
        if bbox:
            params['bounding_box'] = f"{bbox['west']},{bbox['south']},{bbox['east']},{bbox['north']}"
        
        if temporal:
            params['temporal'] = f"{temporal['start']},{temporal['end']}"
        
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            return response.json().get('feed', {}).get('entry', [])
    except Exception as e:
        logger.error(f"Error searching satellite data: {e}")
        st.error(f"Error searching satellite data: {e}")
    return []

def create_correlation_analysis(argo_data, satellite_data=None):
    """Create correlation analysis between ARGO and satellite data"""
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('Temperature vs Salinity', 'Temperature vs Depth', 
                       'Temporal Temperature Trends', 'Geographic Distribution'),
        specs=[[{"type": "scatter"}, {"type": "scatter"}],
               [{"type": "scatter"}, {"type": "mapbox"}]]
    )
    
    # Temperature vs Salinity scatter
    fig.add_trace(
        go.Scatter(x=argo_data['temperature'], y=argo_data['salinity'],
                  mode='markers', name='ARGO Data',
                  marker=dict(color='#ff8c42', size=6)),
        row=1, col=1
    )
    
    # Temperature vs Depth
    fig.add_trace(
        
        go.Scatter(x=argo_data['temperature'], y=argo_data['pressure'],
                  mode='markers', name='Temp vs Depth',
                  marker=dict(color='#ff6b35', size=6)),
        row=1, col=2
    )
    
    # Temporal trends
    if 'measurement_time' in argo_data.columns:
        daily_temp = argo_data.groupby(argo_data['measurement_time'].dt.date)['temperature'].mean()
        fig.add_trace(
            go.Scatter(x=daily_temp.index, y=daily_temp.values,
                      mode='lines+markers', name='Daily Avg Temp',
                      line=dict(color='#10b981')),
            row=2, col=1
        )
    
    # Geographic distribution
    if 'latitude' in argo_data.columns and 'longitude' in argo_data.columns:
        fig.add_trace(
            go.Scattermapbox(
                lat=argo_data['latitude'], lon=argo_data['longitude'],
                mode='markers', name='Float Locations',
                marker=dict(size=8, color=argo_data['temperature'],
                           colorscale='RdYlBu_r', showscale=True)),
            row=2, col=2
        )
    
    fig.update_layout(
        height=800,
        title_text="ARGO Data Analysis Dashboard",
        showlegend=True,
        mapbox=dict(style="carto-darkmatter", center=dict(lat=10, lon=75), zoom=3),
        paper_bgcolor='#2d2d2d',
        plot_bgcolor='#2d2d2d',
        font=dict(color='white')
    )
    
    return fig

def create_temperature_depth_profile(df):
    """Create temperature-depth profile visualization"""
    if 'temperature' not in df.columns or 'pressure' not in df.columns:
        return None
    
    fig = go.Figure()
    
    # Group by platform for different profiles
    for platform in df['platform_number'].unique()[:5]:  # Show top 5 platforms
        platform_data = df[df['platform_number'] == platform]
        fig.add_trace(go.Scatter(
            x=platform_data['temperature'],
            y=platform_data['pressure'],
            mode='lines+markers',
            name=f'Float {platform}',
            line=dict(width=2),
            marker=dict(size=4)
        ))
    
    fig.update_layout(
        title="Temperature-Depth Profiles",
        xaxis_title="Temperature (°C)",
        yaxis_title="Pressure (dbar)",
        yaxis=dict(autorange='reversed'),  # Depth increases downward
        paper_bgcolor='#2d2d2d',
        plot_bgcolor='#2d2d2d',
        font=dict(color='white'),
        height=500
    )
    
    return fig

def create_geographic_heatmap(df):
    """Create geographic heatmap of measurements"""
    if 'latitude' not in df.columns or 'longitude' not in df.columns:
        return None
    
    # Use the new mapbox_style parameter with MapLibre styles
    fig = px.density_mapbox(
        df, lat='latitude', lon='longitude',
        z='temperature' if 'temperature' in df.columns else None,
        radius=20,
        center=dict(lat=df['latitude'].mean(), lon=df['longitude'].mean()),
        zoom=3,
        mapbox_style="carto-darkmatter",  # This should work with the new MapLibre backend
        color_continuous_scale="RdYlBu_r",
        title="Geographic Distribution of Measurements"
    )
    
    fig.update_layout(
        paper_bgcolor='#2d2d2d',
        font=dict(color='white'),
        height=500
    )
    
    return fig

# Tooltip component for better UX
def tooltip(text, help_text):
    st.markdown(f"""
    <div class="tooltip">
        {text}
        <span class="tooltiptext">{help_text}</span>
    </div>
    """, unsafe_allow_html=True)

# Main function with all enhancements
def main():
    # Initialize session state
    if 'query_history' not in st.session_state:
        st.session_state.query_history = []
    
    if 'chat_messages' not in st.session_state:
        st.session_state.chat_messages = []
    
    if 'chat_minimized' not in st.session_state:
        st.session_state.chat_minimized = False
    
    if 'realtime_updates' not in st.session_state:
        st.session_state.realtime_updates = False
    
    # Header (matching original design)
    st.markdown("""
    <div class="main-header">
        <h1 class="header-title">Marinex</h1>
        <p class="header-subtitle">AI-Powered ARGO Float Discovery & Analysis Platform</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Get sample data for display
    sample_data = get_sample_argo_data()
    
    # Statistics grid (matching original style)
    unique_floats = sample_data['platform_number'].nunique()
    total_records = len(sample_data)
    recent_data = len(sample_data[sample_data['measurement_time'] > (datetime.now() - timedelta(days=1))])
    avg_temp = sample_data['temperature'].mean()
    
    st.markdown(f"""
    <div class="stats-grid">
        <div class="metric-card">
            <div class="metric-label">Active Floats</div>
            <div class="metric-value">{unique_floats}</div>
            <div class="metric-description">Currently deployed platforms</div>
        </div>
        <div class="metric-card">
            <div class="metric-label">Total Records</div>
            <div class="metric-value">{total_records:,}</div>
            <div class="metric-description">Oceanographic measurements</div>
        </div>
        <div class="metric-card">
            <div class="metric-label">Recent Data</div>
            <div class="metric-value"><span class="live-indicator"></span>{recent_data}</div>
            <div class="metric-description">Last 24 hours</div>
        </div>
        <div class="metric-card">
            <div class="metric-label">Avg Temperature</div>
            <div class="metric-value">{avg_temp:.1f}°C</div>
            <div class="metric-description">Current ocean conditions</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Real-time updates toggle
    col1, col2 = st.columns([3, 1])
    with col2:
        if st.button("🔄 Enable Real-time Updates" if not st.session_state.realtime_updates else "⏹️ Disable Real-time Updates"):
            st.session_state.realtime_updates = not st.session_state.realtime_updates
            st.rerun()
    
    # Enhanced 3D Globe Visualization
    st.markdown('<div class="panel-title">🌍 Global ARGO Float Network - 3D Visualization</div>', unsafe_allow_html=True)
    
    # Prepare data for Cesium (using latest position for each float)
    latest_positions = sample_data.groupby('platform_number').last().reset_index()
    float_data_for_cesium = []
    
    for _, row in latest_positions.iterrows():
        float_data_for_cesium.append({
            'id': row['platform_number'],
            'lat': row['latitude'],
            'lon': row['longitude'],
            'temp': round(row['temperature'], 1),
            'salinity': round(row['salinity'], 1),
            'depth': 2000,  # Approximate max depth
            'status': 'Active'
        })
    
    # Create and display Cesium map
    cesium_html = create_enhanced_cesium_map(float_data_for_cesium)
    components.html(cesium_html, height=600)
    
    # AI Chat Interface
 
    
    # Query input with tooltip
    col1, col2 = st.columns([4, 1])
    with col1:
        user_query = st.text_input(
            "Ask about ARGO floats, oceanographic data, or specific analyses:",
            placeholder="e.g., Show temperature profiles near Chennai",
            key="main_query"
        )
    
    with col2:
        execute_query = st.button("🔍 Execute", key="execute_main", help="Execute your query")
        tooltip("💡", "Ask natural language questions about ARGO float data")
    
    # Sample queries (matching original design)
    st.markdown("**Sample Queries:**")
    
    sample_queries = [
        "Show floats near Arabian Sea",
        "Temperature above 28°C", 
        "Salinity profiles in Indian Ocean",
        "Recent measurements from last week"
    ]
    
    query_cols = st.columns(len(sample_queries))
    selected_sample = None
    
    for i, query in enumerate(sample_queries):
        with query_cols[i]:
            if st.button(query, key=f"sample_{i}"):
                selected_sample = query
    
    # Process selected sample query
    if selected_sample:
        user_query = selected_sample
        execute_query = True
    
    # Process query if submitted
    if execute_query and user_query:
        # Sanitize input
        user_query = sanitize_input(user_query)
        
        # Add to query history
        st.session_state.query_history.append({
            'query': user_query,
            'timestamp': datetime.now()
        })
        
        # Process query with caching
        natural_response, df, sql_query = process_user_query_cached(user_query)
        
        if df is not None:
            # Display results
            st.markdown(f"""
            <div class="data-panel">
                <div class="panel-title"> Query Results</div>
                <p style=" margin-bottom: 1rem;">{natural_response}</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Results tabs
            tab1, tab2, tab3, tab4 = st.tabs([" Data Table", "🗺️ Geographic View", "📈 Analysis", "🔬 Advanced"])
            
            with tab1:
               
                # Show SQL query
                if sql_query:
                    with st.expander("View Generated SQL Query"):
                        st.code(sql_query, language="sql")
                
                # Data summary
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Records Found", len(df))
                with col2:
                    if 'temperature' in df.columns:
                        st.metric("Avg Temperature", f"{df['temperature'].mean():.1f}°C")
                with col3:
                    if 'platform_number' in df.columns:
                        st.metric("Unique Floats", df['platform_number'].nunique())
                
                # Data table with pagination
                st.subheader("Data Results")
                display_dataframe_with_pagination(df)
                
                # Download button
                csv = df.to_csv(index=False)
                st.download_button(
                    label="📥 Download Results as CSV",
                    data=csv,
                    file_name=f"argo_query_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
                
                st.markdown('</div>', unsafe_allow_html=True)
            
            with tab2:
                st.markdown('<div class="data-panel">', unsafe_allow_html=True)
                
                if 'latitude' in df.columns and 'longitude' in df.columns:
                    # Create Folium map for query results
                    center_lat = df['latitude'].mean()
                    center_lon = df['longitude'].mean()
                    
                    m = folium.Map(
                        location=[center_lat, center_lon],
                        zoom_start=5,
                        tiles='CartoDB dark_matter'
                    )
                    
                    # Add markers with color coding based on temperature
                    for _, row in df.iterrows():
                        # Color based on temperature if available
                        if 'temperature' in df.columns:
                            temp = row['temperature']
                            if temp > 30:
                                color = 'red'
                            elif temp > 28:
                                color = 'orange'
                            elif temp > 26:
                                color = 'yellow'
                            elif temp > 24:
                                color = 'lightgreen'
                            else:
                                color = 'lightblue'
                        else:
                            color = 'blue'
                        
                        popup_text = f"""
                        <div style="font-family: 'Inter', sans-serif; min-width: 200px;">
                            <b>Float {row.get('platform_number', 'N/A')}</b><br>
                            <hr style="margin: 5px 0;">
                            <b>Temperature:</b> {row.get('temperature', 'N/A')}°C<br>
                            <b>Salinity:</b> {row.get('salinity', 'N/A')} PSU<br>
                            <b>Pressure:</b> {row.get('pressure', 'N/A')} dbar<br>
                            <b>Time:</b> {row.get('measurement_time', 'N/A')}
                        </div>
                        """
                        
                        folium.CircleMarker(
                            [row['latitude'], row['longitude']],
                            radius=8,
                            color='white',
                            fillColor=color,
                            fillOpacity=0.8,
                            weight=2,
                            popup=folium.Popup(popup_text, max_width=300)
                        ).add_to(m)
                    
                    # Display map
                    folium_static(m, width=None, height=500)
                    
                    # Geographic heatmap
                    if len(df) > 10:
                        st.subheader("Data Density Heatmap")
                        heatmap_fig = create_geographic_heatmap(df)
                        if heatmap_fig:
                            st.plotly_chart(heatmap_fig, use_container_width=True)
                else:
                    st.info("Geographic coordinates not available for mapping.")
                
                st.markdown('</div>', unsafe_allow_html=True)
            
            with tab3:
                st.markdown('<div class="data-panel">', unsafe_allow_html=True)
                
                # Create analysis visualizations
                if len(df) > 0:
                    # Temperature-Depth Profile
                    if 'temperature' in df.columns and 'pressure' in df.columns:
                        st.subheader("Temperature-Depth Profiles")
                        profile_fig = create_temperature_depth_profile(df)
                        if profile_fig:
                            st.plotly_chart(profile_fig, use_container_width=True)
                    
                    # Statistical summary
                    st.subheader("Statistical Summary")
                    numeric_cols = df.select_dtypes(include=[np.number]).columns
                    if len(numeric_cols) > 0:
                        stats_df = df[numeric_cols].describe()
                        st.dataframe(stats_df, use_container_width=True)
                    
                    # Correlation analysis
                    if len(numeric_cols) > 1:
                        st.subheader("Correlation Analysis")
                        correlation_fig = create_correlation_analysis(df)
                        st.plotly_chart(correlation_fig, use_container_width=True)
                    
                    # Time series analysis if temporal data exists
                    if 'measurement_time' in df.columns:
                        st.subheader("Temporal Analysis")
                        
                        # Daily averages
                        if 'temperature' in df.columns:
                            daily_data = df.groupby(df['measurement_time'].dt.date).agg({
                                'temperature': 'mean',
                                'salinity': 'mean' if 'salinity' in df.columns else lambda x: None
                            }).reset_index()
                            
                            fig = go.Figure()
                            fig.add_trace(go.Scatter(
                                x=daily_data['measurement_time'],
                                y=daily_data['temperature'],
                                mode='lines+markers',
                                name='Temperature',
                                line=dict(color='#ff8c42')
                            ))
                            
                            fig.update_layout(
                                title="Daily Temperature Trends",
                                xaxis_title="Date",
                                yaxis_title="Temperature (°C)",
                                paper_bgcolor='#2d2d2d',
                                plot_bgcolor='#2d2d2d',
                                font=dict(color='white'),
                                height=400
                            )
                            
                            st.plotly_chart(fig, use_container_width=True)
                
                st.markdown('</div>', unsafe_allow_html=True)
            
            with tab4:
                st.markdown('<div class="data-panel">', unsafe_allow_html=True)
                st.subheader("Advanced Analysis & NASA Integration")
                
                # NASA PODAAC Integration
                st.markdown("""
                <div class="nasa-panel">
                    <h3>🛰️ NASA PODAAC Satellite Data Integration</h3>
                    <p>Correlate ARGO float measurements with satellite observations for comprehensive ocean analysis.</p>
                </div>
                """, unsafe_allow_html=True)
                
                nasa_col1, nasa_col2 = st.columns(2)
                
                with nasa_col1:
                    if st.button("🔍 Browse NASA Datasets", key="browse_nasa"):
                        with st.spinner("Fetching NASA datasets..."):
                            datasets = get_nasa_datasets()
                            if datasets:
                                st.success(f"Found {len(datasets)} datasets")
                                for i, dataset in enumerate(datasets[:5]):
                                    with st.expander(f"Dataset {i+1}: {dataset.get('title', 'Unknown')}"):
                                        st.write(f"**Provider:** {dataset.get('data_center', 'N/A')}")
                                        st.write(f"**Summary:** {dataset.get('summary', 'No description available')[:200]}...")
                                        if 'id' in dataset:
                                            st.code(dataset['id'])
                            else:
                                st.warning("No datasets found or API unavailable")
                
                with nasa_col2:
                    st.info("""
                    **Available NASA Data Types:**
                    - Sea Surface Temperature (SST)
                    - Sea Surface Height (SSH) 
                    - Ocean Color (Chlorophyll)
                    - Sea Surface Salinity (SSS)
                    - Ocean Wind Speed
                    """)
                
                # Advanced analytics options
                st.subheader("Advanced Analytics Options")
                
                analysis_options = st.multiselect(
                    "Select analysis types:",
                    ["Machine Learning Clustering", "Anomaly Detection", "Predictive Modeling", 
                     "Spectral Analysis", "Cross-correlation with Satellite Data"],
                    default=[]
                )
                
                if "Machine Learning Clustering" in analysis_options:
                    if len(df) > 20 and 'temperature' in df.columns and 'salinity' in df.columns:
                        from sklearn.cluster import KMeans
                        from sklearn.preprocessing import StandardScaler
                        
                        # Prepare data for clustering
                        features = df[['temperature', 'salinity']].dropna()
                        scaler = StandardScaler()
                        features_scaled = scaler.fit_transform(features)
                        
                        # K-means clustering
                        n_clusters = st.slider("Number of clusters:", 2, 8, 3)
                        kmeans = KMeans(n_clusters=n_clusters, random_state=42)
                        clusters = kmeans.fit_predict(features_scaled)
                        
                        # Visualization
                        fig = px.scatter(
                            features, x='temperature', y='salinity', 
                            color=clusters, title="Water Mass Clustering Analysis",
                            color_continuous_scale='viridis'
                        )
                        fig.update_layout(
                            paper_bgcolor='#2d2d2d',
                            plot_bgcolor='#2d2d2d',
                            font=dict(color='white')
                        )
                        st.plotly_chart(fig, use_container_width=True)
                
                if "Anomaly Detection" in analysis_options:
                    if 'temperature' in df.columns:
                        # Simple anomaly detection using IQR
                        Q1 = df['temperature'].quantile(0.25)
                        Q3 = df['temperature'].quantile(0.75)
                        IQR = Q3 - Q1
                        lower_bound = Q1 - 1.5 * IQR
                        upper_bound = Q3 + 1.5 * IQR
                        
                        anomalies = df[(df['temperature'] < lower_bound) | (df['temperature'] > upper_bound)]
                        
                        if len(anomalies) > 0:
                            st.warning(f"🚨 Found {len(anomalies)} temperature anomalies")
                            st.dataframe(anomalies[['platform_number', 'temperature', 'measurement_time']], use_container_width=True)
                        else:
                            st.success("✅ No significant temperature anomalies detected")
                
                # Export options
                st.subheader("Export & Integration")
                export_col1, export_col2, export_col3 = st.columns(3)
                
                with export_col1:
                    if st.button("📊 Export to NetCDF"):
                        st.info("NetCDF export functionality would be implemented here")
                
                with export_col2:
                    if st.button("🔗 Generate API Endpoint"):
                        st.info("API endpoint generation would be implemented here")
                
                with export_col3:
                    if st.button("📧 Schedule Report"):
                        st.info("Report scheduling functionality would be implemented here")
                
                st.markdown('</div>', unsafe_allow_html=True)
    
    # Query History Sidebar
    with st.sidebar:
        st.markdown("### 📋 Query History")
        if st.session_state.query_history:
            for i, query_item in enumerate(reversed(st.session_state.query_history[-10:])):
                with st.expander(f"Query {len(st.session_state.query_history) - i}"):
                    st.write(f"**Query:** {query_item['query']}")
                    st.write(f"**Time:** {query_item['timestamp'].strftime('%Y-%m-%d %H:%M')}")
                    if st.button("🔄 Run Again", key=f"rerun_{i}"):
                        st.session_state.main_query = query_item['query']
                        st.rerun()
        else:
            st.info("No queries yet. Try asking something above!")
        
        # API Status
        st.markdown("### 🔌 System Status")
        
        # Database status
        pool = init_db_pool()
        if pool:
            db_status = "🟢 Connected"
        else:
            db_status = "🟡 Sample Data"
        
        st.markdown(f"**Database:** {db_status}")
        st.markdown("**AI Model:** 🟢 Online")
        st.markdown("**NASA API:** 🟢 Available")
        st.markdown("**Cesium Maps:** 🟢 Active")
        
        # Help section
        st.markdown("### ❓ Help & Tips")
        with st.expander("How to use this platform"):
            st.write("""
            1. **Ask questions** in natural language about ARGO float data
            2. **Explore results** through interactive visualizations
            3. **Download data** for further analysis
            4. **Use sample queries** to get started quickly
            """)
        
        with st.expander("Sample query examples"):
            st.write("""
            - "Show floats near Chennai"
            - "Temperature above 28°C"
            - "Salinity profiles from last month"
            - "Deepest measurements in Indian Ocean"
            """)

# Function to display dataframe with pagination
def display_dataframe_with_pagination(df):
    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_pagination(paginationAutoPageSize=True)
    gb.configure_side_bar()
    gb.configure_selection('multiple', use_checkbox=True, groupSelectsChildren="Group checkbox select children")
    gridOptions = gb.build()
    
    AgGrid(df, gridOptions=gridOptions, enable_enterprise_modules=True, height=400)

if __name__ == "__main__":
    main()
