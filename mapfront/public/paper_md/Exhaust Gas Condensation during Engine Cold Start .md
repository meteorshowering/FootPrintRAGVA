Article

# Exhaust Gas Condensation during Engine Cold Start and Application of the Dry-Wet Correction Factor

Barouch Giechaskiel *, Alessandro A. Zardini and Michael Claiotte

European Commission—Joint Research Centre, Directorate for Energy, Transport and Climate, Sustainable Transport Unit, 21027 Ispra, Italy; alessandro.zardini@ec.europa.eu (A.A.Z.); michacl.clairotte@ec.europa.eu (M.C.)

* Correspondence: barouch.giechaskiel@ec.europa.eu; Tel.: +39-033-278-5312

Received: 10 May 2019; Accepted: 29 May 2019; Published: 31 May 2019

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/8d7771f5-0052-4ca6-b667-4b05f7740930/e999cf8732246ea9c0ce8bb2df5efe0ba7ebb04e8e84ee5438b8a1720c45c293.jpg)

check for updates

Featured Application: Dry-wet correction factors for diesel, gasoline, and CNG vehicles.

Abstract: Gas components, like carbon monoxide (CO) and dioxide  $(\mathrm{CO}_{2})$ , can be measured on a wet- or dry-basis depending on whether the water is left or removed from the sample before analysis. The dry concentrations of gaseous components in the exhaust from internal combustion engines are converted to wet concentrations with conversion factors based on the combustion products and the fuel properties. Recent  $\mathrm{CO}_{2}$  measurements with portable emissions measurement systems (PEMS) compared to laboratory grade equipment showed differences during the first minutes after engine start. In this study we compared instruments measuring on a dry- and wet-basis using different measuring principles (non-dispersive infrared detection (NDIR) and Fourier-transform infrared spectroscopy (FTIR)) at the exhaust of gasoline, compressed natural gas (CNG), and diesel light-duty and L-category vehicles. The results showed an underestimation of the  $\mathrm{CO}_{2}$  and CO mass emissions up to  $13\%$  at cold start when the conversion factor is applied and not direct "wet" measurements are taken, raising concerns about reported  $\mathrm{CO}_{2}$  and CO cold start emissions in some cases. The underestimation was negligible ( $< 1\%$ ) for  $\mathrm{CO}_{2}$  when the whole test  $(20 - 30\mathrm{min})$  was considered, but not for CO  $(1\% -10\%)$  underestimation) because the majority of emissions takes place at cold start. Exhaust gas temperature,  $\mathrm{H}_2\mathrm{O}$  measurements and different expressions of the dry-wet corrections confirmed that the differences are due to condensation at the exhaust pipes and aftertreatment devices when the surface temperatures are lower than the dew point of the exhaust gases. The results of this study help to interpret differences when comparing instruments with different principles of operation at the same location, instruments sampling at different locations, or the same instrument measuring different driving test cycles or at different ambient temperatures (e.g.,  $-7^{\circ}\mathrm{C}$ ).

Keywords: portable emissions measurement system (PEMS); worldwide harmonized light-duty vehicles test cycle (WLTC); real driving emissions (RDE); Fourier-transform infrared spectroscopy (FTIR); non-dispersive infrared detection (NDIR); gas analyzers; measurement uncertainty; engine cold start emissions; exhaust gas condensation; tailpipe  $\mathrm{CO}_{2}$  measurements

# 1. Introduction

Road transport is a significant source of air pollution in the European Union (EU) and vehicle emissions regulations try to limit the emission levels [1]. For instance, carbon dioxide  $(\mathrm{CO}_{2})$  is a greenhouse gas regulated by the EU with emission limits for vehicles [2]. Exceedance of these limits by the vehicle manufacturers are subject to fines.

The current regulations are traditionally based on measurements of diluted samples from bags filled from a dilution tunnel where the whole exhaust gas is diluted during roller bench tests. However,

direct measurements of the raw exhaust from the tailpipe are permitted in the EU and worldwide in the case of engine emission tests (e.g., heavy duty diesel engines and small utility gasoline engines) [3]. Moreover, direct tailpipe measurements are often conducted for research purposes [4].

Recently, on-road measurements with Portable Emissions Measurement Systems (PEMS) were introduced both in the heavy-duty [5,6] and light-duty regulations [7]. The majority of the commercial systems use the same principle as the laboratory grade equipment in order to measure carbon monoxide (CO) and  $\mathrm{CO}_{2}$ : Non-Dispersive Infrared detection (NDIR) after drying the exhaust gas to reduce water  $(\mathrm{H}_2\mathrm{O})$  spectral interference. However, the PEMS specifications in EU permit other principles as well, as long as the equivalency is proven [7]. Recently the wet-basis measurement with heated NDIR was introduced. Such measurements need to take into account the water interference effects (spectral overlap and molecular interaction) on CO and  $\mathrm{CO}_{2}$ . Roller-bench and on-road tests for research purposes are also conducted with Fourier-Transform Infrared Spectroscopy (FTIR) [8] because several chemical components can be simultaneously detected [9-11]. The measurement in this case is wet-based.

The dry-wet conversion of the gas concentrations is done with a multiplicative correction factor  $(K_{d - w})$  given in several national and international regulations [6,7,12]. They are based on established combustion equations to derive air-to-fuel ratios (derived in the past for the performance of carburetors and fuel injection systems) [13,14]. The different expressions of this correction factor in the various regulations are very similar to each other, but not identical. The correction factors are based on the gaseous dry-based concentrations of combustion products (mainly  $\mathrm{CO}_{2}$  and CO) and the fuel properties assuming that neither condensation nor evaporation of water in the pipes take place.

Condensation of water vapor and several other condensable semi-volatile components in the exhaust gas can take place when the temperatures of the pipes or after-treatment devices are below the dew point temperature of the exhaust gas. The dew point of water in the gasoline exhaust is about  $53^{\circ}\mathrm{C}$ , lower for diesel, higher for CNG (about  $60^{\circ}\mathrm{C}$ ) [15]. These values are for stoichiometric combustion and change for instance at lean conditions and or different winter/summer fuel formulations, especially for high ethanol content. The dew point can further increase and even exceed  $100^{\circ}\mathrm{C}$  in the presence of  $\mathrm{SO}_3$  [16]. Thus, condensation during low ambient temperatures and engine cold start is inevitable.

The exhaust gas condensation has been studied to protect Exhaust Gas Recirculation (EGR) valves [16], to model condensation at aftertreatment devices [17], to recover water from military vehicles [18], to avoid condensation in the dilution tunnels for the measurement of emissions [19], or to avoid failures of  $\mathrm{NO}_{\mathrm{x}}$ , oxygen, ammonia, and soot sensors utilizing ceramic sensing elements containing electrodes or electrochemical cells [20]. It has also been shown that it can result in loss of hydrophilic compounds (such as  $\mathrm{NH}_3$ ) [21]. However, as far as the authors are aware, there is no scientific literature on the sensitivity of measured gas concentrations with respect to different dry-wet correction factors, even though cold start emissions are a topic widely discussed [4,22-31]. The comparison of instruments at the tailpipe with different measurement techniques is not common and only recently it was mentioned that some differences could exist [32]. In most cases the exhaust flow rate was considered the major contributor of the differences and not the  $\mathrm{CO}_{2}$  concentration measurements [33].

The objective of this paper is to explain these differences by comparing wet- and dry-based analyzers, quantifying the differences, and discussing the implications on the measurement results and cold start emissions. For this reason, different principles of measurement (NDIR, FTIR) from different manufacturers will be compared for various engine technologies (spark ignition, compression ignition).

# 2. Materials and Methods

