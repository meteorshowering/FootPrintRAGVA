# Striking impacts of biomass burning on  $\mathrm{PM}_{2.5}$  concentrations in Northeast China through the emission inventory improvement

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/617fd39f-94a5-429e-8f61-b0abbcd11785/41bc4f1049c064e0bd91a1a35398fde98ba9ef750636515b6b1180f9b5ad4e61.jpg)

Lijiao Chen<sup>a</sup>, Yang Gao<sup>a, *</sup>, Mingchen Ma<sup>a</sup>, Lili Wang<sup>b</sup>, Qinglu Wang<sup>b</sup>, Shuhui Guan<sup>c</sup>, Xiaohong Yao<sup>a</sup>, Huiwang Gao<sup>a</sup>

<sup>a</sup> Frontiers Science Center for Deep Ocean Multispheres and Earth System, and Key Laboratory of Marine Environment and Ecology, Ministry of Education, Ocean University of China, and Qingdao National Laboratory for Marine Science and Technology, Qingdao, 266100, China  
$^{b}$  State Key Laboratory of Atmospheric Boundary Layer Physics and Atmospheric Chemistry, Institute of Atmospheric Physics, Chinese Academy of Sciences, Beijing, 100029, China  
c Qilu University of Technology (Shandong Academy of Sciences), Shandong Computer Science Center (National Supercomputer Center in Jinan), Jinan, 250014, PR China

# ARTICLEINFO

Keywords:

Biomass burning

VIIRS

GFED

PM2.5

Northeast China

WRF-CMAQ

Aerosol direct radiative effects

# ABSTRACT

Biomass burning exerts substantial influences on air quality and climate, which in turn to further aggravate air quality. The biomass burning emissions in particular of the agricultural burning may suffer large uncertainties which limits the understanding of their impact on air quality. Based on an improved emission inventory of the Visible Infrared Imaging Radiometer Suite (VIIRS) relative to commonly used Global Fire Emissions Database (GFED), we thoroughly evaluate the impact of biomass burning on air quality and climate during the episodes of November 2017 in Northeast China which is rich in agriculture burning. The results first indicate substantial underestimates in simulated  $\mathrm{PM}_{2.5}$  concentrations without the inclusion of biomass burning emission inventory, based on a regional air quality model Weather Research and Forecasting model and Community Multiscale Air Quality model (WRF-CMAQ). The addition of biomass burning emissions from GFED then reduces the bias to a certain extent, which is further reduced by replacing the agricultural fires data in GFED with VIIRS. Numerical sensitivity experiments show that based on the improved emission inventory, the contribution of biomass burning emissions to  $\mathrm{PM}_{2.5}$  concentrations in Northeast China reaches  $32\%$ , contrasting to  $15\%$  based on GFED, during the episode from November 1 to 7, 2017. Aerosol direct radiative effects from biomass burning are finally elucidated, which not only reduce downward surface shortwave radiation and planetary boundary layer height, but also affect the vertical distribution of air temperature, wind speed and relative humidity, favorable to the accumulation of  $\mathrm{PM}_{2.5}$ . During November 1-7, 2017, the mean daily  $\mathrm{PM}_{2.5}$  enhancement due to aerosol radiative effects from VIIRS_G is  $16\mu \mathrm{g}\mathrm{m}^{-3}$ , a few times higher than that of  $2.8\mu \mathrm{g}\mathrm{m}^{-3}$  from GFED. The study stresses the critical role of biomass burning, particularly of small fires easily missed in the traditional low-resolution satellite products, on air quality.

# 1. Introduction

Biomass burning, mainly including burning from forest, grassland, and agricultural fires (Andreae and Merlet, 2001; Akagi et al., 2011), emits a substantial amount of air pollutants such as fine particles, nitrogen oxides  $\mathrm{(NO_x)}$  (Koppmann et al., 2005; van der Werf et al., 2017; Ballesteros-Gonzalez et al., 2020), which strongly affect air quality (Ryu et al., 2007; Chen et al., 2017a), climate (Randerson et al., 2006; Taylor, 2010; Tosca et al., 2013) and human health (Yao et al., 2016; Punsompong et al., 2021). As one of the major sources of  $\mathrm{PM}_{2.5}$  (Tao et al.,

2013; Cheng et al., 2014; Zong et al., 2016; Zhang et al., 2017b), biomass burning emissions could contribute a large portion of the accumulation of  $\mathrm{PM}_{2.5}$  concentrations (Pimonsree and Vongruang, 2018; Mehmood et al., 2020; Rahman et al., 2020; Rojano et al., 2021).

As the primary grain base, Northeast China produces a large volume of agricultural straw (Bi et al., 2010), which become the dominant burning type in the region (Wang et al., 2020a). The burning of the agricultural straw can cause severe air pollution during harvest seasons (Cui et al., 2021). Even from the national perspective, biomass burning emissions in Northeast China tend to be larger than other areas during

harvest seasons such as spring and fall (Qiu et al., 2016; Li et al., 2020). Recently, severe haze pollution has frequently invaded Northeast China (Cao et al., 2016; Chen et al., 2017b; Zhang et al., 2020a), and high  $\mathrm{PM}_{2.5}$  concentrations therein are strongly associated with the biomass burning particularly of harvest seasons (Cao et al., 2017; van der Werf et al., 2017; Chen et al., 2019b; Li et al., 2019). Specifically, over Northeast China, numerical modeling indicated that biomass burning contributed on average of more than  $50\%$  of the monthly mean  $\mathrm{PM}_{2.5}$  concentrations in October 2014 (Ke et al., 2020),  $75 - 100\mu \mathrm{g}\mathrm{m}^{-3}$  to daily  $\mathrm{PM}_{2.5}$  concentrations during November 6-9, 2015 (van der Werf et al., 2017), and Li et al. (2019) found that mean  $\mathrm{PM}_{2.5}$  concentrations on fire-polluted days were  $22 - 54\%$  higher than those on no-fire-polluted days in Northeast China during 2015-2017. Through applying the method of source apportionment, Chen et al. (2019b) found that biomass burning played an even more important role in causing the air pollution over Northeast China in fall 2018 compared to the major anthropogenic emission sources such as coal combustion and traffic.

Air quality models are efficient tools in quantifying the effect of biomass burning emissions on air quality, which is, however, limited by the accuracy of fire emissions inventory. Traditionally, the commonly adopted fire emissions inventories such as Global Fire Emissions Database (GFED) and Fire INventory from NCAR (FINN), have been reported to underestimate biomass burning emissions over Northeast China (Uranishi et al., 2019; Cheng et al., 2021). For instance, based on Community Multiscale Air Quality (CMAQ) driven by Weather Research and Forecasting model (WRF),  $\mathrm{PM}_{2.5}$  emissions from biomass burning were found to be underestimated by more than seven times in both GFEDv4 and FINNv1.5 emission inventories over Northeast China during 2012-2013 (Uranishi et al., 2019). Another numerical simulation driven by FINN emission inventory revealed striking underestimations of daily  $\mathrm{PM}_{2.5}$  concentrations as high as  $230\mu \mathrm{g}\mathrm{m}^{-3}$  from fall 2018 to spring 2019 in Northeast China (Cheng et al., 2021). The primary reason is associated with the fire data of Moderate Resolution Imaging Spectroradiometer (MODIS), which is unable to detect small agricultural fires due to a relatively coarse spatial resolution at  $1\mathrm{km}$  (Hawbaker et al., 2008). In contrast, data provided by another instrument such as Visible Infrared Imaging Radiometer Suite (VIIRS) has higher spatial resolutions of  $375\mathrm{m}$  and  $750\mathrm{m}$ , being able to detect much smaller (i.e., 5-10 times smaller) fire points compared to MODIS (Zhang et al., 2017a; Vadrevu and Lasko, 2018). Previous studies have combined "small-fire-optimised" product from VIIRS with Himawari-8 sensors and constructed the improved agricultural fire emission inventory over Eastern China  $(111 - 123^{\circ}\mathrm{E},$ $27 - 40^{\circ}\mathrm{N})$  i.e., multiple times as high as the emissions based on GFED (Zhang et al., 2020b). Nevertheless, the capability of VIIRS in detecting fires in Northeast China as well as subsequent influences on the air quality therein is not yet clear.

