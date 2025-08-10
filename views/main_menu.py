import streamlit as st

def display_main_menu():
    # Enhanced header with gradient text
    st.markdown("""
    <div style="text-align: center; margin-bottom: 3rem;">
        <h1 style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; font-size: 3.5rem; font-weight: 800; margin-bottom: 1rem;">
            🚀 Multi-Task Dashboard
        </h1>
        <p style="font-size: 1.2rem; color: #64748b; font-weight: 500; max-width: 600px; margin: 0 auto;">
            Your comprehensive toolkit for system administration, development, and automation tasks
        </p>
    </div>
    """, unsafe_allow_html=True)

    # First row of three columns with enhanced descriptions
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div style="text-align: center; margin-bottom: 1rem;">
            <div style="font-size: 2.5rem; margin-bottom: 0.5rem;">🪟</div>
            <h3 style="color: #1e293b; margin-bottom: 0.5rem;">Windows Tasks</h3>
            <p style="color: #64748b; font-size: 0.9rem; margin: 0;">System management, automation & monitoring</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Windows Tasks", key="windows_main_btn"):
            st.session_state.current_view = "windows_sub_menu"
            st.session_state.selected_category = "Windows Tasks"
            st.session_state.selected_sub_category = None
            st.session_state.selected_ml_sub_category = None
            st.session_state.selected_k8s_sub_category = None
            st.session_state.selected_aws_sub_category = None
            st.session_state.selected_ai_sub_category = None
            st.session_state.selected_pe_sub_category = None
            st.rerun()
    
    with col2:
        st.markdown("""
        <div style="text-align: center; margin-bottom: 1rem;">
            <div style="font-size: 2.5rem; margin-bottom: 0.5rem;">🐧</div>
            <h3 style="color: #1e293b; margin-bottom: 0.5rem;">Linux Tasks</h3>
            <p style="color: #64748b; font-size: 0.9rem; margin: 0;">Server administration & command line tools</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Linux Tasks", key="linux_main_btn"):
            st.session_state.current_view = "linux_sub_menu"
            st.session_state.selected_category = "Linux Tasks"
            st.session_state.selected_sub_category = None
            st.session_state.selected_ml_sub_category = None
            st.session_state.selected_k8s_sub_category = None
            st.session_state.selected_aws_sub_category = None
            st.session_state.selected_ai_sub_category = None
            st.session_state.selected_pe_sub_category = None
            st.rerun()
    
    with col3:
        st.markdown("""
        <div style="text-align: center; margin-bottom: 1rem;">
            <div style="font-size: 2.5rem; margin-bottom: 0.5rem;">🐳</div>
            <h3 style="color: #1e293b; margin-bottom: 0.5rem;">Docker Tasks</h3>
            <p style="color: #64748b; font-size: 0.9rem; margin: 0;">Container management & orchestration</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Docker Tasks", key="docker_main_btn"):
            st.session_state.current_view = "docker_sub_menu"
            st.session_state.selected_category = "Docker Tasks"
            st.session_state.selected_sub_category = None
            st.session_state.selected_ml_sub_category = None
            st.session_state.selected_k8s_sub_category = None
            st.session_state.selected_aws_sub_category = None
            st.session_state.selected_ai_sub_category = None
            st.session_state.selected_pe_sub_category = None
            st.rerun()

    # Second row of three columns
    col4, col5, col6 = st.columns(3)
    
    with col4:
        st.markdown("""
        <div style="text-align: center; margin-bottom: 1rem;">
            <div style="font-size: 2.5rem; margin-bottom: 0.5rem;">🤖</div>
            <h3 style="color: #1e293b; margin-bottom: 0.5rem;">Machine Learning</h3>
            <p style="color: #64748b; font-size: 0.9rem; margin: 0;">Data analysis, modeling & AI tools</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Machine Learning Tasks", key="ml_main_btn"):
            st.session_state.current_view = "ml_sub_menu"
            st.session_state.selected_category = "Machine Learning Tasks"
            st.session_state.selected_sub_category = None
            st.session_state.selected_ml_sub_category = None
            st.session_state.selected_k8s_sub_category = None
            st.session_state.selected_aws_sub_category = None
            st.session_state.selected_ai_sub_category = None
            st.session_state.selected_pe_sub_category = None
            st.rerun()
    
    with col5:
        st.markdown("""
        <div style="text-align: center; margin-bottom: 1rem;">
            <div style="font-size: 2.5rem; margin-bottom: 0.5rem;">☸️</div>
            <h3 style="color: #1e293b; margin-bottom: 0.5rem;">Kubernetes</h3>
            <p style="color: #64748b; font-size: 0.9rem; margin: 0;">Cluster management & deployment</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Kubernetes Tasks", key="k8s_main_btn"):
            st.session_state.current_view = "k8s_sub_menu"
            st.session_state.selected_category = "Kubernetes Tasks"
            st.session_state.selected_sub_category = None
            st.session_state.selected_ml_sub_category = None
            st.session_state.selected_k8s_sub_category = None
            st.session_state.selected_aws_sub_category = None
            st.session_state.selected_ai_sub_category = None
            st.session_state.selected_pe_sub_category = None
            st.rerun()
    
    with col6:
        st.markdown("""
        <div style="text-align: center; margin-bottom: 1rem;">
            <div style="font-size: 2.5rem; margin-bottom: 0.5rem;">☁️</div>
            <h3 style="color: #1e293b; margin-bottom: 0.5rem;">AWS Tasks</h3>
            <p style="color: #64748b; font-size: 0.9rem; margin: 0;">Cloud services & infrastructure</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("AWS Tasks", key="aws_main_btn"):
            st.session_state.current_view = "aws_sub_menu"
            st.session_state.selected_category = "AWS Tasks"
            st.session_state.selected_sub_category = None
            st.session_state.selected_ml_sub_category = None
            st.session_state.selected_k8s_sub_category = None
            st.session_state.selected_aws_sub_category = None
            st.session_state.selected_ai_sub_category = None
            st.session_state.selected_pe_sub_category = None
            st.rerun()
            
    # Third row of two columns
    col7, col8, col9 = st.columns(3)
    
    with col7:
        st.markdown("""
        <div style="text-align: center; margin-bottom: 1rem;">
            <div style="font-size: 2.5rem; margin-bottom: 0.5rem;">🧠</div>
            <h3 style="color: #1e293b; margin-bottom: 0.5rem;">Agentic AI</h3>
            <p style="color: #64748b; font-size: 0.9rem; margin: 0;">Intelligent automation & agents</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Agentic AI", key="ai_main_btn"):
            st.session_state.current_view = "ai_sub_menu"
            st.session_state.selected_category = "Agentic AI"
            st.session_state.selected_sub_category = None
            st.session_state.selected_ml_sub_category = None
            st.session_state.selected_k8s_sub_category = None
            st.session_state.selected_aws_sub_category = None
            st.session_state.selected_ai_sub_category = None
            st.session_state.selected_pe_sub_category = None
            st.rerun()
    
    with col8:
        st.markdown("""
        <div style="text-align: center; margin-bottom: 1rem;">
            <div style="font-size: 2.5rem; margin-bottom: 0.5rem;">✨</div>
            <h3 style="color: #1e293b; margin-bottom: 0.5rem;">Prompt Engineering</h3>
            <p style="color: #64748b; font-size: 0.9rem; margin: 0;">AI prompt optimization & design</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Prompt Engineering", key="pe_main_btn"):
            st.session_state.current_view = "pe_sub_menu"
            st.session_state.selected_category = "Prompt Engineering"
            st.session_state.selected_sub_category = None
            st.session_state.selected_ml_sub_category = None
            st.session_state.selected_k8s_sub_category = None
            st.session_state.selected_aws_sub_category = None
            st.session_state.selected_ai_sub_category = None
            st.session_state.selected_pe_sub_category = None
            st.rerun()
    
    # The last column is intentionally left empty to maintain the 2-button layout in the last row.
    with col9:
        st.write("")
    
    # Add a footer with additional information
    st.markdown("""
    <div style="text-align: center; margin-top: 4rem; padding: 2rem; background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%); border-radius: 16px; border: 1px solid #e2e8f0;">
        <h4 style="color: #1e293b; margin-bottom: 1rem;">🎯 Quick Start Guide</h4>
        <p style="color: #64748b; margin-bottom: 0.5rem;">Select any category above to explore specialized tools and automation tasks.</p>
        <p style="color: #64748b; font-size: 0.9rem; margin: 0;">Each section contains carefully curated tools for specific use cases and workflows.</p>
    </div>
    """, unsafe_allow_html=True)