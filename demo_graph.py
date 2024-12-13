import streamlit as st
import pandas as pd
import geopandas as gpd
import folium
from folium.features import GeoJson
import branca.colormap as cm
from streamlit_folium import folium_static
import matplotlib.pyplot as plt
import numpy as np
from io import BytesIO
import base64

# --------------------------------------------
# Define variable sets
# --------------------------------------------
variables_set_female_age = [
    "P12_027N", "P12_028N", "P12_029N", "P12_030N", "P12_031N",
    "P12_032N", "P12_033N", "P12_034N", "P12_035N", "P12_036N",
    "P12_037N", "P12_038N", "P12_039N", "P12_040N", "P12_041N",
    "P12_042N", "P12_043N", "P12_044N", "P12_045N", "P12_046N",
    "P12_047N", "P12_048N", "P12_049N"
]

variables_set_male_age = [
    "P12_003N", "P12_004N", "P12_005N", "P12_006N", "P12_007N",
    "P12_008N", "P12_009N", "P12_010N", "P12_011N", "P12_012N",
    "P12_013N", "P12_014N", "P12_015N", "P12_016N", "P12_017N",
    "P12_018N", "P12_019N", "P12_020N", "P12_021N", "P12_022N",
    "P12_023N", "P12_024N", "P12_025N"
]

# Third set of variables
variables_set_third = [
    "P10_003N", "P10_004N", "P10_005N", "P10_006N",
    "P10_007N", "P10_008N", "P10_009N", "P10_010N", "P10_011N",
    "P10_012N", "P10_013N", "P10_014N", "P10_015N", "P10_016N",
    "P10_017N", "P10_018N", "P10_019N", "P10_020N", "P10_021N",
    "P10_022N", "P10_023N", "P10_024N", "P10_025N"
]

# --------------------------------------------
# Use the provided variable_labels dictionary
# --------------------------------------------
variable_labels = {
 'P10_003N': 'White alone',
 'P10_004N': 'Black or African American alone',
 'P10_005N': 'American Indian and Alaska Native alone',
 'P10_006N': 'Asian alone',
 'P10_007N': 'Native Hawaiian and Other Pacific Islander alone',
 'P10_008N': 'Some Other Race alone',
 'P10_009N': 'Population of two or more races:',
 'P10_010N': 'Population of two races:',
 'P10_011N': 'White; Black or African American',
 'P10_012N': 'White; American Indian and Alaska Native',
 'P10_013N': 'White; Asian',
 'P10_014N': 'White; Native Hawaiian and Other Pacific Islander',
 'P10_015N': 'White; Some Other Race',
 'P10_016N': 'Black or African American; American Indian and Alaska Native',
 'P10_017N': 'Black or African American; Asian',
 'P10_018N': 'Black or African American; Native Hawaiian and Other Pacific Islander',
 'P10_019N': 'Black or African American; Some Other Race',
 'P10_020N': 'American Indian and Alaska Native; Asian',
 'P10_021N': 'American Indian and Alaska Native; Native Hawaiian and Other Pacific Islander',
 'P10_022N': 'American Indian and Alaska Native; Some Other Race',
 'P10_023N': 'Asian; Native Hawaiian and Other Pacific Islander',
 'P10_024N': 'Asian; Some Other Race',
 'P10_025N': 'Native Hawaiian and Other Pacific Islander; Some Other Race',
 'P12_003N': 'Under 5 years',
 'P12_004N': '5 to 9 years',
 'P12_005N': '10 to 14 years',
 'P12_006N': '15 to 17 years',
 'P12_007N': '18 and 19 years',
 'P12_008N': '20 years',
 'P12_009N': '21 years',
 'P12_010N': '22 to 24 years',
 'P12_011N': '25 to 29 years',
 'P12_012N': '30 to 34 years',
 'P12_013N': '35 to 39 years',
 'P12_014N': '40 to 44 years',
 'P12_015N': '45 to 49 years',
 'P12_016N': '50 to 54 years',
 'P12_017N': '55 to 59 years',
 'P12_018N': '60 and 61 years',
 'P12_019N': '62 to 64 years',
 'P12_020N': '65 and 66 years',
 'P12_021N': '67 to 69 years',
 'P12_022N': '70 to 74 years',
 'P12_023N': '75 to 79 years',
 'P12_024N': '80 to 84 years',
 'P12_025N': '85 years and over',
 'P12_027N': 'Under 5 years',
 'P12_028N': '5 to 9 years',
 'P12_029N': '10 to 14 years',
 'P12_030N': '15 to 17 years',
 'P12_031N': '18 and 19 years',
 'P12_032N': '20 years',
 'P12_033N': '21 years',
 'P12_034N': '22 to 24 years',
 'P12_035N': '25 to 29 years',
 'P12_036N': '30 to 34 years',
 'P12_037N': '35 to 39 years',
 'P12_038N': '40 to 44 years',
 'P12_039N': '45 to 49 years',
 'P12_040N': '50 to 54 years',
 'P12_041N': '55 to 59 years',
 'P12_042N': '60 and 61 years',
 'P12_043N': '62 to 64 years',
 'P12_044N': '65 and 66 years',
 'P12_045N': '67 to 69 years',
 'P12_046N': '70 to 74 years',
 'P12_047N': '75 to 79 years',
 'P12_048N': '80 to 84 years',
 'P12_049N': '85 years and over'
}

