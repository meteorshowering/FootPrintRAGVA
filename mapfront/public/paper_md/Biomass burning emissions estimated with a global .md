# Biomass burning emissions estimated with a global fire assimilation system based on observed fire radiative power

J. W. Kaiser<sup>1</sup>, A. Heil<sup>2</sup>, M. O. Andreae<sup>3</sup>, A. Benedetti<sup>4</sup>, N. Chubarova<sup>5</sup>, L. Jones<sup>1</sup>, J.-J. Morcette<sup>1</sup>, M. Razinger<sup>1</sup>, M. G. Schultz<sup>2</sup>, M. Suttie<sup>1</sup>, and G. R. van der Werf<sup>5</sup>

<sup>1</sup>European Centre for Medium-range Weather Forecasts, Reading, UK  
$^{2}$ Forschungszentrum Jülich, Jülich, Germany  
3Max Planck Institut für Chemie, Mainz, Germany  
$^{4}$ Moscow State University, Moscow, Russia  
$^{5}$ VU University, Amsterdam, The Netherlands

Correspondence to: J. W. Kaiser (j.kaiser@ecmwf.int)

Received: 1 July 2011 - Published in Biogeosciences Discuss.: 22 July 2011  
Revised: 9 December 2011 - Accepted: 12 January 2012 - Published: 27 January 2012

Abstract. The Global Fire Assimilation System (GFASv1.0) calculates biomass burning emissions by assimilating Fire Radiative Power (FRP) observations from the MODIS instruments onboard the Terra and Aqua satellites. It corrects for gaps in the observations, which are mostly due to cloud cover, and filters spurious FRP observations of volcanoes, gas flares and other industrial activity. The combustion rate is subsequently calculated with land cover-specific conversion factors. Emission factors for 40 gas-phase and aerosol trace species have been compiled from a literature survey. The corresponding daily emissions have been calculated on a global  $0.5^{\circ} \times 0.5^{\circ}$  grid from 2003 to the present. General consistency with the Global Fire Emission Database version 3.1 (GFED3.1) within its accuracy is achieved while maintaining the advantages of an FRP-based approach: GFASv1.0 makes use of the quantitative information on the combustion rate that is contained in the FRP observations, and it detects fires in real time at high spatial and temporal resolution. GFASv1.0 indicates omission errors in GFED3.1 due to undetected small fires. It also exhibits slightly longer fire seasons in South America and North Africa and a slightly shorter fire season in Southeast Asia. GFASv1.0 has already been used for atmospheric reactive gas simulations in an independent study, which found good agreement with atmospheric observations. We have performed simulations of the atmospheric aerosol distribution with and without the assimilation of MODIS aerosol optical depth (AOD). They indicate that the emissions of particulate matter need to be boosted by a factor of 2-4 to reproduce the global distribution of organic matter and black carbon. This discrepancy is also evident in the comparison of previously published top-down and bottom-up estimates. For the time being, a global en

hancement of the particulate matter emissions by 3.4 is recommended. Validation with independent AOD and  $\mathrm{PM}_{10}$  observations recorded during the Russian fires in summer 2010 show that the global Monitoring Atmospheric Composition and Change (MACC) aerosol model with GFASv1.0 aerosol emissions captures the smoke plume evolution well when organic matter and black carbon are enhanced by the recommended factor. In conjunction with the assimilation of MODIS AOD, the use of GFASv1.0 with enhanced emission factors quantitatively improves the forecast of the aerosol load near the surface sufficiently to allow air quality warnings with a lead time of up to four days.

# 1 Introduction

Biomass burning occurs in all vegetated terrestrial ecosystems. Humans ignite most fires in the tropics and subtropics. Lightning strikes are another important ignition mechanism, particularly in remote boreal regions. Fires contribute to the build-up of atmospheric carbon dioxide  $\mathrm{(CO_2)}$  through deforestation and peatland fires. There are indications that some areas are experiencing an increase in the fire frequency, which would also lead to a rise in atmospheric  $\mathrm{CO}_{2}$  (Westerling et al., 2006). Fires also emit other greenhouse gases and are a major source of aerosols, carbon monoxide (CO), oxides of nitrogen  $(\mathrm{NO}_{\mathrm{x}})$  and other reactive trace gases, impacting local and regional air quality. Overall, fires impact 8 out of 13 identified radiative forcing agents (Bowman et al., 2009). In addition, they can indirectly impact the fluxes of water and energy.

Because of the large spatial and temporal variability of biomass burning, emissions monitoring and forecasting must be based on satellite observations of the currently active fires (Kaiser et al., 2006). Several systems that monitor and forecast global and regional air quality and visibility include modules that calculate fire emissions from satellite-based observations of burnt area or hot spots (Freitas et al., 2005; Reid et al., 2009; Sofiev et al., 2009).

The European Union (EU) is funding the development and implementation of services for the Global Monitoring for Environment and Security (GMES) atmospheric monitoring service in the Monitoring Atmospheric Composition and Change (MACC) project. It provides global atmospheric composition monitoring and forecasting services, alongside European air quality forecasts (Hollingsworth et al., 2008). In order to provide accurate estimates of aerosol, reactive gas and greenhouse gas emission fluxes to the atmospheric systems, a global fire assimilation system (GFAS) based on satellite-based fire radiative power (FRP) products is being developed. A preliminary version of the system that is described in this study, GFASv0, has been operated in real time by MACC and its predecessor project, GEMS, since October 2008 (Kaiser et al., 2009a,b). Figure 1 shows an example product from the current system.

In this publication, we describe the global fire assimilation system GFASv1.0, present an update to the emission factor compilation by Andreae and Merlet (2001), and compare the resulting emissions to those of the GFED3.1 inventory (van der Werf et al., 2010). We also test the emissions of aerosols with the MACC aerosol assimilation system (Benedetti et al., 2009) and evaluate its performance during the Russian fires of July-August 2010.

# 2 Methodology

# 2.1 Fire observation product processing

# 2.1.1 Fire observation input

The Moderate Resolution Imaging Spectroradiometer (MODIS) instruments on the polar orbiting satellites Aqua and Terra observe the thermal radiation from biomass burning and other sources around  $3.9\mu \mathrm{m}$  and  $11\mu \mathrm{m}$  wavelength. NASA is producing the fire product MOD14 (Justice et al., 2002; Giglio, 2005), which contains a quantitative observation of the fire radiative power (FRP) in addition to the long established binary active fire flag. FRP has been quantitatively linked to the combustion rate (Wooster et al., 2005) and aerosol emission rate (Ichoku and Kaufman, 2005) of a fire.

Since thermal radiation cannot penetrate clouds, satellite observations of active fires are limited to cloud-free areas. The MODIS products also exclude observations over snow and ice cover and over water bodies. Furthermore, their sam

pling frequency is limited by the sun-synchronous orbit of the Terra and Aqua satellites.

MACC has acquired the products in real time from NOAA from June 2008 to February 2011 and from NASA from March 2011 onwards. Re-processed Collection 5 products have been downloaded from NASA for earlier dates.

# 2.1.2 Gridding and cloud correction

The FRP products generally represent the fires observed by the satellite in units of Watt for each satellite pixel. The global fire assimilation system (GFAS) aggregates all observations onto a global grid of  $0.5^{\circ}$  resolution. Finer grid resolutions are not yet produced because of the larger effort to process such data.

In the first processing step, the observed FRP  $F_{i}$ , the area  $A_{i}$  and the view zenith angle  $\theta_{i}$  are calculated for all satellite pixels  $i$  with valid observations of fire  $(F_{i} > 0)$  or no-fire  $(F_{i} = 0)$ . Satellite pixels without valid observations, mostly due to water, ice or cloud cover, are ignored. The total observed FRP and total satellite observed area in each global grid cell  $j$  can be expressed as

$$
<   F > _ {j} = \frac {\sum_ {i \in j} F _ {i} \cos^ {2} \left(\theta_ {i}\right)}{\sum_ {i \in j} \cos^ {2} \left(\theta_ {i}\right)} \tag {1}
$$

$$
<   A > _ {j} = \frac {\sum_ {i \in j} A _ {i} \cos^ {2} \left(\theta_ {i}\right)}{\sum_ {i \in j} \cos^ {2} \left(\theta_ {i}\right)}. \tag {2}
$$

These equations are weighted summations, where the weighting factor  $\cos^2 (\theta_i)$  partially compensates the bow-tie effect of the MODIS scan geometry. The weighting is discussed in more detail below. Using these quantities, the observed FRP areal density  $\varrho_{j}$  and fraction  $\gamma_{j}$  of satellite observed area in each global grid cell  $j$  are calculated as

$$
\begin{array}{l} \varrho_ {j} = \frac {<   F > _ {j}}{<   A > _ {j}} (3) \\ = \frac {\sum_ {i \in j} F _ {i} \cos^ {2} \left(\theta_ {i}\right)}{\sum_ {i \in j} A _ {i} \cos^ {2} \left(\theta_ {i}\right)} (4) \\ \end{array}
$$

$$
\gamma_ {j} = \frac {\sum_ {i \in j} A _ {i} \cos^ {2} \left(\theta_ {i}\right)}{a _ {j}} , \tag {5}
$$

