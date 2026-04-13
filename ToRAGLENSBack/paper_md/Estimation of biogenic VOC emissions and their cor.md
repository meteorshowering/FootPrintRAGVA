# Estimation of biogenic VOC emissions and their corresponding impact on ozone and secondary organic aerosol formation in China

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/ee507cff-688b-41b8-9b9a-13c820585331/63201c254375e619c156aa250f7b44fb33e614ac1ce468aeea703f8716fa1daa.jpg)

Kai Wu $^{a}$ , Xianyu Yang $^{a,\ast}$ , Dean Chen $^{b}$ , Shan Gu $^{a}$ , Yaqiong Lu $^{c}$ , Qi Jiang $^{a}$ , Kun Wang $^{d}$ , Yihan Ou $^{a}$ , Yan Qian $^{e}$ , Ping Shao $^{a}$ , Shihua Lu $^{a}$

$^{a}$  Plateau Atmosphere and Environment Key Laboratory of Sichuan Province, School of Atmospheric Sciences, Chengdu University of Information Technology, Chengdu 610225, China  
$^{b}$  Institute for Atmospheric and Earth System Research (INAR)/Physics, Faculty of Science, University of Helsinki, Helsinki 00560, Finland  
$^{c}$  Institute of Mountain Hazards and Environment, Chinese Academy of Sciences, Chengdu 610041, China  
$^{d}$ Department of Air Pollution Control, Beijing Municipal Institute of Labor Protection, Beijing 100054, China  
$^{e}$  State Key Laboratory of Environmental Criteria and Risk Assessment & Environmental Standards Institute, Chinese Research Academy of Environmental Sciences, Beijing 100012, China

# ARTICLEINFO

Keywords:

BVOC

Ozone

Modeling

MEGAN

SOA

# ABSTRACT

Biogenic volatile organic compounds (BVOC) play an important role in global environmental chemistry and climate. In the present work, biogenic emissions from China in 2017 were estimated based on the Model of Emissions of Gases and Aerosols from Nature (MEGAN). The effects of BVOC emissions on ozone and secondary organic aerosol (SOA) formation were investigated using the WRF-CMAQ modeling system. Three parallel scenarios were developed to assess the impact of BVOC emissions on China's ozone and SOA formation in July 2017. Biogenic emissions were estimated at  $23.54\mathrm{Tg / yr}$ , with a peak in the summer and decreasing from southern to northern China. The high BVOC emissions across eastern and southwestern China increased the surface ozone levels, particularly in the BTH (Beijing-Tianjin-Hebei), SCB (Sichuan Basin), YRD (Yangtze River Delta) and central PRD (Pearl River Delta) regions, with increases of up to  $47\mu \mathrm{g}\mathrm{m}^{-3}$  due to the sensitivity of VOC-limited urban areas. In summer, most SOA concentrations formed over China are from biogenic sources (national average of  $70\%$ ). And SOA concentrations in YRD and SCB regions are generally higher than other regions. Excluding anthropogenic emissions while keeping biogenic emissions unchanged results that SOA concentrations reduce by  $60\%$  over China, which indicates that anthropogenic emissions can interact with biogenic emissions then facilitate biogenic SOA formation. It is suggested that controlling anthropogenic emissions would result in reduction of both anthropogenic and biogenic SOA.

# 1. Introduction

Biogenic volatile organic compounds (BVOCs) emitted from terrestrial ecosystems have substantial effects on the global climate and environmental chemistry. Previous studies have shown that up to  $90\%$  of the total VOC emissions are derived from biogenic sources (Guenther et al. 1995). BVOCs such as isoprene, monoterpenes and sesquiterpenes participate in oxidative chemical reactions in the atmosphere with oxidants such as ozone, OH and  $\mathrm{NO}_3$  radicals. In addition, BVOCs are major sources of secondary organic aerosols (SOA) and new particle formation (Hallquist et al. 2009; Kulmala et al. 2004; Paasonen et al. 2013; Kota et al. 2015). Measurements and modeling of BVOC emissions are of vital importance to understand the carbon cycle, biosphere-atmosphere interactions and climate change (Gu et al. 2017; Hantson et al. 2017).

Over the past few decades, research has been focused on four objectives: (1) developing and improving BVOC instruments and technology, (2) quantifying the effects of BVOC emissions, (3) developing and improving BVOC emission models, and (4) understanding the mechanisms underlying the interactions of BVOCs with anthropogenic volatile organic compounds (AVOCs). Most BVOCs are highly reactive and readily interact with oxidants, consequently influencing the atmospheric composition. Therefore, accurately estimating the BVOC emissions can improve the results of studies of the effects of BVOCs on the regional and global air quality and climate systems (Makkonen et al. 2012).

BVOC emissions are calculated with models, and the Model of Emissions of Gases and Aerosols from Nature (MEGAN) is one of the models commonly used (Guenther et al. 2006). The standard emission potential of a plant depends on the plant functional type (PFT) and its

biomass. Moreover, the driving factors of emission activities are the PFT type, leaf area index (LAI), temperature, radiation, wind speed, humidity and soil moisture content. The meteorological variables can be obtained from observations, reanalysis data and weather forecasting models, and the PFT type, biomass and LAI are obtained from remote sensing databases.

BVOC emissions have been studied regionally and globally for the past several decades (Graedel et al. 1993). Global emissions of biogenic isoprene and monoterpenes were estimated to be  $400 - 600\mathrm{Tg / yr}$  and  $33 - 147\mathrm{Tg / yr}$ , respectively (Arneth et al. 2011). In China, BVOC emissions from plants are estimated to be approximately 1.5 times those from anthropogenic sources. And several studies have been conducted for analyzing the characteristics of BVOC emission in China. However, most studies mainly focused on local and regional scale for the Pearl River Delta (PRD), Beijing, Hong Kong, and Yangtze River Delta (YRD) regions based on various methodologies (Liu et al., 2018; Ou et al. 2015; Pan et al. 2015; Situ et al. 2013; Tsui et al. 2009). Furthermore, in the context of global warming, Yu and Hong (2012) reported that isoprene and monoterpene emissions in China displayed large interannual variations of  $15 - 42\%$  and  $10 - 32\%$  from 2001 to 2006, respectively. Li and Xie (2014) studied the changes in emissions in China from 1981 to 2003 and discovered an increase in BVOC emissions induced by a biomass increase. Due to the large interannual variations of BVOC emissions, it is expected that previous estimates of national BVOC emissions in China which concentrated on early time may not reflect their current characteristics. Therefore, updating BVOC emissions is necessary to provide scientific support for air quality improvements in China.