The experimental setup is given in Figure 1. The light-duty vehicles tested were respecting the Euro 6 emission standard [34] and the two-wheelers (L-category) the recently introduced Euro 4 [35]. They were all registered in 2017-2018 with one exception (2014). The fleet consisted of vehicles with diesel, gasoline, and CNG fueled engines; see Table 2. Market fuels were used during the campaign: diesel B7, gasoline E10, and CNG ( $>87\%$  methane).

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/8d7771f5-0052-4ca6-b667-4b05f7740930/6437e3276885cd1c176767eb9f9facb03c93bdc6a6ace88f79b282da3b7f9f03.jpg)  
Figure 1. Experimental setup. The tests were conducted with various vehicles (Table 2) at two laboratories with different equipment (Table 1).

Table 1. Characteristics of the equipment.  

<table><tr><td>Parameter</td><td>PEMS A</td><td>PEMS B</td><td>Lab 1</td><td>Lab 2</td><td>FTIR</td></tr><tr><td>Manufacturer</td><td>Horiba</td><td>AVL</td><td>AVL</td><td>Horiba</td><td>AVL</td></tr><tr><td>Model</td><td>OBS-ONE</td><td>M.O.V.E.</td><td>AMA i60</td><td>MEXA 7100</td><td>Sesam</td></tr><tr><td>Principle CO2</td><td>Heated NDIR</td><td>NDIR</td><td>NDIR</td><td>NDIR</td><td>FTIR</td></tr><tr><td>Measurement</td><td>wet</td><td>dry</td><td>dry</td><td>dry</td><td>wet</td></tr><tr><td>Max CO2</td><td>20%</td><td>20%</td><td>20%</td><td>20%</td><td>20%</td></tr><tr><td>Calibration gas</td><td>15%</td><td>15%</td><td>15%</td><td>15%</td><td>-</td></tr><tr><td>Sampling line</td><td>90 °C</td><td>90 °C</td><td>190 °C</td><td>190 °C</td><td>190 °C</td></tr></table>

NDIR: Non-dispersive infrared detection; FTIR: Fourier-Transform Infrared Spectroscopy.

Table 2. Characteristics of the vehicles.  

<table><tr><td>Code</td><td>Euro (-)</td><td>MY (-)</td><td>Fuel (-)</td><td>Mass (kg)</td><td>Power (kW)</td><td>Displ. (l)</td><td>Aftertreatment (-)</td></tr><tr><td>Diesel #1</td><td>6b</td><td>2017</td><td>B7</td><td>1360</td><td>90</td><td>1.6</td><td>DOC + DPF</td></tr><tr><td>Diesel #2</td><td>6d-temp</td><td>2018</td><td>B7</td><td>1180</td><td>96</td><td>1.5</td><td>DOC + DPF + SCR</td></tr><tr><td>CNG #1</td><td>6c</td><td>2018</td><td>CNG</td><td>1360</td><td>80</td><td>1.0</td><td>TWC</td></tr><tr><td>CNG #2</td><td>6b</td><td>2018</td><td>CNG</td><td>2310</td><td>100</td><td>3.0</td><td>TWC</td></tr><tr><td>G-PFI #1</td><td>6b</td><td>2014</td><td>E10</td><td>1130</td><td>57</td><td>1.4</td><td>TWC</td></tr><tr><td>G-PFI #2</td><td>6d-temp</td><td>2018</td><td>E10</td><td>1200</td><td>60</td><td>1.2</td><td>TWC</td></tr><tr><td>G-DI #1</td><td>6c</td><td>2017</td><td>E10</td><td>1390</td><td>110</td><td>1.5</td><td>TWC</td></tr><tr><td>Motorcycle</td><td>4</td><td>2018</td><td>E10</td><td>150</td><td>16</td><td>0.28</td><td>TWC</td></tr><tr><td>Moped</td><td>4</td><td>2018</td><td>E10</td><td>95</td><td>2.5</td><td>0.05</td><td>TWC</td></tr></table>

MY: Model Year; CNG: Compressed Natural Gas; G: Gasoline; DI: direct injection; PFI: Port Fuel Injection; DOC: Diesel Oxidation Catalyst; DPF: Diesel Particulate Filter; SCR: Selective Catalytic Reduction for  $\mathrm{NO}_x$ ; TWC: Three-way Catalytic Converter.

The vehicles were tested with the recently introduced Worldwide harmonized Light-duty vehicle Test Cycle (WLTC) for type approval in EU. For two-wheelers, the recently introduced Worldwide harmonized Motorcycle Test Cycle (WMTC) was used. Extra cold and hot NEDC (New European Driving Cycle) and WLTC tests were done with the Gasoline Direct Injection (G-DI) and constant speed tests with the Gasoline Port Fuel Injection (G-PFI) #2 vehicles.

The motorcycles were tested at the one axle roller dynamometer Vehicle Emissions Laboratory (VELA 1) of the European Commission-Joint Research Centre in Italy. The light-duty tests were conducted at the two axis roller dynamometer Vehicle Emissions Laboratory (VELA 2). G-PFI #1

was additionally tested at the one-axis roller dynamometer (VELA 1). In all cases laboratory grade analyzers were sampling from the tailpipe in parallel with PEMS or FTIR. The characteristics of the equipment are summarized in Table 1. All systems used heated lines  $>90^{\circ}\mathrm{C}$  in order to avoid any condensation in their sampling lines.

PEMS A [36] and FTIR measure chemical concentrations on a wet basis, thus they do not apply any dry-wet correction on the original signal. PEMS B and the laboratory grade analyzers of laboratory 1 and 2 measure on a dry basis: PEMS B compensates for the water interference and for Lab1 and Lab2 the dry-wet correction is applied in post-processing.

NDIR analyzers are composed of an infrared source lamp, a sample chamber, and a reference parallel chamber through which the split IR beam is focused, an optical filter to select the wavelength that the molecules absorb, and a detector. FTIR is composed of an infrared source lamp, a Michelson interferometer as dispersive element, a sample chamber, and a detector. The advantage of the FTIR technique is that the full mid-infrared spectra is acquired, which allows building dedicated multilinear models based on specific wavelength area in which interferences of other compounds (i.e.,  $\mathrm{H}_2\mathrm{O}$ ) do not occur.

# 3. Theoretical Analysis

The concentrations measured on a dry basis  $C_{dry}$  are converted to a wet basis  $C_{wet}$  with the dry-wet conversion factor  $(K_{d - w})$  as:

$$
C _ {w e t} = K _ {d - w} \times C _ {d r y}, \tag {1}
$$

We found the following formulas to calculate  $K_{d - w}$ : according to the RDE test procedure, the ISO (International Organization for Standardization) 8178 standard or based on the  $\mathrm{H}_2\mathrm{O}$  measurement:

# 3.1. RDE

The formula used in EU light-duty [7] and heavy-duty [6] regulations is:

$$
K _ {d - w, R D E} = \left\{1 / \left[ 1 + a \times 0. 0 0 5 \times \left(C _ {C O 2} + C _ {C O}\right) \right] - k _ {w 1} \right\} \times 1. 0 0 8, \tag {2}
$$

where

$$
k _ {w 1} = 1. 6 0 8 \times H _ {a} / (1 0 0 0 + 1. 6 0 8 \times H _ {a}), \tag {3}
$$

where  $H_{a}$  (g water per kg dry air) is the vehicle intake air absolute humidity,  $C_{CO2}$  (\%) is the (measured) dry  $\mathrm{CO}_{2}$  concentration,  $C_{CO}$  (\%) is the (measured) dry CO concentration,  $a$  is the molar hydrogen to carbon ratio of the fuel.

The  $H_{a}$  was provided by the climatic chamber where the vehicles were tested: for the typical testing conditions (23–25 °C and 50%–55% relative humidity), it was in the range 8.7–10.9 g/kg. The  $a$  was 1.86 in most gasoline and diesel cases, while 3.85 for CNG.

# 3.2.ISO8178

ISO 8178-1:2017 [12] is applicable to reciprocating internal combustion engines for mobile, transportable, and stationary use, excluding engines for motor vehicles primarily designed for road use.

$$
K _ {d - w, I S O} = 1 / A, \tag {4}
$$