where  $a_{j}$  denotes the area of the global grid cell  $j$ ,  $\gamma_{j} \in [0, \infty[$  and  $\varrho_{j} \in [0, \infty[$ . Grid cells without any valid observations have  $\gamma_{j} = 0$  and  $\varrho_{j} = 0$ , whereby they will not have any effect on the following calculations.

The approach implicitly assumes that the fire distribution in the observed part of each grid cell is representative for the entire grid cell. For partially cloudy grid cells, the assumption is valid whenever the interactions between fires and clouds are negligible. Thus partial cloud cover is automatically corrected for. The approach also treats water bodies and snow cover as if they could burn. The error introduced for water bodies is subsequently corrected with a land fraction mask, see Sect. 2.1.4. The error introduced in partly

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/63045b03-2181-4065-93f8-dc1f28fadaec/3370d7bf70bd235da1705b8ac808df7410795bbc8f1c69fd8274e9561697e8b5.jpg)  
Fig. 1. Daily average Fire Radiative Power (FRP) density  $\left[\mathrm{mW}\mathrm{m}^{-2}\right]$  analysis of GFASv1.0 for 4 June 2011, based on observations from the two MODIS instruments. Equidistant cylindrical projection,  $0.5^{\circ}$  resolution. Published at http://gmes-atmosphere.eu/fire on 5 June 2011.

snowy grid cells is neglected because there is generally very little biomass burning in such grid cells.

The particular geometry of the MODIS scan with increasing pixel areas towards the swath edges leads to a scan-to-scan overlap for off-nadir pixels. It increases with the viewing angle and is often called "bow-tie effect" Wolfe et al. (2002), Freeborn et al. (2010, Fig. 1b). This leads to oversampling of the off-nadir surface areas within each MODIS granule. When calculating the total FRP of a grid cell, the duplicate observations of an individual fire should be corrected for. In Eq. (4), it is automatically corrected for because the multiple observations of the nonburning areas are included in the summations in just the same way in which the multiple observations of burning areas are included. Therefore, the FRP density  $\varrho_{j}$  of is not affected by the scan-to-scan oversampling of the bow-tie effect.

The dependence on the viewing angle  $\theta_{i}$  is important in Eq. (5) because  $\gamma_{j}$  serves as weight when several MODIS overpasses of a grid cell are merged as described in Sect. 2.1.3. Without the factor  $\cos^2 (\theta_i)$ , the multiple observations of off-nadir areas would increase the corresponding  $\gamma_{j}$ , giving these observations more weight than those located closer to the sub-satellite track. We find that the factor  $\cos^2 (\theta_i)$  reduces  $\gamma_{j}$  to similar values across the MODIS scan. It thus gives the combined multiple observations near the swath edges the same weight as the single observations near the sub-satellite track. In this sense, it compensates the bow-tie effect that is shown in Freeborn et al. (2010, Fig. 8c). The factor does not compensate for the increase of the detec

tion threshold towards the swath edges shown in Freeborn et al. (2010, Fig. 8a, b).

In the presented dataset, the summations in Eqs. (1)-(5) have been done for each individual MODIS granule, which corresponds to time periods of five minutes. For such an individual granule, the viewing angle  $\theta_{i}$  is about constant within each  $0.5^{\circ}$  grid cell and the observed areal FRP density could consequently be calculated as

$$
\varrho_ {j} \approx \frac {\sum_ {i \in j} F _ {i}}{\sum_ {i \in j} A _ {i}} \tag {6}
$$

instead of Eq. (4). This formulation has been used in GFASv0 (Kaiser et al., 2009b,a). In GFASv1.0, the dependence on the viewing angle is implemented according to Eqs. (1)-(5) to allow for a processing configuration in which the summations cover another number of granules, even from both instruments, see Sect. 2.1.3. Furthermore, this formulation allows the consistent processing on a grid with coarser resolution, where  $\theta_{i}$  might vary considerably within one grid cell.

The MOD14 product contains all required quantities for the fire pixels and a bitmask that identifies the no-fire pixels. The pixels areas  $A_{i}$  are calculated following the polynomial approximation in Giglio (2005, Sect. 6.4.5). According to this approximation, the nadir pixel area is  $1.01\mathrm{km}^2$ , implying a slight oversampling. Therefore, the fraction of satellite observed area  $\gamma_{j}$  may be larger than unity. The pixel area rises to  $9.74\mathrm{km}^2$  at the swath edge. The geolocation and

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/63045b03-2181-4065-93f8-dc1f28fadaec/1d00b4d6a4f4dc1bf7db8b104c88cafcbcde5400d01bec8aef11a13407c22ab7.jpg)

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/63045b03-2181-4065-93f8-dc1f28fadaec/159898957ba3e78e81be19488d1355a3400c66f18eea3bc6c6faddfc94a78ed1.jpg)  
Fig. 2. Effective number of satellite observations of grid cells  $(\eta_j\tilde{\gamma}_j)$  by MODIS on Terra (top) and Aqua (bottom) on 4 June 2011, 00:00-24:00 UTC. Equidistant cylindrical projection,  $0.5^{\circ}$  resolution. (ECMWF experiment IDs fb15 and fb17)

view zenith angles  $\theta_{i}$  are calculated with a custom parameterisation from the granule corner coordinates.

# 2.1.3 Merging

In order to obtain a combined representation of several gridded satellite products, an estimate of the accuracies of the products in each of the grid cells is needed. The assumptions made when observation gaps occur arguably introduce the largest errors. Therefore, only the representativity error is considered here. Its standard deviation  $\varsigma_{j}$  is assumed to be inversely proportional to the square root of the weighted fraction of observed area:

$$
\varsigma_ {j} = \frac {b}{\sqrt {\gamma_ {j}}} \tag {7}
$$

$$
\varsigma_ {j} ^ {- 2} = b ^ {- 2} \gamma_ {j}, \tag {8}
$$

where  $b$  denotes the proportionality constant. Let an additional index  $k$  distinguish several different satellite products.

Then, these are merged using optimal interpolation as

$$
\begin{array}{l} \tilde {\varrho} _ {j} = \xi_ {j} ^ {2} \sum_ {k} \varsigma_ {j, k} ^ {- 2} \varrho_ {j, k} (9) \\ = \tilde {\gamma} _ {j} ^ {- 1} \sum_ {k} \gamma_ {j, k} \varrho_ {j, k} (10) \\ \end{array}
$$

$$
\begin{array}{l} \tilde {\varsigma} _ {j} ^ {- 2} = \sum_ {k} \varsigma_ {j, k} ^ {- 2} (11) \\ = b ^ {- 2} \tilde {\gamma} _ {j} (12) \\ \end{array}
$$

with  $\tilde{\gamma}_j\equiv \sum_k\gamma_{j,k}$  13

In the presented dataset, these equations are used to merge the observations in each MODIS granule, as represented in Eqs. (4)-(5), for each day (00:00-24:00 UTC). Since the dependence on the viewing angle in Eq. (5) compensates the multiple observations near the swath edge, the weighting in Eq. (10) depends on the number of MODIS overpasses and the cloud cover of each grid cell, but not on the grid cell's position in the swath of any of the MODIS overpasses.

The merging formalism accomplishes a combined representation of simultaneous observations with separate geographical coverage on the one hand, and a temporally averaged representation of repeated observations of any given geographical area on the other hand.  $\tilde{\gamma}_j$  may be interpreted as effective number of observations of the entire grid cell  $j$  and repeated observations will lead to  $\tilde{\gamma}_j\gg 1$ . For example, two observations of a cloud-free grid cell or five observations of a grid cell with  $60\%$  cloud cover will both entail the same  $\tilde{\gamma}_j\approx 2$ . The formalism will also be used in future versions of GFAS to merge coincident observations from geostationary satellite instruments with the MODIS observations.

Note that Eqs. (4), (5), (10), (12) and (13) constitute a consistent framework in which the distribution of the individual satellite pixels into the satellite products  $k$  does not influence the gridded representation of the merged observations. This becomes evident when Eqs. (4) and (5) are substituted into Eqs. (10) and (12):

$$
\tilde {\varrho} _ {j} = \frac {\sum_ {k} \sum_ {i _ {k} \in j} F _ {i _ {k}} \cos^ {2} \left(\theta_ {i _ {k}}\right)}{\sum_ {k} \sum_ {i _ {k} \in j} A _ {i _ {k}} \cos^ {2} \left(\theta_ {i _ {k}}\right)} \tag {14}
$$

$$
\tilde {\zeta} _ {j} ^ {- 2} = \frac {\sum_ {k} \sum_ {i _ {k} \in j} A _ {i _ {k}} \cos^ {2} \left(\theta_ {i _ {k}}\right)}{a _ {j}}, \tag {15}
$$

where  $i_k$  denotes pixel  $i$  of satellite product  $k$ , e.g. MODIS granule  $k$ . Each nested summation over satellite products  $k$  and their individual pixels  $i_k$  can be rearrange as a single summation over all satellite pixels of the satellite products. Consequently, these equations are equivalent to Eqs. (4) and (5) with extended summation ranges. Therefore, the merged GFAS products for any given day do not depend on the grouping of the satellite products during the gridding in Eqs. (4) and (5).

# 2.1.4 Static corrections

It is known a priori that water sub-grid cell areas cannot contain biomass burning. However, since water satellite pixels are excluded from the sums in Eqs. (3)-(5), the merged FRP density  $\tilde{\varrho}_j$  erroneously assumes for any sub-grid water area the same fire distribution as for the land area of the grid cell. This is corrected with the unit-less land fraction  $\eta_j$  of each grid cell  $j$ . Furthermore, observations that are known to contain spurious FRP signals due to infra-red emissions of volcanic eruptions, gas flares and other industrial activity are masked with a map  $\delta_j$  that contains vanishing values in these grid cells and unity elsewhere:

$$
\begin{array}{l} \tilde {\rho} _ {j} = \eta_ {j} \delta_ {j} \tilde {\varrho} _ {j} (16) \\ \tilde {\sigma} _ {j} ^ {- 2} = \eta_ {j} \delta_ {j} \xi_ {j} ^ {- 2} (17) \\ = b ^ {- 2} \tilde {\alpha} _ {j} (18) \\ \end{array}
$$

with  $\tilde{\alpha}_j\equiv \eta_j\delta_j\tilde{\gamma}_j$  (19)

where Eqs. (18)-(19) follow from Eq. (12).

The standard land sea mask of ECMWF's Integrated Forecasting System (IFS) is used for  $\eta_{j}$ .

The achieved global sampling is illustrated in Fig. 2, which shows the merged fractions  $\eta_{j}\tilde{\gamma}_{j}$  of satellite observed area of the two MODIS instruments for one 24-h interval. Each instrument performs typically 1-2 effective observations per day of any grid cell. Taking both instruments into account typically yields between 3 and 4 observations per day, from which a single daily emission rate is derived for use in the atmospheric models. We assume with Eq. (9) that the observations provide a sufficiently representative sampling of the diurnal cycle of the fires. With this assumption, the daily mean value of FRP is simply the mean of the FRP  $\geq 0$  observations. Thus any assumption on the diurnal fire cycle or duration of the observed fires is avoided. The inaccuracy introduced by assuming that the fire observations are representative would clearly be reduced by also taking geostationary fire observations into account, which is planned for future versions of GFAS. In any case, significant observation gaps due to persistent cloud cover remain.

The spurious FRP mask  $\delta_{j}$  removes all observations from  $57.0.5^{\circ}$  grid cells that were found to contain a strong signal from volcanic eruptions, gas flares and other industrial activity. For the identification, the MODIS FRP observations of 2003-2009 were gridded on a  $0.1^{\circ}$  grid, observations gaps were filled with a Kalman smoother based on the Kalman filter in Eq. (32), and the field was temporally integrated to yield a gridded map of the Fire Radiative Energy (FRE). The grid cells of the map were ranked by magnitude. Aerial imagery on Bing Maps (http://www.bing.com/maps/) was used to visually identify the source of the FRE signal in the top 80 grid cells.  $65\%$  of these were identified either as gas flaring signals or as other industrial signals (metallurgical or crude oil processing plants). The latter produce 80 PJ FRE, equivalent to  $0.3\%$  of the global total FRE. Another  $18\%$  are identified as volcanic signals (namely the active volcanoes Fuego, Kilauea, Klyuchevskaya Sopka, La Cumbre, Mount Etna, Nyamuragira, Nyiragongo, Pacaya, Piton de la Fournaise, Semeru, Shiveluch, Sierra Negra), making up in total 47 PJ. Finally, another  $18\%$  are identified as biomass burning signals, making up in total 22 PJ. Interestingly, fires in the peat swamp forests of Sumatra lead the ranking of fire events in terms of FRE. This is not caused by the intensity of one single observation, but due to persistent burning over longer time periods.

# 2.1.5 Daytime and night-time fire radiative energy

The data assimilation and emission calculation described below is based on daily merged observations from the two MODIS instruments. Additionally, the merged daytime and night-time observations are presented in Sect. 3. They are derived by calculating merged hourly observations, setting  $\tilde{\alpha}_j = 0$  for all grid cells with local time in the time intervals 21:00-09:00 and 09:00-21:00, respectively, and averaging

Table 1. List of days in the period January 2003 to April 2011 with suspicious data in the MODIS MOD14 products.  

<table><tr><td>26 Jan 2003</td><td>8 Mar 2006</td><td>7 Jul 2008</td><td>4 Apr 2009</td><td>15 Aug 2009</td><td>30 Jul 2010</td></tr><tr><td>14 Mar 2003</td><td>19 Nov 2006</td><td>22 Oct 2008</td><td>3 Mar 2009</td><td>3 Noc 2009</td><td>8 Feb 2011</td></tr><tr><td>2 Mar 2004</td><td>13 Dec 2007</td><td>30 Oct 2008</td><td>10 Mar 2009</td><td>25 Feb 2010</td><td></td></tr><tr><td>26 Dec 2004</td><td>16 Feb 2008</td><td>8 Dec 2008</td><td>5 Aug 2009</td><td>6 Jun 2010</td><td></td></tr></table>

all hourly observations in any 24-h period. The Fire Radiative Energy (FRE) is subsequently calculated by integrating the FRP over the respective time periods.

# 2.1.6 Quality control

Observation and processing errors in the input data can lead to large errors in the GFAS fire products. This became apparent in the evaluation of the preliminary GFASv0 data. Therefore, a simple observation quality procedure, which analyses the daily merged and corrected MODIS observations, has been implemented. When the FRP density  $\tilde{\rho}_j$  in any grid cell  $j$  of the regular  $0.5^{\circ}$  latitude-longitude grid is larger than  $20\mathrm{Wm}^{-2}$  or when the global mean of the field is larger than  $800\mu \mathrm{Wm}^{-2}$ , a suspicious quality flag is raised and no observations are used in the data assimilation described below. Typically, the extremely large values result from extreme FRP values throughout all pixels of a MODIS granule, which are judged to be erroneous. The flag is raised no more than two times per year for the re-processed MOD14 products, cf. Table 1, 2003–2007. The real time MOD14 products raise the quality flag six times in 2009 and less frequently since, which indicates improvements in the real time processing chain.

# 2.2 Fire data assimilation

Since the observations contain gaps, mostly due to cloud cover, obtaining the best discrete estimate  $\hat{\rho}_t$  for the true, continuous FRP density  $\rho(t)$  requires the use of additional information. We use data assimilation to obtain the additional information from earlier observations. The best estimate that can be made of the true state  $\rho_t$  at a specific time step  $t$ , given the measurements up to and including  $t$ , is given by a Kalman filter (Rodgers, 2000, p. 122-124).

Our system model of FRP density  $\rho_{t}$  at time step  $t$  assumes persistence from the previous time step  $t - 1$  and the observations yield FRP density  $\tilde{\rho}_{t}$  at the time step  $t$ . Thus the observation operator is a unity operator:

$$
\rho_ {t} = \rho_ {t - 1} + \epsilon_ {t} \tag {20}
$$

$$
\tilde {\rho} _ {t} = \rho_ {t} + \tilde {\epsilon} _ {t}, \tag {21}
$$

where  $\epsilon_{t}$  and  $\tilde{\epsilon}_{t}$  represent the variations in the true FRP density, which are not modelled, and the observation error, respectively. Let  $\sigma_{t}$  and  $\tilde{\sigma}_{t}$  denote the corresponding error standard deviations. The system model is a scalar random walk,

except for allowing a time-dependence in the standard deviation  $\sigma_{t}$  of the model error  $\epsilon_{t}$ . Then the model a priori prediction for time step  $t$  is

$$
\check {\rho} _ {t} = \hat {\rho} _ {t - 1} \tag {22}
$$

$$
\check {\sigma} _ {t} ^ {2} = \hat {\sigma} _ {t - 1} ^ {2} + \sigma_ {t} ^ {2} \tag {23}
$$

and optimal interpolation with the observation yields the assimilated "analysis" field

$$
\hat {\rho} _ {t} = \hat {\sigma} _ {t} ^ {2} \left(\check {\sigma} _ {t} ^ {- 2} \check {\rho} _ {t} + \tilde {\sigma} _ {t} ^ {- 2} \tilde {\rho} _ {t}\right) \tag {24}
$$

$$
= \hat {\sigma} _ {t} ^ {2} \left(\frac {\hat {\rho} _ {t - 1}}{\hat {\sigma} _ {t - 1} ^ {2} + \sigma_ {t} ^ {2}} + \frac {\tilde {\rho} _ {t}}{\tilde {\sigma} _ {t} ^ {2}}\right) \tag {25}
$$

$$
\begin{array}{l} \hat {\sigma} _ {t} ^ {- 2} = \check {\sigma} _ {t} ^ {- 2} + \tilde {\sigma} _ {t} ^ {- 2} (26) \\ = \frac {1}{\hat {\sigma} _ {t - 1} ^ {2} + \sigma_ {t} ^ {2}} + \frac {1}{\tilde {\sigma} _ {t} ^ {2}}. (27) \\ \end{array}
$$

Since the presented system implements a time step of one day, the diurnal cycle of fires does not contribute to the error term  $\epsilon_{t}$ . The day-to-day variability has to be accounted for, however. As little is known quantitatively about this term, and in the interest of implementing a globally stable system, we represent the FRP density uncertainty due to day-to-day variability by inflating the variance of the last available FRP density estimate threefold, i.e.  $\sigma_{t} = 3\hat{\sigma}_{t - 1}$ :

$$
\hat {\rho} _ {t} = \hat {\sigma} _ {t} ^ {2} \left(\frac {\hat {\rho} _ {t - 1}}{1 0 \hat {\sigma} _ {t - 1} ^ {2}} + \frac {\tilde {\rho} _ {t}}{\tilde {\sigma} _ {t} ^ {2}}\right) \tag {28}
$$

$$
\hat {\sigma} _ {t} ^ {- 2} = \frac {1}{1 0} \hat {\sigma} _ {t - 1} ^ {- 2} + \tilde {\sigma} _ {t} ^ {- 2}. \tag {29}
$$

For the first time step,  $t = 0$ , of the assimilation, we assume that no a priori information on the fire distribution is available.

$$
\hat {\sigma} _ {- 1} ^ {- 2} = 0. \tag {30}
$$

Thus the FRP density field is solely determined by the observations.

The Kalman filter can be formulated with the corrected weighted fraction  $\tilde{\alpha}_t$  of observed area instead of the variance  $\hat{\sigma}_t^2$  of the FRP density estimate  $\hat{\rho}_t$  by defining the quantitative confidence

$$
\hat {\alpha} _ {t} \equiv b ^ {2} \hat {\sigma} _ {t} ^ {- 2}, \tag {31}
$$

Table 2. Land cover classes  $l$  used in GFASv1.0 (Col. 1), their abbreviation in this manuscript (Col. 2), the associated conversion factor  ${\beta }_{l}\left\lbrack  {\mathrm{\;{kg}}\text{(dry matter)}{\mathrm{{MJ}}}^{-1}}\right\rbrack$  linking fire radiative power in GFASv1.0 and dry matter combustion rate in GFEDv3.1 (Col. 3), and fuel type used for species emission calculations in Eq. (36) (Col. 4).  ${\beta }_{l}$  is used in Eq. (35) to calculate the dry matter combustion rate estimate of GFASv1.0.  

<table><tr><td>land cover class</td><td>abbrev.</td><td>conv. factor</td><td>fuel type</td></tr><tr><td>savannah</td><td>SA</td><td>0.78</td><td>SA</td></tr><tr><td>savannah with organic soil</td><td>SAOS</td><td>0.26</td><td>SA</td></tr><tr><td>agriculture</td><td>AG</td><td>0.29</td><td>AG</td></tr><tr><td>agriculture with organic soil</td><td>AGOS</td><td>0.13</td><td>AG</td></tr><tr><td>tropical forest</td><td>TF</td><td>0.96</td><td>TF</td></tr><tr><td>peat</td><td>PEAT</td><td>5.87</td><td>PEAT</td></tr><tr><td>extratropical forest</td><td>EF</td><td>0.49</td><td>EF</td></tr><tr><td>extratropical forest with organic soil</td><td>EFOS</td><td>1.55</td><td>EF</td></tr></table>

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/63045b03-2181-4065-93f8-dc1f28fadaec/63302477f6c4efae39f7472bbcf855b7b58311c5b1ac8446e67a0cfd83d4c3ad.jpg)  
Fig. 3. Land cover class map based on dominant fire type in GFEDv3.1 and organic soil and peat maps. Gaps in land areas have been filled. Equidistant cylindrical projection,  $0.5^{\circ}$  resolution.

which is based on the weighted observed area fractions, and by using Eq. (18):

$$
\hat {\rho} _ {t} = \frac {1}{\hat {\alpha} _ {t}} \left(\frac {\hat {\alpha} _ {t - 1}}{1 0} \hat {\rho} _ {t - 1} + \tilde {\alpha} _ {t} \tilde {\rho} _ {t}\right) \tag {32}
$$

$$
\hat {\alpha} _ {t} = \frac {\hat {\alpha} _ {t - 1}}{1 0} + \tilde {\alpha} _ {t} \tag {33}
$$

$$
\hat {\alpha} _ {- 1} = 0. \tag {34}
$$

# 2.3 Combustion and species emission rates

Wooster et al. (2005) have proposed a universal conversion factor of  $0.368\mathrm{kgMJ^{-1}}$  that links the FRP to dry matter combustion rate. The conversion factor was calculated from ground-based experiments linking direct FRP observations of small-scale fires to their fuel consumption. Since the MODIS FRP observations miss some proportion of

small fires, and have no atmospheric correction implemented within them, the corresponding factor linking the GFAS FRP density to the true fuel consumption is expected to be higher. Consequently, the preliminary version of the MACC global fire assimilation system, GFASv0, was based on a universal conversion factor and its value that was chosen to be  $1.37\mathrm{kgMJ}^{-1}$  following a comparison to the global emission budgets of the GFED2 inventory (Kaiser et al., 2009a).

Heil et al. (2010, 2012) have analysed linear regressions between the FRP of GFASv1.0 from Eq. (32) and the dry matter combustion rate of GFEDv3.1. They find that the conversion factor linking GFAS FRP and GFED dry matter combustion rate depends on the land cover type and have determined conversion factor values  $\beta_{l}$  for eight land cover classes  $l$ . We assume that GFED describes the real fire activity sufficiently accurately to interpret the conversion factors  $\beta_{l}$  as link between the FRP of GFAS and the real dry matter combustion rate. The dry matter combustion rate  $f(\mathrm{DM})$  for each grid cell is thus calculated as

$$
f (\mathrm {D M}) = \sum_ {i = 1} ^ {8} \delta_ {i, l} \beta_ {i} \hat {\rho}, \tag {35}
$$

where  $l \in [1,8]$  denotes the land cover class of each grid cell and  $\delta$  is Kronecker's delta (e.g. Wüst, 2009, p. 370). The land cover classes are derived from the dominant burning land cover type in GFED3.1 and additional organic soil and peat maps, see Heil et al. (2012). The land cover classes and associated conversion factors are listed in Table 2, Col. 1-3, and the geographical land cover distribution is shown in Fig. 3.

It should be noted that systematic discrepancies between the GFED and GFAS dry matter combustion rate distributions and budgets may occur because the conversion factors  $\beta_{i}$  have been derived using a linear regression, as opposed to a simple scaling of budgets.

The emission rate densities  $f(s)$  [g(s) s $^{-1}$  m $^{-2}$ ] for 40 smoke constituents  $s$  are calculated with the emission factors  $\kappa(s)$  listed in Table 3 from the dry matter combustion rate density  $f(\mathrm{DM})$  as

$$
f (s) = \kappa (s) f (\mathrm {D M}), \tag {36}
$$

where the mapping of land cover classes into species emission classes listed in Table 2, Col. 4, is used to determine the applicable emission factor  $\kappa(s)$  in Table 3.

The combustion rate density expressed in terms of burning carbon  $\left[\mathrm{g}(\mathrm{C})\mathrm{s}^{-1}\mathrm{m}^{-2}\right]$  is finally calculated from the emission rate densities of the five dominant species, using the atomic masses of the involved elements:

$$
\begin{array}{l} f (\mathrm {C}) = \frac {1 2 \cdot f (\mathrm {C O} _ {2})}{1 2 + 2 \cdot 1 6} + \frac {1 2 \cdot f (\mathrm {C O})}{1 2 + 1 6} + \frac {1 2 \cdot f (\mathrm {C H} _ {4})}{1 2 + 4 \cdot 1} + \\ f (\mathrm {O C}) + f (\mathrm {B C}) \tag {37} \\ \end{array}
$$

Table 3. Emission factors [g(species)  ${\mathrm{{kg}}}^{-1}\left( \mathrm{{DM}}\right)$  ] for the different fuel types as defined in Table 2. Values are taken from Andreae and Merlet (2001) with updates from the literature through 2009, unless otherwise marked. The most recent updates, which will be included in the next version of GFAS, are given in bold font. Some values by Akagi et al. (2011) are given in italic font for comparison.  

<table><tr><td>Species</td><td>SA</td><td>TF</td><td>EF</td><td>AG</td><td>PEAT</td></tr><tr><td>CO2</td><td>1646</td><td>1626</td><td>1572</td><td>1308</td><td>1703g</td></tr><tr><td>CO</td><td>61</td><td>101</td><td>106</td><td>92</td><td>210g</td></tr><tr><td>CH4</td><td>2.2</td><td>6.6</td><td>4.8</td><td>8.4</td><td>20.8g</td></tr><tr><td>NMHC</td><td>3.4</td><td>7.0</td><td>5.7</td><td>9.9</td><td>12.1f</td></tr><tr><td>H2</td><td>0.98</td><td>3.5</td><td>1.8</td><td>2.7</td><td>3.5a</td></tr><tr><td>NOx</td><td>2.1</td><td>2.3</td><td>3.4</td><td>2.3</td><td>1.0g</td></tr><tr><td>N2O</td><td>0.21</td><td>0.24d</td><td>0.26</td><td>0.10</td><td>0.24a</td></tr><tr><td>PM2p5</td><td>4.9</td><td>9.1</td><td>13.8</td><td>8.3</td><td>9.1a</td></tr><tr><td></td><td>7.17</td><td>9.1</td><td>15.0</td><td>6.26-14.8</td><td></td></tr><tr><td>TPM</td><td>8.5</td><td>11.8</td><td>17.6</td><td>12.4</td><td>11.8a</td></tr><tr><td>TC</td><td>3.7</td><td>6.0</td><td>8.3</td><td>3.7c</td><td>6.1f</td></tr><tr><td></td><td></td><td></td><td></td><td>4.2</td><td></td></tr><tr><td>OC</td><td>3.2</td><td>4.3</td><td>9.1</td><td>4.2</td><td>6.0g</td></tr><tr><td></td><td>2.62</td><td>4.71</td><td>8.6-9.7</td><td>2.30-9.64</td><td>6.23</td></tr><tr><td>BC</td><td>0.46</td><td>0.57</td><td>0.56</td><td>0.42</td><td>0.04g</td></tr><tr><td></td><td>0.37</td><td>0.52</td><td>0.56</td><td>0.75-0.91</td><td>0.20</td></tr><tr><td>SO2</td><td>0.37</td><td>0.71</td><td>1.0</td><td>0.37c</td><td>0.71a</td></tr><tr><td>C2H6(Ethane)</td><td>0.32</td><td>1.1</td><td>0.72</td><td>1.2</td><td>1.1a</td></tr><tr><td>CH3OH (Methanol)</td><td>1.5</td><td>3.0</td><td>1.9</td><td>3.7</td><td>8.5g</td></tr><tr><td>C2H5OH (Ethanol)</td><td>0.018b</td><td>0.018b</td><td>0.018</td><td>0.018b</td><td>0.018a</td></tr><tr><td>C3H8 (Propane)</td><td>0.087</td><td>1.0</td><td>0.27</td><td>0.16</td><td>1.0a</td></tr><tr><td></td><td></td><td>0.54</td><td></td><td></td><td></td></tr><tr><td>C2H4(Ethylene)</td><td>0.84</td><td>1.5</td><td>1.2</td><td>1.3</td><td>2.6g</td></tr><tr><td>C3H6 (Propylene)</td><td>0.34</td><td>1.1</td><td>0.57</td><td>0.57</td><td>3.4g</td></tr><tr><td></td><td></td><td>0.76</td><td></td><td></td><td></td></tr><tr><td>C5H8 (Isoprene)</td><td>0.026</td><td>0.22</td><td>0.11</td><td>0.40</td><td>1.4g</td></tr><tr><td>Terpenes</td><td>0.014</td><td>0.12d</td><td>0.22</td><td>0.005</td><td>0.12a</td></tr><tr><td>Toluene lump</td><td>0.47</td><td>0.66</td><td>0.98</td><td>0.56</td><td>4.7f</td></tr><tr><td>Higher Alkenes</td><td>0.32</td><td>0.51</td><td>0.47</td><td>0.28</td><td>0.51a</td></tr><tr><td>Higher Alkanes</td><td>0.13</td><td>0.17</td><td>0.29</td><td>0.41</td><td>0.16a</td></tr><tr><td>CH2O (Formaldehyde)</td><td>0.71</td><td>2.2</td><td>2.2</td><td>2.1</td><td>1.4g</td></tr><tr><td></td><td>1.06</td><td></td><td></td><td></td><td></td></tr><tr><td>C2H4O (Acetaldehyde)</td><td>0.50</td><td>2.3</td><td>0.98</td><td>2.8</td><td>3.3g</td></tr><tr><td>C3H6O (Acetone)</td><td>0.48</td><td>0.63</td><td>0.67</td><td>1.1</td><td>1.5g</td></tr><tr><td>NH3</td><td>0.74</td><td>0.93</td><td>1.6</td><td>1.6</td><td>20g</td></tr><tr><td></td><td>0.90</td><td></td><td></td><td></td><td></td></tr><tr><td>C2H6S (DMS)</td><td>0.001</td><td>0.16</td><td>0.081e</td><td>0.001c</td><td>0.16a</td></tr><tr><td>C7H8 (Toluene)</td><td>0.18</td><td>0.24</td><td>0.40</td><td>0.18</td><td>1.6g</td></tr><tr><td>C6H6 (Benzene)</td><td>0.28</td><td>0.37</td><td>0.53</td><td>0.31</td><td>3.2g</td></tr><tr><td>C8H10 (Xylene)</td><td>0.015</td><td>0.043</td><td>0.049</td><td>0.067</td><td>0.043a</td></tr><tr><td></td><td>0.043</td><td>0.087</td><td>0.20</td><td>0.11</td><td></td></tr><tr><td>C4H8 (Butenes)</td><td>0.16</td><td>0.25</td><td>0.28</td><td>0.20</td><td>0.25a</td></tr><tr><td>C5H10 (Pentenes)</td><td>0.062</td><td>0.13</td><td>0.092</td><td>0.050</td><td>0.13a</td></tr><tr><td></td><td></td><td></td><td></td><td></td><td>0.02</td></tr><tr><td>C6H12 (Hexene)</td><td>0.090</td><td>0.11</td><td>0.094</td><td>0.028</td><td>0.11a</td></tr><tr><td>C8H16 (Octene)</td><td>0.006</td><td>0.012</td><td>0.005</td><td>0.003</td><td>0.012a</td></tr><tr><td>C4H10 (Butanes)</td><td>0.026</td><td>0.056</td><td>0.13</td><td>0.032</td><td>0.056a</td></tr><tr><td>C5H12 (Pentanes)</td><td>0.015</td><td>0.022</td><td>0.075</td><td>0.059</td><td>0.022a</td></tr><tr><td>C6H14 (Hexanes)</td><td>0.072</td><td>0.062</td><td>0.051</td><td>0.25</td><td>0.062a</td></tr><tr><td></td><td></td><td>0.12</td><td></td><td>0.07</td><td></td></tr><tr><td>C7H16) (Heptane)</td><td>0.020</td><td>0.026</td><td>0.032</td><td>0.070</td><td>0.026a</td></tr><tr><td></td><td></td><td>0.032</td><td></td><td></td><td></td></tr></table>