Modeling and laboratory studies have shown that BVOC emissions can affect surface ozone and SOA. With the remarkable economic development and rapid increase of fossil fuel consumption, the air quality in China has deteriorated in recent years. Ground-level ozone pollution has become a major air quality issue in China. In addition, heavy pollution episodes exceeding 120 ppbv often occur in metropolis clusters such as Beijing-Tianjin-Hebei, the Yangtze River Delta and Sichuan Basin. A better understanding of the causes of elevated ozone in China is critical to develop effective emissions control strategies. Biogenic SOA (BSOA) is a major pollutant worldwide. Because of the large anthropogenic emission sources in China, anthropogenic SOA could be comparable to BSOA. Ding et al. (2014) analyzed SOA tracers from isoprene, monoterpenes, sesquiterpene and aromatics in China and found that isoprene and aromatics are primary contributors to SOA. Mo et al. (2018) investigated the contribution of biogenic isoprene emissions to ground-level ozone formation based on ground-based measurements in Beijing and found that isoprene emissions accounted for half of the total ozone formation potential. Qin et al. (2018) employed the CMAQ model to simulate isoprene-derived and monoterpene-derived BSOA formation in China, and the results indicated that isoprenederived BSOA dominates BSOA formation in China. However, those studies focused only on a specific temporal period or regional scale. The overall impact of BVOC emissions on ground-level ozone and SOA formation in China remains unclear and must be addressed.

In this study, the objectives are to estimate BVOC emissions in China at a high spatial resolution and probe the effects of BVOC emissions on ground-level ozone and SOA formation in China. MEGAN version 2.1 and Weather Research and Forecasting model coupled with the Community Multiscale Air Quality (WRF-CMAQ model) were adopted to estimate BVOC emissions and investigate the impacts of BVOC emissions on ground-level ozone and SOA. The year 2017 was selected as the base year to simulate the spatiotemporal variations in BVOC emissions. The paper is organized as follows. Section 2 introduces the methodologies and databases used to estimate biogenic emissions, as well as the WRF-CMAQ framework. The model performance is described in Section 3, with comparisons of meteorological data on BVOC emissions with model results. Moreover, the effects of BVOC emissions on summertime  $\mathrm{O}_3$  and SOA formation are described in Section 3. The conclusions are presented in Section 4.

# 2. Methodology

# 2.1.WRF configuration