Besides of deteriorating the air quality, aerosols emitted from biomass burning play pivotal roles in affecting the climate through aerosol radiative effects (Huang et al., 2016; Mukherjee et al., 2020). A number of studies have investigated aerosol radiative effects of biomass burning, implying that the substantial enhancement of aerosols during the burning episodes may weaken downward surface shortwave radiation (DSSR), heat up the top of planetary boundary layer (PBL) and lead to cooler at the surface (Lin et al., 2014; Huang et al., 2016). Aerosols can hinder development of PBL (Gao et al., 2018), inducing a more stable PBL and aggravate air pollution (Chen et al., 2019a). Using the numerical model Weather Research and Forecasting with Chemistry (WRF-Chem), Wang et al. (2016) showed a decrease of DSSR at  $20\mathrm{W}$ $\mathrm{m}^{-2}$  on average and a maximum decrease of near-surface air temperature at  $1.4^{\circ}\mathrm{C}$ , due to aerosol radiative effects over East Asia in March 2005. Wang et al. (2014) illustrated that aerosol radiative feedback induced a decrease of near-surface air temperature and wind speed, and an increase of near-surface RH during a severe haze episode over North China Plain in January 2013. This effect is clarified in Guan et al. (2020), showing that aerosol radiative effects from the intense wildfires in the southeastern United States in November 2016 can lead to an extra  $\mathrm{PM}_{2.5}$

concentrations enhancement. Chen et al. (2019a) further showed a maximum decrease of  $2\mathrm{K}$  for near-surface air temperature due to aerosol radiative effects caused by the haze event in Beijing-Tianjin-Hebei from December 16 to 29, 2015. Besides of surface, Gao et al. (2015) indicated that aerosol radiative effects induced by a haze event in North China Plain during January 10 to 15, 2013 caused the near-surface RH to increase by  $2 - 4\%$  while the aerosol radiative effects would decrease RH at  $950\mathrm{hPa}$  and  $850\mathrm{hPa}$  by  $1 - 6\%$ . However, to what extent the biomass burning may feedback to the climate and subsequently enhance the air pollution in Northeast China remains not to be clear yet.

To this end, we first make a thorough evaluation of the air quality model in reproducing severe pollution events in Northeast China, through the application of the traditional and higher-resolution emission inventory, with the hypothesis that the higher-resolution emission inventory such as VIIRS may strengthen the capability of numerical models in reproducing the severe air pollution events. What is followed is to examine the contribution of biomass burning emissions on air quality in Northeast China based on the improved emission inventory, as well as the elucidation of aerosol radiative effects of biomass burning on aggravating the air quality. Considering the widespread agricultural burning worldwide, the study highlights the importance of re-examining the impact of agricultural burning on air quality based on more accurate emission inventory in broader areas.

# 2. Methodology

# 2.1. Model configurations

The two-way coupled WRF-CMAQ model (Wong et al., 2012; Appel et al., 2018) is used in this study, with versions of 3.8 and 5.2 respectively for WRF and CMAQ, and the simulation domain is displayed in Fig. 1a, including China as well as a few other countries. The spatial resolution of the simulation grid is  $36\mathrm{km}$  by  $36\mathrm{km}$ , and there is a total of 34 vertical layers spanning from surface to  $50\mathrm{hPa}$ . Observational data (shown in Fig. 1b) of  $\mathrm{PM}_{2.5}$  is available at the China National Environmental Monitoring Center (http://www/pm25.in; last access: November 15, 2021), and meteorological parameters including air temperature at  $2\mathrm{-m}$  (T2), specific humidity at  $2\mathrm{-m}$  (Q2) and wind speed at  $10\mathrm{-m}$  (WS10) are obtained from the National Climatic Data Center (NCDC, https://www.ncdc.noaa.gov/data-access/quick-links#dsi-3505; last access: August 15, 2022). The physics schemes applied are the same as those in the previous studies (Zhang et al., 2019; Yan et al., 2021), which are listed in Table S1. The initial and boundary conditions are from NCEP Climate Forecast System Reanalysis (CFSR) version 2 (Saha et al., 2014) for WRF, Model for Ozone and Related chemical Tracers, version 4 (MOZART-4 (Emmons et al., 2010)) for CMAQ with the downscaling technique discussed in Ma et al. (2019). The carbon-bond version 6 (CB6) and Aerosol Module Version 6 (AERO6) are selected for the gas phase chemical mechanism and aerosol scheme, respectively.

# 2.2. Information on emission inventory

Anthropogenic emissions are based on the Multi-resolution Emission Inventory for China (MEIC; http://www.meicmodel.org; last access: November 15, 2021) and biogenic emissions are generated by the Model of Emissions of Gases and Aerosols from Nature version 2.1 (MEGAN (Guenther et al., 2012)), the same as the previous studies (Ma et al., 2019; Ma et al., 2022).

GFED provide monthly biomass burning emissions at a spatial resolution of  $0.25 \times 0.25^{\circ} (\sim 25\mathrm{km})$ , which is interpolated to the model grid with the spatial resolution of  $36\mathrm{km} \times 36\mathrm{km}$ . Daily and hourly emission ratios based on Randerson et al. (2017) are used to obtain the hourly biomass burning emissions, similar to our previous study (Zeng et al., 2022). The vertical distribution of fire emissions are applied based on the injection heights in Table 1 of Dentener et al. (2006), in which the

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/617fd39f-94a5-429e-8f61-b0abbcd11785/40d4f3079ca1e10d61d974643fb5542ac96183595da558caa77ee09c0dae8693.jpg)  
Fig. 1. The simulation domain (Fig. 1a) with the red square indicating the regions of Northeast China (i.e., Heilongjiang (HLJ), Jilin (JL), Liaoning (LN)), which is zoomed in and shown in Fig. 1b, with the red and blue dots indicative of observational data for  $\mathrm{PM}_{2.5}$  and meteorology. (For interpretation of the references to colour in this figure legend, the reader is referred to the Web version of this article.)

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/617fd39f-94a5-429e-8f61-b0abbcd11785/e1cf49f6b79ad2749ca70651c674788f6e26e62d0af62b1ba159ae3258072ce0.jpg)

Table 1 List of six simulation scenarios.  

<table><tr><td>Case</td><td>Fire emissions</td><td>Aerosol direct radiative effects</td></tr><tr><td>1</td><td>No</td><td>On</td></tr><tr><td>2</td><td>No</td><td>Off</td></tr><tr><td>3</td><td>GFED</td><td>On</td></tr><tr><td>4</td><td>GFED</td><td>Off</td></tr><tr><td>5</td><td>VIIRS_G</td><td>On</td></tr><tr><td>6</td><td>VIIRS_G</td><td>Off</td></tr></table>

altitudes are divided into six categories including  $0 - 100\mathrm{m}$ ,  $100 - 500\mathrm{m}$ ,  $500 - 1\mathrm{km}$ ,  $1 - 2\mathrm{km}$ ,  $2 - 3\mathrm{km}$  and  $3 - 6\mathrm{km}$ , and the partition is dependent on the fire location and type. The agricultural fire emissions in Northeast China in GFED are replaced by VIIRS, while the other types of biomass burning emissions maintain the same as GFED, referred to as VIIRS_G. The specific information on how to retrieve daily VIIRS emissions are discussed below, with more detailed information in Zhang et al. (2020b). Note daily VIIRS emissions are allocated to hourly emissions based on allocation factors from GFED (Randerson et al., 2017).

