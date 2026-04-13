# 一种工业热源提取方法:利用温度特征模板的BP神经网络

李博<sup>1</sup>, 范俊甫<sup>1*</sup>, 韩留生<sup>1</sup>, 孙广伟<sup>1</sup>, 张大富<sup>1</sup>, 张盼盼<sup>2</sup>

1. 山东理工大学建筑工程学院，淄博255000；2. 国家海洋技术中心，天津300112

# An Industrial Heat Source Extraction Method: BP Neural Network Using Temperature Feature Template

LI Bo $^{1}$ , FAN Junfu $^{1*}$ , HAN Liusheng $^{1}$ , SUN Guangwei $^{1}$ , ZHANG Dafu $^{1}$ , ZHANG Panpan $^{2}$

1. School of Civil and Architectural Engineering, Shandong University of Technology, Zibo 255000, China; 2. National Ocean Technology Center, Tianjin 300112, China

Abstract: Aiming at the problem of insufficient quantity and spatial refinement in the extraction of industrial heat source from annual scale thermal anomaly data, a neural network industrial heat source extraction method based on temperature feature template is proposed by using VIIRS active fire data. This study took Beijing-Tianjin- Hebei and its surrounding areas as the study area, Firstly, according to the spatial aggregation characteristics of industrial heat sources, the heat source objects were divided by the OPTICS algorithm. Secondly, according to the thermal radiation characteristics of the heat sources, the temperature characteristic template of industrial heat sources and non- industrial heat sources were constructed. Finally, the BP neural network was used to extract industrial heat source objects using the temperature feature template and heat source statistical characteristics as parameters. The results show that: (1) the extraction precision of industrial heat source of the neural network algorithm of temperature feature template proposed in this paper reached  $96.31\%$ . Compared with time filtering and logistic regression methods, the extraction precision of industrial heat sources was improved by  $8.45\%$  and  $7.53\%$ , respectively; (2) From 2015 to 2020, the number of industrial heat sources in the six provinces and cities in Beijing-Tianjin- Hebei and its surrounding areas decreased by  $27.46\%$ . The number of industrial heat source objects and heat anomalies in Hebei Province decreased by  $8.06\%$  and  $7.44\%$  annually, respectively, which was the largest decrease compared with other provinces and cities. The

concentration of industrial heat sources in Shandong and Tianjin increased by  $25.72\%$  and  $86.64\%$ , respectively, indicating that the industrial transformation and upgrade policies in the two places have achieved remarkable results; (3) Tangshan, Handan, Lvliang, and Changzhi accounted for  $31.37\%$  of the total industrial heat sources in the study area, which are the main cities in Beijing-Tianjin-Hebei and its surrounding areas. The degree of industrial heat source accumulation and energy consumption in seven cities such as Linfen and Taiyuan was higher than those in other cities; The degree of industrial heat source accumulation and energy consumption in 11 cities such as Beijing and Zhoukou was lower than those in other cities; (4) From January to May 2020, the number of industrial heat anomalies in Beijing-Tianjin-Hebei and its surrounding areas remained unchanged or increased compared with the same period in 2019 and 2021. The COVID-19 had no significant impact on the industrial heat source in the study area. The number of industrial heat anomalies in Wuhan in January and February 2020 decreased by more than  $66.67\%$  compared with that in the same period in 2019 and 2021, the number of industrial heat anomalies from March to May 2020 was lower than that in the same period of 2019. The COVID-19 has had a significant impact on industrial heat sources in Wuhan from January to May 2020. This study reflects the current situation and trend of industrial heat source development in Beijing-Tianjin-Hebei and its surrounding areas, which provides a valuable reference for the formulation and adjustment of relevant policies such as reducing energy consumption and improving secondary industry concentration.

Key words: industrial heat source; OPTICS algorithm; temperature feature template; neural network; VIIRS Active Fire; Beijing-Tianjin-Hebei and its surrounding areas

*Corresponding author: FAN Junfu, E-mail: fanjf@sdut.edu.cn

摘要针对年尺度热异常数据提取工业热源的方法存在数量和空间精细化程度不足的问题，使用VIIRS Active Fire数据，提出了一种基于温度特征模板的BP神经网络工业热源提取方法。该方法以京津冀及周边地区为试验区，首先，根据工业热源空间聚集性特征，使用OPTICS算法划分热源对象；其次，根据热源的热辐射特征，构建工业热源与非工业热源温度特征模板；最后，以温度特征模板、热源统计特征等作为参数，使用BP神经网络提取工业热源对象。结果表明：①本文提出的基于温度特征模板的BP神经网络算法的工业热源提取精度达到了  $96.31\%$  ，与时间滤波、逻辑回归方法相比较，工业热源提取精度分别提高了  $8.45\% ,7.53\% ;2015 - 2020$  年京津冀及周边地区6省市工业热源数量整体减少了  $27.46\%$  ；河北省工业热源对象数量和热异常点数量年均减少了  $8.06\%$  和  $7.44\%$  ，相对于其他省市减少幅度最大；山东、天津的工业热源集中度分别提高了  $25.72\%$  产 $86.64\%$  ，说明两地工业转型升级政策取得较显著成效；③唐山、邯郸、吕梁和长治4个城市工业热源对象数量占试验区全部的 $31.37\%$  ，为京津冀及周边地区工业热源主要分布城市；临汾、太原等7个城市工业热源聚集程度和能源消耗程度高于其他城市；北京、周口等11个城市工业热源聚集程度和能源消耗程度低于其他城市；④2020年1—5月，京津冀及周边地区工业热异常点数量相对于2019、2021年同期保持不变或增加，新冠疫情对试验区工业热源无显著影响；2020年1、2月武汉工业热异常点数量与2019、2021年同期相比数量减少了  $66.67\%$  以上，2020年3—5月工业热异常点数量低于2019年同期，2020年1—5月新冠疫情对武汉市工业热源影响显著。该研究反映了京津冀及周边地区工业热源发展的现状及趋势，能够为降低能耗和提高第二产业集中度等相关政策的制定与调整提供有价值的参考。