a Values from TF.  
b Values from EF.  
c Values from SA.  
d Values from mean of SA and EF.  
e Values from mean of SA and TF.  
f Values from sum of other species.  
g Values from Christian et al. (2003).

Table 4. Average global and regional combustion budgets  $\left\lbrack  {\mathrm{{Tg}}\left( \mathrm{C}\right) {\mathrm{a}}^{-1}}\right\rbrack$  during 2003-2008 in GFED3.1 and GFASv1.0.  

<table><tr><td>region</td><td>abbrev.</td><td>GFED</td><td>GFAS</td><td>latitudes [°N]</td><td>longitudes [°E]</td></tr><tr><td>Globe</td><td>global</td><td>1991</td><td>2117</td><td>-90–90</td><td>0–360</td></tr><tr><td>North America</td><td>NAme</td><td>76</td><td>102</td><td>30–75</td><td>190–330</td></tr><tr><td>Central America</td><td>CAme</td><td>43</td><td>67</td><td>0–30</td><td>190–330</td></tr><tr><td>South America</td><td>SAme</td><td>333</td><td>377</td><td>-60–0</td><td>190–330</td></tr><tr><td>Europe</td><td>Euro</td><td>17</td><td>33</td><td>30–75</td><td>330–60</td></tr><tr><td>North Africa</td><td>NHAf</td><td>461</td><td>430</td><td>0–30</td><td>330–60</td></tr><tr><td>South Africa</td><td>SHAf</td><td>574</td><td>517</td><td>-35–0</td><td>330–60</td></tr><tr><td>North Asia</td><td>NAsi</td><td>138</td><td>227</td><td>30–75</td><td>60–190</td></tr><tr><td>South Asia</td><td>SAsi</td><td>107</td><td>131</td><td>10–30</td><td>60–190</td></tr><tr><td>Tropical Asia</td><td>TAsi</td><td>119</td><td>97</td><td>-10–10</td><td>60–190</td></tr><tr><td>Australia</td><td>Aust</td><td>119</td><td>131</td><td>-50––10</td><td>60–190</td></tr><tr><td>East of Moscow</td><td>EoMo</td><td>3.3</td><td>5.4</td><td>50–60</td><td>35–55</td></tr></table>

# 2.4 Emission factors

The emission factors in Table 3 are based on a version of the compilation by Andreae and Merlet (2001), with additional information from a literature survey covering papers published from 2001 to 2009. This data is complemented by results from Christian et al. (2003) for peat fires, a category not covered by Andreae and Merlet (2001). The emission factor estimates were obtained by converting the available literature data, which had been reported in a variety of ways as emission factors or emission ratios to various species in the original publications, into a common format as emission factors, i.e. the mass of species emitted per mass of dry fuel combusted. Where necessary, appropriate assumptions regarding fuel carbon content, emission ratios of reference species to  $\mathrm{CO}_{2}$ , ratios of flaming to smouldering combustion, etc., were made. In cases where no published emission data exist, we extrapolated values based on available data from other emission classes by scaling the emission factors with appropriate reference species, usually CO. The accuracy of the emission factor estimates is highly variable, depending on the number and quality of original data that each value is based on. An indication of the variance of the emission values is given in Andreae and Merlet (2001), and it can be assumed that the values given are more accurate than those in Andreae and Merlet (2001) since they are based on a larger number of samples. A further updated version of the compilation by Andreae and Merlet (2001) is in preparation, and future versions of GFAS will be implemented using those values, as well as implementing spatial and temporal variability in emission factors following, e.g., van Leeuwen and van der Werf (2011).

# 3 Results

# 3.1 Regional fire radiative energy

Temporally integrating the corrected FRP density  $\tilde{\rho}$  from Eq. (16) yields the observed fire radiative energy density  $[\mathrm{Jm}^{-2}]$ . Subsequent spatial integration gives regional budgets of observed fire radiative energy [J]. Such budgets have been calculated separately for the daytime and night-time observations, cf. Sect. 2.1.5. They are shown in Fig. 4 for the months January 2003 to April 2011 and the regions defined in Table 4. The fire radiative energy budgets based on the quality-controlled and observation gap-filled best estimate  $\hat{\rho}_t$  of the FRP density, which is used for subsequent emission calculations, is also plotted.

The diurnal cycle of biomass burning leads to a clear separation of the observed energy release during daytime and night-time. It is particularly pronounced in regions with savannah fires that are extinguished during the night, e.g. in Africa, where our results are consistent with an earlier study by Roberts et al. (2009), which was based on FRP observations from SEVIRI aboard Meteosat-8. In regions with fire seasons that comprise large events burning for several days and nights, e.g. Europe and the boreal regions of America and Asia, an increase in the relative contribution of nighttime energy release is observed. Giglio (2007) has previously characterised the diurnal cycle of tropical fires with fire count observations from VIRS aboard TRMM and MODIS in great detail. While our study does not achieve the same temporal resolution, it provides global coverage and uses the quantitative information of the FRP observations.

