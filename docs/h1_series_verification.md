# H1 品类 seriesID 核验报告

- 核验时间：2026-09-03T04:22:51Z
- 数据源：BLS v2 API（`https://api.bls.gov/publicAPI/v2/timeseries/data/`，`catalog=true`，口径 CUUR0000 全国 CPI-U 未季调）
- 核验对象：category_mapping.csv 中「待核实」的 33 个 seriesID
- 结论：✅ 通过 33 项 / ⚠️ 未通过 0 项
- 说明：「数据起始年份」回填的是世纪窗口内最早观测年份（窗口起点 1998，BLS CPI 1998 细项目录重组）；≤1998 表示真实 begin_year ≤ 1998，BLS v2 API catalog 不提供真实 begin_year

## 一、未通过核验（需人工复核，seriesID 在 BLS 目录中不存在）

（无）

## 二、通过核验（已转正为「已核实」，并回填起始年份）

| series_id | 中文品类名 | 官方 series_title | H1分组 | 起始年份 |
|---|---|---|---|---|
| `CUUR0000SEGC01` | 理发及其他个人护理服务 | Haircuts and other personal care services in U.S. city average, all urban consumers, not seasonally adjusted | N | ≤1998 |
| `CUUR0000SEGD01` | 法律服务 | Legal services in U.S. city average, all urban consumers, not seasonally adjusted | N | ≤1998 |
| `CUUR0000SEGD02` | 殡葬服务 | Funeral expenses in U.S. city average, all urban consumers, not seasonally adjusted | N | ≤1998 |
| `CUUR0000SEGD03` | 洗衣与干洗服务 | Laundry and dry cleaning services in U.S. city average, all urban consumers, not seasonally adjusted | N | ≤1998 |
| `CUUR0000SEGD04` | 服装修补与其他服装服务 | Apparel services other than laundry and dry cleaning in U.S. city average, all urban consumers, not seasonally adjusted | N | ≤1998 |
| `CUUR0000SEGD05` | 金融服务 | Financial services in U.S. city average, all urban consumers, not seasonally adjusted | N | ≤1998 |
| `CUUR0000SETD01` | 机动车车身修理 | Motor vehicle body work in U.S. city average, all urban consumers, not seasonally adjusted | N | ≤1998 |
| `CUUR0000SETD02` | 机动车维护保养 | Motor vehicle maintenance and servicing in U.S. city average, all urban consumers, not seasonally adjusted | N | ≤1998 |
| `CUUR0000SETD03` | 机动车维修 | Motor vehicle repair in U.S. city average, all urban consumers, not seasonally adjusted | N | ≤1998 |
| `CUUR0000SEAA01` | 男西装与外套 | Men's suits, sport coats, and outerwear in U.S. city average, all urban consumers, not seasonally adjusted | R | ≤1998 |
| `CUUR0000SEAA02` | 男内衣/睡衣/泳装及配饰 | Men's underwear, nightwear, swimwear, and accessories in U.S. city average, all urban consumers, not seasonally adjusted | R | ≤1998 |
| `CUUR0000SEAA03` | 男衬衫与毛衣 | Men's shirts and sweaters in U.S. city average, all urban consumers, not seasonally adjusted | R | ≤1998 |
| `CUUR0000SEAA04` | 男裤与短裤 | Men's pants and shorts in U.S. city average, all urban consumers, not seasonally adjusted | R | ≤1998 |
| `CUUR0000SEAC01` | 女外套 | Women's outerwear in U.S. city average, all urban consumers, not seasonally adjusted | R | ≤1998 |
| `CUUR0000SEAC02` | 女连衣裙 | Women's dresses in U.S. city average, all urban consumers, not seasonally adjusted | R | ≤1998 |
| `CUUR0000SEAC03` | 女套装与单件 | Women's suits and separates in U.S. city average, all urban consumers, not seasonally adjusted | R | ≤1998 |
| `CUUR0000SEAC04` | 女内衣/睡衣/泳装及配饰 | Women's underwear, nightwear, swimwear, and accessories in U.S. city average, all urban consumers, not seasonally adjusted | R | ≤1998 |
| `CUUR0000SEHH01` | 地面覆盖物 | Floor coverings in U.S. city average, all urban consumers, not seasonally adjusted | R | ≤1998 |
| `CUUR0000SEHH02` | 窗帘与窗饰 | Window coverings in U.S. city average, all urban consumers, not seasonally adjusted | R | ≤1998 |
| `CUUR0000SEHH03` | 其他家纺布艺 | Other linens in U.S. city average, all urban consumers, not seasonally adjusted | R | ≤1998 |
| `CUUR0000SEHJ01` | 卧室家具 | Bedroom furniture in U.S. city average, all urban consumers, not seasonally adjusted | R | ≤1998 |
| `CUUR0000SEHJ02` | 客厅/厨房/餐厅家具 | Living room, kitchen, and dining room furniture in U.S. city average, all urban consumers, not seasonally adjusted | R | ≤1998 |
| `CUUR0000SEHJ03` | 其他家具 | Other furniture in U.S. city average, all urban consumers, not seasonally adjusted | R | ≤1998 |
| `CUUR0000SEHK01` | 大家电 | Major appliances in U.S. city average, all urban consumers, not seasonally adjusted | R | ≤1998 |
| `CUUR0000SEHK02` | 其他家电 | Other appliances in U.S. city average, all urban consumers, not seasonally adjusted | R | ≤1998 |
| `CUUR0000SEHL01` | 钟表灯具装饰品 | Clocks, lamps, and decorator items in U.S. city average, all urban consumers, not seasonally adjusted | R | ≤1998 |
| `CUUR0000SEHL03` | 餐具 | Dishes and flatware in U.S. city average, all urban consumers, not seasonally adjusted | R | ≤1998 |
| `CUUR0000SEHL04` | 非电炊具与餐具 | Nonelectric cookware and tableware in U.S. city average, all urban consumers, not seasonally adjusted | R | ≤1998 |
| `CUUR0000SEHM01` | 工具五金耗材 | Tools, hardware and supplies in U.S. city average, all urban consumers, not seasonally adjusted | R | ≤1998 |
| `CUUR0000SEHM02` | 户外装备与耗材 | Outdoor equipment and supplies in U.S. city average, all urban consumers, not seasonally adjusted | R | ≤1998 |
| `CUUR0000SETC01` | 轮胎 | Tires in U.S. city average, all urban consumers, not seasonally adjusted | R | ≤1998 |
| `CUUR0000SETC02` | 汽车配件（除轮胎） | Vehicle accessories other than tires in U.S. city average, all urban consumers, not seasonally adjusted | R | ≤1998 |
| `CUUR0000SEHL02` | 室内植物花卉 | Indoor plants and flowers in U.S. city average, all urban consumers, not seasonally adjusted | 中性 | ≤1998 |