The WRF model version v3.9.1 was adopted to provide meteorological conditions for high spatiotemporal resolution data to determine the diurnal relative humidity, temperature, solar radiation, and wind speed. The spatial and temporal resolutions were  $27\mathrm{km}\times 27\mathrm{km}$  and  $1\textrm{h}$ , respectively. The vertical dimensions were 27 levels with a  $100\mathrm{hPa}$  model top. The initial and boundary conditions were obtained from the National Centers for Environmental Prediction (NCEP) FNL  $1.0^{\circ}\times 1.0^{\circ}$  reanalysis data (http://dss.ucar.edu/datasets/ds083.2/). To improve the model performance, the NCEP ADP Operational Global Surface Observations were used for surface reanalysis and four dimensional data assimilation. And we chose proper strength of nudging coefficients, i.e.,  $0.00001\mathrm{s}^{-1}$  is used for nudging of water vapor mixing ratio and  $0.00005\mathrm{s}^{-1}$  is used for nudging of both u/v-wind potential temperature (Hogrefe et al. 2015; Xing et al. 2015; Xing et al. 2017). The components of the model setup are listed in Table 1.

# 2.2. MEGAN configuration

MEGAN v2.1 (Guenther et al. 2012) was utilized to estimate BVOC emissions in China with a  $27\mathrm{-km}$  horizontal grid spacing domain (shown in Fig. 1). The inputs for MEGAN include the LAI, PFTs, emission factors, and meteorological data (e.g., solar radiation, temperature, relative humidity and soil moisture). The monthly average LAI was obtained from the 8-day MODIS LAI product (MOD15A2, 2017) with the same horizontal resolution as the study domain, as shown in Fig. 2. The PFT map was obtained from the MODIS MCD12Q1 product and regridded into the WRF domain to compute the fraction of each PFT in each grid (Fig. 3). The default MEGAN emission factors  $(\mathrm{mg~m}^{-2}\mathrm{h}^{-1})$  with a resolution of  $30\mathrm{s}$ $(< 1\mathrm{km})$ , which reflect the BVOC emission rate under standard canopy conditions, were leveraged (http://lar.wsu.edu/megan/guides.html). Meteorological conditions were simulated by the WRF model. A one-year MEGAN simulation was performed for 2017 in China.

# 2.3.CMAQ configuration

We set up Community Multiscale Air Quality model (CMAQ version 5.2.1, Foroutan et al. (2017)) (https://www.cmascenter.org/cmaq/) to simulate the atmospheric composition over China with the same domain and grid resolution for WRF and MEGAN. The initial and boundary conditions for CMAQ simulation were based on the CMAQ default profiles which represent unpolluted atmosphere. The CB05 represented the gas phase, and AERO6 represented the aerosol chemical mechanisms (Appel et al. 2013). For the simulation of SOA, we used the default SOA module of the CMAQv5.2.1. It simulates NMVOC-derived SOA with a two-product model, treats primary organic aerosol (POA) as nonvolatile and nonreactive, and ignores IVOC emissions. Carlton et al. (2010) provided a detailed description of aerosol chemistry in CMAQ, including SOA formation from benzene, isoprene and sesquiterpenes. The POA oxidation mechanism is described in Simon and Bhave (2012). The new updates in CMAQ v5.2.1 accounts for the semivolatile

Table 1 WRF analysis options.  

<table><tr><td>Component</td><td>Option</td></tr><tr><td>Microphysics</td><td>Lin microphysics scheme</td></tr><tr><td>Longwave radiation</td><td>RRTM scheme</td></tr><tr><td>Shortwave radiation</td><td>Goddard shortwave</td></tr><tr><td>Surface layer</td><td>MM5 similarity</td></tr><tr><td>Land surface</td><td>Noah Land Surface Model</td></tr><tr><td>Planetary boundary layer</td><td>Yonsei University scheme</td></tr><tr><td>Cumulus parameterization</td><td>Grell 3D</td></tr></table>

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/ee507cff-688b-41b8-9b9a-13c820585331/12170ca7daf655853008b507f7ccd9c288ec726e78f38042c6a9b19b4fc888bd.jpg)  
Fig. 1. Simulation domain.

partitioning and gas-phase aging of these POA compounds consistent with experimentally derived parameterizations (Murphy et al. 2017), SOA properties and IEPOX organosulfate formation rate constant were updated (Pye et al. 2017). We selected July as representative of summertime and acquired anthropogenic emissions for the CMAQ domain from the MEIC emission inventory 2016 developed by Tsinghua University (http://www.meicmodel.org/), which contains monthly gridded  $(0.25\times 0.25^{\circ})$  emissions information for anthropogenic emissions in the CB05 mechanism. The biogenic emissions were modeled using MEGAN (described in Section 2.2).

# 3. Results and discussion

# 3.1. Evaluation of the performance of the WRF model and MEGAN

Fig. S1 and S2 show the seasonal spatial distribution of temperature at  $2\mathrm{m}$  (T2) and the daily downward shortwave radiation (DSW) simulated by the WRF model. And these meteorological factors were evaluated using in situ measurement data from 824 and 84 national meteorological sites, respectively. The in situ measurement data are from the China Meteorological Data Sharing Service System (http://data.cma.cn/). Table 2 presents the verification statistics for the average daily T2 and DSW among all sites. As shown in Table 2, the mean error (ME), mean bias (MB), correlation coefficient (r) and root mean square error (RMSE) of station-averaged hourly T2 series are 2.47, -1.26, 0.95 and  $2.59^{\circ}\mathrm{C}$ , respectively. The simulation yields cooling biases of  $-0.98$ ,  $-0.90$ ,  $-1.70$  and  $-1.18^{\circ}\mathrm{C}$  in spring, summer, fall and winter, respectively. The ME, MB, r and RMSE values for the annual DSW series are 36.00,  $-29.88$ , 0.80 and  $81.33\mathrm{Wm}^{-2}$ , and the DSW simulation yields underestimations of 32.12, 43.61, 24.25 and  $19.38\mathrm{Wm}^{-2}$  in spring, summer, fall and winter, respectively. It is because that the WRF model overestimate the cloud coverage which lead to the slightly underestimation on T2 and DSW (Wang et al. 2010; Wen et al. 2014). Compared with other studies on yearly long WRF simulation in China (Wang et al., 2014; Ying et al. 2014; Zhang et al., 2012), these biases are

relatively small and the simulations on temperature and radiation are correlated with the observations under a confidence level of 0.01, indicating both seasonally and yearly significant correlations in this study. Therefore, the WRF model performances of meteorological conditions can be considered reasonable for driving MEGAN.

Table 3 illustrates the estimated annual emissions of BVOCs in this work and other studies. The estimate of annual BVOC emissions was  $23.54\mathrm{Tg}$ , which is within the range reported in previous estimates, ranging from  $12.83\mathrm{Tg}$  to  $42.5\mathrm{Tg}$  between 1990 and 2006. Estimates in the present work are greater than the  $20.6\mathrm{Tg}$  for 2000 estimated by Klinger et al. (2002) and  $12.83\mathrm{Tg}$  for 2003 estimated by Chi and Xie (2011). However, the estimates in the present study are lower than the results of Guenther et al. (1995) and Li et al. (2013), who obtained values of  $28.4\mathrm{Tg}$  for 1990 and  $42.5\mathrm{Tg}$  for 2003, respectively. Differences among the discussed studies can be attributed to various factors. It is reported that the forest coverage, the percentage of which increased from  $16.6\%$  in 2003 to  $21.63\%$  in 2014, and the forest area increased from  $1.59\times 10^{8}\mathrm{hm}^{2}$  in 2003 to  $2.08\times 10^{8}\mathrm{hm}^{2}$  in 2014 (China Forestry Bureau (CFB), 2014), which may be the main reasons for large discrepancies. In addition, BVOC emissions were largely followed by LAI changes (Souri et al. 2017). Chen et al. (2019) utilized satellite data to analyze the annual average MODIS LAI in China from 2000 to 2017 and observed a significant increasing trend in eastern China (the trend was higher than  $18\times 10^{-2}\mathrm{m}^2$  per  $\mathrm{m}^2$  per decade; see Fig. S3 in the Supporting Information). Therefore, the interannual variation of LAI is also an important factor which cause the differences. Besides, some of the discrepancies can also be explained by the use of different algorithms and emission factors. In this study, the MEGAN default global average EFs were applied to estimate BVOC emissions. Li et al. (2012) used a simplified isoprene algorithm (PCEEA) and neglected the effect of soil moisture and detailed canopy information, which resulted in a much lower estimate of  $12.97\mathrm{Tg}$  in 2006 than our study. Yu and Hong (2012) adopted lower EFs and leaf biomass densities for each plant type derived from a small number of local measurements, which caused an underestimation of emissions. There is a large difference of isoprene emission

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/ee507cff-688b-41b8-9b9a-13c820585331/7d77089fc2b171743d83c8940ae20e838130acce41c982325ade541ec5b3b8e3.jpg)

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/ee507cff-688b-41b8-9b9a-13c820585331/0acd6ae17cbb26a0549e66727498760ba06acd7f8d821b79d7ef1d14f276c8c6.jpg)

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/ee507cff-688b-41b8-9b9a-13c820585331/f8f08ed440f8f8c20b59a7b7dfa7459a1a7925584869b4fb60338b046f56545e.jpg)  
Fig. 2. Seasonal spatial distribution of the LAI in the model domain.

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/ee507cff-688b-41b8-9b9a-13c820585331/50138856bbd9c3ab8ac23eae8c59ede1af5df7fe2681103a1586f0768ae17af2.jpg)

