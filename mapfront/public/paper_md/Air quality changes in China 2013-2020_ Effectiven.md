# Air quality changes in China 2013-2020: Effectiveness of clean coal technology policies

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/c4f64a11-f495-42ce-8d5d-d616f8721d59/cedb007e6d6a4d83acb18da497ca7432242dfd0dd23dfe1ff4a840e92aebcc9a.jpg)

Boling Zhang a, Sixia Wang a, Dongdong Wang a, Qian Wang a, Xiaoyi Yang b, Ruipeng Tong a,\*

$^{a}$  School of Emergency Management and Safety Engineering, China University of Mining and Technology - Beijing, Beijing, 100083, China

$^{b}$  School of Environmental and Chemical Engineering, Jiangsu Ocean University, China

# ARTICLEINFO

Handling editor: Mingzhou Jin

Keywords:

Coal-based clean energy

Air quality

Clean coal technology policies

Deep learning approaches

Energy transformation

# ABSTRACT

Clean and efficient use of coal in China entered the implementation stage in 2015, and a series of policies were established to promote the sustainable development of clean coal technologies (CCTs). However, the long-term effects of the clean coal technology policies (CCTPs) have not been evaluated, and the outbreak of coronavirus disease 2019 (COVID-19) would bring great uncertainty regarding the effectiveness evaluation. Employing deep learning approaches and spatial autocorrelation analysis, the present work intended to explore the air quality variation before and after the implementation of CCTPs, and investigate the association between air quality and socioeconomic factors to explore the internal mechanism of air quality improvement. Results showed that after implementing CCTPs, the air quality index (AQI) had an average reduction of  $18.82\%$  and the identical drop in air pollution in 2018 implied a 2-year time lag of CCTPs. Additionally, emission reduction and deindustrialization were explored as two promising ways to improve air quality while promoting energy transformation. The findings indicated that the Chinese government ought to pay more attention to long-term plans; industrial restructuring and environmental protection should be insisted upon to realize sustainable energy development. By providing a perspective on air quality improvement after the policies are implemented, this study can lead practitioners and academia to a comprehensive and objective view of clean coal policies.

# 1. Introduction

Energy resource plays a critical role in supporting the modern economy and is one of the important foundations of social development. With the rapid progress of urbanization and industrialization, there is a sharp increase in energy consumption around the globe (Cheng et al., 2021; Elio et al., 2021). It is proposed that the global energy demand will double by 2050 and triple by 2100, and almost  $70\%$  of the projected increase is in emerging markets and developing economies (Guney and Tepe, 2017; IEA, 2021). Amongst, China has shown a substantial increase in energy demand in the past years and is likely to continue this trend in the future, already being the largest energy demander worldwide (Burandt et al., 2019). Although the share of coal in the overall energy mix is slightly decreasing each year, China's energy system would still be dominated by coal in the near term, which accounts for nearly  $56.8\%$  of the energy structure (Tang et al., 2017; Li et al., 2020). The vast majority of its coal is being applied to the industrial and heating sectors. However, coal burning would produce harmful pollutants such as nitrogen oxides  $(\mathrm{NO}_x)$ , and particulate matter (PM), which lead to

severe air pollution, and affect the lives of humans, animals and plants directly (Yuan et al., 2018; Wang et al., 2021). It is reported that coal-related carbon emissions account for  $70\% -80\%$  of the total emissions in China (Xie et al., 2019), and the massive use of coal caused the smog sweeping across most cities of northern China (Sun et al., 2018).

The conflicts between abundant energy consumption and urgent environmental protection are sharper than ever before and have posed great pressure on Chinese sustainable economic growth in the new normal stage (Jiang et al., 2020). To solve these conflicts, the government has been shifting the energy production and utilization way from the traditional investment-led and resource-driven development mode to the sustainability-driven development mode which is low-carbon, waste minimizing, clean, and resource-efficient (Zeb et al., 2014). Specifically, for the coal industry, it is generally believed that clean and efficient use of coal plays an explicitly important role in the energy transformation, adding to a solid support for China's sustainable development, and has been verified as a tremendously important way to realize carbon peak and neutrality goals. Correspondingly, a circular economy industry chain of CCTs covering the life cycle of coal resources

grows up gradually in China, "coal development-coal with high quality-clean energy-the integration of coal-based materials and chemicals".

On the policy side, the Chinese government explicitly proposed to promote the clean and efficient use of coal in 2014. And subsequently, two significant specialized action plans were published in 2015 (Action Plan for Clean and Efficient Use of Coal in Industry and Action Plan for Clean and Efficient Use of Coal), signifying that the clean and efficient use of coal in China has entered the implementation stage since 2015 (Zhu, 2019). Herein, the former plan chose four coal-dominated industries as key objects, and defined 21 types of critical technologies for clean and efficient coal utilization in the industry; the latter plan proposed the subjects involved in CCTPs include the government, enterprises, market, and the public, and all of the coal-rich districts in China were selected as key regions. Currently, a series of laws, regulations, and policies have been brought into effect, to alleviate air pollution and accelerate the development of CCTs. Additionally, China's 13th Five-Year Plan (FYP) ranges from 2016 to 2020, which sets goals and directions for national economic and social development during this period. In response to the economic regulation and marker supervision, 2020 is set as the last implementation year of many CCTPs, as shown in Fig. 1. Overall, these policies directed the dominant logic of atmospheric administration in the 13th FYP, namely utilizing coal resources cleanly and efficiently, reducing emissions comprehensively, and decreasing coal consumption.

Concerning the effective implementation of China's CCTs, many scholars have analyzed the technical conditions and potential environmental burdens, which are mainly centred on coal upgrading processing, clean coal-fired power generation, and the modern coal chemical industry (He et al., 2019; Ren et al., 2021). Nevertheless, it is reported that influenced by the lack of CCTPs and the hysteresis of policy formulation and implementation, the development of CCTs was restricted during earlier years (Tang et al., 2015). Therefore, it is an urgent task to identify the effectiveness of CCTPs, providing a significant reference for the

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/c4f64a11-f495-42ce-8d5d-d616f8721d59/e2a641258d9c556417723b2b30e26dc81c8ea01021348895e04fe692a76bb275.jpg)  
Fig. 1. Timeline of CCTPs implemented in China during 2015-2020. (Note: the public information is collected from the National Energy Administration, and the illustration is made by the authors).

enterprises and the public to utilize coal resources more sustainably and cleanly, and meanwhile, verifying the emission reduction targets of the energy sector during the 13th FYP.

Different from the previous policy effectiveness studies, which focused on a specific region or policy with little to national and industrial overview, the main goal of this study is to systematically and comprehensively measure the air quality variation after the implementation of CCTPs at the national level. Based on China's air quality and meteorological data from 2013 to 2019, deep learning approaches were applied to forecast the air quality in 2020, eliminating the uncertainties that COVID-19 brought about. Then, the spatial autocorrelation analysis was utilized to investigate the temporal and spatial distribution characteristics of air pollution. And applying socioeconomic data, the association between AQI change and socioeconomic factors was calculated to explore the most likely mechanism of CCTPs. Our findings showed that there was a significant air quality improvement after the implementation of CCTPs, indicating that clean coal transformation adapts to the requirements of sustainable development in China. And two main channels to reduce air pollution were excavated, namely industrialization and environmental governance. This is essential to reaching an agreement on clean coal utilization, supporting the formulation of energy policies, and combating climate change.

# 2. Literature review

# 2.1. Evidence from regions with high-polluting and energy-intensive industries

