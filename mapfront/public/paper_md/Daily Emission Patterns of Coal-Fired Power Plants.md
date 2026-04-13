pubs.acs.org/environmentau

Article

# Daily Emission Patterns of Coal-Fired Power Plants in China Based on Multisource Data Fusion

Nana Wu, Guannan Geng, Xinying Qin, Dan Tong, Yixuan Zheng, Yu Lei, and Qiang Zhang*

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/1eeb6f00-7c02-4c45-a22c-6331c7792747/55a02356e7c88e74101594822a1bd384421e4683487e82da63d2f0cb407b9e3d.jpg)

Cite This: ACS Environ. Au 2022, 2, 363-372

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/1eeb6f00-7c02-4c45-a22c-6331c7792747/0468886798a01b082795d89db8c086e6183fd9c720135f572a376e826ad7d6a7.jpg)

Read Online

ACCESS

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/1eeb6f00-7c02-4c45-a22c-6331c7792747/e62e4f13a3add44db83f589919c410b6758352dcaa05dee8d5d0ce47dc644827.jpg)

Metrics & More

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/1eeb6f00-7c02-4c45-a22c-6331c7792747/2d300afae0cd32511e9a83ddcaf0bed4eaa3153b36f4613360fd02287a34abb0.jpg)

Article Recommendations

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/1eeb6f00-7c02-4c45-a22c-6331c7792747/c4903c226d19e7cc7c02b080f3f0b3fec07623a3cde2e9c349987ec09a1e5464.jpg)

Supporting Information

ABSTRACT: Daily emission estimates are essential for tracking the dynamic changes in emission sources. In this work, we estimate daily emissions of coal-fired power plants in China during 2017-2020 by combining information from the unit-based China coal-fired Power plant Emissions Database (CPED) and real-time measurements from continuous emission monitoring systems (CEMS). We develop a step-by-step method to screen outliers and impute missing values for data from CEMS. Then, plant-level daily profiles of flue gas volume and emissions obtained from CEMS are coupled with annual emissions from CPED to derive daily emissions. Reasonable agreement is found between emission variations and available statistics (i.e., monthly power generation and daily coal consumption). Daily power emissions are in the range of 6267-12,994, 0.4-1.3, 6.5-12.0, and  $2.5 - 6.8\mathrm{Gg}$  for  $\mathrm{CO}_{2}$ ,  $\mathrm{PM}_{2.5}$ ,  $\mathrm{NO}_{x}$ , and  $\mathrm{SO}_2$ , respectively, with high emissions in winter and summer caused

by heating and cooling demand. Our estimates can capture sudden decreases (e.g., those associated with COVID-19 lockdowns and short-term emission controls) or increases (e.g., those related to a drought) in daily power emissions during typical socioeconomic events. We also find that weekly patterns from CEMS exhibit no obvious weekend effect compared to those in previous studies. The daily power emissions will help to improve chemical transport modeling and facilitate policy formulation.

KEYWORDS: emission inventory, air pollutant,  $\mathrm{CO}_{2}$ , power plant, high temporal resolution, CEMS, data fusion

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/1eeb6f00-7c02-4c45-a22c-6331c7792747/ea6968aeaa9b5bd9d85470dd125b27e4a00c2fe81229f3b0d28043db7f952955.jpg)

# 1. INTRODUCTION

Temporally resolved emission inventories are essential for atmospheric research and air quality management. [1-3] However, emissions are usually estimated at an annual scale by multiplying annual activity data by emission factors [4,5] and are then broken down into fine temporal resolutions via temporal profiles at different scales (e.g., monthly, weekly, diurnal). [1,2,4-7] Due to the lack of real-time emission measurements, the temporal profiles tend to be empirically selected weighting factors that consider temporal variations in activity rates (e.g., fuel use, production rate, and traffic counts), [8] sociodemographic patterns, [1] source characteristics, [9] or preliminary field measurements, [2] which might not always be able to capture the fluctuations in emissions, especially for those caused by unexpected socioeconomic activities or short-term control policies. Moreover, such uncertainties originating from temporal disaggregation of emissions could further propagate into chemical transport models (CTMs). [3,10-13]

The power sector is the largest energy infrastructure in China, whose energy consumption has surged in the past few decades,[14,15] leading to approximately one-third of China's  $\mathrm{CO}_{2}$  emissions in recent years.[5,16] Efforts have been made to improve the temporal resolution of power emissions in China. For example, monthly scale electricity generation adjusted by the commissioned or decommissioned state of each power unit

is used to quantify monthly variations in power emissions in a unit-level power plant emission inventory in China.17 Indicator data such as power load curves are employed to indicate daily or hourly dynamics of power emissions.1,18 Recent studies have also attempted to estimate dynamically updated daily power emissions,19-22 which are largely stimulated by the demand for quantifying the evolution of emissions during fast-evolving events (e.g., COVID-19 pandemic). Liu et al.19,20 used daily coal consumption from six major power generation groups in China to estimate daily updated power emissions. However, the daily coal consumption data only covers 62 power plants in China, and the activity indicator-based method is relatively indirect and lacks independent evaluations against observations. Studies utilizing satellite observations to estimate daily emission changes are faced with the challenges of differentiating power emissions from the total21,23 or deriving daily power emissions on continuous time scales.24,25 For example, Ding et al.23 used the  $\mathrm{NO}_x$  emission reductions derived from

Received: March 12, 2022

Revised: May 3, 2022

Accepted: May 4, 2022

Published: May 17, 2022

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/1eeb6f00-7c02-4c45-a22c-6331c7792747/abb477d739194b0f955e7035a16b525f54480146c2ca5a88f4a54cca34cc7fa5.jpg)

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/1eeb6f00-7c02-4c45-a22c-6331c7792747/7fd7a76271def16a21b5f186c41b15e704f5fe6319a344775131d922b317fbe1.jpg)  
Figure 1. Methodology framework for fusing multisource data to derive daily emission estimates of coal-fired power plants in China.

satellite observations of a power-dominated province to represent national changes caused by power plants during the COVID-19 lockdown, which might introduce additional uncertainties.

In the past decade, the Chinese government has mandated that key polluting power plants must install the continuous emission monitoring systems (CEMS) to provide real-time measurements of pollutants (e.g.,  $\mathrm{NO}_x$ ,  $\mathrm{SO}_2$ , and PM) and operational status of end-of-pipe control devices.[26,27] In developed countries such as the United States and Canada, independently verified power emission rates from CEMS[28,29] have been incorporated into emission estimations (e.g., the National Emission Inventory)[28,30] and used to investigate the long-term or short-term trends of air pollution.[31-33] In addition, temporal profiles obtained from CEMS have been applied to the temporal disaggregation of annual emission totals before being input to CTMs.[2,34] However, due to the late start and quality concerns[26,35] of CEMS in China, the fusion of CEMS data into emission estimates is rare.

Recent studies estimated power emissions based on time-varying emission factors derived from CEMS and statistical activity data,[36,37] or through the mathematical product of measured concentration and flue gas volume from CEMS.[38-42] Power emissions measured directly by CEMS in China generally deviate from other power emission databases that were based on statistical data and average emission factors[36-39,42] whose emission magnitude and trends have been validated against satellite measurements and were proven to be reliable.[43-46] For example, Tang et al.[36,37] found that emission estimates based on CEMS from 2014 to 2017 are considerably lower (19–92%) than other emission inventories. The quality of CEMS data is largely untested in existing studies and some works have reported possible downward biases in China.[26,35] In this case, using high-temporal-resolution profiles from CEMS to improve the temporal resolutions of emission inventories might be more reasonable than directly using emissions derived from CEMS data.[47-49]

In this work, taking advantage of a well-validated unit-based power emission database covering China and the high temporal resolution of CEMS data, we attempt to construct daily emission estimates of coal-fired power plants in China based on multisource data fusion. Careful screening of outliers and imputation of missing values are conducted for the flue gas volume and emission data. Then, the plant-level daily profiles (i.e., coefficients for day-to-day variations in a year) from CEMS are combined with the unit-level annual emissions from

the China coal-fired Power plant Emissions Database (CPED)[15,17] to achieve daily scale estimation.

# 2. DATA AND METHODS