between our results and those of Klinger et al. (2002). It is mainly because that Klinger et al. (2002) did not include emissions from the shrubs and assumed that BVOC emissions emitted from forests in China with  $251,283\mathrm{km}^2$  which is smaller than the domain of our study. Therefore, variations in these factors in different years may be the cause of the uncertainty in the modeling simulations. However, large discrepancies in the emission estimates still exist among this study and previous studies. These differences result from the use of different emission factors, land cover distributions, meteorological conditions and model algorithms in developing the emission inventories, as discussed above.

# 3.2. Spatial distribution of BVOC emissions

BVOC emissions exhibit overt spatial variations due to the differences in vegetation types, topography and climatic conditions. Previous studies have shown that broadleaf forests and shrubs have strong isoprene emission potentials, coniferous forests have high terpene emission potential, and crops and grasses are generally considered to have low or no isoprene emissions (Wiedinmyer et al. 2006; Chen et al. 2018). Therefore, the distribution of high isoprene emissions is generally associated with the distribution of broadleaf forests and shrubs.

As shown in Fig. 4, BVOC emissions in China are mostly centralized in the northeast and southeast and in southern Yunnan, Hainan and Taiwan Provinces. Specifically, the forest area in Yunnan accounts for nearly  $10\%$  of all forest cover in China. Therefore, Yunnan Province has the highest BVOC emissions, and the large area of tropical rainforest cover in southern Yunnan leads to substantially higher BVOC emissions in the southern region than in other regions. The high emissions in the

northeast are due to the high forest coverage of the genus and eucalyptus forest which have the highest isoprene emission potential. Taiwan's high emissions originate from evergreen broadleaf forests. The distribution of various deciduous, hardwood and mixed broadleaf trees account for the high emissions in southeastern China and the Qinglin Mountains. Owing to the wide coverage of tropical rainforests, the BVOC emissions in Hainan Province are consequently high. Because of the principal contribution of isoprene to total BVOCs, the spatial distribution of total BVOC emissions is similar to that of forest distribution. Terpene emissions are concentrated in the southern part of China (especially in the southeast) because of the high-density coniferous forests there. In southwestern China, especially in the Sichuan-Tibet region, high altitudes and low temperatures on the Tibetan Plateau have led to low levels of emissions in the region. In the Sichuan Basin (SCB), although the forest and shrub coverages are high, isoprene emissions are relatively low. This trend may be caused by the low temperatures in western Sichuan and the low solar radiation in eastern Sichuan, coupled with the closed terrain and extensive cloud cover in the atmosphere Lin and Li, 2016). In addition, high OVOC emissions lead to high total BVOC emissions in most parts of southern China.

# 3.3. Seasonal variations

The modeling results from this study indicate different seasonal BVOC emissions in China (Fig. 5). Isoprene and terpene are the most dominant BVOC emissions. The quantity of seasonal BVOC emissions varies as follows: summer  $>$  spring  $>$  autumn  $>$  winter. The distribution pattern of isoprene in spring and autumn is quite consistent

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/ee507cff-688b-41b8-9b9a-13c820585331/99c3fbb999aefadc61bb5df824c8a8ce5bc8d6562648a3aab0c708bfc46deec7.jpg)

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/ee507cff-688b-41b8-9b9a-13c820585331/7028d6994f0bee655c69b1200aa920f5f7b25dcd430e322ca3b9a9dc9954bf99.jpg)

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/ee507cff-688b-41b8-9b9a-13c820585331/5dc82116851fb2bda68ee98caa0ce8c3e10bef215d235d8bbee86f996edae6d6.jpg)  
Fig. 3. Seasonal distributions of the proportions of PFTs in the model domain.

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/ee507cff-688b-41b8-9b9a-13c820585331/31b45fdf56ef9de114ee37b51d4cc6fa599c68839afeb852bea562378d106e6b.jpg)

Table 2 Verification statistics for the WRF simulations of temperature at  $2\mathrm{m}$  (T2) and downward shortwave radiation (DSW).  

<table><tr><td rowspan="2">Variable</td><td rowspan="2">Season</td><td colspan="2">Mean</td><td rowspan="2">ME</td><td rowspan="2">MB</td><td rowspan="2">r</td><td rowspan="2">RMSE</td></tr><tr><td>Obs.</td><td>Sim.</td></tr><tr><td rowspan="5">T2 (°C)</td><td>Spring</td><td>14.47</td><td>13.49</td><td>2.03</td><td>-0.98</td><td>0.96</td><td>2.26</td></tr><tr><td>Summer</td><td>25.31</td><td>24.41</td><td>1.72</td><td>-0.90</td><td>0.95</td><td>2.21</td></tr><tr><td>Fall</td><td>14.49</td><td>12.79</td><td>2.43</td><td>-1.70</td><td>0.92</td><td>2.45</td></tr><tr><td>Winter</td><td>3.04</td><td>1.86</td><td>2.67</td><td>-1.18</td><td>0.94</td><td>3.28</td></tr><tr><td>Year</td><td>14.32</td><td>13.06</td><td>2.47</td><td>-1.26</td><td>0.95</td><td>2.59</td></tr><tr><td rowspan="5">DSW (W m-2)</td><td>Spring</td><td>200.80</td><td>232.92</td><td>37.09</td><td>-32.12</td><td>0.83</td><td>72.36</td></tr><tr><td>Summer</td><td>229.85</td><td>273.46</td><td>52.33</td><td>-43.61</td><td>0.75</td><td>84.15</td></tr><tr><td>Fall</td><td>137.93</td><td>162.18</td><td>30.85</td><td>-24.25</td><td>0.86</td><td>60.52</td></tr><tr><td>Winter</td><td>108.30</td><td>127.68</td><td>23.72</td><td>-19.38</td><td>0.92</td><td>42.28</td></tr><tr><td>Year</td><td>169.18</td><td>199.06</td><td>36.00</td><td>-29.88</td><td>0.84</td><td>62.83</td></tr></table>