The best estimates of the daily fire radiative energy approximately equals the sum of the observed daytime and night-time observations. This shows that the fires are relatively well observed and supports the assumption of sufficient representation of the diurnal variability of the fires in Eq. (9), cf. Sect. 2.1.4. Differences arise due to the following mechanisms:

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/63045b03-2181-4065-93f8-dc1f28fadaec/eb0c23345c130e595080536a82bb310be4a0e3095bd3c592d83c5b3b243b78df.jpg)

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/63045b03-2181-4065-93f8-dc1f28fadaec/cb75defad6da465bd47b3624051a16d3946e0ea344edafad41f0ac8d10b107e6.jpg)

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/63045b03-2181-4065-93f8-dc1f28fadaec/3f62ea0ad0b193aac2e1f74bdc07bdb385f4a4a129c69db6ee733f3bb8cce558.jpg)

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/63045b03-2181-4065-93f8-dc1f28fadaec/939ceda09a080e5a2cea87adebfe24c524e6486afe938f09ff26d30e94a6c51d.jpg)

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/63045b03-2181-4065-93f8-dc1f28fadaec/6d3557f836ac8f1c63917b47bbac44886faa343308ab7d02647e54f1718a6435.jpg)  
Fig. 4. Monthly fire radiative energy (FRE) observed by MODIS as used in GFASv1.0 for the entire globe and for several regions as defined in Table 4. Also shown is the subsequent FRE analysis ("24 h assimilation").

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/63045b03-2181-4065-93f8-dc1f28fadaec/3fb83e1ebeda9ae224d1c56d100babc0e871058ccb8862cca4d62d975c3b914b.jpg)

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/63045b03-2181-4065-93f8-dc1f28fadaec/a65b46bbaba569dfd233f6fe7d9400fec0436f10ea333ef718ebdfc4340f6a96.jpg)

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/63045b03-2181-4065-93f8-dc1f28fadaec/c65f282803411552939d2ebafe38dd07304342e497eee199a240de4a5fc3f5aa.jpg)

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/63045b03-2181-4065-93f8-dc1f28fadaec/1f3c11c447ee3299b56c437503ecfbcdf7a612b40171ce80f9239b0f4e959e9e.jpg)

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/63045b03-2181-4065-93f8-dc1f28fadaec/8127447e2d38cb357f6b9df51d0126f20b9cee7c5a2535113b3c3c1ebffe9f59.jpg)

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/63045b03-2181-4065-93f8-dc1f28fadaec/65b3da2d1eaebc734f4bd3c1315f4e01fd28404060de4f4c7c9899e8eae263bf.jpg)  
Fig. 4. Continued.

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/63045b03-2181-4065-93f8-dc1f28fadaec/a0ab4324ebc514177b132e76974975cbe68f90127c6940342991e11871b84716.jpg)

Table 5. Average annual emission [Tg] for the species defined in Table 3 in the regions defined in Table 4 from GFASv1.0 and GFED3.1. The GFED values are set in italics below the value for GFASv1.0 where available.  

<table><tr><td>Species</td><td>global</td><td>NAme</td><td>CAme</td><td>SAme</td><td>Euro</td><td>NHAf</td><td>SHAf</td><td>NAsi</td><td>SAsi</td><td>TAsi</td><td>Aust</td><td>EoMo</td></tr><tr><td rowspan="2">C</td><td>2068.8</td><td>98.4</td><td>66.5</td><td>348.9</td><td>33.1</td><td>425.5</td><td>514.4</td><td>215.7</td><td>131.8</td><td>102.9</td><td>130.1</td><td>5.6</td></tr><tr><td>1924.4</td><td>72.8</td><td>41.7</td><td>299.1</td><td>16.7</td><td>446.8</td><td>570.3</td><td>130.1</td><td>107.7</td><td>117.3</td><td>121.9</td><td>3.4</td></tr><tr><td rowspan="2">CO2</td><td>6906.7</td><td>321.7</td><td>222.0</td><td>1162.5</td><td>110.6</td><td>1449.1</td><td>1755.6</td><td>689.5</td><td>432.6</td><td>315.0</td><td>444.0</td><td>17.9</td></tr><tr><td>6508.3</td><td>241.2</td><td>141.0</td><td>1005.0</td><td>56.0</td><td>1531.9</td><td>1947.7</td><td>433.1</td><td>361.6</td><td>372.6</td><td>418.6</td><td>11.5</td></tr><tr><td rowspan="2">CO</td><td>351.520</td><td>19.492</td><td>11.424</td><td>60.903</td><td>5.579</td><td>58.413</td><td>68.859</td><td>50.942</td><td>26.224</td><td>32.096</td><td>17.432</td><td>1.271</td></tr><tr><td>331.115</td><td>15.727</td><td>7.338</td><td>55.068</td><td>3.048</td><td>64.829</td><td>87.192</td><td>26.711</td><td>20.019</td><td>33.710</td><td>17.473</td><td>0.646</td></tr><tr><td rowspan="2">CH4</td><td>19.042</td><td>0.877</td><td>0.634</td><td>3.460</td><td>0.343</td><td>2.439</td><td>2.721</td><td>3.257</td><td>1.687</td><td>2.951</td><td>0.666</td><td>0.108</td></tr><tr><td>17.555</td><td>0.722</td><td>0.410</td><td>3.195</td><td>0.215</td><td>2.861</td><td>3.990</td><td>1.340</td><td>1.207</td><td>2.915</td><td>0.699</td><td>0.051</td></tr><tr><td rowspan="2">NMHC</td><td>21.132</td><td>1.073</td><td>0.741</td><td>3.972</td><td>0.409</td><td>3.392</td><td>3.914</td><td>2.906</td><td>1.817</td><td>1.923</td><td>0.977</td><td>0.103</td></tr><tr><td>19.900</td><td>0.862</td><td>0.490</td><td>3.638</td><td>0.272</td><td>3.871</td><td>5.197</td><td>1.636</td><td>1.389</td><td>1.562</td><td>0.983</td><td>0.064</td></tr><tr><td rowspan="2">H2</td><td>7.565</td><td>0.331</td><td>0.314</td><td>1.759</td><td>0.115</td><td>1.125</td><td>1.226</td><td>0.875</td><td>0.878</td><td>0.653</td><td>0.287</td><td>0.029</td></tr><tr><td>7.405</td><td>0.272</td><td>0.191</td><td>1.594</td><td>0.077</td><td>1.295</td><td>1.836</td><td>0.499</td><td>0.580</td><td>0.759</td><td>0.303</td><td>0.018</td></tr><tr><td rowspan="2">NOx</td><td>9.529</td><td>0.632</td><td>0.308</td><td>1.589</td><td>0.159</td><td>1.891</td><td>2.293</td><td>1.179</td><td>0.607</td><td>0.272</td><td>0.594</td><td>0.025</td></tr><tr><td>9.431</td><td>0.505</td><td>0.203</td><td>1.428</td><td>0.084</td><td>2.058</td><td>2.700</td><td>0.837</td><td>0.517</td><td>0.517</td><td>0.582</td><td>0.017</td></tr><tr><td rowspan="2">N2O</td><td>0.948</td><td>0.050</td><td>0.031</td><td>0.162</td><td>0.013</td><td>0.191</td><td>0.230</td><td>0.105</td><td>0.062</td><td>0.045</td><td>0.058</td><td>0.002</td></tr><tr><td>0.847</td><td>0.039</td><td>0.018</td><td>0.127</td><td>0.006</td><td>0.195</td><td>0.252</td><td>0.064</td><td>0.045</td><td>0.045</td><td>0.055</td><td>0.001</td></tr><tr><td rowspan="2">PM2p5</td><td>29.734</td><td>2.250</td><td>1.012</td><td>5.359</td><td>0.467</td><td>4.800</td><td>5.646</td><td>4.667</td><td>2.362</td><td>1.695</td><td>1.465</td><td>0.092</td></tr><tr><td>29.438</td><td>1.876</td><td>0.669</td><td>4.994</td><td>0.274</td><td>5.517</td><td>7.695</td><td>3.013</td><td>1.813</td><td>2.044</td><td>1.543</td><td>0.056</td></tr><tr><td rowspan="2">TPM</td><td>44.570</td><td>3.167</td><td>1.456</td><td>7.600</td><td>0.737</td><td>7.874</td><td>9.421</td><td>6.486</td><td>3.138</td><td>2.222</td><td>2.447</td><td>0.137</td></tr><tr><td>43.645</td><td>2.589</td><td>0.968</td><td>6.982</td><td>0.412</td><td>8.822</td><td>11.914</td><td>4.235</td><td>2.545</td><td>2.696</td><td>2.483</td><td>0.085</td></tr><tr><td>TC</td><td>20.607</td><td>1.468</td><td>0.691</td><td>3.666</td><td>0.291</td><td>3.516</td><td>4.169</td><td>3.029</td><td>1.562</td><td>1.131</td><td>1.074</td><td>0.051</td></tr><tr><td rowspan="2">OC</td><td>18.157</td><td>1.582</td><td>0.553</td><td>2.836</td><td>0.282</td><td>2.960</td><td>3.575</td><td>3.235</td><td>1.154</td><td>1.016</td><td>0.957</td><td>0.052</td></tr><tr><td>17.652</td><td>1.323</td><td>0.378</td><td>2.682</td><td>0.146</td><td>3.391</td><td>4.715</td><td>2.047</td><td>0.964</td><td>0.999</td><td>1.008</td><td>0.028</td></tr><tr><td rowspan="2">BC</td><td>2.017</td><td>0.109</td><td>0.071</td><td>0.374</td><td>0.032</td><td>0.419</td><td>0.502</td><td>0.192</td><td>0.148</td><td>0.042</td><td>0.127</td><td>0.004</td></tr><tr><td>2.026</td><td>0.085</td><td>0.045</td><td>0.330</td><td>0.018</td><td>0.449</td><td>0.584</td><td>0.148</td><td>0.119</td><td>0.127</td><td>0.122</td><td>0.004</td></tr><tr><td rowspan="2">SO2</td><td>2.264</td><td>0.173</td><td>0.078</td><td>0.414</td><td>0.030</td><td>0.361</td><td>0.424</td><td>0.357</td><td>0.183</td><td>0.133</td><td>0.109</td><td>0.005</td></tr><tr><td>2.239</td><td>0.146</td><td>0.050</td><td>0.385</td><td>0.017</td><td>0.415</td><td>0.585</td><td>0.227</td><td>0.137</td><td>0.159</td><td>0.117</td><td>0.003</td></tr><tr><td>C2H6</td><td>2.540</td><td>0.130</td><td>0.103</td><td>0.569</td><td>0.046</td><td>0.369</td><td>0.404</td><td>0.327</td><td>0.284</td><td>0.209</td><td>0.097</td><td>0.012</td></tr><tr><td>CH3OH</td><td>9.397</td><td>0.372</td><td>0.310</td><td>1.673</td><td>0.170</td><td>1.453</td><td>1.676</td><td>1.349</td><td>0.761</td><td>1.219</td><td>0.412</td><td>0.048</td></tr><tr><td>C2H5OH</td><td>0.075</td><td>0.004</td><td>0.002</td><td>0.013</td><td>0.001</td><td>0.016</td><td>0.019</td><td>0.008</td><td>0.005</td><td>0.003</td><td>0.005</td><td>0.000</td></tr><tr><td>C3H8</td><td>1.568</td><td>0.047</td><td>0.078</td><td>0.460</td><td>0.011</td><td>0.174</td><td>0.159</td><td>0.165</td><td>0.252</td><td>0.193</td><td>0.029</td><td>0.004</td></tr><tr><td>C2H4</td><td>4.713</td><td>0.226</td><td>0.161</td><td>0.869</td><td>0.076</td><td>0.808</td><td>0.945</td><td>0.602</td><td>0.381</td><td>0.409</td><td>0.235</td><td>0.017</td></tr><tr><td>C3H6</td><td>2.952</td><td>0.106</td><td>0.103</td><td>0.578</td><td>0.037</td><td>0.383</td><td>0.420</td><td>0.457</td><td>0.285</td><td>0.484</td><td>0.098</td><td>0.012</td></tr><tr><td>C5H8</td><td>0.627</td><td>0.019</td><td>0.018</td><td>0.100</td><td>0.013</td><td>0.043</td><td>0.041</td><td>0.147</td><td>0.055</td><td>0.181</td><td>0.009</td><td>0.006</td></tr><tr><td>Terpenes</td><td>0.283</td><td>0.035</td><td>0.010</td><td>0.057</td><td>0.002</td><td>0.024</td><td>0.025</td><td>0.071</td><td>0.030</td><td>0.022</td><td>0.007</td><td>0.000</td></tr><tr><td>Toluene l.</td><td>3.289</td><td>0.176</td><td>0.080</td><td>0.420</td><td>0.048</td><td>0.434</td><td>0.520</td><td>0.684</td><td>0.173</td><td>0.617</td><td>0.135</td><td>0.015</td></tr><tr><td>H. Alkenes</td><td>1.638</td><td>0.089</td><td>0.057</td><td>0.307</td><td>0.023</td><td>0.300</td><td>0.354</td><td>0.194</td><td>0.130</td><td>0.095</td><td>0.089</td><td>0.004</td></tr><tr><td>H. Alkanes</td><td>0.690</td><td>0.052</td><td>0.022</td><td>0.111</td><td>0.016</td><td>0.121</td><td>0.146</td><td>0.107</td><td>0.045</td><td>0.031</td><td>0.039</td><td>0.004</td></tr><tr><td>CH2O</td><td>5.368</td><td>0.375</td><td>0.212</td><td>1.155</td><td>0.088</td><td>0.784</td><td>0.875</td><td>0.780</td><td>0.564</td><td>0.315</td><td>0.219</td><td>0.020</td></tr><tr><td>C2H4O</td><td>4.724</td><td>0.185</td><td>0.196</td><td>1.098</td><td>0.091</td><td>0.623</td><td>0.656</td><td>0.610</td><td>0.569</td><td>0.543</td><td>0.151</td><td>0.027</td></tr><tr><td>C3H6O</td><td>2.523</td><td>0.130</td><td>0.079</td><td>0.410</td><td>0.051</td><td>0.443</td><td>0.528</td><td>0.354</td><td>0.169</td><td>0.224</td><td>0.135</td><td>0.012</td></tr><tr><td>NH3</td><td>7.691</td><td>0.293</td><td>0.122</td><td>0.623</td><td>0.119</td><td>0.673</td><td>0.810</td><td>2.107</td><td>0.254</td><td>2.474</td><td>0.214</td><td>0.056</td></tr><tr><td>C2H6S</td><td>0.229</td><td>0.013</td><td>0.011</td><td>0.068</td><td>0.001</td><td>0.017</td><td>0.013</td><td>0.035</td><td>0.039</td><td>0.030</td><td>0.002</td><td>0.000</td></tr><tr><td>C7H8</td><td>1.200</td><td>0.071</td><td>0.030</td><td>0.156</td><td>0.017</td><td>0.163</td><td>0.196</td><td>0.247</td><td>0.064</td><td>0.204</td><td>0.051</td><td>0.005</td></tr><tr><td>C6H6</td><td>1.982</td><td>0.096</td><td>0.046</td><td>0.241</td><td>0.028</td><td>0.255</td><td>0.306</td><td>0.422</td><td>0.098</td><td>0.411</td><td>0.079</td><td>0.010</td></tr><tr><td>C8H10</td><td>0.115</td><td>0.008</td><td>0.004</td><td>0.023</td><td>0.002</td><td>0.016</td><td>0.018</td><td>0.019</td><td>0.011</td><td>0.008</td><td>0.005</td><td>0.001</td></tr><tr><td>C4H8</td><td>0.842</td><td>0.052</td><td>0.029</td><td>0.152</td><td>0.013</td><td>0.151</td><td>0.179</td><td>0.110</td><td>0.064</td><td>0.046</td><td>0.046</td><td>0.002</td></tr><tr><td>C5H10</td><td>0.359</td><td>0.017</td><td>0.013</td><td>0.074</td><td>0.004</td><td>0.062</td><td>0.071</td><td>0.040</td><td>0.034</td><td>0.025</td><td>0.017</td><td>0.001</td></tr><tr><td>C6H12</td><td>0.406</td><td>0.019</td><td>0.014</td><td>0.074</td><td>0.005</td><td>0.081</td><td>0.097</td><td>0.041</td><td>0.030</td><td>0.021</td><td>0.024</td><td>0.001</td></tr><tr><td>C8H16</td><td>0.032</td><td>0.001</td><td>0.001</td><td>0.007</td><td>0.000</td><td>0.006</td><td>0.007</td><td>0.003</td><td>0.003</td><td>0.002</td><td>0.002</td><td>0.000</td></tr><tr><td>C4H10</td><td>0.194</td><td>0.021</td><td>0.006</td><td>0.032</td><td>0.002</td><td>0.026</td><td>0.031</td><td>0.041</td><td>0.015</td><td>0.010</td><td>0.009</td><td>0.000</td></tr><tr><td>C5H12</td><td>0.104</td><td>0.013</td><td>0.003</td><td>0.015</td><td>0.002</td><td>0.014</td><td>0.017</td><td>0.024</td><td>0.006</td><td>0.004</td><td>0.005</td><td>0.000</td></tr><tr><td>C6H14</td><td>0.294</td><td>0.012</td><td>0.009</td><td>0.047</td><td>0.009</td><td>0.063</td><td>0.076</td><td>0.028</td><td>0.018</td><td>0.012</td><td>0.020</td><td>0.002</td></tr><tr><td>C7H16</td><td>0.099</td><td>0.006</td><td>0.003</td><td>0.017</td><td>0.003</td><td>0.018</td><td>0.021</td><td>0.013</td><td>0.007</td><td>0.005</td><td>0.006</td><td>0.001</td></tr></table>