关键词：工业热源；OPTICS算法；温度特征模板；BP神经网络；VIIRSActiveFire；京津冀及周边地区

# 1 引言

工业是中国实体经济增长的主要来源，也是能源消耗的主体[1]。从事化石燃料燃烧(煤炭、石油、天然气等)的行业(钢铁、电解铝等)通常被认为是工业能源消耗的主要行业[2]，它们在生产过程中释放大量的热，形成工业热源。工业热源的空间分布，可以在一定程度上揭示工业的空间分布格局与

发展趋势，对于提高人们认识工业转型升级成效，制定产业政策具有重要参考价值与指导意义。

关于工业空间分布的研究主要基于政府部门公布的统计数据[3-4]，然而统计数据更新缓慢，时间、空间跨度较大，难以反映工业热源真实的空间变化特征。热红外遥感可以远程确定目标温度，具有覆盖范围广，不受地表观测条件限制的优势，为持续监测工业热异常提供了可能[5-6]。目前，热异常监

测技术已经广泛应用于城市热岛[7-8]、森林-草原火灾[9-10]、火山[11-12]等研究领域，并逐渐应用于工业热源的识别和监测。工业热源提取按照方法的不同可分为两类：基于指数的提取方法和基于聚类的提取方法[13]。基于指数的提取方法通过构建热异常指数识别热异常点进而提取工业热源，但是该方法需要结合额外数据去除水体和非工业季节性热源[2,14]。基于聚类的提取方法直接利用热异常数据通过聚类算法划分热源对象，一般可避免使用额外数据。如Ma[15-16]利用VIIRS(Visible Infrared Imaging Radiometer Suite) Active Fire 数据，使用K-means聚类划分热源对象，基于经验阈值分别提取了中国、印度的工业热源。然而对于不同时间跨度的数据，经验阈值主观性太强，对不同研究区、不同行业不具备通用性，需要重新设定阈值。

利用年尺度热异常数据提取工业热源的方法，主要依据工业热源在年尺度上的时间连续性特征和统计特征，不需要额外数据且避免了重新设定阈值的繁琐。因此，研究利用年尺度热异常数据提取工业热源的方法具有重要的应用意义。Liu等[17]利用VIIRS Nightfire数据，使用空间滤波和时间滤波方法划分热源对象并提取了2012—2016年全球每年工业热源对象，共计获得了工业热源对象15199个，提取精度为  $99.03\%$  ；赖建波[18]利用VIIRS Active Fire数据，使用DBSCAN（Density-Based Spatial Clustering of Applications with Noise)聚类和逻辑回归方法划分热源对象并提取了2013—2018年中国每年工业热源对象，其2013年获得了工业热源对象2603个，提取精度为  $97.30\%$  。由于部分工业空间位置集中，导致上述方法存在多个工业热源划分到一个热源对象中的问题，难以满足空间精细化应用的实际需求。

VIIRS Active Fire数据空间分辨率为  $375\mathrm{m}$ ，相对于VIIRS Nightfire数据在识别较小热源方面的能力更好，有利于划定更为精确的热源边界，识别出更多数量的潜在工业热源对象。京津冀及周边6省市地区是中国最大的能源工业基地、重要的钢铁、化工集中区域，同时也是空气污染最严重的地区之一[19]。神经网络具有较强的学习能力和非线性映射能力，广泛应用于判别分类、模式识别等众多领域。目前使用神经网络提取工业热源的研究较少。本文从进一步提高工业热源的提取数量和空间精细化程度的角度，提出了一种基于温度特征模板的BP神经网络方法。采用2015—2020年VIIRS

Active Fire数据，以京津冀及周边6省市为试验区，将本文方法与  $\mathrm{Liu}^{[17]}$  的时间滤波方法和赖建波[18]的逻辑回归方法在相同的实验条件下进行了对比。结果表明，本文方法在工业热源提取数量或精度方面有明显提高。

# 2 研究区概况、研究方法和数据来源

# 2.1 研究区概况

京津冀晋鲁豫6省市位于  $31^{\circ}23'N - 42^{\circ}40'N$ $110^{\circ}14'E - 122^{\circ}42'E$  之间，为中国钢铁、煤电、化工等传统工业分布集中区域[19]，高耗能行业体量大、层次低、能耗高、排放大，结构性过剩矛盾突出[20]。“十三五”时期，为了淘汰落后产能，改造提升传统动能，培育壮大新动能，京津冀及周边地区提出“2+26"城市的大气污染治理任务，涉及京津冀晋鲁豫6省市，重点调控电解铝、化工类企业生产活动[21]；山东省成为新旧动能转换综合试验区，加速钢铁、煤炭、电解铝、轮胎、水泥等行业的落后低效产能退出，为先进产能腾出空间[22]；山西省老工业城市加快创新创业能力建设和新旧动能转换，主动对接京津冀等东部省市[23]。

