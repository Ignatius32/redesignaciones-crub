"""
CRUB Course Team Viewer Application

A Streamlit web application for viewing and filtering course teams by department.
This application provides an interactive interface to explore the course data.

Run with: streamlit run course_viewer_app.py
"""

import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import List, Dict, Any, Optional
import logging

from crub_courses.api.factory import create_google_sheets_client, create_huayca_client
from crub_courses.services.course_team_service import CourseTeamService
from crub_courses.models.core import Course, AcademicPeriod, FacultyRole

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="CRUB Course Team Viewer",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

@st.cache_data(ttl=300)  # Cache for 5 minutes
def load_course_data():
    """Load and cache course data from APIs"""
    try:
        with st.spinner("Loading data from APIs..."):
            # Initialize clients and service
            sheets_client = create_google_sheets_client()
            huayca_client = create_huayca_client()
            service = CourseTeamService(sheets_client, huayca_client)
            
            # Refresh data and detect courses
            status = service.refresh_data()
            courses = service.detect_unique_courses()
            summary = service.generate_summary()
            
            return courses, summary, status
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return [], None, None

def create_courses_dataframe(courses: List[Course]) -> pd.DataFrame:
    """Convert courses to a pandas DataFrame for easier filtering and display"""
    data = []
    
    for course in courses:
        # Get responsible and auxiliary faculty names
        responsible = [m.docente for m in course.responsible_faculty]
        auxiliary = [m.docente for m in course.auxiliary_faculty]
        
        data.append({
            'Código SIU': course.cod_siu,
            'Materia': course.materia,
            'Período': course.periodo,
            'Carrera': course.carrera,
            'Departamento': course.department or 'Sin datos',
            'Área': course.academic_area or 'Sin datos',
            'Es Optativa': 'Sí' if course.is_elective else 'No' if course.is_elective is not None else 'Sin datos',
            'Total Docentes': course.total_team_size,
            'Responsables': len(responsible),
            'Auxiliares': len(auxiliary),
            'Docentes Responsables': ' | '.join(responsible) if responsible else 'Sin asignar',
            'Docentes Auxiliares': ' | '.join(auxiliary) if auxiliary else 'Sin asignar',
            'Tiene Datos Huayca': 'Sí' if course.huayca_details else 'No'
        })
    
    return pd.DataFrame(data)

def display_course_statistics(df: pd.DataFrame):
    """Display course statistics in columns"""
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total de Cursos", len(df))
    
    with col2:
        total_faculty = df['Total Docentes'].sum()
        st.metric("Total Asignaciones", total_faculty)
    
    with col3:
        departments = df['Departamento'].nunique()
        st.metric("Departamentos", departments)
    
    with col4:
        with_huayca = len(df[df['Tiene Datos Huayca'] == 'Sí'])
        percentage = (with_huayca / len(df) * 100) if len(df) > 0 else 0
        st.metric("Con Datos Huayca", f"{with_huayca} ({percentage:.1f}%)")

def create_department_chart(df: pd.DataFrame):
    """Create a chart showing courses by department"""
    dept_counts = df['Departamento'].value_counts()
    
    fig = px.bar(
        x=dept_counts.index,
        y=dept_counts.values,
        labels={'x': 'Departamento', 'y': 'Número de Cursos'},
        title='Distribución de Cursos por Departamento'
    )
    
    fig.update_layout(
        xaxis_tickangle=-45,
        height=400
    )
    
    return fig

def create_period_chart(df: pd.DataFrame):
    """Create a chart showing courses by academic period"""
    period_counts = df['Período'].value_counts()
    
    fig = px.pie(
        values=period_counts.values,
        names=period_counts.index,
        title='Distribución de Cursos por Período Académico'
    )
    
    return fig

def create_faculty_distribution_chart(df: pd.DataFrame):
    """Create a chart showing faculty distribution"""
    fig = go.Figure()
    
    fig.add_trace(go.Histogram(
        x=df['Total Docentes'],
        nbinsx=10,
        name='Distribución del Tamaño de Equipos',
        opacity=0.7
    ))
    
    fig.update_layout(
        title='Distribución del Tamaño de Equipos Docentes',
        xaxis_title='Número de Docentes por Curso',
        yaxis_title='Número de Cursos',
        height=400
    )
    
    return fig

def display_course_details(course_data: pd.Series):
    """Display detailed information for a selected course"""
    st.subheader(f"Detalles del Curso: {course_data['Materia']}")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Información Básica:**")
        st.write(f"- **Código SIU:** {course_data['Código SIU']}")
        st.write(f"- **Período:** {course_data['Período']}")
        st.write(f"- **Carrera:** {course_data['Carrera']}")
        st.write(f"- **Departamento:** {course_data['Departamento']}")
        st.write(f"- **Área:** {course_data['Área']}")
        st.write(f"- **Es Optativa:** {course_data['Es Optativa']}")
    
    with col2:
        st.write("**Equipo Docente:**")
        st.write(f"- **Total Docentes:** {course_data['Total Docentes']}")
        st.write(f"- **Responsables:** {course_data['Responsables']}")
        st.write(f"- **Auxiliares:** {course_data['Auxiliares']}")
        st.write(f"- **Datos Huayca:** {course_data['Tiene Datos Huayca']}")
    
    if course_data['Docentes Responsables'] != 'Sin asignar':
        st.write("**Docentes Responsables:**")
        for docente in course_data['Docentes Responsables'].split(' | '):
            st.write(f"- {docente}")
    
    if course_data['Docentes Auxiliares'] != 'Sin asignar':
        st.write("**Docentes Auxiliares:**")
        for docente in course_data['Docentes Auxiliares'].split(' | '):
            st.write(f"- {docente}")