- Since the daily analysis fills in observation gaps, it is on average larger than the daily observation fields, which vanish in observation gaps. This effect is small due to relatively good observational coverage.  
- The analysis does not contain spurious observations that are flagged by the quality control. The most pronounced example is in December 2009, where the night-time observations in Euro, NAsi and EoMo contain extreme values.  
- The daytime and night-time observations contribute with different weights to the analysis, depending on how complete and frequent the individual observations have been. This effect is small for averages over large regions and long time periods, however.

# 3.2 Emissions

# 3.2.1 Budgets

The average global and regional emission budgets of the various species have been calculated for 2003-2008. They are listed in Table 4, together with the corresponding values of GFED3.1. The global budgets of the two inventories agree within  $12\%$  , with generally larger values in GFAS. The emission budgets of  $6907\mathrm{Tg}(\mathrm{CO}_2)\mathrm{a}^{-1}$  and  $18\mathrm{Tg(OC)a^{-1}}$  are  $6 \%$  and  $3 \%$  larger in GFAS than in GFED, respectively. On the other hand, these values are  $4 \%$  and  $24 \%$  lower than their counterparts for 2005-2009 in the biomass burning emission inventory FINNv1 (Wiedinmyer et al., 2011). The disagreement for OC, even at global level, gives an indication of the uncertainties in the knowledge of individual species emissions.

The regional budgets show much larger discrepancies between GFAS and GFED. GFAS detects less carbon emissions in Africa and tropical Asia and more everywhere else.

# 3.2.2 Geographical distribution

The geographical distribution of the average carbon combustion rate density calculated with Eq. (37) for the years 2003-2008 is shown in Fig. 5 along with the corresponding field from GFED3.1. The locations of the major biomass burning regions agree well in both maps. The grid cells with extreme emissions in Borneo and South America also agree.

GFAS has, however, many more grid cells with low intensity fires on all continents. The detection of small fires with burnt area observations is limited by the pixel resolution; when a fire burns less than half of one of the  $500\mathrm{m} \times 500\mathrm{m}$  MODIS SWIR grid cells that underly the GFED inventory it is not detected (Giglio et al., 2009). On the other hand, FRP observations require at least emission of  $4.5 - 40\mathrm{MW}$  of thermal radiation in order to be detected in the MODIS MIR channel, depending on their distance to the sub-satellite track (Freeborn et al., 2010). Figure 5 shows that there

are many grid cells with small combustion rate densities of  $1 - 10\mathrm{g(C)a^{-1}m^{-2}}$  in GFAS but vanishing combustion rate densities in GFED. The more quantitative analysis by Heil et al. (2012) confirms this and also shows that GFAS has fire emissions in virtually all GFED grid cells with fire emissions. Since the grid cells with small combustion rate densities in GFAS are not arbitrarily distributed they are thought to contain a real signal, which is missing in GFED. Consequently, the underlying MODIS FRP observations have a lower detection threshold than the MODIS burnt area observation product by Giglio et al. (2010), which is used in GFEDv3.1. Even though the effect appears globally, it is most pronounced in North America and Eastern Europe, where agricultural waste burning might play a role.

The regional budgets of the average carbon combustion rate are listed in Table 4, Cols. 3-4. The global carbon budget of GFAS is  $6\%$  higher in GFAS than in GFED even though the conversion factors  $\beta$  have been derived such that they reproduce the proportionality to the GFED dry matter combustion rate (Heil et al., 2012). This may be a consequence of forcing the regression line through zero, which allows the algorithm to increase the number of grid cells with small emissions. The combustion budgets are consequently larger in all regions but Africa and Tropical Asia.

The differences in Tropical Asia are linked to the large uncertainties that are intrinsic to any large-scale combustion rate estimation for peat fires, because the observations (FRP or burnt area) are necessarily restricted to the surface while the bulk of the combustion occurs underground.

# 3.2.3 Temporal evolution

The temporal evolutions of monthly regional combustion rates of GFED3.1 and GFASv1.0 are compared in Fig. 6. Since GFAS is only available since 2003 but produces data in real time, the time range includes periods with only GFED data (1997-2002) and with only GFAS data (2010-April 2011). The global annual cycle is less pronounced in GFAS than in GFED. This is partially due to a reduction in the emission peaks in Southern Africa. North and Central America exhibit at least some combustion throughout the year in GFAS while their combustion rates virtually vanish outside of the fire season in GFED.

The annual cycles of the major fire regions compare well in GFAS and GFED, with a couple of subtle differences: the fire seasons in South America and North Africa appear to consistently last longer and the one in South Asia seems to start later in GFAS.

The regional interannual variabilities of GFAS and GFED are compared in Fig. 7. Minima and maxima are generally consistently detected by GFAS and GFED. The interannual variability of GFAS appears to be smaller for North and South America, and South and Tropical Asia. Conversely, it appears somewhat larger for Europe, South Africa and Australia.

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/63045b03-2181-4065-93f8-dc1f28fadaec/3115fae0510026e69ceb9a9dd2fd0cf2d2a129ed46ed45b2c6f767477fd7dafa.jpg)

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/63045b03-2181-4065-93f8-dc1f28fadaec/87e3fa64b7497934dda7c5037a26ccbc91658dc4a9bf8bf26c55f33e2705a5e1.jpg)  
Fig. 5. Average distribution of carbon combustion  $\left[\mathrm{g}(\mathrm{C})\mathrm{a}^{-1}\mathrm{m}^{-2}\right]$  during 2003-2008 in GFED3.1 (top) and GFASv1.0 (bottom). Equidistant cylindrical projection,  $0.5^{\circ}$  resolution. (ECMWF experiment IDs fhhh and ffxr)

The positive bias of GFAS with respect to GFED discussed in Sect. 3.2.2 is consistent throughout 2003-2009 for Central America, Europe and North Asia and consistent except for one and two individual years for North and South America.

The particularly high combustion rates in South Asia for the years 2004 and 2007 are comparable, but the values of GFAS drop only about half as much in between.

Europe evidently experienced extremely high combustion rates in 2010 caused by the catastrophic forest and peat fires in the region east of Moscow, see Sect. 3.3.2.

# 3.3 Atmospheric aerosol simulations

The aerosol model and assimilation system with which the real time MACC aerosol analyses and forecasts are produced since July 2008 (Morcette et al., 2009; Benedetti et al., 2009) is being used to link the smoke emissions to atmospheric aerosol observations. Dust and sea salt are represented in three size bins each. Organic matter (OM) and black carbon are (BC) represented as two types (hydrophilic and hydrophobic) each. Another type represents sulphate

aerosols. The two types of OM and BC are differentiated because they have different physical properties; prominently, hydrophilic aerosols can grow depending on the humidity of the air. This leads to an increased optical depth and to increased deposition rate in more humid conditions. Hydrophobic aerosols are converted to their hydrophilic counterparts during ageing of the aerosols.

The system performs a data assimilation with all input data used by ECMWF's operational numerical weather prediction plus total aerosol optical depth (AOD) observations from the MODIS instruments. Every  $12\mathrm{h}$ , a forecast/hindcast is initialised from the analysis and run for several days. During the forecast/hindcast, persistence of the biomass burning as prescribed at the initial date is assumed.

We present results from runs covering 15 July-31 December 2010, with a 14-day spin-up period before. In some of the runs, all MODIS AOD products are withheld ("passive", "blacklisted"). Concerning aerosols, this is equivalent to a "model" run without aerosol assimilation. The run with MODIS AOD observations ("active") yields the aerosol "analysis" fields. Its total aerosol mass column and AOD are

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/63045b03-2181-4065-93f8-dc1f28fadaec/e6f27dc7d5dc791429c5ba11d9a7f4ce6a2898db7f8ba23398a33d970f91787e.jpg)

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/63045b03-2181-4065-93f8-dc1f28fadaec/a32ba2fc5411b3d3e53ab6b698b54132ecb6f18bee5e266c7259a473a1b303e4.jpg)

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/63045b03-2181-4065-93f8-dc1f28fadaec/ed708b85ca279cf0a19404bcfffbfabc8fb624e3b257516251af42f14ffd922b.jpg)

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/63045b03-2181-4065-93f8-dc1f28fadaec/6abf89b855063fe904c3ad317fdab37de01cd363fd236a62df23d6f1cdcebc6f.jpg)

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/63045b03-2181-4065-93f8-dc1f28fadaec/55ce194d5d7eb7578397e7b74c31bbd0ab3ad2ac71602b8153b0e935426abdc0.jpg)  
Fig. 6. Monthly carbon emissions in GFASv1.0 and GFED3.1 for the entire globe and several regions as defined in Table 4.

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/63045b03-2181-4065-93f8-dc1f28fadaec/167f8b6ea28433df8cb0964f26c8181afc69d25ec6799f53f028dcdf5fe211da.jpg)

strongly constrained by the assimilated AOD observations. The relative partitioning of the aerosols is, however, prescribed by the aerosol model through the transport processes, the aerosol microphysics, and emission and sink rates of the different aerosol species. Therefore, the analysis may be interpreted as continuous representation of the MODIS observations under the assumption that the partitioning of aerosol species in the model is realistic (Benedetti et al., 2009).

The aerosol modelling system uses the black carbon (BC) emissions directly, while converting organic carbon (OC) to

organic matter (OM) and  $\mathrm{SO}_2$  to sulphate, both with a scaling factor of 1.5. This value may be a conservative estimate.

# 3.3.1 Global comparison to analysis with MODIS AOD

In order to relate the biomass burning emissions to the MODIS AOD observations on a global scale, two runs with daily biomass burning emissions prescribed by GFASv1.0 have been performed: "model" and "analysis" with passive and active AOD assimilation, respectively.

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/63045b03-2181-4065-93f8-dc1f28fadaec/dff81b12099243a3005f94cbef9fa47088cf37a92244760ad6693a1d1a1215de.jpg)

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/63045b03-2181-4065-93f8-dc1f28fadaec/02ad258d57bd0ea45b79ca90edd4ae7a7a70e64749fe34d47c22923564aa9367.jpg)

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/63045b03-2181-4065-93f8-dc1f28fadaec/a0168282d76f33d890f153b40121192cd527ee3420f9013c118e02b08e708674.jpg)

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/63045b03-2181-4065-93f8-dc1f28fadaec/388bef1dce26fd70906cba6ca681798b4776bc14eb1e19499f3359af59c00d86.jpg)

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/63045b03-2181-4065-93f8-dc1f28fadaec/4c64f926d045352ea896c8f6bf108304b0c555b5d2b0040a3ac020b0b81b458d.jpg)  
Fig. 6. Continued.

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/63045b03-2181-4065-93f8-dc1f28fadaec/9381e88c929984e13dc098e53223f9963ebd8485dfdf28c11b51eb6a3ed37d2f.jpg)

Figure 8 shows the average distributions of the sum of the AODs from organic matter and black carbon  $(\mathrm{OM} + \mathrm{BC})$  in the analysis and model. The model represents well the spatial patterns of the analysis in the major biomass burning regions in southern hemispheric America and Africa. However, it is biased low on the entire globe.

The average AOD of  $\mathrm{OM} + \mathrm{BC}$  values for the globe and the five major biomass burning regions during the investigated time window are listed in Table 6. The model is biased low

in southern hemispheric America and Africa by factors of 4.1 and 3.0. These regions dominate the global average AOD of  $\mathrm{OM} + \mathrm{BC}$  and the model is biased low by a factor of 3.4 on a global average.

When enhancing the model OM and BC concentrations by the factor of 3.4, the global pattern of the AOD of  $\mathrm{OM} + \mathrm{BC}$  in the analysis is generally matched, see lowest panel in Fig. 8. However, a few systematic differences remain: the "enhanced model" generally has a slightly lower background

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/63045b03-2181-4065-93f8-dc1f28fadaec/cfc4d1513d91e6b77e96429d4e10b6a46a198fb6183a4a4f351cc4509e282bbe.jpg)

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/63045b03-2181-4065-93f8-dc1f28fadaec/b81e516529316ef164e4e6cd9fe469013c749aa323b29f7409c7cde1db1a7bd2.jpg)

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/63045b03-2181-4065-93f8-dc1f28fadaec/a84e758a3cd68bdbbbf5c47876e0b2385e4846ccc95c715641c6041407057093.jpg)

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/63045b03-2181-4065-93f8-dc1f28fadaec/9195d64e4a8822d13b739b3922826cbfb4d74b6563862aff97ab766463073491.jpg)

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/63045b03-2181-4065-93f8-dc1f28fadaec/fb497146ef927bfd2bb4542b806ae2b296e60edc45fd8622850fb2b132abe30b.jpg)  
Fig. 7. Annual carbon emissions in GFASv1.0 and GFED3.1 for the entire globe and several regions as defined in Table 4.

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/63045b03-2181-4065-93f8-dc1f28fadaec/8290b844ea6456b86f67332523da87988624af11bea934a43b82b7927d5a03bc.jpg)

and slightly more pronounced peaks than the analysis field. The values in boreal fire regions are much more pronounced in the enhanced model field than in the analysis. This may be attributed to an underestimation in the analyses, which partially aliases the observed total AOD signal into wrong aerosol species when the a priori information from the model has incorrect species partitioning. The underlying reason is that the observation of total AOD alone does not discriminate different aerosols types. Therefore, the assimilation always maintains the relative aerosol partitioning that is prescribed by the model.

The temporal evolution of the average  $\mathrm{OM} + \mathrm{BC}$  fields of the analysis, model, and enhanced model is shown for the globe and the five major biomass burning regions in Fig. 9. It confirms that the day-to-day variability of the analysis is very well represented by the model and the annual cycle is reasonably well represented. In terms of absolute values, the enhanced model fits the analysis much better than the standard model. Nevertheless, significant second-order differences between model and analysis remain, minimising which will require a detailed multi-parameter fitting study. Pending the outcome of such a study, the enhanced model with OM

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/63045b03-2181-4065-93f8-dc1f28fadaec/e5da3c6b52cc5742fd5ba3fd4e5b9a11fc3d40fccfb354bfd78c7ade29061faa.jpg)

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/63045b03-2181-4065-93f8-dc1f28fadaec/070f861d745d60ea629d5f1f4bdaa827f726bed8918b1d5068430880d41b1d4b.jpg)

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/63045b03-2181-4065-93f8-dc1f28fadaec/dc3c5187f89029255e4b80d51892b6dccb37ac51f218e5e9ca968bfeaa104204.jpg)

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/63045b03-2181-4065-93f8-dc1f28fadaec/9b150b6aa6c663826e71343f5dc825f269989f029de2f627939cff5f681c3715.jpg)

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/63045b03-2181-4065-93f8-dc1f28fadaec/4879bc1f9d2d531910e38b0211c67b8d93b2a0f967839422b863c38a3fce2089.jpg)  
Fig. 7. Continued.

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/63045b03-2181-4065-93f8-dc1f28fadaec/49cc2a040ea9af02ff6426f288839e77c54279f8ce97c26a6866ec235ead5fd1.jpg)

and BC fields increased by a factor of 3.4 appears to give the best consistency with the analysis in biomass burning regions, and consequently the MODIS AOD observations. The accuracy of the enhanced model will be explored at the example of western Russia in Sect. 3.3.2 below.