$$
A = 1 + a \times 0. 0 0 5 \times \left(C _ {C O 2} + C _ {C O}\right) - 0. 1 \times C _ {H 2} + k _ {w 1} - p _ {r} / p _ {b}, \tag {5}
$$

$$
C _ {H 2} = 0. 5 \times a \times C _ {C O} \times \left(C _ {C O 2} + C _ {C O}\right) / \left(C _ {C O} + 3 \times C _ {C O 2}\right), \tag {6}
$$

where  $C_{H2}(\%)$  is the dry  $\mathrm{H}_2$  concentration,  $p_r$  (kPa) is the water pressure after the instrument cooler,  $p_b$  (kPa) is the total barometric pressure. Their ratio is typically around 0.008.

# 3.3. From  $H_2O$  Measurements

In the case where measurements are on a wet basis and  $\mathrm{H}_2\mathrm{O}$  concentrations are available (typical in case of FTIR deployment),  $C_{H2O}(\%)$ ,  $K_{d - w}$  can be estimated from:

$$
K _ {d - w, H 2 O} = 1 - C _ {H 2 O} / 1 0 0. \tag {7}
$$

# 3.4.  $CO_{2}$  Mass Emissions

The mass  $\mathrm{CO}_{2}$  emissions  $m_{\mathrm{CO2}}(\mathrm{g / s})$  were calculated from the (wet) concentration of the  $\mathrm{CO}_{2} C_{\mathrm{CO2}}$  (\%) and the exhaust gas flow rate  $q_{exh}(\mathrm{kg / s})$  according to the EU RDE legislation:

$$
m _ {C O 2} = u \times C _ {C O 2} \times q _ {e x h}, \tag {8}
$$

where  $u$  is the ratio of the density of the  $\mathrm{CO}_{2}$  and the overall density of the exhaust (0.001517 for diesel B7, 0.001551 for CNG, 0.001518 for gasoline E10) [7]. The exhaust gas flow rate was measured in the laboratory from the difference of the total flow of the dilution tunnel minus the dilution air flow.

# 4. Results

# 4.1. Dry-Wet Correction

The  $K_{d - w}$  factors with the two basic approaches (H $_2$ O or CO $_2$  and CO tailpipe measurements) are plotted for some vehicles in Figure 2 during WLTC and WMTC emission tests (see Section 2). It can be seen that (i) the factor based on H $_2$ O measurements is in general smoother than the second-by-second calculation based on CO $_2$  and CO; (ii) the two expressions based on CO $_2$  and CO measurements (ISO, RDE) are very close to each other (within 1.5%); (iii) the CO and CO $_2$  based factor is lower than the H $_2$ O based factor during the first 30-600 s but then very similar.

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/8d7771f5-0052-4ca6-b667-4b05f7740930/0e069a9d23df9b5a85a94b7917d84661b25d0b260ec5ac80d8c5707aee28c135.jpg)

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/8d7771f5-0052-4ca6-b667-4b05f7740930/efe8f6cbf36b259470a260b1c2f12b6f8bf4a73b9fc4169962ec3185c7d89223.jpg)

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/8d7771f5-0052-4ca6-b667-4b05f7740930/d5889211516150650f278b9bd362752b8aa8f8f63b88ce9cde13dbc78dfb9452.jpg)  
Figure 2. Dry-wet correction factor from dry-based carbon dioxide  $(\mathrm{CO}_{2})$  and carbon monoxide (CO) laboratory measurements (non-dispersive infrared detection (NDIR)) or  $\mathrm{H}_2\mathrm{O}$  measurements from Fourier-transform infrared spectroscopy (FTIR) during cold start cycles for some vehicles. The grey lines are the speed profiles of the WLTC (light-duty vehicles) and WMTC (L-category) (right-hand scale).

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/8d7771f5-0052-4ca6-b667-4b05f7740930/14e6a7bbd4f0fa415764c7667a0a90880d64958e21eec488dbd63ae0c2e605e7.jpg)

There are some cases where the  $K_{d - w,H2O}$  factor drops below 0.8 for a few seconds due to  $\mathrm{H}_2\mathrm{O}$  spikes. These spikes appear at spark ignition vehicles when the exhaust gas temperature is close to the dew point and there is a fuel cut-off. We believe that they are true evaporation of water due to changes of flow (pressure) and temperature when there is an almost equilibrium of evaporation and condensation: the pressure drop lowers the dew point and results in water evaporation.

Table 3 summarizes the values of the conversion factors for the start condensation time, i.e., from engine start until the  $K_{d - w,H2O}$  curve in Figure 2 crosses the  $K_{d - w,RDE}$  curve, and for the rest of the cycle. The ISO factor is not considered because it was not derived for the road vehicles; nevertheless, the results would be similar (within 1.5%). For diesel vehicles the two conversion factor curves meet after 35-45 s and have difference around 5%. The conversion factors of the CNG vehicles at the first 2-3 min have the largest differences of 7%-12%. The conversion factors of the gasoline vehicles differ 5%-7.5%; the difference lasts around 2 min for the two-wheelers and 4-10 min for the passenger cars. The differences become smaller at the rest of the cycle (<3%) but with the opposite trend (results with  $K_{d - w,RDE}$  correction higher).

Table 3. Dry-wet conversion factors  $K_{d - w}$  for the starting condensation period ("Start") and the rest cycle ("Rest") calculated before and after the "Start time" respectively. "Dev" stands for the relative deviation between the  $K_{d - w, H2O}$  and the  $K_{d - w, RDE}$ . Vehicles and acronyms as in Table 2.  

<table><tr><td>Vehicle</td><td>Start Time (s)</td><td>Start Kd-w,H2O</td><td>Start Kd-w,RDE</td><td>Dev (%)</td><td>Rest Kd-w,H2O</td><td>Rest Kd-w,RDE</td><td>Dev (%)</td></tr><tr><td>Diesel #1</td><td>35</td><td>0.99</td><td>0.94</td><td>-5.0%</td><td>0.94</td><td>0.95</td><td>+0.9%</td></tr><tr><td>Diesel #2</td><td>45</td><td>0.99</td><td>0.96</td><td>-3.7%</td><td>0.94</td><td>0.95</td><td>+1.0%</td></tr><tr><td>CNG #1</td><td>200</td><td>0.93</td><td>0.82</td><td>-12.0%</td><td>0.80</td><td>0.82</td><td>+3.1%</td></tr><tr><td>CNG #2</td><td>135</td><td>0.88</td><td>0.82</td><td>-7.1%</td><td>0.80</td><td>0.82</td><td>+1.9%</td></tr><tr><td>G-PFI #1</td><td>230</td><td>0.94</td><td>0.87</td><td>-7.6%</td><td>0.86</td><td>0.88</td><td>+2.0%</td></tr><tr><td>G-PFI #2</td><td>160</td><td>0.95</td><td>0.88</td><td>-7.4%</td><td>0.87</td><td>0.89</td><td>+2.3%</td></tr><tr><td>G-DI</td><td>600</td><td>0.92</td><td>0.88</td><td>-4.6%</td><td>0.85</td><td>0.87</td><td>+2.6%</td></tr><tr><td>Motorcycle</td><td>100</td><td>0.92</td><td>0.87</td><td>-5.2%</td><td>0.86</td><td>0.87</td><td>+1.5%</td></tr><tr><td>Moped</td><td>140</td><td>0.94</td><td>0.88</td><td>-6.0%</td><td>0.86</td><td>0.88</td><td>+2.7%</td></tr></table>

# 4.2.  $\mathrm{CO}_{2}$  Exhaust Measurements