ME: mean error; MB: mean bias; RMSE: root mean square error.

and mainly concentrated in southern China due to the relatively dense vegetation cover in southern China. Additionally, decreasing temperature and solar radiation from south to north contribute to the distribution of isoprene emissions in southern China. In summer, eastern China has high temperatures, intense radiation and vigorous forest growth, subsequently resulting in obviously higher BVOC emissions. Except for Inner Mongolia, which is dominated by grassland desert, the monthly emission intensities of isoprene and terpene are  $30 \times 10^{6} \mathrm{~g}/$  month or higher in most areas. Due to dieback of vegetation and the

presence of snow cover in winter, which cause the LAI to sharply decrease, the emissions of isoprene and terpene are relatively low (generally below  $4 \times 10^{6} \mathrm{~g} / \mathrm{month}$ ), especially in the northeastern region, where temperate deciduous forests are dominant.

Fig. 6 illustrates the different monthly evolution patterns of BVOC emissions in China. BVOC emissions are concentrated between April and September and reach a maximum of  $5.8\mathrm{Tg}$  in June. As seasons transit, accompanied by a decrease in temperature, radiation and vegetation cover, the emissions intensity of BVOC drops sharply and reaches a minimum of  $23\mathrm{Tg}$  in December. The monthly isoprene emissions oscillated between the maximum  $(3.56\mathrm{Tg})$  in July and the minimum  $(0.09\mathrm{Tg})$  in December. The monthly emissions of monoterpene are similar to those of isoprene, which reach a peak of  $0.64\mathrm{Tg}$  in July and a bottom of  $0.05\mathrm{Tg}$  in December. It is noteworthy that the relative contribution of isoprene to monthly total BVOC emissions ascends from January to July and descends from July to December, while terpene and sesquiterpene do not exhibit this characteristic and their seasonal changes are not as obvious as that of isoprene. Therefore, we can reach a conclusion that isoprene is more sensitive than terpene and sesquiterpene to seasonal changes.

# 3.4. Impact of BVOC emissions on summertime  $O_3$  and SOA formation in 2017

Since the control of precursors can only be directed at anthropogenic rather than biogenic emissions, it is of great importance to understand how biogenic emissions interact with anthropogenic

Table 3 Comparison of previous BVOC emission estimations in China (unit:  $\mathrm{Tgyr^{-1}}$  

<table><tr><td>Method</td><td>Area</td><td>ISOP</td><td>TERP</td><td>OVOCs</td><td>Total BVOCs</td><td>Year(s)</td><td>Reference</td></tr><tr><td>MEGAN</td><td>China</td><td>13.3</td><td>3.09</td><td>7.15</td><td>23.54</td><td>2017</td><td>This study</td></tr><tr><td>MEGAN</td><td>China</td><td>15</td><td>4.3</td><td>9.1</td><td>28.4</td><td>1990</td><td>Guenther et al. (1995)</td></tr><tr><td>MEGAN</td><td>China</td><td>4.1</td><td>3.5</td><td>13</td><td>20.6</td><td>2000</td><td>Klinger et al. (2002)</td></tr><tr><td>MEGAN</td><td>China</td><td>7.45</td><td>2.23</td><td>3.14</td><td>12.83</td><td>2003</td><td>Chi and Xie (2011)</td></tr><tr><td>MEGAN</td><td>China</td><td>20.7</td><td>4.9</td><td>13.5</td><td>42.5</td><td>2003</td><td>Li et al. (2013)</td></tr><tr><td>MEGAN</td><td>China</td><td>7.7</td><td>3.16</td><td>\</td><td>\</td><td>2004</td><td>Tie et al. (2006)</td></tr><tr><td>MEGAN</td><td>China</td><td>9.36</td><td>3.61</td><td>\</td><td>12.97</td><td>2006</td><td>Li et al. (2012)</td></tr><tr><td>MEGAN</td><td>China</td><td>9.59</td><td>2.83</td><td>\</td><td>\</td><td>2001-2006</td><td>Yu and Hong (2012)</td></tr></table>

OVOCs: other VOCs.

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/ee507cff-688b-41b8-9b9a-13c820585331/d505089ad225034c399ae7b7345d3846eb9301fc05b135a21a98d52f14253e6a.jpg)

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/ee507cff-688b-41b8-9b9a-13c820585331/79b9a4db18536e87442ca88e1cb2377474c8b49d37144110d70073e129e7e975.jpg)

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/ee507cff-688b-41b8-9b9a-13c820585331/593087c0d6942e3211213c0afaaac76701c4dd79f71581b4752b06f4785e2358.jpg)  
Fig. 4. Annual emissions of isoprene, terpene, other VOCs and total BVOCs in 2017.

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/ee507cff-688b-41b8-9b9a-13c820585331/8ee950b8ff946cdd5415d31558e94b4343f6dba9c09453fba253acdc2aff278e.jpg)

emissions and contribute to air quality that is below national standards. Therefore, to further investigate the influence of BVOC emissions on SOA and ozone in China, we performed three parallel CMAQ simulations, the first of which included both anthropogenic and biogenic emissions, while the NB case only considered anthropogenic emissions to quantify the effects of BVOC emissions on ground-level ozone in the real atmosphere, and the NA case excluded anthropogenic emissions to reflect a clean atmosphere (see Fig. S5 in supporting information).