VIIRS fire products, including  $375\mathrm{m}$  I-band and  $750\mathrm{m}$  M-band products, and cloud mask product at  $375\mathrm{m}$  onboard the polar-orbit Suomi NPP satellite are used (https://ladsweb.modaps.eosdis.nasa.gov/; last access: May 10, 2022) in the calculation of fire emissions from dry matter burned. VIIRS I-band covers the wavelengths of peak spectral radiance for blackbodies which emit at temperatures ranging from  $737\mathrm{K}$  to  $817\mathrm{K}$ , whereas VIIRS M-band is more capable in detecting larger fires with higher temperatures relative to I-band. Taking together, compared to MODIS 1-km fire product, VIIRS I-band and M-band products exhibit enhanced capabilities in detecting small fires (Schroeder et al., 2014), which are therefore used in this study. More detailed information on VIIRS fire products can be found in the User's Guide (https://viirsland.gsfc.nasa.gov/PDF/VIIRS.activefire_USER_Guide.pdf; last access: November 20, 2022). Daily VIIRS fire emissions in Northeast China (i.e. Heilongjiang, Jilin and Liaoning Province; Fig. 1b) are calculated based on Eq. (1) following the method of Zhang et al. (2020b). The calculation is operated at grid spacings of  $0.1^{\circ} \times 0.1^{\circ}$  resolution, which is then interpolated to  $36\mathrm{km} \times 36\mathrm{km}$  to combine with GFED and anthropogenic emissions prior to the simulations.

$$
\mathrm {E} = \mathrm {F R E} \times \mathrm {C R} \times \mathrm {E F} \tag {1}
$$

where E is open agricultural burning emissions for various species, FRE (MJ) is fire radiative energy, CR is the conversion ratio with a value of  $0.368 \pm 0.015 \mathrm{~kg} \mathrm{MJ}^{-1}$ , EF  $(\mathrm{g} \mathrm{kg}^{-1})$  is the emission factor. The product of FRE and CR represents the amount of dry matter burned.

FRE is integrated on daily basis using fire radiative power (FRP; unit: MW). Considering the temporal resolution of FRP in VIIRS is twice per

day ( $\sim$ 01:00 LST and  $\sim$ 13:00 LST), a higher temporal (i.e., hourly) resolution data set Himawari-8 fire product (ftp://ftp.ptree.jaxa.jp/pub/himawari/L3/WLF<sub>2</sub> last access: May 10, 2022), despite of a low spatial resolution at 2-km, is used to fit a Gaussian distribution, which then facilitates the daily integration using Eq. (2) based on the approaches in Andela et al. (2015) and Zhang et al. (2020b).

$$
\rho_ {V I I R S _ {\text {H i m}} t} = \rho_ {V I I R S _ {\text {n i g h t}}} + e ^ {\frac {\left(t _ {V I I R S _ {\text {d a y}}} - t _ {H i m p e a k}\right) ^ {2}}{2 \sigma^ {2}}} \left(\rho_ {V I I R S _ {\text {d a y}}} - \rho_ {V I I R S _ {\text {n i g h t}}}\right) e ^ {- \frac {\left(t - t _ {H i m p e a k}\right) ^ {2}}{2 \sigma^ {2}}} \tag {2}
$$

where  $\rho$  is FRP areal density  $(\mathrm{MW~km}^{-2})$ ,  $\rho_{VIIRS_{night}}$  and  $\rho_{VIIRS_{day}}$  are calculated through the sum of FRP in each grid divided by the total agricultural area without cloud obscuration in the same grid during night ( $\sim 01:00$  LST) and daytime ( $\sim 13:00$  LST), respectively; The agricultural area is calculated based on the land cover data in 2017 with a spatial resolution of  $30\mathrm{-m}$  (Yang and Huang, 2021). t is the instantaneous time;  $t_{VIIRS_{day}}$  is the daytime ( $\sim 13:00$  LST) of FRP in VIIRS;  $t_{Himpeak}$  and  $\sigma$  represent the peak time and standard deviation in the fitted diurnal cycle of Himawari FRP, which are determined to be 13.81 and 5.04, respectively.

The emission factors in Zhang et al. (2020b) only covered four species, including BC,  $\mathrm{PM}_{2.5}$ , CO and  $\mathrm{CO}_{2}$ , which were derived from field observation in Jiangsu Province over eastern China (Zhang et al., 2015) and not suitable for Northeast China. Thus, EFs of most species are updated based on the field agricultural fire burning experiment conducted over Northeast China in April 2018 (Wang et al., 2020b). During the experiment, smoke was collected within a short distance at approximately  $5 - 10\mathrm{m}$  from the fire source, and the concentrations of various species were measured (Wang et al., 2020b). EFs were then derived by applying the carbon mass balance method to the measured concentrations for maize and rice, with detailed discussions on the method in Zhang et al. (2015), and the mean value of these two crops was adopted in this study as the EFs for agriculture burning shown in Table S2 (without asterisk). EFs for other species (Table S2; with asterisk) are directly available at Akagi et al. (2011).

# 2.3. Numerical scenarios designed in this study

Severe haze pollution occurred in Northeast China from November 1 to 7, 2017 (i.e., Fig. 2 in section 3.1). During this period, there were many biomass burning activities in Northeast China, providing a great opportunity to investigate the potential influence from biomass burning emissions. To evaluate the impact of biomass burning emissions, together with their radiative effects, on  $\mathrm{PM}_{2.5}$  concentrations, six numerical experiments are designed (Table 1). The simulation runs are from October 24 to November 30, 2017, with the period of October

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/617fd39f-94a5-429e-8f61-b0abbcd11785/e1ea2bb0537d857233fe4997cd5d62ccad8f2b06e39249eab042bd13bca869ab.jpg)  
Fig. 2. The box-and-whisker plots showing observed daily  $\mathrm{PM}_{2.5}$  concentrations (left Y axis), and the histograms (right Y axis) representing the daily dry matter burned based on GFED (blue solid bars) and VIIRS (blue hatched bars) in November 2017 over three provinces, (a) Heilongjiang Province, (b) Jilin Province and (c) Liaoning Province. The box-and-whisker plots include the minimum, maximum (line end points), 25th percentile, 75th percentile (boxes), medians (black lines), and average (red points). (For interpretation of the references to colour in this figure legend, the reader is referred to the Web version of this article.)

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/617fd39f-94a5-429e-8f61-b0abbcd11785/ae27decd78f4c74f178829ac306ccfde0da7591ff16ea0d9c407c5c386b934c9.jpg)

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/617fd39f-94a5-429e-8f61-b0abbcd11785/f838f59c35ee391d4f7a1ab5650c17369d716b7f911d565ded763dfe1474b65d.jpg)  
24-31 as spin-up.

# 3. Results

# 3.1. Agricultural fire emissions comparisons between VIIRS and GFED

Given that majority of fires in Northeast China are agricultural fires which account for approximately  $90\%$  of the total fires (Wang et al., 2020a), we first compare the capability of VIIRS and GFED in detecting agricultural fires over Northeast China in November 2017. Daily dry matter burned from VIIRS is substantially higher than that of GFED (Fig. 2), which is clearly displayed in the spatial distribution in Fig. S1 in the supporting information. Despite of spatial similarities between the two datasets, the amount of dry matter burned differs dramatically, i.e., it is  $3475\mathrm{Gg}$  and  $1416\mathrm{Gg}$  in Northeast China from VIIRS and GFED, respectively, indicating that VIIRS is on average of 2.5 times as high as that in GFED. It is noteworthy that there are apparent inconsistencies between  $\mathrm{PM}_{2.5}$  concentrations and the amount of biomass burning, e.g., high  $\mathrm{PM}_{2.5}$  concentrations but relatively low amount of dry matter burned is observable on November 6 and 7th, which is likely attributable to the high fraction of cloud cover in particular over Heilongjiang, with cloud cover higher than  $90\%$  in majority of the areas, weakening the capability of detecting fires in both VIIRS and GFED. The higher amount

of agricultural fires in VIIRS than GFED has been found in other regions. For instance, Zhang et al. (2020b) showed that the agricultural fires in Eastern China during 2012-2015 from VIIRS is approximately 2-5 times higher than that of GFED, resulting from the much smaller (i.e., 10 times) pixel area of VIIRS compared to GFED.