Over the last decade, China's persistent airborne pollution has been highly emphasized in academia. Amongst, pollutants emitted from coal mining, processing, and utilization are responsible for the majority of environmental problems and associated losses. In particular, the efficient application of CCTs is often overlooked, resulting in insufficient utilization of inferior coal in China (Wei et al., 2018). Correspondingly, regions which have high-intensity exploitation of coal resources and a high degree of centralized industrial structure, are regarded as the typical epitome of regional air pollution, and often set as the research objects, such as the Beijing-Tianjin-Hebei (BTH) region, Shandong, and Shanxi province (Cheng et al., 2017; Tang et al., 2014). Based on three targets, namely air quality improvement, water savings, and energy conservation and emissions reduction, Zhang et al. (2018) adopted the LEAP (Long-Range Energy Alternatives Planning System) model to discuss the design of coal control targets for Shandong province, analyze the coal reduction level in various coal control scenarios. Results show that the administrative approach is the prominent means to control coal consumption, and the primary reasons for coal consumption control are attributed to atmospheric quality constraints. Sun et al. (2018) assessed the benefits of emission reduction on human health under two assumptions that the air quality of the BJH region will meet the AAQS2 and WHO standards by 2025. It was found that the annual concentration of each pollutant would be cut down proportionally every year, and bring about a significant gain in human health, with the implementation of effective measures for controlling pollution. Apart from coal-dominated industry, residential coal burning would also emit a mixture of air pollutants into homes and the surrounding environment, thus impacting populations over large areas (Archer-Nicholls et al., 2016). It is estimated that residential coal burning accounts for nearly  $45\%$  of the monthly averaged outdoor  $\mathrm{PM}_{2.5}$  in the winter months in northern China. In response, the Beijing municipal government announced an ambitious "coal to electricity" program. Barrington-Leigh et al. (2019) explored this program's impact on household energy use and expenditure, well-being and indoor environmental quality, and results show that under this program, households in high- and middle-income districts eliminated coal use with benefits to indoor temperature, indoor air pollution and life satisfaction. However, in low-income districts, the policy had partial effectiveness.

# 2.2. Targeting a single kind of clean coal policy

To accelerate energy transformation and reduce air pollution, both central and provincial governments in China are taking increasingly leading roles in shaping policy outcomes, through adopting cleaner production or energy saving policies, and revisions of local standards or emission reduction. Since the Chinese energy structure is characterized by being rich in coal, poor in oil, and lack of gas, thus a series of coal-togas (CTG) and coal-to-electricity (CTE) policies are established to promote the clean conversion of coal resources. Further, coal-fired stoves were the most popular source of heating in winter in Northern China, which are cheap and easily available, however, would lead to heavy emissions of various air contaminants (Fan et al., 2020). Strategies to control residential coal combustion (RCC) have been a focus since 2016. Accordingly, there is growing attention from researchers to examine the effectiveness of RCC, CTG, and CTE policies (Xue et al., 2016; Chen and Chen, 2019; Chen et al., 2022). Applying a comprehensive perspective of economic, energy, and environmental impact, Lin and Jia (2020) researched that the CTE policy is an effective pattern to eliminate  $\mathrm{SO}_2$  and  $\mathrm{NO}_{\mathrm{x}}$  emissions, more than half of residents' emissions could be cut down, and the co-benefit between CTE and other energy saving policies was observed. As for the implementation of the RCC policy, Li et al. (2018) estimated that air quality in Beijing would be remarkably improved if residential coal in the BTH region and the surrounding areas are replaced by other clean energy sources. Similar results have been obtained in Xue et al.'s research (2016) as well, using scenario analysis, the projected emissions of primary pollutants from RCC showed that it is difficult to eliminate the emissions from residential sources only rely on mandatory control measures, adopting multiple kinds of policy instruments to promote the clean conversion of coal resources is a preferable pathway (Xue et al., 2016). Yu et al. (2021) examined the dynamic effects of CTG policy and its impact mechanism on air pollution, revealing that this policy has significantly improved air quality in 274 Chinese prefecture-level cities, with a reduction of  $31.3\%$  for industrial  $\mathrm{SO}_2$ ,  $36\%$  for industrial smoke, and  $33.1\%$  for AQI.

As summarized above, the environmental benefits of clean coal-

related policies have reached a consensus. Nevertheless, the contributions mainly focus on regions with high-polluting and energy-intensive industries or target a single kind of clean coal policy. Energy transition is a systematic initiative that requires a long-term and holistic vision to guide nations, industries, companies, and individuals to collaborate from all aspects (Wei et al., 2022). The efficient and effective implementation of CCTPs also emphasizes the interrelatedness of social, technical, institutional and political changes (Markard, 2018), and sets the tone for atmospheric administration in a certain period. Therefore, this paper investigates the effectiveness of CCTPs at the national level with the industrial background of coal-based clean energy, and pays attention to how air quality varied after the implementation of CCTPs. Second, in the existing studies, the mechanism of energy transition policies on environmental pollution control is rarely discussed. By clarifying the association between the AQI and socioeconomic factors, this study tries to provide quantitative results for the internal mechanism of air quality improvement.

# 3. Data and methods

The Chinese mainland is composed of 33 administrative regions, however, the policies implemented by Hong Kong and Macao special administrative regions differ from the other provinces. Moreover, coal-dominated factories and enterprises are mainly located in the capital city of these provinces, which are typical epitomes of regional environmental pollution. Therefore, a total of 31 provincial capital cities in the Chinese mainland are selected. The system architecture of this study is depicted in Fig. 2.

# 3.1. Data collection

Since the index describing air quality was reformulated after the latest published environmental air quality standard (GB3095-2012, 2012) in China, the AQI data is only available from 2013. Furthermore, to suppress the spread of COVID-19, the Chinese government implemented strict lockdowns, which started with Wuhan and radiated to

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/c4f64a11-f495-42ce-8d5d-d616f8721d59/8fc339a368d23f9b5015d4f86239c1bce95c6e9eefb0de0e70c5804b43157d86.jpg)  
Fig. 2. The system architecture of this study.

one-third of cities. Due to the shutdown of industrial activities and traffic volume, an obvious decline in primary air pollutants was observed in most Chinese cities in 2020 (Liu et al., 2020; Yuan et al., 2021). This will undoubtedly cause high uncertainty while investigating the effect of CCTPs on air quality. Therefore, the following data is only extracted from 2013 to 2019, and the AQI in 2020 is predicted through a deep learning network. Subsequently, the investigated data covers 8 years before and after the policy node, namely from 2013 to 2020, which is adequate for policy evaluation (Yu et al., 2021). In the following, air quality and meteorological data are obtained via a web crawler.

# 3.1.1. Air quality data

The AQI describes the level of air pollution and the related health effects. In China, it has been computed using six contamination criteria since 2013, namely,  $\mathrm{PM}_{2.5}$ ,  $\mathrm{PM}_{10}$ ,  $\mathrm{SO}_2$ ,  $\mathrm{NO}_2$ ,  $\mathrm{CO}$ , and  $\mathrm{O}_3$ . In this study, the AQI data and six criteria are extracted from China's air quality online monitoring and analysis platform (https://www.aqistudy.cn/), which provides daily data after calculating the average hourly AQI from the China National Environmental Monitoring Centre.

# 3.1.2. Meteorological data

Air quality prediction can be influenced by meteorological conditions, atmospheric dispersion, and geographic characteristics. Therefore, in addition to the air quality data, daily meteorological parameters such as the highest temperature (HT), lowest temperature (LT), wind direction (WD), and wind power (WP) are also considered. The identified parameters are taken as input along with the air quality parameters to encode the spatiotemporal relation, which is extracted from China's weather forecast and records platform (http://tianqi.2345.com/).

# 3.1.3. Socioeconomic data

According to the STIRPAT model, environmental impacts are the multiplicative product of three key driving forces, namely, population, affluence, and technology (Yang et al., 2018). Meanwhile, referring to previous studies, the considered factors usually comprise population, GDP per capita, energy structure, etc. After selecting and supplementing related factors based on the characteristic of the Energy-Environment system, the connotations are finally ascertained to discuss the internal mechanism of CCTPs, as shown in Table 1 (Kais and Sami, 2016; Yu et al., 2021). Specifically, the values are acquired from the China City Statistical Yearbook and the prefecture-level city's Statistical Bulletin of National Economic and Social Development.

