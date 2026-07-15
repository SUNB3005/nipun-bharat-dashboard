import streamlit as st
import pandas as pd
import streamlit.components.v1 as components

# 1. Page Configuration
st.set_page_config(page_title="NIPUN Bharat Dashboard", layout="wide")

@st.cache_data
def load_data():
    df = pd.read_excel('Book9.xlsx', sheet_name='ALL SCHOOL MM (2)')
    # Clean string columns
    for col in ['district', 'block', 'cluster', 'manag', 'school']:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()
    return df

try:
    df = load_data()
except Exception as e:
    st.error(f"Error loading file: {e}")
    st.stop()

st.title("🎯 NIPUN BHARAT MASTER DASHBOARD")
st.write("📊 मार्च २०२६ स्थिती व जुलै २०२६ अध्ययन स्तर निश्चिती अहवाल")
st.write("---")

# 2. Filters Sidebar
st.sidebar.header("📋 फिल्टर्स निवडा")

# District Filter
districts = sorted(df['district'].dropna().unique())
selected_district = st.sidebar.selectbox("जिल्हा (District)", districts)
filtered_df = df[df['district'] == selected_district]

# Block Filter
blocks = ["सर्व (All)"] + sorted(filtered_df['block'].dropna().unique())
selected_block = st.sidebar.selectbox("तालुका (Block)", blocks)
if selected_block != "सर्व (All)":
    filtered_df = filtered_df[filtered_df['block'] == selected_block]

# Cluster Filter
clusters = ["सर्व (All)"] + sorted(filtered_df['cluster'].dropna().unique())
selected_cluster = st.sidebar.selectbox("केंद्र (Cluster)", clusters)
if selected_cluster != "सर्व (All)":
    filtered_df = filtered_df[filtered_df['cluster'] == selected_cluster]

# Management Filter
managements = ["सर्व (All)"] + sorted(filtered_df['manag'].dropna().unique())
selected_mgmt = st.sidebar.selectbox("व्यवस्थापन (Management)", managements)
if selected_mgmt != "सर्व (All)":
    filtered_df = filtered_df[filtered_df['manag'] == selected_mgmt]

# School Filter
schools = ["सर्व (All)"] + sorted(filtered_df['school'].dropna().unique())
selected_school = st.sidebar.selectbox("शाळा (School Name)", schools)
if selected_school != "सर्व (All)":
    filtered_df = filtered_df[filtered_df['school'] == selected_school]

# Action Button
show_data = st.sidebar.button("Show Data", type="primary")