def main():
    """Main application function"""
    st.title("🎓 CRUB Course Team Viewer")
    st.markdown("Explorador de equipos docentes y cursos del CRUB")
    
    # Load data
    courses, summary, status = load_course_data()
    
    if not courses:
        st.error("No se pudieron cargar los datos. Verifique la conexión a las APIs.")
        st.stop()
    
    # Convert to DataFrame
    df = create_courses_dataframe(courses)
    
    # Sidebar filters
    st.sidebar.header("🔍 Filtros")
    
    # Department filter
    departments = ['Todos'] + sorted(df['Departamento'].unique().tolist())
    selected_dept = st.sidebar.selectbox("Departamento:", departments)
    
    # Period filter
    periods = ['Todos'] + sorted(df['Período'].unique().tolist())
    selected_period = st.sidebar.selectbox("Período:", periods)
    
    # Career filter
    careers = ['Todas'] + sorted(df['Carrera'].unique().tolist())
    selected_career = st.sidebar.selectbox("Carrera:", careers)
    
    # Elective filter
    elective_options = ['Todas', 'Sí', 'No', 'Sin datos']
    selected_elective = st.sidebar.selectbox("Es Optativa:", elective_options)
    
    # Team size filter
    min_team_size = st.sidebar.slider(
        "Tamaño mínimo del equipo:",
        min_value=1,
        max_value=int(df['Total Docentes'].max()),
        value=1
    )
    
    # Apply filters
    filtered_df = df.copy()
    
    if selected_dept != 'Todos':
        filtered_df = filtered_df[filtered_df['Departamento'] == selected_dept]
    
    if selected_period != 'Todos':
        filtered_df = filtered_df[filtered_df['Período'] == selected_period]
    
    if selected_career != 'Todas':
        filtered_df = filtered_df[filtered_df['Carrera'] == selected_career]
    
    if selected_elective != 'Todas':
        filtered_df = filtered_df[filtered_df['Es Optativa'] == selected_elective]
    
    filtered_df = filtered_df[filtered_df['Total Docentes'] >= min_team_size]
    
    # Main content
    st.header("📊 Estadísticas Generales")
    display_course_statistics(filtered_df)
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        if not filtered_df.empty:
            fig_dept = create_department_chart(filtered_df)
            st.plotly_chart(fig_dept, use_container_width=True)
    
    with col2:
        if not filtered_df.empty:
            fig_period = create_period_chart(filtered_df)
            st.plotly_chart(fig_period, use_container_width=True)
    
    # Faculty distribution chart
    if not filtered_df.empty:
        fig_faculty = create_faculty_distribution_chart(filtered_df)
        st.plotly_chart(fig_faculty, use_container_width=True)
    
    # Course list
    st.header("📋 Lista de Cursos")
    
    if filtered_df.empty:
        st.warning("No se encontraron cursos con los filtros seleccionados.")
    else:
        st.write(f"Mostrando {len(filtered_df)} cursos de {len(df)} totales")
        
        # Display table with selection
        display_columns = [
            'Código SIU', 'Materia', 'Período', 'Carrera', 
            'Departamento', 'Total Docentes', 'Responsables', 'Auxiliares'
        ]
        
        st.dataframe(
            filtered_df[display_columns],
            use_container_width=True,
            hide_index=True
        )
        
        # Course selection for details
        st.subheader("Seleccionar curso para ver detalles")
        course_options = [
            f"{row['Código SIU']} - {row['Materia']} ({row['Período']})"
            for _, row in filtered_df.iterrows()
        ]
        
        if course_options:
            selected_course_idx = st.selectbox(
                "Curso:",
                range(len(course_options)),
                format_func=lambda x: course_options[x]
            )
            
            if selected_course_idx is not None:
                selected_course = filtered_df.iloc[selected_course_idx]
                display_course_details(selected_course)
    
    # Data source status
    st.sidebar.header("📡 Estado de Datos")
    if status:
        st.sidebar.write(f"**Materias Equipo:** {status.materias_equipo_count}")
        st.sidebar.write(f"**Designaciones:** {status.designaciones_docentes_count}")
        st.sidebar.write(f"**Huayca:** {status.huayca_materias_count}")
        st.sidebar.write(f"**Match Docentes:** {status.faculty_match_rate:.1f}%")
        st.sidebar.write(f"**Match Huayca:** {status.huayca_match_rate:.1f}%")
    
    # Refresh button
    if st.sidebar.button("🔄 Actualizar Datos"):
        st.cache_data.clear()
        st.rerun()

if __name__ == "__main__":
    main()