i) Economic development (ED): Based on the Environmental Kuznets Curve, there is an inverted U-shaped relationship between environmental quality and income level. Thus, the term of GDP per capita is introduced into the estimation. ii) Environmental governance (EG): A significant factor affecting air pollution (Ouyang et al., 2019), this study evaluates the mean value of the removal rate of wastewater, waste gas and solid waste, to represent the level of EG. iii) Industrialization (IL): Li et al. (2019) found that air pollution presented N-shape relations with the industrialization level in China. In this

Table 1 The descriptions of considered socioeconomic factors.  

<table><tr><td>Confounding factors</td><td>Description (Unit)</td><td>Reference</td></tr><tr><td>Economic development</td><td>GDP per capita (CNY)</td><td>Cheng et al. (2017)</td></tr><tr><td>Environmental governance</td><td>The mean value of the removal rate of wastewater, waste gas and solid waste (%)</td><td>Ouyang et al. (2019)</td></tr><tr><td>Industrialization</td><td>The proportion of the secondary industry in GDP (%)</td><td>Li et al. (2019)</td></tr><tr><td>Population density</td><td>The city&#x27;s population per unit area (people/km2)</td><td>Liu et al. (2019)</td></tr><tr><td>Social development</td><td>The number of civil cars (10000 vehicles)</td><td>Xie et al. (2020)</td></tr></table>

study, the proportion of the secondary industry in GDP is applied to measure the level of industrialization. iv) Population density (PD): Air pollution is closely related to human production and life, and the rapid growth of the world's population is regarded as an important source of such pollution. This study uses the city's population per unit area to estimate the level of PD. v) Social development (SD): Increase in vehicle exhaust emission would undoubtedly lead to air pollution, and the number of civil cars is utilized as an influencing factor.

# 3.2. Data preprocessing

Considering that 2013-2015 is set as the period before CCTPs implementation and that 2016-2020 is the period after the policy node, thus the air pollution condition in 2020 is forecasted using data from 2016 to 2019. After extraction, the daily air quality data and the daily meteorological data of 31 cities are combined to generate a tabular dataset and train the predictive network, ranging from January 22, 2016 to December 31, 2019. Data preprocessing is conducted to feed the subsequent neural networks with complete and low noise data, the four procedures are listed below and shown in Fig. 3.

First, AQI prediction is a regression problem of time-series data, and continuous data are required. Therefore, missing values in the original dataset are filled by Lagrange interpolation, which is conducted using low-order interpolation polynomials in sections (Yang and Sarkar, 2007; Wubetie, 2017). Second, some errors would generate in the process of data acquisition, transmission and storage owing to uncontrollable elements. To eliminate the negative impacts of the abnormal data, a box plot is created to find the outliers. Then, the identified outliers are replaced with null values and filled up through linear interpolation. By doing so, most of the abnormal data are modified, and the quality of the dataset for prediction is greatly improved. Third, a predictive model is established for multivariate prediction, the daily  $\mathrm{PM}_{2.5}$ ,  $\mathrm{PM}_{10}$ ,  $\mathrm{SO}_2$ ,  $\mathrm{NO}_2$ ,  $\mathrm{CO}$ , and  $\mathrm{O}_3$  concentrations and the daily meteorological data are all applied. Specifically, to promote the efficiency of multivariable prediction, the Kendall correlation coefficient is utilized to analyze the correlation between the AQI and the mentioned parameters for each studied city (Ghayekhloo et al., 2015), as the Kendall coefficient is the rank correlation coefficient, and has a good performance in handling ordinal categorical variables which do not obey the normal distribution, conforming the feature of this studied dataset. If the coefficient is less than 0.1, then the corresponding parameter column will be deleted during the prediction process. Finally, Z-score normalization is conducted for the multidimensional data columns to diminish the magnitude differences of the data and speed up the convergence rate of the predictive model. After data preprocessing, a random 6:2:2 split of the data is applied to the training, validation and test set, respectively. At this point, all the input data are ready to be used in the prediction process.

# 3.3. Model training

Compared with traditional techniques for forecasting air pollution, namely empirical approaches and simple statistical models, deep learning approaches can handle complex and non-linear relationships among air quality variables which allow them to better capture the pollution episode forecasts. Therefore, deep learning has been identified as a vital tool for air quality modelling and forecasting, which helps in recognizing pollution hot spots (Schmidhuber, 2015; Ong et al., 2016; Li et al., 2017).

Amongst, Long Short-Term Memory (LSTM) is a variant of recurrent neural network (RNN) models and can solve the problem of long-term dependencies that conventional RNNs cannot learn, which has a remarkable performance in processing time-series data (Qi et al., 2019; Wen et al., 2019). Meanwhile, the intelligent design of the memory cell in LSTM is valid for solving the problem of gradient vanishing in

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/c4f64a11-f495-42ce-8d5d-d616f8721d59/31bab1d85fbfd528a8d64bd216d4652eeeedc59059b365370bd26e174639944b.jpg)  
Fig. 3. Procedures, the corresponding methods and principles of data preprocessing.

backpropagation and learning the input sequence with longer time steps. Further, Convolutional Neural Networks (CNN) have a remarkable advantage in extracting data features and reducing dimensions, which could alleviate the problems of slow training and overfitting in fully connected networks (Alzubaidi et al., 2021). Correspondingly, many variants of the CNN-LSTM combination have been constructed for capturing the spatiotemporal dependencies in air quality forecasting tasks (Donahue et al., 2015; Vinyals et al., 2015; Qin et al., 2019), as it would create a great synergy than the individual models on their own. Specifically, first performing feature extraction using CNN, and then inputting the feature values into the LSTM architecture.

Considering the data features of high-dimension, multivariable, nonlinearity and temporal-spatial correlation, and with the application of Keras and TensorFlow, a predictive model combining CNN and LSTM is applied and tailored in this study. The architecture and workflows are shown in Fig. 4 and summarized as follows.

As shown in Fig. 4, the general architecture of the predictive model is an encoder-decoder structure. The first half of the network is CNN and is utilized for feature extraction of input data. The latter half is LSTM, analyzing the features extracted by CNN and then forecasting the AQI of the next point in time.

Specifically, the CNN part of the predictive model contains two 1D convolution layers, a max pooling layer and a dropout layer; moreover,

multidimensional inputs are flattened by a flattening layer and then repeated by a repcatvec layer. The outputs of the CNN's last layer are one-dimensional vectors with ground data features and are subsequently input to the LSTM layer. A time-series prediction function is added to the LSTM model, and its training processes are presented in Equations (1)-(6).

I. Forget phase. The LSTM first selectively forgets some input air quality data and the related parameters.

$$
f _ {t} = \sigma \left(W _ {f} \left[ h _ {t - 1}, x _ {t} \right] + b _ {f}\right) \tag {1}
$$

II. Selective memory phase. In this phase, LSTM decides what new information to store in the unit state, which originates from two parts. The sigmoid layer determines the updated information, and the tanh layer creates a candidate value vector.

$$
i _ {t} = \sigma \left(W _ {i} \left[ h _ {t - 1}, x _ {t} \right] + b _ {i}\right) \tag {2}
$$

$$
C _ {t} ^ {\prime} = \tanh  \left(W _ {C} \left[ h _ {t - 1}, x _ {t} \right] + b _ {t}\right) \tag {3}
$$

$$
C _ {t} = f _ {t} \odot C _ {t - 1} + i _ {t} \odot C _ {t} ^ {\prime} \tag {4}
$$

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/c4f64a11-f495-42ce-8d5d-d616f8721d59/edfb6a04dc6006557e9a99a46b517c3ce28341cde52e6ef8d8edba5889eb18df.jpg)  
Fig. 4. The architecture of the tailored CNN-LSTM network.

III. Output phase. The output information is decided, namely, the predicted AQI:

$$
o _ {t} = \sigma \left(W _ {o} \left[ h _ {t - 1}, x _ {t} \right] + b _ {o}\right) \tag {5}
$$

$$
h _ {t} = o _ {t} \odot \tanh  \left(C _ {t}\right) \tag {6}
$$