# 2.2 研究方法

# 2.2.1 技术路线

本文使用2015—2020年VIIRSActiveFire数据，为了便于提取工业热源对象，将数据重投影为Albers投影。使用OPTICS算法划分热源对象，通过轮廓系数对聚类结果的优劣进行评价，得到最优聚类结果；根据不同类型热源对象的热辐射特征，统计其温度频率分布，构建工业热源与非工业热源温度特征模板，并结合BP神经网络提取工业热源对象。如图1所示。

# 2.2.2 热源对象划分

长期进行高温生产活动的工业，其工业热源空间位置基本保持不变，热异常点通常以工业热源为中心紧密分布。基于密度的聚类算法将高密度的热异常点区域划分为簇，每一个簇代表一个热源对象。相关学者使用改进的K-means算法[15-16]和DBSCAN算法[18]划分热源对象，然而K-means算法很难发现非球形簇；DBSCAN算法虽然可以发现任意形状的簇，但当簇具有不相同密度的时候，DBSCAN算法性能较差。OPTICS算法是在DBSCAN的基础上改进的算法，降低了距离阈值的敏感性，

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/d00ba602-735d-4164-a1fc-2c45d9868274/b1b06e410300dd52fff31f34cf868a35dc656a6adf70dc679c3123f522955970.jpg)  
图1基于BP神经网络的工业热源对象提取方法技术流程  
Fig. 1 Technical process of industrial heat source object extraction method based on BP neural network

可以发现具有不同密度的簇。OPTICS算法广泛应用于空间信息处理[24]，如轨迹数据聚类[25]、产业空间数据聚类[26]等。

聚类算法是一种无监督的主观分类方法, 设置不同的阈值可能产生不同的聚类结果, 通过聚类评价指标度量聚类结果, 可获得最佳阈值。轮廓系数是评价聚类结果质量的一种指标, 它结合内聚度和分离度两种因素, 将数据集的任一对象与本簇中其它对象及其它簇中对象的相似性进行量化, 用来评

价该聚类结果的优劣。相关划分热源对象的研究均基于经验阈值[15,17-18]实现，本文结合相关学者的研究[15]，引入轮廓系数作为划分热源对象的评价指标，用来辅助判断OPTICS算法的最佳聚类阈值。最优聚类结果的阈值为：半径  $400\mathrm{m}$ ，热异常点数量8个。

# 2.2.3 温度特征模板构建

因不同类型热源的热辐射特征不同，同一类型热源通常会表现出相似的热辐射特征，因此本文根据I4波段亮度温度值构建工业热源与非工业热源温度特征模板。统计热源对象内热异常点的I4波段亮度温度，以  $2\mathrm{K}$  为间隔，对  $295\sim 367\mathrm{K}$  的温度范围进行划分，生成热源温度频率分布统计图。依据谷歌高分影像目视解译山东省2015年290个热源对象，将热源对象分为工业与非工业类型，其中200个工业热源对象，90个非工业热源对象，统计所有热源对象温度频率分布并分配到相应类型的温度特征模板中，温度特征模板如图2所示。

相同类型的热源对象的温度频率分布与所属类型的温度特征模板相似是工业热源划分的主要依据。将热源对象温度频率分布分别与工业热源、非工业热源温度特征模板进行相似性度量，相似性度量值越大，表示热源对象与该类型模板越相似。相似性度量公式如下：

$$
D = \frac {1}{1 + \sqrt {\sum_ {i = 1} ^ {n} \left(x _ {i} - y _ {i}\right) ^ {2}}} \tag {1}
$$

式中：  $D$  为相似性度量值；  $i = 1,2,\dots ,n$  ，  $n$  为温度特征模板中温度的间隔数量(  $295\sim 367\mathrm{K}$  区间内以 $2\mathrm{K}$  为间隔，  $n = 36$  )；  $x_{i}$  为热源对象的温度频率值； $y_{i}$  为温度特征模板的温度频率值。

# 2.2.4 工业热源对象提取

根据温度特征模板可以较好地区分工业热源

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/d00ba602-735d-4164-a1fc-2c45d9868274/cd268399291151b5fe08b3449fd70d40315903aae2f61ab8931532ba5c089108.jpg)  
(a)工业温度特征模板  
图2 工业和非工业温度特征模板的温度频率分布  
Fig. 2 Temperature frequency distribution of industrial and non-industrial temperature characteristic template

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/d00ba602-735d-4164-a1fc-2c45d9868274/088fc1282d412f58ae095e1403ffd4c48f044e79d52a2bea7efa1e8284a3efb3.jpg)  
(b)非工业温度特征模板

与非工业热源对象,但是存在一些热源对象的温度频率分布与同类型温度特征模板不一致的问题。BP神经网络具有较强的学习能力和非线性映射能力,并具有很强的容错性能,在函数逼近、模式识别等领域应用广泛[27],因此本文采用BP神经网络对工业热源对象的提取过程进行改进。