def set_custom_style():
    st.markdown(
        """
        <style>
        .stApp {
            background-color: #FFFFFF;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

st.set_page_config(page_title="Demographic Maps with Bar Charts", layout="wide")

@st.cache_data
def load_data(file_path='merged_gdf_specific.pkl'):
    try:
        gdf = pd.read_pickle(file_path)
        gdf = gpd.GeoDataFrame(gdf, geometry='geometry')
    except FileNotFoundError:
        st.error(f"Data file not found at path: {file_path}")
        st.stop()
    except Exception as e:
        st.error(f"Failed to load data: {e}")
        st.stop()
    return gdf

def get_label(var_code, variable_labels):
    return variable_labels.get(var_code, var_code)

def create_colormap(gdf, variable, variable_labels):
    min_val = gdf[variable].min()
    max_val = gdf[variable].max()
    if min_val == max_val:
        min_val = min_val - 1
        max_val = max_val + 1

    colormap = cm.linear.OrRd_09.scale(min_val, max_val)
    colormap.caption = f'Demographic Metric: {variable_labels.get(variable, variable)}'
    return colormap

def generate_population_pyramid_chart(row, female_vars, male_vars, labels_dict):
    female_values = [row[v] for v in female_vars if v in row and pd.notna(row[v])]
    male_values = [row[v] for v in male_vars if v in row and pd.notna(row[v])]

    if len(female_values) == 0 and len(male_values) == 0:
        return None

    length = min(len(female_values), len(male_values))
    female_values = female_values[:length]
    male_values = male_values[:length]

    female_values = np.array(female_values)
    male_values = np.array(male_values)

    female_labels = [labels_dict.get(v, v) for v in female_vars][:length]

    plt.figure(figsize=(6, 8))
    y_positions = np.arange(length)

    plt.barh(y_positions, -male_values, color='skyblue', label='Male')
    plt.barh(y_positions, female_values, color='pink', label='Female')

    plt.yticks(y_positions, female_labels)
    district_name = row.get('NAME', 'Unknown District')
    plt.xlabel('Population Count')
    plt.title(district_name)

    plt.axvline(0, color='black')

    max_val = max(male_values.max() if len(male_values) > 0 else 0,
                  female_values.max() if len(female_values) > 0 else 0)
    plt.xlim(-max_val, max_val)

    plt.legend()
    plt.tight_layout()

    buf = BytesIO()
    plt.savefig(buf, format='png', dpi=100)
    plt.close()
    buf.seek(0)
    return base64.b64encode(buf.read()).decode('utf-8')

def generate_third_chart(row, third_vars, labels_dict):
    values = [row[v] for v in third_vars if v in row and pd.notna(row[v])]
    if not values:
        return None

    labels = [labels_dict.get(var, var) for var in third_vars]

    plt.figure(figsize=(14, 12))
    plt.bar(labels, values, color='teal')
    plt.xticks(rotation=45, ha='right', fontsize=10)
    plt.ylabel('Count', fontsize=14)
    plt.title('Ethnic Breakdown', fontsize=14)
    plt.tight_layout()

    buf = BytesIO()
    plt.savefig(buf, format='png', dpi=100)
    plt.close()
    buf.seek(0)
    return base64.b64encode(buf.read()).decode('utf-8')

def generate_map(gdf, variable, variable_labels):
    m = folium.Map(location=[37.8, -96], zoom_start=4)
    colormap = create_colormap(gdf, variable, variable_labels)
    colormap.add_to(m)

    def create_html_content(row):
        pyramid_img = row['Population_Pyramid']
        third_img = row['Third_BarChart']
        district_name = row.get('NAME', 'Unknown District')

        pyramid_section = f"<img src='data:image/png;base64,{pyramid_img}' style='width:280px;height:400px;'>" if pyramid_img else "<p>No population pyramid data</p>"
        third_section = f"<img src='data:image/png;base64,{third_img}' style='width:280px;height:150px;'>" if third_img else "<p>No third data</p>"

        html = f"""
        <div style="width:300px;">
            <h4>{district_name}</h4>
            {pyramid_section}
            <h5>Additional Data Set</h5>{third_section}
        </div>
        """
        return html

    for idx, row in gdf.iterrows():
        if row['geometry'] is None:
            continue

        html_content = create_html_content(row)
        iframe = folium.IFrame(html=html_content, width=320, height=600)
        popup = folium.Popup(iframe, max_width=320)

        def style_function(feature):
            val = feature['properties'].get(variable, None)
            color = colormap(val) if pd.notna(val) else 'grey'
            return {
                'fillColor': color,
                'color': 'black',
                'weight': 0.5,
                'fillOpacity': 0.7,
            }

        properties = row.drop(['geometry', 'Population_Pyramid', 'Third_BarChart'], errors='ignore').to_dict()
        feature = {
            'type': 'Feature',
            'properties': properties,
            'geometry': row['geometry'].__geo_interface__
        }

        folium.GeoJson(
            feature,
            style_function=style_function,
            highlight_function=lambda x: {'weight':3, 'color':'blue'},
            tooltip=folium.Tooltip(row.get('NAME', 'Unknown District')),
            popup=popup
        ).add_to(m)

    folium.LayerControl().add_to(m)
    return m

def main():
    set_custom_style()
    gdf = load_data()

    # Generate the Population_Pyramid and Third_BarChart columns
    if 'Population_Pyramid' not in gdf.columns:
        gdf['Population_Pyramid'] = None
    if 'Third_BarChart' not in gdf.columns:
        gdf['Third_BarChart'] = None

    for idx, row in gdf.iterrows():
        if row['geometry'] is None:
            continue
        pyramid_chart = generate_population_pyramid_chart(row, variables_set_female_age, variables_set_male_age, variable_labels)
        third_chart = generate_third_chart(row, variables_set_third, variable_labels)
        gdf.at[idx, 'Population_Pyramid'] = pyramid_chart
        gdf.at[idx, 'Third_BarChart'] = third_chart

    PRESET_VARIABLE = 'P12_027N'
    if PRESET_VARIABLE not in gdf.columns:
        st.error(f"Preset variable '{PRESET_VARIABLE}' not found in the data.")
        st.stop()

    preset_label = variable_labels.get(PRESET_VARIABLE, PRESET_VARIABLE)
    st.write(f"**Color-Coding Demographic Metric:** {preset_label}")

    folium_map = generate_map(gdf, PRESET_VARIABLE, variable_labels)
    folium_static(folium_map, width=1200, height=800)

    st.markdown("---")
    st.markdown("**Data Source:** 2020 Census API | **App Developed by:** Your Name")

if __name__ == "__main__":
    main()
