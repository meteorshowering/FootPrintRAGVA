# Quantifying on-road vehicle emissions during traffic congestion using updated emission factors of light-duty gasoline vehicles and real-world traffic monitoring big data

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/9f92dccd-7045-4b38-83b7-43b51761fb13/964613150bcf1eadc237143eab569719ec9c36d053630358dea6b914d5a902df.jpg)

Xue Chen a, Linhui Jiang a, Yan Xia a, Lu Wang a, Jianjie Ye e, Tangyan Hou a, Yibo Zhang a, Mengying Li a, Zhen Li a, Zhe Song a, Jiali Li a, Yaping Jiang a, Pengfei Li b,\*, Xiaoye Zhang a,c, Yang Zhang d, Daniel Rosenfeld f, John H. Seinfeld g, Shaocalai Yu a,\*

$^{a}$  Research Center for Air Pollution and Health, Key Laboratory of Environmental Remediation and Ecological Health, Ministry of Education, College of Environment and Resource Sciences, Zhejiang University, Hangzhou, Zhejiang 310058, PR China  
<sup>b</sup> College of Science and Technology, Hebei Agricultural University, Baoding, Hebei 071000, PR China  
$^{\mathrm{c}}$  Chinese Academy of Meteorological Sciences, China Meteorological Administration, Beijing 100081, China  
$^{d}$  Department of Civil and Environmental Engineering, Northeastern University, Boston, MA 02115, USA  
e Bytedance Inc., Hangzhou, Zhejiang 310058, China  
$^{\mathrm{f}}$  Institute of Earth Sciences, The Hebrew University of Jerusalem, Jerusalem, Israel  
$^{g}$  Division of Chemistry and Chemical Engineering, California Institute of Technology, Pasadena, CA 91125, USA

# HIGHLIGHTS

- The  $10\%$  highest emitters contribute  $>60\%$  to the total fleet emissions.  
- The emission factors of vehicles produced by different manufacturers differed by 33-49 times.  
- Without traffic congestion, the emissions of CO, HC, and  $\mathrm{NO}_x$  were reduced by  $12 - 28\%$ .

# GRAPHICAL ABSTRACT

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/9f92dccd-7045-4b38-83b7-43b51761fb13/69f1c2b1ef55045f7cc18ebde32196aa5672883aa6d7878e025b85bc6e138440.jpg)

# ARTICLE INFO

Editor: Jianmin Chen

Keywords:

On-road vehicle emissions

Traffic congestion

Light-duty gasoline vehicles

Real-world

Big data

Emission factors

# ABSTRACT

Light-duty gasoline vehicles (LDGVs) have made up  $>90\%$  of vehicle fleets in China since 2019, moreover, with a high annual growth rate  $(>10\%)$  since 2017. Hence, accurate estimates of air pollutant emissions of these fast-changing LDGVs are vital for air quality management, human healthcare, and ecological protection. However, this issue is poorly quantified due to insufficient reserves of timely updated LDGV emission factors, which are dependent on real-world activity levels. Here we constructed a big dataset of explicit emission profiles (e.g., emission factors and accumulated milestones) for 159,051 LDGVs based on an official I/M database by matching real-time traffic dynamics via real-world traffic monitoring (e.g., traffic volumes and speeds). Consequently, we provide robust evidence that the emission factors of these LDGVs follow a clear heavy-tailed distribution. The top  $10\%$  emitters contributed  $>60\%$  to the total fleet emissions, while the bottom  $50\%$  contributed  $<10\%$ . Such emission factors were effectively reduced by  $75.7 - 86.2\%$  as official emission standards upgraded gradually (i.e., from China 2 to China 5) within 13 years from 2004 to 2017.

Nevertheless, such achievements would be offset once traffic congestion occurred. In the real world, the typical traffic congestions (i.e., vehicle speed  $< 5\mathrm{km / h}$ ) can lead to emissions 5-9 times higher than those on non-congested roads (i.e., vehicle speed  $>50\mathrm{km / h}$ ). These empirical analyses enabled us to propose future traffic scenarios that could harmonize emission standards and traffic congestion. Practical approaches on vehicle emission controls under realistic conditions are proposed, which would provide new insights for future urban vehicle emission management.

# 1. Introduction

Tailpipe emissions of on-road vehicles have become a major source of urban air pollution in the past decade (Feng and Liao, 2016; Franco et al., 2013; Saliba et al., 2017; Wu et al., 2017). In 2020, emissions of carbon monoxide (CO), hydrocarbons (HC), and nitrogen oxides  $(\mathrm{NO}_x)$  from gasoline vehicles in China were 5.61 million tons, 1.34 million tons and 295 thousand tons, respectively, accounting for  $80.9\%$ $77.6\%$  and  $4.8\%$  of the total vehicle emissions, respectively (MEEPRC, 2021). Light-duty gasoline vehicles (LDGVs) make up  $>90\%$  of all vehicles in China and their population has been growing rapidly in recent years. Vehicle emissions change significantly in spatial-temporal variations, leading to varying and even opposite environmental effects (Davison et al., 2021; Deng et al., 2020; Liu et al., 2018; Saikawa et al., 2011; Sun et al., 2020; Wen et al., 2020). Thus, vehicle emission inventories play an important role in the management of air pollution and provide key inputs for air quality models.(Davison et al., 2021; Deng et al., 2020; Farren et al., 2020; Jing et al., 2016; Wen et al., 2020). However, it remains difficult to ensure the accuracy of vehicle emissions under realistic conditions.

In order to improve the accuracy of total vehicle emissions, real-world vehicle emission factors are needed, but they are usually difficult to obtain (Deng et al., 2020). Various testing methods have been used in previous studies, such as the chassis dynamometer (Huang et al., 2017; Huang et al., 2020a), tunnel tests (Chang et al., 2016; Huang et al., 2017; Lawrence et al., 2016; Zhang et al., 2018), and portable emission measurement systems (PEMS) (Cao et al., 2016; He et al., 2019; Mera et al., 2019; Yang et al., 2020a; Yu et al., 2016). Different experiments vary in sample composition, sites, conditions, and equipment for test. Various trends, even opposite trends of how vehicle emission factors change with operating modes, are found in previously published studies. Three main different conclusions were obtained as summarized below. Some studies show that emission factors of CO, HC, and  $\mathrm{NO}_{\mathrm{x}}$  decrease with the increase of driving speeds (Huang et al., 2020b; Li et al., 2016), while some studies reveal that emission factors of CO decrease with the increase of driving speed when speeds are lower than  $50~\mathrm{km / h}$  and then increase with speed (Jing et al., 2016). However, other studies report that the HC and  $\mathrm{NO}_{\mathrm{x}}$  emissions increase with speed when speeds are under  $60~\mathrm{km / h}$  and decrease as speeds exceed  $60~\mathrm{km / h}$  (Choudhary and Gokhale, 2016; Ko and Cho, 2006). Large differences in the vehicle emission characteristics will have an adverse impact on the accurate quantification of on-road vehicle emissions, failing to support the identification of target high emitters.

The main cause of the huge differences in the results of previous studies has been associated with the large uncertainties in the test results and poor representativeness of test samples. Test samples were usually so limited (<200) that the test results obtained in previous studies could not statistically represent the emission levels of the whole fleet (Cao et al., 2016; He et al., 2019; Mera et al., 2019; Yang et al., 2020a; Yu et al., 2016). Covering samples of all emission standards and vehicle manufacturers is the key to improving the accuracy of vehicle emission factors. Due to limited budgets or efforts, the design of sample sizes is usually determined on the basis of researchers' experience and has not yet been derived systematically (Chen et al., 2019). Therefore, establishing the high precision vehicle emission inventory from a big data perspective is of vital importance.

The rapid increases of vehicle population have brought serious traffic congestion to megacities. It is generally believed that congestion will increase vehicle emissions, but how vehicle emissions change under different congestion conditions has not been accurately quantified in previous

studies (Lu et al., 2021). Previous studies have reported the traffic congestion emissions from a limited number of vehicles and certain roads (i.e., one signalized intersection) (Alobaidi et al., 2020; Choudhary and Gokhale, 2019), but the real-world traffic congestion emissions for the typical urban road networks have rarely been reported. Ko et al. (2019) tested real-world driving emissions of a Euro-6 diesel vehicle and reported that  $\mathrm{NO}_{\mathrm{x}}$  emissions under the heavy traffic conditions were  $29\%$  higher than those under smooth traffic conditions. Alobaidi et al. (2020) revealed a significant impact of the congestion on air pollution at intersections with  $8 - 25\%$  reductions achieved by optimizing cycle and phase times, and preventing vehicles from stopping near the signalized intersection. The main obstacle towards accurately quantifying traffic congestion emissions is mainly associated with the lack of high temporal and spatial resolution observations of on-road traffic monitoring data and real-time online vehicle emission calculation platforms.

This study aims to study the current status of vehicle emissions in China from a big data perspective. A newly updated dataset of 159,051 light-duty gasoline vehicles from Xiaoshan District, Hangzhou, were used, believed to be the best available sample of real emissions to conduct an analysis. Vehicle-specific emission factors were calculated on the basis of the high-resolution big data of vehicle emission measurements. As a result, the high contributions from target high emitters and significant differences among different manufacturers were quantified. Real-time online traffic monitoring big data in Xiaoshan District provide strong support to quantify road vehicle exhaust emissions. Consequently, the hyper-fine maps of on-road vehicle emissions were obtained. Thus, environmental effects of traffic congestion and to what extent it will offset the benefits of emission standards upgrading were further illustrated. Finally, practical approaches to vehicle emission controls under realistic conditions were proposed, providing new insights for urban vehicle emission management.

# 2. Material and methods

# 2.1. High-resolution measurements of vehicle emissions

The 1 Hz measurements of vehicle emissions in 2018-2019 were obtained from the local official vehicle Inspect/Maintenance (I/M) dataset in Xiaoshan District. During the inspection processes, the emissions of each vehicle were tested under the legislative chassis dynamometer test cycle in the Vehicle Mass Analysis System (VMAS) for  $195\mathrm{s}$  with a maximum speed of  $50~\mathrm{km / h}$  and an average speed of  $19~\mathrm{km / h}$  (MEEPRC, 2018). High-resolution measurements of 159,051 vehicles were collected in this study with a total of 30 million records, including continuous second-by-second emission profiles for gaseous species (CO, HC, and NO) and simultaneous driving speeds. Note that the measurements of vehicle emissions are conducted under the requirements of national standard method (MEEPRC, 2018) and the accuracies of measurements of CO, HC, and NO were  $97\%$ $97\%$  and  $96\%$  respectively. One example of test vehicles is shown in Fig. S1. The registration dates, accumulated Mileages, emission standards, exhaust volumes and other information of each vehicle were also included the I/M dataset.

