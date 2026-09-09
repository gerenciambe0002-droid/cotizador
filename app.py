import streamlit as st
import datetime
from datetime import timedelta
from weasyprint import HTML
import base64

# Configuración de la página
st.set_page_config(
    page_title="Generador de Cotizaciones - MBE",
    page_icon="📦",
    layout="wide"
)

# Estilos CSS personalizados para la interfaz
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

# Formulario principal
with st.form("cotizacion_form"):
    col_dates1, col_dates2 = st.columns(2)
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
        rem_direccion = st.text_input("Dirección Remitente", value="Arenales 1172, CABA (C1061AAJ)")
        rem_pais = st.text_input("País Origen", value="Argentina")

    with col2:
        st.subheader("Destinatario (Destino)")
        dest_nombre = st.text_input("Nombre Destinatario", value="Renata María Moreira de Jager")
        dest_direccion = st.text_input("Dirección Destinatario", value="Rua 30 de Novembro 739, Castro")
        dest_estado_cp = st.text_input("Estado / Código Postal", value="Paraná (CP 84177-022)")
        dest_pais = st.text_input("País Destino", value="Brasil (Zona 1)")

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

    # Cálculos automáticos
    peso_vol = (largo * ancho * alto) / factor_div
    peso_facturable_calc = max(peso_real, peso_vol)
    # Redondeo superior al 0.5 kg más cercano
    import math
    peso_facturable = math.ceil(peso_facturable_calc * 2) / 2

    st.info(f"**Cálculo Automático:** Peso Volumétrico: **{peso_vol:.3f} kg** | Peso Facturable Aplicado: **{peso_facturable} kg**")

    st.markdown('<div class="sub-header">3. Tarifas de Servicios (USD)</div>', unsafe_allow_html=True)
    col6, col7, col8 = st.columns(3)
    with col6:
        precio_connect = st.number_input("CONNECT PLUS (USD)", value=50.0, step=1.0)
    with col7:
        precio_standard = st.number_input("STANDARD (USD)", value=80.0, step=1.0)
    with col8:
        precio_priority = st.number_input("PRIORITY (USD)", value=85.0, step=1.0)

    submitted = st.form_submit_button("📄 GENERAR PDF DE COTIZACIÓN")