The wet  $\mathrm{CO}_{2}$  concentrations (\%) (directly measured or converted with different  $K_{d - w}$  factors) are presented in Figure 3. Only the first  $600\mathrm{s}$  are shown because approximately after the first  $600\mathrm{s}$  the  $K_{d - w}$  corrections tend to be similar (within  $3\%$ ) and thus any  $\mathrm{CO}_{2}$  differences have to do with the accuracy of the  $\mathrm{CO}_{2}$  analyzers (typically better than  $2\%$  for the two techniques: NDIR and FTIR, Table 1) and less with the  $K_{d - w}$  factor. In agreement with the dry-wet correction factor results, there is a big difference at the beginning of the test ( $5\% - 10\%$ ) (FTIR vs. Lab 2 wet corr.) (Table 4). The difference becomes smaller when the  $K_{d - w}$  factor based on  $\mathrm{H}_2\mathrm{O}$  is used ( $< 2\%$ ) (FTIR vs. Lab 2 wet corr.  $\mathrm{H}_2\mathrm{O}$ ). At the rest of the test the differences are  $\pm 2\%$  regardless of the conversion factor that is used.

# 4.3. Principle of Measurement

Figure 4 plots the results for the G-PFI #1 vehicle at two different laboratories. The tests were conducted with a time difference of 1 year and different settings at the chassis dynamometer, so the absolute levels are not directly comparable. Nevertheless, in both cases the wet measurements (PEMS A, left panel or FTIR right panel) are higher than the wet corrected results according to the RDE equation (Lab 1 and PEMS B left panel, Lab 2 and PEMS B, right panel). The differences become smaller when the correction based on  $\mathrm{H}_2\mathrm{O}$  is used (Lab 1 or 2 wet corr.  $\mathrm{H}_2\mathrm{O}$ ). Together with results in Figure 3, this confirms that the cold start differences discussed so far are neither company, nor instrument, nor laboratory dependent, but have to do with the principle of the measurement (direct wet measurement or corrected). The differences between FTIR and heated NDIR are out of the scope of this study.

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/8d7771f5-0052-4ca6-b667-4b05f7740930/d39a7d1d5dfed08eabe5b6cde5dded72585dd7c14de3df92439518cddcfac428.jpg)

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/8d7771f5-0052-4ca6-b667-4b05f7740930/512569ef6a1cf8c0749151453cb83090c03010a7110766dbd6d08ac90a5b7524.jpg)

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/8d7771f5-0052-4ca6-b667-4b05f7740930/caacef9e009ab20143341be8d3302340002ab2365bcf9ce5375d511a637005f7.jpg)  
Figure 3. Comparison of different analyzers during cold start for some vehicles using the  $K_{d - w,RDE}$  (wet corr.) or the  $K_{d - w,H2O}$  (wet corr.  $\mathrm{H}_2\mathrm{O}$ ) equations for the same cycles as in Figure 2.

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/8d7771f5-0052-4ca6-b667-4b05f7740930/a72d113451dd1d7fffed9ce3567f80625655699d828108a4a1322876c76f8ce8.jpg)

Table 4. Mean  $\mathrm{CO}_{2}$  concentration measurements (\%) measured with the FTIR for the starting condensation period of the cycle and the rest of the cycle. The laboratory to the FTIR differences are given using the two conversion factors (real driving emissions (RDE) or  $\mathrm{H}_2\mathrm{O}$ ). Vehicles and acronyms as in Table 2.  

<table><tr><td>Vehicle</td><td>Start Time (s)</td><td>FTIR Start CO2 (%)</td><td>Lab with Kd-w,RDE</td><td>Lab with Kd-w,H2O</td><td>FTIR Rest CO2 (%)</td><td>Lab with Kd-w,RDE</td><td>Lab with Kd-w,H2O</td></tr><tr><td>Diesel #1</td><td>35</td><td>5.53</td><td>-8.4%</td><td>-2.0%</td><td>4.85</td><td>-1.4%</td><td>-1.8%</td></tr><tr><td>Diesel #2</td><td>45</td><td>3.79</td><td>-5.4%</td><td>+0.4%</td><td>5.00</td><td>-0.3%</td><td>-0.5%</td></tr><tr><td>CNG #1</td><td>200</td><td>10.01</td><td>-9.7%</td><td>-0.5%</td><td>9.02</td><td>-1.2%</td><td>-0.1%</td></tr><tr><td>CNG #2</td><td>135</td><td>9.38</td><td>-6.3%</td><td>-1.5%</td><td>9.01</td><td>+0.3%</td><td>+3.0%</td></tr><tr><td>G-PFI #1</td><td>230</td><td>13.04</td><td>-5.3%</td><td>-0.2%</td><td>12.05</td><td>-0.2%</td><td>-1.4%</td></tr><tr><td>G-PFI #2</td><td>160</td><td>13.31</td><td>-7.3%</td><td>+0.6%</td><td>11.79</td><td>+0.7%</td><td>-1.5%</td></tr><tr><td>G-DI</td><td>600</td><td>13.22</td><td>-9.3%</td><td>-1.0%</td><td>12.77</td><td>-1.2%</td><td>-2.2%</td></tr><tr><td>Motorcycle</td><td>100</td><td>13.11</td><td>-6.6%</td><td>-0.7%</td><td>12.97</td><td>-1.7%</td><td>-1.0%</td></tr><tr><td>Moped</td><td>140</td><td>12.57</td><td>-4.6%</td><td>+1.9%</td><td>11.84</td><td>+1.8%</td><td>+1.4%</td></tr></table>

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/8d7771f5-0052-4ca6-b667-4b05f7740930/405b00020b2ab59fbf0f03f53a3a7c0edab01dae88b528939193b80490fdad46.jpg)  
Figure 4. Comparison of different analyzers during a cold start WLTC of the Gasoline Port Fuel Injection (G-PFI) #1 vehicle. Left panel: Laboratory 1, portable emissions measurement system (PEMS) A, and PEMS B. Right panel: Laboratory 2, PEMS B, and FTIR.

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/8d7771f5-0052-4ca6-b667-4b05f7740930/3b3137aa3ca6a04021b47370ef04f1634020d1fe2bf86687754e9125aace2f3d.jpg)

# 4.4. Exhaust Gas Temperature

To further understand the differences, different test cycles were conducted (WLTC or NEDC) with different engine conditions: cold start, hot start (immediately after the cold start test without switching off the engine), warm start (30 min after a cycle). Figure 5 summarizes the results. The  $\mathrm{H}_2\mathrm{O}$  measurements based on FTIR are different at the beginning of the cycle. They reach similar levels after  $250~s$  for the WLTC and after  $850~s$  for the NEDC. These times correspond to a temperature of the exhaust gas at the sampling location of around  $56^{\circ}\mathrm{C}$ , which is just above the dew point of the gasoline exhaust gas  $(53^{\circ}\mathrm{C})$ .

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/8d7771f5-0052-4ca6-b667-4b05f7740930/7897eca540e904864c0abb55abe081917817fefc2772a353812dd14efdeff070.jpg)

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/8d7771f5-0052-4ca6-b667-4b05f7740930/7de0d36be209b7debfe08a9e2a1fc6f3abf5471c2a0b78f83d1c0539fd08586b.jpg)

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/8d7771f5-0052-4ca6-b667-4b05f7740930/d2a57b1f8b76c88f6cf3108e5852eb0009678e7ba2ea5fe1431f939419f94470.jpg)

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/8d7771f5-0052-4ca6-b667-4b05f7740930/cca5aa1ae94644db85a27685448963e53fbeaf33bd920d5310197f4b1e655067.jpg)

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/8d7771f5-0052-4ca6-b667-4b05f7740930/b59ac7b719d03082a6937588ac462a9088dab47a42e846c01cef43fdb4b11781.jpg)  
Figure 5. Vehicle Gasoline Direct Injection (G-DI). Left panels: First  $600\mathrm{s}$  of WLTC. Right panels: NEDC (New European Driving Cycle). Upper:  $\mathrm{H}_2\mathrm{O}$  concentrations. Middle: Exhaust gas temperatures. Low: Speed profiles. Dashed boxes indicate the time period where the  $\mathrm{H}_2\mathrm{O}$  concentrations reached similar levels. The dashed line is the dew point of gasoline exhaust gas  $(53^{\circ}\mathrm{C})$

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/8d7771f5-0052-4ca6-b667-4b05f7740930/69a96c2ce0779393080f237822de67902528b414ad5848760cc8ea8d0e713e08.jpg)