This dataset covers vehicles of four different emission standards (i.e., China 2 to China 5), in which China 4 vehicles accounted for the highest proportion, making up two thirds of the total sample size, followed by China 3, China 5, and China 2 vehicles. The ages of vehicles ranged from 1 to 22 years, with  $65.7\%$  vehicles in the range of 5-10 years old. Cumulative travel distances of these vehicles varied from 1 to 1000 thousand km.

Table S1 gives the statistical summary of the information available in the dataset. The data quality controls of HC, CO, and NO concentrations in the processes of vehicle exhaust detection were carried out according to the technical standard for the emission tests of light gasoline vehicles in China (MEEPRC, 2018). Constrained by the applicable environmental test conditions and measurement ranges of testing equipment, invalid pollutants concentration data were detected. The invalid data accounted for  $< 0.01\%$  of the whole dataset, which were eliminated in the process of data cleaning. The fleet composition is representative due to its coverage of wide ranges of vehicle ages, cumulative travel distances, and diverse manufacturers. When comparing with the mobile source environmental management annual report in China released by the Ministry of Ecology and Environment of the People's Republic of China (MEEPRC, 2019), it can be found that the fleet composition of gasoline vehicles was relatively comparable to the overall situation of the whole country (Fig. S2 (a)). Similar trends in the contributions of pollutant emissions by different emission standards were also found in the results of this study and those released by the MEEPRC (Fig. S2 (b)). Thus, the dataset used in this study is relatively representative in China. To the best of our knowledge, this huge dataset we obtained is highly representative compared with existing studies (Yang et al., 2020a; Yu et al., 2016).

Bootstrap-sampling based Monte-Carlo simulations were used to evaluate the stability of the annual inspection dataset, following the method of Chen et al. (2019). Sample sizes of 5, 10, 20, 30, 50, 200, 500, 1000, 2000, 3000, 5000 were used to examine the statistical robustness of means and variances of the samples to estimate the population mean and variance. For each sample size, 1000 times simulations were performed with replacement. The results (Fig. S3) show that the sample biases gradually decreased and the stability of samples increased with the increase of sample size, which indicated good stability of the big dataset in this study. Despite this, there are still some uncertainties in the measurements of pollutant concentrations, mainly from environment temperature, air pressure and other aspects. But these factors have relatively small influences and will not overturn the existing research results.

# 2.2. Calculation of distance-specific emission factors

The distance-specific emission factors of HC, CO, and  $\mathrm{NO}_{\mathrm{x}}$  were calculated using the following equations (MEEPRC, 2018):

$$
E m = C \times \rho \times Q \tag {1}
$$

$$
\mathrm {E F} = \frac {\sum E m}{\sum \nu} \tag {2}
$$

where  $C$  is the concentrations of pollutants (\% for CO, and  $10^{-6}$  for HC and  $\mathrm{NO}_x$ );  $\rho$  is the density of pollutants,  $\mathrm{g / m^3}$ ;  $Q$  is the flow rate of pollutants,  $\mathrm{m^3 / s}$ ;  $Em$  is the amount of pollutant emissions per second,  $\mathrm{g / s}$ ;  $\nu$  is the equivalent driving distance of vehicles,  $\mathrm{km / s}$ ;  $EF$  is the distance-specific emission factors of pollutants,  $\mathrm{g / km}$ . The densities of pollutants and exhaust flow are corrected to the standard state (273.15 K, 100 kPa).

Tailpipe volume concentrations of HC, CO, and  $\mathrm{NO}_{\mathrm{x}}$  measured from the analyzer are corrected on the basis of dilution and humidity correction factors (MEEPRC, 2018):

$$
C _ {H C} (i) = R _ {H C} (i) \times D F (i) \tag {3}
$$

$$
C _ {C O} (i) = R _ {C O} (i) \times D F (i) \tag {4}
$$

$$
C _ {N O x} (i) = R _ {N O x} (i) \times D F (i) \times k _ {H} (i) \tag {5}
$$

therein  $C_{HC}(i)$  is the corrected HC concentration at the ith second,  $10^{-6}$ ;  $C_{CO}(i)$  is the corrected CO concentration at the ith second, %;  $C_{NOx}(i)$  is the corrected  $\mathrm{NO}_{\mathrm{x}}$  concentration at the ith second,  $10^{-6}$ ;  $R_{HC}(i)$  is the measured HC concentration at the ith second,  $10^{-6}$ ;  $R_{CO}(i)$  is the measured CO concentration at the ith second, %;  $R_{NOx}(i)$  is the measured  $\mathrm{NO}_{\mathrm{x}}$  concentration at the ith second, %;  $R_{NOy}(i)$  is the measured  $\mathrm{NO}_{\mathrm{x}}$  concentration at the ith second, %;  $R_{NOx}(i)$  is the measured  $\mathrm{NO}_{\mathrm{x}}$  concentration at the ith second, %;  $R_{NOy}(i)$  is the measured  $\mathrm{NO}_{\mathrm{x}}$  concentration at the ith second, %;  $R_{NOx}(i)$  is the measured  $\mathrm{NO}_{\mathrm{x}}$

concentration at the ith second,  $10^{-6}$ ;  $DF(i)$  is the dilution factor at the ith second;  $k_{H}(i)$  is the humidity correction factor at the ith second.

The calculation of dilution factor is as follows (MEEPRC, 2018):

$$
D F = \frac {C _ {C O _ {2} , C}}{C _ {C O _ {2} , M}} \tag {6}
$$

$$
C _ {C O _ {2}, C} = \left[ \frac {X}{a + 1 . 8 8 X} \right] \cdot 1 0 0 \tag {7}
$$

$$
X = \frac {C _ {C O _ {2} , M}}{C _ {C O _ {2} , M} + C _ {C O , M}} \tag {8}
$$

Where:  $DF$  is the dilution factor;  $C_{CO_2}$ ,  $C$  is the corrected value of measured  $\mathrm{CO}_2$  concentration,  $\%$ ;  $C_{CO_2}$ ,  $M$  is the measured value of  $\mathrm{CO}_2$  concentration,  $\%$ ;  $C_{CO,M}$  is the measured value of CO concentration,  $\%$ ;  $a$  is fuel calculation coefficient, which varies with fuel types (i.e., Gasoline - 4.644; Compressed natural gas - 6.64; LPG - 5.39). When the calculated value of dilution factor is  $>3.0$ , the dilution factor is set to be 3.0.

# 2.3. Real-time detections of on-road vehicles

Xiaoshan District is located in eastern Hangzhou, in the Yangtze River Delta in China (Fig. 1) with a population of over 2.01 million. In 2021, its annual GDP was 201.16 billion Yuan, ranking fourth among districts in Hangzhou. Equipped with an international airport, Xiaoshan District has become an important transportation center of Zhejiang province with densely distributed road networks (i.e.,  $1953.7\mathrm{km}$  within  $1417.8\mathrm{km}^2$ ). This implies that the on-road vehicle emissions play a crucial role in affecting local fine-scale air quality and public health.

Xiaoshan District is at the forefront of the country in the digital transformation and upgrading of the government. It is one of the few areas that have achieved full coverage of integrated traffic monitoring, and has been interconnected through its intelligent transportation system (called "city brain") since 2017 (Hua, 2018). This provide the opportunity to obtain detailed road traffic and road network information. According to 2021 China Urban Transportation Report released by Baidu Map (Baidu Map, 2021), the congestion index during rush hours of Hangzhou ranks top 9 among cities with  $>3$  million motor vehicles. As the transportation hub of Hangzhou, Xiaoshan District, with dense road network, its speed and traffic flow distribution characteristics can well represent the traffic conditions of large cities. Equipped with real-time online traffic monitoring facilities, the core road network in Xiaoshan District is divided into 4585 road segments. Traffic video records, together with image recognition algorithms (Redmon et al., 2016), were applied to detect vehicle license plates and thus monitor traffic fluxes, vehicle categories and driving speeds. These license plate recognition (LPR) data include the records of traffic fluxes and vehicle-specific speeds of on-road vehicles in Xiaoshan District. The average daily detection records were 4.23 million. As a result, we constructed a dataset of total  $1.53 \times 10^{9}$  records from 1 January 2021 to 31 December 2021.

# 2.4. Mapping of on-road vehicle emissions

A hyperfine-resolution bottom-up model was used to calculate the on-road vehicle emissions in Xiaoshan District, following the method of Jiang et al. (2021). Hourly observations of surface temperature and humidity were used to reflect local meteorological conditions. Meteorological observations came from two sets of real-time online remote sensing monitoring equipment in Xiaoshan District. The information of these remote sensing equipment was introduced in detail in our previous study (Xia et al., 2022). Real-time emissions were quantified on the basis of the vehicle emission factors, driving speeds, traffic fluxes, and the length of road segments:

$$
E _ {h, j, l} = \sum_ {l} E F _ {j (\nu)} \times T F _ {h, l} \times L _ {l} \tag {9}
$$

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/9f92dccd-7045-4b38-83b7-43b51761fb13/6bf08bdec95a268cd54dfb7f568571062f149d0bd4518fce6f5d825bda52f48a.jpg)  
Fig. 1. Comprehensive traffic monitoring network in Xiaoshan District. (a) Xiaoshan District (the red area) is located in the hinterland of the YRD in China. (b) Comprehensive traffic monitoring achieves full coverage over Xiaoshan District. Each dot represents a set of comprehensive traffic monitoring facilities that can recognize license plates, traffic fluxes, vehicle-specific speed, and vehicle categories. The entire road network over Xiaoshan District is divided into 4585 road segments. Such road segments are divided into three road classes: highways (blue lines), arterial roads (pink lines), and residential streets (green lines). Map data © 2022, Gaode Map.