The mean budget of  $\mathrm{OM} + \mathrm{BC}$  from Table 5 is  $29\mathrm{Tg}\mathrm{a}^{-1}$ . Applying the global enhancement factor of 3.4 to all emissions yields  $99\mathrm{Tg}\mathrm{a}^{-1}$ . This value is in reasonable agreement with other atmospheric aerosol forecasting systems that are validated against satellite observations of AOD: the FLAMBE program uses a smoke source function with a global average of  $110\mathrm{Tg}\mathrm{a}^{-1}$  in 2006-2008 (Reid et al.,

2009). Colarco (2011) find that enhancement factors of 1.8 (savannah and grasslands), 2.5 (tropical forest) and 4.5 (extra-tropical forest) are needed to raise the AOD in the NASA GEOS-5 aerosol forecasting system to the AOD values observed by MODIS. Sofiev et al. (2009) have derived empirical emission coefficients for smoke particulate matter valid in Europe using MODIS FRP and ground-based AOD and particulate matter concentration observations in conjunction with the SILAM air quality forecasting system. They conclude that  $35\mathrm{g}$  smoke aerosols are emitted per MJ FRP by forest fires and  $18\mathrm{gMJ}^{-1}$  by grassland and agricultural fires. This is even more than the enhanced values of  $24\mathrm{gMJ}^{-1}$  and

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/63045b03-2181-4065-93f8-dc1f28fadaec/1a78ccd0f76189265ba434db549cb6e125f1b0679adcdf108551257c142a216f.jpg)

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/63045b03-2181-4065-93f8-dc1f28fadaec/ac6849112ba9d15b9cc298a4c497a380bc4bf203ec2100f2768def78fab96db1.jpg)

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/63045b03-2181-4065-93f8-dc1f28fadaec/2c23d80c4aa5c88dd5a00240f94dc1478feb83735d3073c85da51576475bae8f.jpg)  
Fig. 8. Average distribution of the sum of the aerosol optical depths (AODs) at  $550\mathrm{nm}$  of black carbon and organic matter  $(\mathrm{OM} + \mathrm{BC})$  during 15 July-31 December 2010 in the analysis (top), the model (middle) and the model enhanced by a factor 3.4 (bottom). (ECMWF experiment IDs fi92 and fi93)

Table 6. Regional average sums of the aerosol optical depths at  $550\mathrm{nm}$  of black carbon and organic matter during 15 July-31 December 2010 in the analysis and the model. The ratio of the two values is also given.  

<table><tr><td>region</td><td>analysis</td><td>model</td><td>analysis/model</td></tr><tr><td>global</td><td>0.050</td><td>0.015</td><td>3.4</td></tr><tr><td>NAme</td><td>0.031</td><td>0.014</td><td>2.2</td></tr><tr><td>SAme</td><td>0.073</td><td>0.018</td><td>4.1</td></tr><tr><td>Euro</td><td>0.030</td><td>0.012</td><td>2.4</td></tr><tr><td>SHAf</td><td>0.129</td><td>0.043</td><td>3.0</td></tr><tr><td>NAsi</td><td>0.038</td><td>0.017</td><td>2.3</td></tr></table>

$14\mathrm{gMJ}^{-1}$  found in our study for extratropical forest and savannah, respectively.

Inversion studies have also found relatively large smoke emissions. By analysing the FRP and smoke plume AOD of individual fires that are observed by MODIS, Ichoku

and Kaufman (2005) find that the smoke emission in Western Russia is  $80 - 100\mathrm{gMJ}^{-1}$ , which is much larger than the values found by Sofiev et al. (2009) in the same region. For tropical forest and savannah, they find values of  $40 - 80\mathrm{gMJ}^{-1}$ , which is much larger than the value found in our study. Using a global aerosol source inversion, Huneeus et al. (2011) estimate the global emission of  $\mathrm{OM + BC}$  from both biomass burning and fossil fuel combustion to be  $134\mathrm{Tga^{-1}}$ . The contribution of biomass burning is  $96\mathrm{Tga^{-1}}$  (N. Huneeus, personal communication, 2011), which is in excellent agreement with the budget of  $99\mathrm{Tga^{-1}}$  proposed in this manuscript. Given that Ichoku and Kaufman (2005) consider that their values are "probably overestimated by  $50\%$  ", there is a reasonable agreement between the aerosol forecasting systems and the inversion studies.

# 3.3.2 Russian fires

The Russian fires of 2010 are used to further test the biomass burning emissions and the recommended enhancement factor in conjunction with the MACC aerosol monitoring and forecasting system. Four additional simulations have been performed, in which the biomass burning emissions of OC/OM and BC are enhanced by a factor of 3.4, following the findings of Sect. 3.3.1. One analysis and one model are based on an average monthly emission climatology derived from GFEDv2 (van der Werf et al., 2006). They are referred to below as "climatological". Another analysis and model are based on the daily GFASv1.0 emissions. They are referred to below as "NRT" since GFASv1.0 is available in near real time.

Following anomalously high temperatures, large wildfires devastated parts of Russia to the east of Moscow in July and August 2010. Because of the dry conditions, fires also burnt into the peat layer of the soil and emitted large quantities of smoke (e.g. Konovalov et al., 2011).

The daily fire radiative energy (FRE) observed by the MODIS instruments during local daytime and night-time over the region east of Moscow as defined in Table 4 is shown in Fig. 10. The fires built up during a 4-day time period starting on 23 July and abated during another 4-day period following 14 August. During the main burning event, the fires burnt with the same intensity throughout day and night, corresponding to a radiative energy release of  $1.0 - 1.5\mathrm{PJ}$  per day. This is a distinct characteristic of underground peat fires that are hardly influenced by the diurnal cycle of the atmosphere. The daily  $24\mathrm{h}$  FRE analysis of GFASv1.0 is also shown. As in Fig. 4, the  $24\mathrm{h}$  analysis is approximately the sum of the observed daytime and night-time data. However, in such daily data the corrections to this general behaviour introduced by the data assimilation become more evident than in the monthly data. Additionally, the quality control has removed the observations on 30 July and the assimilation consequently repeats the FRE value of the previous day, which

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/63045b03-2181-4065-93f8-dc1f28fadaec/71f6ff9574d0a13e75be18ed19b6824e0ad83ccda69ff89ebe73bc76cf67783a.jpg)

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/63045b03-2181-4065-93f8-dc1f28fadaec/f7660e2658b2bbb7faad7300136f740b2895747ae0908596215894c6686fc403.jpg)

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/63045b03-2181-4065-93f8-dc1f28fadaec/1552ecf288b7af51aeca97a76afac5588db11de8506f0c86261eaba604741f99.jpg)

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/63045b03-2181-4065-93f8-dc1f28fadaec/c75f4624fdf6d974247d8995c377b6ee273d4ed20d9d6cc5d247417b90ad5017.jpg)

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/63045b03-2181-4065-93f8-dc1f28fadaec/ea1d2fa35703d350a748377f65e77f5c10af5f8f53d6fc65d2b094a9033492ec.jpg)  
Date of year 2010

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/63045b03-2181-4065-93f8-dc1f28fadaec/9e99e7778f290bcb947152c2670256b169c5db63babc14512a1a38edd219741b.jpg)  
Date of year 2010  
Fig. 9. Daily sums of the average aerosol optical depths (AODs) at  $550\mathrm{nm}$  of black carbon and organic matter  $(\mathrm{OM} + \mathrm{BC})$  during 15 July-31 December 2010 in the analysis, the model and the model enhanced by a factor 3.4.

happens to be the maximum of the entire period with a very pronounced peak of 4.6 PJ.

The geographical distribution of the calculated carbon combustion rate is shown at the example of 4 August in Fig. 11. It shows that the most severe fires were located in five  $0.5^{\circ}$  grid cells with carbon combustion rates of more than  $50\mathrm{g}\mathrm{d}^{-1}\mathrm{m}^{-2}$ .

Figure 12 shows a comparison of the simulated AODs with independent, ground-based AOD observations at the Meteorological Observatory of Moscow State University (MSU MO), and in Zvenigorod, Minsk, Bucarest and Sevastopol during August 2010. The observations have been taken by CIMEL sun/sky photometers as part of AERONET world

wide network (Holben et al., 2001). In addition to the standard cloud-screening procedure a special cloud filter on the base of hourly cloud observations is used for Moscow data (Uliumdzhieva et al., 2005). Direct sun measurements are made with a  $1.2^{\circ}$  full field of view collimator at 340, 380, 440, 500, 675, 870, 940 and  $1020\mathrm{nm}$  every  $15\mathrm{min}$  during daytime. The direct sun measurements (excluding the  $940\mathrm{nm}$  channel, which is used to estimate the total water content) are used to compute the aerosol optical depth (AOD) and the Ångstrom exponent. The uncertainty of AOD measurements with level 2 processing does not exceed 0.01 in the visible range and 0.02 in the UV spectral range. We use level 2 data for Moscow, Minsk and Sevastopol and Bucarest,

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/63045b03-2181-4065-93f8-dc1f28fadaec/a7c37c0286d5e19b5974eb9faba7c8d3741d479aedcbe26fb0303fa1da28da00.jpg)  
Fig. 10. Daily FRE observed during daytime and night-time east of Moscow, along with assimilated FRE, for July and August 2010.

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/63045b03-2181-4065-93f8-dc1f28fadaec/9bab12d96dd0bf0615b484f1cd2f7344bffafe35ddd3080826e169b9743858a6.jpg)  
Fig. 11. GFASv1.0 combustion rate  $\left[\mathrm{g}(\mathrm{C})\mathrm{m}^{-2}\mathrm{d}^{-1}\right]$  on 4 August 2010.

which are available for download from the AERONET home page. The data from Zvenigorod have kindly been provided by Mikhail A. Sviridenkov. The presented period includes the first part of August with a dramatic increase in AOD due to fire smoke aerosol advection from forest and peat fires near Moscow and other regions of Central Russia. The maximum AOD observed in Moscow on 7 August reached a value of 4.6, which is the absolute maximum ever observed in this location. After relatively low AOD values on 11 and 12 August, another aerosol plume is observed starting from 13 August onwards. However, after the intensive rainfalls and change of atmospheric circulation, the AOD around Moscow dropped to 0.06 on 20 August. A very similar behaviour is observed in Zvenigorod, which is located at a distance of about  $55\mathrm{km}$  of Moscow State University. The observations in Minsk, Bucharest and Sevastopol document a distinct aerosol plume passing through around 17 August, albeit with much lower AOD values than in Moscow.

The  $\mathrm{D} + 0(3 - 24\mathrm{h})$  hindcasts depicted in the top row of Fig. 12 represent the monitoring capabilities of the different

simulation setups. The climatological model captures neither temporal evolution nor the magnitude of the smoke plumes at any of the five AERONET stations. This is expected because it is based on GFED2 fire emissions from earlier years. The climatological analysis uses additional information from the MODIS AOD observations. In Minsk, Bucharest and Sevastopol, where the smoke plume arrives after several days of transport – and observation by MODIS – the observed AOD is well represented despite the lack of adequate emission input. In Moscow and Zvenigorod, which are located closer to the fires, the climatological analysis captures the first smoke period, albeit with a negative bias. This shows that the assimilation of MODIS AOD was partially able to correct for the missing emissions. The fact that the climatological analysis misses the second smoke period highlights the limitations of an assimilation without accurate a priori information on the emissions.

The NRT model, which is based on the GFASv1.0 emissions enhanced by a factor 3.4, captures the timing of all elevated AOD episodes well. The AOD values are also mostly well reproduced, but with a clear overestimation during the second smoke period in Moscow and Zvenigorod and some underestimation in Bucarest and Sevastopol. The comparison clearly confirms the applicability of the enhancement factor of 3.4 for the usage of GFASv1.0 (and GFED) emissions in the global MACC aerosol system.

The NRT analysis is almost identical to the climatological analysis in Minsk, Bucharest and Sevastopol. This confirms that, far downwind of the fires, the total AOD in the MACC analyses are dominated by the assimilated MODIS AOD products rather than the modelled emission rates. This conclusion does not apply to the AOD of the individual species, though, because the relative partitioning of the aerosol species is prescribed by the model. Therefore, overly wrong emission rates lead to aliasing of the MODIS AOD signal into the wrong aerosol type; typically sulphate in the presented situation.

During the first smoke period in Moscow and Zvenigorod, the NRT analysis combines the information on high aerosol load from the GFASv1.0 emissions and the MODIS AOD product and yields the largest and most realistic AOD values. This is the ideal operation mode of the MACC system. During the second smoke period in Moscow and Zvenigorod, the NRT analysis is very close to the NRT model, and biased high. In this case the assimilation did not produce significant increments to modify the first guess provided by the model, presumably due to a lack of suitable AOD observations.

The  $\mathrm{D} + 3(75 - 96\mathrm{h})$  hindcasts depicted in the bottom row of Fig. 12 represent the forecasting capabilities of the different simulation setups. Since the fire emissions that are valid on the day of the initialising analysis,  $\mathrm{D} - 1$ , are persisted throughout the entire hindcast, the fire emissions are kept constant for an extended time period in these calculations. This persistence of the extreme fire activity observed on 29 July, cf. Fig. 10, is thought to lead to the extremely

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/63045b03-2181-4065-93f8-dc1f28fadaec/764e65d54568aaac09d78ac6603e054fdf618beb31876b450bd051ba5770ac41.jpg)

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/63045b03-2181-4065-93f8-dc1f28fadaec/8f877bac2466b502e9a94ce47385b3937e13b16e5b6b166c297151a2c5c6cbcf.jpg)

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/63045b03-2181-4065-93f8-dc1f28fadaec/44bba2033dc58969ac065dc1af73d3f9472ab8a1c06c2268e882fb24ba5385df.jpg)

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/63045b03-2181-4065-93f8-dc1f28fadaec/ad053e7eec86293e9e9e0145f87ca8dafe1985efa710d638fef2e5ea8205312a.jpg)

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/63045b03-2181-4065-93f8-dc1f28fadaec/8fce12f1ef9c2b453524f86f108237834ef963b17e81b24eb469c2a13505a19f.jpg)

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/63045b03-2181-4065-93f8-dc1f28fadaec/6fc343069875d200269dec5d1cb1082f66c708b24edc58503f625797518e4cc3.jpg)

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/63045b03-2181-4065-93f8-dc1f28fadaec/df2cbbff2e0f2b0336fdf2c98e5c7981d8db4806915c326a65b19857cc7fcf0f.jpg)  
Fig. 12. Simulated AOD at  $550\mu \mathrm{m}$  (lines) compared to AERONET AOD observations at  $500\mu \mathrm{m}$  (black symbols) for five locations affected by the Russian fires in August 2010. Hindcasts with lead times of  $3 - 24\mathrm{h}$ $(\mathrm{D} + 0$  top),  $27 - 48\mathrm{h}$ $(\mathrm{D} + 1,2^{nd}$  row),  $51 - 72\mathrm{h}$ $(\mathrm{D} + 2,3^{rd}$  row) and  $75 - 96\mathrm{h}$ $(\mathrm{D} + 3$  , bottom). Climatological analysis in blue (fj5a), NRT analysis in red (fj5b), climatological model in yellow (fj5c), NRT model in green (fj5d). (Zvenigorod: AERONET data courtesy Mikhail A. Sviridenkov. Others: AERONET level 2 data from http: //aeronet.gsfc.nasa.gov).

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/63045b03-2181-4065-93f8-dc1f28fadaec/309231e161601f0fa3834fdc7537a2d20a000d4b44ec81130f559238cda69c9c.jpg)

overestimated AOD hindcast for Moscow and Zvenigorod on 2 and 3 August. On the other hand, smoke from fires that ignite only during the hindcast period is necessarily missing from the hindcasts. This might be the reason for the failure to predict the plume over Bucharest on 16 and 17 August. Apart from these cases, the NRT model and analysis are predicting the periods of elevated AOD remarkably well. The climatological analysis is still able to predict the plumes of

Minsk and Sevastopol, but not those nearer the fires, i.e. in Moscow and Zvenigorod.