where  $f_{t}$  is the output of the forget gate,  $\sigma$  is the sigmoid activation function,  $W_{f}, W_{o}, W_{C}, W_{i}$ , and  $b_{f}b_{o}, b_{i}, b_{t}$  are the coefficients and biases of the linear relationship,  $h_{t-1}$  is the hidden status of the last sequence,  $x_{t}$  is the data of this sequence, which is the first part of the output,  $C_{t}'$  is the second part of the output,  $C_{t}$  is the present cell status,  $C_{t-1}$  is the previous cell status,  $h_{t}$  is the update of the hidden status,  $o_{t}$  is the update of the first hidden status, and  $\odot$  represents the Hadamard product, which requires the corresponding elements in the matrix to be multiplied.

Last, in the two dense layers, the correlations among the features are extracted through nonlinear variation and then mapped to the output space. Through rolling prediction, the sequence prediction results from the output layer are added to the dataset to achieve dynamic outward prediction. Notably, to improve the learning performance, the hyperparameters are adjusted and optimized for different studied cities, namely for different input datasets. Table 2 lists the parameters used for model training in Beijing.

Root Mean Square Error (RMSE) is taken for the performance evaluation, which quantifies the dispersion between predicted and actual data, and the smaller the value is, the better the performance of the predictive model. To test the performance comprehensively,  $60\%$  of data are chosen as the training set,  $20\%$  as the validation set and  $20\%$  as the test set. The measurement index and its equation are shown in Equation (7):

$$
R M S E = \sqrt {\frac {1}{N} \sum_ {i = 1} ^ {N} \left(P _ {i} - O _ {i}\right) ^ {2}} \tag {7}
$$

where  $N$  is the number of test samples,  $P_{i}$  is the predicted air pollutant concentration, and  $O_{i}$  is the observed air pollutant concentration.

# 3.4. Spatial autocorrelation analysis

To further analyze the temporal and spatial variation features of air quality in 31 provincial capital cities from 2013 to 2020, the spatial autocorrelation analysis method is applied. ArcGIS 10.6 and GeoDa software is used for the calculation and analytic process.

# 3.4.1. Global spatial autocorrelation analysis

First, the global spatial autocorrelation analysis method is utilized to reflect the space gathering of the AQI. The calculation formulas for global Moran's I are listed in Equations (8) and (9), and its significance test is conducted in Equation (10):

Table 2 CNN-LSTM model parameters for Beijing's AQI prediction.  

<table><tr><td>Parameters</td><td>Value</td></tr><tr><td>Kernel size of convolution layer1</td><td>3 × 3</td></tr><tr><td>Kernel size of convolution layer2</td><td>3 × 3</td></tr><tr><td>Number of convolution layer1 parameters</td><td>1600</td></tr><tr><td>Number of convolution layer2 parameters</td><td>12352</td></tr><tr><td>Kernel size of pooling layer</td><td>2 × 2</td></tr><tr><td>Ratio of dropout</td><td>0.2</td></tr><tr><td>Number of LSTM nodes</td><td>200</td></tr><tr><td>Learning rate</td><td>0.001</td></tr><tr><td>Batch size</td><td>32</td></tr></table>

$$
I = \sum_ {i = 1} ^ {n} \sum_ {j = 1} ^ {n} w _ {i j} \left(x _ {i} - \bar {x}\right) \left(x _ {j} - \bar {x}\right) / S ^ {2} \sum_ {i = 1} ^ {n} \sum_ {j = 1} ^ {n} w _ {i j} \tag {8}
$$

$$
S ^ {2} = \frac {1}{n} \sum_ {i = 1} ^ {n} \left(x _ {i} - \bar {x}\right) ^ {2} \tag {9}
$$

$$
Z (I) = \frac {I - E (I)}{\sqrt {\operatorname {V a r} (I)}} \tag {10}
$$

where  $S^2$  is the variance of attribute value,  $n$  represents 31 studied cities,  $x_i$  and  $x_j$  are the AQI values of cities  $i$  and  $j$ , respectively;  $\bar{x}$  is the average AQI of all cities,  $w_{ij}$  is spatial weight,  $E(I)$  is the mean of global Moran's I,  $Var(I)$  is the variance of global Moran's I, and  $Z(I)$  is the significance level of global Moran's I. The range of global Moran's I is -1 to 1. If the value is greater than 0, indicating that the spatial distribution of AQI is positive, if it is less than 0, indicating a negative correlation, and if equals 0, indicating a random distribution.

# 3.4.2. Regional spatial autocorrelation analysis

Second, the highly and slightly polluted areas before and after the policy node are clarified through the regional spatial autocorrelation analysis method, and the calculation process of regional Moran's I is shown in Equation (11).

$$
I _ {i} = \frac {\left(x _ {i} - \bar {x}\right)}{S ^ {2}} \sum_ {j = 1} w _ {i j} \left(x _ {j} - \bar {x}\right) \tag {11}
$$

The significance level of regional Moran's I is tested by Equation (10) as well. If regional Moran's I is greater than 0 and is significant, then there is a high-high or low-low gathering area; if it is less than 0 and is significant, then there are high-low or low-high gathering areas.

# 3.5. Measuring the AQI change rate during 2013-2020

A comparison is made between the AQI pre- and post-policy node using Equation (12), to clarify the air quality variation after CCTPs are implemented.

$$
C _ {A Q I} = \frac {p r _ {A Q I} - p o _ {A Q I}}{p r _ {A Q I}} \times 100 \% \tag{12}
$$

where  $C_{AQI}$  is the change rate of the AQI for each studied city,  $pr_{AQI}$  is the average AQI of each month for the studied cities from 2013 to 2015, and  $po_{AQI}$  is the average AQI of each month from 2016 to 2020. The calculated results vary between  $-100\%$  and  $+100\%$ , where negative and positive values indicate improvement or deterioration of air quality, and 0 represents no change.

# 3.6. Investigating the association between the AQI and socioeconomic factors

To comprehensively explore the association between air quality change and socioeconomic factors, and reflect the internal mechanism of CCTPs working on air quality improvement, the correlation coefficients were calculated with all socioeconomic factors separately using Equation (13). Ordinary least squares regression was also carried out, and the variance inflation factor of each parameter was computed to verify the existence of multicollinearity.

$$
\begin{array}{l} \ln C _ {A Q I} = a _ {0} + a _ {1} \ln \Delta E D + a _ {2} \ln \Delta E G + a _ {3} \ln \Delta I L + a _ {4} \ln \Delta P D \\ + a _ {5} \ln \Delta S D \tag {13} \\ \end{array}
$$

where  $\Delta ED$ ,  $\Delta EG$ ,  $\Delta IL$ ,  $\Delta PD$ , and  $\Delta SD$  are the changes in ED, EG, IL, PD, and SD pre- and post- CCTPs node, and  $a_0$ ,  $a_1$ , ...,  $a_5$  are the model parameters.

# 4. Results

# 4.1. Performance of the CNN-LSTM model

The study obtained the data including a total of 1440 daily air quality and meteorological data (January 22, 2016, to December 31, 2019) from 31 provincial capital cities in the Chinese mainland,  $60\%$  of which are chosen as the training set,  $20\%$  as the validation set and  $20\%$  as the test set. After determining the best basic network architecture for the current prediction tasks, models are set up in units of cities, and the training set is used to train the tailored CNN-LSTM models. The accuracy indicators of the model prediction results of 31 cities, namely RMSE values averaging 22.06, models perform well overall, indicating that the applied CNN-LSTM network has good capabilities for AQI prediction (Jin et al., 2020; Mao et al., 2021).

# 4.2. Spatial changes in air quality

# 4.2.1. Results of the global spatial autocorrelation analysis

Global spatial autocorrelation analysis is carried out using the average monthly AQIs for the 31 studied cities from 2013 to 2020. As shown in Table 3, the results of global Moran's I are all greater than 0 and statistically significant, indicating that there are significant and positive spatial correlations among the average monthly AQIs. In summary, there is an obvious regional integration tendency of air pollution in Chinese cities.