$E_{h,j,l}$  is the emission of pollutant  $j$  on the road segment  $l$  at hour  $h$  (g/h).  $EF_{j(\nu)}$  is the emission factor of the pollutant  $j$  at the speed  $\nu$  (g/km), which is derived from local vehicle I/M dataset.  $TF_{h,l}$  is the traffic fluxes on the road segment  $l$  at hour  $h$  (vehicle/h), which comes from the real-time integrated traffic monitoring system.  $L_{l}$  is the length of the road segment  $l$  (km), which is quantified on the basis of the geographic coordinates of each traffic monitoring station.

Eqs. (1)-(8) are the calculation methods mentioned in the measurement standard required by the Ministry of Ecology and Environment of the People's Republic of China (MEEPRC, 2018). The Eq. (9) is widely used in the quantification of on-road vehicle emissions in China (Wu et al., 2020; Zhang et al., 2016), which also has application cases in Hangzhou (Jiang et al., 2021; Pu et al., 2015). Thus, the Eqs. (1)-(9) are well applicable for the calculation of vehicle emissions in Hangzhou.

# 3. Results and discussion

# 3.1. Sharp decreases in the LDGV emissions caused by the upgrading emission standards

China's vehicle emissions are highly heterogeneous (Deng et al., 2020). Continuous upgrading of vehicle emission standards has resulted in on-road vehicle fleets consisting of at least three emission levels (Deng et al., 2020), thus challenging the accurate estimation of emission characteristics of vehicles. Currently, the most widely used vehicle emission factor dataset is based on the technical guidelines on emission inventory (GEI) released by the Ministry of Ecology and Environment of the People's Republic of China (MEEPRC) in 2014 (MEEPRC, 2014), with testing speeds of  $30 - 35\mathrm{km / h}$ . In order to eliminate the influences of working conditions on emission factors, we selected vehicle data with the same driving speeds from the annual inspection dataset to derive corresponding vehicle

emission factors. Fig. 2 (a) illustrates the differences between our results and those released by the MEEPRC.

Similar reductions in the emission factors of CO, HC, and  $\mathrm{NO}_{\mathrm{x}}$  were observed with the upgrading of emission standards. On the whole, with the continuous upgrading of emission standards for light-duty gasoline vehicles, the emission factors decreased significantly. Slight differences were found in the reduction rates between our results and the MEEPRC guidelines. In the process of upgrading from China 2 to China 5, it was found that the emission factors of CO, HC, and  $\mathrm{NO}_{\mathrm{x}}$  decreased by  $75.7\%$ ,  $70.7\%$  and  $86.2\%$ , respectively. In contrast, CO, HC, and  $\mathrm{NO}_{\mathrm{x}}$  decreased by  $81.7\%$ ,  $82.2\%$  and  $94.8\%$ , respectively, as reported in the MEEPRC dataset. The reductions of emission factors obtained in this study were not as significant as those in the MEEPRC dataset. The CO and  $\mathrm{NO}_{\mathrm{x}}$  emission factors obtained in this study were significantly higher than the MEEPRC results, by  $18 - 69\%$  for CO and  $37 - 261\%$  for  $\mathrm{NO}_{\mathrm{x}}$ . However, the HC emission factors in this study were  $20 - 52\%$  lower than the MEEPRC results. One possible reason might be that the test samples used in this study traveled longer distance and aged older than those in the MEEPRC results, since the vehicle engines, catalysts and the particle filters deteriorated gradually with the vehicle's ages (Chen and Borken-Kleefeld, 2016).

According to the local vehicle annual inspection dataset, vehicles from 88 manufacturers were involved. The top five manufacturers in terms of vehicle population were Shanghai Volkswagen, Shanghai Automotive Industry Corporation (SAIC) General Motors, Beijing Hyundai, SAIC-GM Wuling, and Dongfeng Nissan, accounting for  $45\%$  of the total population. Fig. 2(b) shows the vehicle emission factors of these five manufacturers and the average vehicle emission factors of all vehicles in our dataset as a function of model years. It can be found that the average vehicle emission factors of all vehicles decreased sharply and converged gradually as model years increased. The average emission factors of CO, HC, and  $\mathrm{NO}_{\mathrm{x}}$  from

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/9f92dccd-7045-4b38-83b7-43b51761fb13/d1114f5ceb2b35b2da124e7d4a03aa8668c2ef27733b913e2f703894ccb64d41.jpg)

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/9f92dccd-7045-4b38-83b7-43b51761fb13/3bf1308f5e466104ef550852074891491edd1ec866fb680a5a48d71848288796.jpg)

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/9f92dccd-7045-4b38-83b7-43b51761fb13/9e1597c1a9ec9273b0d62dfe595d743b0b3585b2e449bb478108b5140e369ac4.jpg)

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/9f92dccd-7045-4b38-83b7-43b51761fb13/8f29d45cba55d3b286ba9e0fb7da4fe636f45946a0e2ed3c34801b6a2a679d47.jpg)  
Fig. 2. (a) The average emission factors of CO, HC and NOx in this study and those released by the Ministry of Ecology and Environment of the People's Republic of China (MEEPRC) in 2014, stratified by vehicle emission standards. The error bars represent the  $95\%$  confidence intervals. (b) Variations of emission factors of vehicles produced by five representative manufactures as a function of vehicle model years. The red lines represent the mean emission factors of vehicles from the 88 manufactures.

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/9f92dccd-7045-4b38-83b7-43b51761fb13/763195574e96811f422ab8dca370e9a3cbeef33f3402431d7b8199087751c982.jpg)

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/9f92dccd-7045-4b38-83b7-43b51761fb13/8a4e4c17b523370b8bef214891f9b49a8a836f035c01740683709f161cdb9d20.jpg)

1998 to 2019 decreased by  $93.5\%$ ,  $90.6\%$ , and  $95.8\%$ , respectively. Similar trends were also found for these five manufactures with decreases of the vehicle emission factors of CO, HC, and  $\mathrm{NO}_{\mathrm{x}}$  by  $74.5 - 96.9\%$ ,  $67.1 - 98.2\%$ , and  $87.8 - 98.6\%$ , respectively. Among them, the decline trends of Shanghai Volkswagen vehicles were the most significant with the decreases of emission factors of CO, HC, and  $\mathrm{NO}_{\mathrm{x}}$  all by  $>96\%$ .

# 3.2. Extremely high contributions to pollutant emissions from the  $10\%$  high-emitters

Overall, the on-road vehicle emission intensities of CO, HC, and  $\mathrm{NO}_{\mathrm{x}}$  varied with seasons (Fig. S4). The hourly average on-road HC emission intensities varied from 10.3 to  $14.2~\mathrm{g / km}$ , with emissions in winter significantly higher than spring and summer. Similar trends were also found in the emission intensities of  $\mathrm{NO}_{\mathrm{x}}$ , with hourly emissions in winter  $17\%$  higher than in spring and summer. However, the emission intensities of CO peaked in autumn, which were around  $15\%$  higher than those in spring. The variations in HC emissions are attributed to seasonal changes of fuel composition. To meet fuel vapor pressure requirements, refineries usually replace lighter compounds (such as butane) used in the winter with lower volatility alkanes and aromatic compounds (such as toluene) in the summer. The seasonal variations of vehicle emission characteristics in this study are similar to those of Wang et al. (Wang et al., 2018).

Light-duty gasoline vehicles make up the largest share  $(>90\%)$  of all vehicles and are growing the fastest in China (Huang et al., 2017). Thus, enhancing the supervision and management of high emitters is of vital importance. As presented in Fig. 3, our results also show that the distribution curves of CO, HC, and  $\mathrm{NO}_{\mathrm{x}}$  emission factors have an obvious long tail, indicating that they were mainly concentrated in the low-value part. CO emission factors of  $73.2\%$  vehicles were lower than  $2\mathrm{g / km}$ , with only  $5.4\%$  larger than  $8\mathrm{g / km}$ . At the same time, vehicles with HC emission factors lower than  $0.1\mathrm{g / km}$  made up  $67.8\%$  of the total vehicles. Similarly, around  $62.9\%$  of vehicles had  $\mathrm{NO}_{\mathrm{x}}$  emission factors below  $0.1\mathrm{g / km}$ . This highly skewed distribution patterns of CO, HC, and  $\mathrm{NO}_{\mathrm{x}}$  emissions were consistent with previous studies (Bishop and Haugen, 2018; Huang et al.,

2018a, 2018b). Many factors account for this kind of distribution, such as large differences among vehicles of different emission standards, manufacturers, vehicle ages and accumulated mileages, which will be discussed in detail later.

Further, we quantified the emission contributions of the high-emitters from a vehicle-specific emission perspective. The annual emissions of each vehicle were calculated on the basis of the vehicle-specific emission factors and the annual distance traveled. The emissions of all the vehicles were summed into annual total fleet emissions and we defined the  $10\%$  high-emitters as the vehicles with annual emissions ranking at the top  $10\%$  of the total fleet. Extremely high contributions from the  $10\%$  high-emitters were observed in CO, HC, and  $\mathrm{NO}_{\mathrm{x}}$ . The results (Table 1) show that the  $10\%$  high-emitters contributed  $>63 - 73\%$  of the total fleet emissions (Scenario M1), while the  $50\%$  cleanest vehicles only accounted for  $< 3 - 7\%$  of the total fleet emissions. Our findings are similar to those of Beaton et al. (1995), while the portions of  $\mathrm{NO}_{\mathrm{x}}$  were significantly higher than those of Huang et al. (2020b). Since we were unable to obtain the real-time activity trajectories of high emission vehicles, this may lead to non-negligible errors in the calculations of annual emissions. Therefore, we designed another four different mileage scenarios (M2-M5) to analyze the emission proportions of the  $10\%$  high emitters. Surprisingly, even at the lowest activity level (M5), the emission contributions of the  $10\%$  high emitters were still higher in the cases of CO and  $\mathrm{NO}_{\mathrm{x}}$  or close in the case of HC relative to the  $50\%$  cleanest vehicles.