Generally, both analyses are closer to their corresponding models than in the case of the  $\mathrm{D} + 0$  hindcasts. This stresses the importance of accurate emission rates for the AOD forecasts, in addition to their importance for the relative aerosol partitioning.

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/63045b03-2181-4065-93f8-dc1f28fadaec/b4ab413c6c9519cc548f44c01aeb46e33324691b116b0908c23a6b90e8dbf7f1.jpg)

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/63045b03-2181-4065-93f8-dc1f28fadaec/f917768358f401f485322b8bf2e815eed4c33c2430f156d47859a9c17193dffc.jpg)

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/63045b03-2181-4065-93f8-dc1f28fadaec/d0c4604d5c92d8384b7c457c4b69d5370baa75b501296d2a16c2c714b1d70a1f.jpg)

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/63045b03-2181-4065-93f8-dc1f28fadaec/ce432306a38a4dd0f6a67b6519840006c3e6be783ca9a167804357c3d71f2f73.jpg)  
Fig. 12. Continued.

The time series of in-situ observations of  $\mathrm{PM}_{10}$  in Fig. 13 show that the air quality of Virolahti in Finland was affected by smoke around 8 August, which caused a transgression of the EU threshold of  $50\mu \mathrm{g}(\mathrm{PM}_{10})\mathrm{m}^{-3}$  for the 24-h average. The  $\mathrm{D} + 0$ ,  $\mathrm{D} + 1$ ,  $\mathrm{D} + 2$  and  $\mathrm{D} + 3$  hindcasts of the total aerosol concentration near the surface are compared to the in-situ observations. The climatological model shows some variability with a small amplitude and incorrect timing. The NRT model forecasts elevated aerosol concentrations with the correct timing within half a day for all lead times. It is, however, biased low by at least  $50\%$  in most cases. The anal

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/63045b03-2181-4065-93f8-dc1f28fadaec/344b387a399d8cf72fd64c2e18d2dea183d17c449974805ad845f2553cf23446.jpg)

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/63045b03-2181-4065-93f8-dc1f28fadaec/bb899e8658a704ac3988f550d6a20e4921cefe592ec21ca3a021e82836974374.jpg)

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/63045b03-2181-4065-93f8-dc1f28fadaec/3e43254cd186a1d8453d7e25d182bf9082f4900b0ce0a5a4026542a277522c16.jpg)

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/63045b03-2181-4065-93f8-dc1f28fadaec/71371fb28e3bc443b2bd592fc9519559c120386f19b1f7765decdb3600770769.jpg)

ysis agree relatively well with each other. This shows that they are strongly constrained by the MODIS AOD products. Their hindcasts with  $27 - 72\mathrm{h}$  lead time predict the timing and  $\mathrm{PM}_{10}$  load of the smoke plume well. The  $\mathrm{D} + 0$  hindcasts capture the maximum of the plume extremely well but miss the onset of the plume overpass, apparently due a misleading assimilation of the MODIS AOD products on 6 and 7 August. The  $\mathrm{D} + 3$  hindcasts by the two analysis simulations still give a reasonable indication of the timing and typical aerosol concentration of the plume.

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/63045b03-2181-4065-93f8-dc1f28fadaec/2b803f3df1db1ee2e2726e26afaa201f1e4158f70548e965546a906f0ff39a50.jpg)

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/63045b03-2181-4065-93f8-dc1f28fadaec/44981ad7aa176f510858531163dce52bbbe5b331d4d30a060f93fa79f577ffd7.jpg)

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/63045b03-2181-4065-93f8-dc1f28fadaec/83dd3b26d356347e9e4d071269ebf9c8d6f8be78e5f13685c960fa06c92b5732.jpg)

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/63045b03-2181-4065-93f8-dc1f28fadaec/bc95260fb2c57138f90333758d1fca278b66be28a947df90371407dae2e2e425.jpg)  
Fig. 12. Continued.

# 4 Conclusions

The Global Fire Assimilation System GFASv1.0 is calculating global biomass burning emission estimates for forty species from fire radiative power (FRP) observations by the MODIS instruments aboard the Terra and Aqua satellites. It achieves higher spatial and temporal resolutions than most inventories, and can estimate emissions in real time. Assumptions on the diurnal variability of fires are avoided by including observations of  $\mathrm{FRP} = 0$ . The effect of observation gaps due to partial cloud cover in the global grid cells is

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/63045b03-2181-4065-93f8-dc1f28fadaec/ad6c980dfb2775159baa77c78d4f67381325153fd460f098e4b71e010ccc9525.jpg)

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/63045b03-2181-4065-93f8-dc1f28fadaec/4acb7a1aef5c7438f65e9d18e2ff87a2f60b8c06bddd19ccadfd02991d7fc3f3.jpg)

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/63045b03-2181-4065-93f8-dc1f28fadaec/34705e9316d6390cf9c6dd602ecbff087265688bb4c3030a6df695ac038661ff.jpg)

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/63045b03-2181-4065-93f8-dc1f28fadaec/be11aaadb833c582971b34635324fc8bf621fdab3677367cbb27bd8e90b2559f.jpg)  
Fig. 13. In-situ observations of  $\mathrm{PM}_{10}$  and hindcasts of atmospheric aerosol concentrations  $[\mu \mathrm{g} \mathrm{m}^{-3}]$  near the surface in Virolahti, Finland for 4-11 August 2010. Hindcasts with lead times of  $3 - 24\mathrm{h}$ $(\mathrm{D} + 0)$ ,  $27 - 48\mathrm{h}$ $(\mathrm{D} + 1)$ ,  $51 - 72\mathrm{h}$ $(\mathrm{D} + 2)$  and  $75 - 96\mathrm{h}$ $(\mathrm{D} + 3)$ . Climatological analysis in blue (fj5a), NRT analysis in red (fj5b), climatological model in yellow (fj5c), NRT model in green (fj5d). (observations courtesy Finnish Meteorological Institute)

corrected by assuming the same FRP areal density throughout the grid cell. Observation gaps are further filled with a Kalman filter and a system model that assumes persistence of FRP. The strongest spurious FRP signals from volcanoes, gas flaring and industrial activity are masked, and

a quality control system filters out observations with suspiciously large observations over large areas.

GFASv1.0 makes use of the quantitative information in FRP by calculating the biomass combustion rate with landcover-specific conversion factors. The emission factor compilation by Andreae and Merlet (2001) has been updated. Species emission rates are calculated with emission factors for five land cover classes. The carbon (C) combustion/emission rate is calculated from the emission rates of  $\mathrm{CO}_{2}$ , CO,  $\mathrm{CH}_4$ , organic matter (OM) and black carbon (BC).

The FRP to dry matter combusted conversion factors derived by Heil et al. (2012) result in a distribution and magnitude of the C combustion rate of GFASv1.0 that is consistent with the GFED3.1 inventory within its accuracy. However, distinct differences exist, most notably more widespread biomass burning with low combustion rates. Some of the additional signal is spuriously caused by remaining gas flares, industrial activity and, possibly, occasional MODIS FRP values of doubtful quality. Nevertheless, the main effect is attributed to a lower detection threshold of the FRP-based approach than the approach based on burnt area.

Simulations of atmospheric aerosols using the global MACC system with and without MODIS AOD assimilation show that a model based on the GFASv1.0 emissions of OC and BC can be made consistent with the analysis, and consequently the MODIS AOD observations, when the AOD due to the OM and BC fields is enhanced by a factor of 3.4. Since all aerosol sink processes are linear, the average AOD of an aerosol species scales linearly with its source strength. Therefore, we recommend to correct the OM and BC emission estimates of GFASv1.0 with a factor of 3.4 when using them in the global MACC aerosol forecasting system. The recommendation would equally apply to GFED3.1 since its budgets are consistent with GFASv1.0.

The recommended enhancement of the aerosol emissions in the MACC systems is consistent with findings in recent major top-down emission estimates but inconsistent with bottom-up estimates. Under the assumption that the MODIS AOD observations are sufficiently accurate, the inconsistency between the two approaches can originate from errors in the biomass combustion estimates, inaccuracies in the emissions factors, an inadequate representation of aerosols and their source and sink processes in the models, or erroneous optical properties of smoke in the models.

The uncertainty related to the estimate of biomass combustion amounts can be tested using CO, since the CO budget is fairly well constrained. For example, Huijnen et al. (2011) validate atmospheric chemistry simulations of the western Russian fire episode of 2010 that use the GFASv1.0 emissions. They find good consistency with MOPITT CO and SCIAMACHY  $\mathrm{CH}_2\mathrm{O}$  observations. This indicates that the apparent low bias in the bottom-up emission inventories is specific to aerosols. It is therefore unlikely that the inconsistency is caused by a systematic inaccuracy in the biomass combustion estimates.

An underestimation of the mass extinction of smoke aerosols by a factor of 3.4 would lead to the observed discrepancy. The global MACC system uses OPAC (Hess et al., 1998) to calculate the optical properties of aerosols, accounting for hygroscopic growth. For example, the extinction coefficient of organic matter at  $555\mathrm{nm}$  wavelength varies between 3.2 and  $20\mathrm{m}^2\mathrm{g}^{-1}$  for relative humidities between  $0\%$  and  $95\%$ , with a value of  $4.9\mathrm{m}^2\mathrm{g}^{-1}$  at  $40\%$ . This is in reasonable agreement with the value of  $5.3\mathrm{m}^2\mathrm{g}^{-1}$  observed for  $545\mathrm{nm}$  wavelength by Chand et al. (2006) in smoke near the surface in air of  $40\%$  relative humidity. It is also consistent with the mass scattering coefficients of 3.5– $5.2\mathrm{m}^2\mathrm{g}^{-1}$  and absorption coefficients of  $0.21 - 0.57\mathrm{m}^2\mathrm{g}^{-1}$  retrieved from selected AERONET observations by Reid et al. (2005a). Furthermore, Sofiev et al. (2009) have obtained similar smoke aerosol emission coefficients to our recommendation by scaling against AOD and  $\mathrm{PM}_{10}$  observations, thus ensuring consistency between the physical and optical properties. The consistency assumption is further supported by the presented validation against independent  $\mathrm{PM}_{10}$  observations in Virolahti (Fig. 13). Finally, a 3.4-fold increase of extinction coefficient would be unphysical, given the well-determined size range of the particles.

The representation of smoke aerosols as OM  $(=1.5\times\mathrm{OC})$ , BC and sulphate  $(=1.5\times\mathrm{SO}_2)$  in the MACC model appears to be not entirely adequate in view of Table 3: for example, adding up the emission factors for OM, BC and sulphate for savannah yields  $5.8\mathrm{g}\mathrm{kg}^{-1}$  while the emission factor for total particulate matter is  $8.5\mathrm{g}\mathrm{kg}^{-1}$ . As a consequence, a scaling factor of 2.2 instead of 1.5 might be used for the calculation of the OM and sulphate emissions. Values around 2.2 for the OM/OC ratio have also been proposed for aged pollution and biomass burning aerosols by Turpin and Lim (2001), Pang et al. (2006) and Chen and Yu (2007). This would still leave an unexplained discrepancy by a factor of 2.3.

The similarity of the smoke outflow from Africa and South America into the South Atlantic in the analysis and the enhanced model in Fig. 8 is an indication that the aerosol sink processes are adequately implemented in the atmospheric model. Furthermore, it is unlikely – but possible – that all four atmospheric aerosol models (Morcette et al., 2009; Reid et al., 2009; Sofiev et al., 2009; Colarco, 2011) drastically overestimate the smoke aerosol sinks.

The aerosol emission factors appear to be well established: those compiled by Akagi et al. (2011), which are partially reproduced in Table 3, are within  $20\%$  of the values used in GFASv1.0. The extensive review of Janhäll et al. (2010) is also consistent. The emission ratio  $\mathrm{PM}_{2.5} / \mathrm{CO}$  can be even more robustly measured than the aerosol emission factor. Janhäll et al. (2010) show that it is  $0.09 \pm 0.04$  for all fires, which agrees excellently with the corresponding value of 0.084 derived from Table 3. However, there are also studies that find significantly larger values. Reid et al. (2005b) report average PM emission factors of 9 and  $34\mathrm{gkg}^{-1}$  (DM) for flaming and smouldering combustion, respectively, and point

out that the duration of the smouldering phase may be underestimated. Particularly large emission factors have been found by Patterson et al. (1986) with optical absorption measurements instead of the more widely used thermal oxidation techniques. A comparison of thermal and optical BC measurements reveals that thermal methods generally yield lower emission factors. There are indications for a systematic underestimate by thermal measurements (Martins et al., 1998). Chin et al. (2002) use emission factors of 2 and  $14\mathrm{gkg}^{-1}$  for BC and OC, respectively, based on Patterson et al. (1986) and Andreae et al. (1988). These values are within the range of the top-down estimates mentioned above.

The physical and chemical properties of smoke particles rapidly change with age. In addition to coagulation, there are various interactions with the gas-phase chemistry and clouds. Reid et al. (1998) observed in Brazil that biomass burning aerosol mass increases by about  $20\%$  to  $40\%$  during ageing over several hours to days. Reid et al. (2005b) find a volume median diameter of 0.25 to  $0.30\mu \mathrm{m}$  for freshly generated smoke particles and an increase by about  $0.05\mu \mathrm{m}$  during ageing into regional haze. This correspond to a mass increase of  $59\%$  to  $73\%$ . This might explain part of the discrepancy.

Up to now, the interaction of aerosols with the gas-phase chemistry are not included in the MACC aerosol model. However, developments in this direction are ongoing. They should contribute to closing the gap between the bottom-up emission estimates and the atmospheric aerosol representation.

Further investigations are required to resolve the discrepancy by a factor of 3.4 between the bottom-up and top-down aerosol emission estimates. To our knowledge no single aspect allows for such a large correction. However, an increase of  $43\%$  in the conversion rate of OC to OM can be justified and ageing has also been shown to increase the smoke aerosol mass by up to  $73\%$ . Applying these two corrections can thus reduce the unexplained discrepancy to a factor of only about 1.4. The individual contributions of OM and BC to the discrepancy still needs to be established.

Climate models that use fire emissions derived from the existing bottom-up inventories might experience an underestimation of the smoke AOD by a factor similar to the identified discrepancy between bottom-up and top-down aerosol fire emissions, i.e. about threefold. If this was the case, the climate forcing of biomass burning aerosols could potentially be severely misrepresented. We recommend to investigate whether it is occurring in current climate models and what the implications are.

The Russian fires of July and August 2010 were observed by the MODIS instruments with almost the same fire radiative power during daytime and night-time. This is a strong indication that the fires were predominantly peat fires, which is consistent with the land cover map from Heil et al. (2012). Four atmospheric aerosol simulations with enhanced aerosol emissions have been performed; two based on averaged historical fire emissions and the other two based on

daily GFASv1.0 emissions of 2010; two with and the other two without MODIS AOD assimilation. Comparisons to independent AOD and  $\mathrm{PM}_{10}$  observations show that the analysis and hindcasts with enhanced GFASv1.0 emissions and AOD assimilation are overall the most realistic and allow quantitative smoke plume forecasting with lead times of up to  $96\mathrm{h}$ . The accuracy of such multi-day forecasts is, however, intrinsically limited by the poor predictability of the evolution of wildfires. Thus even the occurrence of a plume may be wrongly predicted or not predicted at all in situations with extreme variability in the fire activity. At locations close to the wildfire, accurate estimation of the fire emissions is more important for the forecast accuracy than the AOD assimilation. After several days of transport, on the other hand, the AOD assimilation provides most of the AOD forecast accuracy. The fire emission estimates determine the aerosol partitioning of the forecast in all cases.

The daily global biomass burning emission estimates GFASv1.0 described in this manuscript are produced in real time with  $0.5^{\circ}$  resolution. The ongoing development focuses on improving the spatial and temporal resolutions, including geostationary FRP observations and predicting the evolution of the observed fires over several days. The GFASv1.0 emissions will be used in the next upgrade of the real time atmospheric monitoring and forecasting systems of MACC, using the recommended enhancement factor for the OM and BC emissions. All data are publicly available, see http:// gmes-atmosphere.eu/fire and http://macc.icg.kfa-juelich.de: 50080.