Fig. 7a-c shows the simulated and observed daily 1-h maximum  $\mathrm{O_3}$ $(\mathrm{DM1O_3})$  concentration over China in July 2017. In general, the model successfully captured the spatial pattern over the simulated domain with highest  $\mathrm{DM1O_3}$  areas centralized in the east, especially in the BTH, PRD, YRD and SCB regions due to the relatively large  $\mathrm{NO_x}$  and VOC emission and favorable meteorological conditions for ozone formation in these areas (e.g., little rain and strong solar radiation). And model

performance of  $\mathrm{DM1O_3}$  in different regions is evaluated in Table 4. As shown in Table 4 and Fig. 7, the model well reproduced  $\mathrm{DM1O_3}$  in most cities except for slightly underestimates  $\mathrm{DM1O_3}$  concentrations in BTH, YRD, PRD and SCB. The underestimation might be caused by uncertainty of meteorological condition simulated by WRF (such as T2 and DSW discussed in Section 3.1). Besides, the relatively coarse spatial resolution in the model and underestimation of anthropogenic emissions in these megacities may also contribute to the underestimation.

As shown in Fig. 7d-e, ozone concentration simulated by NB case is significantly higher than NA case which indicated that effect of biogenic emissions on ozone concentration is less than that of anthropogenic emissions. To clarify the change in ozone concentration after removal of BVOC, Fig. 8 shows the relative difference in ozone concentration with/without BVOC emissions. The high BVOC emissions across the eastern and southwestern areas of China increased  $\mathrm{DM1O_3}$

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/ee507cff-688b-41b8-9b9a-13c820585331/885d1aab3bb197b1f090812ec83460282b3284465077ff39ed63afd769094d26.jpg)

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/ee507cff-688b-41b8-9b9a-13c820585331/8118981f7fa33a0d990952a33e7823fc04886537bf8984dd3d5e1e91488febbe.jpg)

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/ee507cff-688b-41b8-9b9a-13c820585331/b68adff69843fbd879a3700e3afd833b1d8f4f53691e3bf1cabc0d825a14e074.jpg)

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/ee507cff-688b-41b8-9b9a-13c820585331/2477be1797b46485c2259ad9e34b1002bfc2965550fb58f8119084b4a889b267.jpg)

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/ee507cff-688b-41b8-9b9a-13c820585331/c1c8b4d01c3cbf89da8988501b286fa69a5adf15ecd7597839111d9323bb6115.jpg)

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/ee507cff-688b-41b8-9b9a-13c820585331/d5a7ea490932b9ee4cdadc8b8361e4776022f458af4c87cc0fbc74198caa97e2.jpg)

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/ee507cff-688b-41b8-9b9a-13c820585331/17b39af0bd9196447d2c6a081c473e5cc56eee9d45aec8fc28aafecfcfe9e5ca.jpg)

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/ee507cff-688b-41b8-9b9a-13c820585331/bc20274c6af462e270233e4142a699aad5c63a9a544fd637232a321aab06f8da.jpg)

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/ee507cff-688b-41b8-9b9a-13c820585331/82aa4d6fb74ac2b44b6c505ccdc80f5d69b57bb373f5c6ae764b3ba1aede5e5c.jpg)

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/ee507cff-688b-41b8-9b9a-13c820585331/b0d570b246d13e5c38123669052e180b6dbc124677e5388fa4b3380c65e61f2c.jpg)

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/ee507cff-688b-41b8-9b9a-13c820585331/9fef4a185f5d8065472d65f4d5a0927767ea40017b26cf28611095d8610ffe30.jpg)

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/ee507cff-688b-41b8-9b9a-13c820585331/31948ac590ebf9cc795cb2ddace5c0384d7e01724df66a7cb1ba1d54c3c5248d.jpg)

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/ee507cff-688b-41b8-9b9a-13c820585331/487ec84184b1b0ca69615d8f012e425f9cc0da38078bc7ee765c64898a720868.jpg)

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/ee507cff-688b-41b8-9b9a-13c820585331/1a4ec8048fbf396826d39cd8d5643cbea0372b01fe09fe20f9ae55a469bb75f2.jpg)  
Fig. 5. Monthly BVOC (four types) emissions in China in 2017.

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/ee507cff-688b-41b8-9b9a-13c820585331/b635521a02186821a13c899a7195451d5cd57b6ed624fbc2e055eef432c89b13.jpg)

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/ee507cff-688b-41b8-9b9a-13c820585331/7f1f18fc12e273cde72e46f0b7de39ca943bd2b5978826fce4694c2c5416e7ff.jpg)

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/ee507cff-688b-41b8-9b9a-13c820585331/c1741f8a32a3052d7ae52e6ace81320aa56821d19f9555c93c1d7f949f57ce28.jpg)  
Fig. 6. Seasonal emissions of isoprene, terpene, other VOCs and total BVOCs in 2017.

particularly in BTH, YRD, SCB and central PRD, by up to  $47\mu \mathrm{g}\mathrm{m}^{-3}$ . This phenomenon is likely due to the combined effects of BVOC emissions and  $\mathrm{O_3 - NOx - VOC}$  sensitivity in these regions. As shown in Fig. 5,

the major source of BVOCs in July is isoprene and terpene, which are most abundant in summer (discussed in Section 3.3). In addition, Jin and Holloway (2015) reported that the NOx-limited regime is dominant in southern China and that northern China is dominated by VOC-limited and transitional regimes (see Fig. S4 in the Supporting Information). In areas (especially rural areas) where NOx is limited but VOC emissions are already abundant, biogenic emissions have little effect on ozone formation; in areas where VOC emissions are low, however, mounting VOC emissions (i.e., inclusion of biogenic emissions) will result in more ozone formation.