使用MATLAB软件中神经网络模式识别工具对已划分的热源对象进行训练并预测。该神经网络是两层前馈型BP神经网络(Back-Propagation Network), 使用trainscg函数进行训练。选取热源对象与两类温度特征模板的相似性度量值、两度量值之间的差值、热源对象的最小外接凸多边形面积和热异常点的数量、起止时间、工作天数、密度、热异常点数量与起止时间的比值、热异常点数量与工作天数的比值等作为特征参数。随机选择京津冀及周边地区2015年  $50\%$  的热源对象作为样本数据并目视解译, 训练、验证、测试比例分别为  $70\%$  、 $15\%$  、 $15\%$  , 隐藏神经元数量为10个。交叉熵、误差百分比越小表示错误分类越少, 对样本数据连续训

练50次，保留交叉熵和误差百分比较小的3个网络模型。选择roc最高  $(98.98\%)$  、混淆矩阵整体准确率最高  $(97.10\%)$  的网络模型作为最优网络模型，并使用该模型提取热源对象中的工业热源对象。

# 2.3 数据来源

VIIRS Active Fire数据下载自美国NASA（National Aeronautics and Space Administration）FIRMS（Fire Information for Resource Management System）系统，相关属性信息如表1所示。该产品使用VIIRS I4波段和I5波段的亮度温度值进行火点和无火背景的识别，通过I1波段、I2波段和I3波段的数据区分云、阳光和水体，利用M13波段得到火点辐射功率[28]。VIIRS Active Fire产品在MODIS（Moderate-resolution Imaging Spectroradiometer)热异常产品(MOD14/MYD14)算法的基础上进行了一些修改，使用固定和上下文算法相结合的方法探测白天和夜间的主动火灾和其他热异常，在小型火灾探测方面优于VIIRS Nightfire数据[28]

表 1 VIIRS Active Fire数据关键属性信息  
Tab. 1 VIIRS Active Fire data key attribute information  

<table><tr><td>关键属性</td><td>详细信息</td></tr><tr><td>空间分辨率</td><td>375m</td></tr><tr><td>下载地址</td><td>https://earthdata.nasa.gov/earth-observation-data/near-real-time/firms/active-fire-data</td></tr><tr><td>识别温度范围</td><td>400~1200K</td></tr><tr><td>研究时段</td><td>“十三五”前后时期,即2015年1月—2020年12月</td></tr><tr><td>热异常点数量</td><td>699478个</td></tr><tr><td>所含属性信息</td><td>中心点经纬度、时间(年/月/日/时/分)、亮度与传感器、热辐射能量等</td></tr></table>

# 3 结果与分析

# 3.1 实验结果与对比分析

使用最优网络模型对京津冀及周边地区2015年的样本数据预测分类，正例覆盖率为  $98.49\%$  。依次将2015—2020年热异常数据合并为年尺度热异常数据，使用最优网络模型提取京津冀及周边地区每年的工业热源对象。其数量依次为：1155、1111、1018、975、902、835个，根据谷歌高分影像等数据目视解译提取的工业热源对象，每年提取正确的工业热源对象数量分别为：1118、1071、980、937、859、811个，6年间累计提取的工业热源对象数量、累计提取正确的工业热源对象数量及整体提取精度分

别为：5996个、5775个、  $96.31\%$

目前，使用年尺度热异常数据提取工业热源的方法为空间滤波-时间滤波方法[17]、DBSCAN聚类-逻辑回归方法[18]。上述2种方法提取河北省、山西省2015年工业热源对象的数量均不足260个[17-18]，本文方法提取的数量分别为379、323个。本文方法在提取2015年河北省、山西省工业热源对象总数上优于上述2种方法，提取数量提高了  $35.00\%$  以上。主要因为上述2种方法都是基于经验阈值聚类划分热源对象，存在多个热源划分为一个热源对象的现象，导致提取工业热源对象数量较少。使用OPTICS算法划分热源对象，分别使用温度特征模板、基于温度特征模板的BP神经网络（温度+BP神经网络）、时间滤

波、逻辑回归4种方法提取工业热源对象。

如表2所示，4种方法每年工业热源提取精度相对于各方法的总体精度差值的正负浮动范围依次为  $1.54\%$  、  $1.08\%$  、  $2.15\%$  、  $1.74\%$  ，温度  $+\mathrm{BP}$  神经网络方法  $(1.08\%)$  具有更好的稳定性。虽然温度特征模板、逻辑回归方法在提取工业热源对象数量上高于温度  $+\mathrm{BP}$  神经网络方法（分别提高了  $1.26\%$  、  $4.28\%$  )，但温度  $+\mathrm{BP}$  神经网络方法整体精度为 $96.31\%$  ，相对于温度特征模板、时间滤波、逻辑回归3种提取方法分别提高了  $0.58\%$  、  $8.45\%$  、  $7.53\%$  。时间滤波方法应用于VIIRSNightfire数据具有较高的精度，主要因为VIIRSNightfire数据空间分辨率为 $750~\mathrm{m}$  ，仅能识别高温热源对象。VIIRSActiveFire

数据具有更高的空间分辨率(375m)，可探测出较多长期存在的非工业低温热源，如畜牧业、城市内大型建材批发市场等，导致时间滤波方法提取精度降低。温度+BP神经网络方法考虑到逻辑回归方法所使用的工业热源的最小外接面积、热源对象内的热异常点数量和热异常点的起止时间等因素，并结合更有效的温度特征模板作为特征参数提取工业热源，获得了优于逻辑回归方法的效果，工业热源对象提取精度提高了  $7.53\%$