Moreover, the total emissions of  $\mathrm{CO}_{2}$ , CO,  $\mathrm{PM}_{2.5}$ , BC, OC,  $\mathrm{SO}_{2}$ , NO,  $\mathrm{NO}_2$ ,  $\mathrm{NH}_3$  and non-methane volatile organic compounds (NMVOC) from agricultural fires in VIIRS over Northeast China in November 2017 are approximately one to three times as high as those from GFED (Fig. 3a). Specifically, the evolutions of daily  $\mathrm{PM}_{2.5}$  emissions are delineated (Fig. 3b), indicating that besides of an overall enhancement in VIIRS relative to GFED on the daily basis, a much stronger emission boost in VIIRS is clearly observable during the episodic period, i.e., first week of November 2017.

# 3.2. Model evaluation

To evaluate how well the model reproduces the meteorological conditions, the simulated T2, Q2 and WS10 are compared with observational data of NCDC. The statistical metrics are shown in Table S3 indicating a satisfactory performance in comparison to the benchmarks proposed by Emery et al. (2001). For air pollutants, hourly  $\mathrm{PM}_{2.5}$  concentrations between observations and three simulated cases averaged

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/617fd39f-94a5-429e-8f61-b0abbcd11785/bc5032559b352d6724d04bace6c9456f9e07db3f0fc14aa56df1382ac8a42574.jpg)

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/617fd39f-94a5-429e-8f61-b0abbcd11785/1c58997060a48a6a3176d2aae2e9a2047586e5e926be515d0bdb568f71bb741e.jpg)  
Fig. 3. Comparison of emissions of air pollutants due to agricultural fires from GFED and VIIRS in Northeast China in November 2017. (a), comparison of monthly emissions of each species reported by GFED and VIIRS over Northeast China for November 2017. (b), comparison of daily  $\mathrm{PM}_{2.5}$  emissions reported by GFED and VIIRS over Northeast China in November 2017.

over the selected regions (black boxes in Fig. S1b) are shown in Fig. 4, and the reason of focusing on these areas lies in that biomass burning emissions over there account for the majority of burnings  $(76\% -98\%)$  of the three provinces based on VIIRS emission inventory. For the case without taking biomass burning emissions into account, referred to as Base, the mean fractional biases (MFB) range from  $-53\%$  to  $-22\%$  for the three provinces in Northeast China. By adding biomass burning emissions from GFED, the MFB are slightly reduced by  $1\% -8\%$ . When the agricultural burning emissions in GFED are replaced by VIIRS (referred to as VIIRS_G), the MFB of  $\mathrm{PM}_{2.5}$  concentrations are further reduced by  $5\% -7\%$ , with correlation coefficients between model and observations improved as well. In particular, the peaks, i.e., during November 1-7 2017, to a large degree is better captured by the simulations.

Despite of the comparable fractional increment by adding VIIRS compared to GFED among the three provinces, the amount changes in  $\mathrm{PM}_{2.5}$  vary quite a bit. To better understand the contribution of  $\mathrm{PM}_{2.5}$  constituents to  $\mathrm{PM}_{2.5}$  changes (e.g., scenario GFED vs. VIIRS_G), Fig. S2 displays the concentrations of  $\mathrm{PM}_{2.5}$  constituents, including primary organic aerosol (POA), secondary organic aerosol (SOA), elemental carbon (EC), sulfate  $(\mathrm{SO}_4^{2-})$ , nitrate  $(\mathrm{NO}_3^-)$ , ammonium  $(\mathrm{NH}_4^+)$ , and others which is the difference between  $\mathrm{PM}_{2.5}$  concentrations and summation of the six constituents abovementioned. Specifically, the mean  $\mathrm{PM}_{2.5}$  concentration enhancement from scenario GFED (case 3 in Table 1) to VIIRS_G (case 5 in Table 1) is  $39~\mu \mathrm{g}~\mathrm{m}^{-3}$ ,  $18~\mu \mathrm{g}~\mathrm{m}^{-3}$  and  $1~\mu \mathrm{g}~\mathrm{m}^{-3}$  over the selected areas of Heilongjiang, Jilin and Liaoning, respectively (Fig. 4). Among the  $\mathrm{PM}_{2.5}$  increases from GFED to VIIRS,

secondary inorganic aerosol in general accounts for less than  $25\%$ , SOA accounts for  $6\% - 10\%$ , whereas POA accounts for  $28\% - 50\%$ , and others majority of which are from primary emissions (Appel et al., 2008) account for  $35\% - 42\%$ , indicating a predominant effect of primary emissions and aerosols.

Another feature emerges from Fig. 4 is that the influence of VIIRS data on  $\mathrm{PM}_{2.5}$  concentrations in Jilin and Liaoning (Fig. 4b and c) is much smaller compared to that in Heilongjiang (Fig. 4a). To illustrate the possible reasons, using organic carbon (OC) as an example, we compare the emission amount of OC from MEIC (anthropogenic emissions), GFED and VIIRS over the selected areas in the Northeast (Fig. S1b) on November 1-7, 2017. In general, OC emission amount in VIIRS is a factor of two to three compared to that in GFED for the three provinces. Similarly, anthropogenic OC emissions over Heilongjiang are less than one third of OC emissions in VIIRS over Heilongjiang. However, anthropogenic OC emissions are comparable to or even a few times larger than those in VIIRS over Jilin and Liaoning, respectively, triggering a much smaller impact of VIIRS emissions over these two provinces, particular of Liaoning, in comparison to that for Heilongjiang (Fig. 4).

It is noteworthy that underestimation may still exist even with the VIIRS agricultural emission inventory, and there are a few possible reasons. Firstly, Liu et al. (2019) indicated that over northwestern India, MODIS only captured approximately half of the active fires, whereas VIIRS could detect about two thirds (0.68), and this scaling ratio is directly applied to the VIIRS emission inventory in another study (Yang et al., 2020). However, in terms of the uncertainties of the ratio, we keep

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/617fd39f-94a5-429e-8f61-b0abbcd11785/c83354b805b9ef3c3783ba9470bb6ab38eb6c64af6b87c7032a3e26247fd3f65.jpg)

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/617fd39f-94a5-429e-8f61-b0abbcd11785/aa86c39867b433fc6b5aced6f069faa8dcf038a916672579f691a37909223cdd.jpg)

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/617fd39f-94a5-429e-8f61-b0abbcd11785/761bf7ef4c10e4137a7be3ea468d6c72927dc843fa50ef9b29a9dffaa8818ae5.jpg)  
Fig. 4. Time series of simulated and observed  $\mathrm{PM}_{2.5}$  concentrations in Heilongjiang Province (a), Jilin Province (b) and Liaoning Province (c). Please note that only the data inside the black boxes (Fig. S1b) over these three provinces are used. The black line represents observations, the green, red and blue lines represent the scenarios, respectively, without biomass burning emissions (Case 1 in Table 1), with biomass burning emissions from GFED (Case 3 in Table 1) and VIIRS_G (Case 5 in Table 1). The statistical metrics including MFB, MFE and R (formula shown in Appendix A) among the three scenarios are listed on top of each panel. (For interpretation of the references to colour in this figure legend, the reader is referred to the Web version of this article.)

the amount of agricultural burning emissions derived from VIIRS in this study despite of possible underestimations. The negative bias during the episode particularly of November 7 is tightly linked to the low emission amount detected by VIIRS (Fig. 2), which was explained above to be associated with high cloud cover therein. Secondly, the bias may lie in the organic aerosols. Compared to a previous version CMAQ5.1 (Appel et al., 2017), CMAQ5.2 includes several enhancement of aerosol treatment, e.g., adding a calculation of semi-volatile primary organic aerosol and an empirical representation of anthropogenic combustion SOA, and

improving properties of SOA species such as the ratio of aerosol organic mass to organic carbon (Pye et al., 2017; Appel et al., 2018). However, there still might be underestimates of primary organic aerosol resulting from uncertainties in anthropogenic emissions (Gao et al., 2022), as well as underestimates of secondary organic aerosol such as monoterpene oxidation (Appel et al., 2021).

# 3.3. The impact of biomass burning emissions on  $PM_{2.5}$  concentrations by GFED and VIIRS_G

