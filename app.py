import streamlit as st
import datetime
import io
import math
import pandas as pd

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle

# Configuración de la página
st.set_page_config(
    page_title="Generador de Cotizaciones - MBE",
    page_icon="📦",
    layout="wide"
)

# Estilos CSS
st.markdown("""
<style>
    .main-header {
        font-size: 24px;
        font-weight: bold;
        color: #0d233a;
        margin-bottom: 20px;
        border-bottom: 3px solid #c0392b;
        padding-bottom: 10px;
    }
    .sub-header {
        font-size: 16px;
        font-weight: bold;
        color: #1a365d;
        margin-top: 15px;
        margin-bottom: 10px;
    }
    .stButton>button {
        width: 100%;
        background-color: #0d233a;
        color: white;
        font-weight: bold;
        height: 50px;
        border-radius: 5px;
    }
    .stButton>button:hover {
        background-color: #c0392b;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-header">📦 Generador Oficial de Cotizaciones | Mail Boxes Etc.</div>', unsafe_allow_html=True)

# ---------------------------------------------------------
# CARGA DE DATOS EXCEL
# ---------------------------------------------------------
@st.cache_data
def cargar_cotizadores():
    try:
        excel_expo = pd.ExcelFile("Cotizador Expo 2026 (1).xlsx")
        df_areas_expo = pd.read_excel(excel_expo, sheet_name="Areas")
        
        return {
            "status": True,
            "areas_expo": df_areas_expo
        }
    except Exception as e:
        return {"status": False, "error": str(e)}

cotiz_data = cargar_cotizadores()

def obtener_paises():
    if cotiz_data["status"]:
        df = cotiz_data["areas_expo"]
        paises = df.iloc[1:, 1].dropna().unique().tolist()
        return sorted([str(p).strip() for p in paises])
    return ["Argentina", "Brasil", "Estados Unidos", "España", "Uruguay", "Chile", "Alemania"]

lista_paises = obtener_paises()

# ---------------------------------------------------------
# FORMULARIO Y CONTROLES DE COTIZACIÓN
# ---------------------------------------------------------
with st.form("cotizacion_form"):
    col_tipo, col_dates1, col_dates2 = st.columns([1, 1, 1])
    with col_tipo:
        tipo_operacion = st.selectbox("Tipo de Operación", ["Exportación", "Importación"])
    with col_dates1:
        fecha_emision = st.date_input("Fecha de Cotización", datetime.date.today())
    with col_dates2:
        validez_dias = st.number_input("Días de Validez", value=5, min_value=1)

    st.markdown('<div class="sub-header">1. Datos del Remitente y Destinatario</div>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Remitente (Origen)")
        rem_nombre = st.text_input("Nombre / Razón Social Remitente", value="JOSEFINA ESTRELLA")
        rem_cuit = st.text_input("CUIT / DNI Remitente", value="27-16920864-1")
        rem_direccion = st.text_input("Dirección Remitente", value="Arenales 1172, CABA")
        rem_cp = st.text_input("Código Postal Origen", value="C1061AAJ")
        rem_pais = st.text_input("País Origen", value="Argentina")

    with col2:
        st.subheader("Destinatario (Destino)")
        dest_nombre = st.text_input("Nombre Destinatario", value="Renata María Moreira de Jager")
        dest_direccion = st.text_input("Dirección / Calle Destinatario", value="Rua 30 de Novembro 739, Castro")
        
        col_cp1, col_cp2 = st.columns([2, 1])
        with col_cp1:
            dest_estado = st.text_input("Estado / Provincia", value="Paraná")
        with col_cp2:
            dest_cp = st.text_input("Código Postal (CP)", value="84177-022", help="Escribe o verifica el código postal según la dirección.")
            
        dest_pais = st.selectbox("País Destino", options=lista_paises, index=lista_paises.index("Brasil") if "Brasil" in lista_paises else 0)

    st.markdown('<div class="sub-header">2. Detalle de Carga</div>', unsafe_allow_html=True)
    col3, col4, col5 = st.columns(3)
    with col3:
        mercaderia = st.text_input("Mercadería / Descripción", value="3 Ovejas de Fieltro/Madera")
        valor_declarado = st.number_input("Valor Declarado (USD)", value=99.0, step=1.0)
    with col4:
        largo = st.number_input("Largo (cm)", value=10.0, step=1.0)
        ancho = st.number_input("Ancho (cm)", value=36.0, step=1.0)
        alto = st.number_input("Alto (cm)", value=29.0, step=1.0)
    with col5:
        peso_real = st.number_input("Peso Real (kg)", value=0.365, step=0.05, format="%.3f")
        factor_div = st.selectbox("Factor Volumétrico", [5000, 6000], index=0)

    # Cálculo de Peso
    peso_vol = (largo * ancho * alto) / factor_div
    peso_facturable_calc = max(peso_real, peso_vol)
    peso_facturable = math.ceil(peso_facturable_calc * 2) / 2

    st.info(f"**Cálculo Automático:** Peso Volumétrico: **{peso_vol:.3f} kg** | Peso Facturable Aplicado: **{peso_facturable} kg**")

    # ---------------------------------------------------------
    # SECCIÓN 3: MARGEN DE GANANCIA Y PRECIOS DE COSTO
    # ---------------------------------------------------------
    st.markdown('<div class="sub-header">3. Tarifas Base (Costo) y Margen de Ganancia</div>', unsafe_allow_html=True)
    
    col_m1, col_m2 = st.columns([1, 2])
    with col_m1:
        margen_porcentaje = st.number_input("Margen de Ganancia (%)", value=30.0, min_value=0.0, max_value=200.0, step=5.0)
    
    factor_margen = 1 + (margen_porcentaje / 100.0)

    st.write("**Ingresa los costos base (los precios finales con margen se calcularán automáticamente):**")
    
    col_c1, col_c2, col_c3, col_c4 = st.columns(4)
    with col_c1:
        costo_connect = st.number_input("Costo Connect Plus (USD)", value=38.5)
        precio_connect = round(costo_connect * factor_margen, 2)
        st.caption(f"Precio Venta: **USD {precio_connect}**")

    with col_c2:
        costo_ups = st.number_input("Costo UPS (USD)", value=57.6)
        precio_ups = round(costo_ups * factor_margen, 2)
        st.caption(f"Precio Venta: **USD {precio_ups}**")

    with col_c3:
        costo_fedex = st.number_input("Costo FedEx (USD)", value=61.5)
        precio_fedex = round(costo_fedex * factor_margen, 2)
        st.caption(f"Precio Venta: **USD {precio_fedex}**")

    with col_c4:
        costo_priority = st.number_input("Costo Priority (USD)", value=65.0)
        precio_priority = round(costo_priority * factor_margen, 2)
        st.caption(f"Precio Venta: **USD {precio_priority}**")

    # ---------------------------------------------------------
    # SECCIÓN 4: SELECCIÓN DE SERVICIOS VISIBLES EN EL PDF
    # ---------------------------------------------------------
    st.markdown('<div class="sub-header">4. Configurar Servicios Visibles en el PDF</div>', unsafe_allow_html=True)
    st.write("Selecciona cuáles servicios deseas mostrar en la tabla comparativa del cliente:")
    
    col_v1, col_v2, col_v3, col_v4 = st.columns(4)
    with col_v1:
        ver_connect = st.checkbox("Mostrar CONNECT PLUS", value=True)
    with col_v2:
        ver_ups = st.checkbox("Mostrar UPS", value=True)
    with col_v3:
        ver_fedex = st.checkbox("Mostrar FEDEX", value=True)
    with col_v4:
        ver_priority = st.checkbox("Mostrar PRIORITY", value=True)

    submitted = st.form_submit_button("📄 GENERAR PDF DE COTIZACIÓN")

# ---------------------------------------------------------
# GENERACIÓN DE PDF REPORTLAB
# ---------------------------------------------------------
def generar_pdf_reportlab():
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )
    
    styles = getSampleStyleSheet()
    
    style_header_title = ParagraphStyle('HeaderTitle', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=16, textColor=colors.HexColor('#FFFFFF'))
    style_doc_title = ParagraphStyle('DocTitle', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=13, textColor=colors.HexColor('#F39C12'), alignment=2)
    style_sec_title = ParagraphStyle('SecTitle', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=10, textColor=colors.HexColor('#0D233A'), spaceBefore=10, spaceAfter=6)
    style_cell_title = ParagraphStyle('CellTitle', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=8.5, textColor=colors.HexColor('#0D233A'))
    style_cell_text = ParagraphStyle('CellText', parent=styles['Normal'], fontName='Helvetica', fontSize=8, textColor=colors.HexColor('#2D3748'))
    
    style_th = ParagraphStyle('TH', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=8.5, textColor=colors.HexColor('#FFFFFF'))
    style_td = ParagraphStyle('TD', parent=styles['Normal'], fontName='Helvetica', fontSize=8.5, textColor=colors.HexColor('#2D3748'))
    style_td_rec = ParagraphStyle('TDRec', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=8.5, textColor=colors.HexColor('#744210'))
    style_rec_title = ParagraphStyle('RecTitle', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=9, textColor=colors.HexColor('#2B6CB0'))
    style_footer = ParagraphStyle('Footer', parent=styles['Normal'], fontName='Helvetica', fontSize=7.5, textColor=colors.HexColor('#718096'), alignment=1)

    elements = []
    fecha_str = fecha_emision.strftime("%d/%m/%Y")

    # Filtrar servicios según los checkboxes
    todos_servicios = []
    if ver_connect:
        todos_servicios.append({"nombre": "CONNECT PLUS", "precio": precio_connect})
    if ver_ups:
        todos_servicios.append({"nombre": "UPS", "precio": precio_ups})
    if ver_fedex:
        todos_servicios.append({"nombre": "FEDEX", "precio": precio_fedex})
    if ver_priority:
        todos_servicios.append({"nombre": "PRIORITY", "precio": precio_priority})

    if not todos_servicios:
        todos_servicios.append({"nombre": "CONNECT PLUS", "precio": precio_connect})

    servicios_ordenados = sorted(todos_servicios, key=lambda x: x["precio"])
    mejor_opcion = servicios_ordenados[0]

    # Encabezado
    header_data = [
        [
            Paragraph("MAIL BOXES ETC.<br/><font size=8>#PeoplePossible | Patagonia Logistics S.R.L.</font>", style_header_title),
            Paragraph(f"COTIZACIÓN LOGÍSTICA ({tipo_operacion.upper()})<br/><font size=8>Fecha: {fecha_str}<br/>Validez: {validez_dias} días</font>", style_doc_title)
        ]
    ]
    t_header = Table(header_data, colWidths=[320, 202])
    t_header.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#0D233A')),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('PADDING', (0,0), (-1,-1), 10),
        ('BOTTOMPADDING', (0,0), (-1,-1), 12),
        ('LINEBELOW', (0,0), (-1,-1), 3, colors.HexColor('#C0392B')),
    ]))
    elements.append(t_header)
    elements.append(Spacer(1, 10))

    # Sección 1: Datos Remitente / Destinatario
    elements.append(Paragraph("1. INFORMACIÓN DE ENVÍO", style_sec_title))
    rem_text = f"<b>Nombre:</b> {rem_nombre}<br/><b>CUIT:</b> {rem_cuit}<br/><b>Dirección:</b> {rem_direccion}<br/><b>CP:</b> {rem_cp}<br/><b>País:</b> {rem_pais}"
    dest_text = f"<b>Nombre:</b> {dest_nombre}<br/><b>Dirección:</b> {dest_direccion}<br/><b>Estado/CP:</b> {dest_estado} (CP: {dest_cp})<br/><b>País:</b> {dest_pais}"
    
    info_data = [
        [Paragraph("<b>REMITENTE (ORIGEN)</b>", style_cell_title), Paragraph("<b>DESTINATARIO (DESTINO)</b>", style_cell_title)],
        [Paragraph(rem_text, style_cell_text), Paragraph(dest_text, style_cell_text)]
    ]
    t_info = Table(info_data, colWidths=[256, 256])
    t_info.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#FFFFFF')),
        ('BOX', (0,0), (0,1), 1, colors.HexColor('#E2E8F0')),
        ('BOX', (1,0), (1,1), 1, colors.HexColor('#E2E8F0')),
        ('PADDING', (0,0), (-1,-1), 6),
        ('BACKGROUND', (0,0), (0,0), colors.HexColor('#F7FAFC')),
        ('BACKGROUND', (1,0), (1,0), colors.HexColor('#F7FAFC')),
    ]))
    elements.append(t_info)
    elements.append(Spacer(1, 10))

    # Sección 2: Detalle de Carga
    elements.append(Paragraph("2. DETALLE DE CARGA Y PESO FACTURABLE", style_sec_title))
    carga_data = [
        [
            Paragraph(f"<b>Mercadería:</b> {mercaderia}", style_cell_text),
            Paragraph(f"<b>Dimensiones:</b> {int(largo)}x{int(ancho)}x{int(alto)} cm", style_cell_text),
            Paragraph(f"<b>Valor Dec.:</b> USD {valor_declarado:.2f}", style_cell_text)
        ],
        [
            Paragraph(f"<b>Peso Real:</b> {peso_real:.3f} kg", style_cell_text),
            Paragraph(f"<b>Peso Vol.:</b> {peso_vol:.3f} kg", style_cell_text),
            Paragraph(f"<b>Peso Facturable:</b> {peso_facturable} kg", style_cell_title)
        ]
    ]
    t_carga = Table(carga_data, colWidths=[170, 170, 172])
    t_carga.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#E2E8F0')),
        ('PADDING', (0,0), (-1,-1), 6),
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#FFFFFF')),
    ]))
    elements.append(t_carga)
    elements.append(Spacer(1, 10))

    # Sección 3: Comparativa de Servicios
    elements.append(Paragraph("3. COMPARATIVA DE SERVICIOS SELECCIONADOS", style_sec_title))
    prices_data = [
        [Paragraph("Servicio / Courier", style_th), Paragraph("Precio Final (USD)", style_th), Paragraph("Estado", style_th)]
    ]
    
    for s in servicios_ordenados:
        es_rec = (s["nombre"] == mejor_opcion["nombre"])
        st_style = style_td_rec if es_rec else style_td
        estado_label = "RECOMENDADO" if es_rec else "Disponible"
        prices_data.append([
            Paragraph(s["nombre"], st_style),
            Paragraph(f"USD {s['precio']:.2f}", st_style),
            Paragraph(estado_label, st_style)
        ])

    t_prices = Table(prices_data, colWidths=[200, 160, 152])
    t_prices.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1A365D')),
        ('BACKGROUND', (0,1), (-1,1), colors.HexColor('#FEFCBF')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
        ('PADDING', (0,0), (-1,-1), 6),
    ]))
    elements.append(t_prices)
    elements.append(Spacer(1, 10))

    # Opción recomendada
    rec_data = [
        [Paragraph(f"OPCIÓN SELECCIONADA / RECOMENDADA: {mejor_opcion['nombre']} — USD {mejor_opcion['precio']:.2f}", style_rec_title)],
        [Paragraph(f"El servicio {mejor_opcion['nombre']} ofrece la tarifa más conveniente para la entrega en destination.", style_cell_text)]
    ]
    t_rec = Table(rec_data, colWidths=[512])
    t_rec.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#EBF8FF')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#3182CE')),
        ('PADDING', (0,0), (-1,-1), 6),
    ]))
    elements.append(t_rec)
    elements.append(Spacer(1, 10))

    # Términos y Condiciones
    elements.append(Paragraph("4. TÉRMINOS Y CONDICIONES", style_sec_title))
    terms = f"• Tarifas válidas por {validez_dias} días corridos. Sujeto a variaciones tarifarias.<br/>• Los valores no incluyen impuestos de importación ni aranceles aduaneros en destino.<br/>• El peso y las dimensiones están sujetos a verificación en balanza oficial."
    elements.append(Paragraph(terms, style_cell_text))
    elements.append(Spacer(1, 20))

    elements.append(Paragraph("Mail Boxes Etc. Argentina | Centro MBE 0002 | Arenales 1172, CABA | Tel: +54 299 4156099 | www.mbe.ar", style_footer))

    doc.build(elements)
    buffer.seek(0)
    return buffer

if submitted:
    try:
        pdf = generar_pdf_reportlab()
        st.success("✅ Cotización generada con éxito.")
        st.download_button(
            label="📥 DESCARGAR PDF OFICIAL",
            data=pdf,
            file_name=f"Cotizacion_MBE_{dest_nombre.replace(' ', '_')}.pdf",
            mime="application/pdf"
        )
    except Exception as e:
        st.error(f"Error al generar el PDF: {e}")