Fig. 9 presents the SOA concentrations simulated by base case, NA and NB case, respectively. In summer, SOA concentrations in central and eastern China typically exceed  $1\mu \mathrm{g}\mathrm{m}^{-3}$  and can reach up to  $3\mu \mathrm{g}\mathrm{m}^{-3}$ . There is also a relatively high SOA concentration in other southern provinces and the Sichuan Basin. The simulated SOA concentrations are low in northern and northeastern China. Removing anthropogenic VOC emissions in July causes a decrease of SOA in major areas by relative change of approximately  $60\%$  while eliminating biogenic emissions results in an approximately  $70\%$  reduction of the simulated SOA concentrations. Therefore, the removal of biogenic emissions affects both biogenic and anthropogenic compounds of SOA.

As shown in Fig. 10, biogenic emissions are the most important contributors to SOA in summer. In China, biogenic emissions account for approximately  $70\%$  of SOA. In most areas, biogenic emissions are the most crucial contributors; even in areas where there are no significant isoprene emissions, the relative contribution of biogenic

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/ee507cff-688b-41b8-9b9a-13c820585331/be92d643c12bb18be9cfbd0f8085718b4e3074a02f630f38ab7c9318408b1bf1.jpg)  
(a)  $\mathbf{O}_3$  simulated by base case in July

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/ee507cff-688b-41b8-9b9a-13c820585331/1ff76482e158769ae948ad59d0ba33364dcd19fb1bb4f6e4a66e9a51d2a63b14.jpg)  
(b) Observation

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/ee507cff-688b-41b8-9b9a-13c820585331/6f0f3787de15af61cf0a3816145676170bb2b3b93fed8a0d2c60140d1f99e527.jpg)  
(c) Simulation  
(e)  $\mathrm{O}_3$  simulated by NA case in July

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/ee507cff-688b-41b8-9b9a-13c820585331/580f5caa82424137077ffe3b6e3adfd058c23841212a57fdc7194d80cf54eb8a.jpg)  
(d)  $\mathrm{O}_3$  simulated by NB case in July

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/ee507cff-688b-41b8-9b9a-13c820585331/9eb4a75f2fe2964e262ed7c7c751835c853f36b2782bf5dfb6809e29649b7964.jpg)  
Fig. 7. Observed and simulated monthly average of the daily 1-h maximum  $\mathrm{O_3}$  concentrations ((Base case: anthropogenic emissions + biogenic emissions; NB case: only anthropogenic emissions; NA case: only biogenic emissions,  $\mu \mathrm{g} \mathrm{m}^{-3}$ ).

Table 4 Model performance on  $\mathrm{DM1O_3}$  in different regions during July 2017 (Units:  $\mu \mathrm{g}$ $\mathrm{m}^{-3}$ ).  

<table><tr><td></td><td></td><td>BTH</td><td>YRD</td><td>PRD</td><td>SCB</td><td>Other</td><td>China</td></tr><tr><td rowspan="5">O3-1h</td><td>Obs.</td><td>198.2</td><td>170.5</td><td>110.4</td><td>185.6</td><td>137.6</td><td>160.5</td></tr><tr><td>Sim.</td><td>173.1</td><td>156.3</td><td>102.3</td><td>173.4</td><td>124.6</td><td>145.9</td></tr><tr><td>MB</td><td>-25.1</td><td>-14.2</td><td>-8.1</td><td>-12.2</td><td>-13.0</td><td>-14.6</td></tr><tr><td>ME</td><td>27.3</td><td>16.2</td><td>10.2</td><td>14.4</td><td>16.7</td><td>18.1</td></tr><tr><td>r</td><td>0.82</td><td>0.85</td><td>0.92</td><td>0.90</td><td>0.87</td><td>0.86</td></tr></table>

emissions to SOA formation is as high as  $80\%$  (Hu et al. 2017; Wang et al. 2018). In addition, due to the influence of the summer monsoon, precursors from high biogenic emissions in southern China are transported to central and northern China. High temperatures and intense solar radiation in summer enhance biogenic VOC emissions and photochemical generation of SOA, resulting in high national contributions of biogenic emissions to the formation of SOA. Xu et al. (2015) showed that monoterpene-derived SOA are mediated by  $\mathrm{SO}_2$  and NOx. By providing an absorptive organic mass, the biogenic compounds of particles facilitate the condensation of anthropogenic compounds. The

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/ee507cff-688b-41b8-9b9a-13c820585331/60e3af9c0971a2942f332786444ee587d7ed32819540111c214c9101311005e6.jpg)  
Fig. 8. Relative difference between the surface  $\mathrm{O}_3$  averaged in July with and without biogenic emissions (monthly average of the daily 1-h maximum,  $\mu \mathrm{g} \, \mathrm{m}^{-3}$ ).

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/ee507cff-688b-41b8-9b9a-13c820585331/5f5f94289697e46f174d107af6a74f1493d04d75a0f6d1e5052f92d5b8df192e.jpg)  
Fig. 9. Spatial distribution of SOA simulations in July 2017 (Base case: anthropogenic emissions + biogenic emissions; NB case: only anthropogenic emissions; NA case: only biogenic emissions).

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/ee507cff-688b-41b8-9b9a-13c820585331/ea1de31261398ddb436580cebd39d3f9ae9f4bb49a2e41b11ab71844dc5d9153.jpg)

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/ee507cff-688b-41b8-9b9a-13c820585331/aa13d4e69aa402c336ff4f18773730c0dc00fd5c60e7a06707dde75b9103942b.jpg)

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/ee507cff-688b-41b8-9b9a-13c820585331/7271c1f0a6fb4f03e1a9aebc35ae1ae0298fc9051be34962636548ed0de35a69.jpg)  
Fig. 10. Relative difference between the SOA concentrations averaged in July with and without biogenic emissions  $(\mu \mathrm{g}\mathrm{m}^{-3})$