# 5. Discussion

The main observation of this study is that during cold start of spark ignition engines, the  $\mathrm{CO}_{2}$  concentrations measured on a wet basis or estimated from a dry basis may have large differences. This is the first study to quantify this effect. The differences of the first seconds, which originate from the dry-wet correction, were up to  $10\%$  (Figure 3, Table 4). However, for the rest of the test cycle the differences were within experimental uncertainties ( $\pm 2\%$ ). Such comparisons are rare in the literature, even though the engine cold start topic is widely investigated (see Introduction). One study that compared a heated NDIR with the corrected dry laboratory measurement found  $7\%$  for a gasoline vehicle, but it was attributed to the heated NDIR water corrections [37]. Another study that compared the FTIR with the laboratory analyzers showed that the differences of the gasoline vehicles were higher than of the diesel vehicles for  $\mathrm{CO}_{2}$  [26].

The differences were not company, laboratory, or instrument dependent (Figure 4), but they were principle of measurement dependent, i.e., they were seen only between wet- and dry-based measurements. The various equations for the dry-wet correction factor (e.g., RDE or ISO) had a small difference (Figure 2) that could not explain the cold start differences in concentrations. Only using measured  $\mathrm{H}_2\mathrm{O}$  the agreement between wet and corrected measurements was good. The conversion factors based on  $\mathrm{H}_2\mathrm{O}$  or  $\mathrm{CO}_{2}$  and CO had differences  $4\% -12\%$  for the start of a test cycle, but  $< 3\%$  for the rest of the cycle (Table 3).

We believe that the differences during the first seconds of a test are due to condensation of water on the cold surfaces of the vehicle exhaust pipes (assuming that the instruments sampling lines are heated). When the surfaces reach the dew point temperature of the exhaust gas, the differences become negligible (as speculated in Figure 5). The water condensation at the tailpipe has been observed by some researchers [17,20]. The low  $\mathrm{H}_2\mathrm{O}$  concentration at the beginning of a cold start test is something that has been seen [19], but no special attention has been given as until recently measurements from the tailpipe were not required by the legislation.

In order to further investigate this hypothesis, steady cycles at constant speed points were conducted with G-PFI #2 vehicle starting with cold engine at  $23^{\circ}\mathrm{C}$  (Figure 6). During the first 150 s the FTIR  $\mathrm{CO}_{2}$  concentration was higher than the laboratory corrected  $\mathrm{CO}_{2}$ , indicating water vapor condensation. When the exhaust gas temperature reached  $53^{\circ}\mathrm{C}$  the two concentrations were similar. For the time period of 150-210 s the exhaust gas temperature remained relatively constant indicating that both condensation and evaporation were taking place. The two  $\mathrm{CO}_{2}$  concentrations continued to be at the same level until the end of the  $50\mathrm{km/h}$  point (exhaust gas temperature  $< 66^{\circ}\mathrm{C}$ ). When the vehicle accelerated to  $100\mathrm{km/h}$ , the exhaust gas temperature exceeded  $100^{\circ}\mathrm{C}$  and the FTIR  $\mathrm{CO}_{2}$  concentration was lower than the laboratory corrected  $\mathrm{CO}_{2}$ , indicating evaporation of condensed water and that the  $K_{d-w,RDE}$  correction cannot capture it. At the end of the  $100\mathrm{km/h}$  point the two concentrations were at the same level. When the vehicle accelerated to  $130\mathrm{km/h}$  the exhaust gas temperature further increased but the two  $\mathrm{CO}_{2}$  concentrations remained at the same level. This means that the condensed water during the cold start evaporated during the  $100\mathrm{km/h}$  point and no further evaporation took place at  $130\mathrm{km/h}$ . Going back to  $50\mathrm{km/h}$  did not change the differences of the  $\mathrm{CO}_{2}$  concentrations which remained at the same levels.

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/8d7771f5-0052-4ca6-b667-4b05f7740930/b12de35c92ae6acfef99079e2c27f89a29577c69d8b9c173accb0c8706444fe5.jpg)  
Figure 6. Steady speeds test with G-PFI #2. The arrow shows the time when the temperature reached  $53^{\circ}\mathrm{C}$ . On the right  $y$ -axis, "T<sub>exh</sub>" stands for the temperature of the exhaust gas.

Based on the previous discussion, the existing equations which are based on fuel combustion without considering condensation or evaporation cannot capture correctly the first minutes. When the surfaces that the exhaust gas comes into contact exceed the dew point the differences become negligible. The time necessary to reach the dew point depends on various parameters such as ambient temperature, driving cycle, length of tubes (or sampling location), exhaust gas flow rate, fuel composition, etc.

It should be emphasized that the differences have to do with condensation taking place at the tailpipe and aftreatment devices and not with the engine temperature. A warm engine start with tailpipe surface temperatures below the dew point also showed similar (but smaller) effects (Figure 5). On the other hand, a hot engine start with tailpipe surface temperatures above the dew point showed no condensation (Figure 5).

In order to quantify the effect of the condensation in the emissions, the  $\mathrm{CO}_{2}$  mass emissions (g) were calculated as described in Section 3.4 for the start of the cycle ("Start  $\mathrm{CO}_{2}$ " column in Table 5) and the complete cycle ("Total  $\mathrm{CO}_{2}$ " column in Table 5) using the  $K_{d - w,H2O}$ . Then the  $\mathrm{CO}_{2}$  emissions for the start of the cycle were recalculated using the  $K_{d - w,RDE}$  and the difference to the Start  $\mathrm{CO}_{2}$  emissions with  $K_{d - w,H2O}$  is given as "  $\Delta \mathrm{CO}_{2}$ " in Table 5. The difference is negative because the RDE correction is underestimating the  $\mathrm{CO}_{2}$  emissions at the beginning of the cycle. The results are summarized in Table 5, where also the Emission Factors (EF) of the specific tests are given using the  $K_{d - w,H2O}$  ( $\mathrm{EF}_{\mathrm{CO2}}$ ). The effect of condensation ( $\Delta \mathrm{CO}_{2}/$  Start  $\mathrm{CO}_{2}$  or  $\Delta \mathrm{CO}_{2}/$  Total  $\mathrm{CO}_{2}$ ) is significant for the beginning of the cycle ( $5\% -13\%$ ) but almost negligible (diesel vehicles  $0.1\%$ ) to very small (rest vehicles  $<1\%$ ) for the complete cycle. It should be mentioned that this water will completely evaporate when the temperature exceeds  $100^{\circ}\mathrm{C}$  and will result in the opposite effect (excess of water and underestimation of the emissions). The net effect during the entire cycle will be close to zero.

Table 5. Effect of condensation on  $\mathrm{CO}_{2}$  mass emissions for the beginning (start) of the cycle and the full (total) cycle (WLTC or WMTC for two-wheelers). “ $\Delta \mathrm{CO}_{2}$ ” stands for the difference between the  $\mathrm{CO}_{2}$  mass emissions calculated using the  $K_{d - w,RDE}$  and the  $K_{d - w,H2O}$  for the start duration of the cycle given in column “Time.”  