# 4.2.2. Spatial pattern representing north-south differentiation

After the spatial gatherings of air pollution are confirmed, to better identify the gathering district, a regional spatial autocorrelation analysis is also conducted. As shown in Fig. 5, there were still high-high gathering areas (high levels of pollution) and low-low gathering areas (low levels of pollution) from 2013 to 2020. Meanwhile, a north-south spatial heterogeneity pattern was obvious, depicting the high levels of pollution in northern China and low levels of pollution in southern China.

From analyzing the zone of high pollution and its variation characteristics, a unicentric pattern centred on northern China can easily be found before the CCTPs node (2013-2015). After the policy node (2016-2020), although the air quality generally improved, relatively speaking, the highly polluted zones enlarged. Specifically, they expanded to the northwest and northeast China, however, still centred on northern China.

Regarding the variation characteristics of the zone with low levels of pollution, there are two evident spatial patterns, the monocentric pattern centred in southern China and the bicentric pattern centred in south of southwest China. Specifically, from 2013 to 2015, the slightly polluted areas nationwide were mainly in southern China. After the CCTPs were implemented, the regional distribution of the slightly polluted areas gradually scattered to the south of southwest China. This phenomenon can most easily be observed in 2019.

# 4.3. Air quality variation before and after CCTPs implemented

Temporally, it is evident that the AQI in the Chinese mainland

Table 3  
Results of global Moran's I from 2013 to 2020.  

<table><tr><td>Year</td><td>Global Moran&#x27;s I</td></tr><tr><td>2013</td><td>0.267</td></tr><tr><td>2014</td><td>0.499</td></tr><tr><td>2015</td><td>0.548</td></tr><tr><td>2016</td><td>0.601</td></tr><tr><td>2017</td><td>0.551</td></tr><tr><td>2018</td><td>0.559</td></tr><tr><td>2019</td><td>0.516</td></tr><tr><td>2020</td><td>0.240</td></tr></table>

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/c4f64a11-f495-42ce-8d5d-d616f8721d59/318200e3ef47de15cef2efb92cc6d0f00b1e6f4520039ddf917d180494fb11bd.jpg)

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/c4f64a11-f495-42ce-8d5d-d616f8721d59/140cb453acd9f25ffb67e0fa1f458bd66e04d385b7f7d8f7e39c00a3e9892cca.jpg)

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/c4f64a11-f495-42ce-8d5d-d616f8721d59/19d28421c26ec5aa28eb43c758a2837ca1dd150894713703a8c82739e608ce19.jpg)

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/c4f64a11-f495-42ce-8d5d-d616f8721d59/1e27df9ef0003f336be6c304f2f8a9e04318625e750f2dabfd88dec19b2fc9db.jpg)  
Fig. 5. AQI regional spatial autocorrelation in 31 provincial cities of the Chinese mainland.

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/c4f64a11-f495-42ce-8d5d-d616f8721d59/e2f30ef7661b6ec078c590185635e4906389504f78aeec186c8bf333721c8807.jpg)  
Fig. 6. The variation trend of AQI in the Chinese mainland.

considerably decreased from 2013 to 2020. As shown in Fig. 6, the AQI of all studied cities was all less than 100 since 2017, which is the threshold AQI value of excessive pollutants, indicating that air quality in China began to pick up. Herein, for better comparison, the 31 provincial capital cities were categorized into 7 districts according to the official administrative geographical area division. An identical trend was seen to that in central China, which showed the greatest improvement in air quality during 7 years.

To better understand the policy effect on air quality improvement, the change rate of AQI was computed between the pre- and post-policy nodes, as shown in Table 4. All the areas experienced improved air quality, with the change rate of AQI ranging from  $4.28\%$  to  $29.54\%$ . Regionally, the degree of improvement was maximum in central China  $(25.61\%)$ , followed by northeast  $(25.47\%)$ , eastern  $(20.88\%)$ , and northern China  $(18.30\%)$ . The three districts with the least improvement were northwest, southern, and southwest China, with change rates of  $15.27\%$ $14.63\%$  and  $14.44\%$  respectively. On average, the AQI value was reduced by  $18.82\%$  from 2013 to 2020, indicating that China's air quality was greatly improved after the implementation of CCTPs.

To conduct a thorough analysis of AQI variations based on seasonal patterns, the average AQI change rate in four seasons was computed, as shown in Fig. 7. The four seasons were divided based on meteorology, where spring ranges from March to May, summer from June to August, autumn from September to November, and winter from December to February of the next year. Results showed that the most significant decrease in AQI occurred in winter, with average rates of  $35.46\%$ ,  $30.23\%$ ,  $29.22\%$ ,  $25.90\%$ ,  $24.25\%$ ,  $22.37\%$  and  $6.63\%$  for the northeast, southern, central, eastern, northern, southwest, and northwest China, respectively. The AQI decrease in autumn was also substantial, and northeast China had the greatest decline, averaging  $35.77\%$  after the implementation of CCTPs. The AQI change rate in summer and spring was less than that of the other two seasons, with an average of  $15.81\%$  and  $13.41\%$ , respectively.

# 4.4. Mechanism analysis of CCTPs on air quality

The Kendall correlation coefficients depicted the association between air quality change and socioeconomic factors, as shown in Fig. 8. Ordinary least squares analysis was also done to assess the variance inflation factors, which ranged from 1.007 to 2.297 and were all less than the threshold of 10, indicating that there was no multiple collinearity issue and no high correlation among socioeconomic variables, which made the subsequent correlation analysis more reliable.

As depicted in Fig. 8, the socioeconomic factors were seen not to be highly associated with the change rate of AQI. Amongst, an obvious observation was that the increase in environmental governance and a decrease in industrialization were positively related to air quality improvement. Furthermore, the increase in economic development,

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/c4f64a11-f495-42ce-8d5d-d616f8721d59/57d0a55b0ed68e0dd9c57f0b5e6b8c90f72bbad9640a0b95cb730c3ae41a6172.jpg)  
Fig. 7. The variation trend of AQI in four seasons.

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/c4f64a11-f495-42ce-8d5d-d616f8721d59/a1fb7cc200e1969bd71854f58885cbeb724b5dc872dc66febd074e070565758a.jpg)  
Fig. 8. Correlation coefficients between air quality change and socioeconomic factors.