On this basis, the spatial distributions of vehicle emissions from the  $10\%$  high emitters were depicted in detail (Fig. 4, Figs. S5-S6). Scenarios M1-5 and M6-10 represented vehicle emissions during rush hours and off-peak hours, respectively, with the accumulated mileages of the  $10\%$  high emitters corresponding to M1-M5 in Table 1. It was found that the emissions of the target high emitters decreased sharply from M1 to M5, or M6 to M10. Thus, strict restrictions on the travels of these high emitters can effectively reduce road vehicle emissions, implying that accelerating clean substitution of these high emitters will be a feasible approach. As shown in Fig. S7, pre-China 3 vehicles made up around  $50\%$  of these  $10\%$  high emitters. We designed four different clean alternative scenarios

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/9f92dccd-7045-4b38-83b7-43b51761fb13/faf22b611cd83e24ee280864c725aa1fb1d1367d78db15c68ea5f640f2a6972b.jpg)

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/9f92dccd-7045-4b38-83b7-43b51761fb13/922fa92e54b4473bfcf867eac59ab83263426301e639f975bcc82f8592e448ca.jpg)  
Fig. 3. (a) Distribution of HC, CO and  $\mathrm{NO}_{\mathrm{x}}$  emission factors in the total vehicle fleet. (b) Probability density distribution of HC, CO and  $\mathrm{NO}_{\mathrm{x}}$  emission factors, stratified by vehicle emission standards.

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/9f92dccd-7045-4b38-83b7-43b51761fb13/11c123b783f982d91bc7e035891111945b62a3be60054655b2f297fa5d55e0a1.jpg)

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/9f92dccd-7045-4b38-83b7-43b51761fb13/d2faecceee40f8979811a99798014b9614a8d9b10c650711a227a221e0375fde.jpg)

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/9f92dccd-7045-4b38-83b7-43b51761fb13/3ded7fa45bb773a1d890769473dae23f5242e430563aa5e2c450af4affe6caeb.jpg)

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/9f92dccd-7045-4b38-83b7-43b51761fb13/6269573bda732dda8bd330a3826459ebc2f56c60db06a92ffd44a98ad63d66bd.jpg)

Table 1 Emission contributions of the  $10\%$  high emitters and the cleanest  $50\%$  emitters to the total fleet emission.  

<table><tr><td rowspan="2">Scenarios</td><td rowspan="2">Activity level of the 10 % high emitters</td><td rowspan="2">Pollutants</td><td rowspan="2">Annual emissions of all vehicles(t)</td><td colspan="2">The 10 % high emitters</td><td colspan="2">The cleanest 50 % emitters</td></tr><tr><td>Annual emissions (t)</td><td>Contribution(%)</td><td>Annual emissions (t)</td><td>Contribution(%)</td></tr><tr><td rowspan="3">M1</td><td rowspan="3">Average annual mileage</td><td>HC</td><td>381.7</td><td>241.0</td><td>63.1 %</td><td>25.4</td><td>6.7 %</td></tr><tr><td>CO</td><td>7217.8</td><td>4859.6</td><td>67.3 %</td><td>349.0</td><td>4.8 %</td></tr><tr><td>NOx</td><td>726.5</td><td>531.3</td><td>73.1 %</td><td>22.9</td><td>3.2 %</td></tr><tr><td rowspan="3">M2</td><td rowspan="3">Average annual mileage *0.7</td><td>HC</td><td>309.4</td><td>168.7</td><td>54.5 %</td><td>25.4</td><td>8.2 %</td></tr><tr><td>CO</td><td>5759.9</td><td>3401.7</td><td>59.1 %</td><td>349.0</td><td>6.1 %</td></tr><tr><td>NOx</td><td>567.1</td><td>371.9</td><td>65.6 %</td><td>22.9</td><td>4.0 %</td></tr><tr><td rowspan="3">M3</td><td rowspan="3">Average annual mileage *0.5</td><td>HC</td><td>261.2</td><td>120.5</td><td>46.1 %</td><td>25.4</td><td>9.7 %</td></tr><tr><td>CO</td><td>4788.0</td><td>2429.8</td><td>50.7 %</td><td>349.0</td><td>7.3 %</td></tr><tr><td>NOx</td><td>460.9</td><td>265.7</td><td>57.6 %</td><td>22.9</td><td>5.0 %</td></tr><tr><td rowspan="3">M4</td><td rowspan="3">Average annual mileage *0.3</td><td>HC</td><td>213.0</td><td>72.3</td><td>33.9 %</td><td>25.4</td><td>11.9 %</td></tr><tr><td>CO</td><td>3816.1</td><td>1457.9</td><td>38.2 %</td><td>349.0</td><td>9.1 %</td></tr><tr><td>NOx</td><td>354.6</td><td>159.4</td><td>45.0 %</td><td>22.9</td><td>6.5 %</td></tr><tr><td rowspan="3">M5</td><td rowspan="3">Average annual mileage *0.1</td><td>HC</td><td>164.8</td><td>24.1</td><td>14.6 %</td><td>25.4</td><td>15.4 %</td></tr><tr><td>CO</td><td>2844.2</td><td>486.0</td><td>17.1 %</td><td>349.0</td><td>12.3 %</td></tr><tr><td>NOx</td><td>248.3</td><td>53.1</td><td>21.4 %</td><td>22.9</td><td>9.2 %</td></tr></table>

for these  $10\%$  high emitters and quantified expected pollutant emission reductions (Table S2). Scenario R1 focused on the China 2 high emitters only, while the scenarios R2-R4 focused on both China 2 and China 3 high emitters. Under the R1 scenario, pollutant emissions were only reduced by  $13 - 17\%$ . On this basis, if the China 3 high emitters were further replaced in S2, the reductions in pollutant emissions in S2 were increased to  $30 - 34\%$ . The R1 and R2 scenarios only considered China 5 vehicles as alternative targets, while R3 and R4 scenarios also took vehicle electrifications into consideration. With strict controls of pre-China 3 high emitters, the R4 scenario achieved the highest reductions in pollutant emissions  $(36 - 41\%)$ .

# 3.3. Huge differences among the emissions for different vehicle manufacturers

Manufacturer-level vehicle emissions were accurately quantified in this study based on manufacturers with vehicle ownerships  $>15$ . A total of 133,851 vehicles produced by 68 manufacturers were included in this analysis. The emission factors of the 10 cleanest manufacturers and the 10 manufacturers with the highest emissions are shown in Fig. 5a. It was found that the emission factors of vehicles produced by different manufacturers might vary as highly as ten times. The vehicles with high CO emissions, such as Zhongshun, Shuguang and Beijing Jeep, had average emission factors of 10.79-19.41 g/km. However, the vehicles like Chang'an Mazda, Guangzhou Fiat and Chang'an Ford had average CO emission factors of only 0.44-0.62 g/km. The top three manufacturers with the highest HC emissions were Zhongshun (1.47 g/km), Shuguang (0.84 g/km) and Shuangbei (0.74 g/km), and the three manufacturers with the lowest emissions were Chang'an Volvo (0.05 g/km), Dongfeng Honda (0.04 g/km), and Chang'an Mazda (0.04 g/km). The manufacturers with the highest  $\mathrm{NO}_{\mathrm{x}}$  emission level were Shuguang automobile, First Automobile Works Light and Fudi, with average emission factors of 2.22, 2.07 and 1.66 g/km, respectively. The lowest  $\mathrm{NO}_{\mathrm{x}}$  emission levels were found in Chang'an Mazda, Dongfeng Honda and Fujian Benz, with average emission factors of 0.05, 0.04 and 0.04 g/km, respectively. Vehicles produced by manufacturers like Shuguang, First Automobile Works Light, Fudi, Zhongshun, Guangzhou Automobile Changfeng have relatively higher emissions than other manufactures. In contrast, vehicles produced by manufacturers like Dongfeng Honda, Chang'an Mazda, Chang'an Volvo, Chang'an Ford, Shanghai Automotive Industry Corporation (SAIC) General Motors have relatively lower emissions.

Significant differences were also observed in the deterioration trends of vehicle emission factors among different types of vehicles. As shown in Fig. 5(b-c), vehicles produced by Shanghai Volkswagen show the fastest deterioration rate of emission factors. In contrast, those produced by SAIC General Motors and FAW Volkswagen (Audi) had relatively slower deterioration rates. The deterioration trends of emission factors with driving mileages can be well fitted by linear equations (Fig. 5b, Table S3), with

$\mathbb{R}^2$  in the range of 0.349- 0.952. The deterioration trends of emission factors with vehicle ages can be well fitted by polynomial equations (Fig. 5c, Table S4), with  $\mathbb{R}^2$  in the range of 0.367- 0.986. Overall, when the vehicle ages were  $< 10$  years, the degradation rates of emission factors were relatively slow (0.018- 0.066 g/km per year). However, when the vehicle ages were  $>10$  years, the degradation rates accelerated significantly (0.055- 0.191 g/km per year).

Different manufacturers have significant differences in engine models, and exhaust gas treatment equipment, resulting in large differences in vehicle emission factors (Bernard et al., 2018; Davison et al., 2021; Mera et al., 2019). In the future, strengthening the supervision of high emission manufacturers will be an effective method to reduce vehicle emissions. Publishing the quantitative emission factor reports of different manufacturers on a regular basis may be an effective way to urge high-emission manufacturers to make rectifications. The government can consider giving some subsidies to vehicle enterprises using more effective exhaust treatment devices, and encourage enterprises to develop more effective exhaust treatment technologies to further reduce vehicle emissions.

# 3.4. Unexpected high emissions under the slow driving conditions

