"""
基于Flask实现的HTTP API,用于查询任意经纬度位置的土壤质地组成和水力特性(数据源基于SoilGrid250m)
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
import sys

# 添加当前目录到Python路径，确保可以导入soil_moisture_model
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

from soil_moisture_model import run_soil_moisture_models


app = Flask(__name__)
CORS(app)  

@app.route('/')
def index():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>土壤质地与水力特性查询API</title>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; line-height: 1.6; }
            .container { max-width: 800px; margin: 0 auto; }
            h1, h2, h3 { color: #336699; }
            input, button, select { padding: 8px; margin: 5px 0; }
            button { background-color: #4CAF50; color: white; border: none; cursor: pointer; }
            button:hover { background-color: #45a049; }
            pre { background-color: #f5f5f5; padding: 10px; border-radius: 5px; overflow-x: auto; }
            .loading { display: none; color: #666; }
            .section { margin-bottom: 30px; border-bottom: 1px solid #eee; padding-bottom: 20px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>土壤质地与水力特性查询API</h1>
            
            <div class="section">
                <h2>土壤质地查询</h2>
                <p>输入经纬度查询特定位置的土壤质地组成及占比</p>
                
                <div>
                    <label for="longitude">经度:</label>
                    <input type="number" id="longitude" step="0.0001" value="115.0" />
                    
                    <label for="latitude">纬度:</label>
                    <input type="number" id="latitude" step="0.0001" value="30.5" />
                    
                    <button id="queryBtn">查询质地</button>
                    <span id="loading" class="loading">查询中，请稍候...</span>
                </div>
                
                <h3>质地结果</h3>
                <pre id="result">请输入经纬度后点击查询按钮</pre>
            </div>
            
            <div class="section">
                <h2>土壤水力特性查询</h2>
                <p>输入经纬度查询特定位置的土壤水力特性</p>
                
                <div>
                    <label for="hydraulic-longitude">经度:</label>
                    <input type="number" id="hydraulic-longitude" step="0.0001" value="115.0" />
                    
                    <label for="hydraulic-latitude">纬度:</label>
                    <input type="number" id="hydraulic-latitude" step="0.0001" value="30.5" />
                    
                    <label for="hydraulic-depth">深度:</label>
                    <select id="hydraulic-depth">
                        <option value="0-5cm">0-5cm</option>
                        <option value="5-15cm">5-15cm</option>
                        <option value="15-30cm">15-30cm</option>
                        <option value="30-60cm">30-60cm</option>
                    </select>
                    
                    <button id="hydraulicBtn">查询水力特性</button>
                    <span id="hydraulic-loading" class="loading">查询中，请稍候...</span>
                </div>
                
                <h3>水力特性结果</h3>
                <pre id="hydraulic-result">请输入经纬度后点击查询按钮</pre>
            </div>
            
            <h2>API使用说明</h2>
            <div class="section">
                <h3>土壤质地API</h3>
                <p>API端点: <code>/api/soil-texture</code></p>
                <p>查询参数:</p>
                <ul>
                    <li><code>longitude</code>: 经度 (必需)</li>
                    <li><code>latitude</code>: 纬度 (必需)</li>
                </ul>
                <p>示例请求: <code>/api/soil-texture?longitude=115.0&latitude=30.5</code></p>
            </div>
            
            <div class="section">
                <h3>土壤水力特性API</h3>
                <p>API端点: <code>/api/soil-hydraulics</code></p>
                <p>查询参数:</p>
                <ul>
                    <li><code>longitude</code>: 经度 (必需)</li>
                    <li><code>latitude</code>: 纬度 (必需)</li>
                    <li><code>depth</code>: 土壤深度 (可选, 默认为"0-5cm")</li>
                </ul>
                <p>示例请求: <code>/api/soil-hydraulics?longitude=115.0&latitude=30.5&depth=0-5cm</code></p>
            </div>
            
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
                
                document.getElementById('hydraulicBtn').addEventListener('click', function() {
                    const longitude = document.getElementById('hydraulic-longitude').value;
                    const latitude = document.getElementById('hydraulic-latitude').value;
                    const depth = document.getElementById('hydraulic-depth').value;
                    const loadingEl = document.getElementById('hydraulic-loading');
                    const resultEl = document.getElementById('hydraulic-result');
                    
                    loadingEl.style.display = 'inline';
                    resultEl.textContent = '查询中...';
                    
                    fetch(`/api/soil-hydraulics?longitude=${longitude}&latitude=${latitude}&depth=${depth}`)
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
    """
    查询特定经纬度位置的单个土壤属性数据
    """
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
    """并行查询的工作函数"""
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

# 以下是新增的水力特性相关函数

def load_soil_data(filename='soil_data.json'):
    """加载土壤数据库"""
    # 尝试多个可能的路径
    module_dir = os.path.dirname(os.path.abspath(__file__))
    possible_paths = [
        os.path.join(module_dir, 'soil_moisture_model', filename),
        os.path.join(module_dir, filename)
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            with open(path, 'r') as file:
                return json.load(file)
    
    raise FileNotFoundError(f"找不到 {filename}，已尝试路径: {possible_paths}")

def find_closest_soil_code(input_clay, input_silt, soil_data):
    """查找最接近的土壤代码"""
    closest_code = None
    min_diff = float('inf')
    input_sand = 100 - input_clay - input_silt  
    
    for code, fractions in soil_data.items():
        clay_diff = abs(fractions['clay'] - input_clay)
        silt_diff = abs(fractions['silt'] - input_silt)
        sand_diff = abs(fractions['sand'] - input_sand)
        total_diff = clay_diff + silt_diff + sand_diff
        
        if total_diff < min_diff:
            min_diff = total_diff
            closest_code = code
    
    return closest_code

def format_code(code):
    """格式化土壤代码为4位字符串"""
    if not isinstance(code, str):
        code = str(code)
    
    if len(code) != 4:
        code = (code[:4] if len(code) > 4 else code.zfill(4))
        
    return code

def extract_hydraulic_properties(output_data):
    """从模型输出中提取水力特性参数"""
    properties = {}
    
    # 遍历所有模型输出
    for model_name, model_data in output_data.items():
        if not model_data or not isinstance(model_data, dict) or 'output' not in model_data:
            continue
            
        output = model_data['output']
        lines = output.splitlines() if output else []
        
        for line in lines:
            # 提取饱和含水量 (qs)
            if 'qs =' in line:
                try:
                    parts = line.split('qs =')
                    if len(parts) > 1:
                        value = float(parts[1].split()[0])
                        properties['saturated_water_content'] = value
                except:
                    pass
                    
            # 提取田间持水量
            if '33KPa' in line:
                try:
                    value = float(line.split()[-1])
                    properties['field_capacity'] = value
                except:
                    pass
                    
            # 提取萎蔫点
            if '15000KPa' in line:
                try:
                    value = float(line.split()[-1])
                    properties['wilting_point'] = value
                except:
                    pass
                    
            # 提取饱和导水率 (Ks)
            if 'Ks =' in line:
                try:
                    ks_str = line.split('Ks =')[1].split()[0]
                    if 'e+' in ks_str:
                        base, exp = ks_str.split('e+')
                        properties['Ks'] = float(base) * (10 ** int(exp))
                    else:
                        properties['Ks'] = float(ks_str)
                except:
                    pass
                    
            # 提取van Genuchten参数 (alpha)
            if 'a =' in line:
                try:
                    alpha_str = line.split('a =')[1].split()[0]
                    properties['alpha'] = float(alpha_str)
                except:
                    pass
                    
            # 提取van Genuchten参数 (n)
            if 'n =' in line or 'Therefore n =' in line:
                try:
                    if 'n =' in line:
                        n_str = line.split('n =')[1].split()[0]
                    else:
                        n_str = line.split('Therefore n =')[1].split()[0]
                    properties['n'] = float(n_str)
                except:
                    pass
    
    # 计算可利用水分量
    if 'field_capacity' in properties and 'wilting_point' in properties:
        properties['available_water'] = round(
            properties['field_capacity'] - properties['wilting_point'], 3)
    
    return properties

def get_soil_hydraulics(longitude, latitude, depth="0-5cm"):
    """
    查询特定经纬度位置的土壤水力特性
    
    参数:
    longitude: 经度
    latitude: 纬度
    depth: 土壤深度层
    
    返回:
    dict: 包含土壤水力特性的字典
    """
    # 1. 获取土壤质地数据
    texture_data = get_soil_texture(longitude, latitude)
    
    # 2. 查找指定深度的数据
    target_data = None
    for item in texture_data:
        if item["depth"] == depth:
            target_data = item
            break
    
    if not target_data:
        return {"error": f"未找到深度为{depth}的土壤数据"}
    
    # 3. 提取粘土和粉粒百分比
    clay_percent = target_data["clay_percent"]
    silt_percent = target_data["silt_percent"]
    
    # 4. 加载土壤数据
    try:
        soil_data = load_soil_data()
    except Exception as e:
        return {"error": f"加载土壤数据失败: {str(e)}"}
    
    # 5. 查找最接近的土壤代码
    closest_code = find_closest_soil_code(clay_percent, silt_percent, soil_data)
    closest_code = format_code(closest_code)
    
    # 6. 运行土壤水分模型并捕获所有输出
    try:
        # 记录开始运行模型的时间
        model_start_time = time.time()
        print(f"开始运行土壤水分模型，土壤代码: {closest_code}")
        
        # 运行模型并获取原始结果
        hydraulic_properties = run_soil_moisture_models(closest_code)
        
        # 记录模型运行时间
        model_run_time = time.time() - model_start_time
        print(f"模型运行完成，耗时: {model_run_time:.2f}秒")
        
        # 如果模型返回None或空值，抛出异常
        if hydraulic_properties is None:
            raise ValueError("模型返回了空值 (None)")
        
        # 7. 构建响应数据
        response = {
            "位置信息": {
                "经度": longitude,
                "纬度": latitude,
                "深度": depth
            },
            "土壤质地": {
                "粘土百分比": clay_percent,
                "粉粒百分比": silt_percent,
                "砂粒百分比": target_data["sand_percent"]
            },
            "土壤代码": closest_code,
            "水力特性": hydraulic_properties
        }
        
        # 同时提供英文版本的数据，确保API的通用性
        response_en = {
            "location": {
                "longitude": longitude,
                "latitude": latitude,
                "depth": depth
            },
            "soil_texture": {
                "clay_percent": clay_percent,
                "silt_percent": silt_percent,
                "sand_percent": target_data["sand_percent"]
            },
            "soil_code": closest_code,
            "hydraulic_properties": {
                "field_capacity": hydraulic_properties.get("田间持水量"),
                "wilting_point": hydraulic_properties.get("萎蔫点"),
                "saturated_water_content": hydraulic_properties.get("饱和含水量"),
                "Ks": hydraulic_properties.get("饱和导水率(cm/day)"),
                "alpha": hydraulic_properties.get("范根参数alpha"),
                "n": hydraulic_properties.get("范根参数n"),
                "available_water": hydraulic_properties.get("有效水分量"),
                "model_results": {}
            }
        }
        
        # 添加各个模型结果到英文数据
        if "各模型结果" in hydraulic_properties:
            for model_name, model_data in hydraulic_properties["各模型结果"].items():
                response_en["hydraulic_properties"]["model_results"][model_name] = {
                    "field_capacity": model_data.get("田间持水量"),
                    "wilting_point": model_data.get("萎蔫点"),
                    "saturated_water_content": model_data.get("饱和含水量"),
                    "Ks": model_data.get("饱和导水率(cm/day)"),
                    "alpha": model_data.get("范根参数alpha"),
                    "n": model_data.get("范根参数n"),
                    "available_water": model_data.get("有效水分量")
                }
        
        # 合并两个响应
        final_response = {
            "中文数据": response,
            "英文数据": response_en
        }
        
        return final_response
    except Exception as e:
        error_msg = f"运行土壤水分模型失败: {str(e)}"
        print(error_msg)
        import traceback
        traceback.print_exc()
        
        # 返回带有详细错误信息的响应
        return {
            "错误": error_msg,
            "位置信息": {
                "经度": longitude,
                "纬度": latitude,
                "深度": depth
            },
            "土壤质地": {
                "粘土百分比": clay_percent,
                "粉粒百分比": silt_percent,
                "砂粒百分比": target_data["sand_percent"]
            },
            "土壤代码": closest_code,
            "水力特性": None
        }

@app.route('/api/soil-hydraulics', methods=['GET'])
def soil_hydraulics_api():
    """土壤水力特性查询API端点"""
    try:
        # 获取查询参数
        longitude = float(request.args.get('longitude'))
        latitude = float(request.args.get('latitude'))
        depth = request.args.get('depth', "0-5cm")  # 默认为0-5cm深度
        
        # 检查参数有效性
        if longitude < -180 or longitude > 180 or latitude < -90 or latitude > 90:
            return jsonify({"error": "经纬度参数无效，经度范围-180到180，纬度范围-90到90"}), 400
        
        # 执行查询
        result = get_soil_hydraulics(longitude, latitude, depth)
        
        # 返回结果
        return jsonify(result)
    
    except Exception as e:
        return jsonify({"error": f"查询出错: {str(e)}"}), 500

if __name__ == '__main__':
    # 确保在正确的目录启动
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    port = int(os.environ.get("PORT", 5000))
    print(f"启动土壤质地与水力特性Web API服务，访问 http://localhost:{port}/")
    app.run(host='0.0.0.0', port=port, debug=True)