<table><tr><td>Vehicle</td><td>Start Time</td><td>ΔCO2</td><td>Start CO2</td><td>Effect</td><td>Total CO2</td><td>Effect</td><td>EFCO2</td></tr><tr><td></td><td>(s)</td><td>(g)</td><td>(g)</td><td></td><td>(g)</td><td></td><td>(g/km)</td></tr><tr><td>Diesel #1</td><td>35</td><td>-2.7</td><td>49</td><td>-5.6%</td><td>3374</td><td>-0.1%</td><td>144.8</td></tr><tr><td>Diesel #2</td><td>45</td><td>-2.8</td><td>46</td><td>-6.0%</td><td>2760</td><td>-0.1%</td><td>118.5</td></tr><tr><td>CNG #1</td><td>200</td><td>-24.8</td><td>195</td><td>-12.7%</td><td>2842</td><td>-0.9%</td><td>122.0</td></tr><tr><td>CNG #2</td><td>135</td><td>-40.9</td><td>455</td><td>-9.0%</td><td>6819</td><td>-0.6%</td><td>292.7</td></tr><tr><td>G-PFI #1</td><td>230</td><td>-23.5</td><td>322</td><td>-7.3%</td><td>3669</td><td>-0.6%</td><td>157.5</td></tr><tr><td>G-PFI #2</td><td>160</td><td>-11.5</td><td>123</td><td>-10.5%</td><td>3250</td><td>-0.4%</td><td>139.5</td></tr><tr><td>G-DI</td><td>600</td><td>-26.8</td><td>318</td><td>-8.4%</td><td>3096</td><td>-0.9%</td><td>132.9</td></tr><tr><td>Motorcycle</td><td>100</td><td>-3.2</td><td>70</td><td>-4.5%</td><td>1058</td><td>-0.3%</td><td>80.8</td></tr><tr><td>Moped</td><td>140</td><td>-3.1</td><td>53</td><td>-5.9%</td><td>451</td><td>-0.7%</td><td>59.3</td></tr></table>

EF: Emission Factor; CNG: Compressed Natural Gas; G: Gasoline; DI: Direct Injection; PFI: Port Fuel Injection.

The same analysis was conducted for CO (Table 6). The effect of the correction expression was similar to the  $\mathrm{CO}_{2}$  for the cold start: the values varied from  $5\%$  (diesel vehicles, half minute) and  $7\%$  (two-wheelers) to  $8\% -12\%$  (PFIs) and  $13\%$  (CNG). The underestimation during the cold start though had a significant contribution to the total CO emissions, starting from  $1\% -3\%$  for the low CO emitting vehicles and reaching  $7\% -10\%$  with the CNG fueled vehicles. One of the CNG vehicles had  $500~\mathrm{mg / km}$  of CO emissions (half of the Euro 6 limit). The reason that the condensation at cold start remained significant for the full cycle is that CO emissions took place at cold start in most cases [22,38]. Thus, when the condensed water evaporates, the influence on the CO mass will be small due to the low CO concentrations at the hot part of the cycle. Only for a few cases some recent studies showed high CO emissions at the highway part of a trip [38,39].

One more area of interest is the cold start at low ambient temperatures and the laboratory type approval test at low ambient temperatures, the so called Type VI test [40]. It has been discussed to include a WLTC at  $-7^{\circ}\mathrm{C}$  in the Regulation in future. A few tests at this temperature with Diesel #2 and G-PFI #2 showed that the additional  $\mathrm{CO}_{2}$  underestimation is  $5 - 10\mathrm{g}$ . The exact quantification is difficult because also the combustion and the exhaust gas recirculation strategy change and the tests at the two temperatures are not completely comparable.

Table 6. Effect of condensation on CO mass emissions for the beginning of the cycle and the full cycle (WLTC or WMTC for two-wheelers). "ΔCO" stands for the difference between the CO mass emissions calculated using the  $K_{d-w,RDE}$  and the  $K_{d-w,H2O}$  for the start duration of the cycle given in column "Time."  

<table><tr><td>Vehicle</td><td>Start Time</td><td>ΔCO</td><td>Start CO</td><td>Effect</td><td>Total CO</td><td>Effect</td><td>EFCO</td></tr><tr><td></td><td>(s)</td><td>(mg)</td><td>(mg)</td><td></td><td>(mg)</td><td></td><td>(mg/km)</td></tr><tr><td>Diesel #1</td><td>35</td><td>29</td><td>511</td><td>-5.7%</td><td>884</td><td>-3.3%</td><td>38</td></tr><tr><td>Diesel #2</td><td>45</td><td>12</td><td>261</td><td>-4.7%</td><td>1253</td><td>-1.0%</td><td>54</td></tr><tr><td>CNG #1</td><td>200</td><td>798</td><td>6195</td><td>-12.9%</td><td>11,700</td><td>-6.8%</td><td>502</td></tr><tr><td>CNG #2</td><td>135</td><td>195</td><td>1467</td><td>-13.3%</td><td>1971</td><td>-9.9%</td><td>85</td></tr><tr><td>G-PFI #1</td><td>230</td><td>510</td><td>4354</td><td>-11.7%</td><td>16,204</td><td>-3.1%</td><td>695</td></tr><tr><td>G-PFI #2</td><td>160</td><td>145</td><td>1844</td><td>-7.9%</td><td>2914</td><td>-5.0%</td><td>125</td></tr><tr><td>G-DI</td><td>600</td><td>102</td><td>1076</td><td>-9.5%</td><td>2172</td><td>-4.7%</td><td>93</td></tr><tr><td>Motorcycle</td><td>100</td><td>113</td><td>1696</td><td>-6.7%</td><td>8336</td><td>-1.4%</td><td>636</td></tr><tr><td>Moped</td><td>140</td><td>85</td><td>1319</td><td>-6.4%</td><td>6805</td><td>-1.2%</td><td>895</td></tr></table>

EF: Emission Factor; CNG: Compressed Natural Gas; G: Gasoline; DI: direct injection; PFI: Port Fuel Injection.

The results of this study (Table 4 for concentrations or Table 5 for mass emissions) can be used to correct the emissions during the engine cold start period even when no direct "wet" measurement was taken.

Finally, our results can be used to correct "dry" concentrations after the engine cold start period with the following multiplicative correction factors: diesel 0.94, gasoline (including two-wheelers) 0.86, CNG 0.80 (Table 3). Instruments that need such corrections include for instance simplified on-board emissions monitoring systems (SEMS) [41] or garage analyzers that are used for on-road testing [42].

# 6. Implications and Outlook

The implications of water condensation at cold engine start touch many areas of research in the engine and automotive fields:

- Cold start  $\mathrm{CO}_{2}$  and CO emissions, either as absolute value or as contribution to total emissions can be underestimated.  
- Comparisons of instrument measuring on dry- or wet-based methodology at the same location: this is the case, for example, of comparison of PEMS or FTIR systems with laboratory grade analyzers for gases that are measured with analyzers that have interference effects from water  $\mathrm{CO}_{2}$  and CO).  
- Comparison of instruments at different sampling locations: differences can be observed due to condensation between the two locations. This is the case of tailpipe versus dilution tunnel with constant volume sampling (CVS) sampling.  
- Comparison (validation) of PEMS with bags measurement if done in phases (at the moment the comparison is done for the complete cycle).  
- Comparisons of different test cycles with the same instrument. The condensation takes place until the tailpipe and aftertreatment devices reach the dew point. However, this depends on the test parameters. As an example, the WLTC needed  $250\mathrm{~s}$ , while the NEDC  $850\mathrm{~s}$  to reach the dew point at the exit of the tailpipe.  
- Comparisons of tests with different ambient relative humidity, because the amount of stored water in the aftertreatment devices could be different. For example, porous, honeycomb ceramic substrates such as those commonly used in diesel and gasoline particulate filters can store water at relatively high levels (up to  $100\mathrm{g/L}$  under worst case conditions at  $85^{\circ}\mathrm{C}$  and  $85\%$  relative humidity) [43].  
- Estimation of exhaust flow rate based on  $\mathrm{CO}_{2}$  (or CO) measurements (e.g., the tracer method) or fuel consumption and air-to-fuel ratio.

It should be added that the condensation effect will be higher with the increasing adoption of engine stop-start technologies, vehicle hybridization, and improvements in engine efficiencies, which all contribute to lower exhaust temperatures.

# 7. Conclusions

In this study we compared CO and  $\mathrm{CO}_{2}$  emissions from instruments measuring on a dry- and wet-basis using different measuring principles at the exhaust of gasoline, compressed natural gas (CNG), and diesel light-duty and L-category vehicles. The dry concentrations were converted to wet by applying formulas given in the regulation or based on  $\mathrm{H}_2\mathrm{O}$  measurements.