Vehicle emissions vary with instantaneous driving conditions (Fu et al., 2012; Huang et al., 2020b; Mera et al., 2019; Yang et al., 2016; Zhang et al., 2020). To investigate how vehicle emissions vary under the different working conditions, emission factors of CO, HC, and  $\mathrm{NO}_{\mathrm{x}}$  were divided into 11 groups according to driving speeds. Slow driving conditions, normal urban driving conditions and high-speed driving conditions were defined as driving with speeds of  $0 - 5\mathrm{km / h}$ ,  $30 - 35\mathrm{km / h}$  and larger than  $50\mathrm{km / h}$ , respectively (Feng et al., 2020; Fu et al., 2012; Kumar et al., 2015). As presented in Fig. 6(a), unexpected high emissions under the idling conditions were found in vehicles of all emission standards. Emission factors of CO, HC, and  $\mathrm{NO}_{\mathrm{x}}$  decreased sharply with the increase of vehicle speeds. The emission factors of CO, HC, and  $\mathrm{NO}_{\mathrm{x}}$  were the highest under the slow driving conditions, with average values of 8.35, 0.44, and  $0.71\mathrm{g / km}$ , respectively. When speeds were lower than  $5\mathrm{km / h}$ , the average emission factors of CO, HC, and  $\mathrm{NO}_{\mathrm{x}}$  were extremely high under the normal urban driving conditions with the values of 1.48, 0.07, and  $0.19\mathrm{g / km}$ , respectively. Under the high-speed driving conditions, the average emission factors of CO, HC, and  $\mathrm{NO}_{\mathrm{x}}$  were 1.01, 0.05, and  $0.14\mathrm{g / km}$ , respectively. In summary, the emission factors of CO, HC, and  $\mathrm{NO}_{\mathrm{x}}$  under the slow driving conditions were 5-9 times higher than under the high-speed conditions ( $>50\mathrm{km / h}$ ) and 3-6 times higher than under the normal urban driving conditions. Emission factors under the slow driving conditions were significantly higher than previous studies (Huang et al., 2020b; Yang et al., 2020b. One of the possible reasons might be that the emission data of second by second used in this study can better capture the ultra-high emissions at low speeds or even idling speeds. In contrast with the significant

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/9f92dccd-7045-4b38-83b7-43b51761fb13/a178e834bff3103928ddca5aee492ced24fa43a0bb5c436f09043cbc309259bd.jpg)  
Fig. 4. Hourly average on-road vehicle emission intensities of the  $10\%$  high emitters under different congestion scenarios during rush hours (from 07:00 to 09:00 and from 16:30 to 18:30 local time).

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/9f92dccd-7045-4b38-83b7-43b51761fb13/8243c4b8b369d0314e4f682c3cafd2b3ab83b7ff6309b0d2e7196c1b9ceb4472.jpg)

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/9f92dccd-7045-4b38-83b7-43b51761fb13/744109a9d8febab3630ad11bb76ee090696c40ca0097e49829c58a8ed9934f3a.jpg)

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/9f92dccd-7045-4b38-83b7-43b51761fb13/e3c64198266379ba6a6fe2c69dde8c8c0ad6905199e632ac9ceea68d5ff25838.jpg)  
DAVMAF DOKDQO LMAF O WHOHS OAMF OAMS

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/9f92dccd-7045-4b38-83b7-43b51761fb13/271f75aec7f44f6932ea96af4a7b9a62566a05becf6c5c672c72834e9ff5d49c.jpg)

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/9f92dccd-7045-4b38-83b7-43b51761fb13/4e1f36a5bf1004912dd72402a60f7e31b5232510b1efbb64d89697abada3c7e6.jpg)

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/9f92dccd-7045-4b38-83b7-43b51761fb13/6c1f32a2d57efb8cd5db1207fcee5ef051b82fedb88c2f1aeca154a94117faff.jpg)

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/9f92dccd-7045-4b38-83b7-43b51761fb13/9a02e13c313cc6cbf3648302c271a0f62e0178320ab52b231226c668cc79dfb0.jpg)  
Fig. 5. Differences between different vehicle manufactures. (a) Vehicle emission factors of 10 manufacturers with the highest and 10 manufacturers with the lowest emissions. The size of bubbles is directly proportional to the logarithm of car ownership. (b) Deterioration trends of emission factors with the increase of accumulated mileage. (c) Deterioration trends of emission factors with the increase of vehicle age.

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/9f92dccd-7045-4b38-83b7-43b51761fb13/f5c6913b7f74b3f20da3f23070776da05c085e620fd3d4ba62d2ee9b36a774f1.jpg)

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/9f92dccd-7045-4b38-83b7-43b51761fb13/f055dcb024f85d10a95a19b38acc8d04aaeebdc968c3d74fd6b07c6145a07bdd.jpg)

reductions under the high speed driving conditions (69–87 %), relatively smaller (69–79 %) reductions were found under the slow driving conditions when vehicle emission standards upgraded from China 2 to China 5. This implies that more technological innovations are needed to support the emission reductions of slow driving conditions.

Traffic congestion frequently occurs due to the rapid increases in vehicle population, especially in megacities. On this occasion, vehicles may leave the engine idling for several minutes or longer, which leads to massive emissions (Feng et al., 2020; Sentoff et al., 2010; Shancita et al., 2014; Zhang et al., 2020). Lab measurements showed that the low-speed vehicles produced much higher emissions. Real-world traffic observations allowed us to know where the low-speed motor vehicles were usually distributed and how many emissions they produced. On-road vehicle emissions under the low-speed driving and high-speed driving conditions can be further quantified so as to reveal the significant impact of traffic congestion on the urban vehicle emissions, which so far has no observational evidence. As shown in Fig. 6(b-c), observed traffic congested roads were widespread, mainly distributed in the Airport Highway and the arterial roads. These road segments accounted for around  $20\%$  of the whole roads.

To investigate the environmental effects of traffic congestion, six different traffic congestion scenarios and three fleet composition scenarios were designed (Fig. S8, Tables S5-S6). Traffic congestion scenarios S2 and S5 represented the traffic states under the actual conditions of rush hours

from 07:00 to 09:00 and from 16:30 to 18:30 local time) and off-peak hours (from 9:00 to 16:30 and from 18:30 to 7:00 local time), respectively. On this basis, two smooth traffic (all speeds  $>25\mathrm{km / h}$ ) scenarios (S1 and S4) and two severe congested scenarios (S3 and S6) were designed to represent different traffic conditions. Fleet composition scenario F0 was designed based on the local official vehicle Inspect/Maintenance (I/M) dataset, representing the current composition of road vehicles. On this basis, F1 and F2 scenarios were designed by considering the upgrading of emission standards and the increasing proportion of electric vehicles, respectively. Combining traffic congestion scenarios S1-S6 and fleet composition scenarios F0-F3, a total of 18 scenarios were studied (Table 2 and Table 3). For example, scenario S2F0 quantified the vehicle emissions when the traffic condition is S2 and the fleet composition is F0, which represents the current rush-hour traffic condition and current on-road fleet compositions. Similarly, scenario S5F0 quantified the vehicle emissions when the traffic condition is S5 and the fleet composition is F0, which represents the current traffic condition during off-peak hours and current on-road fleet compositions. In the subsequent comparison, scenarios S2F0 and S5F0 were used as the benchmark scenarios for rush hour and off-peak hours, respectively. Overall, our results show that under the ideal situations of no traffic congestion (i.e., S1 and S4), the emissions of CO, HC, and  $\mathrm{NO}_{\mathrm{x}}$  will be significantly reduced with the continuous upgrading of fleet composition (from F0 to F2). However, the impacts of traffic

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/9f92dccd-7045-4b38-83b7-43b51761fb13/6584e63fbef8bed8b6e4f31d5b120a39c5221624c6bd08df147ac47dd20430a4.jpg)

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/9f92dccd-7045-4b38-83b7-43b51761fb13/3adb10854df0e4bab832561b6fa4b2f3cc7aeb7363d463693c2e34754b0564f7.jpg)

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/9f92dccd-7045-4b38-83b7-43b51761fb13/9ab9c90e36d78fa53f19f7b8c230807a2a9a893cf31af25008b1b78890a52c64.jpg)  
Speed (km/h)

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/9f92dccd-7045-4b38-83b7-43b51761fb13/99165c057291da186165218decb076f805540c19e6b500885c15e69c1db6f209.jpg)

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/9f92dccd-7045-4b38-83b7-43b51761fb13/ca7f4cccbbd1ebebf0ccd82a15d8b236cc185871da5f200e51b54837c1d735bf.jpg)  
Fig. 6. (a) Vehicle emission factors under different driving speeds. (b) Spatial distribution of hourly average on-road vehicle driving speeds (in km/h) during rush hours (from 07:00 to 09:00 and from 16:30 to 18:30 local time). (c) Spatial distribution of hourly average on-road vehicle driving speeds (in km/h) during off-peak hours (from 9:00 to 16:30 and from 18:30 to 7:00 local time). (d) Spatial distribution of hourly average traffic fluxes during rush hours (from 07:00 to 09:00 and from 16:30 to 18:30 local time). (e) Spatial distribution of hourly average traffic fluxes during off-peak hours (from 9:00 to 16:30 and from 18:30 to 7:00 local time).

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/9f92dccd-7045-4b38-83b7-43b51761fb13/42732f9c3dc2213c338c758a4e009fe9a923cccb6647d09070af916089702e17.jpg)

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/9f92dccd-7045-4b38-83b7-43b51761fb13/20426c7f129aed6eceec49ccc6c75dea6d8a8cbf5e631d449ed4654408478830.jpg)

congestion will offset the benefits of fleet upgrading under the conditions of realistic traffic (i.e., S2 and S5) and more serious traffic congestion (S3 and S6).

The quantitative results of traffic congestion scenarios show that during the rush hours, if the traffic congestion were effectively alleviated (S1F0), the hourly emissions of CO, HC, and  $\mathrm{NO}_{\mathrm{x}}$  could be reduced by  $-19.4\%$

Table 2 Scenarios during rush hours (from 07:00 to 09:00 and from 16:30 to 18:30 local time) and their relative percentage changes in on-road vehicle emissions compared to S2F0.  

<table><tr><td>Scenarios</td><td>Traffic conditions</td><td>Fleet compositions</td><td>NOx</td><td>CO</td><td>HC</td></tr><tr><td>S1F0</td><td>S1</td><td>F0</td><td>-12.4 %</td><td>-19.4 %</td><td>-28.4 %</td></tr><tr><td>S2F0</td><td>S2</td><td>F0</td><td>0</td><td>0</td><td>0</td></tr><tr><td>S3F0</td><td>S3</td><td>F0</td><td>10.1 %</td><td>16.4 %</td><td>21.4 %</td></tr><tr><td>S1F1</td><td>S1</td><td>F1</td><td>-33.5 %</td><td>-36.3 %</td><td>-40.3 %</td></tr><tr><td>S2F1</td><td>S2</td><td>F1</td><td>-1.9 %</td><td>-3.0 %</td><td>-4.3 %</td></tr><tr><td>S3F1</td><td>S3</td><td>F1</td><td>6.7 %</td><td>10.9 %</td><td>13.8 %</td></tr><tr><td>S1F2</td><td>S1</td><td>F2</td><td>-51.9 %</td><td>-51.6 %</td><td>-50.3 %</td></tr><tr><td>S2F2</td><td>S2</td><td>F2</td><td>-3.7 %</td><td>-5.6 %</td><td>-8.1 %</td></tr><tr><td>S3F2</td><td>S3</td><td>F2</td><td>3.2 %</td><td>5.9 %</td><td>7.1 %</td></tr></table>

