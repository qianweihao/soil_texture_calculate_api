"""
基于Flask实现的HTTP API,用于查询任意经纬度位置的土壤质地组成(数据源基于SoilGrid250m)
"""
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import pandas as pd
from soilgrids import SoilGrids
import rioxarray
import os
import tempfile
import concurrent.futures
import time
import json

app = Flask(__name__)
CORS(app)  

@app.route('/')
def index():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>土壤质地查询API</title>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; line-height: 1.6; }
            .container { max-width: 800px; margin: 0 auto; }
            h1 { color: #336699; }
            input, button { padding: 8px; margin: 5px 0; }
            button { background-color: #4CAF50; color: white; border: none; cursor: pointer; }
            button:hover { background-color: #45a049; }
            pre { background-color: #f5f5f5; padding: 10px; border-radius: 5px; overflow-x: auto; }
            .loading { display: none; color: #666; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>土壤质地查询API</h1>
            <p>输入经纬度查询特定位置的土壤质地组成及占比</p>
            
            <div>
                <label for="longitude">经度:</label>
                <input type="number" id="longitude" step="0.0001" value="115.0" />
                
                <label for="latitude">纬度:</label>
                <input type="number" id="latitude" step="0.0001" value="30.5" />
                
                <button id="queryBtn">查询</button>
                <span id="loading" class="loading">查询中，请稍候...</span>
            </div>
            
            <h2>结果</h2>
            <pre id="result">请输入经纬度后点击查询按钮</pre>
            
            <h2>API使用说明</h2>
            <p>API端点: <code>/api/soil-texture</code></p>
            <p>查询参数:</p>
            <ul>
                <li><code>longitude</code>: 经度 (必需)</li>
                <li><code>latitude</code>: 纬度 (必需)</li>
            </ul>
            <p>示例请求: <code>/api/soil-texture?longitude=115.0&latitude=30.5</code></p>
            
            <script>
                document.getElementById('queryBtn').addEventListener('click', function() {
                    const longitude = document.getElementById('longitude').value;
                    const latitude = document.getElementById('latitude').value;
                    const loadingEl = document.getElementById('loading');
                    const resultEl = document.getElementById('result');
                    
                    loadingEl.style.display = 'inline';
                    resultEl.textContent = '查询中...';
                    
                    fetch(`/api/soil-texture?longitude=${longitude}&latitude=${latitude}`)
                        .then(response => response.json())
                        .then(data => {
                            resultEl.textContent = JSON.stringify(data, null, 2);
                            loadingEl.style.display = 'none';
                        })
                        .catch(error => {
                            resultEl.textContent = '查询出错: ' + error;
                            loadingEl.style.display = 'none';
                        });
                });
            </script>
        </div>
    </body>
    </html>
    '''

def query_soil_property(longitude, latitude, service_id, depth="0-5cm", stat="mean"):
    west = longitude - 0.01
    east = longitude + 0.01
    south = latitude - 0.01
    north = latitude + 0.01
    
    coverage_id = f"{service_id}_{depth}_{stat}"
    
    with tempfile.NamedTemporaryFile(suffix='.tif', delete=False) as temp:
        temp_filename = temp.name
    
    try:
        sg = SoilGrids()
        data = sg.get_coverage_data(
            service_id=service_id,
            coverage_id=coverage_id,
            west=west,
            south=south,
            east=east,
            north=north,
            crs="urn:ogc:def:crs:EPSG::4326",
            width=10,  
            height=10,
            output=temp_filename,
        )
        
        ds = rioxarray.open_rasterio(temp_filename)
        value = ds.sel(x=longitude, y=latitude, method='nearest').values[0]  # 获取第一个值
        
        unit = sg.metadata.get("units", "未知单位")
        
        return service_id, depth, value, unit
    except Exception as e:
        print(f"查询{coverage_id}时出错: {str(e)}")
        return service_id, depth, None, None
    finally:
        try:
            if os.path.exists(temp_filename):
                os.remove(temp_filename)
        except:
            pass

def query_worker(args):
    longitude, latitude, prop_id, depth = args
    return query_soil_property(longitude, latitude, prop_id, depth)

def get_soil_texture(longitude, latitude):
    """
    查询特定经纬度位置的土壤质地组成及占比
    
    参数:
    longitude: 经度
    latitude: 纬度
    
    返回:
    dict: 包含不同深度土壤质地组成及占比的字典
    """
    texture_properties = [
        {"id": "clay", "name": "粘土含量"},
        {"id": "sand", "name": "砂粒含量"},
        {"id": "silt", "name": "粉粒含量"}
    ]
    
    depths = ["0-5cm", "5-15cm", "15-30cm", "30-60cm"]
    
    texture_data = {}
    for prop in texture_properties:
        texture_data[prop["id"]] = {"name": prop["name"], "values": {}}
    
    tasks = []
    for prop in texture_properties:
        for depth in depths:
            tasks.append((longitude, latitude, prop["id"], depth))
    
    start_time = time.time()
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        results = list(executor.map(query_worker, tasks))
    
    for service_id, depth, value, unit in results:
        if value is not None:
            texture_data[service_id]["values"][depth] = value
            texture_data[service_id]["unit"] = unit
    
    response_data = []
    
    for depth in depths:
        clay_value = texture_data.get("clay", {}).get("values", {}).get(depth)
        sand_value = texture_data.get("sand", {}).get("values", {}).get(depth)
        silt_value = texture_data.get("silt", {}).get("values", {}).get(depth)
        
        if clay_value is not None and sand_value is not None and silt_value is not None:
            total = clay_value + sand_value + silt_value
            if total > 0:
                clay_pct = clay_value / total * 100
                sand_pct = sand_value / total * 100
                silt_pct = silt_value / total * 100
                
                response_data.append({
                    "depth": depth,
                    "clay_content": float(clay_value),
                    "sand_content": float(sand_value),
                    "silt_content": float(silt_value),
                    "total": float(total),
                    "clay_percent": round(float(clay_pct), 2),
                    "sand_percent": round(float(sand_pct), 2),
                    "silt_percent": round(float(silt_pct), 2)
                })
    
    return response_data

@app.route('/api/soil-texture', methods=['GET'])
def soil_texture_api():
    """土壤质地查询API端点"""
    try:
        longitude = float(request.args.get('longitude'))
        latitude = float(request.args.get('latitude'))
        
        if longitude < -180 or longitude > 180 or latitude < -90 or latitude > 90:
            return jsonify({"error": "经纬度参数无效，经度范围-180到180，纬度范围-90到90"}), 400
        
        result = get_soil_texture(longitude, latitude)
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({"error": f"查询出错: {str(e)}"}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    
    print(f"启动土壤质地Web API服务,访问 http://localhost:{port}/")
    app.run(host='0.0.0.0', port=port, debug=True) 