At the beginning of a cold start test, when the exhaust gas temperature was below the dew point (i.e.,  $53^{\circ}\mathrm{C}$  for gasoline vehicles) condensation at the unheated exhaust pipes took place. The condensation lasted 2-3 min for spark-ignition vehicles, but only half a minute for compression ignition vehicles. The duration depended on the ambient temperature and the test cycle. For the New European Driving Cycle it lasted almost 15 min for a gasoline vehicle. The condensation resulted in  $5\% - 13\%$  underestimation of the  $\mathrm{CO}_{2}$  concentrations and emissions using a dry-wet correction factor. The effect was almost indistinguishable ( $<1\%$ ) from experimental uncertainties when considering the whole test cycles (20-30 min). It remained important for CO (10%) for the vehicles since the majority of CO emissions took place during the cold start period.

Author Contributions: Conceptualization, B.G.; formal analysis, B.G., M.C. and A.A.Z.; data curation, B.G.; writing—original draft preparation, B.G.; writing—review and editing, M.C. and A.A.Z.

Acknowledgments: The authors would like to acknowledge the VELA technical staff (in alphabetical order): A. Bonamin, C. Bonato, M. Cadario, P. Le Lijour, D. Lesueur, M. Sculati.

Conflicts of Interest: The opinions expressed in this manuscript are those of the authors and should in no way be considered to represent an official opinion of the European Commission. Mention of trade names or commercial products does not constitute endorsement or recommendation by the authors or the European Commission.

# Abbreviations

<table><tr><td>CNG</td><td>Compressed Natural Gas</td></tr><tr><td>CVS</td><td>Constant Volume Sampling</td></tr><tr><td>DI</td><td>Direct Injection</td></tr><tr><td>DOC</td><td>Diesel Oxidation Catalyst</td></tr><tr><td>DPF</td><td>Diesel Particulate Filter</td></tr><tr><td>EF</td><td>Emission Factor</td></tr><tr><td>EGR</td><td>Exhaust Gas Recirculation</td></tr><tr><td>EU</td><td>European Union</td></tr><tr><td>FTIR</td><td>Fourier-Transform Infrared Spectroscopy</td></tr><tr><td>G</td><td>Gasoline</td></tr><tr><td>G-DI</td><td>Gasoline Direct Injection</td></tr><tr><td>G-PFI</td><td>Gasoline Port Fuel Injection</td></tr><tr><td>IR</td><td>InfraRed</td></tr><tr><td>ISO</td><td>International Organization for Standardization</td></tr><tr><td>MY</td><td>Model Year</td></tr><tr><td>NDIR</td><td>Non-Dispersive Infrared Detection</td></tr><tr><td>NEDC</td><td>New European Driving Cycle</td></tr><tr><td>PEMS</td><td>Portable Emissions Measurement System</td></tr><tr><td>PFI</td><td>Port Fuel Injection</td></tr><tr><td>RDE</td><td>Real Driving Emissions</td></tr><tr><td>SCR</td><td>Selective Catalytic Reduction for NOx</td></tr><tr><td>SEMS</td><td>Simplified onboard Emissions Monitoring Systems</td></tr><tr><td>TWC</td><td>Three-way Catalytic Converter</td></tr><tr><td>VELA</td><td>Vehicle Emissions LABoratory</td></tr><tr><td>WLTC</td><td>Worldwide harmonized Light-duty vehicles Test Cycle</td></tr><tr><td>WMTC</td><td>Worldwide harmonized Motorcycle Test Cycle</td></tr></table>

# References

1. European Environmental Energy. Air Quality in Europe—2018 Report; EEA Report No. 12/2018; Publication Office of the European Union: Luxembourg, 2018. [CrossRef]  
2. European Commission. Regulation (EU) No 333/2014 of the European Parliament and of the Council of 11 March 2014 amending Regulation (EC) No 443/2009 to define the modalities for reaching the 2020 target to reduce CO2 emissions from new passenger cars. Off. J. Eur. Union 2014, L103, 15-21.  
3. UNECE. Uniform Provisions Concerning the Measures to Be Taken against the Emission of Gaseous and Particulate Pollutants from Compression Ignition Engines and Positive Ignition Engines for Use in Vehicles; Regulation No. 49. Revision 6; United Nations Economic Commission for Europe: Geneva, Switzerland, 2013.  
4. Clairotte, M.; Adam, T.W.; Zardini, A.A.; Manfredi, U.; Martini, G.; Krasenbrink, A.; Vicet, A.; Tournié, E.; Astorga, C. Effects of low temperature on the cold start gaseous emissions from light duty vehicles fuelled by ethanol-blended gasoline. Appl. Energy 2013, 102, 44-54. [CrossRef]  
5. Code of Federal Regulations. Title 40: Protection of Environment. Part 1065—Engine-Testing Procedures. Subpart J—Field Testing and Portable Emission Measurement Systems. Available online: https://www.ecfr.gov/cgi-bin/text-idx?SID=6aca586aabc6de74a06dea2a85f5a5ab&mc=true&node=sp40.37.1065.j&rgn=div6 (accessed on 8 May 2019).  
6. European Commission. Commission Regulation (EU) No 582/2011 of 25 May 2011 implementing and amending Regulation (EC) No 595/2009 of the European Parliament and of the Council with respect to emissions from heavy-duty vehicles (Euro VI) and amending Annexes I and III to Directive 2007/46/EC of the European Parliament and of the Council. Off. J. Eur. Union 2011, L167, 1-168.  
7. European Commission. Commission Regulation (EU) 2016/427 of 10 March 2016 amending Regulation (EC) No 692/2008 as regards emissions from light passenger and commercial vehicles (Euro 6). Off. J. Eur. Union 2016, L82, 1-98.  
8. Adachi, M. Emission measurement techniques for advanced powertrains. Meas. Sci. Technol. 2000, 11, R113-R129. [CrossRef]  
9. Daham, B.; Andrews, G.; Li, H.; Ballesteros, R.; Bell, M.; Tate, J.; Ropkins, K. Application of a portable FTIR measuring on-road emissions. SAE Tech. Pap. 2005, 20, 171-192. [CrossRef]  
10. Zardini, A.A.; Suarez-Bertoa, R. Unregulated pollutants from tampered two-wheelers. Transp. Res. Procedia 2016, 14, 3109-3118. [CrossRef]  
11. Clairotte, M.; Adam, T.W.; Chirico, R.; Giechaskiel, B.; Manfredi, U.; Elsasser, M.; Sklorz, M.; De Carlo, P.F.; Heringa, M.F.; Zimmermann, R.; et al. Online characterization of regulated and unregulated gaseous and particulate exhaust emissions from two-stroke mopeds: A chemometric approach. *Anal. Chim.* Acta 2012, 717, 28-38. [CrossRef]  
12. ISO 8178-1:2017. Reciprocating Internal Combustion Engines—Exhaust Emission Measurement—Part 1: Test-Bed Measurement Systems of Gaseous and Particulate Emissions; ISO: Geneva, Switzerland, 2017.  
13. Silvis, W. An algorithm for calculating the air/fuel ratio from exhaust emissions. SAE Tech. Pap. 1997, 970514. [CrossRef]  
14. D'Ambrosio, S.; Spessa, E.; Vassallo, A. Methods for specific emission evaluation in spark ignition engines based on calculation procedures of air-fuel ratio: Development, assessment, and critical comparison. J. Eng. Gas Turbines Power 2005, 127, 869-882. [CrossRef]  
15. Garrido Gonzalez, N.; Baar, R.; Drueckhammer, J.; Kaepner, C. The thermodynamics of exhaust gas condensation. SAE Tech. Pap. 2017, 10, 1411-1421. [CrossRef]  
16. Yang, B.; Mao, S.; Altin, O.; Feng, Z.; Michaelides, E. Condensation analysis of exhaust gas recirculation system for heavy-duty trucks. J. Therm. Sci. Eng. Appl. 2011, 3, 041007. [CrossRef]  
17. Sharma, M.; Laing, P.; Son, S. Modeling water condensation in exhaust A/T devices. SAE Tech. Pap. 2010, 2010-01-0885. [CrossRef]  
18. Barros, S.; Atkinson, W.; Piduru, N. Extraction of liquid water from the exhaust of a diesel engine. SAE Tech. Pap. 2015, 2015-01-2806. [CrossRef]  
19. Inoue, K.; Ishihara, M.; Akashi, K.; Adachi, M.; Ishida, K. Numerical analysis of mass emission measurement systems at low emission vehicles. SAE Tech. Pap. 1999, 1999-01-0150. [CrossRef]  
20. Meena, R.; Krusch, A.; Meister, K.; Holzknecht, C. Water load determination approach in two wheeler exhaust system. SAE Tech. Pap. 2018, 2018-32-0075. [CrossRef]