$-28.4\%$  and  $-12.4\%$  respectively. If superimposed upgrading of fleet composition (S1F2), a reduction of around  $50\%$  in CO, HC, and  $\mathrm{NO}_{\mathrm{x}}$  emissions was observed. In contrast, if the traffic congestion were aggravated (S3F0), this increased CO, HC, and  $\mathrm{NO}_{\mathrm{x}}$  emissions by  $16.4\%$ $21.4\%$  ,and  $10.1\%$  , respectively (Fig. 7, Figs. S9-S10, Table 2). Increasing traffic congestion completely offset the reductions of pollutants achieved by emission

Table 3 Scenarios during off-peak hours (from 9:00 to 16:30 and from 18:30 to 7:00 local time) and their relative percentage changes in on-road vehicle emissions compared to S5F0.  

<table><tr><td>Scenarios</td><td>Traffic conditions</td><td>Fleet compositions</td><td>NOx</td><td>CO</td><td>HC</td></tr><tr><td>S4F0</td><td>S4</td><td>F0</td><td>-9.6 %</td><td>-14.2 %</td><td>-21.4 %</td></tr><tr><td>S5F0</td><td>S5</td><td>F0</td><td>0</td><td>0</td><td>0</td></tr><tr><td>S6F0</td><td>S6</td><td>F0</td><td>5.2 %</td><td>7.8 %</td><td>11.4 %</td></tr><tr><td>S4F1</td><td>S4</td><td>F1</td><td>-31.4 %</td><td>-32.2 %</td><td>-34.4 %</td></tr><tr><td>S5F1</td><td>S5</td><td>F1</td><td>-1.3 %</td><td>-1.9 %</td><td>-3.0 %</td></tr><tr><td>S6F1</td><td>S6</td><td>F1</td><td>3.3 %</td><td>4.9 %</td><td>6.8 %</td></tr><tr><td>S4F2</td><td>S4</td><td>F2</td><td>-50.3 %</td><td>-48.5 %</td><td>-45.4 %</td></tr><tr><td>S5F2</td><td>S5</td><td>F2</td><td>-2.9 %</td><td>-3.9 %</td><td>-5.9 %</td></tr><tr><td>S6F2</td><td>S6</td><td>F2</td><td>0.8 %</td><td>1.8 %</td><td>2.3 %</td></tr></table>

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/9f92dccd-7045-4b38-83b7-43b51761fb13/c76f1920f449da450eefd86d007a9faea141f2c4f8688aa50556473f6e40295c.jpg)  
Fig. 7. Hourly average on-road vehicle emission intensities under different congestion scenarios during rush hours (from 07:00 to 09:00 and from 16:30 to 18:30 local time).

standard upgrading, and even increased on-road vehicle emissions instead (see S1F2, S2F2, S3F2 in Table 2). Similarly, if the traffic congestion were effectively alleviated (S4F0) during the off-peak hours, the hourly emissions of CO, HC, and  $\mathrm{NO}_{\mathrm{x}}$  could be reduced by  $-14.2\%$ ,  $-21.4\%$ , and  $-9.6\%$  respectively, but increased by  $7.8\%$ ,  $11.4\%$ , and  $5.2\%$  if the congestions were aggravated (S6F0) (Figs. S11-S13, Table 3). Note that, in the southern areas of the district, the emission intensities in the arterial and residential streets far exceeded ( $\sim 5$  times) those in the northern areas (Fig. 7, Fig. S11). These high emission hotspots were mainly attributed to the high traffic fluxes and low traffic speeds. Frequent traffic congestion, accelerations and decelerations led to significant increases in vehicles' fuel consumption. Thus, better traffic management policies should be applied to reduce vehicles' energy consumption and mitigate pollutant emissions as well (Huang et al., 2020b).

# 3.5. Emission profiles under the different operating modes

To evaluate the effects of driving conditions on vehicle emissions, we quantified vehicle emissions under 11 speed bins. Very different trends were observed in the variations of different pollutants with the changes of operating modes (Fig. 8). The unqualified vehicles (those failed in the annual inspection due to over high emissions), made up  $7.6\%$  of the total 159,051 vehicles. As shown in Fig. 8, HC was not sensitive to the changes in operating modes, while NO showed good correlations with driving speeds. Slight variations were observed in CO concentrations with the increase of speeds. Comparisons of qualified and unqualified vehicles indicate that the exhaust concentrations of unqualified vehicles were higher than qualified vehicles by a factor of 5-9 in (Fig. 8(a)).

Both qualified and unqualified vehicles show slight increases in CO concentrations as the driving speed increased gradually. The CO concentrations of qualified and unqualified vehicles increased by  $17.2\%$  (from  $7.8\%$  to  $9.1\%$ ) and  $24.6\%$  (from  $67.5\%$  to  $84.1\%$ ), respectively. In contrast, HC concentrations of unqualified vehicles exhibited a slightly descending trend while those of qualified vehicles stayed relatively stable when the driving speeds increased. The HC concentrations of qualified and unqualified

vehicles decreased by  $16.0\%$  (from 124.50 to  $104.56~\mathrm{ppm}$ ) and  $6.7\%$  (from 22.50 to  $21.00~\mathrm{ppm}$ ), respectively. What is striking in this figure is that NO concentrations of unqualified vehicles showed a strong positive correlation with driving speeds. As the vehicle driving speeds increased, the NO concentrations of unqualified vehicles increased sharply, with a maximum concentration of  $866~\mathrm{ppm}$  in the speed bin of  $45 - 50~\mathrm{km/h}$ , being four times higher than during the  $0 - 5~\mathrm{km/h}$  speed bin. Similarly, NO concentrations of qualified vehicles increased considerably with driving speeds with the maximum concentration of  $107~\mathrm{ppm}$  obtained in the speed bin of  $45 - 50~\mathrm{km/h}$ , being three times higher than those in the  $0 - 5~\mathrm{km/h}$  speed bin (34 ppm).

# 4. Conclusions

Based on the newly updated big data of high-resolution vehicle emission profiles, the emission characteristics of light gasoline vehicles were analyzed in this study. The extent to which pollutant emission factors varied with different emission standards, vehicle manufactures and operating modes were illustrated in detail. The significant influence of traffic congestion on vehicle emissions was addressed with the support of the real-time on-road traffic monitoring system in Xiaoshan District. Additionally, several approaches to reducing on-road vehicle emissions under realistic conditions were proposed from a big data perspective. The results showed that the emissions of LDGVs in China have decreased significantly (75.7–86.2 %) with the continuous upgrading of emission standards (i.e., from China 2 to China 5) in the past 13 years. Heavy-tailed distributions were found in CO, HC, and  $\mathrm{NO}_{\mathrm{x}}$  emission factors. The results showed that the  $10\%$  high emitters contributed  $>60\%$  to the total fleet emissions, significantly higher than previous studies. In order to achieve greater emission reductions in the future, it is necessary to strengthen the gradual replacements of pre-China 3 vehicles, especially those in the  $10\%$  high emitters. Large differences were found in the emissions of vehicles produced by different manufacturers. It was found that the emission factors of the cleanest and most polluted vehicles produced by different manufacturers differed by 33–49 times. Therefore, in the future, the supervision of

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/9f92dccd-7045-4b38-83b7-43b51761fb13/61313ba23e7b2113228783b65ec260d5ddc9773f338a8c9c2616a12c5ab48b2d.jpg)  
a

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/9f92dccd-7045-4b38-83b7-43b51761fb13/95e2d66059de8f0d5939dcf9f04e8b507bccb179d506fef594bd06fc585c971d.jpg)

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/9f92dccd-7045-4b38-83b7-43b51761fb13/f720b7603861b202b093fe387f49cc4d9f61e475878a53e8d87d8b139fcc10be.jpg)

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/9f92dccd-7045-4b38-83b7-43b51761fb13/444d10e0fbaf27b06c897123f8d1d719272dc1ffba1e5081f54b0089e8d7115f.jpg)  
b  
Fig. 8. The comparison of vehicle emissions between qualified and unqualified vehicles, including 104,548 qualified vehicles and 7363 unqualified vehicles. Mean values and  $95\%$  confidence intervals are shown in the inset.

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/9f92dccd-7045-4b38-83b7-43b51761fb13/58ba4a9e4699a6529e503645df441649f40ddccdf9b315fc2991448251e72e8a.jpg)

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/9f92dccd-7045-4b38-83b7-43b51761fb13/380eae7342998b245d60bf55ee3accf0c41ccd5ee827afbdd677792e60f9f6cb.jpg)

the high-emission manufacturers (i.e., requiring the improvement of exhaust treatment facilities) should be strengthened. Unexpected high emissions were found at the slow driving speeds  $(< 5\mathrm{km / h})$ . Further spatial distribution analyses also showed extremely high emissions under traffic congestion conditions. Increasing traffic congestion completely offset the reduction of pollutants achieved by emission standards upgrading, and even increased on-road vehicle emissions instead.

The implication of the present results of this study for other cities mainly lies in more refined and efficient management of vehicle emissions. To achieve effective reductions of vehicle emissions in the future, the following aspects should be strengthened: First, identify high-emission vehicles based on local I/M dataset and set specific restrictions on the activity areas or travel time for ultra-high emission vehicles; Second, enhance the supervision of vehicle manufacturers with extremely high emissions; Third, the cooperation between environmental protection and traffic command departments should be strengthened to achieve win-win goals, not only to alleviate traffic congestion, but also to reduce the emissions of air pollutants.

Due to the limited time span of the vehicle emissions dataset, the interannual variation characteristics of emissions of the high emitters cannot be further analyzed. Future research can fill this gap to explore more suitable cleaning alternative cycles for the high emitters. This study has investigated the contributions of the  $10\%$  high emitters to the total fleet emissions, but the travel behavior and typical activity trajectories of these high emitters still need to be explored. In the follow-up research, the driving trajectories and hot spots of high emission vehicles can be obtained based on the accurate matching of vehicle-specific emission factors and vehicle-specific activity data, so as to provide more effective support for the managements and controls of target high emission vehicles. The analysis of environmental impacts of traffic congestion reveals the importance of traffic congestion controls on air pollutant reductions. Existing on-road vehicle emission models (i.e., IVE and COPERT (Choudhary and Gokhale, 2019)) usually lack considerations of traffic congestion when calculating on-road emissions, so it can be optimized in future research to better reflect the realistic on-road emissions.