# 3.2 工业热源空间分布

2015—2020年京津冀及周边地区累计提取了5775个工业热源对象(图3)。需要说明的是，由于

表 2 工业热源提取方法对比表  
Tab. 2 Comparison of industrial heat source extraction methods  

<table><tr><td rowspan="2">提取方法与精度</td><td colspan="6">年份</td><td rowspan="2">总体</td></tr><tr><td>2015</td><td>2016</td><td>2017</td><td>2018</td><td>2019</td><td>2020</td></tr><tr><td>温度特征模板/个</td><td>1131</td><td>1065</td><td>1002</td><td>945</td><td>875</td><td>830</td><td>5848</td></tr><tr><td>精度/%</td><td>96.58</td><td>96.47</td><td>95.89</td><td>94.50</td><td>94.19</td><td>96.51</td><td>95.73</td></tr><tr><td>温度+BP神经网络/个</td><td>1118</td><td>1071</td><td>980</td><td>936</td><td>859</td><td>811</td><td>5775</td></tr><tr><td>精度/%</td><td>96.80</td><td>96.40</td><td>96.27</td><td>96.00</td><td>95.23</td><td>97.13</td><td>96.31</td></tr><tr><td>时间滤波/个</td><td>1031</td><td>985</td><td>881</td><td>873</td><td>818</td><td>802</td><td>5390</td></tr><tr><td>精度/%</td><td>89.26</td><td>85.73</td><td>88.45</td><td>85.76</td><td>88.34</td><td>90.01</td><td>87.86</td></tr><tr><td>逻辑回归/个</td><td>1151</td><td>1108</td><td>1014</td><td>978</td><td>906</td><td>865</td><td>6022</td></tr><tr><td>精度/%</td><td>90.42</td><td>87.04</td><td>89.26</td><td>87.87</td><td>90.06</td><td>88.09</td><td>88.78</td></tr></table>

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/d00ba602-735d-4164-a1fc-2c45d9868274/fa7e0bd1074d6fed9539463952993fc0903ca8c1ad37e002d9504e2ccc7beb6d.jpg)  
(a) 1667个工业热源对象

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/d00ba602-735d-4164-a1fc-2c45d9868274/8951550aac930343a5b356133c1dbcb8541f45f878f4245d4ed369d4483c3808.jpg)  
(b)各城市工业热源对象数量  
图3 工业热源对象空间分布  
Fig. 3 Spatial distribution of industrial heat source objects

工业持续进行高温生产活动，6年间部分工业热源被多次识别提取，因此实际工业热源对象数量（1667个）小于累计提取的工业热源对象数量。京津冀及周边地区6省市1667个工业热源对象空间分布如图3所示，工业热源对象数量较高的城市位于河北省、山西省。河北省唐山市工业热源对象数量最多（105~249个），邯郸市、吕梁市和长治市工业热源对象数量较多（58~104个）。长治市和吕梁市为煤炭资源型城市；唐山市、邯郸市、长治市均为老工业城市，且为京津冀大气污染传输通道中的城市，存在产业层次低，工业发展方式粗放等问题[20]。河北省工业热源对象主要分布在唐山市（ $46.89\%$ ）、邯郸市（ $17.89\%$ ），分布呈现显著的空间聚集态势；山西省  $50.00\%$  以上城市的热源对象数量处于31~57个之间，未出现大于104个热源对象数量的城市，整体分布相对比较平均；山东省工业热源对象主要分布于中部地区，潍坊、滨州、济宁、东营、淄博、临沂、济南7个城市的规模以上工业企业的营业收入占比超过全省一半[29]；河南省工业热源对象数量较少， $77.77\%$  的城市的工业热源对象数量小于15个，整体分布相对平均；北京市工业热源对象数量最少（1~14个）；天津市工业热源对象数量处于中等程度（31~57个）。

# 3.3 工业热源省级尺度分析

# 3.3.1 实验区工业热源的整体变化趋势

2015—2020年，京津冀及周边地区工业热源对象数量减少了  $27.46\%$  ，工业热异常点数量减少了  $22.15\%$  ，整体呈下降趋势(图4)。2016—2017年工业热异常点数量减少比例小于工业热源对象数量减少比例，2017—2019年工业热异常点数量减少比例大于工业热源对象数量减少比例，主要是因为环保新政策推进，取缔“小散乱污”企业，实施电解铝、

化工类企业生产调控，导致部分工厂受到政策限制而停产或者关闭[21]。

# 3.3.2 各省市工业热源的数量及变化特征

工业热源对象和工业热异常点的数量可以表示工业生产的空间分布以及变化特征。2015—2020年，6个地区工业热源对象数量均有不同程度减少(图5(a))；工业热异常点数量除天津略有增加外，其余地区均有不同程度的减少(图5(b))；河北、山西、山东3省工业热源对象及工业热异常点数量较多；山东省和天津市工业热源对象数量分别减少了  $35.83\%$  、  $16.67\%$  ，两地工业热异常点数量分别减少了  $19.32\%$  、  $-55.54\%$  ，两地工业热源对象数量减少值与工业热异常点数量的减少值之间的差值分别为  $16.51\%$  、  $72.21\%$  ，表明两地工业热源对象数量减少比例显著高于工业热异常点数量的减少比例，进一步说明了山东、天津两地工业热源集中度分别提高了  $25.72\%$  和  $86.64\%$  。