Acknowledgements. We thank Hugo Dernier van der Gon, Zig Klimont, Stefan Kinne for valuable discussions and Mikhail A. Sviridenkov for AERONET AOD observations from Zvenigorod. We thank NASA for providing the MODIS data, and the AERONET PIs and their staff for establishing and maintaining the sites in Minsk, Bucharest_Inoe and Sevastopol. This research was supported by the EU Seventh Research Framework Programme (MACC project, contract number 218793).

Edited by: D. Fernández Prieto

# References

Akagi, S. K., Yokelson, R. J., Wiedinmyer, C., Alvarado, M. J., Reid, J. S., Karl, T., Crounse, J. D., and Wennberg, P. O.: Emission factors for open and domestic biomass burning for use in atmospheric models, Atmos. Chem. Phys., 11, 4039-4072, doi:10.5194/acp-11-4039-2011, 2011.  
Andreae, M. O. and Merlet, P.: Emission of trace gases and aerosols from biomass burning, Global Biogeochem. Cy., 15, 955-966, 2001.  
Andreae, M. O., Browell, E. V., Garstang, M., Gregory, G. L., Harriss, R. C., Hill, G. F., Jacob, D. J., Pereira, M. C., Sachse, G. W., Setzer, A. W., Silva Dias, P. L., Talbot, R. W., Torres, A. L., and Wofsy, S. C.: Biomass-burning emissions and associated haze layers over Amazonia, J. Geophys. Res., 93, 1509-1527, 1988.

Benedetti, A., Morcette, J.-J., Boucher, O., Dethof, A., Engelen, R. J., Fisher, M., Flentje, H., Huneeus, N., Jones, L., Kaiser, J. W., Kinne, S., Mangold, A., Razinger, M., Simmons, A. J., and Suttie, M.: Aerosol analysis and forecast in the European Centre for Medium-Range Weather Forecasts Integrated Forecast System: 2. Data assimilation, J. Geophys. Res., 114, D13205, doi:10.1029/2008JD011115, 2009.  
Bowman, D. M. J. S., Balch, J. K., Artaxo, P., Bond, W. J., Carlson, J. M., Cochrane, M. A., D'Antonio, C. M., DeFries, R. S., Doyle, J. C., Harrison, S. P., Johnston, F. H., Keeley, J. E., Krawchuk, M. A., Kull, C. A., Marston, J. B., Moritz, M. A., Prentice, I. C., Roos, C. I., Scott, A. C., Swetnam, T. W., van der Werf, G. R., and Pyne, S. J.: Fire in the Earth System, Science, 324, 481-484, 2009.  
Chand, D., Guyon, P., Artaxo, P., Schmid, O., Frank, G. P., Rizzo, L. V., Mayol-Bracero, O. L., Gatti, L. V., and Andreae, M. O.: Optical and physical properties of aerosols in the bound ary layer and free troposphere over the Amazon Basin during the biomass burning season, Atmos. Chem. Phys., 6, 2911-2925, doi:10.5194/ACP-6-2911-2006, 2006.  
Chen, X. and Yu, J.: Measurement of organic mass to organic carbon ratio in ambient aerosol samples using a gravimetric technique in combination with chemical analysis, Atmos. Environ., 41, 8857-8864, 2007.  
Chin, M., Ginoux, P., Kinne, S., Torres, O., Holben, B. N., Duncan, B. N., Martin, R. V., Logan, J. A., Higurashi, A., and Nakajima, T.: Tropospheric aerosol optical thickness from the GOCART model and comparisons with satellite and Sun photometer measurements, J. Atmos. Sci., 59, 461-483, 2002.  
Christian, T. J., Kleiss, B., Yokelson, R. J., Holzinger, R., Crutzen, P. J., Hao, W. M., Saharjo, B. H., and Ward, D. E.: Comprehensive laboratory measurements of biomass-burning emissions: 1. Emissions from Indonesian, African, and other fuels, J. Geophys. Res, 108, 4719, doi:10.1029/2003JD003704, 2003.  
Colarco, P.: The NASA GEOS-5 Aerosol Forecasting System, in: MACC Conference, Driebergen, The Netherlands, 2011.  
Freeborn, P. H., Wooster, M. J., and Roberts, G.: Addressing the spatiotemporal sampling design of MODIS to provide estimates of the fire radiative energy emitted from Africa, Remote Sensing of Environment, 115, 475-498, 2010.  
Freitas, S. R., Longo, K. M., Silva Dias, M. A. F., Silva Dias, P. L., Chatfield, R., Prins, E., Artaxo, P., Grell, G. A., and Recuero, F. S.: Monitoring the transport of biomass burning emissions in South America, Environ. Fluid Mech., 5, 135-167, 2005.  
Giglio, L.: MODIS Collection 4 Active Fire Product User's Guide Version 2.3, Science Systems and Applications, Inc, 2005.  
Giglio, L.: Characterization of the tropical diurnal fire cycle using VIRS and MODIS observations, Remote Sens. Environ., 108, 407-421, 2007.  
Giglio, L., Loboda, T., Roy, D. P., Quayle, B., and Justice, C. O.: An active-fire based burned area mapping algorithm for the MODIS sensor, Rem. Sens. Environ., 113, 408-420, 2009.  
Giglio, L., Randerson, J. T., van der Werf, G. R., Kasibhatla, P. S., Collatz, G. J., Morton, D. C., and DeFries, R. S.: Assessing variability and long-term trends in burned area by merging multiple satellite fire products, Biogeosciences, 7, 1171-1186, doi:10.5194/bg-7-1171-2010, 2010.  
Heil, A., Kaiser, J. W., van der Werf, G. R., Wooster, M. J., Schultz, M. G., and Dernier van der Gon, H.: Assessment of the Real

Time Fire Emissions (GFASv0) by MACC, Tech. Memo. 628, ECMWF, Reading, UK, 2010.  
Heil, A., Kaiser, J. W., Schultz, M. G., van der Werf, G. R., and Wooster, M. J.: On the use of MODIS Fire Radiative Power for Global Fire Emission Estimation, Atmos. Chem. Pys. Discuss., in preparation, 2012.  
Hess, M., Koepke, P., and Schult, I.: Optical properties of aerosols and clouds: The software package OPAC, Bull. Amer. Meteor. Soc., 79, 831-844, 1998.  
Holben, B. N., Smirnov, A., Eck, T. F., Slutsker, I., Abuhassan, N., Newcomb, W. W., Schafer, J. S., Tanre, D., Chatenet, B., and Lavenu, F.: An emerging ground-based aerosol climatology: Aerosol optical depth from AERONET, J. Geophys. Res., 106, 12067-12097, 2001.  
Hollingsworth, A., Engelen, R. J., Textor, C., Benedetti, A., Boucher, O., Chevallier, F., Dethof, A., Elbern, H., Eskes, H., Flemming, J., Granier, C., Kaiser, J. W., Morcette, J.-J., Rayner, P., Peuch, V.-H., Rouil, L., Schultz, M. G., and Simmons, A. J.: Toward a Monitoring and Forecasting System For Atmospheric Composition: The GEMS Project, Bull. Am. Meteor. Soc., 89, 1147-1164, 2008.  
Huijnen, V., Flemming, J., Kaiser, J. W., Inness, A., Leito, J., Heil, A., Eskes, H. J., Schultz, M. G., Benedetti, A., Dufour, G., and Eremenko, M.: Hindcast experiments of tropospheric composition during the summer 2010 fires over Western Russia, Atmos. Chem. Phys. Discuss., 11, 31851-31909, doi:10.5194/acpd-11-31851-2011, 2011.  
Huneeus, N., Chevallier, F., and Boucher, O.: Estimating aerosol emissions by assimilating observed aerosol optical depth in a global aerosol model, Atmos. Chem. Phys. Discuss., in press, 2011.  
Ichoku, C. and Kaufman, Y. J.: A method to derive smoke emission rates from MODIS fire radiative energy measurements, IEEE TGRS, 43, 2636-2649, 2005.  
Janhäll, S., Andreae, M. O., and Pschl, U.: Biomass burning aerosol emissions from vegetation fires: particle number and mass emission factors and size distributions, Atmos. Chem. Phys., 10, 1427-1439, doi:10.5194/ACP-10-1427-2010, 2010.  
Justice, C. O., Giglio, L., Korontzi, S., Owens, J., Morisette, J. T., Roy, D., Descloitre, J., Alleaume, S., Petitcolin, F., and Kaufman, Y.: The MODIS fire products, RSE, 83, 244-262, 2002.  
Kaiser, J. W., Schultz, M. G., Gregoire, J. M., Textor, C., Sofiev, M., Bartholome, E., Leroy, M., Engelen, R. J., and Hollingsworth, A.: Observation Requirements for Global Biomass Burning Emission Monitoring, in: Proc. 2006 EUMETSAT Met. Sat. Conf., 2006.  
Kaiser, J. W., Flemming, J., Schultz, M. G., Suttie, M., and Wooster, M. J.: The MACC Global Fire Assimilation System: First Emission Products (GFASv0), Tech. Memo. 596, ECMWF, Reading, UK, 2009a.  
Kaiser, J. W., Suttie, M., Flemming, J., Morcrette, J.-J., Boucher, O., and Schultz, M. G.: Global Real-time Fire Emission Estimates Based on Space-borne Fire Radiative Power Observations, AIP Conf. Proc., 1100, 645-648, doi:10.1063/1.3117069, 2009b.  
Konovalov, I. B., Beekmann, M., Kuznetsova, I. N., Yurova, A., and Zvyagintsev, A. M.: Atmospheric impacts of the 2010 Russian wildfires: integrating modelling and measurements of an extreme air pollution episode in the Moscow region, Atmos. Chem. Phys., 11, 10031-10056, doi:10.5194/acp-11-10031-2011, 2011.

Martins, J. V., Artaxo, P., Lioussse, C., Reid, J. S., Hobbs, P. V., and Kaufman, Y. J.: Effects of black carbon content, particle size, and mixing on light absorption by aerosols from biomass burning in Brazil, J. Geophys. Res., 103, 32041-32050, 1998.  
Morcrette, J.-J., Boucher, O., Jones, L., Salmon, D., Bechtold, P., Beljaars, A., Benedetti, A., Bonet, A., Kaiser, J. W., Razinger, M., Schulz, M., Serrar, S., Simmons, A. J., Sofiev, M., Suttie, M., Tompkins, A. M., and Untch, A.: Aerosol analysis and forecast in the European Centre for Medium-Range Weather Forecasts Integrated Forecast System: Forward modeling, J. Geophys. Res., 114, D06206, doi:10.1029/2008JD011235, 2009.  
Pang, Y., Turpin, B., and Gundel, L.: On the importance of organic oxygen for understanding organic aerosol particles, Aerosol Sci. Tech., 40, 128-133, 2006.  
Patterson, E. M., McMahon, C. K., and Ward, D. E.: Absorption properties and graphitic carbon emission factors of forest fire aerosols, Geophys. Res. Lett., 13, 129-132, 1986.  
Reid, J. S., Hobbs, P. V., Ferek, R. J., Blake, D. R., Martins, J. V., Dunlap, M. R., and Lioussse, C.: Physical, chemical, and optical properties of regional hazes dominated by smoke in Brazil, J. Geophys. Res., 103, 32059-32080, 1998.  
Reid, J. S., Eck, T. F., Christopher, S. A., Koppmann, R., Dubovik, O., Eleuterio, D. P., Holben, B. N., Reid, E. A., and Zhang, J.: A review of biomass burning emissions part III: intensive optical properties of biomass burning particles, Atmos. Chem. Phys., 5, 827-849, doi:10.5194/ACP-5-827-2005, 2005a.  
Reid, J. S., Koppmann, R., Eck, T. F., and Eleuterio, D. P.: A review of biomass burning emissions part II: intensive physical properties of biomass burning particles, Atmos. Chem. Phys., 5, 799-825, doi:10.5194/ACP-5-799-2005, 2005b.  
Reid, J. S., Hyer, E. J., Prins, E. M., Westphal, D. L., Zhang, J., Wang, J., Christopher, S. A., Curtis, C. A., Schmidt, C. C., Eleuterio, D. P., Richardson, K. A., and Hoffman, J. P.: Global Monitoring and Forecasting of Biomass-Burning Smoke: Description of and Lessons from the Fore Location and Modeling of Buning Emissions (FLAMBE) Program, IEEE J. Selected Topics Appl. Earth Observations and Remote Sens., 2, 144-162, 2009.  
Roberts, G., Wooster, M. J., and Lagoudakis, E.: Annual and diurnal african biomass burning temporal dynamics, Biogeosciences, 6, 849-866, doi:10.5194/bg-6-849-2009, 2009.  
Rodgers, C. D.: Inverse methods for atmospheric sounding: Theory and practice, World Scientific Publishing, Singapore, 2000.  
Sofiev, M., Vankevich, R., Lotjonen, M., Prank, M., Petukhov, V., Ermakova, T., Koskinen, J., and Kukkonen, J.: An operational system for the assimilation of the satellite information on wildland fires for the needs of air quality modelling and forecasting, Atmos. Chem. Phys., 9, 6833-6847, doi:10.5194/ACP-9-6833-2009, 2009.

Turpin, B. J. and Lim, H.-J.: Species contributions to PM2.5 mass concentrations: Revisiting common assumptions for estimating organic mass, Aerosol Sci. Tech., 36, 602-610, 2001.  
Uliumdzhieva, N., Chubarova, N., and Smirnov, A.: Aerosol characteristics of the atmosphere over Moscow from Cimel sun photometer data, Russian Meteorology and Hydrology, 1, 37-44, 2005.  
van der Werf, G. R., Randerson, J. T., Giglio, L., Collatz, G. J., Kasibhatla, P. S., and Arellano Jr., A. F.: Interannual variability in global biomass burning emissions from 1997 to 2004, Atmos. Chem. Phys., 6, 3423-3441, doi:10.5194/ACP-6-3423-2006, 2006.  
van der Werf, G. R., Randerson, J. T., Giglio, L., Collatz, G. J., Mu, M., Kasibhatla, P. S., Morton, D. C., DeFries, R. S., Jin, Y., and van Leeuwen, T. T.: Global fire emissions and the contribution of deforestation, savanna, forest, agricultural, and peat fires (1997-2009), Atmos. Chem. Phys., 10, 11707-11735, doi:10.5194/ACP-10-11707-2010, 2010.  
van Leeuwen, T. T. and van der Werf, G. R.: Spatial and temporal variability in the ratio of trace gases emitted from biomass burning, Atmos. Chem. Phys., 11, 3611-3629, doi:10.5194/ACP-11-3611-2011, 2011.  
Westerling, A. L., Hidalgo, H. G., Cayan, D. R., and Swetnam, T. W.: Warming and earlier spring increase western US forest wildfire activity, Science, 313, 940-943, 2006.  
Wiedinmyer, C., Akagi, S. K., Yokelson, R. J., Emmons, L. K., Al-Saadi, J. A., Orlando, J. J., and Soja, A. J.: The Fire INventory from NCAR (FINN): a high resolution global model to estimate the emissions from open burning, Geosci. Model Dev., 4, 625-641, doi:10.5194/gmd-4-625-2011, 2011.  
Wolfe, R. E., Nishihama, M., Fleig, A. J., Kuyper, J. A., Roy, D. P., Storey, J. C., and Patt, F. S.: Achieving sub-pixel geolocation accuracy in support of MODIS land science, Remote Sens. Environ., 83, 31-49, 2002.  
Wooster, M. J., Roberts, G., Perry, G. L. W., and Kaufman, Y. J.: Retrieval of biomass combustion rates and totals from fire radiative power observations: FRP derivation and calibration relationships between biomass consumption and fire radiative energy release, J. Geophys. Res., 110, D24311, 2005.  
Wüst, R.: Mathematik für Physiker und Mathematiker, vol. 1: Reelle Analysis und Lineare Algebra, WILEY-VCH GmbH & Co. KGaA, 3. edn., 2009.