Fig. 5a-c shows the spatial distribution of mean  $\mathrm{PM}_{2.5}$  concentrations at Base (without biomass burning emissions), the case by adding biomass burning emissions from GFED (GFED), and another case by replacing agricultural emissions in GFED with VIIRS (VIIRS_G) in Northeast China from November 1 to 7, 2017. Biomass burning emissions have large impacts on  $\mathrm{PM}_{2.5}$  concentrations in Northeast China, especially in Heilongjiang Province. Fig. 5d and e show the contributions to  $\mathrm{PM}_{2.5}$  concentrations driven by emission inventory from GFED and VIIRS_G, displaying an amplified impact of biomass burning emissions on  $\mathrm{PM}_{2.5}$  from VIIRS_G compared to that from GFED.

To quantify to what extent biomass burning emissions enhance  $\mathrm{PM}_{2.5}$  concentrations, the fractional contribution is calculated over the key pollution areas (i.e., black boxes in Fig. S1). Biomass burning emissions from GFED contribute to  $29\%$ $14\%$  and  $3\%$  on average of  $15\%$  of the mean  $\mathrm{PM}_{2.5}$  concentrations in Heilongjiang, Jilin and Liaoning, respectively (Fig. 5d vs. Fig. 5a). When VIIRS_G emission inventory is applied,

the contributions increase to  $60\%$ ,  $32\%$  and  $5\%$ , respectively, on average of  $32\%$  which is two times as high as that from GFED. Considering that small fires are largely missed in GFED, our results emphasize the importance of small fires in contributing to the enhancement of  $\mathrm{PM}_{2.5}$  concentrations (Fig. 5e vs. Fig. 5a, d).

# 3.4. The aerosol direct radiative effects of biomass burning emissions on  $PM_{2.5}$

Previous studies have indicated that aerosol direct radiative effects can deteriorate local air quality by altering meteorological parameters, i.e., reducing DSSR and PBL height, modifying the vertical distribution of air temperature, relative humidity (RH), and wind speed (Wang et al., 2014; Qiu et al., 2017). To investigate the radiative effects from biomass burning emissions in VIIRS_G, calculations (i.e., (case 5 - case 6) - (case 1 - case 2) in Table 1) are conducted over the areas with the most intensive biomass burning (top black box in Fig. S1b) during November 1 to 7 2017, for meteorological parameters including DSSR, PBL height, T2, RH, and wind speed (Fig. 6). Specifically, the differences between case 5

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/617fd39f-94a5-429e-8f61-b0abbcd11785/8b04023f5608ec3839b051f46e77ab3fdd92ae537247d77eb5f7184d46a4f06c.jpg)

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/617fd39f-94a5-429e-8f61-b0abbcd11785/b9e544fe804ca3cf79de45b9041168636db69d46fd889c1d6b559b02cb09ab8e.jpg)

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/617fd39f-94a5-429e-8f61-b0abbcd11785/30a1c18749897bcdeab263108ae71f1fa13cb9b4dc7e18ebadab1430932d720d.jpg)

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/617fd39f-94a5-429e-8f61-b0abbcd11785/7ccfa996b2ed6f130a2351958fca8630daed9deb4dd05869a384a5b674b57fe5.jpg)  
Fig. 5. Spatial distribution of mean  $\mathrm{PM}_{2.5}$  concentrations under different scenarios from November 1 to 7, 2017, for cases without biomass burning (a; Case 1 in Table 1), with biomass burning emissions from GFED (b; Case 3 in Table 1) and VIIRS_G (c; Case 5 in Table 1), as well as the differences between cases GFED (d), VIIRS_G (e) and Base.

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/617fd39f-94a5-429e-8f61-b0abbcd11785/3b8173b914b5050accef8b24fc0fe8993413b1954112869d3e984a3edd4532bc.jpg)

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/617fd39f-94a5-429e-8f61-b0abbcd11785/a25dc1f4089026bbfa628e45f7fb6b07b2990b2b2f9d8672e26311efd99e8fc7.jpg)  
Fig. 6. Simulated hourly  $\mathrm{PM}_{2.5}$  concentrations, as well as changes (i.e., (case 5 - case 6) - (case 1 - case 2) in Table 1) of  $\mathrm{PM}_{2.5}$  concentrations, meteorological parameters including downward surface shortwave radiation, PBL height, air temperature at  $2\text{-m}$ , relative humidity and wind speed at  $10\text{-m}$  induced by aerosol direct radiative effects over Heilongjiang (top black box in Fig. S1b) from November 1 to 7, 2017.

and case 6 (case 5 - case 6) reflect the aerosol radiative effects from all emissions, whereas differences between case 1 and case 2 (case 1- case 2) indicate aerosol radiative effects due to emissions except biomass burning. Therefore, results of (case 5 - case 6) - (case 1 - case 2) are indicative of aerosol radiative effects due to biomass burning emissions from VIIRS_G, i.e., DSSR is strikingly reduced by  $18\mathrm{Wm}^{-2}$ $(20\%)$  on average, primarily attributable to the absorption and scattering of aerosols (Gao et al., 2016). Meanwhile, other meteorological parameters are also affected, i.e., a decrease in PBL height, T2 and near-surface wind speed and an increase in near-surface RH.

Strongly affected by changes in the meteorological conditions due to aerosol radiative effects, an extra increase in  $\mathrm{PM}_{2.5}$  concentration is yielded. The mean daily  $\mathrm{PM}_{2.5}$  enhancement due to radiative effects from aerosols in VIIRS_G during November 1 to 7 2017 is  $16\mu \mathrm{g}\mathrm{m}^{-3}$ , and it is doubled  $(28\mu \mathrm{g}\mathrm{m}^{-3})$  during the first three-day under much heavier air pollution. The radiative effect on  $\mathrm{PM}_{2.5}$  concentration boost due to biomass burning emissions in VIIRS_G is a few times higher than that from GFED, which only triggers an extra of  $2.8\mu \mathrm{g}\mathrm{m}^{-3}\mathrm{PM}_{2.5}$  concentration increase during November 1 to 7 2017 and  $4\mu \mathrm{g}\mathrm{m}^{-3}$  during the

first three-day. The result further stresses the improved biomass burning emission inventory, particularly of identification of more small fires, plays a critical role in elucidating aerosol radiative effects on air quality.

Looking into the peak time of changes in  $\mathrm{PM}_{2.5}$  versus the meteorological parameters, time shift emerges such as DSSR and PBL height relative to  $\mathrm{PM}_{2.5}$ . To examine the possible reasons in detail, the diurnal cycle of  $\mathrm{PM}_{2.5}$  concentrations, averaged over the first three-day with the highest biomass burning intensity, DSSR (Fig. 7a), PBL height (Fig. 7b) and their changes due to aerosol radiative effects is displayed. The results reveal an interesting simultaneous governance of  $\mathrm{PM}_{2.5}$  concentrations and meteorological parameters on the aerosol radiative effects, meaning that this effect is not only related to  $\mathrm{PM}_{2.5}$  concentrations, but also constraint by the base value of meteorology. For instance, the peak time of changes in DSSR is much earlier than that of  $\mathrm{PM}_{2.5}$  concentrations, highly attributable to the characteristics of DSSR diurnal variations, which tends to become zero during night when  $\mathrm{PM}_{2.5}$  is usually very high (Fig. 7a, dashed gray vs. black and red lines). Similar phenomenon can be found for PBL height (Fig. 7b, dashed gray vs. black and red lines). The peak of  $\mathrm{PM}_{2.5}$  changes, governed by aerosol radiative

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/617fd39f-94a5-429e-8f61-b0abbcd11785/110623a9b50ea85102041a70017b6c11ed81522a916170962fb8c232ede6068f.jpg)

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/617fd39f-94a5-429e-8f61-b0abbcd11785/ab33bf31dcf96a6ed04ee40c0711a53c278de76f8f1a1ef0c6439948d7cb0b21.jpg)  
Fig. 7. a, mean diurnal cycle of simulated  $\mathrm{PM}_{2.5}$  concentrations, downward surface shortwave radiation based on case 5, as well as their changes due to aerosol radiative effects ((case 5 - case 6) - (case 1 - case 2)) over Heilongjiang (top black box in Fig. S1b) from November 1 to 3, 2017. b, the same as a, but the meteorological parameters were changed to PBL height.