Figure 1 shows the methodology framework in this study, including the input database and processes to fuse multisource data to derive daily emission estimates of coal-fired power plant emissions.

# 2.1. Multisource Input Data

2.1.1. Unit-Level Emission Database of Coal-Fired Power Plants in China. The CPED, $^{17}$  developed by Tsinghua University, is a high-resolution emission inventory that provides year-by-year emissions from coal-fired power plants since 1990 in China. Established based on detailed and unit-level information from the Ministry of Ecology and Environment (MEE, undisclosed data), CPED contains unit locations, operational status, unit capacity, coal consumption, control technologies, and emission factors, which enable accurate spatial allocation and emission estimates for power plants. More details about CPED can be found in the paper by Liu et al. $^{16}$  Previous studies have verified that the magnitude and trends of power emissions in CPED are in good agreement with top-down estimates from satellite measurements. $^{43,50}$  Liu et al. $^{43}$  compared  $\mathrm{NO}_x$  emissions in CPED with those based on satellite data and found rather good agreement with the relative differences of  $4 \pm 18\%$ . CPED used here covers 30 provinces (except Hong Kong, Macao, Taiwan, and Tibet), 3948 power plants, and 8722 in-use electricity-generating units from 2017 to 2020.

2.1.2. Stack-Level Measurements of Power Emissions by CEMS. The CEMS network in China is managed by the Environment of supervision center of ministry of Ecology and Environment (http://www.envsc.cn/). CEMS provides basic information (e.g., locations and sector) and stack-level hourly data (e.g., emission rates of  $\mathrm{NO}_x$ ,  $\mathrm{SO}_2$ , and PM, flue gas flow, oxygen content), which are valuable for fine temporal-scale emission estimations. The CEMS dataset used here covers 30 provinces (except Hong Kong, Macao, Taiwan, and Tibet), 3146 power plants, and 5768 stacks during 2017-2020. It is worth noting that the CEMS dataset contains outliers and missing values, although a series of technical guidelines (e.g., HJ/T 75-2017,[51] HJ/T 76-2017,[52] and HJ/T 373-2007[53]) have been issued to guide the installation, operation, and management of CEMS.

# 2.2. Combining CPED and CEMS to Obtain Unit-Level Daily Emissions

In this work, we develop a framework that fuses plant-level daily profiles from CEMS with yearly emission estimates from CPED to obtain daily emissions (Figure 1). According to guideline HJ/T 75-2017, the maximum volume fraction of  $\mathrm{CO}_{2}$  emissions from the combustion of specific fuels remains stable, so we use daily profiles of flue gas volume that takes the oxygen content into account to describe daily variations in  $\mathrm{CO}_{2}$  emissions. Daily profiles of emission rates from CEMS are used for major air pollutants of  $\mathrm{SO}_{2}, \mathrm{NO}_{x},$  and  $\mathrm{PM}_{2.5}$ .

Table 1. Summary of the Power Plants in the CPED Database Equipped with  ${\mathrm{{CEMS}}}^{a}$  

<table><tr><td rowspan="2">year</td><td rowspan="2">number of plants</td><td rowspan="2">total installed capacity (MW)</td><td colspan="4">emissions (Gg)</td></tr><tr><td>SO2</td><td>NOx</td><td>PM2.5</td><td>CO2</td></tr><tr><td>2017</td><td></td><td></td><td>1912 (94.9%)</td><td>3501 (95.7%)</td><td>356 (94.6%)</td><td>3,472,528 (98.1%)</td></tr><tr><td>2018</td><td>3119 (79.0%)</td><td>1,065,758 (96.4%)</td><td>1665 (94.4%)</td><td>3351 (95.3%)</td><td>262 (96.7%)</td><td>3,635,448 (98.1%)</td></tr><tr><td>2019</td><td></td><td></td><td>1348 (93.3%)</td><td>3198 (95.2%)</td><td>224 (98.5%)</td><td>3,650,556 (98.1%)</td></tr><tr><td>2020</td><td></td><td></td><td>1213 (92.7%)</td><td>3025 (95.0%)</td><td>203 (98.5%)</td><td>3,623,965 (98.1%)</td></tr></table>

${}^{a}$  Numbers in brackets represent the fraction of data in CPED.

2.2.1. Mapping Power Plants in CPED with Those in CEMS. The power plants in CPED are paired with those in CEMS and then categorized into two groups: enterprises equipped with or without CEMS. Although only  $79.0\%$  of the total number of power plants in CPED could be matched with those in CEMS, they occupy  $96.4\%$  of the total installed capacity, and 94.0, 95.3, 96.7, and  $98.1\%$  of  $\mathrm{SO}_2$ ,  $\mathrm{NO}_x$ ,  $\mathrm{PM}_{2.5}$ , and  $\mathrm{CO}_2$  emissions in the CPED during 2017-2020, respectively (Table 1).

2.2.2. Preprocessing of CEMS Data. We remove outliers and impute the missing values of flue gas volume and emission rates from CEMS before calculating daily temporal profiles. Outliers including negative values, zeros that are not recorded as outage status, and extremely high values are all excluded. Extremely high values are defined as those exceeding the theoretical maximum values per hour, which are determined by the uncontrolled emission factors, installed capacity, coal consumption per unit of electricity generation, and theoretical flue gas volume per unit of coal consumption (see details in the Supporting Information). Data missing in CEMS include nulls in discrete hours and successive nulls lasting for several hours or days owing to malfunction or abnormal conditions in the management and operation of CEMS (e.g., invalid data communication).

Then, we use a stepwise method to impute the missing data, considering the length of missing periods: (1) Imputation is first conducted at the hourly scale and stack level. The missing hourly data are linearly interpolated when the missing periods are less than  $6\mathrm{h}$ . Then, daily mean values are calculated for days with more than 12 valid hourly records. (2) Subsequently, the imputation is performed at the daily scale. Average data on the same day of week or weekdays/weekends in the same month are applied for each stack (eq 1)

$$
V _ {\text {s t a c k}, y, m, d} ^ {\prime} = \frac {1}{n} \sum_ {i = 1} ^ {n} V _ {\text {s t a c k}, y, m, d _ {i}} \tag {1}
$$

where  $V_{stack,y,m,d}^{\prime}$  refers to the imputed variables (i.e., flue gas volume or emission rates) of stack stack for year  $y$  in month  $m$  on day  $d$ ;  $V_{stack,y,m,d,i}$  represents the corresponding measured variables on day  $d_i$  from CEMS; and  $d_i$  denotes the selected days used to fill the gaps in missing data on day  $d$ , which are preferably the same day of week in the same month or weekdays/weekends when data on a certain day of week are all missing. For example, weekday average emissions in September 2020 are used to interpolate the missing Monday's data in this month since the four Mondays' data are all unavailable. (3) If eq 1 is still not workable, a method similar to step (2) but using data from the other 3 years is implemented, considering the interannual changes in coal consumption or emissions of the corresponding plant from CPED (eq 2)

$$
V _ {s t a c k, y, m, d} ^ {\prime} = \frac {\sum_ {k = 1} ^ {3} \sum_ {i = 1} ^ {n _ {k}} V _ {s t a c k , y _ {k} , m , d _ {i}}}{\sum_ {k = 1} ^ {3} n _ {k}} \times \frac {\nu_ {p l a n t , y}}{\frac {1}{3} \times \sum_ {k = 1} ^ {3} \nu_ {p l a n t , y _ {k}}} \tag {2}
$$

where  $V_{\text{stack},y_k,m,d_i}$  represents the measured variables of stack stack for the other 3 years  $y_k$  in month  $m$  on day  $d_i$  from CEMS;  $\nu_{\text{plant},y_k}$  is the annual coal consumption (for  $V =$  flue gas volume) or emissions (for  $V =$  emission rates) from stack stack's corresponding plant plant for the other 3 years  $y_k$  from CPED. Due to insufficient information to pair the stack in CEMS with the unit in CPED, we use plant-level rather than unit-level data from CPED to describe the interannual

changes. (4) If step (3) is not feasible, average data from other plants with similar installed capacity in the same province are used (eq 3)

$$
V _ {\text {s t a c k}, y, m, d} ^ {\prime} = \frac {1}{n} \sum_ {i = 1} ^ {n} V _ {\text {s t a c k} _ {i}, y, m, d} \times \frac {v _ {\text {p l a n t} , y}}{\frac {1}{q} \sum_ {p = 1} ^ {q} v _ {\text {p l a n t} p , y}} \tag {3}
$$

where  $V_{\text{stack}_i y, m, d}$  denotes the measured data from other stacks whose corresponding plants have similar installed capacity in the same province for year  $y$  in month  $m$  on day  $d$ ;  $\nu_{\text{plant}_p y}$  refers to the annual coal consumption (for  $V =$  flue gas volume) or emissions (for  $V =$  emission rates) from stack  $\text{stack}_i$ 's corresponding plant  $\text{plant}_p$ . For the imputed variables during 2017-2020, the imputed periods by steps (2), (3), and (4) account for 3.1-5.5, 6.3-9.1, and 2.6-5.2% of the total days, respectively. (5) As existing information does not support the mapping of stacks from CEMS with units in CPED, plant-level rather than stack-level daily profiles from CEMS will be used for daily emission estimations. Therefore, data from stacks in the same plant are aggregated to the plant level, as depicted in eq 4

$$
V _ {\text {p l a n t}, y, m, d} = \sum_ {\text {s t a c k} _ {i} \in \text {p l a n t}} V _ {\text {s t a c k} _ {i}, y, m, d} \tag {4}
$$

The above step-by-step imputation method might lead to uncertainties, which are quantified by two sensitivity tests via different imputation methods (see Section 4.2).

2.2.3. Estimation of Daily-Resolved Unit-Level Emissions. We assume that units in the same plant from CPED exhibit similar daily variations. For power plants equipped with CEMS, the daily unit-based emissions are derived by multiplying the unit-level annual emissions from CPED by corresponding plant-level daily profiles from CEMS (eq 5)

$$
e _ {u n i t, y, m, d} = e _ {u n i t, y} \times \frac {V _ {\text {p l a n t} , y , m , d}}{\sum_ {m} \sum_ {d} V _ {\text {p l a n t} , y , m , d}} \tag {5}
$$

where  $e$  represents the emission data in CPED;  $V$  is the flue gas volume (for  $\mathrm{CO}_{2}$ ) or emission rates (for  $\mathrm{SO}_{2}, \mathrm{NO}_{x},$  and  $\mathrm{PM}_{2.5}$ ) from CEMS; and the subscript unit and plant indicate the unit in CPED and its corresponding plant in CEMS. For power plants without CEMS, daily profiles from other plants with similar installed capacity in the same province are used (eq 6)

$$
e _ {u n i t, y, m, d} = e _ {u n i t, y} \times \frac {\sum_ {p = 1} ^ {q} V _ {\text {p l a n t} , y , m , d}}{\sum_ {m} \sum_ {d} \sum_ {p = 1} ^ {q} V _ {\text {p l a n t} , y , m , d}} \tag {6}
$$

where  $plant_{p}$  represents other plants with similar installed capacity in the same province.

# 2.3. Relevant Statistical Data

Provincial thermal and hydropower generation at the monthly scale from 2017 to 2020 are accessed from the National Bureau of Statistics (https://data.stats.gov.cn/). The best available daily-scale data in China are from the coal consumption reports from six major power generation groups (i.e., Zhedian, Shangdian, Yuedian, Guodian, Datang, and Huaneng), which cover 62 power plants, whose coal consumption accounted for  $12 - 13\%$  of the national total in the power sector during 2017-2020. Due to the suspension of data release around July 2020, we obtain daily coal consumption from January 1,

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/1eeb6f00-7c02-4c45-a22c-6331c7792747/828054ab67f517c2f869e64e1046f9309d40dac5ecbc282faf39a9f8a463a384.jpg)  
(a)

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/1eeb6f00-7c02-4c45-a22c-6331c7792747/8839ce96f5dc1af4a75bcc69a6363ae1a7d1f6bbebe1db55b963bf1bad72f092.jpg)  
(b)

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/1eeb6f00-7c02-4c45-a22c-6331c7792747/8e440880568a6e72f627cb6e0a67f231220a2643e2e141f667c89561fe13c940.jpg)  
(c)  
(d)

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/1eeb6f00-7c02-4c45-a22c-6331c7792747/668407a9b4f3810d65eab80bf0d49ce28cd1493330c2c5893c538381087218de.jpg)  
(g)

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/1eeb6f00-7c02-4c45-a22c-6331c7792747/5ae19d2c76c7637f1e869b7ad8b1efbdf7c8b0c757cc90dcb45dcc299f8ba4fc.jpg)  
(e)  
(f)

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/1eeb6f00-7c02-4c45-a22c-6331c7792747/ec68c59ba2ae38d51662664352699c7200652a74c2c16a1081e11c41634e6613.jpg)

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/1eeb6f00-7c02-4c45-a22c-6331c7792747/79d2e676b54be2c049512ac222bd3b3d8a70158f29d94374e19af659557ed38e.jpg)

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/1eeb6f00-7c02-4c45-a22c-6331c7792747/0cd5d1551b2ab0d76e24ea9cfc5140ab738a873f9e2e1d9725feab12db15601b.jpg)  
(h)  
Figure 2. Daily emission patterns of (a)  $\mathrm{CO}_{2}$ , (b)  $\mathrm{PM}_{2.5}$ , (c)  $\mathrm{NO}_{x}$ , and (d)  $\mathrm{SO}_{2}$  from 2017 to 2020 in China. The light orange shades represent the Spring Festival. (e–g) Maps of  $\mathrm{SO}_{2}$  emissions from power units on January 10, 2017 (the date of maximum daily  $\mathrm{SO}_{2}$  emissions during 2017–2020), July 24, 2019 (the date of maximum daily  $\mathrm{SO}_{2}$  emissions in summer of 2019), and February 9, 2020 (the date of minimum daily  $\mathrm{SO}_{2}$  emissions during 2017–2020). The size and color of the circles represent the installed capacity and  $\mathrm{SO}_{2}$  emissions, respectively. (h) Daily emission estimates of  $\mathrm{CO}_{2}$ ,  $\mathrm{SO}_{2}$ ,  $\mathrm{NO}_{x}$ , and  $\mathrm{PM}_{2.5}$  from a unit of Guangdong Guohua Taishan Power Plant from 2017 to 2020 as an example.