SOA yield of the oxidized products of monoterpene and isoprene can be enhanced at high NOx concentrations, favoring the formation of organic nitrate, which is a low-volatility product and is likely to partition into seed particles. When the NOx level is low, isoprene oxidation occurs via the ISOPOOH pathway to form IEPOX-SOA, which favorably forms organic sulfate in acidic environments. This reaction has been incorporated into CMAQ; thus, the inclusion of both anthropogenic and biogenic emissions reflects these products, but including only one of them is unable to account for their reaction.

# 3.5. Discussion of uncertainties in model driving variables

The meteorological parameters, emission factors and parameterization method are essential driving variables for MEGAN and the uncertainties of estimated BVOC emissions and their corresponding impacts on surface ozone and SOA are related with uncertainties in these inputs (Hogrefe et al. 2011; Jiang et al. 2019). In this part, we discussed the uncertainties to better understand the results and improve future research directions.

# 3.5.1. Meteorological parameters

The WRF model performance in this study was comparable to other studies (Wang et al., 2014; Hu et al. 2016; Zhang et al., 2012). Although we employed four-dimensional data assimilation for improving model performance, some meteorological parameters are still biased. For

example, the WRF model underestimated T2 and DSW, especially in summer. On the one hand, considering the significant impact of solar radiation and temperature on photochemical reaction, underestimation of T2 and DSW may lead to corresponding underestimation on BVOC emission and ozone. On the other hand, it may cause underestimation on SOA because it is expected to form more SOA due to higher VOCs emissions and higher atmospheric reactivity during summer. Therefore, improvements on WRF model capability are urgently needed for accurate BVOC estimation.

# 3.5.2. Parameterization method

It has been reported that soil moisture could impact biogenic emissions and subsequent ozone concentrations (Wang et al. 2017; Jiang et al., 2018). In our study, soil moisture is simulated by using Noah Land Surface Model parameterization in WRF. And the reduction of isoprene emissions due to potential soil moisture limitation was not considered because MEGAN 2.1 simplified soil moisture's impact on BVOC estimation. Hence, soil moisture's impact on BVOC estimation should be considered by further detailed parameterization method in future research.

# 4. Conclusion

In this study, we utilized MEGAN to estimate the BVOC emissions in 2017 throughout China, then further applied the WRF-CMAQ model to

quantify the contributions of BVOCs to surface ozone and SOA formation in China in July 2017. BVOC emissions in China were estimated to be  $23.54\mathrm{Tg}$  in 2017, decreasing from south to north, which is related to the vegetation distribution. Additionally, BVOC emissions exhibited strong seasonal variations due to changes in temperature and solar radiation, with the highest emissions in summer.

Ozone concentrations mainly peaked in the eastern and southwestern China, particularly in the BTH, YRD, PRD and SCB regions because of their considerably large NOx and VOC emission sources and advantageous meteorological conditions for ozone formation. Even though the effect of biogenic emissions on  $\mathrm{O_3}$  is less profound than that of anthropogenic emissions (as shown in Fig. 7(d)(e)), the BVOC emissions still made a significant contribution to summertime ozone due to the influence of the southerly wind, transporting precursors from high biogenic emission regions in southern China to central China and the BTH area. And the regions where the influence of biogenic emissions is high match with those where ozone formation is VOC limited.

BVOC emissions make a large contribution to summertime SOA (national average of  $70\%$ ). Locally, the effects of biogenic emissions tend to be greater in the southern region than in the northern region, as the megacities are surrounded by regions of high biogenic emissions. In summer, the impact of biogenic emissions on SOA is much greater than that of anthropogenic emissions. However, the impact of anthropogenic emissions in individual regions may be rather high (up to  $50\%$ ), indicating that even BSOA can be significantly controlled by limiting anthropogenic emissions. When anthropogenic emissions are not considered, the reduction in BSOA depends on the chemical precursor. In particular, isoprene SOA is more easily reduced than monoterpene SOA due to their different volatilities. ASOA are also affected by biogenic emissions (the absorption of organic matter by SOA), and the relative impact may be as high as  $40\%$ . In order to accurately simulate SOA, it is necessary to precisely simulate both ASOA and BSOA (Pye et al. 2019).

It should be noted that the simulated SOA concentrations in this study have not been compared with direct measurements of organic particulate matter and SOA because of the data limitations. Extensive measurements of organic components have been conducted in megacities and major clusters in China by aerosol mass spectrometers (AMS), which provides details about various organic aerosols (Hu et al. 2016; Yang et al., 2016). And these data can be used as model validation for future local scale SOA modeling studies which can promote the understanding of SOA formation. Besides, a great deal of additional research is needed to further address the remaining questions. For example, to better quantify the separate and synergistic effects of anthropogenic and VOC emissions based on sensitivity testing, it is necessary to investigate the spatial distribution of ozone changes by comparing NOx and VOC emissions. Both chamber studies and field measurements have shown that HOMs (highly oxygenated molecules) can substantially increase the SOA mass because of their low volatility (Ehn et al. 2014). This mechanism has already been incorporated into box models (Öström et al. 2017) with detailed chemistry, and it would be interesting to observe the impact of this mechanism on SOA formation from BVOCs at the regional scale.

# Author contributions

The manuscript was written through contributions of all authors. All authors have given approval to the final version of the manuscript.

# Acknowledgements

This work was funded by the National Key Research and Development Program of China (No.2018YFC0214002), the Basic Applied Research Project of Science and Technology Plan of Sichuan Province (No.2018JY0011), the Key Project of Science and Technology Plan of Sichuan Province (No.2018SZDZX0023) and the Scientific Research Foundation of Chengdu University of Information Technology

(No.KYTZ201731 and KYTZ201814). The meteorological dataset was provided by the China Meteorological Data Sharing Service System (http://cdc.cma.gov.cn). Additionally, the air pollutant data were downloaded from the National Urban Air Quality Real-time Publishing Platform (http://106.37.208.233:20035/). The datasets generated during and/or analyzed in this study are publicly available as referenced within the article. All data and scripts are available from the corresponding author upon request.

# Appendix A. Supplementary data

Supplementary data to this article can be found online at https://doi.org/10.1016/j.atmosres.2019.104656.

# References
