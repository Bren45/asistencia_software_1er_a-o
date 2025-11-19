# app_streamlit.py
"""
Versión web del Sistema de Asistencia usando Streamlit.
Reutiliza la lógica de src/core/ (AttendanceManager y DataLoader).
"""

import streamlit as st
import pandas as pd
from datetime import datetime

# Asegúrate de que las importaciones a src/core funcionen
# Si estás ejecutando Streamlit desde la raíz, no debería haber problema.
try:
    from src.core.attendance_manager import AttendanceManager
    MANAGER = AttendanceManager()
except ImportError as e:
    st.error(f"Error al cargar la lógica de negocio: {e}. Asegúrate de que los archivos de 'src/core' estén en la ubicación correcta y que la estructura sea adecuada.")
    st.stop()
except Exception as e:
    st.error(f"Error al inicializar el Manager: {e}")
    st.stop()


# --- Configuración de la Página ---
st.set_page_config(
    page_title="Sistema de Asistencia Web",
    layout="wide"
)

st.title("👨‍🏫 Sistema de Asistencia - 1er Año Desarrollo de Software (WEB)")

# --- Control de Pestañas de Streamlit ---

# Streamlit utiliza bloques para simular pestañas
tab1, tab2, tab3 = st.tabs(["1. Asistencia Manual", "2. Gestión de Estudiantes", "3. Reportes"])

# =========================================================================
# === PESTAÑA 1: ASISTENCIA MANUAL (Nombre y Apellido) =====================
# =========================================================================
with tab1:
    st.header("1. Registro de Asistencia Manual")
    
    with st.container(border=True):
        st.subheader("Registrar Presente")
        
        # Usamos st.session_state para limpiar los campos después del éxito
        if 'att_nombre' not in st.session_state:
            st.session_state['att_nombre'] = ""
        if 'att_apellido' not in st.session_state:
            st.session_state['att_apellido'] = ""
            
        col_n, col_a = st.columns(2)
        with col_n:
            nombre = st.text_input("Nombre del Estudiante:", key="att_nombre_input", 
                                   value=st.session_state['att_nombre'])
        with col_a:
            apellido = st.text_input("Apellido del Estudiante:", key="att_apellido_input", 
                                     value=st.session_state['att_apellido'])

        if st.button("REGISTRAR PRESENTE", type="primary"):
            if nombre and apellido:
                try:
                    # Llama a la lógica de negocio existente
                    student_full_name = MANAGER.record_attendance_by_name(nombre, apellido)
                    st.success(f"✅ Asistencia de **{student_full_name}** registrada con éxito.")
                    
                    # Limpiar los campos después del registro
                    st.session_state['att_nombre'] = ""
                    st.session_state['att_apellido'] = ""
                    st.experimental_rerun() # Rerun para limpiar los campos de entrada
                    
                except ValueError as e:
                    st.error(f"❌ ERROR: {e}")
            else:
                st.warning("¡Error! Nombre y Apellido son obligatorios.")

# =========================================================================
# === PESTAÑA 2: GESTIÓN DE ESTUDIANTES (DNI, Nombre, Apellido) =============
# =========================================================================
with tab2:
    st.header("2. Agregar Nuevo Estudiante")
    
    with st.form("student_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            dni = st.text_input("DNI (Identificador Único):")
            nombre = st.text_input("Nombre:")
        with col2:
            apellido = st.text_input("Apellido:")

        submitted = st.form_submit_button("GUARDAR ESTUDIANTE", type="primary")

        if submitted:
            if dni and nombre and apellido:
                success = MANAGER.add_student(dni, nombre, apellido)
                if success:
                    st.success(f"✅ Estudiante **{nombre} {apellido}** agregado con éxito.")
                else:
                    st.error(f"❌ ERROR: El DNI '{dni}' ya existe.")
            else:
                st.warning("¡Error! Todos los campos son obligatorios.")

    st.markdown("---")
    # Muestra el conteo en tiempo real
    total_students = len(MANAGER.loader.load_students())
    st.info(f"Total de Estudiantes Registrados: **{total_students}**")


# =========================================================================
# === PESTAÑA 3: REPORTES (Muestra el CSV) =================================
# =========================================================================
with tab3:
    st.header("3. Reporte de Asistencia (Histórico)")
    
    if st.button("ACTUALIZAR REPORTE", type="secondary"):
        st.cache_data.clear() # Limpiar la caché de datos de Streamlit para asegurar la recarga
        
    records = MANAGER.generate_report()
    
    if records:
        df_reporte = pd.DataFrame(records)
        
        # Formatear la columna de tiempo para una mejor visualización en la web
        df_reporte['timestamp'] = pd.to_datetime(df_reporte['timestamp']).dt.strftime("%Y-%m-%d %H:%M:%S")

        st.dataframe(
            df_reporte,
            use_container_width=True,
            column_order=['timestamp', 'DNI', 'Nombre', 'Apellido', 'method'],
            hide_index=True
        )
    else:
        st.info("Aún no hay registros de asistencia.")

# Opcional: Mostrar los datos crudos de estudiantes
# st.sidebar.header("Datos de Estudiantes (Debugging)")
# st.sidebar.dataframe(MANAGER.students)