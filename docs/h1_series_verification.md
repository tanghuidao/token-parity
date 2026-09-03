# H1 品类 seriesID 核验报告

- 核验时间：2026-09-03T02:58:12Z
- 数据源：BLS v2 API（`https://api.bls.gov/publicAPI/v2/timeseries/data/`，`catalog=true`，口径 CUUR0000 全国 CPI-U 未季调）
- 核验对象：category_mapping.csv 中「待核实」的 137 个 seriesID
- 结论：✅ 通过 137 项 / ⚠️ 未通过 0 项

## 一、未通过核验（需人工复核，seriesID 在 BLS 目录中不存在）

（无）

## 二、通过核验（已转正为「已核实」，并回填起始年份）

| series_id | 中文品类名 | 官方 series_title | H1分组 | 起始年份 |
|---|---|---|---|---|
| `CUUR0000SAH` | 住房（整体） | Housing in U.S. city average, all urban consumers, not seasonally adjusted | 排除 |  |
| `CUUR0000SAM` | 医疗保健（整体） | Medical care in U.S. city average, all urban consumers, not seasonally adjusted | 排除 |  |
| `CUUR0000SAR` | 娱乐（整体） | Recreation in U.S. city average, all urban consumers, not seasonally adjusted | 排除 |  |
| `CUUR0000SAA` | 服装（整体） | Apparel in U.S. city average, all urban consumers, not seasonally adjusted | 排除 |  |
| `CUUR0000SAT` | 交通（整体） | Transportation in U.S. city average, all urban consumers, not seasonally adjusted | 排除 |  |
| `CUUR0000SAE` | 教育与通信（整体） | Education and communication in U.S. city average, all urban consumers, not seasonally adjusted | 排除 |  |
| `CUUR0000SAG` | 其他商品与服务（整体） | Other goods and services in U.S. city average, all urban consumers, not seasonally adjusted | 排除 |  |
| `CUUR0000SA0E` | 能源 | Energy in U.S. city average, all urban consumers, not seasonally adjusted | 排除 |  |
| `CUUR0000SA0L1` | 总指数（除食品） | All items less food in U.S. city average, all urban consumers, not seasonally adjusted | 排除 |  |
| `CUUR0000SA0L12` | 总指数（除食品与住房） | All items less food and shelter in U.S. city average, all urban consumers, not seasonally adjusted | 排除 |  |
| `CUUR0000SA0L12E` | 总指数（除食品住房能源） | All items less food, shelter, and energy in U.S. city average, all urban consumers, not seasonally adjusted | 排除 |  |
| `CUUR0000SA0L12E4` | 总指数（除食品住房能源二手车） | All items less food, shelter, energy, and used cars and trucks in U.S. city average, all urban consumers, not seasonally adjusted | 排除 |  |
| `CUUR0000SA0L1E` | 总指数（除食品与能源） | All items less food and energy in U.S. city average, all urban consumers, not seasonally adjusted | 排除 |  |
| `CUUR0000SA0L2` | 总指数（除住房） | All items less shelter in U.S. city average, all urban consumers, not seasonally adjusted | 排除 |  |
| `CUUR0000SA0L5` | 总指数（除医疗） | All items  less medical care in U.S. city average, all urban consumers, not seasonally adjusted | 排除 |  |
| `CUUR0000SA0LE` | 总指数（除能源） | All items less energy in U.S. city average, all urban consumers, not seasonally adjusted | 排除 |  |
| `CUUR0000SA311` | 服装（除鞋类） | Apparel less footwear in U.S. city average, all urban consumers, not seasonally adjusted | 排除 |  |
| `CUUR0000SAA1` | 男装及童男装 | Men's and boys' apparel in U.S. city average, all urban consumers, not seasonally adjusted | 排除 |  |
| `CUUR0000SAA2` | 女装及童女装 | Women's and girls' apparel in U.S. city average, all urban consumers, not seasonally adjusted | 排除 |  |
| `CUUR0000SAC` | 商品（整体） | Commodities in U.S. city average, all urban consumers, not seasonally adjusted | 排除 |  |
| `CUUR0000SACE` | 能源商品 | Energy commodities in U.S. city average, all urban consumers, not seasonally adjusted | 排除 |  |
| `CUUR0000SACL1` | 商品（除食品） | Commodities less food in U.S. city average, all urban consumers, not seasonally adjusted | 排除 |  |
| `CUUR0000SACL11` | 商品（除食品饮料） | Commodities less food and beverages in U.S. city average, all urban consumers, not seasonally adjusted | 排除 |  |
| `CUUR0000SACL1E` | 商品（除食品能源） | Commodities less food and energy commodities in U.S. city average, all urban consumers, not seasonally adjusted | 排除 |  |
| `CUUR0000SACL1E4` | 商品（除食品能源二手车） | Commodities less food, energy, and used cars and trucks in U.S. city average, all urban consumers, not seasonally adjusted | 排除 |  |
| `CUUR0000SAD` | 耐用消费品 | Durables in U.S. city average, all urban consumers, not seasonally adjusted | 排除 |  |
| `CUUR0000SAE1` | 教育 | Education in U.S. city average, all urban consumers, not seasonally adjusted | 排除 |  |
| `CUUR0000SAE2` | 通信 | Communication in U.S. city average, all urban consumers, not seasonally adjusted | 排除 |  |
| `CUUR0000SAEC` | 教育与通信商品 | Education and communication commodities in U.S. city average, all urban consumers, not seasonally adjusted | 排除 |  |
| `CUUR0000SAES` | 教育与通信服务 | Education and communication services in U.S. city average, all urban consumers, not seasonally adjusted | 排除 |  |
| `CUUR0000SAF1` | 食品 | Food in U.S. city average, all urban consumers, not seasonally adjusted | 排除 |  |
| `CUUR0000SAG1` | 个人护理 | Personal care in U.S. city average, all urban consumers, not seasonally adjusted | 排除 |  |
| `CUUR0000SAGC` | 其他商品 | Other goods in U.S. city average, all urban consumers, not seasonally adjusted | 排除 |  |
| `CUUR0000SAGS` | 其他个人服务 | Other personal services in U.S. city average, all urban consumers, not seasonally adjusted | 排除 |  |
| `CUUR0000SAH1` | 住所 Shelter | Shelter in U.S. city average, all urban consumers, not seasonally adjusted | 排除 |  |
| `CUUR0000SAH2` | 燃料与公用事业 | Fuels and utilities in U.S. city average, all urban consumers, not seasonally adjusted | 排除 |  |
| `CUUR0000SAH3` | 家居陈设与运营 | Household furnishings and operations in U.S. city average, all urban consumers, not seasonally adjusted | 排除 |  |
| `CUUR0000SAH31` | 家居陈设与用品 | Household furnishings and supplies in U.S. city average, all urban consumers, not seasonally adjusted | 排除 |  |
| `CUUR0000SAM1` | 医疗保健商品 | Medical care commodities in U.S. city average, all urban consumers, not seasonally adjusted | 排除 |  |
| `CUUR0000SAN` | 非耐用消费品 | Nondurables in U.S. city average, all urban consumers, not seasonally adjusted | 排除 |  |
| `CUUR0000SAN1D` | 国产农产食品 | Domestically produced farm food in U.S. city average, all urban consumers, not seasonally adjusted | 排除 |  |
| `CUUR0000SANL1` | 非耐用消费品（除食品） | Nondurables less food in U.S. city average, all urban consumers, not seasonally adjusted | 排除 |  |
| `CUUR0000SANL11` | 非耐用消费品（除食品饮料） | Nondurables less food and beverages in U.S. city average, all urban consumers, not seasonally adjusted | 排除 |  |
| `CUUR0000SANL113` | 非耐用消费品（除食品饮料服装） | Nondurables less food, beverages, and apparel in U.S. city average, all urban consumers, not seasonally adjusted | 排除 |  |
| `CUUR0000SANL13` | 非耐用消费品（除食品服装） | Nondurables less food and apparel in U.S. city average, all urban consumers, not seasonally adjusted | 排除 |  |
| `CUUR0000SARC` | 娱乐商品 | Recreation commodities in U.S. city average, all urban consumers, not seasonally adjusted | 排除 |  |
| `CUUR0000SARS` | 娱乐服务 | Recreation services in U.S. city average, all urban consumers, not seasonally adjusted | 排除 |  |
| `CUUR0000SAS` | 服务（整体） | Services in U.S. city average, all urban consumers, not seasonally adjusted | 排除 |  |
| `CUUR0000SAS24` | 公用事业与公共交通 | Utilities and public transportation in U.S. city average, all urban consumers, not seasonally adjusted | 排除 |  |
| `CUUR0000SAS2RS` | 住房租金（rent of shelter） | Rent of shelter in U.S. city average, all urban consumers, not seasonally adjusted | 排除 |  |
| `CUUR0000SAS367` | 其他服务 | Other services in U.S. city average, all urban consumers, not seasonally adjusted | 排除 |  |
| `CUUR0000SAS4` | 交通服务 | Transportation services in U.S. city average, all urban consumers, not seasonally adjusted | 排除 |  |
| `CUUR0000SASL2RS` | 服务（除住房租金） | Services less rent of shelter in U.S. city average, all urban consumers, not seasonally adjusted | 排除 |  |
| `CUUR0000SASL5` | 服务（除医疗服务） | Services less medical care services in U.S. city average, all urban consumers, not seasonally adjusted | 排除 |  |
| `CUUR0000SASLE` | 服务（除能源服务） | Services less energy services in U.S. city average, all urban consumers, not seasonally adjusted | 排除 |  |
| `CUUR0000SAT1` | 私人交通 | Private transportation in U.S. city average, all urban consumers, not seasonally adjusted | 排除 |  |
| `CUUR0000SATCLTB` | 交通商品（除汽车燃油） | Transportation commodities less motor fuel in U.S. city average, all urban consumers, not seasonally adjusted | 排除 |  |
| `CUUR0000SEAE` | 鞋类 | Footwear in U.S. city average, all urban consumers, not seasonally adjusted | 排除 |  |
| `CUUR0000SEAF` | 婴幼儿服装 | Infants' and toddlers' apparel in U.S. city average, all urban consumers, not seasonally adjusted | R |  |
| `CUUR0000SEAG` | 珠宝与手表 | Jewelry and watches in U.S. city average, all urban consumers, not seasonally adjusted | 排除 |  |
| `CUUR0000SEEEC` | 信息技术商品 | Information technology commodities in U.S. city average, all urban consumers, not seasonally adjusted | 排除 |  |
| `CUUR0000SEGA` | 烟草及吸烟用品 | Tobacco and smoking products in U.S. city average, all urban consumers, not seasonally adjusted | 中性 |  |
| `CUUR0000SERA` | 影音（整体） | Video and audio in U.S. city average, all urban consumers, not seasonally adjusted | 排除 |  |
| `CUUR0000SERAC` | 影音产品 | Video and audio products in U.S. city average, all urban consumers, not seasonally adjusted | 排除 |  |
| `CUUR0000SERAS` | 影音服务 | Video and audio services in U.S. city average, all urban consumers, not seasonally adjusted | 排除 |  |
| `CUUR0000SERB` | 宠物及相关（整体） | Pets, pet products and services in U.S. city average, all urban consumers, not seasonally adjusted | 排除 |  |
| `CUUR0000SERC` | 体育用品（整体） | Sporting goods in U.S. city average, all urban consumers, not seasonally adjusted | 排除 |  |
| `CUUR0000SERD` | 摄影（整体） | Photography in U.S. city average, all urban consumers, not seasonally adjusted | 排除 |  |
| `CUUR0000SERE` | 其他娱乐商品（整体） | Other recreational goods in U.S. city average, all urban consumers, not seasonally adjusted | 排除 |  |
| `CUUR0000SERF` | 其他娱乐服务（整体） | Other recreation services in U.S. city average, all urban consumers, not seasonally adjusted | 排除 |  |
| `CUUR0000SERG` | 娱乐读物（整体） | Recreational reading materials in U.S. city average, all urban consumers, not seasonally adjusted | 排除 |  |
| `CUUR0000SETG` | 公共交通 | Public transportation in U.S. city average, all urban consumers, not seasonally adjusted | 排除 |  |
| `CUUR0000SAE21` | 信息与信息处理 | Information and information processing in U.S. city average, all urban consumers, not seasonally adjusted | 排除 |  |
| `CUUR0000SAF11` | 居家食品 | Food at home in U.S. city average, all urban consumers, not seasonally adjusted | 排除 |  |
| `CUUR0000SAF116` | 酒精饮料 | Alcoholic beverages in U.S. city average, all urban consumers, not seasonally adjusted | 中性 |  |
| `CUUR0000SAH21` | 家庭能源 | Household energy in U.S. city average, all urban consumers, not seasonally adjusted | 排除 |  |
| `CUUR0000SEAA` | 男装 | Men's apparel in U.S. city average, all urban consumers, not seasonally adjusted | R |  |
| `CUUR0000SEAB` | 童男装 | Boys' apparel in U.S. city average, all urban consumers, not seasonally adjusted | R |  |
| `CUUR0000SEAC` | 女装 | Women's apparel in U.S. city average, all urban consumers, not seasonally adjusted | R |  |
| `CUUR0000SEAD` | 童女装 | Girls' apparel in U.S. city average, all urban consumers, not seasonally adjusted | R |  |
| `CUUR0000SEAE01` | 男鞋 | Men's footwear in U.S. city average, all urban consumers, not seasonally adjusted | R |  |
| `CUUR0000SEAE02` | 童鞋 | Boys' and girls' footwear in U.S. city average, all urban consumers, not seasonally adjusted | R |  |
| `CUUR0000SEAE03` | 女鞋 | Women's footwear in U.S. city average, all urban consumers, not seasonally adjusted | R |  |
| `CUUR0000SEAG01` | 手表 | Watches in U.S. city average, all urban consumers, not seasonally adjusted | 中性 |  |
| `CUUR0000SEAG02` | 珠宝 | Jewelry in U.S. city average, all urban consumers, not seasonally adjusted | 中性 |  |
| `CUUR0000SEEB` | 学费/其他学杂费/托儿 | Tuition, other school fees, and childcare in U.S. city average, all urban consumers, not seasonally adjusted | 排除 |  |
| `CUUR0000SEEC` | 邮政与快递服务 | Postage and delivery services in U.S. city average, all urban consumers, not seasonally adjusted | 排除 |  |
| `CUUR0000SEEE` | 信息技术硬件与服务 | Information technology, hardware and services in U.S. city average, all urban consumers, not seasonally adjusted | 排除 |  |
| `CUUR0000SEFV` | 外食 | Food away from home in U.S. city average, all urban consumers, not seasonally adjusted | 排除 |  |
| `CUUR0000SEGB` | 个人护理用品 | Personal care products in U.S. city average, all urban consumers, not seasonally adjusted | 中性 |  |
| `CUUR0000SEGC` | 个人护理服务 | Personal care services in U.S. city average, all urban consumers, not seasonally adjusted | N |  |
| `CUUR0000SEGD` | 杂项个人服务 | Miscellaneous personal services in U.S. city average, all urban consumers, not seasonally adjusted | N |  |
| `CUUR0000SEGE` | 杂项个人商品 | Miscellaneous personal goods in U.S. city average, all urban consumers, not seasonally adjusted | 中性 |  |
| `CUUR0000SEHA` | 主要住所租金 | Rent of primary residence in U.S. city average, all urban consumers, not seasonally adjusted | N |  |
| `CUUR0000SEHB` | 外出住宿 | Lodging away from home in U.S. city average, all urban consumers, not seasonally adjusted | 排除 |  |
| `CUUR0000SEHC` | 自有住房等价租金（整体） | Owners' equivalent rent of residences in U.S. city average, all urban consumers, not seasonally adjusted | 排除 |  |
| `CUUR0000SEHD` | 租户与家庭保险 | Tenants' and household insurance in U.S. city average, all urban consumers, not seasonally adjusted | N |  |
| `CUUR0000SEHG` | 水、排污与垃圾处理服务 | Water and sewer and trash collection services in U.S. city average, all urban consumers, not seasonally adjusted | 中性 |  |
| `CUUR0000SEHH` | 窗饰与地面覆盖物 | Window and floor coverings and other linens in U.S. city average, all urban consumers, not seasonally adjusted | R |  |
| `CUUR0000SEHJ` | 家具与寝具 | Furniture and bedding in U.S. city average, all urban consumers, not seasonally adjusted | R |  |
| `CUUR0000SEHK` | 家电 | Appliances in U.S. city average, all urban consumers, not seasonally adjusted | R |  |
| `CUUR0000SEHL` | 其他家用设备与陈设 | Other household equipment and furnishings in U.S. city average, all urban consumers, not seasonally adjusted | R |  |
| `CUUR0000SEHM` | 工具/五金/户外装备 | Tools, hardware, outdoor equipment and supplies in U.S. city average, all urban consumers, not seasonally adjusted | R |  |
| `CUUR0000SEHN` | 家居清洁用品 | Housekeeping supplies in U.S. city average, all urban consumers, not seasonally adjusted | 中性 |  |
| `CUUR0000SEHP` | 家庭运营服务 | Household operations in U.S. city average, all urban consumers, not seasonally adjusted | 排除 |  |
| `CUUR0000SEMC` | 专业医疗服务 | Professional services in U.S. city average, all urban consumers, not seasonally adjusted | 排除 |  |
| `CUUR0000SEMD` | 医院及相关服务 | Hospital and related services in U.S. city average, all urban consumers, not seasonally adjusted | 排除 |  |
| `CUUR0000SEME` | 健康保险 | Health insurance in U.S. city average, all urban consumers, not seasonally adjusted | 排除 |  |
| `CUUR0000SEMF` | 药品 | Medicinal drugs in U.S. city average, all urban consumers, not seasonally adjusted | 排除 |  |
| `CUUR0000SEMG` | 医疗设备与耗材 | Medical equipment and supplies in U.S. city average, all urban consumers, not seasonally adjusted | 中性 |  |
| `CUUR0000SERA02` | 有线/卫星/流媒体电视服务 | Cable, satellite, and live streaming television service in U.S. city average, all urban consumers, not seasonally adjusted | 中性 |  |
| `CUUR0000SERA03` | 其他视频设备 | Other video equipment in U.S. city average, all urban consumers, not seasonally adjusted | R |  |
| `CUUR0000SERA04` | 视频购买/订阅/租赁 | Purchase, subscription, and rental of video in U.S. city average, all urban consumers, not seasonally adjusted | R |  |
| `CUUR0000SERA05` | 音频设备 | Audio equipment in U.S. city average, all urban consumers, not seasonally adjusted | R |  |
| `CUUR0000SERA06` | 录制音乐与订阅 | Recorded music and music subscriptions in U.S. city average, all urban consumers, not seasonally adjusted | R |  |
| `CUUR0000SERB01` | 宠物及宠物用品 | Pets and pet products in U.S. city average, all urban consumers, not seasonally adjusted | 中性 |  |
| `CUUR0000SERB02` | 宠物服务（含兽医） | Pet services including veterinary in U.S. city average, all urban consumers, not seasonally adjusted | N |  |
| `CUUR0000SERC01` | 运动车辆（含自行车） | Sports vehicles including bicycles in U.S. city average, all urban consumers, not seasonally adjusted | R |  |
| `CUUR0000SERC02` | 运动装备 | Sports equipment in U.S. city average, all urban consumers, not seasonally adjusted | R |  |
| `CUUR0000SERD01` | 摄影器材 | Photographic equipment and supplies in U.S. city average, all urban consumers, not seasonally adjusted | R |  |
| `CUUR0000SERD02` | 摄影师与照片冲洗 | Photographers and photo processing in U.S. city average, all urban consumers, not seasonally adjusted | 中性 |  |
| `CUUR0000SERE02` | 缝纫机/布料/辅料 | Sewing machines, fabric and supplies in U.S. city average, all urban consumers, not seasonally adjusted | R |  |
| `CUUR0000SERE03` | 乐器及配件 | Music instruments and accessories in U.S. city average, all urban consumers, not seasonally adjusted | R |  |
| `CUUR0000SERF01` | 俱乐部会费/参与费 | Club membership for shopping clubs, fraternal, or other organizations, or participant sports fees in U.S. city average, all urban consumers, not seasonally adjusted | N |  |
| `CUUR0000SERF02` | 门票 | Admissions in U.S. city average, all urban consumers, not seasonally adjusted | N |  |
| `CUUR0000SERF03` | 课程与指导费 | Fees for lessons or instructions in U.S. city average, all urban consumers, not seasonally adjusted | N |  |
| `CUUR0000SERG01` | 报纸与杂志 | Newspapers and magazines in U.S. city average, all urban consumers, not seasonally adjusted | 中性 |  |
| `CUUR0000SERG02` | 娱乐书籍 | Recreational books in U.S. city average, all urban consumers, not seasonally adjusted | R |  |
| `CUUR0000SETA` | 新车与二手车 | New and used motor vehicles in U.S. city average, all urban consumers, not seasonally adjusted | 排除 |  |
| `CUUR0000SETB` | 汽车燃油 | Motor fuel in U.S. city average, all urban consumers, not seasonally adjusted | 排除 |  |
| `CUUR0000SETC` | 机动车零配件 | Motor vehicle parts and equipment in U.S. city average, all urban consumers, not seasonally adjusted | R |  |
| `CUUR0000SETD` | 机动车维修保养 | Motor vehicle maintenance and repair in U.S. city average, all urban consumers, not seasonally adjusted | N |  |
| `CUUR0000SETE` | 机动车保险 | Motor vehicle insurance in U.S. city average, all urban consumers, not seasonally adjusted | N |  |
| `CUUR0000SETF` | 机动车税费 | Motor vehicle fees in U.S. city average, all urban consumers, not seasonally adjusted | 中性 |  |
| `CUUR0000SETG01` | 机票 | Airline fares in U.S. city average, all urban consumers, not seasonally adjusted | 中性 |  |
| `CUUR0000SETG02` | 其他城际交通 | Other intercity transportation in U.S. city average, all urban consumers, not seasonally adjusted | N |  |
| `CUUR0000SETG03` | 市内交通 | Intracity transportation in U.S. city average, all urban consumers, not seasonally adjusted | 中性 |  |

## 三、老品类「已核实」sanity check（不动，仅复核存在性）

| series_id | 中文品类名 | 在 BLS 目录 | 官方起始年份 vs 映射起始年份 |
|---|---|---|---|
| `CUUR0000SEMD01` | 医院服务 | ✅ |  vs 1996 |
| `CUUR0000SEEB01` | 大学学费 | ✅ |  vs 1977 |
| `CUUR0000SAM2` | 医疗护理服务 | ✅ |  vs 1935 |
| `CUUR0000SEEB03` | 托儿照护 | ✅ |  vs 1990 |
| `CUUR0000SEHC01` | 住房（位置性） | ✅ |  vs 1982 |
| `CUUR0000SAF` | 食品饮料 | ✅ |  vs 1967 |
| `CUUR0000SEED03` | 手机通信服务 | ✅ |  vs 1997 |
| `CUUR0000SEEE02` | 电脑软件 | ✅ |  vs 1997 |
| `CUUR0000SERE01` | 玩具 | ✅ |  vs 1977 |
| `CUUR0000SERA01` | 电视机 | ✅ |  vs 1950 |
| `CUUR0000SA0` | CPI总指数 | ✅ |  vs 1913 |