Table 4 The change rate of AQI pre- and post-CCTPs node (Unit:  $\%$  -  

<table><tr><td>District</td><td>City</td><td>CAQI</td><td>District</td><td>City</td><td>CAQI</td><td>District</td><td>City</td><td>CAQI</td></tr><tr><td rowspan="5">Northern</td><td>Beijing</td><td>26.46</td><td>Southwest</td><td>Chongqing</td><td>18.58</td><td>Northwest</td><td>Xi&#x27;an</td><td>11.69</td></tr><tr><td>Tianjin</td><td>22.47</td><td></td><td>Chengdu</td><td>19.16</td><td></td><td>Lanzhou</td><td>10.10</td></tr><tr><td>Shijiazhuang</td><td>27.60</td><td></td><td>Guiyang</td><td>20.83</td><td></td><td>Xining</td><td>17.62</td></tr><tr><td>Taiyuan</td><td>4.28</td><td></td><td>Kunming</td><td>6.30</td><td></td><td>Yinchuan</td><td>17.62</td></tr><tr><td>Huhhot</td><td>10.70</td><td></td><td>Lasa</td><td>7.34</td><td></td><td>Urumqi</td><td>19.34</td></tr><tr><td rowspan="3">Northeast</td><td>Shenyang</td><td>25.26</td><td>Southern</td><td>Guangzhou</td><td>15.52</td><td>Central</td><td>Zhengzhou</td><td>22.47</td></tr><tr><td>Changchun</td><td>26.40</td><td></td><td>Nanning</td><td>21.66</td><td></td><td>Wuhan</td><td>29.54</td></tr><tr><td>Harbin</td><td>24.75</td><td></td><td>Haikou</td><td>6.72</td><td></td><td>Changsha</td><td>24.82</td></tr><tr><td rowspan="7">Eastern</td><td>Shanghai</td><td>21.01</td><td></td><td></td><td></td><td></td><td></td><td></td></tr><tr><td>Nanjing</td><td>27.48</td><td></td><td></td><td></td><td></td><td></td><td></td></tr><tr><td>Hangzhou</td><td>21.93</td><td></td><td></td><td></td><td></td><td></td><td></td></tr><tr><td>Hefei</td><td>24.09</td><td></td><td></td><td></td><td></td><td></td><td></td></tr><tr><td>Fuzhou</td><td>14.28</td><td></td><td></td><td></td><td></td><td></td><td></td></tr><tr><td>Nanchang</td><td>10.92</td><td></td><td></td><td></td><td></td><td></td><td></td></tr><tr><td>Jinan</td><td>26.42</td><td></td><td></td><td></td><td></td><td></td><td></td></tr></table>

population density, and social development were all negatively related to air quality improvement. It should be mentioned that high association doesn't mean that one factor controls others, implying that countermeasures on emission reduction and deindustrialization can help to improve air quality with the background of CCTPs.

# 5. Discussion

# 5.1. Discussion of findings

During the period of CCTPs implementation, an obvious air quality improvement was observed in the Chinese mainland, manifested as a decrease of AQI value by  $18.82\%$  from 2013 to 2020. It is concluded that the clean and efficient transformation of coal resources conforms to China's national conditions, and could indeed improve the atmospheric environment, which has been demonstrated in the existing research as well (Li and Patino-Echeverri, 2017; Liu et al., 2021). Specifically, correlation coefficients showed that the promotion of emission reduction and deindustrialization could fundamentally help to reduce airborne contamination, although their persistence relies on continued efforts and is influenced by various factors (Yang and Teng, 2018). Another important observation was a 2-year time lag before the stringent CCTPs starting from 2015 takes any strong positive effects, shown as a dramatical reduction of AQI in 2018. It implies that the influence of time lag should be considered in the decision-making process, as a time lag commonly appears in air pollution regulations and plans (Van der et al., 2017).

Differences in research objects are probably the leading cause of the distinction between our results and those in the literature. As stated before, the majority of contributions centred on the environmental effectiveness brought by one single kind of clean coal policy. Different from this, the study intends to investigate the variations caused by the profound industrial transformation, from a more convenient but intuitive perspective. Namely, investigating the air quality variations before and after the implementation of a variety of CCTPs at the national level.

# 5.2. Theoretical and practical implications

By investigating the effective national control policies, this study has implications for theoretical research on the effectiveness of energy policies. The most valid deployment and efficiency of energy policies have been hotly debated in the literature. The single regional model is not applicable because it lacks a national perspective, as same as research on an individual policy. This single view is not conducive to allocating governance resources reasonably and establishing regional emission reduction targets and regulations. In addition, regarding uncertainties would be brought about when discussing the air quality change since the outbreak of COVID-19, the introduced deep learning approaches could supply researchers with new insights.

From a practical perspective, this study could provide references for the government to adjust and implement coal-related pollution prevention and control policies in 14th FYP. Since the air pollution in China shows an integration trend, it is crucial to insist on the joint prevention methods which converge the adjustment of industrial structure with the improvement of social consensus. Further, the government and departments should notice the time lags of CCTPs and establish long-term plans, such as improving the efforts of preferential policies from the tax revenue perspective to actively guide investment in the clean coal industry coming from market subjects. For the districts with coaldominated industries and heavy air pollution, additional policies should be formulated between local jurisdictions and the central government, while strengthening the air quality monitoring indicators and improving air quality standards. Considering that the findings emphasized the association between air quality improvement and deindustrialization and implied that the transformation of industrial structure from secondary to tertiary industry should be insisted upon.

China plays an increasingly important role in international energy transformation and environment protection. With the positive influence of the national control policies has been verified, its establishment and implementation might be a reference for countries that have similar energy structures and environmental conditions to China. And the results of this study can be used by various stakeholders in the international energy market to understand clean coal transformation more comprehensively, which could lead to more sustainable energy activities.

# 5.3. Limitations and future research directions

Limitations in both data acquisition and method selection should be acknowledged. First, the air quality variation before and after the implementation of CCTPs was investigated over a time span of 7 years, owing to the AQI data is available since 2013. The future study would be enriched with broader periods to observe a long-term performance. For method selection, the first limitation is that only CNN and LSTM were applied, ensemble-based approaches would be explored and incorporated along with the proposed model for further improvement in the prediction performance of the proposed framework. Further, the five socioeconomic factors were extracted and analyzed based on existing research and empirical knowledge. Future studies should continue to examine the deeper mechanisms of CCTPs using more quantitative and modelling methods.

# 6. Conclusions

The increase in population size and economic activity has remarkably increased the demand for fossil fuels in China, posing a severe threat to the environment. However, the recently implemented coal-based energy transition has shifted the energy structure from polluting energies to environment-friendly energies, and the subsequent policies created a great revolution in energy development and environment protection. Nevertheless, the energy distribution and air pollution in China are characterized by regionality, thus, targeting the efficiency of these national control policies, scholars mainly focus on regions with high-polluting and energy-intensive industries, such as Shanxi province and the BJH region; or target a specific policy, such as CTG and CTE policy. Differently, this study revealed the air quality improvement during the implementation of CCTPs at the national level. Clarifying the internal mechanism of these policies is significant when revising and implementing the following policies to achieve sustainable development. The quantitative assessment provided significant results: i) After implementing CCTPs, the Chinese mainland experienced air quality improvement, with the reduction of AQI averaging  $18.82\%$ ; ii) An identical reduction of air pollution was observed in 2018, indicating a 2-year time lag of the related control policies; iii) There were positive associations between emission reduction promoting, deindustrialization and air quality improvement, suggesting two promising ways to realize sustainable energy development. Through assessing the air quality changes before and after the implementation of CCTPs, it is expected to provide a scientific basis for policymakers and stakeholders to forge consensus on the establishment and enforcement of clean coal policies.

# CRediT authorship contribution statement

Boling Zhang: Data curation, Formal analysis, Methodology, Writing - original draft. Sixia Wang: Software, Writing - review & editing, Validation, Visualization. Dongdong Wang: Conceptualization, Reference acquisition, Funding acquisition, Writing - review & editing. Qian Wang: Reference acquisition, Funding acquisition, Writing - review & editing. Xiaoyi Yang: Investigation, Writing - review & editing, Visualization. Ruipeng Tong: Conceptualization, Funding acquisition, Methodology, Resources.

# Declaration of competing interest

The authors declare that they have no known competing financial interests or personal relationships that could have appeared to influence the work reported in this paper.

# Acknowledgements

The work was financially supported by the National Natural Science Foundation of China (No. 52074302), and the Natural Science Foundation of Beijing Municipality (No. 8212015).

# References