21. Mohn, J.; Forss, A.-M.; Bruhlmann, S.; Zeyer, K.; Luscher, R.; Emmenegger, L.; Novak, P.; Heeb, N. Time-resolved ammonia measurement in vehicle exhaust. Int. J. Environ. Pollut. 2004, 22, 342-356. [CrossRef]  
22. Weilenmann, M.; Soltic, P.; Saxer, C.; Forss, A.; Heeb, N. Regulated and nonregulated diesel and gasoline cold start emissions at different temperatures. Atmos. Environ. 2005, 39, 2433-2441. [CrossRef]  
23. Weilenmann, M.; Favez, J.-Y.; Alvarez, R. Cold-start emissions of modern passenger cars at different low ambient temperatures and their evolution over vehicle legislation categories. Atmos. Environ. 2009, 43, 2419-2429. [CrossRef]  
24. Favez, J.-Y.; Weilenmann, M.; Stilli, J. Cold start extra emissions as a function of engine stop time: Evolution over the last 10 years. Atmos. Environ. 2009, 43, 996-1007. [CrossRef]  
25. Zardini, A.A.; Platt, S.M.; Clairotte, M.; El Haddad, I.; Temime-Roussel, B.; Marchand, N.; Ježek, I.; Drinovec, L.; Močnik, G.; Slowik, J.G.; et al. Effects of alkylate fuel on exhaust emissions and secondary aerosol formation of a 2-stroke and a 4-stroke scooter. Atmos. Environ. 2014, 94, 307-315. [CrossRef]  
26. Ko, J.; Son, J.; Myung, C.; Park, S. Comparative study on low ambient temperature regulated/unregulated emissions characteristics of idling light-duty diesel vehicles at cold start and hot restart. *Fuel* 2018, 233, 620-631. [CrossRef]  
27. Li, H.; Andrews, G.; Savvidis, D.; Daham, B.; Ropkins, K.; Bell, M.; Tate, J. Characterization of regulated and unregulated cold start emissions for different real world urban driving cycles using a SI passenger car. SAE Tech. Pap. 2008, 2008-01-1648. [CrossRef]  
28. Khalfan, A.; Li, H.; Andrews, G. Cold Start SI Passenger Car Emissions from Real World Urban Congested Traffic. SAE Tech. Pap. 2015, 2015-01-1064. [CrossRef]  
29. Giechaskiel, B. Solid particle number emission factors of Euro VI heavy-duty vehicles on the road and in the laboratory. Int. J. Environ. Res. Public Health 2018, 15, 304. [CrossRef] [PubMed]  
30. Giechaskiel, B.; Gloria, R.; Carriero, M.; Lahde, T.; Forloni, F.; Perujo, A.; Martini, G.; Bissi, L.M.; Terenghi, R. Emission factors of a Euro VI heavy-duty diesel refuse collection vehicle. Sustainability 2019, 11, 1067. [CrossRef]  
31. Giechaskiel, B.; Suarez-Bertoa, R.; Lahde, T.; Clairotte, M.; Carriero, M.; Bonnel, P.; Maggiore, M. Emissions of a Euro 6b diesel passenger car retrofitted with a solid ammonia reduction system. Atmosphere 2019, 10, 180. [CrossRef]  
32. Varella, R.; Giechaskiel, B.; Sousa, L.; Duarte, G. Comparison of portable emissions measurement systems (PEMS) with laboratory grade equipment. Appl. Sci. 2018, 8, 1633. [CrossRef]  
33. Giechaskiel, B.; Casadei, S.; Mazzini, M.; Sammarco, M.; Montabone, G.; Tonelli, R.; Deana, M.; Costi, G.; Di Tanno, F.; Prati, M.V.; et al. Inter-laboratory correlation exercise with portable emissions measurement systems (PEMS) on chassis dynamometers. Appl. Sci. 2018, 8, 2275. [CrossRef]  
34. European Commission. Regulation (EC) No 715/2007 of the European Parliament and of the Council of 20 June 2007 on type approval of motor vehicles with respect to emissions from light passenger and commercial vehicles (Euro 5 and Euro 6) and on access to vehicle repair and maintenance information. Off. J. Eur. Union 2007, L171, 1-16.  
35. European Commission. Regulation (EU) No 168/2013 of the European parliament and of the council of 15 January 2013 on the approval and market surveillance of two- or three-wheel vehicles and quadricycles. Off. J. Eur. Union 2013, L60, 52-128.  
36. Ohtsuki, S.; Inoue, K.; Yamagishi, Y.; Namiyama, K. Studies on emission measurement techniques for super-ultra low emission vehicles. SAE Tech. Pap. 2002, 2002-01-2709. [CrossRef]  
37. Ropkins, K.; Tate, J.; Li, H.; Andrews, G.; Hawley, G.; Bell, M. Chassis dynamometer evaluation of on-board exhaust emission measurement system performance in SI car under transient operating conditions. SAE Tech. Pap. 2008, 2008-01-1826. [CrossRef]  
38. Clairotte, M.; Valverde, V.; Bonnel, P.; Giechaskiel, B.; Carriero, M.; Otura, M.; Fontaras, G.; Pavlovic, J.; Martini, G.; Krasenbrink, A.; et al. Joint Research Centre 2017 Light-Duty Vehicles Emissions Testing; EUR 29302EN; Publications Office of the European Union: Luxembourg, 2018.  
39. Valverde, V.; Adri, B.; Clairotte, M.; Pavlovic, J.; Suarez-Bertoa, R.; Giechaskiel, B.; Astoga-Llorens, C.; Fontaras, G. Emission factors derived from thirteen Euro 6b light-duty vehicles based on laboratory and on-road measurements. Atmosphere 2019, 10, 243. [CrossRef]  
40. Suarez-Bertoa, R.; Astorga, C. Impact of cold temperature on Euro 6 passenger car emissions. Environ. Pollut. 2018, 234, 318-329. [CrossRef]

41. Heepen, F.; Yu, W. SEMS for individual trip reports and long-time measurement. SAE Tech. Pap. 2019, 2019-01-0752. [CrossRef]  
42. Varella, R.; Duarte, G.; Baptista, P.; Sousa, L.; Mendoza Villafuerte, P. Analysis of the influence of outdoor temperature in vehicle cold-start operation following EU real driving emission test procedure. SAE Int. J. Commer. Veh. 2017, 10, 596-697. [CrossRef]  
43. Sappok, A.; Ragaller, P.; Guarino, A.; Mandelbaum, J.; Lapenta, L.; Kolberg, D.; Newman, R.; Lu, X.; Cors, D. Direct measurement of aftertreatment system stored water levels for improved dew point management using radio frequency sensing. SAE Tech. Pap. 2019, 2019-01-0739. [CrossRef]

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/8d7771f5-0052-4ca6-b667-4b05f7740930/8466c491994f1dd1cc993f18631ce7bb86a87971293d6b97b3e095fcd1a87e3e.jpg)

© 2019 by the authors. Licensee MDPI, Basel, Switzerland. This article is an open access article distributed under the terms and conditions of the Creative Commons Attribution (CC BY) license (http://creativecommons.org/licenses/by/4.0/).