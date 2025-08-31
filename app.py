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

# Enhanced CSS with vibrant colors and dynamic animations
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
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600&display=swap');
    
    /* Global styles */
    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        box-sizing: border-box;
    }
    
    /* Enhanced main header with vibrant gradient */
    .main-header {
        background: linear-gradient(135deg, #ff6b6b 0%, #4ecdc4 25%, #45b7d1 50%, #96ceb4 75%, #ffeaa7 100%);
        background-size: 400% 400%;
        animation: gradientShift 8s ease-in-out infinite;
        padding: 3rem;
        border-radius: 20px;
        margin-bottom: 2rem;
        color: white;
        box-shadow: 0 20px 60px rgba(255, 107, 107, 0.3);
        position: relative;
        overflow: hidden;
        border: none;
        transform: perspective(1000px) rotateX(2deg);
    }
    
    @keyframes gradientShift {
        0%, 100% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
    }
    
    .main-header::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: url("data:image/svg+xml,%3Csvg width='100' height='100' viewBox='0 0 100 100' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath d='M11 18c3.866 0 7-3.134 7-7s-3.134-7-7-7-7 3.134-7 7 3.134 7 7 7zm48 25c3.866 0 7-3.134 7-7s-3.134-7-7-7-7 3.134-7 7 3.134 7 7 7zm-43-7c1.657 0 3-1.343 3-3s-1.343-3-3-3-3 1.343-3 3 1.343 3 3 3zm63 31c1.657 0 3-1.343 3-3s-1.343-3-3-3-3 1.343-3 3 1.343 3 3 3zM34 90c1.657 0 3-1.343 3-3s-1.343-3-3-3-3 1.343-3 3 1.343 3 3 3zm56-76c1.657 0 3-1.343 3-3s-1.343-3-3-3-3 1.343-3 3 1.343 3 3 3zM12 86c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm28-65c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm23-11c2.76 0 5-2.24 5-5s-2.24-5-5-5-5 2.24-5 5 2.24 5 5 5zm-6 60c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm29 22c2.76 0 5-2.24 5-5s-2.24-5-5-5-5 2.24-5 5 2.24 5 5 5zM32 63c2.76 0 5-2.24 5-5s-2.24-5-5-5-5 2.24-5 5 2.24 5 5 5zm57-13c2.76 0 5-2.24 5-5s-2.24-5-5-5-5 2.24-5 5 2.24 5 5 5zm-9-21c1.105 0 2-.895 2-2s-.895-2-2-2-2 .895-2 2 .895 2 2 2zM60 91c1.105 0 2-.895 2-2s-.895-2-2-2-2 .895-2 2 .895 2 2 2zM35 41c1.105 0 2-.895 2-2s-.895-2-2-2-2 .895-2 2 .895 2 2 2zM12 60c1.105 0 2-.895 2-2s-.895-2-2-2-2 .895-2 2 .895 2 2 2z' fill='%23ffffff' fill-opacity='0.08' fill-rule='evenodd'/%3E%3C/svg%3E");
        animation: floatPattern 20s linear infinite;
    }
    
    @keyframes floatPattern {
        0% { transform: translateX(0) translateY(0); }
        25% { transform: translateX(-10px) translateY(-5px); }
        50% { transform: translateX(10px) translateY(-10px); }
        75% { transform: translateX(-5px) translateY(-5px); }
        100% { transform: translateX(0) translateY(0); }
    }
    
    .header-title {
        font-size: 3.2rem;
        font-weight: 900;
        margin: 0 0 0.5rem 0;
        letter-spacing: -0.03em;
        text-shadow: 0 4px 8px rgba(0,0,0,0.3);
        position: relative;
        background: linear-gradient(45deg, #fff, #f0f0f0);
        background-clip: text;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: titleGlow 3s ease-in-out infinite alternate;
    }
    
    @keyframes titleGlow {
        0% { text-shadow: 0 4px 8px rgba(255,255,255,0.2); }
        100% { text-shadow: 0 4px 20px rgba(255,255,255,0.4); }
    }
    
    .header-subtitle {
        font-size: 1.3rem;
        font-weight: 500;
        opacity: 0.95;
        margin: 0;
        text-shadow: 0 2px 4px rgba(0,0,0,0.2);
        animation: subtitleFloat 4s ease-in-out infinite;
    }
    
    @keyframes subtitleFloat {
        0%, 100% { transform: translateY(0); }
        50% { transform: translateY(-3px); }
    }
    
    /* Enhanced stats grid with rainbow accent */
    .stats-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
        gap: 2rem;
        margin: 3rem 0;
    }
    
    .metric-card {
        background: linear-gradient(145deg, #2d2d2d, #1a1a1a);
        border-radius: 20px;
        padding: 2.5rem;
        color: white;
        border: 2px solid transparent;
        background-clip: padding-box;
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        position: relative;
        overflow: hidden;
        cursor: pointer;
    }
    
    .metric-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 5px;
        background: linear-gradient(90deg, #ff6b6b, #4ecdc4, #45b7d1, #96ceb4, #ffeaa7, #fd79a8);
        background-size: 200% 100%;
        animation: rainbowSlide 3s linear infinite;
    }
    
    @keyframes rainbowSlide {
        0% { background-position: 0% 0%; }
        100% { background-position: 200% 0%; }
    }
    
    .metric-card::after {
        content: '';
        position: absolute;
        top: -2px;
        left: -2px;
        right: -2px;
        bottom: -2px;
        background: linear-gradient(45deg, #ff6b6b, #4ecdc4, #45b7d1, #96ceb4, #ffeaa7, #fd79a8);
        background-size: 400% 400%;
        border-radius: 22px;
        z-index: -1;
        opacity: 0;
        animation: gradientRotate 6s ease infinite;
        transition: opacity 0.4s ease;
    }
    
    @keyframes gradientRotate {
        0%, 100% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
    }
    
    .metric-card:hover {
        transform: translateY(-8px) scale(1.02);
        box-shadow: 0 25px 50px rgba(255, 107, 107, 0.3);
    }
    
    .metric-card:hover::after {
        opacity: 1;
    }
    
    .metric-label {
        font-size: 0.9rem;
        font-weight: 700;
        color: #bbb;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
        gap: 0.6rem;
        transition: color 0.3s ease;
    }
    
    .metric-card:hover .metric-label {
        color: #4ecdc4;
    }
    
    .metric-value {
        font-size: 3rem;
        font-weight: 900;
        background: linear-gradient(45deg, #ff6b6b, #4ecdc4);
        background-clip: text;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        line-height: 1;
        margin-bottom: 0.8rem;
        text-shadow: 0 4px 8px rgba(0,0,0,0.3);
        transition: transform 0.3s ease;
    }
    
    .metric-card:hover .metric-value {
        transform: scale(1.05);
    }
    
    .metric-description {
        font-size: 1rem;
        color: #aaa;
        margin: 0;
        line-height: 1.6;
        transition: color 0.3s ease;
    }
    
    .metric-card:hover .metric-description {
        color: #ddd;
    }
    
    /* Dynamic live indicator */
    .live-indicator {
        display: inline-block;
        width: 12px;
        height: 12px;
        background: radial-gradient(circle, #10b981, #059669);
        border-radius: 50%;
        margin-right: 10px;
        animation: livePulse 2s ease-in-out infinite;
        box-shadow: 0 0 0 rgba(16, 185, 129, 0.6);
        position: relative;
    }
    
    .live-indicator::after {
        content: '';
        position: absolute;
        top: -2px;
        left: -2px;
        right: -2px;
        bottom: -2px;
        border-radius: 50%;
        background: radial-gradient(circle, transparent 40%, #10b981 80%);
        animation: livePulse 2s ease-in-out infinite 0.5s;
    }
    
    @keyframes livePulse {
        0% {
            transform: scale(0.8);
            box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.8);
        }
        50% {
            transform: scale(1.1);
            box-shadow: 0 0 0 15px rgba(16, 185, 129, 0);
        }
        100% {
            transform: scale(0.8);
            box-shadow: 0 0 0 0 rgba(16, 185, 129, 0);
        }
    }
    
    /* Spectacular button enhancements */
    .query-button {
        background: linear-gradient(135deg, #ff6b6b 0%, #4ecdc4 50%, #45b7d1 100%);
        background-size: 200% 200%;
        border: none;
        border-radius: 16px;
        padding: 1.2rem 2.5rem;
        color: white;
        font-weight: 700;
        cursor: pointer;
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        box-shadow: 0 8px 25px rgba(255, 107, 107, 0.4);
        font-size: 1.1rem;
        letter-spacing: 0.03em;
        text-transform: uppercase;
        position: relative;
        overflow: hidden;
        animation: buttonBreathe 3s ease-in-out infinite;
    }
    
    @keyframes buttonBreathe {
        0%, 100% { 
            background-position: 0% 50%;
            box-shadow: 0 8px 25px rgba(255, 107, 107, 0.4);
        }
        50% { 
            background-position: 100% 50%;
            box-shadow: 0 8px 25px rgba(78, 205, 196, 0.4);
        }
    }
    
    .query-button::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent);
        transition: left 0.6s ease;
    }
    
    .query-button:hover {
        transform: translateY(-6px) scale(1.05);
        box-shadow: 0 20px 40px rgba(255, 107, 107, 0.6);
        background-position: 100% 50%;
    }
    
    .query-button:hover::before {
        left: 100%;
    }
    
    .query-button:active {
        transform: translateY(-2px) scale(1.02);
        box-shadow: 0 8px 20px rgba(255, 107, 107, 0.5);
    }
    
    /* Enhanced Streamlit buttons */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border: none;
        border-radius: 14px;
        padding: 1rem 2rem;
        font-weight: 700;
        color: white;
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
        text-transform: uppercase;
        letter-spacing: 0.05em;
        position: relative;
        overflow: hidden;
    }
    
    .stButton > button::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
        transition: left 0.5s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-4px) scale(1.03);
        box-shadow: 0 15px 35px rgba(102, 126, 234, 0.6);
        background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
    }
    
    .stButton > button:hover::before {
        left: 100%;
    }
    
    .stButton > button:active {
        transform: translateY(-1px) scale(1.01);
    }
    
    /* Global styles */
    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        box-sizing: border-box;
    }
    
    /* Ocean animation background */
    body, .stApp {
        background: linear-gradient(180deg, #001122 0%, #003366 30%, #004080 60%, #0066cc 100%);
        position: relative;
        min-height: 100vh;
    }
    
    .stApp::before {
        content: '';
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: 
            radial-gradient(ellipse at 20% 50%, rgba(0, 100, 200, 0.3) 0%, transparent 50%),
            radial-gradient(ellipse at 80% 30%, rgba(0, 150, 255, 0.2) 0%, transparent 60%),
            radial-gradient(ellipse at 40% 80%, rgba(100, 200, 255, 0.1) 0%, transparent 50%);
        animation: oceanCurrent 20s ease-in-out infinite;
        pointer-events: none;
        z-index: -2;
    }
    
    .stApp::after {
        content: '';
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 200%;
        background-image: 
            repeating-linear-gradient(
                0deg,
                transparent,
                transparent 2px,
                rgba(255, 255, 255, 0.03) 2px,
                rgba(255, 255, 255, 0.03) 4px
            ),
            repeating-linear-gradient(
                90deg,
                transparent,
                transparent 2px,
                rgba(255, 255, 255, 0.02) 2px,
                rgba(255, 255, 255, 0.02) 4px
            );
        animation: oceanWaves 15s linear infinite;
        pointer-events: none;
        z-index: -1;
        transform: translateZ(0);
    }
    
    @keyframes oceanCurrent {
        0%, 100% { 
            transform: translateX(0) translateY(0) scale(1);
            filter: hue-rotate(0deg);
        }
        25% { 
            transform: translateX(-20px) translateY(-10px) scale(1.05);
            filter: hue-rotate(30deg);
        }
        50% { 
            transform: translateX(20px) translateY(-20px) scale(1.1);
            filter: hue-rotate(60deg);
        }
        75% { 
            transform: translateX(-10px) translateY(10px) scale(1.05);
            filter: hue-rotate(30deg);
        }
    }
    
    @keyframes oceanWaves {
        0% { transform: translateY(0) rotateZ(0deg); }
        100% { transform: translateY(-50px) rotateZ(1deg); }
    }
    
    /* Scroll-responsive ocean effect */
    .ocean-scroll-layer {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: 
            radial-gradient(circle at var(--mouse-x, 50%) var(--mouse-y, 50%), 
                rgba(0, 200, 255, 0.1) 0%, 
                transparent 50%),
            linear-gradient(45deg, 
                transparent 0%, 
                rgba(100, 200, 255, 0.05) 25%, 
                transparent 50%, 
                rgba(0, 150, 255, 0.05) 75%, 
                transparent 100%);
        background-size: 200px 200px, 400px 400px;
        animation: oceanFlow 25s linear infinite;
        pointer-events: none;
        z-index: -3;
        will-change: transform;
    }
    
    @keyframes oceanFlow {
        0% { 
            background-position: 0% 0%, 0% 0%;
            transform: translateY(0) scale(1);
        }
        25% { 
            background-position: 25% 25%, 100% 0%;
            transform: translateY(-10px) scale(1.02);
        }
        50% { 
            background-position: 50% 50%, 200% 100%;
            transform: translateY(-20px) scale(1.05);
        }
        75% { 
            background-position: 75% 25%, 100% 200%;
            transform: translateY(-10px) scale(1.02);
        }
        100% { 
            background-position: 100% 0%, 0% 300%;
            transform: translateY(0) scale(1);
        }
    }
    
    /* Floating bubbles effect */
    .bubble-layer {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-image: 
            radial-gradient(circle at 10% 20%, rgba(255, 255, 255, 0.1) 1px, transparent 1px),
            radial-gradient(circle at 20% 80%, rgba(200, 255, 255, 0.08) 2px, transparent 2px),
            radial-gradient(circle at 80% 40%, rgba(150, 220, 255, 0.06) 1.5px, transparent 1.5px),
            radial-gradient(circle at 40% 60%, rgba(255, 255, 255, 0.05) 1px, transparent 1px),
            radial-gradient(circle at 90% 10%, rgba(180, 240, 255, 0.07) 2px, transparent 2px);
        background-size: 300px 300px, 200px 200px, 400px 400px, 250px 250px, 350px 350px;
        animation: bubbleFloat 30s linear infinite;
        pointer-events: none;
        z-index: -4;
        opacity: 0.6;
    }
    
    @keyframes bubbleFloat {
        0% { 
            background-position: 0% 100%, 0% 0%, 0% 100%, 0% 0%, 0% 100%;
            transform: translateY(0);
        }
        100% { 
            background-position: 100% 0%, 100% 100%, 100% 0%, 100% 100%, 100% 0%;
            transform: translateY(-100px);
        }
    }
    
    .sample-query::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: linear-gradient(45deg, #ff6b6b, #4ecdc4, #45b7d1, #96ceb4);
        background-size: 400% 400%;
        opacity: 0;
        transition: opacity 0.4s ease;
        animation: gradientShift 4s ease infinite;
        z-index: -1;
    }
    
    .sample-query:hover {
        color: white;
        border-color: transparent;
        transform: translateY(-6px) scale(1.02);
        box-shadow: 0 20px 40px rgba(255, 107, 107, 0.3);
    }
    
    .sample-query:hover::before {
        opacity: 0.9;
    }
    
    /* Enhanced download button */
    .stDownloadButton > button {
        background: linear-gradient(135deg, #10b981 0%, #059669 50%, #047857 100%);
        background-size: 200% 200%;
        border: none;
        border-radius: 14px;
        color: white;
        font-weight: 700;
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        padding: 1rem 2rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        position: relative;
        overflow: hidden;
        animation: downloadPulse 3s ease-in-out infinite;
    }
    
    @keyframes downloadPulse {
        0%, 100% { 
            background-position: 0% 50%;
            box-shadow: 0 6px 20px rgba(16, 185, 129, 0.4);
        }
        50% { 
            background-position: 100% 50%;
            box-shadow: 0 6px 20px rgba(4, 120, 87, 0.4);
        }
    }
    
    .stDownloadButton > button::before {
        content: '⬇';
        position: absolute;
        top: 50%;
        left: 1rem;
        transform: translateY(-50%);
        font-size: 1.2rem;
        transition: transform 0.3s ease;
    }
    
    .stDownloadButton > button:hover {
        transform: translateY(-4px) scale(1.05);
        box-shadow: 0 15px 35px rgba(16, 185, 129, 0.6);
        background-position: 100% 50%;
    }
    
    .stDownloadButton > button:hover::before {
        transform: translateY(-50%) translateX(2px);
        animation: downloadBounce 0.6s ease infinite;
    }
    
    @keyframes downloadBounce {
        0%, 100% { transform: translateY(-50%) translateX(2px); }
        50% { transform: translateY(-40%) translateX(2px); }
    }
    
    /* Enhanced metric cards with unique colors */
    .metric-card:nth-child(1) {
        border-image: linear-gradient(45deg, #ff6b6b, #ff8e88) 1;
    }
    
    .metric-card:nth-child(2) {
        border-image: linear-gradient(45deg, #4ecdc4, #6ee0d6) 1;
    }
    
    .metric-card:nth-child(3) {
        border-image: linear-gradient(45deg, #45b7d1, #67c3db) 1;
    }
    
    .metric-card:nth-child(4) {
        border-image: linear-gradient(45deg, #96ceb4, #a8d5c1) 1;
    }
    
    /* Enhanced input fields */
    .query-input {
        background: linear-gradient(145deg, #3a3a3a, #2d2d2d);
        border: 2px solid #555;
        border-radius: 16px;
        padding: 1.5rem;
        color: white;
        width: 100%;
        margin-bottom: 1.5rem;
        font-size: 1.1rem;
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        box-shadow: inset 0 4px 8px rgba(0,0,0,0.15);
        position: relative;
    }
    
    .query-input:focus {
        outline: none;
        border-color: #4ecdc4;
        box-shadow: 0 0 0 4px rgba(78, 205, 196, 0.25), inset 0 4px 8px rgba(0,0,0,0.15);
        transform: scale(1.02);
        background: linear-gradient(145deg, #404040, #353535);
    }
    
    /* Enhanced panels */
    .data-panel {
        background: linear-gradient(145deg, #2d2d2d, #1e1e1e);
        border-radius: 20px;
        padding: 2.5rem;
        color: white;
        border: 1px solid #404040;
        margin: 2rem 0;
        box-shadow: 0 12px 40px rgba(0,0,0,0.15);
        position: relative;
        overflow: hidden;
        transition: all 0.3s ease;
    }
    
    .data-panel::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: radial-gradient(circle at 20% 20%, rgba(255, 107, 107, 0.05) 0%, transparent 50%),
                    radial-gradient(circle at 80% 80%, rgba(78, 205, 196, 0.05) 0%, transparent 50%);
        pointer-events: none;
    }
    
    .data-panel:hover {
        transform: translateY(-3px);
        box-shadow: 0 20px 50px rgba(0,0,0,0.2);
    }
    
    .panel-title {
        background: linear-gradient(45deg, #ff6b6b, #4ecdc4);
        background-clip: text;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 1.6rem;
        font-weight: 800;
        margin-bottom: 2rem;
        border-bottom: 3px solid transparent;
        border-image: linear-gradient(90deg, #ff6b6b, #4ecdc4) 1;
        padding-bottom: 1rem;
        display: flex;
        align-items: center;
        gap: 1rem;
        animation: titleShimmer 3s ease-in-out infinite;
    }
    
    @keyframes titleShimmer {
        0%, 100% { filter: brightness(1); }
        50% { filter: brightness(1.2); }
    }
    
    /* Enhanced NASA panel */
    .nasa-panel {
        background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 25%, #60a5fa 50%, #93c5fd 75%, #dbeafe 100%);
        background-size: 300% 300%;
        animation: nasaGradient 6s ease infinite;
        border-radius: 20px;
        padding: 2.5rem;
        color: white;
        margin: 2rem 0;
        box-shadow: 0 15px 45px rgba(59, 130, 246, 0.3);
        border: none;
        position: relative;
        overflow: hidden;
        transform: perspective(1000px) rotateX(1deg);
    }
    
    @keyframes nasaGradient {
        0%, 100% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
    }
    
    .nasa-panel::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='0.08'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E");
        animation: starTwinkle 4s linear infinite;
    }
    
    @keyframes starTwinkle {
        0%, 100% { opacity: 0.05; transform: rotate(0deg); }
        50% { opacity: 0.15; transform: rotate(180deg); }
    }
    
    /* Enhanced status indicators */
    .api-status {
        display: inline-flex;
        align-items: center;
        padding: 8px 16px;
        border-radius: 25px;
        font-size: 0.8rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        gap: 0.6rem;
        transition: all 0.3s ease;
        cursor: pointer;
        animation: statusGlow 2s ease-in-out infinite;
    }
    
    .status-active {
        background: linear-gradient(135deg, rgba(16, 185, 129, 0.2), rgba(5, 150, 105, 0.3));
        color: #10b981;
        border: 2px solid rgba(16, 185, 129, 0.4);
        box-shadow: 0 4px 15px rgba(16, 185, 129, 0.2);
    }
    
    .status-active:hover {
        background: linear-gradient(135deg, rgba(16, 185, 129, 0.3), rgba(5, 150, 105, 0.4));
        box-shadow: 0 8px 25px rgba(16, 185, 129, 0.3);
        transform: scale(1.05);
    }
    
    .status-inactive {
        background: linear-gradient(135deg, rgba(245, 158, 11, 0.2), rgba(217, 119, 6, 0.3));
        color: #f59e0b;
        border: 2px solid rgba(245, 158, 11, 0.4);
        box-shadow: 0 4px 15px rgba(245, 158, 11, 0.2);
    }
    
    .status-inactive:hover {
        background: linear-gradient(135deg, rgba(245, 158, 11, 0.3), rgba(217, 119, 6, 0.4));
        box-shadow: 0 8px 25px rgba(245, 158, 11, 0.3);
        transform: scale(1.05);
    }
    
    @keyframes statusGlow {
        0%, 100% { box-shadow: 0 4px 15px rgba(16, 185, 129, 0.2); }
        50% { box-shadow: 0 6px 20px rgba(16, 185, 129, 0.4); }
    }
    
    /* Enhanced cesium container */
    .cesium-container {
        height: 650px;
        border-radius: 20px;
        overflow: hidden;
        box-shadow: 0 20px 60px rgba(0,0,0,0.25);
        border: 2px solid transparent;
        background: linear-gradient(145deg, #1a1a1a, #2d2d2d);
        margin: 2rem 0;
        position: relative;
        transition: all 0.4s ease;
    }
    
    .cesium-container::before {
        content: '';
        position: absolute;
        top: -2px;
        left: -2px;
        right: -2px;
        bottom: -2px;
        background: linear-gradient(45deg, #ff6b6b, #4ecdc4, #45b7d1, #96ceb4);
        background-size: 400% 400%;
        border-radius: 22px;
        z-index: -1;
        animation: borderGlow 8s ease infinite;
    }
    
    @keyframes borderGlow {
        0%, 100% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
    }
    
    .cesium-container:hover {
        transform: scale(1.01);
        box-shadow: 0 25px 70px rgba(0,0,0,0.3);
    }
    
    /* Enhanced chat interface */
    .chat-interface {
        background: linear-gradient(145deg, #2d2d2d, #1e1e1e);
        border-radius: 20px;
        padding: 2.5rem;
        margin: 2.5rem 0;
        border: 2px solid transparent;
        color: white;
        box-shadow: 0 15px 45px rgba(0,0,0,0.2);
        position: relative;
        overflow: hidden;
    }
    
    .chat-interface::before {
        content: '';
        position: absolute;
        top: -2px;
        left: -2px;
        right: -2px;
        bottom: -2px;
        background: linear-gradient(45deg, #667eea, #764ba2, #f093fb, #f5576c);
        background-size: 400% 400%;
        border-radius: 22px;
        z-index: -1;
        animation: chatBorderFlow 10s ease infinite;
    }
    
    @keyframes chatBorderFlow {
        0%, 100% { background-position: 0% 50%; }
        25% { background-position: 100% 0%; }
        50% { background-position: 100% 100%; }
        75% { background-position: 0% 100%; }
    }
    
    /* Enhanced tabs with neon effect */
    .stTabs [data-baseweb="tab-list"] {
        gap: 12px;
        background: linear-gradient(145deg, #2d2d2d, #1e1e1e);
        border-bottom: 2px solid #404040;
        padding: 0.5rem;
        border-radius: 16px 16px 0 0;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: linear-gradient(145deg, #3a3a3a, #2d2d2d);
        color: #888;
        border-radius: 12px;
        border: 2px solid transparent;
        padding: 1rem 2rem;
        font-weight: 600;
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        position: relative;
        overflow: hidden;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    .stTabs [data-baseweb="tab"]::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(78, 205, 196, 0.3), transparent);
        transition: left 0.5s ease;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background: linear-gradient(145deg, #4a4a4a, #3a3a3a);
        color: #4ecdc4;
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(78, 205, 196, 0.2);
    }
    
    .stTabs [data-baseweb="tab"]:hover::before {
        left: 100%;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #4ecdc4, #45b7d1);
        color: white;
        border-color: #4ecdc4;
        transform: translateY(-3px);
        box-shadow: 0 12px 30px rgba(78, 205, 196, 0.4);
        animation: tabGlow 2s ease-in-out infinite alternate;
    }
    
    @keyframes tabGlow {
        0% { box-shadow: 0 12px 30px rgba(78, 205, 196, 0.4); }
        100% { box-shadow: 0 12px 30px rgba(78, 205, 196, 0.6); }
    }
    
    /* Enhanced data tables */
    .stDataFrame {
        background: linear-gradient(145deg, #2d2d2d, #1e1e1e);
        border-radius: 16px;
        border: 2px solid #404040;
        box-shadow: 0 10px 30px rgba(0,0,0,0.15);
        transition: all 0.3s ease;
    }
    
    .stDataFrame:hover {
        border-color: #4ecdc4;
        box-shadow: 0 15px 40px rgba(78, 205, 196, 0.2);
    }
    
    /* Enhanced select boxes */
    .stSelectbox > div > div {
        background: linear-gradient(145deg, #3a3a3a, #2d2d2d);
        border: 2px solid #555;
        border-radius: 14px;
        color: white;
        transition: all 0.3s ease;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }
    
    .stSelectbox > div > div:hover {
        border-color: #4ecdc4;
        box-shadow: 0 6px 18px rgba(78, 205, 196, 0.2);
        transform: translateY(-1px);
    }
    
    /* Enhanced multiselect */
    .stMultiSelect > div > div {
        background: linear-gradient(145deg, #3a3a3a, #2d2d2d);
        border: 2px solid #555;
        border-radius: 14px;
        color: white;
        transition: all 0.3s ease;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }
    
    .stMultiSelect > div > div:hover {
        border-color: #ff6b6b;
        box-shadow: 0 6px 18px rgba(255, 107, 107, 0.2);
        transform: translateY(-1px);
    }
    
    /* Enhanced expander with animation */
    .streamlit-expanderHeader {
        background: linear-gradient(135deg, #667eea, #764ba2);
        border-radius: 16px;
        padding: 1.5rem;
        border: none;
        font-weight: 700;
        color: white;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.3);
        cursor: pointer;
        position: relative;
        overflow: hidden;
    }
    
    .streamlit-expanderHeader::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
        transition: left 0.6s ease;
    }
    
    .streamlit-expanderHeader:hover {
        transform: translateY(-3px) scale(1.02);
        box-shadow: 0 12px 35px rgba(102, 126, 234, 0.5);
        background: linear-gradient(135deg, #764ba2, #667eea);
    }
    
    .streamlit-expanderHeader:hover::before {
        left: 100%;
    }
    
    .streamlit-expanderContent {
        background: linear-gradient(145deg, #2d2d2d, #1e1e1e);
        border-radius: 0 0 16px 16px;
        padding: 2rem;
        border: 2px solid #667eea;
        border-top: none;
        animation: expandFadeIn 0.5s ease-out;
    }
    
    @keyframes expandFadeIn {
        0% { opacity: 0; transform: translateY(-10px); }
        100% { opacity: 1; transform: translateY(0); }
    }
    
    /* Floating action button style */
    .floating-button {
        position: fixed;
        bottom: 2rem;
        right: 2rem;
        width: 60px;
        height: 60px;
        border-radius: 50%;
        background: linear-gradient(135deg, #ff6b6b, #4ecdc4);
        border: none;
        color: white;
        font-size: 1.5rem;
        cursor: pointer;
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        box-shadow: 0 8px 25px rgba(255, 107, 107, 0.4);
        z-index: 1000;
        animation: floatBob 3s ease-in-out infinite;
    }
    
    @keyframes floatBob {
        0%, 100% { transform: translateY(0) rotate(0deg); }
        50% { transform: translateY(-10px) rotate(5deg); }
    }
    
    .floating-button:hover {
        transform: scale(1.2) rotate(15deg);
        box-shadow: 0 15px 40px rgba(255, 107, 107, 0.6);
    }
    
    /* Enhanced tooltips */
    .tooltip {
        position: relative;
        display: inline-block;
        cursor: pointer;
    }
    
    .tooltip .tooltiptext {
        visibility: hidden;
        width: 250px;
        background: linear-gradient(135deg, #2d2d2d, #1e1e1e);
        color: white;
        text-align: center;
        border-radius: 12px;
        padding: 15px;
        position: absolute;
        z-index: 1000;
        bottom: 125%;
        left: 50%;
        margin-left: -125px;
        opacity: 0;
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        border: 2px solid #4ecdc4;
        box-shadow: 0 12px 35px rgba(0,0,0,0.2);
        font-size: 0.95rem;
        line-height: 1.6;
        transform: translateY(10px) scale(0.9);
    }
    
    .tooltip .tooltiptext::after {
        content: "";
        position: absolute;
        top: 100%;
        left: 50%;
        margin-left: -8px;
        border-width: 8px;
        border-style: solid;
        border-color: #4ecdc4 transparent transparent transparent;
    }
    
    .tooltip:hover .tooltiptext {
        visibility: visible;
        opacity: 1;
        transform: translateY(0) scale(1);
    }
    
    /* Enhanced sidebar */
    .css-1d391kg {
        background: linear-gradient(180deg, #252525, #1e1e1e);
        border-right: 2px solid #404040;
    }
    
    /* Animated loading states */
    .loading-shimmer {
        background: linear-gradient(90deg, #3a3a3a 25%, #4a4a4a 50%, #3a3a3a 75%);
        background-size: 200% 100%;
        animation: shimmerMove 1.5s infinite;
        border-radius: 8px;
        height: 20px;
        margin: 8px 0;
    }
    
    @keyframes shimmerMove {
        0% { background-position: -200% 0; }
        100% { background-position: 200% 0; }
    }
    
    /* Enhanced code blocks */
    .stCodeBlock {
        border-radius: 16px;
        border: 2px solid #404040;
        background: linear-gradient(145deg, #1e1e1e, #2d2d2d);
        transition: all 0.3s ease;
    }
    
    .stCodeBlock:hover {
        border-color: #4ecdc4;
        box-shadow: 0 8px 25px rgba(78, 205, 196, 0.15);
    }
    
    code {
        font-family: 'JetBrains Mono', monospace;
        background: linear-gradient(135deg, #2d2d2d, #3a3a3a);
        padding: 4px 8px;
        border-radius: 6px;
        color: #4ecdc4;
        font-size: 0.95em;
        font-weight: 500;
        transition: all 0.3s ease;
    }
    
    code:hover {
        background: linear-gradient(135deg, #3a3a3a, #4a4a4a);
        color: #ff6b6b;
        transform: scale(1.05);
    }
    
    pre {
        background: linear-gradient(145deg, #1e1e1e, #2d2d2d);
        border-radius: 12px;
        padding: 2rem;
        border: 2px solid #404040;
        overflow-x: auto;
        transition: all 0.3s ease;
    }
    
    pre:hover {
        border-color: #667eea;
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.15);
    }
    
    /* Enhanced ag-grid styling */
    .ag-theme-alpine-dark {
        --ag-background-color: #2d2d2d;
        --ag-border-color: #404040;
        --ag-header-background-color: linear-gradient(135deg, #3a3a3a, #4a4a4a);
        --ag-odd-row-background-color: #2d2d2d;
        --ag-row-hover-color: rgba(78, 205, 196, 0.1);
        --ag-header-column-separator-color: #4ecdc4;
        border-radius: 16px;
        border: 2px solid #404040;
        box-shadow: 0 10px 30px rgba(0,0,0,0.15);
        transition: all 0.3s ease;
    }
    
    .ag-theme-alpine-dark:hover {
        border-color: #4ecdc4;
        box-shadow: 0 15px 40px rgba(78, 205, 196, 0.2);
    }
    
    /* Particle animation background with ocean theme */
    .particle-bg {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        pointer-events: none;
        z-index: -5;
        background: 
            linear-gradient(180deg, #001122 0%, #003366 30%, #004080 60%, #0066cc 100%),
            radial-gradient(ellipse at top, rgba(0, 150, 255, 0.05) 0%, transparent 70%),
            radial-gradient(ellipse at bottom right, rgba(100, 200, 255, 0.03) 0%, transparent 70%),
            radial-gradient(ellipse at bottom left, rgba(0, 100, 200, 0.04) 0%, transparent 70%);
    }
    
    /* Scroll-triggered ocean depth effect */
    .main-content {
        position: relative;
        z-index: 1;
        background: transparent;
    }
    
    /* Ocean parallax scrolling layers */
    .ocean-layer-1 {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 120%;
        background: 
            linear-gradient(45deg, 
                transparent 40%, 
                rgba(0, 150, 255, 0.02) 50%, 
                transparent 60%),
            repeating-linear-gradient(
                -45deg,
                transparent,
                transparent 20px,
                rgba(100, 200, 255, 0.01) 20px,
                rgba(100, 200, 255, 0.01) 40px
            );
        animation: oceanLayer1 40s linear infinite;
        pointer-events: none;
        z-index: -6;
        will-change: transform;
    }
    
    .ocean-layer-2 {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 120%;
        background: 
            repeating-linear-gradient(
                30deg,
                transparent,
                transparent 30px,
                rgba(0, 100, 200, 0.015) 30px,
                rgba(0, 100, 200, 0.015) 60px
            );
        animation: oceanLayer2 60s linear infinite reverse;
        pointer-events: none;
        z-index: -7;
        will-change: transform;
    }
    
    @keyframes oceanLayer1 {
        0% { transform: translateX(0) translateY(0) rotate(0deg); }
        100% { transform: translateX(-100px) translateY(-50px) rotate(2deg); }
    }
    
    @keyframes oceanLayer2 {
        0% { transform: translateX(0) translateY(0) rotate(0deg); }
        100% { transform: translateX(50px) translateY(-30px) rotate(-1deg); }
    }
    
    /* Deep ocean ambient glow */
    .ocean-glow {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: 
            radial-gradient(circle at 30% 40%, rgba(0, 150, 255, 0.08) 0%, transparent 50%),
            radial-gradient(circle at 70% 60%, rgba(100, 200, 255, 0.06) 0%, transparent 60%),
            radial-gradient(circle at 50% 20%, rgba(0, 200, 255, 0.04) 0%, transparent 40%);
        animation: oceanGlow 25s ease-in-out infinite;
        pointer-events: none;
        z-index: -8;
    }
    
    @keyframes oceanGlow {
        0%, 100% { 
            opacity: 0.8;
            transform: scale(1) rotate(0deg);
        }
        33% { 
            opacity: 1;
            transform: scale(1.1) rotate(2deg);
        }
        66% { 
            opacity: 0.9;
            transform: scale(0.95) rotate(-1deg);
        }
    }
    
    /* Mobile responsiveness with enhanced animations */
    @media (max-width: 768px) {
        .stats-grid {
            grid-template-columns: 1fr;
            gap: 1.5rem;
        }
        
        .cesium-container {
            height: 450px;
            border-radius: 16px;
        }
        
        .main-header {
            padding: 2rem;
            border-radius: 16px;
        }
        
        .header-title {
            font-size: 2.5rem;
        }
        
        .header-subtitle {
            font-size: 1.1rem;
        }
        
        .metric-card {
            padding: 2rem;
        }
        
        .metric-value {
            font-size: 2.5rem;
        }
        
        .sample-queries {
            grid-template-columns: repeat(2, 1fr);
            gap: 1rem;
        }
        
        .sample-query {
            height: 80px;
            font-size: 0.9rem;
            padding: 1rem;
        }
        
        .data-panel, .chat-interface {
            padding: 2rem;
        }
        
        .floating-button {
            bottom: 1rem;
            right: 1rem;
            width: 50px;
            height: 50px;
            font-size: 1.2rem;
        }
    }
    
    @media (max-width: 480px) {
        .sample-queries {
            grid-template-columns: 1fr;
        }
        
        .sample-query {
            height: 70px;
        }
    }
    
    /* Accessibility improvements */
    @media (prefers-reduced-motion: reduce) {
        *, *::before, *::after {
            animation-duration: 0.01ms !important;
            animation-iteration-count: 1 !important;
            transition-duration: 0.01ms !important;
        }
    }
    
    /* Enhanced focus indicators */
    button:focus, input:focus, select:focus, textarea:focus {
        outline: 3px solid #4ecdc4;
        outline-offset: 3px;
        box-shadow: 0 0 0 6px rgba(78, 205, 196, 0.2);
    }
    
    /* Custom scrollbar with rainbow effect */
    ::-webkit-scrollbar {
        width: 12px;
        height: 12px;
    }
    
    ::-webkit-scrollbar-track {
        background: linear-gradient(145deg, #2d2d2d, #1e1e1e);
        border-radius: 6px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(45deg, #ff6b6b, #4ecdc4);
        border-radius: 6px;
        transition: all 0.3s ease;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(45deg, #4ecdc4, #45b7d1);
        box-shadow: 0 0 10px rgba(78, 205, 196, 0.5);
    }
    
    /* Success/Error message styling */
    .stSuccess {
        background: linear-gradient(135deg, rgba(16, 185, 129, 0.1), rgba(5, 150, 105, 0.2));
        border: 2px solid #10b981;
        border-radius: 12px;
        animation: successPulse 2s ease-in-out infinite;
    }
    
    @keyframes successPulse {
        0%, 100% { box-shadow: 0 0 0 rgba(16, 185, 129, 0.4); }
        50% { box-shadow: 0 0 20px rgba(16, 185, 129, 0.6); }
    }
    
    .stError {
        background: linear-gradient(135deg, rgba(239, 68, 68, 0.1), rgba(220, 38, 38, 0.2));
        border: 2px solid #ef4444;
        border-radius: 12px;
        animation: errorShake 0.5s ease-in-out;
    }
    
    @keyframes errorShake {
        0%, 100% { transform: translateX(0); }
        25% { transform: translateX(-5px); }
        75% { transform: translateX(5px); }
    }
    
    /* Glassmorphism effect for special elements */
    .glass-effect {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
    }
    
    /* Neon glow effect for important elements */
    .neon-glow {
        position: relative;
        background: linear-gradient(45deg, #ff6b6b, #4ecdc4);
        border-radius: 16px;
        padding: 1px;
        animation: neonPulse 2s ease-in-out infinite alternate;
    }
    
    .neon-glow::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: linear-gradient(45deg, #ff6b6b, #4ecdc4, #45b7d1, #96ceb4);
        border-radius: 16px;
        filter: blur(10px);
        opacity: 0.7;
        z-index: -1;
    }
    
    @keyframes neonPulse {
        0% { filter: brightness(1) drop-shadow(0 0 5px rgba(78, 205, 196, 0.5)); }
        100% { filter: brightness(1.2) drop-shadow(0 0 20px rgba(78, 205, 196, 0.8)); }
    }
    
    /* Progress bar enhancement */
    .stProgress > div > div {
        background: linear-gradient(90deg, #ff6b6b, #4ecdc4, #45b7d1, #96ceb4) !important;
        background-size: 200% 100%;
        animation: progressFlow 2s linear infinite;
        border-radius: 10px;
        height: 12px !important;
    }
    
    @keyframes progressFlow {
        0% { background-position: 0% 0%; }
        100% { background-position: 200% 0%; }
    }
    
    /* Interactive hover effects for all clickable elements */
    [role="button"], button, .stButton, .stDownloadButton, .sample-query {
        transform-origin: center;
        backface-visibility: hidden;
    }
    
    /* Special effects for metric cards */
    .metric-card:nth-child(1):hover {
        box-shadow: 0 25px 50px rgba(255, 107, 107, 0.4);
        border-color: #ff6b6b;
    }
    
    .metric-card:nth-child(2):hover {
        box-shadow: 0 25px 50px rgba(78, 205, 196, 0.4);
        border-color: #4ecdc4;
    }
    
    .metric-card:nth-child(3):hover {
        box-shadow: 0 25px 50px rgba(69, 183, 209, 0.4);
        border-color: #45b7d1;
    }
    
    .metric-card:nth-child(4):hover {
        box-shadow: 0 25px 50px rgba(150, 206, 180, 0.4);
        border-color: #96ceb4;
    }
    
    /* High contrast mode support */
    @media (prefers-contrast: high) {
        .main-header, .metric-card, .data-panel {
            border: 3px solid white;
        }
        
        .query-button, .stButton > button {
            border: 2px solid white;
        }
    }
    
    /* JavaScript for scroll-responsive ocean effects */
    window.addEventListener('scroll', function() {
        const scrolled = window.pageYOffset;
        const rate = scrolled * -0.5;
        const deepRate = scrolled * -0.3;
        const bubbleRate = scrolled * -0.8;
        
        const oceanLayer1 = document.querySelector('.stApp::before');
        const oceanLayer2 = document.querySelector('.ocean-layer-1');
        const bubbleLayer = document.querySelector('.bubble-layer');
        
        if (oceanLayer1) {
            oceanLayer1.style.transform = `translateY(${rate}px) scale(${1 + scrolled * 0.0001})`;
        }
        if (oceanLayer2) {
            oceanLayer2.style.transform = `translateY(${deepRate}px) rotate(${scrolled * 0.02}deg)`;
        }
        if (bubbleLayer) {
            bubbleLayer.style.transform = `translateY(${bubbleRate}px)`;
        }
        
        // Change ocean depth based on scroll
        const maxScroll = document.body.scrollHeight - window.innerHeight;
        const scrollPercent = scrolled / maxScroll;
        const hueShift = scrollPercent * 60; // Shift from blue to deep blue-green
        
        document.body.style.filter = `hue-rotate(${hueShift}deg) saturate(${1 + scrollPercent * 0.3})`;
    });
    
    /* Initialize ocean layers on page load */
    document.addEventListener('DOMContentLoaded', function() {
        // Create ocean layers
        const oceanLayer1 = document.createElement('div');
        oceanLayer1.className = 'ocean-layer-1';
        document.body.appendChild(oceanLayer1);
        
        const oceanLayer2 = document.createElement('div');
        oceanLayer2.className = 'ocean-layer-2';
        document.body.appendChild(oceanLayer2);
        
        const bubbleLayer = document.createElement('div');
        bubbleLayer.className = 'bubble-layer';
        document.body.appendChild(bubbleLayer);
        
        const oceanGlow = document.createElement('div');
        oceanGlow.className = 'ocean-glow';
        document.body.appendChild(oceanGlow);
    });
</style>
""", unsafe_allow_html=True)

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