Alzubaidi, L., Zhang, J., Humaidi, A.J., Al-Dujaili, A., Duan, Y., Al-Shamma, O., Santamaría, J., Fadhel, M.A., Al-Amidie, M., Farhan, L., 2021. Review of deep learning: concepts, CNN architectures, challenges, applications, future directions. J Big Data 8 (1), 1-74. https://doi.org/10.1186/s40537-021-00444-8.  
Archer-Nicholls, S., Carter, E., Kumar, R., Xiao, Q., Liu, Y., Frostad, J., Forouzanfar, M., Forouzanfar, A., Brauer, M., Baumgartner, J., Wiedinmyer, C., 2016. The regional impacts of cooking and heating emissions on ambient air quality and disease burden in China. Environ. Sci. Technol. 50 (17), 9416-9423. https://doi.org/10.1021/acs.est.6b02533.  
Barrington-Leigh, C., Baumgartner, J., Carter, E., Robinson, B.E., Tao, S., Zhang, Y., 2019. An evaluation of air quality, home heating and well-being under Beijing's programme to eliminate household coal use. Nat. Energy 4 (5), 416-423. https://doi.org/10.1038/s41560-019-0386-2.  
Burandt, T., Xiong, B., Löffler, K., Oei, P., 2019. Decarbonizing China's energy system: Modeling the transformation of the electricity, transportation, heat, and industrial sectors. Appl. Energy 255: 113820. https://doi.org/10.1016/j.apenergy.2019.11.3820.  
Cheng, M., Zhi, G., Tang, W., Liu, S., Dang, H., Guo, Z., Du, J., Du, X., Zhang, W., Zhang, Y., Meng, F., 2017. Air pollutant emission from the underestimated households' coal consumption source in China. Sci. Total Environ. 580, 641-650. https://doi.org/10.1016/j.scitotenv.2016.12.143.  
Cheng, Y., Awan, U., Ahmad, S., Tan, Z., 2021. How do technological innovation and fiscal decentralization affect the environment? A story of the fourth industrial revolution and sustainable growth. Technol Forecast Soc 162, 120398. https://doi.org/10.1016/j.technfore.2020.120398.  
Cheng, Z., Li, L., Liu, J., 2017. Identifying the spatial effects and driving factors of urban  $\mathrm{PM}_{2.5}$  pollution in China. Ecol. Indicat. 82, 61-75. https://doi.org/10.1016/j.ecolind.2017.06.043.  
Chen, H., Chen, W., 2019. Potential impact of shifting coal to gas and electricity for building sectors in 28 major northern cities of China. Appl. Energy 236, 1049-1061. https://doi.org/10.1016/j.apenergy.2018.12.051.  
Chen, Z., Tan, Y., Xu, J., 2022. Economic and environmental impacts of the coal-to-gas policy on households: evidence from China. J. Clean. Prod. 130608 https://doi.org/10.1016/j.jclepro.2022.130608.  
Donahue, J., Anne, Hendricks, L., Guadarrama, S., Rohrbach, M., Venugopalan, S., Saenko, K., Darrell, T., 2015. Long-term recurrent convolutional networks for visual recognition and description. Proceedings of the IEEE conference on computer vision and pattern recognition 2625-2634.  
Elio, J., Phelan, P., Villalobos, R., Milcarek, R.J., 2021. A review of energy storage technologies for demand-side management in industrial facilities. J. Clean. Prod. 307, 127322 https://doi.org/10.1016/j.jclepro.2021.127322.  
Fan, M., He, G., Zhou, M., 2020. The winter choke: coal-fired heating, air pollution, and mortality in China. J. Health Econ. 71, 102316 https://doi.org/10.1016/j.jhealeco.2020.102316  
GB3095-2012, 2012. Ambient Air Quality Standards. Ministry of Environmental Protection of the People's Republic of China.  
Ghayekhloo, M., Menhaj, M., Ghofrani, M., 2015. A hybrid short-term load forecasting with a new data preprocessing framework. Elec. Power Syst. Res. 119, 138-148. https://doi.org/10.1016/j.epsr.2014.09.002.  
Guney, M.S., Tepe, Y., 2017. Classification and assessment of energy storage systems. Renew. Sustain. Energy Rev. 75, 1187-1197. https://doi.org/10.1016/j.rser.2016.11.102.  
He, J., Yao, Y., Lu, W., Long, G., Bai, Q., Wang, H., 2019. Cleaning and upgrading of coalseries kaolin fines via decarbonization using triboelectric separation. J. Clean. Prod. 228, 956-964. https://doi.org/10.1016/j.jclepro.2019.04.329.  
IEA (International Energy Agency), 2021. Global Energy Review 2021: assessing the effects of economic recoveries on global energy demand and CO2 emissions in 2021. https://www.iea.org/reports/global-energy-review-2021. (Accessed 16 January 2022). Accessed.  
Jiang, Z., Lyu, P., Ye, L., Zhou, Y., 2020. Green innovation transformation, economic sustainability and energy consumption during China's new normal stage. J. Clean. Prod. 273, 123044 https://doi.org/10.1016/j.jclepro.2020.123044.  
Jin, X., Yang, N., Wang, X., Bai, T., Su, L., Kong, J., 2020. Deep hybrid model based on EMD with classification by frequency characteristics for long-term air quality prediction. Mathematics 8 (2), 214 https://doi.org/2227-7390/8/2/214.  
Kais, S., Sami, H., 2016. An econometric study of the impact of economic growth and energy use on carbon emissions: panel data evidence from fifty eight countries.