if submitted:
    # Generar el HTML estandarizado
    fecha_str = fecha_emision.strftime("%d/%m/%Y")
    
    html_template = f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<style>
  @page {{ size: A4; margin: 15mm 15mm; background-color: #fcfcfc; }}
  * {{ box-sizing: border-box; }}
  body {{ font-family: Arial, 'Helvetica Neue', sans-serif; color: #2c3e50; margin: 0; padding: 0; font-size: 10pt; line-height: 1.4; }}
  .header {{ background-color: #0d233a; color: #ffffff; margin: -15mm -15mm 15px -15mm; padding: 20px 20mm; border-bottom: 4px solid #c0392b; }}
  .header table {{ width: 100%; border-collapse: collapse; }}
  .brand-title {{ font-size: 18pt; font-weight: bold; letter-spacing: 1px; color: #ffffff; }}
  .brand-subtitle {{ font-size: 9pt; color: #e0e6ed; margin-top: 3px; }}
  .doc-title {{ text-align: right; font-size: 14pt; font-weight: bold; color: #f39c12; text-transform: uppercase; }}
  .doc-meta {{ text-align: right; font-size: 8.5pt; color: #d0d7de; }}
  .section-title {{ font-size: 11pt; font-weight: bold; color: #0d233a; border-left: 4px solid #c0392b; padding-left: 8px; margin-top: 15px; margin-bottom: 8px; text-transform: uppercase; }}
  .grid-table {{ width: 100%; border-collapse: collapse; margin-bottom: 12px; }}
  .grid-table td {{ vertical-align: top; padding: 6px 8px; width: 50%; }}
  .card {{ background-color: #ffffff; border: 1px solid #e2e8f0; border-radius: 4px; padding: 10px 12px; }}
  .card-title {{ font-size: 9.5pt; font-weight: bold; color: #0d233a; border-bottom: 1px solid #edf2f7; padding-bottom: 4px; margin-bottom: 6px; }}
  .info-row {{ font-size: 9pt; margin-bottom: 4px; }}
  .info-label {{ font-weight: bold; color: #4a5568; }}
  .price-table {{ width: 100%; border-collapse: collapse; margin-top: 8px; margin-bottom: 15px; font-size: 9.5pt; }}
  .price-table th {{ background-color: #1a365d; color: #ffffff; padding: 9px; text-align: left; font-weight: bold; font-size: 9pt; text-transform: uppercase; }}
  .price-table td {{ padding: 9px; border-bottom: 1px solid #e2e8f0; }}
  .price-table tr:nth-child(even) {{ background-color: #f7fafc; }}
  .highlight-row {{ background-color: #fefcbf !important; font-weight: bold; }}
  .highlight-row td {{ border-top: 2px solid #d69e2e; border-bottom: 2px solid #d69e2e; color: #744210; }}
  .badge-rec {{ background-color: #d69e2e; color: #ffffff; padding: 3px 8px; border-radius: 3px; font-size: 8pt; font-weight: bold; }}
  .rec-box {{ background-color: #ebf8ff; border: 1px solid #3182ce; border-radius: 4px; padding: 12px; margin-top: 10px; margin-bottom: 15px; }}
  .rec-title {{ font-weight: bold; color: #2b6cb0; font-size: 10pt; margin-bottom: 4px; }}
  .footer {{ margin-top: 25px; border-top: 1px solid #cbd5e0; padding-top: 10px; font-size: 8pt; color: #718096; text-align: center; }}
</style>
</head>
<body>
<div class="header">
  <table>
    <tr>
      <td>
        <div class="brand-title">MAIL BOXES ETC.</div>
        <div class="brand-subtitle">#PeoplePossible | Patagonia Logistics S.R.L.</div>
      </td>
      <td>
        <div class="doc-title">Cotización Logística</div>
        <div class="doc-meta">Fecha: {fecha_str}<br>Validez: {validez_dias} días corridos</div>
      </td>
    </tr>
  </table>
</div>

<div class="section-title">1. Información de Envío</div>
<table class="grid-table">
  <tr>
    <td>
      <div class="card">
        <div class="card-title">Remitente (Origen)</div>
        <div class="info-row"><span class="info-label">Nombre:</span> {rem_nombre}</div>
        <div class="info-row"><span class="info-label">CUIT:</span> {rem_cuit}</div>
        <div class="info-row"><span class="info-label">Dirección:</span> {rem_direccion}</div>
        <div class="info-row"><span class="info-label">País:</span> {rem_pais}</div>
      </div>
    </td>
    <td>
      <div class="card">
        <div class="card-title">Destinatario (Destino)</div>
        <div class="info-row"><span class="info-label">Nombre:</span> {dest_nombre}</div>
        <div class="info-row"><span class="info-label">Dirección:</span> {dest_direccion}</div>
        <div class="info-row"><span class="info-label">Estado/CP:</span> {dest_estado_cp}</div>
        <div class="info-row"><span class="info-label">País:</span> {dest_pais}</div>
      </div>
    </td>
  </tr>
</table>

<div class="section-title">2. Detalle de Carga y Peso Facturable</div>
<div class="card" style="margin-bottom: 12px;">
  <table style="width:100%; border-collapse:collapse; font-size:9pt;">
    <tr>
      <td style="width:33%; padding:3px 0;"><span class="info-label">Mercadería:</span> {mercaderia}</td>
      <td style="width:33%; padding:3px 0;"><span class="info-label">Dimensiones:</span> {int(largo)} x {int(ancho)} x {int(alto)} cm</td>
      <td style="width:33%; padding:3px 0;"><span class="info-label">Valor Declarado:</span> USD {valor_declarado:.2f}</td>
    </tr>
    <tr>
      <td style="padding:3px 0;"><span class="info-label">Peso Real:</span> {peso_real:.3f} kg</td>
      <td style="padding:3px 0;"><span class="info-label">Peso Volumétrico:</span> {peso_vol:.3f} kg</td>
      <td style="padding:3px 0;"><span class="info-label">Peso Facturable:</span> <strong>{peso_facturable} kg</strong></td>
    </tr>
  </table>
</div>

<div class="section-title">3. Comparativa de Servicios</div>
<table class="price-table">
  <thead>
    <tr>
      <th>Servicio</th>
      <th>Precio Final (USD)</th>
      <th>Estado</th>
    </tr>
  </thead>
  <tbody>
    <tr class='highlight-row'>
      <td><strong>CONNECT PLUS</strong></td>
      <td style="font-size:11pt;"><strong>USD {int(precio_connect)}</strong></td>
      <td><span class='badge-rec'>RECOMENDADO</span></td>
    </tr>
    <tr>
      <td><strong>STANDARD</strong></td>
      <td style="font-size:11pt;"><strong>USD {int(precio_standard)}</strong></td>
      <td><span style='color:#718096;'>Disponible</span></td>
    </tr>
    <tr>
      <td><strong>PRIORITY</strong></td>
      <td style="font-size:11pt;"><strong>USD {int(precio_priority)}</strong></td>
      <td><span style='color:#718096;'>Disponible</span></td>
    </tr>
  </tbody>
</table>

<div class="rec-box">
  <div class="rec-title">💡 OPCIÓN RECOMENDADA: CONNECT PLUS — USD {int(precio_connect)}</div>
  <div style="font-size:8.5pt; color: #2d3748;">
    El servicio <strong>CONNECT PLUS</strong> ofrece la tarifa más conveniente con excelente cobertura y tiempos de entrega optimizados.
  </div>
</div>

<div class="section-title">4. Términos y Condiciones</div>
<ul style="font-size: 8pt; color: #4a5568; padding-left: 15px; margin-top: 4px;">
  <li>Tarifas válidas por {validez_dias} días corridos. Sujeto a variaciones tarifarias y recargos semanales.</li>
  <li>Los valores no incluyen impuestos de importación, aranceles o tasas aduaneras en destino, los cuales deberán ser abonados por el destinatario.</li>
  <li>El peso y las dimensiones están sujetos a verificación en la balanza/escáner oficial al momento del ingreso.</li>
</ul>

<div class="footer">
  Mail Boxes Etc. Argentina | Centro MBE 0002 | Arenales 1172, CABA | Tel: +54 299 4156099 | www.mbe.ar
</div>
</body>
</html>
"""
    
    # Generación de PDF en memoria
    pdf_bytes = HTML(string=html_template).write_pdf()
    
    st.success("✅ Cotización generada con éxito con el formato estandarizado.")
    
    st.download_button(
        label="📥 DESCARGAR PDF OFICIAL",
        data=pdf_bytes,
        file_name=f"Cotizacion_MBE_{dest_nombre.replace(' ', '_')}.pdf",
        mime="application/pdf"
    )