2017 to June 18, 2020 from the Wind Data Service (https://www. wind.com.cn/).

# 3. RESULTS

# 3.1. Comparison of Emission Variations Derived from CEMS with Relevant Activity Indicators

The fluctuation of emissions within a year is largely shaped by variations in relevant activity rates, although changes in the pollution control measures also contribute to the variations in air pollutant emissions. We compare the provincial-level monthly profiles based on monthly power generation with corresponding profiles of flue gas volume (for  $\mathrm{CO}_{2}$ ) or emission rates (for  $\mathrm{SO}_{2}, \mathrm{NO}_{x}, \mathrm{PM}_{2.5}$ ) aggregated from power unit data from CEMS 2017-2020 and find good agreement. Table S1 shows that the Pearson correlation coefficients (i.e.,  $R$ ) in most provinces (27 out of 30 for  $\mathrm{CO}_{2}$ ; 25 out of 30 for  $\mathrm{NO}_{x}$ ; 16 out of 30 for  $\mathrm{SO}_{2}$ ; and 18 out of 30 for  $\mathrm{PM}_{2.5}$ ) are greater than 0.7, which proves the reliability of monthly profiles derived from CEMS. Flue gas volume is generally in better agreement with power generation compared to emission

rates because it mainly depends on activity rates but emission rates are also affected by pollution control technology.

We further compare daily profiles of flue gas volume or emission rates with daily coal consumption from the six major power generation groups in China in which 58 out of 62 are equipped with CEMS. Figure S1 shows that they are in good agreement, and the Pearson correlation coefficients range from 0.63 to 0.82, 0.40 to 0.81, 0.48 to 0.83, and 0.38 to 0.80 for flue gas volume,  $\mathrm{SO}_2$ ,  $\mathrm{NO}_x$ , and  $\mathrm{PM}_{2.5}$ , respectively. Since the flue gas volume is not affected by emission control measures, it could better characterize the daily variations in coal consumption. Peaks and valleys (e.g., a sudden decrease during the Spring Festival) of daily coal consumption are well captured by CEMS, indicating that daily profiles from CEMS are capable of reflecting high-temporal-resolution variations in activity rates and emissions.

# 3.2. Daily Emission Patterns from the Fused Coal-Fired Emission Inventory

Figure 2a-d presents China's daily emissions of  $\mathrm{CO}_{2}$ ,  $\mathrm{PM}_{2.5}$ ,  $\mathrm{NO}_{x}$ , and  $\mathrm{SO}_{2}$  from the fused database. The  $\mathrm{CO}_{2}$  emissions

increased slightly by  $1.8\%/\mathrm{yr}$ $(1.7 - 2.0\%/\mathrm{yr})$  during 2017-2020, while major air pollutants of  $\mathrm{PM}_{2.5}$ ,  $\mathrm{NO}_x$ , and  $\mathrm{SO}_2$  decreased continuously from 2017 to 2020 with mean annual changes of  $-18.0\%/\mathrm{yr}$ $(-18.2$  to  $-17.8\%/\mathrm{yr})$ ,  $-4.8\%/\mathrm{yr}$ $(-5.0$  to  $-4.7\%/\mathrm{yr})$ , and  $-15.6\%/\mathrm{yr}$ $(-15.8$  to  $-15.5\%/\mathrm{yr})$ , respectively, demonstrating the efficacy of the ultralow emission policy. Daily power emissions are in the range of 6267-12,994, 0.4-1.3, 6.5-12.0, and  $2.5 - 6.8~\mathrm{Gg}$  for  $\mathrm{CO}_2$ ,  $\mathrm{PM}_{2.5}$ ,  $\mathrm{NO}_x$ , and  $\mathrm{SO}_2$ , respectively, with higher emissions in winter and summer caused by larger heating and cooling demand. The Spring Festival holiday (typically in January or February) and the National Day holiday (in October) are usually the times with the lowest daily power emissions within a year. For example, the largest  $\mathrm{CO}_2$  emissions were in December and August during 2017-2020, with a monthly average of  $340~\mathrm{Tg}$ ,  $33.9\%$  higher than that in October and February.

Figure 2e-g presents the unit-level  $\mathrm{SO}_2$  emission map of days with highest value during 2017-2020 (6.8 Gg) and in the summer of 2019 (3.8 Gg) and lowest value during 2017-2020 (2.5 Gg), respectively. The lowest value was contributed by the reduced human activities resulting from the Spring Festival holiday and the COVID-19 lockdown. Consistently higher  $\mathrm{SO}_2$  emissions were observed in the northwest and southwest region, which are related to factors such as high-sulfur coal and the longer implementation timeline of the ultralow emission policy. Power units with high installed capacity dominated the difference in the 3 days. Figure 2h presents an example of unit-level daily emissions during 2017-2020, which show specific temporal variation characteristics, such as the low emissions in winter caused by the shutdown of certain units in the plant.

# 3.3. Daily Emission Variations Associated with Typical Socioeconomic Events

3.3.1. Emission Estimates during COVID-19. To curb the spread of COVID-19, the Chinese government imposed stringent measures, such as locking down cities and closing factories. From January 23 to April 8, 2020, Wuhan experienced a 76-day lockdown (i.e., Wuhan lockdown) during which energy consumption and pollutant emissions were reduced drastically.[19,21,54-56] Figure 3a shows the national daily  $\mathrm{NO}_x$  emissions around the Wuhan lockdown and the same period in previous years. As the beginning of the Spring Festival is different in 2017-2020 according to the Western solar calendar, we present daily emissions based on the Chinese Lunar Calendar for direct comparisons between different years. During 2017-2019, emissions decreased during the Spring Festival holiday but soon recovered at the end of the holiday, while the rebound of emissions in 2020 was much slower owing to the continued impact of COVID-19. For example, we compare 10-day averages before Lunar New Year's Day with daily  $\mathrm{NO}_x$  emissions after the day and find that the  $\mathrm{NO}_x$  emissions exceeded the 10-day averages for the first time on Lunar January 21, 11, 8, and 42 in 2017-2020, respectively. During the Wuhan lockdown,  $\mathrm{NO}_x$  emissions in Hubei Province showed the greatest decline  $(-37.1\%)$  compared to those in the same period in 2019, while the proportion of other provinces was  $-11.3\%$  (Figure 3b,c), which was attributed to the earlier recovery of normal activities in the regions outside Hubei. Notably, the  $\mathrm{NO}_x$  emissions of Yunnan Province increased by  $9.2\%$ , owing to the decrease in hydropower generation and increase in thermal power generation caused by a drought (see Section 3.3.2).

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/1eeb6f00-7c02-4c45-a22c-6331c7792747/1d39ff86ebe8fbe3030825e004b2093cc44f9b736e829270cfe44cf8354afb9e.jpg)

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/1eeb6f00-7c02-4c45-a22c-6331c7792747/3db017c80f806b8446a25c3a49c823a5ab83f42ae3d283333e78a798c526377c.jpg)

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/1eeb6f00-7c02-4c45-a22c-6331c7792747/b1ab09dec1442b6106b9687ee93e95e563671066da70a17c84b727d5785c2120.jpg)  
Figure 3. (a) Daily variations in China's  $\mathrm{NO}_x$  emissions from coal-fire power plants around Lunar New Year 2017-2020. The dark gray shading around the blue line shows the range of daily  $\mathrm{NO}_x$  emissions during 2017-2019. The light gray shading highlights the period of the Wuhan lockdown. The  $x$ -axis represents the number of days relative to the Lunar New Year's Day. (b) Daily reductions in power plant  $\mathrm{NO}_x$  emissions in Hubei and other provinces during the Wuhan lockdown in 2020 compared to 2019. (c) Spatial distribution of the reduction rates of  $\mathrm{NO}_x$  emissions from power units in 2020 relative to 2019. The shades in each province indicate the relative differences in power  $\mathrm{NO}_x$  emissions, and the shaded circles represent the changes in  $\mathrm{NO}_x$  emissions for each power unit. Gray shading indicates no valid data.