# CRediT authorship contribution statement

S.Y., P.L., and X. C. designed this research, developed the model, performed the analysis, and wrote the paper. L. J., Y. X., L. W., J. Y., T. H., Y. Z., M. L., Z. L., Z. S., J. L., Y. J., X. Z., Y. Z., D. R., and J. H. S. made contributions to discussing and improving this research.

# Data availability

Data will be made available on request.

# Declaration of competing interest

The authors declare that they have no known competing financial interests or personal relationships that could have appeared to influence the work reported in this paper.

# Acknowledgments

This study is supported by the National Natural Science Foundation of China (No. 42175084, 21577126, and 41561144004), Department of Science and Technology of China (No. 2018YFC0213506 and 2018YFC0213503), and National Research Program for Key Issues in Air Pollution Control in China (No. DQGG0107). Pengfei Li is supported by National Natural Science Foundation of China (No. 22006030), Science and Technology Program of Hebei Province (22343702D), Research Foundation of Education Bureau of Hebei (BJ2020032), and Initiation Fund of Hebei Agricultural University (412201904). YZ acknowledged support from the U.S. NOAA Office of Climate AC4 Program (NA20OAR4310293).

# Appendix A. Supplementary data

Supplementary data to this article can be found online at https://doi.org/10.1016/j.scitotenv.2022.157581.

# References

Alobaidi, M.K., Badri, R.M., Salman, M.M., 2020. Evaluating the negative impact of traffic congestion on air pollution at signalized intersection. IOP Conf. Ser. Mater. Sci. Eng. 737, 012146. https://doi.org/10.1088/1757-899X/737/1/012146.  
Baidu Map, 2021. 2021 China urban transportation report. Available from: https://huiyan.baidu.com/reports/landing?id=111&role=traffic.  
Beaton, S.P., Bishop, G.A., Zhang, Y., Ashbaugh, L.L., Lawson, D.R., Stedman, D.H., 1995. On-road vehicle emissions: regulations, costs, and benefits. Science 268, 991-993. https://doi.org/10.1126/science.268.5213.991.  
Bernard, Y., Tietge, U., German, J., Muncrief, R., 2018. Determination of real-world emissions from passenger vehicles using remote sensing data. https://www.theicct.org/publications/real-world-Emis.  
Bishop, G.A., Hauge, M.J., 2018. The story of ever diminishing vehicle tailpipe emissions as observed in the Chicago, Illinois area. Environ. Sci. Technol. 52, 7587-7593. https://doi.org/10.1021/acs.est.8b00926.  
Cao, X., Yao, Z., Shen, X., Ye, Y., Jiang, X., 2016. On-road emission characteristics of VOCs from light-duty gasoline vehicles in Beijing, China. Atmos. Environ. 124, 146-155. https://doi.org/10.1016/j.atmosenv.2015.06.019.  
Chang, Y., Zou, Z., Deng, C., Huang, K., Collett, J.L., Lin, J., Zhuang, G., 2016. The importance of vehicle emissions as a source of atmospheric ammonia in the megacity of Shanghai. Atmos. Chem. Phys. 16, 3577-3594. https://doi.org/10.5194/acp-16-3577-2016.  
Chen, Y., Borken-Kleefeld, J., 2016.  $\mathrm{NO}_{\mathrm{x}}$  emissions from diesel passenger cars worsen with age. Environ. Sci. Technol. 50, 3327-3332. https://doi.org/10.1021/acs.est.5b04704.  
Chen, Y., Zhang, Y., Borken-Kleefeld, J., 2019. When is enough? Minimum sample sizes for on-road measurements of car emissions. Environ. Sci. Technol. 53, 13284-13292. https://doi.org/10.1021/acs.est.9b04123.  
Choudhary, A., Gokhale, S., 2016. Urban real-world driving traffic emissions during interruption and congestion. Transp. Res. Part D: Transp. Environ. 43, 59-70. https://doi.org/10.1016/j.trd.2015.12.006.  
Choudhary, A., Gokhale, S., 2019. On-road measurements and modelling of vehicular emissions during traffic interruption and congestion events in an urban traffic corridor. Atmos. Pollut. Res. 10, 480-492. https://doi.org/10.1016/j.apr.2018.09.008.  
Davison, J., Rose, R.A., Farren, N.J., Wagner, R.L., Murrells, T.P., Carslaw, D.C., 2021. Verification of a National Emission Inventory and influence of on-road vehicle manufacturer-level emissions. Environ. Sci. Technol. 55, 4452-4461. https://doi.org/10.1021/acs.est.0c08363.  
Deng, F., Lv, Z., Qi, L., Wang, X., Shi, M., Liu, H., 2020. A big data approach to improving the vehicle emission inventory in China. Nat. Commun. 11, 1-12. https://doi.org/10.1038/s41467-020-16579-w.  
Farren, N.J., Davison, J., Rose, R.A., Wagner, R.L., Carslaw, D.C., 2020. Underestimated ammonia emissions from road vehicles. Environ. Sci. Technol. 54, 15689-15697. https://doi.org/10.1021/acs.est.0c05839.  
Feng, L., Liao, W., 2016. Legislation, plans, and policies for prevention and control of air pollution in China: achievements, challenges, and improvements. J. Clean. Prod. 112, 1549-1558. https://doi.org/10.1016/j.jclepro.2015.08.013.  
Feng, J., Zhang, Y., Song, W., Deng, W., Zhu, M., Fang, Z., Ye, Y., Fang, H., Wu, Z., Lowther, S., Jones, K.C., Wang, X., 2020. Emissions of nitrogen oxides and volatile organic compounds from liquefied petroleum gas-fueled taxis under idle and cruising modes. Environ. Pollut. 267, 115623. https://doi.org/10.1016/j.envpol.2020.115623.  
Franco, V., Kousoulidou, M., Muntean, M., NtziaChristos, L., Hausberger, S., Dilara, P., 2013. Road vehicle emission factors development: a review. Atmos. Environ. 70, 84-97. https://doi.org/10.1016/j.atmosenv.2013.01.006.  
Fu, M., Ge, Y., Tan, J., Zeng, T., Liang, B., 2012. Characteristics of typical non-road machinery emissions in China by using portable emission measurement system. Sci. Total Environ. 437, 255-261. https://doi.org/10.1016/j.scitotenv.2012.07.095.  
He, L., Hu, J., Yang, L., Li, Z., Zheng, X., Xie, S., Zu, L., Chen, J., Li, Y., Wu, Y., 2019. Realworld gaseous emissions of high-mileage taxi fleets in China. Sci. Total Environ. 659, 267-274. https://doi.org/10.1016/j.scitotenv.2018.12.336.  
Hua, X.-S., 2018. The city brain: towards real-time search for the real-world. The 41st International ACM SIGIR Conference on Research & Development in Information Retrieval. Association for Computing Machinery, New York, NY, USA, pp. 1343-1344. https://doi.org/10.1145/3209978.3210214.  
Huang, C., Tao, S., Lou, S., Hu, Q., Wang, Hongli, Wang, Q., Li, L., Wang, Hongyu, Liu, J., Quan, Y., Zhou, L., 2017. Evaluation of emission factors for light-duty gasoline vehicles based on chassis dynamometer and tunnel studies in Shanghai, China. Atmos. Environ. 169, 193-203. https://doi.org/10.1016/j.atmosenv.2017.09.020.  
Huang, Y., Organ, B., Zhou, J.L., Surawski, N.C., Hong, G., Chan, E.F.C., Yam, Y.S., 2018a. Remote sensing of on-road vehicle emissions: mechanism, applications and a case study from Hong Kong. Atmos. Environ. 182, 58-74. https://doi.org/10.1016/j.atmosenv.2018.03.035.  
Huang, Y., Organ, B., Zhou, J.L., Surawski, N.C., Hong, G., Chan, E.F.C., Yam, Y.S., 2018b. Emission measurement of diesel vehicles in Hong Kong through on-road remote sensing: performance review and identification of high-emitters. Environ. Pollut. 237, 133-142. https://doi.org/10.1016/j.envpol.2018.02.043.  
Huang, Y., Surawski, N.C., Yam, Y.S., Lee, C.K.C., Zhou, J.L., Organ, B., Chan, E.F.C., 2020a. Re-evaluating effectiveness of vehicle emission control programmes targeting high-emitters. Nat. Sustain. 3, 904-907. https://doi.org/10.1038/s41893-020-0573-y.