effects, are also limited by reaction rate, and higher  $\mathrm{PM}_{2.5}$  concentrations period in general reflects a faster particle accumulation rate therein. In this regard, the peak of changes in  $\mathrm{PM}_{2.5}$  tend to be towards the  $\mathrm{PM}_{2.5}$  concentration peak time, not necessarily the same as, though should be close to, peak time of changes in meteorological parameters, i.e., around 3:00 p.m. in this case (dashed pink line in Fig. 7b).

In addition to the surface level, the vertical profile of changes in meteorological parameters due to aerosol direct radiative effects from November 1 to 7, 2017 is displayed in Fig. 8. The near-surface air temperature and wind speed generally decrease, with the maximum decrease of  $0.5\mathrm{K}$  and  $0.4\mathrm{ms}^{-1}$ , respectively, whereas they increase slightly at the top of PBL. The opposite pattern is clearly discernible for RH. Specifically, aerosol radiative effects increase RH near the ground, with the largest increase of  $1\%$ , and the maximum decrease in RH at the top of PBL is  $2\%$ . A repeated examination based on GFED emission inventory yields a very weak signal of radiative direct effects on either meteorology or the  $\mathrm{PM}_{2.5}$  concentrations in both surface and the upper altitudes. The comparison of aerosol radiative effects induced by GFED and VIIRS is synthesized in Fig. S3.

# 4. Conclusion and discussions

In this study, by utilizing an improved biomass burning emission inventory, the quantification of biomass burning on air quality in a typical air pollution prone region such as Northeast China is thoroughly investigated. The improved emission inventory substantially enhances the capability of the regional air quality model in reproducing the  $\mathrm{PM}_{2.5}$  concentrations particularly during biomass burning events. Given the important role of aerosol direct radiative effects in modulating the meteorological conditions as well as the subsequent governance on aerosol concentrations, numerical sensitivity experiments reveal that

the aerosols emitted by biomass burning strikingly steer the development of the PBL by changing meteorological conditions, which then subsequently induce the accumulation of  $\mathrm{PM}_{2.5}$  concentrations. The underlying message delivered in this study indicates an urgent need to re-evaluate how the previously missed biomass burning emissions, particularly of regions with strong agriculture burning, might affect the air quality at present as well as in future. Moreover, considering the potential underestimation in VIIRS, it is encouraged to continue to improve the biomass burning emission inventory, e.g., adding fire FRP data measured by other satellites (Fengyun 4 geostationary satellite and NOAA20 polar orbiting satellite) or fire burned area provided by satellite with high the spatial resolution (e.g. Sentinel-2A), so as to further enhance the capability of numerical models in assessing biomass burning induced air quality issues. In addition, the spatial resolution applied in this study is  $36\mathrm{km}$  by  $36\mathrm{km}$ , and a higher resolution is desired to potentially better quantify the impact of biomass burning on air quality in particular of burning with a strong intensity in a relatively small area.

# Credit author statement

Lijiao Chen: Formal analysis, Methodology, Writing - original draft. Yang Gao: Conceptualization, Methodology, Writing - review & editing. Mingchen Ma: Visualization. Lili Wang: Methodology, Writing - review & editing. Qinglu Wang: Formal analysis. Shuhui Guan: Visualization. Xiaohong Yao: Writing - review & editing. Huiwang Gao: Writing - review & editing.

# Declaration of competing interest

The authors declare that they have no known competing financial

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/617fd39f-94a5-429e-8f61-b0abbcd11785/dc33a376096b0f680c32d13c23d97ae60279de3697750251ab948348e21443ce.jpg)

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/617fd39f-94a5-429e-8f61-b0abbcd11785/416d97558543cdb789db63fc1e8e79dbb5c12a95131c406b4d55a7cd4911919b.jpg)

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/617fd39f-94a5-429e-8f61-b0abbcd11785/8a6bdaa45d48e3f64370c011d92f01236936761d0ceac43a234605b05614a587.jpg)  
Fig. 8. Vertical profile of simulated hourly air temperature, RH, and wind speed due to aerosol direct radiative effects ((case 5 - case 6) - (case 1 - case 2) in Table 1) averaged in the area with intensive biomass burning (i.e., top black box in Heilongjiang Province in Fig. S1b) from November 1 to 7, 2017. The black line indicates the altitude of PBL.

interests or personal relationships that could have appeared to influence the work reported in this paper.

# Data availability

Data will be made available on request.

# Acknowledgements

This research was supported by grants from the National Key R&D Program of China (2022YFE0106400), National Natural Science Foundation of China (41775162 and 42061130215), and Royal Society-Newton Advanced Fellowship (NAF\R1\201354).

# Appendix B. Supplementary data

Supplementary data to this article can be found online at https://doi.org/10.1016/j.envpol.2022.120835.

# Appendix A. Statistical parameters for evaluation model performance

The model performance evaluation criteria used in this study include MB, MFB, MFE, RMSE, GE and R, and the formulas are shown below. The MOD and OBS represent the corresponding values in model simulations and observations, respectively.

$$
M B = \frac {1}{N} \sum_ {i = 1} ^ {N} \left(M O D _ {i} - O B S _ {i}\right)
$$