3.3.2. Effects of a Drought on  $\mathrm{CO}_{2}$  Emissions from Thermal Power Plants in Yunnan Province. Yunnan is a major hydropower-producing province, whose hydropower generation and thermal power generation were 67.36 and 9.31 billion kWh from January to April 2019, accounting for 75.0 and  $10.4\%$  of its total power generation, respectively (http:// www.stats.gov.cn/). However, Yunnan experienced a severe drought in 2020, which reduced hydropower generation by  $28.6\%$  (to 48.12 billion kWh) and increased thermal power generation by  $75.6\%$  (to 16.35 billion kWh) compared to the

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/1eeb6f00-7c02-4c45-a22c-6331c7792747/d6b5ac183262000df064c3a71d4a6b85bb53739f6cb4de5663c7f0b9597edc2d.jpg)  
(a)

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/1eeb6f00-7c02-4c45-a22c-6331c7792747/41f97950413be61a79d98c54d9d4462c012d27199b0753236b884427d57a0808.jpg)  
(b)

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/1eeb6f00-7c02-4c45-a22c-6331c7792747/1d2c40b9d48ee75a7bdbe1b79ad47c1112c79d6a8e439e3740104c1c68adfd99.jpg)  
(c)

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/1eeb6f00-7c02-4c45-a22c-6331c7792747/326dc47b02a073ac22d76ac3f62c211d2b250f6a709fbb578cbfee839caa44b3.jpg)  
(d)  
Figure 4. Effects of a drought on  $\mathrm{CO}_{2}$  emissions from thermal power plants in Yunnan Province are presented in panels (a) and (b). The impact of emission control measures on  $\mathrm{SO}_{2}$  emissions during the 7th CISM Military World Games is shown in (c) and (d). (a) Relative changes in  $\mathrm{CO}_{2}$  emissions in Yunnan Province and other provinces from 2019 to 2020. (b) Relative changes in hydropower generation and thermal power generation in Yunnan Province from 2019 to 2020. Since January and February are usually combined in the statistical data released by the National Bureau of Statistics, they are plotted as a whole here. (c) Daily  $\mathrm{SO}_{2}$  emissions before, during, and after the emission control period in Wuhan, other cities in Hubei, and other provinces except Hubei. The light gray shading covers the periods of short-term emission control. The daily emissions are normalized to the value on October 6. (d) Relative changes in average  $\mathrm{SO}_{2}$  emissions during the emission control period compared to the periods before and after this period.