## 三、老品类「已核实」sanity check（不动，仅复核存在性）

| series_id | 中文品类名 | 在 BLS 目录 | 窗口内最早年份 |
|---|---|---|---|
| `CUUR0000SEMD01` | 医院服务 | ✅ | ≤1998 |
| `CUUR0000SEEB01` | 大学学费 | ✅ | ≤1998 |
| `CUUR0000SAM2` | 医疗护理服务 | ✅ | ≤1998 |
| `CUUR0000SEEB03` | 托儿照护 | ✅ | ≤1998 |
| `CUUR0000SEHC01` | 住房（位置性） | ✅ | ≤1998 |
| `CUUR0000SAF` | 食品饮料 | ✅ | ≤1998 |
| `CUUR0000SEED03` | 手机通信服务 | ✅ | ≤1998 |
| `CUUR0000SEEE02` | 电脑软件 | ✅ | ≤1998 |
| `CUUR0000SERE01` | 玩具 | ✅ | ≤1998 |
| `CUUR0000SERA01` | 电视机 | ✅ | ≤1998 |
| `CUUR0000SA0` | CPI总指数 | ✅ | ≤1998 |
| `CUUR0000SAH` | 住房（整体） | ✅ | ≤1998 |
| `CUUR0000SAM` | 医疗保健（整体） | ✅ | ≤1998 |
| `CUUR0000SAR` | 娱乐（整体） | ✅ | ≤1998 |
| `CUUR0000SAA` | 服装（整体） | ✅ | ≤1998 |
| `CUUR0000SAT` | 交通（整体） | ✅ | ≤1998 |
| `CUUR0000SAE` | 教育与通信（整体） | ✅ | ≤1998 |
| `CUUR0000SAG` | 其他商品与服务（整体） | ✅ | ≤1998 |
| `CUUR0000SA0E` | 能源 | ✅ | ≤1998 |
| `CUUR0000SA0L1` | 总指数（除食品） | ✅ | ≤1998 |
| `CUUR0000SA0L12` | 总指数（除食品与住房） | ✅ | ≤1998 |
| `CUUR0000SA0L12E` | 总指数（除食品住房能源） | ✅ | ≤1998 |
| `CUUR0000SA0L12E4` | 总指数（除食品住房能源二手车） | ✅ | ≤1998 |
| `CUUR0000SA0L1E` | 总指数（除食品与能源） | ✅ | ≤1998 |
| `CUUR0000SA0L2` | 总指数（除住房） | ✅ | ≤1998 |
| `CUUR0000SA0L5` | 总指数（除医疗） | ✅ | ≤1998 |
| `CUUR0000SA0LE` | 总指数（除能源） | ✅ | ≤1998 |
| `CUUR0000SA311` | 服装（除鞋类） | ✅ | ≤1998 |
| `CUUR0000SAA1` | 男装及童男装 | ✅ | ≤1998 |
| `CUUR0000SAA2` | 女装及童女装 | ✅ | ≤1998 |
| `CUUR0000SAC` | 商品（整体） | ✅ | ≤1998 |
| `CUUR0000SACE` | 能源商品 | ✅ | ≤1998 |
| `CUUR0000SACL1` | 商品（除食品） | ✅ | ≤1998 |
| `CUUR0000SACL11` | 商品（除食品饮料） | ✅ | ≤1998 |
| `CUUR0000SACL1E` | 商品（除食品能源） | ✅ | ≤1998 |
| `CUUR0000SACL1E4` | 商品（除食品能源二手车） | ✅ | ≤1998 |
| `CUUR0000SAD` | 耐用消费品 | ✅ | ≤1998 |
| `CUUR0000SAE1` | 教育 | ✅ | ≤1998 |
| `CUUR0000SAE2` | 通信 | ✅ | ≤1998 |
| `CUUR0000SAEC` | 教育与通信商品 | ✅ | 2009 |
| `CUUR0000SAES` | 教育与通信服务 | ✅ | 2009 |
| `CUUR0000SAF1` | 食品 | ✅ | ≤1998 |
| `CUUR0000SAG1` | 个人护理 | ✅ | ≤1998 |
| `CUUR0000SAGC` | 其他商品 | ✅ | 2009 |
| `CUUR0000SAGS` | 其他个人服务 | ✅ | 2009 |
| `CUUR0000SAH1` | 住所 Shelter | ✅ | ≤1998 |
| `CUUR0000SAH2` | 燃料与公用事业 | ✅ | ≤1998 |
| `CUUR0000SAH3` | 家居陈设与运营 | ✅ | ≤1998 |
| `CUUR0000SAH31` | 家居陈设与用品 | ✅ | 2009 |
| `CUUR0000SAM1` | 医疗保健商品 | ✅ | ≤1998 |
| `CUUR0000SAN` | 非耐用消费品 | ✅ | ≤1998 |
| `CUUR0000SAN1D` | 国产农产食品 | ✅ | ≤1998 |
| `CUUR0000SANL1` | 非耐用消费品（除食品） | ✅ | ≤1998 |
| `CUUR0000SANL11` | 非耐用消费品（除食品饮料） | ✅ | ≤1998 |
| `CUUR0000SANL113` | 非耐用消费品（除食品饮料服装） | ✅ | ≤1998 |
| `CUUR0000SANL13` | 非耐用消费品（除食品服装） | ✅ | ≤1998 |
| `CUUR0000SARC` | 娱乐商品 | ✅ | 2009 |
| `CUUR0000SARS` | 娱乐服务 | ✅ | 2009 |
| `CUUR0000SAS` | 服务（整体） | ✅ | ≤1998 |
| `CUUR0000SAS24` | 公用事业与公共交通 | ✅ | ≤1998 |
| `CUUR0000SAS2RS` | 住房租金（rent of shelter） | ✅ | ≤1998 |
| `CUUR0000SAS367` | 其他服务 | ✅ | ≤1998 |
| `CUUR0000SAS4` | 交通服务 | ✅ | ≤1998 |
| `CUUR0000SASL2RS` | 服务（除住房租金） | ✅ | ≤1998 |
| `CUUR0000SASL5` | 服务（除医疗服务） | ✅ | ≤1998 |
| `CUUR0000SASLE` | 服务（除能源服务） | ✅ | ≤1998 |
| `CUUR0000SAT1` | 私人交通 | ✅ | ≤1998 |
| `CUUR0000SATCLTB` | 交通商品（除汽车燃油） | ✅ | 2009 |
| `CUUR0000SEAE` | 鞋类 | ✅ | ≤1998 |
| `CUUR0000SEAF` | 婴幼儿服装 | ✅ | ≤1998 |
| `CUUR0000SEAG` | 珠宝与手表 | ✅ | ≤1998 |
| `CUUR0000SEEEC` | 信息技术商品 | ✅ | 2009 |
| `CUUR0000SEGA` | 烟草及吸烟用品 | ✅ | ≤1998 |
| `CUUR0000SERA` | 影音（整体） | ✅ | ≤1998 |
| `CUUR0000SERAC` | 影音产品 | ✅ | 2009 |
| `CUUR0000SERAS` | 影音服务 | ✅ | 2009 |
| `CUUR0000SERB` | 宠物及相关（整体） | ✅ | ≤1998 |
| `CUUR0000SERC` | 体育用品（整体） | ✅ | ≤1998 |
| `CUUR0000SERD` | 摄影（整体） | ✅ | ≤1998 |
| `CUUR0000SERE` | 其他娱乐商品（整体） | ✅ | ≤1998 |
| `CUUR0000SERF` | 其他娱乐服务（整体） | ✅ | ≤1998 |
| `CUUR0000SERG` | 娱乐读物（整体） | ✅ | ≤1998 |
| `CUUR0000SETG` | 公共交通 | ✅ | ≤1998 |
| `CUUR0000SAE21` | 信息与信息处理 | ✅ | ≤1998 |
| `CUUR0000SAF11` | 居家食品 | ✅ | ≤1998 |
| `CUUR0000SAF116` | 酒精饮料 | ✅ | ≤1998 |
| `CUUR0000SAH21` | 家庭能源 | ✅ | ≤1998 |
| `CUUR0000SEAA` | 男装 | ✅ | ≤1998 |
| `CUUR0000SEAB` | 童男装 | ✅ | ≤1998 |
| `CUUR0000SEAC` | 女装 | ✅ | ≤1998 |
| `CUUR0000SEAD` | 童女装 | ✅ | ≤1998 |
| `CUUR0000SEAE01` | 男鞋 | ✅ | ≤1998 |
| `CUUR0000SEAE02` | 童鞋 | ✅ | ≤1998 |
| `CUUR0000SEAE03` | 女鞋 | ✅ | ≤1998 |
| `CUUR0000SEAG01` | 手表 | ✅ | ≤1998 |
| `CUUR0000SEAG02` | 珠宝 | ✅ | ≤1998 |
| `CUUR0000SEEB` | 学费/其他学杂费/托儿 | ✅ | ≤1998 |
| `CUUR0000SEEC` | 邮政与快递服务 | ✅ | ≤1998 |
| `CUUR0000SEEE` | 信息技术硬件与服务 | ✅ | ≤1998 |
| `CUUR0000SEFV` | 外食 | ✅ | ≤1998 |
| `CUUR0000SEGB` | 个人护理用品 | ✅ | ≤1998 |
| `CUUR0000SEGC` | 个人护理服务 | ✅ | ≤1998 |
| `CUUR0000SEGD` | 杂项个人服务 | ✅ | ≤1998 |
| `CUUR0000SEGE` | 杂项个人商品 | ✅ | ≤1998 |
| `CUUR0000SEHA` | 主要住所租金 | ✅ | ≤1998 |
| `CUUR0000SEHB` | 外出住宿 | ✅ | ≤1998 |
| `CUUR0000SEHC` | 自有住房等价租金（整体） | ✅ | ≤1998 |
| `CUUR0000SEHD` | 租户与家庭保险 | ✅ | ≤1998 |
| `CUUR0000SEHG` | 水、排污与垃圾处理服务 | ✅ | ≤1998 |
| `CUUR0000SEHH` | 窗饰与地面覆盖物 | ✅ | ≤1998 |
| `CUUR0000SEHJ` | 家具与寝具 | ✅ | ≤1998 |
| `CUUR0000SEHK` | 家电 | ✅ | ≤1998 |
| `CUUR0000SEHL` | 其他家用设备与陈设 | ✅ | ≤1998 |
| `CUUR0000SEHM` | 工具/五金/户外装备 | ✅ | ≤1998 |
| `CUUR0000SEHN` | 家居清洁用品 | ✅ | ≤1998 |
| `CUUR0000SEHP` | 家庭运营服务 | ✅ | ≤1998 |
| `CUUR0000SEMC` | 专业医疗服务 | ✅ | ≤1998 |
| `CUUR0000SEMD` | 医院及相关服务 | ✅ | ≤1998 |
| `CUUR0000SEME` | 健康保险 | ✅ | 2005 |
| `CUUR0000SEMF` | 药品 | ✅ | 2009 |
| `CUUR0000SEMG` | 医疗设备与耗材 | ✅ | 2009 |
| `CUUR0000SERA02` | 有线/卫星/流媒体电视服务 | ✅ | ≤1998 |
| `CUUR0000SERA03` | 其他视频设备 | ✅ | ≤1998 |
| `CUUR0000SERA04` | 视频购买/订阅/租赁 | ✅ | ≤1998 |
| `CUUR0000SERA05` | 音频设备 | ✅ | ≤1998 |
| `CUUR0000SERA06` | 录制音乐与订阅 | ✅ | ≤1998 |
| `CUUR0000SERB01` | 宠物及宠物用品 | ✅ | ≤1998 |
| `CUUR0000SERB02` | 宠物服务（含兽医） | ✅ | ≤1998 |
| `CUUR0000SERC01` | 运动车辆（含自行车） | ✅ | ≤1998 |
| `CUUR0000SERC02` | 运动装备 | ✅ | ≤1998 |
| `CUUR0000SERD01` | 摄影器材 | ✅ | ≤1998 |
| `CUUR0000SERD02` | 摄影师与照片冲洗 | ✅ | ≤1998 |
| `CUUR0000SERE02` | 缝纫机/布料/辅料 | ✅ | ≤1998 |
| `CUUR0000SERE03` | 乐器及配件 | ✅ | ≤1998 |
| `CUUR0000SERF01` | 俱乐部会费/参与费 | ✅ | ≤1998 |
| `CUUR0000SERF02` | 门票 | ✅ | ≤1998 |
| `CUUR0000SERF03` | 课程与指导费 | ✅ | ≤1998 |
| `CUUR0000SERG01` | 报纸与杂志 | ✅ | ≤1998 |
| `CUUR0000SERG02` | 娱乐书籍 | ✅ | ≤1998 |
| `CUUR0000SETA` | 新车与二手车 | ✅ | ≤1998 |
| `CUUR0000SETB` | 汽车燃油 | ✅ | ≤1998 |
| `CUUR0000SETC` | 机动车零配件 | ✅ | ≤1998 |
| `CUUR0000SETD` | 机动车维修保养 | ✅ | ≤1998 |
| `CUUR0000SETE` | 机动车保险 | ✅ | ≤1998 |
| `CUUR0000SETF` | 机动车税费 | ✅ | ≤1998 |
| `CUUR0000SETG01` | 机票 | ✅ | ≤1998 |
| `CUUR0000SETG02` | 其他城际交通 | ✅ | ≤1998 |
| `CUUR0000SETG03` | 市内交通 | ✅ | ≤1998 |