Huang, W., Guo, Y., Xu, X., 2020b. Evaluation of real-time vehicle energy consumption and related emissions in China: a case study of the Guangdong-Hong Kong-Macao greater Bay Area. J. Clean. Prod. 263, 121583. https://doi.org/10.1016/j.jclepro.2020.121583.  
Jiang, L., Xia, Y., Wang, L., Chen, X., Ye, J., Hou, T., Wang, L., Zhang, Y., Li, M., Li, Z., Song, Z., Jiang, Y., Liu, W., Li, P., Rosenfeld, D., Seinfeld, J.H., Yu, S., 2021. Hyperfine-resolution mapping of on-road vehicle emissions with comprehensive traffic monitoring and an intelligent transportation system. Atmos. Chem. Phys. 21, 16985-17002. https://doi.org/10.5194/acp-21-16985-2021.  
Jing, B., Wu, L., Mao, H., Gong, S., He, J., Zou, C., Song, G., Li, X., Wu, Z., 2016. Development of a vehicle emission inventory with high temporal-spatial resolution based on NRT traffic data and its impact on air pollution in Beijing - part 1: development and evaluation of vehicle emission inventory. Atmos. Chem. Phys. 16, 3161-3170. https://doi.org/10.5194/acp-16-3161-2016.  
Ko, Y.W., Cho, C.H., 2006. Characterization of large fleets of vehicle exhaust emissions in middle Taiwan by remote sensing. Sci. Total Environ. 354, 75-82. https://doi.org/10.1016/j.scitotenv.2005.05.040.  
Ko, J., Myung, C.L., Park, S., 2019. Impacts of ambient temperature, DPF regeneration, and traffic congestion on  $\mathrm{NO}_x$  emissions from a euro 6-compliant diesel vehicle equipped with an LNT under real-world driving conditions. Atmos. Environ. 200, 1-14. https://doi.org/10.1016/j.atmosenv.2018.11.029.  
Kumar, R., Parida, P., Shukla, S., Saleh, W., 2015. MOVES model for idling emission of signalised junction in developing country. World J. Sci. Technol. Sustain. Dev. 12, 25-38. https://doi.org/10.1108/wjstds-06-2014-0009.  
Lawrence, S., Sokhi, R., Ravindra, K., 2016. Quantification of vehicle fleet  $\mathrm{PM}_{10}$  particulate matter emission factors from exhaust and non-exhaust sources using tunnel measurement techniques. Environ. Pollut. 210, 419-428. https://doi.org/10.1016/j.envpol.2016.01.011.  
Li, M., Yu, L., Asce, M., Zhai, Z., He, W., Song, G., 2016. Development of emission factors for an urban road network based on speed distributions. J. Transp. Eng. 04016036, 1-9. https://doi.org/10.1061/(ASCE)TE.1943-5436.0000858.  
Liu, Y., Ma, J., Li, L., Lin, X., Xu, W., Ding, H., 2018. A high temporal-spatial vehicle emission inventory based on detailed hourly traffic data in a medium-sized city of China. Environ. Pollut. 236, 324-333. https://doi.org/10.1016/j.envpol.2018.01.068.  
Lu, J., Li, B., Li, H., Al-Barakani, A., 2021. Expansion of city scale, traffic modes, traffic congestion, and air pollution. Cities 108, 102974. https://doi.org/10.1016/j.cities.2020.102974.  
Ministry of Ecology and Environment of the People's Republic of China (MEEPRC), 2014, National Technical Guidelines of the On-Road Vehicle Emissions Inventory, pp. 26-49. Available from: https://www.mee.gov.cn/gkml/hbbb/bbg/201501/t20150107_293955.htm.  
Ministry of Ecology and Environment of the People's Republic of China (MEEPRC), 2018. GB 18285-2018 emission limits and measuring methods of pollutants from gasoline vehicles. Available from: http://mee.gov.cn/ywgz/fgbz/bz/bzwb/dqhjhbh/dqdydwwpfbz/201811/t20181113_673593.shtml.  
Ministry of Ecology and Environment of the People's Republic of China (MEEPRC), 2019. China mobile source environmental management annual report. Available from: https://www.mee.gov.cn/hjzl/sthjk/ydyhgl/201909/P020190905586230826402.pdf.  
Ministry of Ecology and Environment of the People's Republic of China (MEEPRC), 2021. China Mobile Source Environmental Management Annual Report (2021). Available from https://www.mee.gov.cn/hjzl/sthjk/ydyhjlq/202109/W020210910400449015882.pdf.  
Mera, Z., Fonseca, N., López, J., Casanova, J., 2019. Analysis of the high instantaneous  $\mathrm{NO}_x$  emissions from euro 6 diesel passenger cars under real driving conditions. Appl. Energy 242, 1074-1089. https://doi.org/10.1016/j.apenergy.2019.03.120.  
Pu, Y., Yang, C., Liu, H., Chen, Z., Chen, A., 2015. Impact of license plate restriction policy on emission reduction in Hangzhou using a bottom-up approach. Transp. Res. Part D Transp. Environ. 34, 281-292. https://doi.org/10.1016/j.trd.2014.11.007.  
Redmon, J., Divvala, S., Girshick, R., Farhadi, A., 2016. You only look once: unified, real-time object detection. 2016 IEEE Conference on Computer Vision and Pattern Recognition (CVPR), 2016, pp. 779-788. https://doi.org/10.1109/CVPR.2016.91.  
Saikawa, E., Kurokawa, J., Takigawa, M., Borken-Kleefeld, J., Mauzerall, D.L., Horowitz, L.W., Ohara, T., 2011. The impact of China's vehicle emissions on regional air quality in 2000 and 2020: a scenario analysis. Atmos. Chem. Phys. 11, 9465-9484. https://doi.org/10.5194/acp-11-9465-2011.  
Saliba, G., Saleh, R., Zhao, Y., Presto, A.A., Lambe, A.T., Frodin, B., Sardar, S., Maldonado, H., Maddox, C., May, A.A., Drozd, G.T., Goldstein, A.H., Russell, L.M., Hagen, F., Robinson,

A.L., 2017. Comparison of gasoline direct-injection (GDI) and port fuel injection (PFI) vehicle emissions: emission certification standards, cold-start, secondary organic aerosol formation potential, and potential climate impacts. Environ. Sci. Technol. 51, 6542-6552. https://doi.org/10.1021/acs.est.6b06509.  
Sentoff, K.M., Robinson, M.K., Holmen, B.A., 2010. Second-by-second characterization of cold-start gas-phase and air toxic emissions from a light-duty vehicle. Transp. Res. Rec. 2158, 95-104. https://doi.org/10.3141/2158-12.  
Shancita, I., Masjuki, H.H., Kalam, M.A., Fattah, I.M.R., Rashed, M.M., Rashedul, H.K., 2014. A review on idling reduction strategies to improve fuel economy and reduce exhaust emissions of transport vehicles. Energy Convers. Manag. 88, 794-807. https://doi.org/10.1016/j.enconman.2014.09.036.  
Sun, S., Jin, J., Xia, M., Liu, Y., Gao, M., Zou, C., Wang, T., Lin, Y., Wu, L., Mao, H., Wang, P., 2020. Vehicle emissions in a middle-sized city of China: current status and future trends. Environ. Int. 137, 105514. https://doi.org/10.1016/j.envint.2020.105514.  
Wang, J.M., Jeong, C., Zimmerman, N., Healy, R.M., Evans, G.J., 2018. Real world vehicle fleet emission factors: seasonal and diurnal variations in traffic related air pollutants. Atmos. Environ. 184, 77-86. https://doi.org/10.1016/j.atmosenv.2018.04.015.  
Wen, Y., Zhang, S., Zhang, J., Bao, S., Wu, X., Yang, D., Wu, Y., 2020. Mapping dynamic road emissions for a megacity by using open-access traffic congestion index data. Appl. Energy 260, 114357. https://doi.org/10.1016/j.apenergy.2019.114357.  
Wu, Y., Zhang, S., Hao, J., Liu, H., Wu, X., Hu, J., Walsh, M.P., Wallington, T.J., Zhang, K.M., Stevanovic, S., 2017. On-road vehicle emissions and their control in China: a review and outlook. Sci. Total Environ. 574, 332-349. https://doi.org/10.1016/j.scitotenv.2016.09.040.  
Wu, L., Chang, M., Wang, X., Hang, J., Zhang, J., Wu, L., Shao, M., 2020. Development of the real-time on-road emission (ROE v1.0) model for street-scale air quality modeling based on dynamic traffic big data. Geosci. Model Dev. 13, 23-40. https://doi.org/10.5194/gmd-13-23-2020.  
Xia, Y., Jiang, L., Wang, L.L., Chen, X., Ye, J., Hou, T., Wang, L.L., Zhang, Y., Li, M., Li, Z., Song, Z., Jiang, Y., Liu, W., Li, P., Rosenfeld, D., Seinfeld, J.H., Yu, S., 2022. Rapid assessments of light-duty gasoline vehicle emissions using on-road remote sensing and machine learning. Sci. Total Environ. 815, 152771. https://doi.org/10.1016/j.scitotenv.2021.152771.  
Yang, L., Zhang, S., Wu, Y., Chen, Q., Niu, T., Huang, X., Zhang, S., Zhang, L., Zhou, Y., Hao, J., 2016. Evaluating real-world  $\mathrm{CO}_{2}$  and  $\mathrm{NO}_{\mathrm{x}}$  emissions for public transit buses using a remote wireless on-board diagnostic (OBD) approach. Environ. Pollut. 218, 453-462. https://doi.org/10.1016/j.envpol.2016.07.025.  
Yang, Z., Liu, Y., Wu, L., Martinet, S., Zhang, Y., Andre, M., 2020a. Real-world gaseous emission characteristics of euro 6b light-duty gasoline- and diesel-fueled vehicles. Transp. Res. D 78, 102215. https://doi.org/10.1016/j.trd.2019.102215.  
Yang, Zhiwen, Peng, Jianfei, Wu, Lin, Ma, Chao, Zou, Chao, Wei, Ning, Zhang, Yanjie, Liu, Yao, Andre, Michel, Li, Dong, Mao, Hongjun, 2020b. Speed-guided intelligent transportation system helps achieve low-carbon and green traffic: evidence from real-world measurements. J. Clean. Prod. 268, 122230. https://doi.org/10.1016/j.jclepro.2020.122230.  
Yu, Q., Li, T., Li, H., 2016. Improving urban bus emission and fuel consumption modeling by incorporating passenger load factor for real world driving. Appl. Energy 161, 101-111. https://doi.org/10.1016/j.apenergy.2015.09.096.  
Zhang, S., Wu, Y., Huang, R., Wang, J., Yan, H., Zheng, Y., Hao, J., 2016. High-resolution simulation of link-level vehicle emissions and concentrations for air pollutants in a traffic-populated eastern asian city. Atmos. Chem. Phys. 16, 9965-9981. https://doi.org/10.5194/acp-16-9965-2016.  
Zhang, Q., Wu, L., Fang, X., Liu, M., Zhang, J., Shao, M., Lu, S., Mao, H., 2018. Emission factors of volatile organic compounds (VOCs) based on the detailed vehicle classification in a tunnel study. Sci. Total Environ. 624, 878-886. https://doi.org/10.1016/j.scitotenv.2017.12.171.  
Zhang, Y., Deng, W., Hu, Q., Wu, Z., Yang, W., Zhang, H., Wang, Z., Fang, Z., Zhu, M., Li, S., Song, W., Ding, X., Wang, X., 2020. Comparison between idling and cruising gasoline vehicles in primary emissions and secondary organic aerosol formation during photochemical ageing. Sci. Total Environ. 722, 137934. https://doi.org/10.1016/j.scitotenv.2020.137934.