$$
M F B = \frac {2}{N} \sum_ {i = 1} ^ {N} \left(\frac {\left(M O D _ {i} - O B S _ {i}\right)}{\left(M O D _ {i} + O B S _ {i}\right)} \times 100 \% \right.
$$

$$
\begin{array}{l} M F E = \frac {2}{N} \sum_ {i = 1} ^ {N} \frac {\left| M O D _ {i} - O B S _ {i} \right|}{\left(M O D _ {i} + O B S _ {i}\right)} \times 100 \% \\ R M S E = \sqrt {\frac {1}{N} \sum_ {i = 1} ^ {N} \left(M O D _ {i} - O B S _ {i}\right) ^ {2}} \\ G E = \frac {1}{N} \sum_ {i = 1} ^ {N} \left| M O D _ {i} - O B S _ {i} \right| \\ R = \frac {\sum_ {i = 1} ^ {N} \left[ \left(M O D _ {i} - \overline {{M O D}}\right) \times \left(O B S _ {i} - \overline {{O B S}}\right) \right]}{\sqrt {\sum_ {i = 1} ^ {N} \left[ \left(M O D _ {i} - \overline {{M O D}}\right) ^ {2} \times \sum_ {i = 1} ^ {N} \left(O B S _ {i} - \overline {{O B S}}\right) ^ {2} \right]}} \\ \end{array}
$$

# References

Akagi, S.K., Yokelson, R.J., Wiedinmyer, C., Alvarado, M.J., Reid, J.S., Karl, T., Crounse, J.D., Wennberg, P.O., 2011. Emission factors for open and domestic biomass burning for use in atmospheric models. Atmos. Chem. Phys. 11, 4039-4072.  
Andela, N., Kaiser, J.W., van der Werf, G.R., Wooster, M.J., 2015. New fire diurnal cycle characterizations to improve fire radiative energy assessments made from MODIS observations. Atmos. Chem. Phys. 15, 8831-8846.  
Andreae, M.O., Merlet, P., 2001. Emission of trace gases and aerosols from biomass burning. Global Biogeochem. Cycles 15, 955-966.  
Appel, K.W., et al., 2021. The Community Multiscale Air Quality (CMAQ) model versions 5.3 and 5.3.1: system updates and evaluation. Geosci. Model Dev. (GMD) 14, 2867-2897.  
Appel, K.W., Bhave, P.V., Gilliland, A.B., Sarwar, G., Roselle, S.J., 2008. Evaluation of the community multiscale air quality (CMAQ) model version 4.5: sensitivities impacting model performance; Part II - particulate matter. Atmos. Environ. 42, 6057-6066.  
Appel, K.W., et al., 2018. Overview and Evaluation of the Community Multiscale Air Quality (CMAQ) Modeling System Version 5.2. Air Pollution Modeling and its Application XXV. Springer International Publishing, Cham, pp. 69-73.  
Appel, K.W., et al., 2017. Description and evaluation of the community multiscale air quality (CMAQ) modeling system version 5.1. Geosci. Model Dev 10, 1703-1732.  
Ballesteros-Gonzalez, K., Sullivan, A.P., Morales-Betancourt, R., 2020. Estimating the air quality and health impacts of biomass burning in northern South America using a chemical transport model. Sci. Total Environ. 739, 139755.  
Bi, Y., Wang, Y., Gao, C., 2010. Straw resource quantity and its regional distribution in China. J. Agric. Mech. Res. 3, 1-7.  
Cao, F., et al., 2017. Chemical characteristics of dicarboxylic acids and related organic compounds in PM2.5 during biomass-burning and non-biomass-burning seasons at a rural site of Northeast China. Environ. Pollut. 231, 654-662.  
Cao, F., Zhang, S., Kawamura, K., Zhang, Y., 2016. Inorganic markers, carbonaceous components and stable carbon isotope from biomass burning aerosols in Northeast China. Sci. Total Environ. 572, 1244-1251.  
Chen, J., et al., 2017a. A review of biomass burning: emissions and impacts on air quality, health and climate in China. Sci. Total Environ. 579, 1000-1034.  
Chen, L., Zhu, J., Liao, H., Gao, Y., Qiu, Y., Zhang, M., Liu, Z., Li, N., Wang, Y., 2019a. Assessing the formation and evolution mechanisms of severe haze pollution in the Beijing-Tianjin-Hebei region using process analysis. Atmos. Chem. Phys. 19, 10845-10864.  
Chen, W., Li, J., Bao, Q., Gao, Z., Cheng, T., Yu, Y., 2019b. Evaluation of straw open burning prohibition effect on provincial air quality during october and november 2018 in Jilin province. Atmosphere 10, 375.  
Chen, W., Tong, D., Dan, M., Zhang, S., Zhang, X., Pan, Y., 2017b. Typical atmospheric haze during crop harvest season in northeastern China: a case in the Changchun region. J. Environ. Sci. 54, 101-113.  
Cheng, Y., Yu, Q., Liu, J., Zhu, S., Zhang, M., Zhang, H., Zheng, B., He, K., 2021. Model vs. observation discrepancy in aerosol characteristics during a half-year long campaign in Northeast China: the role of biomass burning. Environ. Pollut. 269, 116167.  
Cheng, Z., et al., 2014. Impact of biomass burning on haze pollution in the Yangtze River delta, China: a case study in summer 2011. Atmos. Chem. Phys. 14, 4573-4585.  
Cui, S., Song, Z., Zhang, L., Shen, Z., Hough, R., Zhang, Z., An, L., Fu, Q., Zhao, Y., Jia, Z., 2021. Spatial and temporal variations of open straw burning based on fire spots in northeast China from 2013 to 2017. Atmos. Environ. 244, 117962.  
Dentener, F., et al., 2006. Emissions of primary aerosol and precursor gases in the years 2000 and 1750 prescribed data-sets for AeroCom. Atmos. Chem. Phys. 6, 4321-4344.  
Emery, C., Tai, E., Yarwood, G., 2001. Enhanced Meteorological Modeling and Performance Evaluation for Two Texas Ozone Episodes. Prepared for the Texas Natural Resource Conservation Commission. ENVIRON International Corporation.

Emmons, L.K., et al., 2010. Description and evaluation of the model for ozone and related chemical tracers, version 4 (MOZART-4). Geosci. Model Dev. (GMD) 3, 43-67.  
Gao, J., Zhu, B., Xiao, H., Kang, H., Pan, C., Wang, D., Wang, H., 2018. Effects of black carbon and boundary layer interaction on surface ozone in Nanjing, China. Atmos. Chem. Phys. 18, 7081-7094.  
Gao, M., Carmichael, G.R., Wang, Y., Saide, P.E., Yu, M., Xin, J., Liu, Z., Wang, Z., 2016. Modeling study of the 2010 regional haze event in the North China Plain. Atmos. Chem. Phys. 16, 1673-1691.  
Gao, Y., et al., 2022. Impacts of biogenic emissions from urban landscapes on summer ozone an secondary organic aerosol formation in megacities. Sci. Total Environ. 814, 152654.  
Gao, Y., Zhang, M., Liu, Z., Wang, L., Wang, P., Xia, X., Tao, M., Zhu, L., 2015. Modeling the feedback between aerosol and meteorological variables in the atmospheric boundary layer during a severe fog-haze event over the North China Plain. Atmos. Chem. Phys. 15, 4279-4295.  
Guan, S., Wong, D.C., Gao, Y., Zhang, T., Pouliot, G., 2020. Impact of wildfire on particulate matter in the southeastern United States in November 2016. Sci. Total Environ. 724, 138354.  
Guenther, A.B., Jiang, X., Heald, C.L., Sakulyanontvittaya, T., Duhl, T., Emmons, L.K., Wang, X., 2012. The Model of Emissions of Gases and Aerosols from Nature version 2.1 (MEGAN2.1): an extended and updated framework for modeling biogenic emissions. Geosci. Model Dev. (GMD) 5, 1471-1492.  
Hawbaker, T.J., Radeloff, V.C., Syphard, A.D., Zhu, Z., Stewart, S.I., 2008. Detection rates of the MODIS active fire product in the United States. Remote Sens. Environ. 112, 2656-2664.  
Huang, X., et al., 2016. Effects of aerosol-radiation interaction on precipitation during biomass-burning season in East China. Atmos. Chem. Phys. 16, 10063-10082.  
Ke, H., Gong, S., He, J., Zhou, C., Zhang, L., Zhou, Y., 2020. Assessment of open biomass burning impacts on surface PM2.5 concentration. J. Appl. Meteor. Sci. 31, 105-116.  
Koppmann, R., Czapiewski, K., Reid, J., 2005. A review of biomass burning emissions, Part I: gaseous emissions of carbon monoxide, methane, volatile organic compounds, and nitrogen containing compounds. Atmos. Chem. Phys. Discuss. 5, 10455-10516.  
Li, R., Chen, W., Zhao, H., Wu, X., Zhang, M., Tong, D.Q., Xiu, A., 2020. Inventory of atmospheric pollutant emissions from burning of crop residues in China based on satellite-retrieved farmland data. Chin. Geogr. Sci. 30, 266-278.  
Li, Y., Liu, A., Han, H., Zhao, T., Zhang, X., Zhuang, B., Wang, T., Chen, H., Wu, Y., Li, M., 2019. Collective impacts of biomass burning and synoptic weather on surface PM2.5 and CO in Northeast China. Atmos. Environ. 213, 64-80.  
Lin, C., Zhao, C., Liu, X., Lin, N.H., Chen, W., 2014. Modelling of long-range transport of Southeast Asia biomass-burning aerosols to Taiwan and their radiative forcings over East Asia. Tellus Ser. B Chem. Phys. Meteorol. 66, 23733.  
Liu, T., Marlier, M.E., Karambelas, A., Jain, M., Singh, S., Singh, M.K., Gautam, R., DeFries, R.S., 2019. Missing emissions from post-monsoon agricultural fires in northwestern India: regional limitations of MODIS burned area and active fire products. Environ. Res. Commun. 1, 011007.  
Ma, M., et al., 2022. Development and assessment of a high-resolution biogenic emission inventory from urban green spaces in China. Environ. Sci. Technol. 56, 175-184.  
Ma, M., et al., 2019. Substantial ozone enhancement over the North China Plain from increased biogenic emissions due to heat waves and land cover in summer 2017. Atmos. Chem. Phys. 19, 12195-12207.  
Mehmood, K., et al., 2020. Relative effects of open biomass burning and open crop straw burning on haze formation over central and eastern China: modeling study driven by constrained emissions. Atmos. Chem. Phys. 20, 2419-2443.  
Mukherjee, T., Vinoj, V., Midya, S.K., Adhikary, B., 2020. Aerosol radiative impact on surface ozone during a heavy dust and biomass burning event over South Asia. Atmos. Environ. 223, 117201.  
Pimonsree, S., Vongruang, P., 2018. Impact of biomass burning and its control on particulate matter over a city in mainland Southeast Asia during a smog episode. Atmos. Environ. 195, 196-209.  
Punsompong, P., Pani, S.K., Wang, S.H., Bich Pham, T.T., 2021. Assessment of biomass-burning types and transport over Thailand and the associated health risks. Atmos. Environ. 247, 118176.

Pye, H.O.T., et al., 2017. On the implications of aerosol liquid water and phase separation for organic aerosol mass. Atmos. Chem. Phys. 17, 343-369.  
Qiu, X., Duan, L., Chai, F., Wang, S., Yu, Q., Wang, S., 2016. Deriving high-resolution emission inventory of open biomass burning in China based on satellite observations. Environ. Sci. Technol. 50, 11779-11786.  
Qiu, Y., Liao, H., Zhang, R., Hu, J., 2017. Simulated impacts of direct radiative effects of scattering and absorbing aerosols on surface layer aerosol concentrations in China during a heavily polluted event in February 2014. J. Geophys. Res. Atmos. 122, 5955-5975.  
Rahman, M.M., Begum, B.A., Hopke, P.K., Nahar, K., Thurston, G.D., 2020. Assessing the PM2.5 impact of biomass combustion in megacity Dhaka, Bangladesh. Environ. Pollut. 264, 114798.  
Randerson, J.T., et al., 2006. The impact of boreal forest fire on climate warming. Science 314, 1130-1132.  
Randerson, J.T., Van Der Werf, G.R., Giglio, L., Collatz, G.J., Kasibhatla, P.s., 2017. Global Fire Emissions Database, Version 4.1 (GFEDv4). ORNL Distributed Active Archive Center.  
Rojano, R., Arregoces, H., Frias, E.G., 2021. Changes in ambient particulate matter during the COVID-19 and associations with biomass burning and Sahara dust in northern Colombia. Heliyon 7, e08595.  
Ryu, S.Y., Kwon, B.G., Kim, Y.J., Kim, H.H., Chun, K.J., 2007. Characteristics of biomass burning aerosol and its impact on regional air quality in the summer of 2003 at Gwangju, Korea. Atmos. Res. 84, 362-373.  
Saha, S., et al., 2014. The NCEP climate Forecast system version 2. J. Clim. 27, 2185-2208.  
Schroeder, W., Oliva, P., Giglio, L., Csiszar, I.A., 2014. The New VIIRS  $375\mathrm{m}$  active fire detection data product: algorithm description and initial assessment. Remote Sens. Environ. 143, 85-96.  
Tao, J., Zhang, L., Engling, G., Zhang, R., Yang, Y., Cao, J., Zhu, C., Wang, Q., Luo, L., 2013. Chemical composition of PM2.5 in an urban environment in Chengdu, China: importance of springtime dust storms and biomass burning. Atmos. Res. 122, 270-283.  
Taylor, D., 2010. Biomass burning, humans and climate change in Southeast Asia. Biodivers. Conserv. 19, 1025-1042.  
Tosca, M.G., Randerson, J.T., Zender, C.S., 2013. Global impact of smoke aerosols from landscape fires on climate and the Hadley circulation. Atmos. Chem. Phys. 13, 5227-5241.  
Uranishi, K., Ikemori, F., Shimada, H., Kondo, A., Sugata, S., 2019. Impact of field biomass burning on local pollution and long-range transport of PM2.5 in Northeast Asia. Environ. Pollut. 244, 414-422.  
Vadrevu, K., Lasko, K., 2018. Intercomparison of MODIS AQUA and VIIRS I-band fires and emissions in an agricultural landscape-implications for air pollution research. Rem. Sens. 10, 978.  
van der Werf, G.R., et al., 2017. Global fire emissions estimates during 1997-2016. Earth Syst. Sci. Data 9, 697-720.  
Wang, J., Allen, D.J., Pickering, K.E., Li, Z., He, H., 2016. Impact of aerosol direct effect on East Asian air quality during the EAST-AIRE campaign. J. Geophys. Res. Atmos. 121, 6534-6554.

Wang, J., et al., 2014. Impact of aerosol-meteorology interactions on fine particle pollution during China's severe haze episode in January 2013. Environ. Res. Lett. 9, 094002.  
Wang, L., Jin, X., Wang, Q., Mao, H., Liu, Q., Weng, G., Wang, Y., 2020a. Spatial and temporal variability of open biomass burning in Northeast China from 2003 to 2017. Atmos. Oceanogr. Sci. Libr. 13, 240-247.  
Wang, Q., et al., 2020b. Emission characteristics of size distribution, chemical composition and light absorption of particles from field-scale crop residue burning in Northeast China. Sci. Total Environ. 710, 136304.  
Wong, D.C., Pleim, J., Mathur, R., Binkowski, F., Otte, T., Gilliam, R., Pouliot, G., Xiu, A., Young, J.O., Kang, D., 2012. WRF-CMAQ two-way coupled system with aerosol feedback: software development and preliminary results. Geosci. Model Dev. (GMD) 5, 299-312.  
Yan, F., Gao, Y., Ma, M., Liu, C., Ji, X., Zhao, F., Yao, X., Gao, H., 2021. Revealing the modulation of boundary conditions and governing processes on ozone formation over northern China in June 2017. Environ. Pollut. 272, 115999.  
Yang, G., Zhao, H., Tong, D., Xiu, A., Zhang, X., Gao, C., 2020. Impacts of post-harvest open biomass burning and burning ban policy on severe haze in the Northeastern China. Sci. Total Environ. 716, 136517.  
Yang, J., Huang, X., 2021. The  $30\mathrm{m}$  annual land cover dataset and its dynamics in China from 1990 to 2019. Earth Syst. Sci. Data 13, 3907-3925.  
Yao, J., Eyamie, J., Henderson, S.B., 2016. Evaluation of a spatially resolved forest fire smoke model for population-based epidemiologic exposure assessment. J. Expo. Sci. Environ. Epidemiol. 26, 233-240.  
Zeng, X., Gao, Y., Wang, Y., Ma, M., Zhang, J., Sheng, L., 2022. Characterizing the distinct modulation of future emissions on summer ozone concentrations between urban and rural areas over China. Sci. Total Environ. 820, 153324.  
Zhang, G., Gao, Y., Cai, W., Leung, L.R., Wang, S., Zhao, B., Wang, M., Shan, H., Yao, X., Gao, H., 2019. Seesaw haze pollution in North China modulated by the sub-seasonal variability of atmospheric circulation. Atmos. Chem. Phys. 19, 565-576.  
Zhang, J., et al., 2020a. Exploring wintertime regional haze in northeast China: role of coal and biomass burning. Atmos. Chem. Phys. 20, 5355-5372.  
Zhang, T., de Jong, M.C., Wooster, M.J., Xu, W., Wang, L., 2020b. Trends in eastern China agricultural fire emissions derived from a combination of geostationary (Himawari) and polar (VIIRS) orbiter fire radiative power products. Atmos. Chem. Phys. 20, 10687-10705.  
Zhang, T., Wooster, M.J., Green, D.C., Main, B., 2015. New field-based agricultural biomass burning trace gas, PM2.5, and black carbon emission ratios and factors measured in situ at crop residue fires in Eastern China. Atmos. Environ. 121, 22-34.  
Zhang, T., Wooster, M.J., Xu, W., 2017a. Approaches for synergistically exploiting VIIRS I- and M-Band data in regional active fire detection and FRP assessment: a demonstration with respect to agricultural residue burning in Eastern China. Remote Sens. Environ. 198, 407-424.  
Zhang, Z., Gao, J., Zhang, L., Wang, H., Tao, J., Qiu, X., Chai, F., Li, Y., Wang, S., 2017b. Observations of biomass burning tracers in PM2.5 at two megacities in North China during 2014 APEC summit. Atmos. Environ. 169, 54-64.  
Zong, Z., Wang, X., Tian, C., Chen, Y., Qu, L., Ji, L., Zhi, G., Li, J., Zhang, G., 2016. Source apportionment of PM2.5 at a regional background site in North China using PMF linked with radiocarbon analysis: insight into the contribution of biomass burning. Atmos. Chem. Phys. 16, 11249-11265.