if show_data or 'clicked' in st.session_state:
    st.session_state['clicked'] = True
    
    # --- 🎯 गणना (Calculations using Unique UDISE) ---
    total_schools = filtered_df['udise'].nunique()
    
    # Assessed आणि Not Assessed शाळांची संख्या (UDISE वरून अचूक मॅचिंग)
    filtered_df['is_assessed'] = filtered_df[['all reading assesed', 'all writing assesed', 'all numercy assesed', 'all 0peration assesed']].max(axis=1) > 0
    assessed_schools_count = filtered_df[filtered_df['is_assessed'] == True]['udise'].nunique()
    not_assessed_schools_count = filtered_df[filtered_df['is_assessed'] == False]['udise'].nunique()
    
    # टक्केवारी काढणे
    tot_ra = filtered_df['all reading assesed'].sum()
    tot_r_ni = filtered_df['all reading nipun'].sum()
    reading_per = (tot_r_ni / tot_ra * 100) if tot_ra > 0 else 0
    
    tot_wa = filtered_df['all writing assesed'].sum()
    tot_w_ni = filtered_df['all writing nipun'].sum()
    writing_per = (tot_w_ni / tot_wa * 100) if tot_wa > 0 else 0
    
    tot_na = filtered_df['all numercy assesed'].sum()
    tot_n_ni = filtered_df['all numercy nipun'].sum()
    numeracy_per = (tot_n_ni / tot_na * 100) if tot_na > 0 else 0
    
    tot_opa = filtered_df['all 0peration assesed'].sum()
    tot_op_ni = filtered_df['all operation nipun'].sum()
    operation_per = (tot_op_ni / tot_opa * 100) if tot_opa > 0 else 0

    # व्यवस्थापनानुसार शाळांची संख्या (UDISE नुसार)
    zp_count = filtered_df[filtered_df['manag'].str.contains('Zilla Parishad', case=False, na=False)]['udise'].nunique()
    other_mgmt_count = total_schools - zp_count

    # Display Streamlit Metric Cards
    st.subheader("📊 मुख्य प्रगती अहवाल (KPIs)")
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Total Schools", f"{total_schools}")
    c2.metric("Reading %", f"{reading_per:.2f}%")
    c3.metric("Writing %", f"{writing_per:.2f}%")
    c4.metric("Numeracy %", f"{numeracy_per:.2f}%")
    c5.metric("Operation %", f"{operation_per:.2f}%")
    
    st.write("---")
    
    # School Info HTML
    school_info_html = ""
    if selected_school != "सर्व (All)" and len(filtered_df) > 0:
        udise_code = filtered_df['udise'].iloc[0]
        school_info_html = f"""
        <tr>
            <td colspan="2" style="padding: 8px;"><strong>School Name:</strong> {selected_school}</td>
            <td colspan="2" style="padding: 8px;"><strong>UDISE Code:</strong> {udise_code}</td>
        </tr>
        """
    else:
        school_info_html = f"""
        <tr>
            <td colspan="4" style="padding: 8px;"><strong>School Name:</strong> सर्व शाळा अहवाल (एकूण: {total_schools})</td>
        </tr>
        """

    # --- HTML Report Generation ---
    html_content = f"""
    <div style="font-family: Arial, sans-serif; padding: 15px; border: 1px solid #cbd5e1; background-color: #ffffff; color: #000000; border-radius: 8px;">
        <div style="text-align: center;">
            <h2 style="margin: 0; color: #1e3a8a; font-size: 22px;">NIPUN DASHBOARD अहवाल</h2>
            <h4 style="margin: 5px 0; color: #475569; font-size: 14px;">(मार्च २०२६ स्थिती व जुलै २०२६ अध्ययन स्तर निश्चिती)</h4>
        </div>
        <br>
        
        <table style="width: 100%; margin-bottom: 15px; font-size: 13px; background: #f8fafc; padding: 10px; border-radius: 6px; border-collapse: collapse; border: 1px solid #e2e8f0;">
            <tr style="border-bottom: 1px solid #e2e8f0;">
                <td style="padding: 8px;"><strong>District:</strong> {selected_district}</td>
                <td style="padding: 8px;"><strong>Block:</strong> {selected_block}</td>
                <td style="padding: 8px;"><strong>Cluster:</strong> {selected_cluster}</td>
                <td style="padding: 8px;"><strong>Management:</strong> {selected_mgmt}</td>
            </tr>
            {school_info_html}
            <tr>
                <td style="padding: 8px;"><strong>Total School:</strong> {total_schools}</td>
                <td style="padding: 8px;"><strong>Assessed School:</strong> {assessed_schools_count}</td>
                <td style="padding: 8px;"><strong>Not Assessed School:</strong> {not_assessed_schools_count}</td>
                <td style="padding: 8px;"><strong>Zilla Parishad:</strong> {zp_count} | <strong>Other:</strong> {other_mgmt_count}</td>
            </tr>
        </table>

        <table style="width: 100%; margin-bottom: 20px; text-align: center; border-collapse: separate; border-spacing: 10px;">
            <tr>
                <td style="background: #eff6ff; padding: 12px; border-radius: 6px; border: 1px solid #bfdbfe; width: 25%;">
                    <div style="font-size: 12px; color: #1e40af; font-weight: bold;">Reading %</div>
                    <div style="font-size: 20px; font-weight: bold; color: #1e3a8a;">{reading_per:.2f}%</div>
                </td>
                <td style="background: #f0fdf4; padding: 12px; border-radius: 6px; border: 1px solid #bbf7d0; width: 25%;">
                    <div style="font-size: 12px; color: #166534; font-weight: bold;">Writing %</div>
                    <div style="font-size: 20px; font-weight: bold; color: #14532d;">{writing_per:.2f}%</div>
                </td>
                <td style="background: #fdf2f8; padding: 12px; border-radius: 6px; border: 1px solid #fbcfe8; width: 25%;">
                    <div style="font-size: 12px; color: #9d174d; font-weight: bold;">Numeracy %</div>
                    <div style="font-size: 20px; font-weight: bold; color: #701a75;">{numeracy_per:.2f}%</div>
                </td>
                <td style="background: #fff7ed; padding: 12px; border-radius: 6px; border: 1px solid #ffedd5; width: 25%;">
                    <div style="font-size: 12px; color: #9a3412; font-weight: bold;">Nu. Operation %</div>
                    <div style="font-size: 20px; font-weight: bold; color: #7c2d12;">{operation_per:.2f}%</div>
                </td>
            </tr>
        </table>
    """
    
    # कोष्टक माहिती
    classes_info = [
        ('इयत्ता दुसरी (Class 2)', 'class 2 Total Student', 'Class 2 reading assesed', 'Class 2 reading nipun', 'Class 2 writing assesed', 'Class 2 writing nipun', 'Class 2 numercy assesed', 'Class 2 numercy nipun', 'Class 2 0peration assesed', 'Class 2 operation nipun', 'Class 2 all nipun', 'मार्च २०२६ (इ. २ री)', 'जुलै २०२६ (इ. ३ री)'),
        ('इयत्ता तिसरी (Class 3)', 'class 3 Total Student', 'Class 3 reading assesed', 'Class 3 reading nipun', 'Class 3 writing assesed', 'Class 3 writing nipun', 'Class 3 numercy assesed', 'Class 3 numercy nipun', 'Class 3 0peration assesed', 'Class 3 operation nipun', 'Class 3 all nipun', 'मार्च २०२६ (इ. ३ री)', 'जुलै २०२६ (इ. ४ थी)'),
        ('इयत्ता चौथी (Class 4)', 'class 4 Total Student', 'Class 4 reading assesed', 'Class 4 reading nipun', 'Class 4 writing assesed', 'Class 4 writing nipun', 'Class 4 numercy assesed', 'Class 4 numercy nipun', 'Class 4 0peration assesed', 'Class 4 operation nipun', 'Class 4 all nipun', 'मार्च २०२६ (इ. ४ थी)', 'जुलै २०२६ (इ. ५ वी)'),
        ('इयत्ता पाचवी (Class 5)', 'class 5 Total Student', 'Class 5 reading assesed', 'Class 5 reading nipun', 'Class 5 writing assesed', 'Class 5 writing nipun', 'Class 5 numercy assesed', 'Class 5 numercy nipun', 'Class 5 0peration assesed', 'Class 5 operation nipun', 'Class 5 all nipun', 'मार्च २०२६ (इ. ५ वी)', 'जुलै २०२६ (इ. ६ वी)')
    ]
    
    for title, to_col, ra_col, r_ni_col, wa_col, w_ni_col, na_col, n_ni_col, opa_col, op_ni_col, al_ni_col, m_lbl, j_lbl in classes_info:
        c_to = filtered_df[to_col].sum()
        c_ra = filtered_df[ra_col].sum()
        c_r_ni = filtered_df[r_ni_col].sum()
        c_wa = filtered_df[wa_col].sum()
        c_w_ni = filtered_df[w_ni_col].sum()
        c_na = filtered_df[na_col].sum()
        c_n_ni = filtered_df[n_ni_col].sum()
        c_opa = filtered_df[opa_col].sum()
        c_op_ni = filtered_df[op_ni_col].sum()
        c_al_ni = filtered_df[al_ni_col].sum()
        c_per = (c_al_ni / c_to * 100) if c_to > 0 else 0
        
        html_content += f"""
        <h4 style="margin: 15px 0 5px 0; color: #1e3a8a; border-left: 4px solid #1e3a8a; padding-left: 8px;">{title}</h4>
        <table style="width: 100%; border-collapse: collapse; font-size: 11px; text-align: center; border: 1px solid #cbd5e1; margin-bottom: 10px;">
            <tr style="background-color: #f1f5f9; font-weight: bold; border: 1px solid #cbd5e1;">
                <th style="padding: 6px; border: 1px solid #cbd5e1;">कालावधी</th>
                <th style="padding: 6px; border: 1px solid #cbd5e1;">Total Students</th>
                <th style="padding: 6px; border: 1px solid #cbd5e1;">वाचन Assessed</th>
                <th style="padding: 6px; border: 1px solid #cbd5e1;">वाचन NIPUN</th>
                <th style="padding: 6px; border: 1px solid #cbd5e1;">लेखन Assessed</th>
                <th style="padding: 6px; border: 1px solid #cbd5e1;">लेखन NIPUN</th>
                <th style="padding: 6px; border: 1px solid #cbd5e1;">संख्याज्ञान Assessed</th>
                <th style="padding: 6px; border: 1px solid #cbd5e1;">संख्याज्ञान NIPUN</th>
                <th style="padding: 6px; border: 1px solid #cbd5e1;">संख्यावरील क्रिया Assessed</th>
                <th style="padding: 6px; border: 1px solid #cbd5e1;">संख्यावरील क्रिया NIPUN</th>
                <th style="padding: 6px; border: 1px solid #cbd5e1;">NIPUN All 4 Subjects</th>
                <th style="padding: 6px; border: 1px solid #cbd5e1;">NIPUN All 4 %</th>
            </tr>
            <tr>
                <td style="padding: 6px; border: 1px solid #cbd5e1; font-weight: bold; background: #f8fafc; text-align: left;">{m_lbl}</td>
                <td style="padding: 6px; border: 1px solid #cbd5e1;">{c_to}</td>
                <td style="padding: 6px; border: 1px solid #cbd5e1;">{c_ra}</td>
                <td style="padding: 6px; border: 1px solid #cbd5e1;">{c_r_ni}</td>
                <td style="padding: 6px; border: 1px solid #cbd5e1;">{c_wa}</td>
                <td style="padding: 6px; border: 1px solid #cbd5e1;">{c_w_ni}</td>
                <td style="padding: 6px; border: 1px solid #cbd5e1;">{c_na}</td>
                <td style="padding: 6px; border: 1px solid #cbd5e1;">{c_n_ni}</td>
                <td style="padding: 6px; border: 1px solid #cbd5e1;">{c_opa}</td>
                <td style="padding: 6px; border: 1px solid #cbd5e1;">{c_op_ni}</td>
                <td style="padding: 6px; border: 1px solid #cbd5e1; font-weight: bold; background: #fdf2f8;">{c_al_ni}</td>
                <td style="padding: 6px; border: 1px solid #cbd5e1; font-weight: bold; color: #1e3a8a; background: #eff6ff;">{c_per:.2f}%</td>
            </tr>
            <tr>
                <td style="padding: 6px; border: 1px solid #cbd5e1; font-weight: bold; background: #f8fafc; text-align: left;">{j_lbl}</td>
                <td style="padding: 6px; border: 1px solid #cbd5e1;"></td><td style="padding: 6px; border: 1px solid #cbd5e1;"></td>
                <td style="padding: 6px; border: 1px solid #cbd5e1;"></td><td style="padding: 6px; border: 1px solid #cbd5e1;"></td>
                <td style="padding: 6px; border: 1px solid #cbd5e1;"></td><td style="padding: 6px; border: 1px solid #cbd5e1;"></td>
                <td style="padding: 6px; border: 1px solid #cbd5e1;"></td><td style="padding: 6px; border: 1px solid #cbd5e1;"></td>
                <td style="padding: 6px; border: 1px solid #cbd5e1;"></td><td style="padding: 6px; border: 1px solid #cbd5e1;"></td>
                <td style="padding: 6px; border: 1px solid #cbd5e1;"></td>
            </tr>
        </table>
        """

    new_tables = [("सन २०२६-२७_इयत्ता पहिली", "जुलै २०२६ (इ. १ ली)"), ("सन २०२६-२७_इयत्ता दुसरी", "जुलै २०२६ (इ. २ री)")]
    for title, j_lbl in new_tables:
        html_content += f"""
        <h4 style="margin: 15px 0 5px 0; color: #1e3a8a; border-left: 4px solid #1e3a8a; padding-left: 8px;">{title}</h4>
        <table style="width: 100%; border-collapse: collapse; font-size: 11px; text-align: center; border: 1px solid #cbd5e1; margin-bottom: 10px;">
            <tr style="background-color: #f1f5f9; font-weight: bold; border: 1px solid #cbd5e1;">
                <th style="padding: 6px; border: 1px solid #cbd5e1;">कालावधी</th>
                <th style="padding: 6px; border: 1px solid #cbd5e1;">Total Students</th>
                <th style="padding: 6px; border: 1px solid #cbd5e1;">वाचन Assessed</th>
                <th style="padding: 6px; border: 1px solid #cbd5e1;">वाचन NIPUN</th>
                <th style="padding: 6px; border: 1px solid #cbd5e1;">लेखन Assessed</th>
                <th style="padding: 6px; border: 1px solid #cbd5e1;">लेखन NIPUN</th>
                <th style="padding: 6px; border: 1px solid #cbd5e1;">संख्याज्ञान Assessed</th>
                <th style="padding: 6px; border: 1px solid #cbd5e1;">संख्याज्ञान NIPUN</th>
                <th style="padding: 6px; border: 1px solid #cbd5e1;">संख्यावरील क्रिया Assessed</th>
                <th style="padding: 6px; border: 1px solid #cbd5e1;">संख्यावरील क्रिया NIPUN</th>
                <th style="padding: 6px; border: 1px solid #cbd5e1;">NIPUN All 4 Subjects</th>
                <th style="padding: 6px; border: 1px solid #cbd5e1;">NIPUN All 4 %</th>
            </tr>
            <tr>
                <td style="padding: 6px; border: 1px solid #cbd5e1; font-weight: bold; background: #f8fafc; text-align: left;">{j_lbl}</td>
                <td style="padding: 6px; border: 1px solid #cbd5e1;"></td><td style="padding: 6px; border: 1px solid #cbd5e1;"></td>
                <td style="padding: 6px; border: 1px solid #cbd5e1;"></td><td style="padding: 6px; border: 1px solid #cbd5e1;"></td>
                <td style="padding: 6px; border: 1px solid #cbd5e1;"></td><td style="padding: 6px; border: 1px solid #cbd5e1;"></td>
                <td style="padding: 6px; border: 1px solid #cbd5e1;"></td><td style="padding: 6px; border: 1px solid #cbd5e1;"></td>
                <td style="padding: 6px; border: 1px solid #cbd5e1;"></td><td style="padding: 6px; border: 1px solid #cbd5e1;"></td>
                <td style="padding: 6px; border: 1px solid #cbd5e1;"></td>
            </tr>
        </table>
        """

    tot_all_to = filtered_df['all Total Student'].sum()
    tot_all_ra = filtered_df['all reading assesed'].sum()
    tot_all_r_ni = filtered_df['all reading nipun'].sum()
    tot_all_wa = filtered_df['all writing assesed'].sum()
    tot_all_w_ni = filtered_df['all writing nipun'].sum()
    tot_all_na = filtered_df['all numercy assesed'].sum()
    tot_all_n_ni = filtered_df['all numercy nipun'].sum()
    tot_all_opa = filtered_df['all 0peration assesed'].sum()
    tot_all_op_ni = filtered_df['all operation nipun'].sum()
    tot_all_al_ni = filtered_df['all all nipun'].sum()
    tot_all_per = (tot_all_al_ni / tot_all_to * 100) if tot_all_to > 0 else 0

    html_content += f"""
    <h4 style="margin: 15px 0 5px 0; color: #1e3a8a; border-left: 4px solid #1e3a8a; padding-left: 8px;">इयत्ता २ री ते ५ वी एकूण (All Classes Summary)</h4>
    <table style="width: 100%; border-collapse: collapse; font-size: 11px; text-align: center; border: 1px solid #cbd5e1; margin-bottom: 20px;">
        <tr style="background-color: #f1f5f9; font-weight: bold; border: 1px solid #cbd5e1;">
            <th style="padding: 6px; border: 1px solid #cbd5e1;">कालावधी</th>
            <th style="padding: 6px; border: 1px solid #cbd5e1;">Total Students</th>
            <th style="padding: 6px; border: 1px solid #cbd5e1;">वाचन Assessed</th>
            <th style="padding: 6px; border: 1px solid #cbd5e1;">वाचन NIPUN</th>
            <th style="padding: 6px; border: 1px solid #cbd5e1;">लेखन Assessed</th>
            <th style="padding: 6px; border: 1px solid #cbd5e1;">लेखन NIPUN</th>
            <th style="padding: 6px; border: 1px solid #cbd5e1;">संख्याज्ञान Assessed</th>
            <th style="padding: 6px; border: 1px solid #cbd5e1;">संख्याज्ञान NIPUN</th>
            <th style="padding: 6px; border: 1px solid #cbd5e1;">संख्यावरील क्रिया Assessed</th>
            <th style="padding: 6px; border: 1px solid #cbd5e1;">संख्यावरील क्रिया NIPUN</th>
            <th style="padding: 6px; border: 1px solid #cbd5e1;">NIPUN All 4 Subjects</th>
            <th style="padding: 6px; border: 1px solid #cbd5e1;">NIPUN All 4 %</th>
        </tr>
        <tr>
            <td style="padding: 6px; border: 1px solid #cbd5e1; font-weight: bold; background: #f8fafc; text-align: left;">मार्च २०२६ एकूण</td>
            <td style="padding: 6px; border: 1px solid #cbd5e1;">{tot_all_to}</td>
            <td style="padding: 6px; border: 1px solid #cbd5e1;">{tot_all_ra}</td>
            <td style="padding: 6px; border: 1px solid #cbd5e1;">{tot_all_r_ni}</td>
            <td style="padding: 6px; border: 1px solid #cbd5e1;">{tot_all_wa}</td>
            <td style="padding: 6px; border: 1px solid #cbd5e1;">{tot_all_w_ni}</td>
            <td style="padding: 6px; border: 1px solid #cbd5e1;">{tot_all_na}</td>
            <td style="padding: 6px; border: 1px solid #cbd5e1;">{tot_all_n_ni}</td>
            <td style="padding: 6px; border: 1px solid #cbd5e1;">{tot_all_opa}</td>
            <td style="padding: 6px; border: 1px solid #cbd5e1;">{tot_all_op_ni}</td>
            <td style="padding: 6px; border: 1px solid #cbd5e1; font-weight: bold; background: #fdf2f8;">{tot_all_al_ni}</td>
            <td style="padding: 6px; border: 1px solid #cbd5e1; font-weight: bold; color: #1e3a8a; background: #eff6ff;">{tot_all_per:.2f}%</td>
        </tr>
        <tr>
            <td style="padding: 6px; border: 1px solid #cbd5e1; font-weight: bold; background: #f8fafc; text-align: left;">जुलै २०२६ एकूण</td>
            <td style="padding: 6px; border: 1px solid #cbd5e1;"></td><td style="padding: 6px; border: 1px solid #cbd5e1;"></td>
            <td style="padding: 6px; border: 1px solid #cbd5e1;"></td><td style="padding: 6px; border: 1px solid #cbd5e1;"></td>
            <td style="padding: 6px; border: 1px solid #cbd5e1;"></td><td style="padding: 6px; border: 1px solid #cbd5e1;"></td>
            <td style="padding: 6px; border: 1px solid #cbd5e1;"></td><td style="padding: 6px; border: 1px solid #cbd5e1;"></td>
            <td style="padding: 6px; border: 1px solid #cbd5e1;"></td><td style="padding: 6px; border: 1px solid #cbd5e1;"></td>
            <td style="padding: 6px; border: 1px solid #cbd5e1;"></td>
        </tr>
    </table>
    """

    # --- 🎯 नियम: लॉजिकनुसार पहिला अहवाल ऑटो-बदल (Clusterwise OR Schoolwise) ---
    if selected_cluster == "सर्व (All)":
        report_title = "📊 Cluster Wise Report (According All NIPUN Percentage)"
        grouped_cluster = filtered_df.groupby(['block', 'cluster']).agg({
            'all all nipun': 'sum',
            'all Total Student': 'sum'
        }).reset_index()
        grouped_cluster['all all nipun percentage'] = (grouped_cluster['all all nipun'] / grouped_cluster['all Total Student'] * 100).fillna(0)
        grouped_cluster = grouped_cluster.sort_values(by='all all nipun percentage', ascending=False).reset_index(drop=True)
        
        html_content += f"""
        <br><hr style="border-top: 2px dashed #cbd5e1;"><br>
        <h3 style="color: #1e3a8a; text-align: center;">{report_title}</h3>
        <table style="width: 100%; border-collapse: collapse; font-size: 11px; text-align: left; border: 1px solid #cbd5e1;">
            <thead>
                <tr style="background-color: #1e3a8a; color: white; font-weight: bold;">
                    <th style="padding: 8px; border: 1px solid #cbd5e1;">Sr.No.</th>
                    <th style="padding: 8px; border: 1px solid #cbd5e1;">Block</th>
                    <th style="padding: 8px; border: 1px solid #cbd5e1;">Cluster Name</th>
                    <th style="padding: 8px; border: 1px solid #cbd5e1; text-align: center;">All NIPUN Percentage</th>
                    <th style="padding: 8px; border: 1px solid #cbd5e1; text-align: center;">Rank</th>
                </tr>
            </thead>
            <tbody>
        """
        for idx, row in grouped_cluster.iterrows():
            html_content += f"""
                <tr>
                    <td style="padding: 6px; border: 1px solid #cbd5e1;">{idx + 1}</td>
                    <td style="padding: 6px; border: 1px solid #cbd5e1;">{row['block']}</td>
                    <td style="padding: 6px; border: 1px solid #cbd5e1;">{row['cluster']}</td>
                    <td style="padding: 6px; border: 1px solid #cbd5e1; text-align: center; font-weight: bold; color: #1e3a8a;">{row['all all nipun percentage']:.2f}%</td>
                    <td style="padding: 6px; border: 1px solid #cbd5e1; text-align: center; font-weight: bold;">#{idx + 1}</td>
                </tr>
            """
    else:
        report_title = f"🏫 School Wise Report for Cluster: {selected_cluster} (According All NIPUN Percentage)"
        school_wise_df = filtered_df.copy()
        school_wise_df = school_wise_df.sort_values(by='all all nipun percentage', ascending=False).reset_index(drop=True)
        
        html_content += f"""
        <br><hr style="border-top: 2px dashed #cbd5e1;"><br>
        <h3 style="color: #1e3a8a; text-align: center;">{report_title}</h3>
        <table style="width: 100%; border-collapse: collapse; font-size: 11px; text-align: left; border: 1px solid #cbd5e1;">
            <thead>
                <tr style="background-color: #1e3a8a; color: white; font-weight: bold;">
                    <th style="padding: 8px; border: 1px solid #cbd5e1;">Sr.No.</th>
                    <th style="padding: 8px; border: 1px solid #cbd5e1;">Block</th>
                    <th style="padding: 8px; border: 1px solid #cbd5e1;">Cluster</th>
                    <th style="padding: 8px; border: 1px solid #cbd5e1;">UDISE Code</th>
                    <th style="padding: 8px; border: 1px solid #cbd5e1;">School Name</th>
                    <th style="padding: 8px; border: 1px solid #cbd5e1; text-align: center;">All NIPUN Percentage</th>
                    <th style="padding: 8px; border: 1px solid #cbd5e1; text-align: center;">Rank</th>
                </tr>
            </thead>
            <tbody>
        """
        for idx, row in school_wise_df.iterrows():
            html_content += f"""
                <tr>
                    <td style="padding: 6px; border: 1px solid #cbd5e1;">{idx + 1}</td>
                    <td style="padding: 6px; border: 1px solid #cbd5e1;">{row['block']}</td>
                    <td style="padding: 6px; border: 1px solid #cbd5e1;">{row['cluster']}</td>
                    <td style="padding: 6px; border: 1px solid #cbd5e1;">{row['udise']}</td>
                    <td style="padding: 6px; border: 1px solid #cbd5e1;">{row['school']}</td>
                    <td style="padding: 6px; border: 1px solid #cbd5e1; text-align: center; font-weight: bold; color: #1e3a8a;">{row['all all nipun percentage']:.2f}%</td>
                    <td style="padding: 6px; border: 1px solid #cbd5e1; text-align: center; font-weight: bold;">#{idx + 1}</td>
                </tr>
            """
    html_content += "</tbody></table>"

    # --- नॉट असेस्ड शाळांची यादी ---
    not_assessed_df = filtered_df[~filtered_df['is_assessed'] & (filtered_df['all Total Student'] > 0)].reset_index(drop=True)
    
    html_content += """
    <br><hr style="border-top: 2px dashed #cbd5e1;"><br>
    <h3 style="color: #b91c1c; text-align: center;">⚠️ Not Assessed School List (एकही विद्यार्थ्याची परीक्षा न घेतलेल्या शाळा)</h3>
    <table style="width: 100%; border-collapse: collapse; font-size: 11px; text-align: left; border: 1px solid #cbd5e1;">
        <thead>
            <tr style="background-color: #b91c1c; color: white; font-weight: bold;">
                <th style="padding: 8px; border: 1px solid #cbd5e1;">Sr.No.</th>
                <th style="padding: 8px; border: 1px solid #cbd5e1;">Block</th>
                <th style="padding: 8px; border: 1px solid #cbd5e1;">Cluster</th>
                <th style="padding: 8px; border: 1px solid #cbd5e1;">UDISE Code</th>
                <th style="padding: 8px; border: 1px solid #cbd5e1;">School Name</th>
                <th style="padding: 8px; border: 1px solid #cbd5e1;">Management</th>
                <th style="padding: 8px; border: 1px solid #cbd5e1; text-align: center;">All Total Student</th>
                <th style="padding: 8px; border: 1px solid #cbd5e1; text-align: center;">Assessed Student</th>
                <th style="padding: 8px; border: 1px solid #cbd5e1; color: yellow;">Remark</th>
            </tr>
        </thead>
        <tbody>
    """
    if len(not_assessed_df) == 0:
        html_content += """
            <tr>
                <td colspan="9" style="padding: 10px; text-align: center; font-weight: bold; color: green;">सर्व शाळांचे मूल्यांकन पूर्ण झाले आहे! (No Unassessed Schools)</td>
            </tr>
        """
    else:
        for idx, row in not_assessed_df.iterrows():
            html_content += f"""
                <tr>
                    <td style="padding: 6px; border: 1px solid #cbd5e1;">{idx + 1}</td>
                    <td style="padding: 6px; border: 1px solid #cbd5e1;">{row['block']}</td>
                    <td style="padding: 6px; border: 1px solid #cbd5e1;">{row['cluster']}</td>
                    <td style="padding: 6px; border: 1px solid #cbd5e1;">{row['udise']}</td>
                    <td style="padding: 6px; border: 1px solid #cbd5e1;">{row['school']}</td>
                    <td style="padding: 6px; border: 1px solid #cbd5e1;">{row['management_type']}</td>
                    <td style="padding: 6px; border: 1px solid #cbd5e1; text-align: center;">{row['all Total Student']}</td>
                    <td style="padding: 6px; border: 1px solid #cbd5e1; text-align: center; font-weight: bold; color: red;">0</td>
                    <td style="padding: 6px; border: 1px solid #cbd5e1; font-weight: bold; color: #b91c1c;">परीक्षा घेतली नाही</td>
                </tr>
            """
    html_content += "</tbody></table>"
    html_content += "</div>"
    
    components.html(html_content, height=2200, scrolling=True)
    
    st.sidebar.download_button(
        label="📥 Export to HTML / Print Report",
        data=html_content,
        file_name=f"NIPUN_Master_Report_{selected_cluster}.html",
        mime="text/html"
    )