import streamlit as st
import pandas as pd
import geopandas as gpd
import folium
from folium.features import GeoJson, GeoJsonTooltip
import branca.colormap as cm
import base64
from streamlit_folium import folium_static

# Apply custom CSS for a white background
def set_custom_style():
    """
    Apply custom CSS styles for a minimalist design.
    """
    st.markdown(
        """
        <style>
        /* Set app background color to white */
        .stApp {
            background-color: #FFFFFF;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

# Set page configuration (optional, can be modified as needed)
st.set_page_config(page_title="Demographic Maps with Bar Charts", layout="wide")

@st.cache_data
def load_data(file_path='merged_gdf_specific.pkl'):
    """
    Loads the merged GeoDataFrame from a pickle file.
    Returns a GeoDataFrame.
    """
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

def extract_variable_labels(gdf):
    """
    Extracts variable labels from the GeoDataFrame.
    Assumes that labels are embedded in the column names after the last underscore.
    Returns a dictionary mapping variable codes to labels.
    """
    variable_labels = {}
    for col in gdf.columns:
        if col.startswith('P12_'):
            parts = col.split('_', 2)  # Split into ['P12', '027N', 'Total Population']
            if len(parts) == 3:
                label = parts[2].strip()
            else:
                label = col  # Fallback to variable code if label not present
            variable_labels[col] = label
    return variable_labels

def create_colormap(gdf, variable, variable_labels):
    """
    Creates a color map for the specified variable.
    Returns a branca colormap object.
    """
    # Handle cases where the variable might have constant values
    min_val = gdf[variable].min()
    max_val = gdf[variable].max()
    
    if min_val == max_val:
        # Avoid colormap errors by setting a default range
        min_val = min_val - 1
        max_val = max_val + 1
    
    colormap = cm.linear.OrRd_09.scale(
        min_val,
        max_val
    )
    colormap.caption = f'Demographic Metric: {variable_labels.get(variable, variable)}'
    return colormap

def generate_map(gdf, variable, variable_labels):
    """
    Generates a Folium map with color-coded districts and popups containing bar charts.
    Returns a Folium Map object.
    """
    # Initialize Folium map
    m = folium.Map(location=[37.8, -96], zoom_start=4)

    # Create color scale
    colormap = create_colormap(gdf, variable, variable_labels)
    colormap.add_to(m)

    # Function to create HTML content with two bar charts
    def create_html_content(row):
        """
        Create HTML content with two bar charts embedded.
        """
        # Extract the base64 images
        female_img = row['Female_BarChart']
        male_img = row['Male_BarChart']

        # Get district name
        district_name = row['NAME']

        # Handle cases where bar charts might not be generated
        if female_img is None or male_img is None:
            html = f"""
            <div style="width: 300px;">
                <h4>{district_name}</h4>
                <p>No data available for bar charts.</p>
            </div>
            """
        else:
            # Create HTML content
            html = f"""
            <div style="width: 300px;">
                <h4>{district_name}</h4>
                <div style="display: flex; flex-direction: column; gap: 10px;">
                    <div>
                        <h5>Female Age Data</h5>
                        <img src="data:image/png;base64,{female_img}" style="width: 280px; height: 150px;">
                    </div>
                    <div>
                        <h5>Male Age Data</h5>
                        <img src="data:image/png;base64,{male_img}" style="width: 280px; height: 150px;">
                    </div>
                </div>
            </div>
            """
        return html

    # Iterate over each row to add GeoJson with popups
    for idx, row in gdf.iterrows():
        # Skip rows without geometry
        if row['geometry'] is None:
            continue

        # Create HTML content with embedded bar charts
        html_content = create_html_content(row)

        # Create an iframe for the popup
        iframe = folium.IFrame(html=html_content, width=320, height=400)
        popup = folium.Popup(iframe, max_width=320)

        # Define the style function for color-coding
        def style_function(feature):
            val = feature['properties'].get(variable, None)
            if pd.isna(val):
                color = 'grey'
            else:
                color = colormap(val)
            return {
                'fillColor': color,
                'color': 'black',
                'weight': 0.5,
                'fillOpacity': 0.7,
            }

        # Create a GeoJSON Feature with properties and geometry
        # Exclude 'geometry', 'Female_BarChart', 'Male_BarChart' from properties
        properties = row.drop(['geometry', 'Female_BarChart', 'Male_BarChart']).to_dict()
        feature = {
            'type': 'Feature',
            'properties': properties,
            'geometry': row['geometry'].__geo_interface__
        }

        # Add GeoJson layer with popup
        folium.GeoJson(
            feature,
            style_function=style_function,
            highlight_function=lambda x: {'weight':3, 'color':'blue'},
            tooltip=folium.Tooltip(row['NAME']),
            popup=popup
        ).add_to(m)

    # Add layer control (optional)
    folium.LayerControl().add_to(m)

    return m

def main():
    # Apply custom styles
    set_custom_style()

    # Load data
    gdf = load_data()

    # Extract demographic variable codes (assuming they start with 'P12_')
    demographic_vars = [col for col in gdf.columns if col.startswith('P12_')]

    # Extract variable labels from gdf
    variable_labels = extract_variable_labels(gdf)

    # Define the preset demographic variable for color-coding
    PRESET_VARIABLE = 'P12_027N'  # <-- Replace with your desired variable code

    # Check if the preset variable exists in the data
    if PRESET_VARIABLE not in gdf.columns:
        st.error(f"Preset variable '{PRESET_VARIABLE}' not found in the data.")
        st.stop()

    # Display the preset variable being used
    preset_label = variable_labels.get(PRESET_VARIABLE, PRESET_VARIABLE)
    st.write(f"**Color-Coding Demographic Metric:** {preset_label}")

    # Generate the map using the preset variable
    folium_map = generate_map(gdf, PRESET_VARIABLE, variable_labels)

    # Display the map
    folium_static(folium_map, width=1200, height=800)

    # **Optional Footer (Can be removed if desired)**
    st.markdown("---")
    st.markdown("**Data Source:** 2020 Census API | **App Developed by:** Your Name")

if __name__ == "__main__":
    main()