Slope_NWH值（图5(c))和Slope_NFHWH值(图5(d))分别表示2015—2020年工业热源对象数量和热异常点数量相对标准化的增长速率。当Slope_NFHWH值小于0时，工业热异常点数量减少，Slope_NFHWH值越小，工业热异常点数量减少幅度越大[15]。河北省Slope_NWH值和Slope_NFHWH值为6省市最小值，河北省Slope_NFHWH值是山西、山东、河南3个地区总和的1.87倍，工业热源对象和热异常点数量减少幅度最大，表明河北省淘汰落后产能取得相对明显的成效。

# 3.4工业热源市级尺度分析

# 3.4.1 不同城市的工业热源聚集特征

工业热异常点密度变化可以反映工业园区空间分布变化。以  $10\mathrm{km}$  尺度的网格为单位，统计

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/d00ba602-735d-4164-a1fc-2c45d9868274/161a34cfb793c959d6adfe722aa8aa0b6e8c63e02590ea048b0a27e3309e774a.jpg)  
(a) 工业热源对象  
Fig. 4 Number of industrial heat source objects and industrial heat anomaly points in Beijing-Tianjin-Hebei and its surrounding areas

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/d00ba602-735d-4164-a1fc-2c45d9868274/a66407475a572f93a1c83acb63c9bc5c7df4de1519fd898b5a778e5db16232c2.jpg)  
(b) 工业热源热异常点  
图4 京津冀及周边地区工业热源对象和工业热异常点数量

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/d00ba602-735d-4164-a1fc-2c45d9868274/bc054b98e01979ebfb5b0cb7762ba0c5e68abb207a97be41b584b30545c3a9a2.jpg)  
(a) 热源对象

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/d00ba602-735d-4164-a1fc-2c45d9868274/997570b5a0c71a4c3a8cbb9126861bb9fdf23a66338a13addd2b8b0e77dd4427.jpg)  
(b) 热异常点

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/d00ba602-735d-4164-a1fc-2c45d9868274/dffeefb5f2b88be8158abbca2c88e23c833dff21740cd08741014ac6bce97f50.jpg)  
(c) Slope_NWH

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/d00ba602-735d-4164-a1fc-2c45d9868274/3fabe6cd08c2e46318e08bf32bbdcf4f44d9d1ffe00d192747097c13b64020eb.jpg)  
(d) Slope_NFHWH  
图5各区域工业热源对象数量、工业热异常点数量、Slope_NWH值、Slope_NFHWH值  
Fig. 5 Number of industrial heat source objects, number of industrial thermal anomaly points, Slope_NWH value and Slope_NFHWH value in each region

2015—2020年工业热异常点数量(图6)，根据网格中的工业热异常点数量将网格等级划分为一至五级，等级越高表明工业热源聚集程度越高。由图6可知，唐山、邯郸、临汾、石家庄、吕梁、运城、长治、滨州、太原、晋中、忻州、济宁、廊坊、临沂、潍坊、天津、秦皇岛共17个城市2015—2020年其中一年出现过五个以上五级网格，说明其工业热源聚集程度较高；北京、周口、威海、开封、漯河、濮阳、焦作、衡水、郑州、阳泉、鹤壁共11个城市6年未出现五级网格，说明其工业热源聚集程度较低。唐山、邯郸、临汾、吕梁其中一年出现10个以上五级网格，工业热源聚集程度高于其他城市；驻马店等其余30个城市六年出现过五级网格，但是每年均未超过4个五级网格。

对比2020年与2015年五级网格数量变化，唐山、廊坊、临汾、邯郸、石家庄、聊城、忻州、济宁、邢台、运城、潍坊共11个城市减少2个以上五级网格，商丘、太原、晋城、青岛、大同、三门峡、泰安、天津8个城市增加1个或者2个五级网格。减少两个以上五级网格的城市中唐山、廊坊、邯郸、石家庄、聊城、济宁、邢台7个城市属于“2+26”城市，“2+26”城市中滨州、新乡、保定、淄博、德州、长治6个城市减少一个五级网格，表明京津冀及周边地区涉及工业热源的相关产业调控政策取得了明显效果。

# 3.4.2 不同城市的工业能源消耗特征

FRP(Fire Radiative Power, 热辐射能量)大小可

以表征工业的能源消耗水平。以  $10\mathrm{km}$  尺度的网格为单位，统计2015—2020年工业热源FRP值分布（图7）。根据网格中的FRP值将网格等级划分为一至五级，等级越高表明工业能源消耗程度越高。临汾、吕梁、唐山、太原、石家庄、邯郸、长治7个城市2015—2020年其中一年出现过5个以上五级网格，说明其工业能源消耗程度较高；东营、北京、南阳、周口、商丘、大同、威海、平顶山、开封、朔州、洛阳、济源、淄博、漯河、濮阳、烟台、焦作、衡水、郑州、阳泉、青岛、驻马店、鹤壁共23个城市6年未出现五级网格，说明其工业能源消耗程度较低；唐山、邯郸至少有1年出现超过10个五级网格，表明两城市工业能源消耗程度明显高于其他城市；济南等其余28个城市6年出现过五级网格，但是每年均未超过4个五级网格，工业能源消耗程度总体平稳。

