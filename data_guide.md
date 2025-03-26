# SoilGrids 数据指南

SoilGrids提供全球范围内的土壤特性数据集。以下是主要的土壤特性参数：

## 主要数据类型 (service_id)

1. **bdod** - 容重 (Bulk density)
   - 单位: kg/dm³
   - 描述: 表示单位体积的干土重量，与土壤紧实度和孔隙度相关

2. **cec** - 阳离子交换量 (Cation Exchange Capacity)
   - 单位: cmol(c)/kg
   - 描述: 土壤保持和交换阳离子的能力，与肥力密切相关

3. **cfvo** - 粗碎片体积 (Coarse fragments volumetric)
   - 单位: cm3/dm3 (体积百分比)
   - 描述: 土壤中直径大于2mm的颗粒所占的体积比例

4. **clay** - 粘土含量 (Clay content)
   - 单位: g/kg (重量百分比)
   - 描述: 土壤中粘土颗粒(直径<0.002mm)的含量

5. **nitrogen** - 总氮 (Total nitrogen)
   - 单位: g/kg
   - 描述: 土壤中总氮含量，是重要的植物营养元素

6. **phh2o** - pH值 (pH in H2O)
   - 单位: pH
   - 描述: 土壤pH值，影响养分有效性和生物活动

7. **sand** - 砂粒含量 (Sand content)
   - 单位: g/kg (重量百分比)
   - 描述: 土壤中砂粒(直径0.05-2mm)的含量

8. **silt** - 粉粒含量 (Silt content)
   - 单位: g/kg (重量百分比)
   - 描述: 土壤中粉粒(直径0.002-0.05mm)的含量

9. **soc** - 土壤有机碳 (Soil organic carbon)
   - 单位: g/kg
   - 描述: 土壤中有机碳含量，与土壤肥力和健康度相关

10. **ocd** - 有机碳密度 (Organic carbon density)
    - 单位: kg/m³
    - 描述: 单位体积土壤中有机碳的质量

11. **ocs** - 有机碳储量 (Organic carbon stocks)
    - 单位: t/ha
    - 描述: 单位面积土壤下有机碳的总量

## 覆盖范围类型 (coverage_id)

每种土壤特性有多个不同深度的数据层，例如:

- `phh2o_0-5cm_mean`: 0-5厘米深度的平均pH值
- `phh2o_5-15cm_mean`: 5-15厘米深度的平均pH值
- `phh2o_15-30cm_mean`: 15-30厘米深度的平均pH值
- `phh2o_30-60cm_mean`: 30-60厘米深度的平均pH值
- `phh2o_60-100cm_mean`: 60-100厘米深度的平均pH值
- `phh2o_100-200cm_mean`: 100-200厘米深度的平均pH值

每个深度层次还包括三种统计指标:
- `mean`: 平均值
- `Q0.05`: 5%分位数 (置信区间下限)
- `Q0.95`: 95%分位数 (置信区间上限)

## 数据应用

这些土壤数据可用于:
1. 农业规划与管理
2. 环境监测与保护
3. 土地适宜性评价
4. 气候变化研究
5. 水资源管理
6. 生态系统服务评估 