same 4 months in 2019 (Figure 4b). Daily  $\mathrm{CO}_{2}$  emissions from thermal power generation in Yunnan between January and April were  $61.2\%$  higher than the same period in 2019 (Figure 4a). However, due to the impact of COVID-19, they were reduced by  $7.8\%$  in the other provinces. The increase in coal consumption caused by the drought in Yunnan offset the reduction in activity rates resulting from the lockdown.

3.3.3. Impact of Emission Control Measures during the 7th CISM Military World Games. To ensure good air quality during great events, the government often adopts strict temporary emission control measures whose effects on emission dynamics need to be estimated. Here, we take the 7th CISM Military World Games as an example, which was held in Wuhan from October 18 to 27, 2019. From October 13, Wuhan and the surrounding cities in Hubei Province began to implement many air quality guarantee measures, such as staggered peak production. As shown in Figure 4c,d, during the emission control period,  $\mathrm{SO}_2$  emissions in Wuhan experienced a significant decline, which were estimated to be 42.1 and  $30.2\%$  lower than 1-week average before and after the emission control period, respectively. For other cities in Hubei, the decreases were also obvious  $(-21.2$  and  $-11.1\%)$ , while the changes in other provinces outside Hubei were minimal, with an increase of  $2.1\%$  and decrease of  $1.5\%$ , respectively.

# 4.DISCUSSION

In this study, data from CPED and CEMS are fused to improve the daily estimation of emissions from coal-fired power units in China. The comprehensive, highly resolved emission database could capture the dynamic changes in emissions during typical socioeconomic events and could be applied to providing more accurate inputs for CTMs and guiding future policies.

# 4.1. Assessment of Widely Used Temporal Profiles in Previous Studies