# 3.5新冠肺炎病毒疫情对工业热源的影响

2017—2019年因为环保政策推进，导致部分工厂受到政策限制而停产或者关闭，工业热源数量有明显的减少。2020年1月25日，由于新冠病毒疫情爆发，京津冀及周边地区相继启动了重大突发公共卫生事件一级响应，限制人口非必要流动[30]，新冠疫情是否对工业热源产生影响？国家统计局数据显示：2020年1—4月全国规模以上工业企业利润同比下降  $27.4\%$  。然而2020年1—4月与2019年同期相比，山东、山西、河北、河南4省工业部门二氧化

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/d00ba602-735d-4164-a1fc-2c45d9868274/038c8c30b989ecc31f33c0fac19c6e81cefeac0aa48fe2598471fc27a5aaedf6.jpg)  
(a) 2015年

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/d00ba602-735d-4164-a1fc-2c45d9868274/7cf9445086e39c16a6263c4b02199dd872a72c33eaad9e3c70fb940f972ced38.jpg)  
(b) 2016年

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/d00ba602-735d-4164-a1fc-2c45d9868274/4830291da9d61b45474d62981bd74a2b732940dc96772b5bba98b3790a3a5bc9.jpg)  
(c) 2017年

(d) 2018年  
图62015—2020年工业热异常点数量分布（  $10\mathrm{km}$  网格）  
![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/d00ba602-735d-4164-a1fc-2c45d9868274/19fe1dec50478bb48d2bce4533feb1491b4cfe6819b008427bfbc5956695f482.jpg)  
工业热异常点 /（数量/个） 一级(1~3) 二级(4~11) 三级(12~41) 四级(42~115) 五级(>115)  $0.100\mathrm{km}$

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/d00ba602-735d-4164-a1fc-2c45d9868274/92e8aba41af6041030ff372df7eb5c8215b961b7c397c3728ff7176e75f99a81.jpg)  
(e) 2019年

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/d00ba602-735d-4164-a1fc-2c45d9868274/c5dd83cb2b544f9870de2d652891aad443414d05b29c2724e9ca9490f7f907eb.jpg)  
(f) 2020年  
Fig. 6 The number distribution map of industrial thermal anomaly points from 2015 to  $2020(10\mathrm{km}$  grid)

碳排放量均增加，且山东、河南两省工业部门二氧化碳排放量增加值大于中国其他省份[31]，推测表明上述4省工业生产活动基本未受新冠肺炎疫情的影响。为分析新冠肺炎疫情对上述4省工业生产活动是否产生实际影响，以武汉市作为对比进行分析。2020年1月武汉市最先爆发疫情，且公共卫生应急响应一级时间持续最长（至2020年5月2日），武汉市的工业生产活动也因疫情管控而受到明显影响。因此本文从新冠肺炎疫情防控的4个时期和月尺度上对比研究了疫情对京津冀及周边地区和武汉市工业生产活动的影响。

各地区疫情响应等级调整时间、复工复产时间不一致，河北省为京津冀及周边地区疫情响应等级调整为二级的最后一个地区，因此本文以河北省为基准，将疫情防控分为4个时期：前期(1月1日—23日)、初期(1月24日—2月19日)、中期(2月20日—4

月30日)和后期(5月1—31日)。使用2019、2020、2021年热异常数据，前期阶段划分以农历除夕为分界点(2019年2月4日；2020年1月24日；2021年2月11日)[32]，其余阶段按相等时间跨度增加或减少。

疫情防控4个时期，京津冀及周边地区工业热异常点数量变化如图8(a)所示，疫情初、中、后3个时期2020年工业热异常点数量均位于2019年和2021年同期中间位置及以上，与2019年、2021年一致呈上升趋势。武汉市工业热异常点数量变化如图8(b)所示，2020年4个时期工业热异常点数量少于2019年同期，疫情初期2020年工业热异常点数量少于2019年、2021年，且为2019年同期的 $57.14\%$ ；疫情中期2020年工业热异常点数量为2019年的  $26.44\%$ ，与2021年无显著差异。

月尺度上，京津冀及周边地区2020年工业热异常点数量仅在2月少于2021年，其余时间多于或与

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/d00ba602-735d-4164-a1fc-2c45d9868274/9e80a9e44654ff1ad1e1ab9987598516252e707271ac0a72dfb90964da671fa9.jpg)  
(a) 2015年

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/d00ba602-735d-4164-a1fc-2c45d9868274/dfeec6bc0f218052217fd4a69689f0b113a714b170e4940219db08b4aff031a3.jpg)  
(b) 2016年

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/d00ba602-735d-4164-a1fc-2c45d9868274/61260d1020bb1c72507cede40f43351320a7bc3b37024cba200c7c6c4d8e91f7.jpg)  
(c) 2017年

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/d00ba602-735d-4164-a1fc-2c45d9868274/9bb6a69e0ff811296a49f401305c84baef7701cab4a236267013f49d36fb5f5e.jpg)  
(d) 2018年

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/d00ba602-735d-4164-a1fc-2c45d9868274/66951970629e19af61ebda3232d06b768b78ce12ceef4890e848dfc6c29712d2.jpg)  
(e) 2019年

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/d00ba602-735d-4164-a1fc-2c45d9868274/58aed071d38efc8c7d1985d02b1c5220e85e4e1f2b763bb6a4b0a7de07750893.jpg)

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/d00ba602-735d-4164-a1fc-2c45d9868274/3554fc46b95fd91a1d17ee11a4391a89153c5ed184b31eeb6c859aa2383469e6.jpg)  
(f) 2020年  
图72015—2020年工业热源FRP值分布图（  $10\mathrm{km}$  网格）

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/d00ba602-735d-4164-a1fc-2c45d9868274/da42f85efd12700b67dcdf3439c4cb36b42fca0e63b0d354c689cdb150a9fc87.jpg)  
(a)京津冀及周边地区  
图8疫情防控4个时期工业热异常点日平均数量  
Fig. 8 Daily average number of industrial heat anomaly points in four periods of epidemic prevention and control

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/d00ba602-735d-4164-a1fc-2c45d9868274/fe699e85203a1fa132a6c1d19ecc8e510a11c4bed0fc54e8f5321befc137a3e7.jpg)  
Fig. 7 FRP value distribution map of industrial heat source from 2015 to 2020 (10 km grid)  
(b)武汉

