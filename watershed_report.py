import os
import base64
import glob
import pandas as pd
from datetime import datetime

def image_to_base64(filepath):
    try:
        with open(filepath, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
            ext = os.path.splitext(filepath)[1][1:]
            if ext == 'jpg': ext = 'jpeg'
            return f"data:image/{ext};base64,{encoded_string}"
    except Exception as e:
        print(f"Error encoding {filepath}: {e}")
        return None

def get_stats_html():
    stats_html = ""
    stats_dir = 'outputs/stats'
    if os.path.exists(stats_dir):
        for csv_file in glob.glob(os.path.join(stats_dir, '*.csv')):
            try:
                df = pd.read_csv(csv_file)
                title = os.path.basename(csv_file).replace('_', ' ').replace('.csv', '')
                stats_html += f"<h3>{title}</h3>\n"
                stats_html += df.to_html(classes="stats-table", index=False) + "\n"
            except Exception as e:
                print(f"Error reading {csv_file}: {e}")
    else:
        stats_html = "<p>No statistics data available.</p>"
    return stats_html

def get_maps_html():
    maps_html = ""
    maps_dir = 'outputs/maps'
    if os.path.exists(maps_dir):
        map_files = glob.glob(os.path.join(maps_dir, '*.png'))
        for map_file in sorted(map_files):
            b64_img = image_to_base64(map_file)
            if b64_img:
                title = os.path.basename(map_file).replace('_', ' ').replace('.png', '').title()
                maps_html += f"""
                <div class="map-card">
                    <h3>{title}</h3>
                    <img src="{b64_img}" alt="{title}" style="max-width: 100%; border-radius: 8px;">
                </div>
                """
    else:
        maps_html = "<p>No maps generated yet.</p>"
    return maps_html

def generate_report():
    out_file = 'outputs/Murredu_Watershed_Report.html'
    os.makedirs('outputs', exist_ok=True)
    
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Murredu Watershed Analysis Report</title>
        <style>
            :root {{
                --bg-color: #121212;
                --text-color: #e0e0e0;
                --card-bg: #1e1e1e;
                --accent-color: #bb86fc;
                --border-color: #333;
            }}
            body {{
                background-color: var(--bg-color);
                color: var(--text-color);
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                margin: 0;
                padding: 20px;
                line-height: 1.6;
            }}
            .container {{
                max-width: 1200px;
                margin: 0 auto;
            }}
            header {{
                text-align: center;
                padding: 40px 0;
                border-bottom: 2px solid var(--border-color);
                margin-bottom: 40px;
            }}
            h1 {{
                color: var(--accent-color);
                font-size: 2.5em;
                margin-bottom: 10px;
            }}
            h2 {{
                color: #03dac6;
                border-bottom: 1px solid var(--border-color);
                padding-bottom: 10px;
                margin-top: 40px;
            }}
            .section {{
                background-color: var(--card-bg);
                padding: 30px;
                border-radius: 12px;
                margin-bottom: 30px;
                box-shadow: 0 4px 6px rgba(0,0,0,0.3);
            }}
            .map-card {{
                background-color: #2c2c2c;
                padding: 20px;
                border-radius: 8px;
                margin-bottom: 30px;
                text-align: center;
            }}
            .stats-table {{
                width: 100%;
                border-collapse: collapse;
                margin-top: 20px;
                background-color: #2c2c2c;
                color: #fff;
            }}
            .stats-table th, .stats-table td {{
                padding: 12px;
                border: 1px solid var(--border-color);
                text-align: left;
            }}
            .stats-table th {{
                background-color: #333;
                color: var(--accent-color);
            }}
            .flowchart {{
                background-color: #2c2c2c;
                padding: 20px;
                border-radius: 8px;
                font-family: monospace;
                white-space: pre;
                overflow-x: auto;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <header>
                <h1>Murredu Watershed Analysis Report</h1>
                <p>Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            </header>

            <div class="section">
                <h2>1. Study Area Overview</h2>
                <p>This report presents a comprehensive hydrological and terrain analysis of the Murredu Watershed. It includes geomorphological characteristics, drainage network delineation, and remote sensing derived insights.</p>
            </div>

            <div class="section">
                <h2>2. Data Sources</h2>
                <ul>
                    <li><strong>Elevation Data:</strong> Copernicus DEM 30m</li>
                    <li><strong>Optical Imagery:</strong> Sentinel-2 L2A Multispectral Data</li>
                </ul>
            </div>

            <div class="section">
                <h2>3. Methodology</h2>
                <div class="flowchart">
[DEM Acquisition] -> [Terrain Analysis: Slope, Aspect] -> [Hydrology: Flow Acc, Streams]
       |
       v
[Sentinel-2 Data] -> [Indices: NDVI, NDWI] -> [LULC & Water Masks]
       |
       v
[Map Generation] -> [Statistical Extraction] -> [Final Report Generation]
                </div>
            </div>

            <div class="section">
                <h2>4. Results & Maps</h2>
                {get_maps_html()}
            </div>

            <div class="section">
                <h2>5. Statistical Analysis</h2>
                {get_stats_html()}
            </div>

            <div class="section">
                <h2>6. Conclusions</h2>
                <p>The automated GIS pipeline successfully delineated the Murredu watershed, identified the drainage network under varying thresholds, and mapped vegetation and water bodies. The outputs provided in this report can be used for informed water resource management and planning.</p>
            </div>
        </div>
    </body>
    </html>
    """
    try:
        with open(out_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        print(f"Successfully generated report at {out_file}")
    except Exception as e:
        print(f"Error writing report: {e}")

if __name__ == '__main__':
    generate_report()