In previous studies, monthly activity data (e.g., electricity generation and fuel consumption) $^{4}$  and invariable parameters considering factors such as working times $^{1,57}$  have been widely used to disaggregate annual power emissions into monthly and daily scales, respectively. Figure 5 shows comparisons of the multiscale temporal profiles from CEMS with the widely used temporal profiles. At the monthly scale (Figure 5a), the comparison between national average profiles obtained from CEMS and electricity generation shows good agreement ( $R$  between 0.74 and 0.97). The results imply that the commonly used activity indicators are reliable at monthly scale when direct emission measurements are unavailable. At the weekly scale, previous studies $^{1,57}$  use fixed parameters that do not vary over time to allocate emissions from weekly totals to daily scales, considering the empirical production schedule and a few observations, which tend to fail to reflect fluctuations caused by unexpected events. Distinct weekly patterns of power emissions in previous studies $^{1,57}$  are presented in Figure 5b, which are manifested as strong intensity of production activities on weekdays and weak intensity on weekends. Conversely, the weekly profiles from CEMS exhibit no obvious weekend effects, showing that the widely used profiles might exaggerate the differences between weekdays and weekends. Indeed, in many developed countries, $^{58}$  power demand on working days is usually higher than that on weekends. However, owing to different lifestyle, economic, and cultural background, there is no significant difference in electricity demand and power generation between weekdays and weekends in China. And unlike peaking power plants (e.g., natural gas power plants and hydroelectric facilities), coal-fired

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/1eeb6f00-7c02-4c45-a22c-6331c7792747/6abcf662593e9b9515117ddec05d38a5decc64dd8790ce5aaa02af9b3e2b3048.jpg)

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/1eeb6f00-7c02-4c45-a22c-6331c7792747/521f7322873c38808fb40b459c843cc4b61e5d734748b506c570ab43e2d3fa68.jpg)  
Figure 5. Comparisons of monthly and weekly profiles based on flue gas volume or emission rates from CEMS and those widely used in previous studies. (a) Monthly temporal profiles derived from national  $\mathrm{SO}_2$  emission,  $\mathrm{NO}_x$  emission,  $\mathrm{PM}_{2.5}$  emission, and flue gas volume data from CEMS or electricity generation. The electricity-generation data is accessed from the National Bureau of Statistics (https://data.stats.gov.cn/). (b) Weekly temporal profiles calculated by national average flue gas volume,  $\mathrm{SO}_2$  emission,  $\mathrm{NO}_x$  emission, and  $\mathrm{PM}_{2.5}$  emission data from CEMS or from previous studies including that of He et al. $^{57}$  and the EDGAR. $^1$

power plants run throughout the week to provide baseload power as constant and reliable sources of electricity.[59] Evidence from satellite measurements also reflects that  $\mathrm{NO}_2$  columns decrease largely on Saturday and especially on Sunday in cities of North America, Europe, Australia, Korea, and Japan, but no indications for the weekend effect can be found in China.[60,61]

# 4.2. Uncertainties

Our study is subject to some uncertainties. First, daily profiles of 829 power plants without CEMS are derived from other plants with a similar installed capacity in the same province, which are expected to be improved after the installation of CEMS. In addition, we develop a stepwise interpolation method for the missing flue gas volume and emission rates in Section 2.2.2. To quantify the imputation-associated uncertainties, we conduct two sensitivity tests in which we do not impute the missing data (Exp1) or only use linear interpolation for imputation (Exp2). As shown in Figure S2 and Table S2, different imputation methods have limited influence on monthly and weekly temporal profiles at the national and provincial level: The Pearson correlation coefficients range from 0.90 to 0.98 for national scale and from 0.61 to 0.92 for provincial level, which might be affected by the percentage of missing data in different provinces (Figure S3). In addition, the proportion of emissions obtained from imputation to the total could be estimated from Exp1. An uncertainty of  $-20$  to  $-10\%$  indicates that emissions from the stepwise imputation account for a reasonable percentage in

total emissions. And the linear interpolation in Exp2 leads to  $\sim 1\%$  changes of the total emissions, proving that using different imputation methods is robust.

Despite the limitations, our study offers a framework to apply emission measurements from CEMS to improving the temporal representation of emission inventories. Insight obtained from this work could be extended to other sectors (e.g., cement, iron, and steel). In the future, we expect to develop a multisector dataset at the daily scale via data fusion to facilitate atmospheric research and clean air policy formation in China.

# 5. CONCLUSIONS

In this work, we estimate daily emissions from coal-fired power plants in China during 2017-2020 through data fusion of a well-validated unit-based power emission database and high-temporal-resolution measurements from CEMS. A step-by-step method is developed to screen outliers and impute missing values for data from CEMS, and sensitivity tests show that monthly and weekly temporal profiles by different imputation methods are in good agreement ( $R = 0.90 - 0.98$  for national scale,  $R = 0.61 - 0.92$  for provincial level). We find that the temporal profiles from CEMS agree well with available statistical data like monthly power generation and daily coal consumption, with  $R$  greater than 0.7 for 16-27 out of 30 provinces at the monthly scale and  $R$  up to 0.83 at the daily scale. Daily power emissions from the fused database are in the range of 6267-12,994, 0.4-1.3, 6.5-12.0, and  $2.5 - 6.8\mathrm{Gg}$  for  $\mathrm{CO}_{2}$ ,  $\mathrm{PM}_{2.5}$ ,  $\mathrm{NO}_x$ , and  $\mathrm{SO}_2$ , respectively, during 2017-2020, reflecting higher emissions in winter and summer caused by heating and cooling demand and lower ones resulting from holidays. Our estimates are also able to capture the sudden changes in daily power emissions during typical socioeconomic events, including the much slower rebound of power emissions after the Spring Festival holiday due to the impact of COVID-19, higher daily  $\mathrm{CO}_{2}$  emissions from thermal power generation in Yunnan owing to a severe drought, and significant decline of power emissions in Wuhan caused by a short-term emission control during the 7th CISM Military World Games. We also find that previous studies (e.g.,  $\mathrm{EDGAR}^1$ ) that apply fixed parameters to allocate weekly power emission totals to daily scales exaggerate the differences between weekdays and weekends. This work provides a framework to propagate information from real-time emission measurements to high-temporal-resolution emission estimates, which will support dynamic emission tracking and air pollution modeling.

# ASSOCIATED CONTENT

# Supporting Information

The Supporting Information is available free of charge at https://pubs.acs.org/doi/10.1021/acsenvironau.2c00014.

Details on the removal of outliers of CEMS data; figures and tables: evaluation of monthly and daily profiles from CEMS and sensitivity tests for imputation methods (PDF)

# AUTHOR INFORMATION

# Corresponding Author

Qiang Zhang - Ministry of Education Key Laboratory for Earth System Modeling, Department of Earth System Science,

Tsinghua University, Beijing 100084, China;

Email: qiangzhang@tsinghua.edu.cn

# Authors

Nana Wu - Ministry of Education Key Laboratory for Earth System Modeling, Department of Earth System Science, Tsinghua University, Beijing 100084, China  
Guannan Geng - State Key Joint Laboratory of Environment Simulation and Pollution Control, School of Environment, Tsinghua University, Beijing 100084, China; orcid.org/0000-0002-1605-8448  
Xinying Qin - Ministry of Education Key Laboratory for Earth System Modeling, Department of Earth System Science, Tsinghua University, Beijing 100084, China  
Dan Tong - Ministry of Education Key Laboratory for Earth System Modeling, Department of Earth System Science, Tsinghua University, Beijing 100084, China  
Yixuan Zheng - Center of Air Quality Simulation and System Analysis, Chinese Academy of Environmental Planning, Beijing 100012, China; orcid.org/0000-0002-3429-5754  
Yu Lei - Center of Air Quality Simulation and System Analysis, Chinese Academy of Environmental Planning, Beijing 100012, China  
Complete contact information is available at:

https://pubs.acs.org/10.1021/acsenvironau.2c00014

# Notes

The authors declare no competing financial interest.

Daily emissions of  $\mathrm{SO}_2$ ,  $\mathrm{NO}_x$ ,  $\mathrm{PM}_{2.5}$ , and  $\mathrm{CO}_2$  from 2017 to 2020 of 30 provinces in China (except Hong Kong, Macao, Taiwan, and Tibet) can be accessed from http://meicmodel.org/?page_id=2232.

# ACKNOWLEDGMENTS

This work was supported by the National Natural Science Foundation of China (91744310, 92044303, 41625020, and 41921005).

# REFERENCES

(1) Crippa, M.; Solazzo, E.; Huang, G.; Guizzardi, D.; Koffi, E.; Muntean, M.; Schieberle, C.; Friedrich, R.; Janssens-Maenhout, G. High resolution temporal profiles in the Emissions Database for Global Atmospheric Research. Sci. Data 2020, 7, No. 121.  
(2) Guevara, M.; Jorba, O.; Tena, C.; Denier van der Gon, H.; Kuenen, J.; Elguindi, N.; Darras, S.; Granier, C.; Pérez García-Pando, C. Copernicus Atmosphere Monitoring Service TEMPOral profiles (CAMS-TEMPO): global and European emission temporal profile maps for atmospheric chemistry modelling. Earth Sys. Sci. Data 2021, 13, 367-404.  
(3) Mues, A.; Kuenen, J.; Hendriks, C.; Manders, A.; Segers, A.; Scholz, Y.; Hueglin, C.; Builtjes, P.; Schaap, M. Sensitivity of air pollution simulations with LOTOS-EUROS to the temporal distribution of anthropogenic emissions. Atmos. Chem. Phys. 2014, 14, 939-955.  
(4) Zhang, Q.; Streets, D. G.; Carmichael, G. R.; He, K. B.; Huo, H.; Kannari, A.; Klimont, Z.; Park, I. S.; Reddy, S.; Fu, J. S.; Chen, D.; Duan, L.; Lei, Y.; Wang, L. T.; Yao, Z. L. Asian emissions in 2006 for the NASA INTEX-B mission. Atmos. Chem. Phys. 2009, 9, 5131-5153.  
(5) Li, M.; Liu, H.; Geng, G.; Hong, C.; Liu, F.; Song, Y.; Tong, D.; Zheng, B.; Cui, H.; Man, H.; Zhang, Q.; He, K. Anthropogenic emission inventories in China: a review. Natl. Sci. Rev. 2017, 4, 834-866.

(6) Nassar, R.; Napier-Linton, L.; Gurney, K. R.; Andres, R. J.; Oda, T.; Vogel, F. R.; Deng, F. Improving the temporal and spatial distribution of CO2 emissions from global fossil fuel emission data sets. J. Geophys. Res.: Atmos. 2013, 118, 917-933.  
(7) Houyoux, M. R.; Vukovich, J. M. Updates to the Sparse Matrix Operator Kernel Emissions (SMOKE) Modeling System and Integration with Models-3. The Emission Inventory: Regional Strategies for the Future, 1999; Vol. 1461, pp 1-11.  
(8) Zheng, B.; Zhang, Q.; Geng, G.; Chen, C.; Shi, Q.; Cui, M.; Lei, Y.; He, K. Changes in China's anthropogenic emissions and air quality during the COVID-19 pandemic in 2020. Earth Syst. Sci. Data 2021, 13, 2895–2907.  
(9) Baldasano, J. M.; Güereca, L. P.; López, E.; Gasso, S.; Jimenez-Guerrero, P. Development of a high-resolution  $(1\mathrm{km} \times 1\mathrm{km}, 1\mathrm{h})$  emission model for Spain: The High-Elective Resolution Modelling Emission System (HERMES). Atmos. Environ. 2008, 42, 7215-7233.  
(10) Wang, X.; Liang, X.-Z.; Jiang, W.; Tao, Z.; Wang, J. X. L.; Liu, H.; Han, Z.; Liu, S.; Zhang, Y.; Grell, G. A. WRF-Chem simulation of East Asian air quality: Sensitivity to temporal and vertical emissions distributions. Atmos. Environ. 2010, 44, 660-669.  
(11) Ge, X.; Schaap, M.; Kranenburg, R.; Segers, A.; Reinds, G. J.; Kros, H.; de Vries, W. Modeling atmospheric ammonia using agricultural emissions with improved spatial variability and temporal dynamics. Atmos. Chem. Phys. 2020, 20, 16055-16087.  
(12) Menut, L.; Goussebaile, A.; Bessagnet, B.; Khvorostiyanov, D.; Ung, A. Impact of realistic hourly emissions profiles on air pollutants concentrations modelled with CHIMERE. Atmos. Environ. 2012, 49, 233-244.  
(13) Georgiou, G. K.; Kushta, J.; Christoudias, T.; Proestos, Y.; Lelieveld, J. Air quality modelling over the Eastern Mediterranean: Seasonal sensitivity to anthropogenic emissions. Atmos. Environ. 2020, 222, No. 117119.  
(14) British Petroleum. BP Statistical Review of World Energy Report, BP: London, U.K.; 2019.  
(15) Tong, D.; Zhang, Q.; Liu, F.; Geng, G.; Zheng, Y.; Xue, T.; Hong, C.; Wu, R.; Qin, Y.; Zhao, H.; Yan, L.; He, K. Current Emissions and Future Mitigation Pathways of Coal-Fired Power Plants in China from 2010 to 2030. Environ. Sci. Technol. 2018, 52, 12905-12914.  
(16) Zheng, B.; Tong, D.; Li, M.; Liu, F.; Hong, C.; Geng, G.; Li, H.; Li, X.; Peng, L.; Qi, J.; Yan, L.; Zhang, Y.; Zhao, H.; Zheng, Y.; He, K.; Zhang, Q. Trends in China's anthropogenic emissions since 2010 as the consequence of clean air actions. Atmos. Chem. Phys. 2018, 18, 14095-14111.  
(17) Liu, F.; Zhang, Q.; Tong, D.; Zheng, B.; Li, M.; Huo, H.; He, K. B. High-resolution inventory of technologies, activities, and emissions of coal-fired power plants in China from 1990 to 2010. Atmos. Chem. Phys. 2015, 15, 13299-13317.  
(18) Ma, L.; Cai, B.; Wu, F.; Zeng, H. Hourly disaggregation of industrial CO2 emissions from Shenzhen, China. Environ. Pollut. 2018, 236, 396-404.  
(19) Liu, Z.; Ciais, P.; Deng, Z.; Lei, R.; Davis, S. J.; Feng, S.; Zheng, B.; Cui, D.; Dou, X.; Zhu, B.; Guo, R.; Ke, P.; Sun, T.; Lu, C.; He, P.; Wang, Y.; Yue, X.; Wang, Y.; Lei, Y.; Zhou, H.; Cai, Z.; Wu, Y.; Guo, R.; Han, T.; Xue, J.; Boucher, O.; Boucher, E.; Chevallier, F.; Tanaka, K.; Wei, Y.; Zhong, H.; Kang, C.; Zhang, N.; Chen, B.; Xi, F.; Liu, M.; Breon, F. M.; Lu, Y.; Zhang, Q.; Guan, D.; Gong, P.; Kammen, D. M.; He, K.; Schellnhuber, H. J. Near-real-time monitoring of global CO(2) emissions reveals the effects of the COVID-19 pandemic. Nat. Commun. 2020, 11, No. 5172.  
(20) Liu, Z.; Ciais, P.; Deng, Z.; Davis, S. J.; Zheng, B.; Wang, Y.; Cui, D.; Zhu, B.; Dou, X.; Ke, P.; Sun, T.; Guo, R.; Zhong, H.; Boucher, O.; Breon, F.-M.; Lu, C.; Guo, R.; Xue, J.; Boucher, E.; Tanaka, K.; Chevallier, F. Carbon Monitor, a near-real-time daily dataset of global CO2 emission from fossil fuel and cement production. Sci. Data 2020, 7, No. 392.  
(21) Zheng, B.; Geng, G.; Ciais, P.; Davis, S. J.; Martin, R. V.; Meng, J.; Wu, N.; Chevallier, F.; Broquet, G.; Boersma, F.; van der, A. R.; Lin, J.; Guan, D.; Lei, Y.; He, K.; Zhang, Q. Satellite-based estimates

of decline and rebound in China's CO(2) emissions during COVID-19 pandemic. Sci. Adv. 2020, 6, No. eabd4998.  
(22) Wang, Q.; Lu, M.; Bai, Z.; Wang, K. Coronavirus pandemic reduced China's CO2 emissions in short-term, while stimulus packages may lead to emissions growth in medium- and long-term. Appl. Energy 2020, 278, No. 115735.  
(23) Ding J.; van der A, R. J.; Eskes, H. J.; Mijling, B.; Stavrakou, T.; van Geffen, J. H. G. M.; Veefkind, J. P. NOx Emissions Reduction and Rebound in China Due to the COVID-19 Crisis. Geophys. Res. Lett. 2020, 47, No. e2020GL089912.  
(24) Nassar, R.; Hill, T. G.; McLinden, C. A.; Wunch, D.; Jones, D. B. A.; Crisp, D. Quantifying CO2 Emissions From Individual Power Plants From Space. Geophys. Res. Lett. 2017, 44, 10045-10053.  
(25) Nassar, R.; Mastrogiacomo, J.-P.; Bateman-Hemphill, W.; McCracken, C.; MacDonald, C. G.; Hill, T.; O'Dell, C. W.; Kiel, M.; Crisp, D. Advances in quantifying power plant CO2 emissions with OCO-2. Remote Sens. Environ. 2021, 264, No. 112579.  
(26) Karplus, V. J.; Zhang, S.; Almond, D. Quantifying coal power plant responses to tighter SO2 emissions standards in China. Proc. Natl. Acad. Sci. U.S.A. 2018, 115, 7004-7009.  
(27) Zhang, X.; Schreibels, J. Continuous emission monitoring systems at power plants in China: Improving SO2 emission measurement. Energy Policy 2011, 39 (11), 7432-7438.  
(28) Frost, G. J.; McKeen, S. A.; Trainer, M.; Ryerson, T. B.; Neuman, J. A.; Roberts, J. M.; Swanson, A.; Holloway, J. S.; Sueper, D. T.; Fortin, T.; Parrish, D. D.; Fehsenfeld, F. C.; Flocke, F.; Peckham, S. E.; Grell, G. A.; Kowal, D.; Cartwright, J.; Auerbach, N.; Habermann, T. Effects of changing power plant NOx emissions on ozone in the eastern United States: Proof of concept. J. Geophys. Res.: Atmos. 2006, 111, D12306.  
(29) Peischl, J.; Ryerson, T. B.; Holloway, J. S.; Parrish, D. D.; Trainer, M.; Frost, G. J.; Aikin, K. C.; Brown, S. S.; Dubé, W. P.; Stark, H.; Fehsenfeld, F. C. A top-down analysis of emissions from selected Texas power plants during TexAQS 2000 and 2006 J. Geophys. Res.: Atmos. 2010, 115D16 DOI: 10.1029/2009JD013527.  
(30) Pouliot, G.; Denier van der Gon, H. A. C.; Kuenen, J.; Zhang, J.; Moran, M. D.; Makar, P. A. Analysis of the emission inventories and model-ready emission datasets of Europe and North America for phase 2 of the AQMEII project. Atmos. Environ. 2015, 115, 345-360.  
(31) He, H.; Stehr, J. W.; Hains, J. C.; Krask, D. J.; Doddridge, B. G.; Vinnikov, K. Y.; Canty, T. P.; Hosley, K. M.; Salawitch, R. J.; Worden, H. M.; Dickerson, R. R. Trends in emissions and concentrations of air pollutants in the lower troposphere in the Baltimore/Washington airshed from 1997 to 2011. Atmos. Chem. Phys. 2013, 13, 7859-7874.  
(32) He, H.; Hembeck, L.; Hosley, K. M.; Canty, T. P.; Salawitch, R. J.; Dickerson, R. R. High ozone concentrations on hot days: The role of electric power demand and NOx emissions. Geophys. Res. Lett. 2013, 40, 5291-5294.  
(33) Liu, F.; Duncan, B. N.; Krotkov, N. A.; Lamsal, L. N.; Beirle, S.; Griffin, D.; McLinden, C. A.; Goldberg, D. L.; Lu, Z. A methodology to constrain carbon dioxide emissions from coal-fired power plants using satellite observations of co-emitted nitrogen dioxide. Atmos. Chem. Phys. 2020, 20, 99-116.  
(34) Farkas, C. M.; Moeller, M. D.; Felder, F. A.; Baker, K. R.; Rodgers, M.; Carlton, A. G. Temporalization of Peak Electric Generation Particulate Matter Emissions during High Energy Demand Days. Environ. Sci. Technol. 2015, 49, 4696-4704.  
(35) Karplus, V. J. Clearing the air in China. Nat. Energy 2019, 4, 904-905.  
(36) Tang, L.; Xue, X.; Qu, J.; Mi, Z.; Bo, X.; Chang, X.; Wang, S.; Li, S.; Cui, W.; Dong, G. Air pollution emissions from Chinese power plants based on the continuous emission monitoring systems network. Sci. Data 2020, 7, No. 325.  
(37) Tang, L.; Qu, J.; Mi, Z.; Bo, X.; Chang, X.; Anadon, L. D.; Wang, S.; Xue, X.; Li, S.; Wang, X.; Zhao, X. Substantial emission reductions from Chinese power plants after the introduction of ultralow emissions standards. Nat. Energy 2019, 4, 929-938.  
(38) Zhang, Y.; Bo, X.; Zhao, Y.; Nielsen, C. P. Benefits of current and future policies on emissions of China's coal-fired power sector

indicated by continuous emission monitoring. Environ. Pollut. 2019, 251, 415-424.  
(39) Zhang, Y.; Zhao, Y.; Gao, M.; Bo, X.; Nielsen, C. P. Air quality and health benefits from ultra-low emission control policy indicated by continuous emission monitoring: a case study in the Yangtze River Delta region, China. Atmos. Chem. Phys. 2021, 21, 6411-6430.  
(40) Hu, X.; Liu, Q.; Fu, Q.; Xu, H.; Shen, Y.; Liu, D.; Wang, Y.; Jia, H.; Cheng, J. A high-resolution typical pollution source emission inventory and pollution source changes during the COVID-19 lockdown in a megacity, China. Environ. Sci. Pollut. Res. 2021, 28, 45344-45352.  
(41) Liu, X.; Gao, X.; Wu, X.; Yu, W.; Chen, L.; Ni, R.; Zhao, Y.; Duan, H.; Zhao, F.; Chen, L.; Gao, S.; Xu, K.; Lin, J.; Ku, A. Y. Updated Hourly Emissions Factors for Chinese Power Plants Showing the Impact of Widespread Ultralow Emissions Technology Deployment. Environ. Sci. Technol. 2019, 53, 2570-2578.  
(42) Zhang, L.; Zhao, T.; Gong, S.; Kong, S.; Tang, L.; Liu, D.; Wang, Y.; Jin, L.; Shan, Y.; Tan, C.; Zhang, Y.; Guo, X. Updated emission inventories of power plants in simulating air quality during haze periods over East China. Atmos. Chem. Phys. 2018, 18, 2065-2079.  
(43) Liu, F.; Beirle, S.; Zhang, Q.; Dörner, S.; He, K.; Wagner, T. NOx lifetimes and emissions of cities and power plants in polluted background estimated by satellite observations. Atmos. Chem. Phys. 2016, 16, 5283-5298.  
(44) Wang, S.; Zhang, Q.; Martin, R. V.; Philip, S.; Liu, F.; Li, M.; Jiang, X.; He, K. Satellite measurements oversee China's sulfur dioxide emission reductions from coal-fired power plants. Environ. Res. Lett. 2015, 10, No. 114015.  
(45) Zhao, Y.; Xia, Y.; Zhou, Y. Assessment of a high-resolution NOX emission inventory using satellite observations: A case study of southern Jiangsu, China. Atmos. Environ. 2018, 190, 135-145.  
(46) Han, P.; Zeng, N.; Oda, T.; Lin, X.; Crippa, M.; Guan, D.; Janssens-Maenhout, G.; Ma, X.; Liu, Z.; Shan, Y.; Tao, S.; Wang, H.; Wang, R.; Wu, L.; Yun, X.; Zhang, Q.; Zhao, F.; Zheng, B. Evaluating China's fossil-fuel CO2 emissions from a comprehensive dataset of nine inventories. Atmos. Chem. Phys. 2020, 20, 11371-11385.  
(47) Chen, X.; Liu, Q.; Sheng, T.; Li, F.; Xu, Z.; Han, D.; Zhang, X.; Huang, X.; Fu, Q.; Cheng, J. A high temporal-spatial emission inventory and updated emission factors for coal-fired power plants in Shanghai, China. Sci. Total Environ. 2019, 688, 94-102.  
(48) Zhong, Z.; Zheng, J.; Zhu, M.; Huang, Z.; Zhang, Z.; Jia, G.; Wang, X.; Bian, Y.; Wang, Y.; Li, N. Recent developments of anthropogenic air pollutant emission inventories in Guangdong province, China. Sci. Total Environ. 2018, 627, 1080-1092.  
(49) Huang, Z.; Zhong, Z.; Sha, Q.; Xu, Y.; Zhang, Z.; Wu, L.; Wang, Y.; Zhang, L.; Cui, X.; Tang, M.; Shi, B.; Zheng, C.; Li, Z.; Hu, M.; Bi, L.; Zheng, J.; Yan, M. An updated model-ready emission inventory for Guangdong Province by incorporating big data and mapping onto multiple chemical mechanisms. Sci. Total Environ. 2021, 769, No. 144535.  
(50) Liu, F.; Beirle, S.; Zhang, Q.; van der, A. R.; Zheng, B.; Tong, D.; He, K. NOx emission trends over Chinese cities estimated from OMI observations during 2005 to 2015. Atmos. Chem. Phys. 2017, 17, 9261-9275.  
(51) Ministry of Ecology and Environment of the People's Republic of China, Specifications for continuous emissions monitoring of SO2, NOx, and particulate matter in the flue gas emitted from stationary sources, HJ 75-2017 (in Chinese), Ministry of Ecology and Environment of the People's Republic of China, 2017, https://www.mee.gov.cn/ywgz/fgbz/bz/bzwjcfbz/201801/W020180322535566350157.pdf (accessed 2022-04-15).  
(52) Ministry of Ecology and Environment of the People's Republic of China, Specifications and test procedures for a continuous emission monitoring system for SO2, NOx, and particulate matter in flue gas emitted from stationary sources, HJ 76-2017 (in Chinese), Ministry of Ecology and Environment of the People's Republic of China, 2017, https://www.mee.gov.cn/ywgz/fgbz/bz/bzwb/jcffbz/201801/W020180108591018226127.pdf (accessed 2022-04-15).

(53) Ministry of Ecology and Environment of the People's Republic of China, Technical specifications of quality assurance and quality control for the monitoring of stationary pollution sources, HJ/T 373-2007 (in Chinese), Ministry of Ecology and Environment of the People's Republic of China, 2007, https://www.mee.gov.cn/ywgz/fgbz/bz/bzwb/jcffbz/200711/W020071204548033175747.pdf (accessed 2022-04-15).  
(54) Liu, F.; Page, A.; Strode, S. A.; Yoshida, Y.; Choi, S.; Zheng, B.; Lamsal, L. N.; Li, C.; Krotkov, N. A.; Eskes, H.; van der A, R.; Veefkind, P.; Levelt, P. F.; Hauser, O. P.; Joiner, J. Abrupt decline in tropospheric nitrogen dioxide over China after the outbreak of COVID-19. Sci. Adv. 2020, 6, No. eabc2992.  
(55) Le Quere, C.; Jackson, R. B.; Jones, M. W.; Smith, A. J. P.; Abernethy, S.; Andrew, R. M.; De-Gol, A. J.; Willis, D. R.; Shan, Y.; Canadell, J. G.; Friedlingstein, P.; Creutzig, F.; Peters, G. P. Temporary reduction in daily global CO2 emissions during the COVID-19 forced confinement. Nat. Clim. Change 2020, 10, 647–653.  
(56) Wang, Q.; Lu, M.; Bai, Z.; Wang, K. Coronavirus pandemic reduced China's CO(2) emissions in short-term, while stimulus packages may lead to emissions growth in medium- and long-term. Appl. Energy 2020, 278, 115735.  
(57) He, K.; Zhang, Q.; Wang, S.; Cheng, S.; Ding, Y.; Feng, Y.; Lei, Y.; Song, Y.; Tang, Q.; Wang, S.; Wang, X.; Wu, Y.; Xie, S.; Xue, Z.; Yao, Z.; Zheng, B. Technical Manual for City-Scale Emission Inventory Compilation (in Chinese), Ministry of Ecology and Environment of the People's Republic of China, 2018.  
(58) Santiago, I.; Moreno-Munoz, A.; Quintero-Jiménez, P.; Garcia-Torres, F.; Gonzalez-Redondo, M. J. Electricity demand during pandemic times: The case of the COVID-19 in Spain. Energy Policy 2021, 148, 111964.  
(59) Kahrl, F.; Williams, J.; Jianhua, D.; Junfeng, H. Challenges to China's transition to a low carbon electricity system. Energy Policy 2011, 39, 4032-4041.  
(60) Beirle, S.; Platt, U.; Wenig, M.; Wagner, T. Weekly cycle of  $\mathrm{NO}_2$  by GOME measurements: a signature of anthropogenic sources. Atmos. Chem. Phys. 2003, 3, 2225-2232.  
(61) Stavrakou, T.; Müller, J. F.; Bauwens, M.; Boersma, K. F.; van Geffen, J. Satellite evidence for changes in the NO2 weekly cycle over large cities. Sci. Rep. 2020, 10, No. 10066.

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/1eeb6f00-7c02-4c45-a22c-6331c7792747/3bceb0ffdaa8926dcb3b4a5713c7a93f7d9351fcea857098d072099e38e72364.jpg)

# CAS BIOFINDER DISCOVERY PLATFORM™

# PRECISION DATA

# FOR FASTER

# DRUG

# DISCOVERY

CAS BioFinder helps you identify

targets, biomarkers, and pathways

Unlock insights

CAS

A division of the American Chemical Society

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/1eeb6f00-7c02-4c45-a22c-6331c7792747/0decb41f57b21607f978324ac6bbb019d191ecdd1a18b7113395959139a0d1ae.jpg)