2019、2021年工业热异常点数量基本一致（图9(a)）。武汉市2020年1—5月工业热异常点数量少于2019年同期，2020年1—4月工业热异常点数量与2019年同期相比数量减少了  $70\%$  以上；武汉市2020年1、2月工业热异常点数量与2021年同期相

比数量分别减少了  $66.67\%$  、  $75.00\%$

由上述结果可知，京津冀及周边地区工业热源在新冠病毒疫情时期(1—5月)未受到明显影响，与刘竹[31]的研究结果一致，武汉市工业热源受新冠病毒疫情影响比较严重。主要原因是京津冀及周边

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/d00ba602-735d-4164-a1fc-2c45d9868274/bc3f4c4463f002c2a306164b3e4fc5695ad1ef5f2b89a9689fc4688246e234a0.jpg)  
图91—5月热异常点数量  
Fig. 9 Number of thermal anomaly points from January to May

地区为中国重化工聚集区域，钢铁、冶金、石化等资源型行业对工厂生产的连续性要求高[33]；新冠疫情期间武汉市电力、水泥、陶瓷等企业部分停工停产[34]，因此上述结果可在一定程度上反映实验区内工业生产活动的精细化时空变化特征。

# 4 结论与讨论

自2011年以来，中国加快工业转型升级，获取工业热源空间分布信息对于了解工业碳排放、第二产业集中度具有重要的意义。本文针对年尺度热异常数据提取工业热源的方法存在提取数量和时空精细化程度不足的问题，设计了一种BP神经网络结合温度特征模板的工业热源对象精细化提取方法。采用该方法实现了对2015—2020年京津冀及周边区域工业热源对象的识别和提取，并对其时空变化特征进行了分析和讨论。结论如下：

(1)通过较少的数据(2015年山东省热源对象温度频率分布)生成的温度特征模板，在提取工业热源对象时获得了  $95.73\%$  的精度，表明根据热辐射特征构建的温度特征模板可较好的划分工业热源和非工业热源对象。基于温度特征模板及BP神经网络的工业热源提取方法获得了  $96.31\%$  的精度，优于传统的时间滤波、逻辑回归等方法，2015—2020年京津冀及周边地区共计提取了1667个工业热源对象。  
(2)2015—2020年京津冀及周边地区工业热源对象和热异常点数量整体呈减少趋势。工业转型升级对于工业热源影响较大，且已经取得明显成效。山东、天津地区工业热源集中度得到提高，河北地区工业热源呈现显著的聚集态势，且工业热源对象和热异常点减少数量大于其他省市减少数量。唐山、邯郸等17个城市工业热源聚集程度较高；临汾、吕梁等7个城市工业能源消耗程度较高；

唐山、邯郸两城市其中一年出现过10个以上工业热异常点数量和FRP值五级网格，工业热源聚集程度及能源消耗程度最高。

(3)京津冀及周边地区2020年疫情防控4个时期和月尺度的工业热异常点数量相对于2019年、2021年同期保持不变或增加，表明2020年1—5月新冠病毒疫情对京津冀及周边地区工业热源无显著影响。武汉市2020年疫情防控4个时期和月尺度工业热异常点数量均少于2019年同期，武汉市2020年1—2月工业热异常点数量不足2021年同期的  $33.33\%$  。表明2020年1—5月新冠病毒疫情对武汉市工业生产活动影响显著。

本文提出的基于温度特征模板和BP神经网络的年尺度工业热源提取方法可以较好的识别工业热源对象，相关研究结果反映了京津冀及周边地区工业热源发展的现状。2015—2018年，京津冀及周边地区工业热源数量整体呈减少趋势，与 $\mathrm{Ma}^{[15]}$ 和赖建波[18]得出的中国工业热源数量减少趋势的结论一致，由于环保政策的影响，部分中小型工业热源停产或者关闭。河北省工业热源主要分布在唐山市、邯郸市，这一结果与之前在京津冀地区的工业热源空间分布的研究一致[35]，2个城市均为老工业城市，工业热源以钢铁厂、煤化工厂相关类型为主，存在产业层次低，工业发展方式粗放等问题。对工业热源空间分布的相关研究[13,15,18]主要在省级尺度方面，本文在省级尺度和市级尺度上分析了工业热源的空间分布、聚集程度和能源消耗程度，有助于我们更好的把握工业热源时空演变规律。