Renew. Sustain. Energy Rev. 59, 1101-1110. https://doi.org/10.1016/j.rser.2016.01.054.  
Li, J., Zhang, Y., Tian, Y., Cheng, W., Yang, J., Xu, D., Wang, Y., Xie, K., Ku, A.Y., 2020. Reduction of carbon emissions from China's coal-fired power industry: insights from the province-level data. J. Clean. Prod. 242, 118518 https://doi.org/10.1016/j.jclepro.2019.118518.  
Li, M., Patino-Echeverri, D., 2017. Estimating benefits and costs of policies proposed in the 13th FYP to improve energy efficiency and reduce air emissions of China's electric power sector. Energy Pol. 111, 222-234. https://doi.org/10.1016/j.enpol.2017.09.011.  
Li, T., Li, Y., An, D., Han, Y., Xu, S., Lu, Z., Crittenden, J., 2019. Mining of the association rules between industrialization level and air quality to inform high-quality development in China. J. Environ. Manag. 246, 564-574. https://doi.org/10.1016/j.jenvman.2019.06.022.  
Li, X., Peng, L., Yao, X., Cui, S., Hu, Y., You, C., Chi, T., 2017. Long short-term memory neural network for air pollutant concentration predictions: method development and evaluation. Environ. Pollut. 23 (1), 997-1004. https://doi.org/10.1016/j.envpol.2017.08.114.  
Li, X., Wu, J., Elser, M., Feng, T., Cao, J., El-Haddad, I., Huang, R., Tie, X., Prévôt, A., Li, G., 2018. Contributions of residential coal combustion to the air quality in Beijing-Tianjin-Hebei (BTH), China: a case study. Atmos. Chem. Phys. 18 (14), 10675-10691. https://doi.org/10.5194/acp-18-10675-2018.  
Lin, B., Jia, Z., 2020. Economic, energy and environmental impact of coal-to-electricity policy in China: a dynamic recursive CGE study. Sci. Total Environ. 698, 134241 https://doi.org/10.1016/j.scitotenv.2019.134241.  
Liu, C., Zhu, B., Ni, J., Wei, C., 2021. Residential coal-switch policy in China: development, achievement, and challenge. Energy Pol. 151, 112165 https://doi.org/10.1016/j.enpol.2021.112165, 2021.  
Liu, F., Page, A., Strode, S.A., Yoshida, Y., Choi, S., Zheng, B., Lamsal, L.N., Li, C., Krotkov, N.A., Eskes, H., Van Der A, R., Veefkind, P., Levelt, P.F., Hauser, O.P., Joiner, J., 2020. Abrupt decline in tropospheric nitrogen dioxide over China after the outbreak of COVID-19. Sci. Adv. 2992 https://doi.org/10.1126/sciadv.abc2992.  
Liu, Q., Wang, S., Zhang, W., Li, J., Dong, G., 2019. The effect of natural and anthropogenic factors on  $\mathrm{PM}_{2.5}$ : empirical evidence from Chinese cities with different income levels. Sci. Total Environ. 653, 157-167. https://doi.org/10.1016/j.scitotenv.2018.10.367.  
Mao, W., Wang, W., Jiao, L., Zhao, S., Liu, A., 2021. Modeling air quality prediction using a deep learning approach: method optimization and evaluation. Sustain. Cities Soc. 65, 102567 https://doi.org/10.1016/j.scs.2020.102567.  
Markard, J., 2018. The next phase of the energy transition and its implications for research and policy. Nat. Energy 3, 628-633. https://doi.org/10.1038/s41560-018-0171-7.  
Ong, B.T., Sugiura, K., Zettsu, K., 2016. Dynamically pre-trained deep recurrent neural networks using environmental monitoring data for predicting  $\mathrm{PM}_{2.5}$ . Neural Comput. Appl. 27 (6), 1553-1566. https://doi.org/10.1007/s00521-015-1955-3.  
Ouyang, X., Shao, Q., Zhu, X., He, Q., Xiang, C., Wei, G., 2019. Environmental regulation, economic growth and air pollution: panel threshold analysis for OECD countries. Sci. Total Environ. 657, 234-241. https://doi.org/10.1016/j.scitotenv.2018.12.056.  
Qin, D., Yu, J., Zou, G., Yong, R., Zhao, Q., Zhang, B., 2019. A novel combined prediction scheme based on CNN and LSTM for urban  $\mathrm{PM}_{2.5}$  concentration. IEEE Access 7, 20050-20059. https://10.1109/ACCESS.2019.2897028.  
Qi, Y., Li, Q., Karimian, H., Liu, D., 2019. A hybrid model for spatiotemporal forecasting of  $\mathrm{PM}_{2.5}$  based on graph convolutional neural network and long short-term memory. Sci. Total Environ. 664, 1-10. https://doi.org/10.1016/j.scitotenv.2019.01.333.  
Ren, K., Zhang, T., Tan, X., Zhai, Y., Bai, Y., Shen, X., Jia, Y., Hong, J., 2021. Life cycle assessment of ammonia synthesis based on pulverized coal entrained flow gasification technology in China. J. Clean. Prod. 328, 129658 https://doi.org/10.1016/j.jclepro.2021.129658.  
Schmidhuber, J., 2015. Deep learning in neural networks: an overview. Neural Network. 61, 85-117. https://doi.org/10.1016/j.neunet.2014.09.003.  
Sun, D., Fang, J., Sun, J., 2018. Health-related benefits of air quality improvement from coal control in China: evidence from the Jing-Jin-Ji region. Resour. Conserv. Recycl. 129, 416-423. https://doi.org/10.1016/j.resconrec.2016.09.021.  
Tang, B., Li, R., Li, X., Chen, H., 2017. An optimal production planning model of coal-fired power industry in China: considering the process of closing down inefficient units and developing CCS technologies. Appl. Energy 206, 519-530. https://doi.org/10.1016/j.apenergy.2017.08.215.  
Tang, D., Wang, C., Nie, J., Chen, R., Niu, Q., Kan, H., Chen, B., Perera, F., Taiyuan, C.D. C., 2014. Health benefits of improving air quality in Taiyuan, China. Environ. Int. 73, 235-242. https://doi.org/10.1016/j.envint.2014.07.016.  
Tang, X., Snowden, S., McLellan, B.C., Hoek, M., 2015. Clean coal use in China: challenges and policy implications. Energy Pol. 87, 517-523. https://doi.org/10.1016/j.enpol.2015.09.041.  
Van der, A.R.J., Mijling, B., Ding, J., Koukouli, M.E., Liu, F., Li, Q., Mao, H., Theys, N., 2017. Cleaning up the air: effectiveness of air quality policy for  $\mathrm{SO}_2$  and  $\mathrm{NO}_{\mathrm{x}}$  emissions in China. Atmos. Chem. Phys. 17 (3), 1775-1789. https://doi.org/10.5194/acp-17-1775-2017.  
Vinyals, O., Toshev, A., Bengio, S., Erhan, D., 2015. Show and tell: a neural image caption generator. Proceed. IEEE conf. comp. vision and pattern recog. 3156-3164.  
Wang, X., Wang, L., Liu, Y., Hu, S., Liu, X., Dong, Z., 2021. A data-driven air quality assessment method based on unsupervised machine learning and median statistical analysis: the case of China. J. Clean. Prod. 328, 129531 https://doi.org/10.1016/j.jclepro.2021.129531.  
Wei, W., Li, P., Wang, H., Song, M., 2018. Quantifying the effects of air pollution control policies: a case of Shanxi province in China. Atmos. Pollut. Res. 9 (3), 429-438. https://doi.org/10.1016/j.apr.2017.11.010.

Wei, Y., Chen, K., Kang, J., Chen, W., Wang, X., Zhang, X., 2022. Policy and management of carbon peaking and carbon neutrality: a literature review. Engineering. https://doi.org/10.1016/j.eng.2021.12.018.  
Wen, C., Liu, S., Yao, X., Peng, L., Li, X., Hu, Y., Chi, T., 2019. A novel spatiotemporal convolutional long short-term neural network for air pollution prediction. Sci. Total Environ. 654, 1091-1099. https://doi.org/10.1016/j.scitotenv.2018.11.086.  
Wubetie, H., 2017. Missing data management and statistical measurement of socioeconomic status: application of big data. J Big Data 4 (1), 1-44. https://doi.org/10.1186/s40537-017-0099-y.  
Xie, H., Wu, L., Zheng, D., 2019. Prediction on the energy consumption and coal demand of China in 2025. J. China Coal Soc. 44 (7), 1949-19.  
Xie, Y., Wu, D., Zhu, S., 2020. Can new energy vehicles subsidy curb the urban air pollution? Empirical evidence from pilot cities in China. Sci. Total Environ. 754, 142232 https://doi.org/10.1016/j.scitotenv.2020.142232.  
Xue, Y., Zhou, Z., Nie, T., Wang, K., Nie, L., Pan, T., Wu, X., Tian, H., Zhong, L., Li, J., Liu, H., Liu, S., Shao, P., 2016. Trends of multiple air pollutants emissions from residential coal combustion in Beijing and its implication on improving air quality for control measures. Atmos. Environ. 142, 303-312. https://doi.org/10.1016/j.atmosenv.2016.08.004.  
Yang, J., Sarkar, T., 2007. Interpolation/extrapolation of radar cross-section (RCS) data in the frequency domain using the Cauchy method. IEEE Trans. Antenn. Propag. 55 (10), 2844-2851. https://doi.org/10.1109/TAP.2007.904063.  
Yang, L., Xia, H., Zhang, X., Yuan, S., 2018. What matters for carbon emissions in regional sectors? A China study of extended STIRPAT model. J. Clean. Prod. 180, 595-602. https://doi.org/10.1016/j.jclepro.2018.01.116.

Yang, X., Teng, F., 2018. The air quality co-benefit of coal control strategy in China. Resour. Conserv. Recycl. 129, 373-382. https://doi.org/10.1016/j.resconrec.2016.08.011.  
Yuan, J., Na, C., Lei, Q., Xiong, M., Guo, J., Hu, Z., 2018. Coal use for power generation in China. Resour. Conserv. Recycl. 129, 443-453. https://doi.org/10.1016/j.resconrec.2016.03.021.  
Yuan, Q., Qi, B., Hu, D., Wang, J., Zhang, J., Yang, H., Zhang, S., Liu, L., Xu, L., Li, W., 2021. Spatiotemporal variations and reduction of air pollutants during the COVID-19 pandemic in a megacity of Yangtze River Delta in China. Sci. Total Environ. 751, 141820 https://doi.org/10.1016/j.scitotenv.2020.141820.  
Yu, C., Kang, J., Teng, J., Long, H., Fu, Y., 2021. Does coal-to-gas policy reduce air pollution? Evidence from a quasi-natural experiment in China. Sci. Total Environ. 773, 144645 https://doi.org/10.1016/j.scitotenv.2020.144645.  
Zeb, R., Salar, L., Awan, U., Zaman, K., Shahbaz, M., 2014. Causal links between renewable energy, environmental degradation and economic growth in selected SAARC countries: progress towards green economy. Renew. Energy 71, 123-132. https://doi.org/10.1016/j.renene.2014.05.012.  
Zhang, Y., Liu, C., Li, K., Zhou, Y., 2018. Strategy on China's regional coal consumption control: a case study of Shandong province. Energy Pol. 112, 316-327. https://doi.org/10.1016/j.enpol.2017.10.035.  
Zhu, T., 2019. Energy transformation and efficient and clean utilization of coal in China. Energy Sci. Technol. 17 (2), 75-81+96.