# Extension of an assessment model of ship traffic exhaust emissions for particulate matter and carbon monoxide

J.-P. Jalkanen<sup>1</sup>, L. Johansson<sup>1</sup>, J. Kukkonen<sup>1</sup>, A. Brink<sup>2</sup>, J. Kalli<sup>3</sup>, and T. Stipa<sup>1</sup>

$^{1}$ Finnish Meteorological Institute, P.O. Box 503, 00101 Helsinki, Finland  
$^{2}$  Åbo Akademi, Process Chemistry Center (CMC), Tuomiokirkontori 3, 20500 Turku, Finland  
<sup>3</sup>University of Turku, Centre for Maritime Studies, P.O. Box 181, 28101 Pori, Finland

Correspondence to: J.-P. Jalkanen (jukka-pekka.jalkanen@fmi.fi)

Received: 9 June 2011 - Published in Atmos. Chem. Phys. Discuss.: 5 August 2011

Revised: 20 February 2012 - Accepted: 2 March 2012 - Published: 12 March 2012

Abstract. A method is presented for the evaluation of the exhaust emissions of marine traffic, based on the messages provided by the Automatic Identification System (AIS), which enable the positioning of ship emissions with a high spatial resolution (typically a few tens of metres). The model also takes into account the detailed technical data of each individual vessel. The previously developed model was applicable for evaluating the emissions of  $\mathrm{NO}_{\mathrm{x}}$ ,  $\mathrm{SO}_{\mathrm{x}}$  and  $\mathrm{CO}_{2}$ . This paper addresses a substantial extension of the modelling system, to allow also for the mass-based emissions of particulate matter (PM) and carbon monoxide (CO). The presented Ship Traffic Emissions Assessment Model (STEAM2) allows for the influences of accurate travel routes and ship speed, engine load, fuel sulphur content, multiengine setups, abatement methods and waves. We address in particular the modeling of the influence on the emissions of both engine load and the sulphur content of the fuel. The presented methodology can be used to evaluate the total PM emissions, and those of organic carbon, elemental carbon, ash and hydrated sulphate. We have evaluated the performance of the extended model against available experimental data on engine power, fuel consumption and the composition-resolved emissions of PM. We have also compared the annually averaged emission values with those of the corresponding EMEP inventory. As example results, the geographical distributions of the emissions of PM and CO are presented for the marine regions of the Baltic Sea surrounding the Danish Straits.

# 1 Introduction

Emissions of PM from shipping have a significant impact on ambient air quality in densely populated coastal areas and these may substantially contribute to detrimental impacts on human health (Corbett et al., 2007). Stringent limits for the sulphur content of marine fuels and  $\mathrm{NO}_{\mathrm{x}}$ -emissions are expected to reduce the emissions from ships. The PM emissions are simultaneously reduced, as a major part of PM emissions is in the form of sulphate. However, sulphur content reductions will not eradicate PM emissions completely (Winnes and Fridell, 2010b; Fridell et al., 2008; Cooper, 2001, 2003; Kasper et al., 2007; Buhaug et al., 2009), even if the global fleet would switch to low sulphur fuel. The emissions of PM can also be reduced by using after-treatment techniques, which will remove a significant part of the PM emissions (Corbett et al., 2010; European Commission Directorate General Environment, 2005) Scrubbing systems from engine manufacturers have been commonly applied to diesel power plants on land, but their commercial installations to ships have been scarce. This is expected to change, after the the implementation of the stringent sulphur limits included in the revised Marpol Annex VI of the IMO (International Maritime Organization, 1998).

International ship emissions are not part of the routine reporting under the Convention on the Long-Range Transport of Atmospheric Pollutants (CLRTAP). Top-down emission inventories are generated based on the fuel sales or cargo statistics (e.g. Schrooten et al., 2009). New ship emission inventories have recently been generated especially for arctic regions (Paxian et al., 2010; Corbett et al., 2010).

Various regional ship emission inventories have been introduced (Matthias et al., 2010; De Meyer et al., 2008) and the previously significant uncertainties in the estimated emissions of global ship traffic have been evaluated to have decreased during the last half decade (Paxian et al., 2010; Lack et al., 2009).

Information is currently scarce especially regarding the geographical distribution and chemical composition of PM emissions arising from ship traffic, and the chemical composition details have not commonly been introduced to global inventories of ship emissions. Corbett et al. (2010) subdivided PM from marine traffic into organic carbon and black carbon. They did not allow for the dependency on engine load of the constituents of PM; instead, fixed, predetermined loads were used for main and auxiliary engines. However, the emissions of both the various chemical components of PM and CO are sensitive to engine load. The classifications of PM components, and the detailed definitions of such classes also can vary, depending on the measurement techniques used. For instance, the experimental methods using absorptive techniques often provide black carbon (Eyring et al., 2010), but chemical techniques report a division to elemental and organic carbon. Clearly, black carbon and elemental carbon cannot be used as synonymous expressions, since there are components of organic carbon, which also absorb light (e.g. Andreae and Gelencsér, 2006).

There are several situations, in which decreasing the speed of a vessel will result in substantial changes of the engine loads and chemical composition of emissions; examples of such conditions are port maneuvers, slow steaming and ships that are breaking ice cover (Winnes and Fridell, 2010a). In such conditions, the assumptions of pre-determined engine loads and static emission factors are not valid. Although port emissions have been determined previously (Hulskotte and Denier van der Gon, 2010; Cooper, 2003), these have been neglected in many studies, due to their complexity regarding engine operating modes and different fuel types. Evaluation of shipping emissions in port areas is challenging, caused by the dependency of emissions on engine load, the changes of fuel type and the differences of operating profiles of ships at berth, during maneuvering and during normal cruising. In case of slow steaming, the effects of running the engines of ships on abnormally low loads result in increased emissions in most marine diesel engines. However, this is not necessarily the case for multi-engine setups or combined diesel-electric installations, since unnecessary engines can be switched off to conserve fuel and taken to operation whenever needed. The influences of such more detailed features involving engine operation and engine load, including multi-engine setups, are practically neglected in all previously available ship emissions inventories.

The authors of this article have previously presented a method for the evaluation of the exhaust emissions of marine traffic, based on the messages provided by the Automatic Identification System (AIS), which enable the identi

fication, and the determination of the location and instantaneous speeds of the vessels (Jalkanen et al., 2009). The accuracy of the AIS data for the positioning of ship emissions is limited only by the inaccuracies of the Global Positioning System and the information on the exact location of AIS transponders onboard ships (typically a few tens of metres). The use of AIS data substantially reduces the uncertainties in analyzing the operational states of the ship engines. It also resolves the uncertainties in evaluating the times of ships spent at sea and at berth, and eliminates the need to computationally construct ship routes.

The previously developed model was applicable for evaluating the emissions of  $\mathrm{NO}_{\mathrm{x}}$ ,  $\mathrm{SO}_{\mathrm{x}}$  and  $\mathrm{CO}_{2}$ . The model was based on the relationship of the instantaneous speed to the design speed and the use of the detailed technical information of the engines. The effect of waves was also included in the model. However, the methodologies for evaluating the power and fuel consumption were fairly simple, and these assumptions were observed to provide biased estimates, especially for auxiliary engines.

Using the STEAM2 model, engine loads during voyages can be determined with reasonable accuracy based on the ratio of ship speed and the calculated resistance that the ship is required to overcome at a specified speed. This can be done even for ships with multi-engine setups (these are known for each ship). To our understanding these features have not currently been included in the existing global inventories of Corbett et al. (2010) and Paxian et al. (2010). Both of the models used in computing the above-mentioned two inventories are well suited for evaluating future scenarios. On the other hand, the AIS data offers highly detailed information of the past and present state of maritime traffic.

The objectives of this article are (i) to present the principles and mathematical structure of the extended ship emission model (STEAM2), (ii) to compare the predictions of the extended model with those of the original model (STEAM), regarding the instantaneous power and fuel consumption, using onboard engine measurements, (iii) to compare the annually averaged emission values briefly with those of the corresponding EMEP inventory, (iv) to evaluate the extended model against available experimental data, and (v) to illustrate the capabilities of the model by presenting some selected numerical results.

# 2 The STEAM2 model

We have developed a more sophisticated scheme for the resistance evaluation and a load balancing of the engines; these improvements were necessary especially for the accurate modeling of PM and CO emissions. The STEAM2 model is also more versatile compared with the original model in describing the effects of ship speed and movement, engine load and fuel changes, abatement techniques, and operating profiles of vessels. The methods to model the effect of waves

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/e04ee8f3-21c7-4e13-b98f-bb26187f54a1/58b718cb4f1ca4067b796fb0c5cee1e5857ed00916b38935745aa7976a29cb61.jpg)  
Fig. 1. A schematic diagram of the main components of the STEAM2 model and their inter-relations. The model input data sources are presented on the uppermost row of rectangles, and the model output data (i.e. emissions) are presented on the lowest row of rectangles. The arrows describe either the flow of information in the model, or a modelled dependency between various factors. The different colors denote the various categories of factors included in the model; dotted and solid arrows are used only for visual clarity.

to ship emissions are identical to those in the earlier version of the model (Jalkanen et al., 2009). Abatement techniques are also included in the STEAM2 model and applied to the evaluation of the emissions of PM and CO whenever appropriate. However, the number of vessels with abatement techniques installed is less than  $1\%$  of all the vessels in the ship properties database.

The information on each individual ship and the installed main and auxiliary engines were obtained from IHS Fairplay (IHS Fairplay, 2010), but augmented with data from various other sources (such as other classification societies and ship owners), whenever necessary. An illustration of the main components of the STEAM2 model is presented in Fig. 1. The main input data sources are the internal ship database (compiled in this study) and the AIS-data.

The internal ship database of the STEAM2 model contains the technical details of ships used in the evaluation of emissions. The database contains the information of more than 30 000 ships; this is approximately a third of the global fleet. Most of the ships in the database are newer ships that have been built within the last two decades; most of these ships are frequently operating in the Baltic Sea.

The use of the AIS data facilitates an accurate mapping of the ship traffic, including the detailed instantaneous location and speed of each vessel in the considered area. For example, in 2007 there were 9497 vessels equipped with AIS signal transmitters in the Baltic Sea; more than 210 million so-called position reports were received from these vessels. The automatic position reports contain the detailed information on the identification, location, speed and heading of each individual vessel. For each ship in a regular schedule, this results in tens of thousands of position updates each month.

Based on the properties of the ships and its power requirements, the model can evaluate the power consumption and load of the engine, and the fuel consumption of the ship. Based on these values, the model is used to evaluate the emissions of  $\mathrm{NO}_{\mathrm{x}}$ ,  $\mathrm{SO}_{\mathrm{x}}$ , CO,  $\mathrm{CO}_{2}$  and PM, as a function of time and location. Geographical resolution of emission grids is limited by the accuracy of the Global Positioning System (GPS), which is of the order of a few tens of meters. The update frequency of AIS signals varies according to the data source; studies covering limited sea areas, such as the Baltic Sea or the North Sea, have usually a downscaled update frequency of from five to six minutes, whereas the best available update rate is once in every two seconds. In the model, the ship positions are updated every second, as

the model interpolates the location information between two subsequent AIS position reports.

The main differences between the new model (STEAM2) and the previously developed one (STEAM) include that the CO- and PM emissions are included in the new model. A revised evaluation method is also used for analyzing the resistance of ships in water. The model also includes an enhanced modeling of the power consumption of auxiliary engines, which depend on ship type and its operation mode.

# 3 The evaluation of resistance and ship specifications

A method presented by Hollenbach (1998) is used to calculate the resistance of ships due to moving in water. The predictions of the Hollenbach method agree well with other performance prediction methods, such as those of Holtrop-Mennen (Matulja and Dejhalla, 2007; Holtrop and Mennen, 1978, 1982). The use of this method, compared with the previous model, improves the predictions of resistance and engine power, especially in cases, in which the hull dimensions and the engine data is available, but the design speed of the vessel is unknown.

In the previous version of the STEAM model, the design speed was a critical parameter for the model performance; if that value was not available, an average speed was used instead that was specific for each ship type. The use of the Hollenbach method avoids such assumptions, and therefore provides a more reliable basis for the resistance calculations. However, the application of the method is in many cases limited by the availability of the hull and propeller details.

The total resistance of a moving marine vessel (in kN) can be estimated with

$$
R _ {\text {T o t a l}} \approx R _ {\mathrm {F}} + R _ {\mathrm {R}} \tag {1}
$$

where  $R_{\mathrm{F}}$  is the frictional resistance acting on the wet surface of the vessel and  $R_{\mathrm{R}}$  is the residual resistance, which can be loosely described as the resistance from forming waves and turbulence. Contributions from moving in shallow water and from air resistance are neglected because of their small contribution to overall result.

The frictional resistance  $(R_{\mathrm{F}})$  is described using the International Towing Tank Conference procedure (ITTC, 1999)

$$
R _ {\mathrm {F}} = C _ {\mathrm {F}} \frac {\rho}{2} v ^ {2} S \tag {2}
$$

where the frictional resistance coefficient  $(C_{\mathrm{F}})$  is  $C_{\mathrm{F}} = 0.075 / (\log R_n - 2)^2$ , where  $R_{n}$  is the Reynolds number,  $\rho$  is the seawater density  $(\mathrm{km~m}^{-3})$ ,  $v$  is the speed of the vessel (in  $\mathrm{ms}^{-1}$ ) and  $S$  is the wet surface (in  $\mathrm{m}^2$ ). The residual resistance is calculated as

$$
R _ {\mathrm {R}} = C _ {\mathrm {R}} \frac {\rho}{2} v ^ {2} \left(\frac {B T}{1 0}\right) \tag {3}
$$

where  $B$  is vessel breadth (in meters) and  $T$  is draught (in meters). The residual resistance coefficient  $(C_{\mathrm{R}})$  and wet surface  $(S,$  in Eq. 2) are evaluated according to Schneekluth and

Bertram (1998) and Hollenbach (1998). This calculation is lengthy and depends on whether the vessel has single or twin propellers and whether it has a bulbous bow or not. The details of these calculations can be found in Schneekluth and Bertram (1998) and Hollenbach (1998).

The Hollenbach method is based on the resistance measurements of 433 tank tests. The method requires some parameters, like the Block coefficient  $(C_{\mathrm{b}})$  and propeller diameter  $(d)$  to be known, which are not usually available from commercial ship technical databases. These coefficients were evaluated as suggested by Watson and Gilfillan (1976) and further described by Watson (1998). The  $C_{\mathrm{b}}$  is one of the coefficients describing the shape of the hull and it can be written as

$$
C _ {\mathrm {b}} = 0. 7 + \frac {1}{8} \operatorname {a t a n} \left(\frac {2 3 - 1 0 0 F _ {n}}{4}\right), \tag {4}
$$

where  $F_{n}$  is Froude number, which is computed as vessel speed/(gravity constant  $\times$  waterline length). Neither waterline length nor the length over surface (used by the Hollenbach method) was readily available for most of the vessels. In these cases we used instead an average value of overall length in meters (LOA) and length between perpendiculars in meters (LBP).

Propeller diameter is required in order to apply the Hollenbach method. In case the propeller diameter  $d$  is unknown, it is estimated using the method described by Watson (1998) using the following estimate:

$$
d = 1 6. 2 \frac {P _ {\mathrm {s}} ^ {0 . 2}}{N ^ {0 . 6}} \tag {5}
$$

where  $P_{\mathrm{s}}$  is the service power of the main engine (80% of the maximum continuous rating) provided by IHS Fairplay (2010) in kilowatts and  $N$  is the propeller's angular velocity expressed in rpm (revolutions per minute). Propeller rpm is required to estimate the propeller and transmission losses and the required main engine power. If the number of propellers is unknown, then the ship is simply assumed to operate with a single propeller. Both  $C_{\mathrm{b}}$  and  $d$  are required to evaluate the residual resistance coefficient of Eq. (3), see Schneekluth and Betram (1998) and Hollenbach (1998).

Equation (5) was applied for all single-propeller vessels, for which the propeller rpm was known. For multi-propeller vessels, or if both the propeller rpm and diameter were unknown, an estimated value was used based on the vessel draught. This approach does not consider exceptional cases of surface piercing propellers. It is expected to lead to a reasonable estimate of propeller diameter. In multi-propeller cases and also if propeller data is unavailable, propeller size is estimated with a ship type specific fraction of draught, as draught is one of the main limiting factors for propeller size. Fractions of draught values, which have been estimated using the internal ship database, are listed in Appendix A.

From total resistance (in kN) the propelling power  $(P_{\mathrm{Propel}}$  in kW) is obtained by

$$
P _ {\text {P r o p e l}} = R _ {\text {T o t a l}} v \tag {6}
$$

where  $v$  is the instantaneous vessel speed (in  $\mathrm{ms}^{-1}$ ). The main engine power, however, can never be completely transformed to actual propelling power of the ship. The dimensionless quasi propulsive constant  $\eta_{\mathrm{qpc}}$  is used to describe the effectiveness of converting the main engine power to actual propelling power, taking propulsive losses arising from transmission, hull, shaft and propeller itself into account. According to Watson (1998) it can be written as

$$
\eta_ {\mathrm {q p c}} = 0. 8 4 - \frac {N \sqrt {\mathrm {L B P}}}{1 0 0 0 0}, \tag {7}
$$

where  $N$  is the rpm of the propeller and LBP is the length between perpendiculars (in m). Propeller efficiency is commonly substantially less than unity; usually  $60 - 80\%$  of the main engine power is transmitted to the water by the propeller (Watson, 1998). If propeller rpm cannot be determined from ship technical data and it cannot be estimated using Eq. (5), the power is predicted based on the previous version of the model (Jalkanen et al., 2009).

Finally, the total required engine power  $(P_{\mathrm{Total}})$ , taking the efficiency of the power transmission to the propeller into account, is described by

$$
P _ {\text {T o t a l}} = \frac {P _ {\text {P r o p e l}}}{\eta_ {\mathrm {q p c}}} \tag {8}
$$

which yields the required engine power (in kW). The additional resistance because of waves is calculated according to Townsin et al. (1993) and is identical to the previous version of the STEAM (Jalkanen et al., 2009).

In the internal ship database sufficient propeller details exist for about  $60\%$  of the cases, which facilitate the evaluation of the quasi propulsive constant. In the remaining cases, the previous method (Jalkanen et al., 2009) of engine power estimation for the main engines has to be used, which requires that the design speed of the ship has to be known. In approximately five percent of the ship database entries both the propeller rpm and vessel design speed are missing. In such cases, the emission predictions are relatively less accurate, as average values specific to this ship type have to be used as a substitute for the missing ship data values. The values larger than the total installed engine power are not allowed for by the model.

# 3.1 The operating characteristics of engines

In addition to the prediction of the instantaneous main engine power also auxiliary engine power is needed to describe the total exhaust emissions. Furthermore, variable engine loads will have a significant impact on fuel consumption and emissions of CO and PM. Each of these features will be discussed in consecutive chapters, starting from load determination and its impact on fuel consumption.

# 3.1.1 The load balancing for multi-engine installations

A load balancing scheme for multi-engine installations has also been implemented in the STEAM2 model. Load balancing is a crucial issue for the proper functioning of multi-engine installations. Engines that are not needed at a specific moment can be turned off, which saves fuel and ensures that the remaining engines are operated with an optimal engine load. To simulate this operation of the engines, the STEAM2 model determines the minimum number of engines, which need to be in operation to overcome the predicted resistance of the ship.

Clearly, the engine load, i.e. ratio of currently used power and installed power, affects fuel consumption and the emissions of PM and CO. While it is straightforward to estimate an engine load of a single engine ship, if required power is known, this estimation is more challenging for multi-engine setups. The model estimates the engine power needed to achieve the ship speed as reported in the AIS position reports, using a resistance calculation by the Hollenbach method. Total instantaneous engine power is compared against the capabilities of each engine.

The model assumes all main engines to be identical, a minimum number of engines are assumed to be used, and the load values are assumed to be less or equal than  $85\%$ . The latter assumption is needed, as engine loads larger than  $85\%$  are commonly avoided. If this load value would be exceeded, an additional engine is assumed to be taken online and the load is balanced among the operational engines. For example, let us consider a ship with four installed engines, each with a power of  $6\mathrm{MW}$ , and an instantaneous power requirement of  $11\mathrm{MW}$ . The minimum requirement to obtain  $11\mathrm{MW}$  would require operation of two engines at  $91.7\%$  load level, which is not feasible. The modeling assumption is therefore that three engines would be used instead, each with a load of  $61.1\%$ .

For all multi-engine setups, all engines are assumed to be identical. Thus the number of operational engines ( $n_{\mathrm{OE}}$ ) can be calculated from

$$
n _ {\mathrm {O E}} = \frac {P _ {\text {T o t a l}}}{P _ {\mathrm {E}}} + 1 \tag {9}
$$

where  $P_{\mathrm{Total}}$  is the total instantaneous power of the engines, determined from Eq. (8) and  $P_{\mathrm{E}}$  is the maximum continuous rating of a single installed engine.  $n_{\mathrm{OE}}$  is rounded down to integer. For all setups, the engine load (EL) is then determined from

$$
\mathrm {E L} = \frac {P _ {\text {T o t a l}}}{P _ {\mathrm {E}} n _ {\mathrm {E}}} \tag {10}
$$

where  $n_{\mathrm{E}}$  is the number of installed identical engines. A limitation of this approach is that the model treats all main engines as equal and neglects engine setups, for which one engine in a pair is larger than another. For instance, in case of four engines with two pairs of identical engines, a so-called

2+2 setup, the accuracy of the predictions of fuel consumption and emissions will deteriorate. Passenger classed vessels and ships with more than one propeller are required to have at least two engines operational at all times due vessel safety rules. Load balancing is applied to both main and auxiliary engines, but in case of diesel-electric engine setups, all the power commonly required for ship systems and propulsion is taken from the main engines. In such cases, the main engines are operated to generate electricity, and electrical motors are used as propulsion. Diesel engines do not run the ship directly in these cases and no auxiliary engines are used.

# 3.1.2 The evaluation of auxiliary power

The previous model estimated auxiliary power using ship type classification and three different operation modes for the ship. In STEAM2, auxiliary engine usage is evaluated as in previous model, but with the following modifications: passenger class vessels (cruise ships, RoRo/passenger and yacht) use a base value of  $750\mathrm{kW}$  of auxiliary engine power for all operating modes, but an additional requirement of  $3\mathrm{kW}$  is added for each cabin. This emulates the additional need for electricity required by air conditioning, hot water and other electrical installations inside the cabins. For reefers and containerships, similar assumptions are applied. A base value of  $750\mathrm{kW}$  is used while cruising,  $1000\mathrm{kW}$  during hoteling and  $1250\mathrm{kW}$  while maneuvering. In addition to these values, each refrigerated Twenty-foot Equivalent Unit (TEU, standardized cargo container) consumes approximately  $4\mathrm{kW}$  of electricity to maintain the containers in a constant temperature. Clearly, the actual power requirement of the container depends on the temperature difference between the environment and the container (Wild, 2009).

All other vessel classes use 750, 1000 and  $1250\mathrm{kW}$  for cruising, hoteling and maneuvering, respectively. With these modifications, STEAM2 can distinguish between large and small vessels of the same ship type. However, in all cases, the installed auxiliary engine power is used as an upper limit for the predicted auxiliary engine power (in cases, for which the computed auxiliary power would exceed the installed auxiliary power). Boiler energy usage is included in the estimates of auxiliary engine power; these have not been modeled explicitly due to the lack of data.

# 3.1.3 The impact of engine load on specific fuel oil consumption

Instantaneous total fuel consumption is influenced by many independent factors. Fuel consumption of main engines used in propulsion is commonly estimated in available literature as a product of the constant specific fuel oil consumption (SFOC) and instantaneous engine power, which results in a linear relationship between fuel consumption and engine power. Ideally, all power systems that require fuel to operate should be modeled separately, such as the main engines for

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/e04ee8f3-21c7-4e13-b98f-bb26187f54a1/88cea0a72f23fa3ec22c064c95a33b12e4929c7b151f8fa80fab4fbf8cd996db.jpg)  
Fig. 2. The relative specific fuel-oil consumption (SFOC) as a function of the relative engine load, based on the data of three engine manufacturers: Wärtsilä, Caterpillar and MAN. The data of Caterpillar is based on three different SFOC-curves of small four-stroke engines (see Appendix B, Table B3), and the data of MAN is based on large two-stroke engines (see Appendix B, Table B2). Wärtsilä data for “46” engine family was used (see Appendix B, Table B1). A more detailed description of the data is presented in the main text and in Appendix B.

propulsion, the auxiliary engines for power generation and the boilers for heat generation. However, in practice a separate modeling of all of these is currently not feasible.

The relative SFOC curve provided by the engine manufacturer Wärtsilä for a medium sized four-stroke engine is presented in Fig. 2. Two other relative SFOC-curves by other manufacturers are also presented; each of these corresponds to selected engine specifications (Caterpillar, 2010; Man B&W, 2009). The engines by MAN considered here are large two-stroke models, whereas the Caterpillar engines are relatively small four-stroke models.

For all three curves presented, the SFOC is a non-linear function of engine load, and this function has a minimum at a specific engine load. According to the data of Caterpillar, MAN and Wärtsilä, the minimum of EL is located approximately at the relative engine load of 70, 75 and  $80\%$ , respectively. Minimizing fuel oil consumption therefore requires engine loads approximately from 70 to  $80\%$ , which represents the optimum regime in terms of both consumption and performance. There is an approximately parabolic dependency between the SFOC and the engine load.

In the STEAM2 model, we have assumed a parabolic function for all engines. Using regression analysis of the comprehensive SFOC-measurement data from Wärtsilä, we derived a second degree polynomial equation for the relative SFOC:

$$
\mathrm {S F O C} _ {\text {R e l a t i v e}} = 0. 4 5 5 \mathrm {E L} ^ {2} - 0. 7 1 \mathrm {E L} + 1. 2 8 \tag {11}
$$

where EL is the engine load ranging from 0 to 1. The absolute fuel consumption is estimated from

$$
\mathrm {S F O C} = \mathrm {S F O C} _ {\text {R e l a t i v e}} \mathrm {S F O C} _ {\text {b a s e}} \tag {12}
$$

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/e04ee8f3-21c7-4e13-b98f-bb26187f54a1/f66bfa1c3bf0ff53ac015ff4cd3e1431ea69790e07c08723eebae90565df7b26.jpg)  
Fig. 3. The emission factor of the total PM, and for its chemical constituents as a function of fuel sulphur content (mass-based percentage), based on the data from the second IMO GHG study (Buhaug et al., 2009). Lines indicate the PM component emission factors in STEAM2. The emission factors of the total PM,  $\mathrm{SO}_4$  and  $\mathrm{H}_2\mathrm{O}$  are linearly dependent on the fuel sulphur content. The scale used for total PM,  $\mathrm{SO}_4$  and associated  $\mathrm{H}_2\mathrm{O}$  is different (left-hand axis) from the scale used for EC, OC and ash (right-hand axis).

where  $\mathrm{SFOC_{base}}$  is the so-called base value for SFOC that is a constant for each engine. According to second IMO greenhouse gas report (Buhaug et al., 2009), a lower consumption is assigned for new engines, describing the technical development and better efficiency of modern engines. The base value is also influenced by engine stroke type and power. We use primarily engine-model specific base values of SFOC from the engine manufacturers. If such a value is not available, the value is evaluated (taking the above mentioned factors into account) according to the IMO GHG2 report (Buhaug et al., 2009).

For simplicity, it has been assumed that engine load and SFOC-dependence from Eqs. (11) and (12) applies to all engines. For turbine machinery,  $\mathrm{SFOC_{base}}$  of  $260\mathrm{g}\mathrm{kWh}^{-1}$  is used. Auxiliary engine  $\mathrm{SFOC_{base}}$  was set to  $220\mathrm{g}\mathrm{kWh}^{-1}$  and the same load dependency was applied. In case of diesel-electric engine setups, the power normally generated using auxiliary engines was added to main engine power and engine loads were determined accordingly. However, diesel engines with common rail fuel injection technology may show a different behavior compared to the one described above. This should be taken into account in the future, as the fraction of common rail diesel engines is expected to increase.

# 3.2 The exhaust emissions

# 3.2.1 The emissions as a function of engine load

In STEAM2, PM is divided into Elementary Carbon (EC), Organic Carbon (OC), Ash, Sulphate  $(\mathrm{SO}_4)$  and associated

water  $(\mathrm{H}_2\mathrm{O})$ . The carbon monoxide (CO) emissions are also modelled. Clearly, the main aim is that the model would provide accurate emission factors for the all pollutants, including all the chemical components of PM, for all values of the fuel sulphur content throughout whole operating load range. The evaluation of the influence of engine load is needed especially for an accurate description of emissions of PM, CO and  $\mathrm{CO}_{2}$ . All emissions have therefore been assumed to be dependent on engine load, except for those of  $\mathrm{NO}_{\mathrm{x}}$ , which are only slightly dependent.

Emissions of particulate matter and  $\mathrm{SO}_{\mathrm{x}}$  depend on the fuel consumption of the ship, whereas emissions of  $\mathrm{NO}_{\mathrm{x}}$  mainly depend on the temperature and the duration of the combustion cycle. Emissions of carbon monoxide depend not only on engine load and engine power, but also on the gradient of engine power. Acceleration of ship results in incomplete combustion of fuel and relatively higher emissions of CO. As discussed previously, fuel consumption is dependent on engine load; the emissions of several pollutants have the same dependency. Several authors have reported experimental results on the composition of particulate matter as a function of engine load (Agrawal et al., 2008a, b, 2010; Petzold et al., 2008; Moldanova et al., 2009; Sarvi et al., 2008a) and sulphur content (Sarvi et al., 2008b; Buhaug et al., 2009). These datasets represent cases where measurements over the whole load range with several types of fuel with variable sulphur content were available.

Additionally, load balancing facilitates the estimation of effectiveness of slow steaming. In these cases the ship

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/e04ee8f3-21c7-4e13-b98f-bb26187f54a1/64241215b5df6df9ca53dda3b2b91a10048cb656b2265ef3f841dbd0efc0334a.jpg)  
Fig. 4. The predictions of the STEAM2 model for total PM emission factor (legend, in units of  $\mathrm{gKWh}^{-1}$ ) as a function of engine load and fuel sulphur content.

decreases its speed to save fuel. However, if the engine is run outside its normal operating load range, emissions and fuel consumption will increase, since the engines are not commonly optimized to run on low loads for prolonged periods. This is correct for single engine installations, but for multi-engine installations, unnecessary engines can be turned off. This effect is taken into account by the model.

# 3.2.2 The emissions of PM in terms of fuel sulphur content and engine load

The sulphur content of the fuel has a crucial influence on the PM emissions. The dependency of PM emission factor on fuel sulphur content was modelled according to Buhaug et al. (2009), as presented in Fig. 3. The emission factors of the total PM,  $\mathrm{SO}_4$  and associated  $\mathrm{H}_2\mathrm{O}$  (i.e.  $\mathrm{H}_2\mathrm{O}$  attached to sulphate) are assumed to be linearly dependent on the fuel sulphur content, whereas the emission factors of EC, OC and ash are independent of this factor in STEAM2. The emissions of PM could therefore not be eradicated totally, even if sulphur would be completely eliminated from ship fuels (Winnes and Fridell, 2010b; Buhaug et al., 2009). The measured total mass of particulate matter as defined here includes also the associated  $\mathrm{H}_2\mathrm{O}$ ; the amount of which may substantially vary according to the experimental set-up and conditions during the exhaust measurements.

Applying linear regression analysis to the data presented in (based on data from Buhaug et al., 2009) yields the following emission factor dependencies:

$$
\mathrm {E F} _ {\mathrm {S O} _ {4}} = 0. 3 1 2 S \tag {13a}
$$

$$
\mathrm {E F} _ {\mathrm {H} _ {2} \mathrm {O}} = 0. 2 4 4 S \tag {13b}
$$

and

$$
\mathrm {O C} _ {\mathrm {E L}} = \left\{ \begin{array}{l} 3. 3 3 3, \mathrm {E L} <   0. 1 5 \\ \frac {a}{1 + b e ^ {- c _ {\mathrm {E L}}}}, \mathrm {E L} \geq 0. 1 5 \end{array} \right. \tag {13c}
$$

$$
\begin{array}{l} \mathrm {E F} _ {\mathrm {E C}} = 0. 0 8 \mathrm {g} \mathrm {k W h} ^ {- 1}, \mathrm {E F} _ {\mathrm {O C}} = 0. 2 \mathrm {g} \mathrm {k W h} ^ {- 1}, \\ \mathrm {E F} _ {\text {A s h}} = 0. 0 6 \mathrm {g} \mathrm {k W h} ^ {- 1} \tag {13d} \\ \end{array}
$$

where  $S$  is the fuel sulphur content in percentages and the emission coefficients for EC, OC and ash have been assumed to be independent of the sulphur content, but for OC an additional dependency on engine load is used. In Eq. (13c), the dimensionless constants are  $a = 1.024$ ,  $b = -47.660$  and  $c = 32.547$ , respectively. The  $\mathrm{EF_{OC}}$  emission as a function of engine load was fitted to the results of Agrawal et al. (2008a, b) and Petzold et al. (2010). A cut-off value at engine load of  $15\%$  was applied which constrains the OC emission factor to a constant value at very low engine loads. The amount of ash may change between different fuel grades, but this effect is neglected for now. The total PM emission factor (in  $\mathrm{g~kWh^{-1}}$ ) is assumed to be the sum of the above mentioned emission factors

$$
\begin{array}{l} \mathrm {E F} _ {\mathrm {P M}} = \mathrm {S F O C} _ {\text {R e l a t i v e}} \left(\mathrm {E F} _ {\mathrm {S O} _ {4}} + \mathrm {E F} _ {\mathrm {H} _ {2} \mathrm {O}} + \mathrm {E F} _ {\mathrm {O C}} \mathrm {O C} _ {\mathrm {E L}} \right. \\ + \mathrm {E F} _ {\mathrm {E C}} + \mathrm {E F} _ {\mathrm {A s h}}) \tag {14} \\ \end{array}
$$

In STEAM2, the PM emissions  $\left[\mathrm{g}\mathrm{kWh}^{-1}\right]$  are evaluated as the product of specific fuel-oil consumption and emission factors, where the relative SFOC is computed using Eq. (11). The variations of this emission factor have been graphically illustrated in Fig. 4. According to Lack et al. (2009) a clear correlation between fuel sulphur content and the emissions of organic carbon exists. It is not clear whether this is because of the changes in the type and consumption of lubricating oil, but this feature is not currently modeled by STEAM2, which assumes that OC emissions are independent of fuel sulphur content.

The emissions of the chemical components of PM have been reported to change as a function of engine load (Agrawal et al., 2008a, b, 2010); this has been taken into account in the modeling of STEAM2. In STEAM2, the variation of the PM emission factor for different components has

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/e04ee8f3-21c7-4e13-b98f-bb26187f54a1/85366156fdb08bd3bff224320a60d3251301d68349cdd62d683660720fc1681d.jpg)  
Fig. 5. Organic Carbon emission factor (in  $\mathrm{gKWh^{-1}}$ ) as a function of engine load. Solid line indicates STEAM2, symbols represent experimental data points.

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/e04ee8f3-21c7-4e13-b98f-bb26187f54a1/9b325873991b1bbda9c698a3c2ed931ea5859579242d77f7add0deb01890e3a5.jpg)  
Fig. 6. The base value of CO-emission as a function of relative engine load. The measurements of Agrawal, Moldanova and Sarvi have been shown, and the CO-base emission factor curve is based on Sarvi (2008a). The emissions of CO are also influenced by rapid changes of relative engine load.

been modeled based on the variation of SFOC. An additional dependency for OC is used as given in Eq. (13c) for which results from Agrawal et al. (2008a, b, 2010) and Petzold et al. (2010) were used and fitted to a mathematical form (see Fig. 5). The emissions of all PM components are modeled based on the variations of SFOC and instantaneous power, and in addition the emission factors of sulphate and associated water are dependent on the fuel sulphur content.

# 3.2.3 The emissions of carbon monoxide

Assuming perfect combustion conditions, the amount of emitted  $\mathrm{CO}_{2}$  can be estimated in a straightforward manner from the amount of fuel burned. However, the CO emissions are substantially dependent on engine load. The data based on three experimental studies and the modeled dependency of the base emission factor of CO as a function of engine load has been presented in Fig. 6. The CO base emission factor as described by Sarvi (2008a) has been adopted in STEAM2,

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/e04ee8f3-21c7-4e13-b98f-bb26187f54a1/0fa32499638cd06daa53b8e2e0ac5e667f2b5fc9b9fb8c3ad802ade33b37e652.jpg)  
Fig. 7. The predictions of the STEAM and STEAM2 models and the corresponding measured engine power. The data has been measured for a  $60000\mathrm{t}$  RoPax vessel that was sailing in the Baltic Sea within and near the archipelago surrounding the city of Stockholm in April 2008.

as it is based on a systematic inclusion of a wide range of engine loads.

During normal engine operation, when engine load ranges from  $75\%$  to full load, the base emission factor of CO is small according to Sarvi (2008a). However, using the engine at low engine loads will significantly increase the CO emission factor.

A rapid change of engine load has been observed (Cooper, 2001, 2003) to result in increased emissions of carbon monoxide. This is usually the case, when the ship is accelerating or actively decelerating (braking). We have therefore modified the modeled curve (as presented above) with an additional scaling term, that amplifies the CO emission factor, if the ship is accelerating.

Using this scaling factor called Acceleration Based Component (ABC), the CO emissions takes the following form:

$$
\mathrm {E F} _ {\mathrm {C O}} = \mathrm {C O} _ {\text {b a s e}} \mathrm {A B C} \tag {15}
$$

where

$$
\mathrm {A B C} = \max  \left\{\alpha \frac {| \Delta v |}{\Delta t}, 1 \right\} \tag {16}
$$

where  $\Delta v$  is the rate of change of the ship's speed  $(\mathrm{ms}^{-1})$  during a time interval of  $\Delta t$  between two consecutive position reports (in seconds) and  $\alpha$  is a dimensionless empirical factor. For simplicity  $\alpha$  has been assumed to be the same for all ships and has a value of 582, given by regression analysis. The ABC factor is simply unity if there is no significant acceleration and otherwise larger.

Strictly speaking the ABC value is ship-dependent. The parameter  $\alpha$  is certainly a function of the total mass of the vessel and very likely also a function of hull shape, but the determination of its exact form requires further study. More experimental data would be needed to model these relationships in more detail. The modeling above cannot distinguish

between natural deceleration (engines stopped) and active braking (ship using its engines to decelerate). The CO emissions might therefore be over-predicted in case of natural deceleration.

# 4 Model evaluation and example numerical results

In this chapter, we (i) compare the predictions of the STEAM2 model with those of the original model, (ii) evaluate the extended model against available experimental data, and (iii) present selected numerical results.

# 4.1 Evaluation and inter-comparison of the predictions of STEAM and STEAM2 for engine power and fuel consumption

An example comparison between the predictions on main engine power of the two model versions is presented in Fig. 7. The engine power data has been collected in this study at the engine room of a large RoPax (Roll On - Roll Off cargo/Passenger) vessel using its own data logging systems. The presented voyage was done in an archipelago area near Stockholm, Sweden, and in the vicinity of this archipelago, in April 2008. We have used this specific dataset, as it was the only one available in the Baltic sea region. Measured power profiles, such as the one presented in Fig. 7, are difficult to obtain, as only a limited number of vessels have internal equipment suitable to collect this data.

The basic statistical measures of this comparison are presented in Table 1. The predicted main engine powers of both models are in a fairly good agreement with the measured values. The predictions of the STEAM2 model are moderately better than those of STEAM in terms of the mean absolute error, and vice versa in terms of the mean error. STEAM2 slightly under-estimated the engine power. There

Table 1. Statistical measures for the power predictions of STEAM and STEAM2.  $P$  is the predicted power,  ${P}_{\mathrm{M}}$  is the measured power and the number of observations  $n = {729}$  . Errors in percent in the table have been computed with respect to the mean values of the measurements.  

<table><tr><td></td><td>Formula</td><td>STEAM2</td><td>STEAM</td><td>Measured (M)</td></tr><tr><td>Mean value</td><td>1/nΣP</td><td>11 190 kW</td><td>12 130 kW</td><td>12 338 kW</td></tr><tr><td>Mean Error</td><td>1/n(P - PM)</td><td>-1148 kW (-9.3%)</td><td>-206 kW (-1.7%)</td><td>-</td></tr><tr><td>Mean Absolute Error</td><td>1/n(|P - PM|)</td><td>1845 kW (15%)</td><td>2267 kW (18.4%)</td><td>-</td></tr></table>

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/e04ee8f3-21c7-4e13-b98f-bb26187f54a1/59eb664f38e6f2afdd10323026b816a864a75fb69ec6783b7619d07718b29c94.jpg)  
Total fuel consumption

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/e04ee8f3-21c7-4e13-b98f-bb26187f54a1/3d6339032f2c6fc76a6d9d9245fc210f4571f9d8f7f96e554788104d46f70cbf.jpg)  
Fuel consumption of auxiliary engines and boilers  
Fig. 8. (a)-(b): the monthly average fuel consumption of a RoPax ship in 2007, as reported by the ship owner, and predicted by the two model versions. The total fuel consumption is presented in the upper panel, and the fuel consumption of auxiliary engines and boilers in the lower panel.

are physical factors that have been neglected in both models, such as the influences of the sea ice on the kinetic energy of the ship, the squat effect and the sea currents. Both models would therefore be expected to under-predict the required engine power in most cases, except in a case with calm sea with no ice and a strong sea current coming from the stern.

Largest differences between the two model versions are found in the beginning and near the end of the voyage; in the latter stage the original version of STEAM clearly overpredicts the engine power. The Hollenbach method used in

STEAM2 results in a steeper power curve compared with the corresponding method in STEAM, i.e. a relatively lower resistance for low ship speeds and a higher one for high speeds. The most substantial differences between the two models in case of the presented data are therefore expected for low ship speeds. The reported and predicted fuel consumption of a RoPax ship in 2007 has been presented in Fig. 8a-b. The STEAM2 model predicts the total fuel consumption fairly accurately and slightly over-predicts the fuel consumption of auxiliary engines and boilers. The older model version

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/e04ee8f3-21c7-4e13-b98f-bb26187f54a1/bd1aa99a506ab8c103fce4637391d5fb48b65f779feb1b4e51e835aecc221a36.jpg)  
Fig. 9. The reported and predicted total fuel consumption for five RoPax vessels from January to November in 2007. The vessel RoPax 4 is the same ship, the data of which has been presented in Fig. 7a-b.

substantially over-predicts the latter consumption. A similar comparison for five RoPax-ships is presented in Table 3. No substantial differences are found in the performance of the two model versions.

# 4.2 Evaluation of the modelling of load balancing in STEAM2

The STEAM2 model determines the number of engines, which need to be operated to overcome the predicted resistance of the ship, and the engine load of all running engines. We have evaluated the performance of this sub-module, by using the data from the cruise presented above (cf. Fig. 7).

There were four identical main engines in the vessel considered. The observed and predicted engine loads during the test cruise are presented in Fig. 11a-d. The overall accuracy of predicted engine loads is fairly good or good for most of the time in the cases presented. However, there is some inaccuracy in the initial stages of the voyage, and for the fourth predicted engine (i.e. the one used only for very limited time periods).

# 4.3 Evaluation of the PM emission factors

The emission factor predictions by STEAM2 are compared with measurements available from literature in Fig. 11a–d. The engine loads and fuel sulphur contents in these studies are as follows:  $85\%$  and  $2.85\%$  (Agrawal et al., 2008b),  $84\%$  and  $1.90\%$  (Moldanova et al., 2009),  $85\%$  and  $2.21\%$  (Petzold et al., 2008), and  $57\%$  and  $3.01\%$  (Murphy et al., 2009). For simplicity, these studies are in the following referred to as AGR, MOL, PET and MUR. The engine load is within the commonly used operation range for the three first-mentioned studies, but it was substantially lower in MUR. The sulphur content of fuels varies from 1.9 to  $3.0\%$ .

For a substantial fraction of these predictions, STEAM2 is in agreement with the measurements; the agreement is best in case of AGR. However, there are also significant differences.

The most significant differences are found in comparison with the data by MOL, especially for OC and  $\mathrm{SO}_4$ . The predicted sulphate emission factor is approximately three times larger than the measured value. According to MOL, the measured low sulphur conversion to sulphate may be a result of the relatively smaller amounts of V and Ni in the fuel, compared with, e.g. AGR. The catalytic properties of Ni and V enhance the sulphur conversion to sulphate.

According to Petzold et al. (2010), the conversion efficiency of fuel sulphur to particulate sulphate is linearly increasing from 1 to  $5\%$  with increasing engine load (such a dependency is not included in STEAM2 yet). A detailed investigation of the complete data set of Petzold et al. (2010) using STEAM2 reveals an increasing difference in S to particulate  $\mathrm{SO}_4$  conversion with decreasing engine loads. This could be one of the reasons for the deviations of predictions and data in case of MUR, due to the low engine load. Furthermore, MUR reports airborne measurements of an aged ship exhaust plume, whereas the measurements of MOL were made for a diluted and cooled sample of fresh exhaust.

In case of MUR and AGR, the ash emission factor was computed from the ash content of the fuel, whereas MOL and PET report directly measured values of ash. These ash emission factors are therefore not directly comparable with each other, and the MUR and AGR ash emission values are strictly speaking not comparable with the STEAM2 predictions. There may be processes during fuel combustion, which lead to changes in the amount of emitted ash. MOL reports the highest ash emissions, although the ash content of the fuel used by MOL is the lowest. In comparison with PET, the STEAM2 ash emission factors are in a good agreement. The ash emissions in principle depend on the ash content of the fuel, but this is not taken into account in the model. However, one cannot conclude based on the above comparison of predictions and data that this would be a significant impact. In regional scale studies of ship emissions, fuel sulphur content of each vessel is not known and assumptions have to be

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/e04ee8f3-21c7-4e13-b98f-bb26187f54a1/bc6e5ecff7085abc0c2a3e17565ab78bc081039ce0a42a97ceca7a60e8f9451e.jpg)  
Fig. 10. (a)-(d): predicted and observed engine loads of four identical main engines in a large RoPax ship. The time scale for all plots (a)-(d) is the same, presented in panel (d).  $\mathrm{ME}_x$ ,  $x = 1,2,3,4$ , are the four main engines. "Estimate" refers to the prediction of STEAM2. The numbering of the main engines in the model has no influence on the engine load predictions; for instance, in panel (b) the curves ME2 (estimate) and ME3 (observed) are directly comparable.

made. For studies in  $\mathrm{SO}_{\mathrm{x}}$  Emission Control Areas maximum allowable sulphur content is used, which in some cases can deviate significantly from reality. This is the case if a vessel is voluntarily using fuel with very low sulphur content. However, the default sulphur content used in STEAM2 and resulting  $\mathrm{SO}_{\mathrm{x}}$  emissions seems to be in reasonable agreement with experiments (Berg et al., 2011).

The water content of PM in these four datasets varies significantly. This can be due to differences in the experimental setups, sampling conditions and reporting. Water and organic compounds may condense on particulate surfaces after fuel combustion. Dilution and cooling of the PM sample to a lower concentration and temperature have an effect on the amount of condensed water and organic carbon components. The amount of water is commonly calculated assuming a

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/e04ee8f3-21c7-4e13-b98f-bb26187f54a1/a9835986d3f6f2df10939274b8f906b52a6c25a18025372a7f19e795ee0c86a5.jpg)

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/e04ee8f3-21c7-4e13-b98f-bb26187f54a1/a57476d32e1d9ea3876480930906d82f953ee364d1072716bfc4fd82e88aae78.jpg)

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/e04ee8f3-21c7-4e13-b98f-bb26187f54a1/243323c22161b914822f7093f38711e1367043f2bc062eb35012d0b18b30a646.jpg)  
Fig. 11. (a)-(d): comparison of the predicted and measured emission factors for the chemical constituents of PM. The measured data has been extracted from Agrawal et al. (2008a), Moldanova et al. (2009), Petzold et al. (2008) and Murphy et al. (2009).

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/e04ee8f3-21c7-4e13-b98f-bb26187f54a1/d32d4d3bcc5379ec60b794760fe26af1a8906b4fea99339267eff6041e31918e.jpg)

constant ratio of  $\mathrm{SO}_4$  and water (Agrawal et al., 2008a, b, 2010; Petzold et al., 2008). To overcome these difficulties, a dry PM mass could be used instead; however, this would require the inclusion of aerosol condensation processes. In STEAM2, the associated water is modelled separately (according to the IMO GHG2 study), and the user has an option to exclude it.

The large variations in the experimentally determined emission factors of PM chemical components are probably caused to a large extent by the fast aerosol processes, which occur immediately, as the exhaust leaves the funnel. Significant changes in particle number concentrations, mass and composition can occur, which should be included either in the emission model or in the consecutive air quality modelling. The selection of either one of these options depends at least on the spatial scale of the modelling. In local scale air quality studies it may be more reasonable to apply the emissions as they are measured directly from the stack (or after the fastest aerosol processes have taken place). For regional scale studies, the PM emissions after some specified

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/e04ee8f3-21c7-4e13-b98f-bb26187f54a1/c0b665165ddb9306e4e1efb5b65dc43f553b468ceb9a8698a289cb5af742f2fc.jpg)  
Fig. 12. A comparison of the emission inventories by EMEP (left-hand panels) and STEAM2 (right-hand panels) for the marine regions surrounding the Danish straits in 2009. The upper and lower panels represent the predicted annual emissions for PM and CO, respectively. For EMEP, the transparent blue color indicates emission estimates lower than  $7.7\mathrm{kg}\mathrm{km}^{-2}$  and  $77\mathrm{kg}\mathrm{km}^{-2}$ , for PM and CO, respectively. Grid resolution:  $50\times 50\mathrm{km}$  for EMEP and  $1.9\times 3.4\mathrm{km}$  for STEAM2.

initial dilution would probably be most suitable, due to the relatively larger scale. Inclusion of the information on the undiluted exhaust emissions in STEAM2 would necessitate chemical component resolving, near real time measurements of PM, which are currently unavailable.

# 4.4 Predicted emissions of CO and PM in a selected marine area

The STEAM2 model can be used, e.g. for very detailed evaluations of the geographical and temporal distribution of marine emissions. As an example application of the model, a geographical distribution of CO and PM emissions from shipping has been presented in the marine regions surrounding the Danish Straits in 2009. This region has been selected as an example, as it is the most densely trafficked region in the Baltic Sea. Marine diesel engines commonly do not emit major amounts of CO during normal operation conditions; however, temporally variable engine loads can result

Table 2. Emissions from ships in the Baltic Sea during 2006-2009 according to various studies. Data from EMEP was extracted from (www.ceip.at). All values in the table are presented in units of Gg. The percentage differences of the predictions of STEAM2 compared with those of EMEP are also presented. N/A = not available.  

<table><tr><td>Area, pollutant (Data source)</td><td>2006</td><td>2007</td><td>2008</td><td>2009</td></tr><tr><td>Baltic, NOx (EMEP)</td><td>309.3</td><td>315.3</td><td>321.3</td><td>327.3</td></tr><tr><td>Baltic, NOx (STEAM)</td><td>370.0</td><td>400.0</td><td>393.0</td><td>N/A</td></tr><tr><td>Baltic, NOx (STEAM2)</td><td>335.9</td><td>369.1</td><td>377.2</td><td>359.7</td></tr><tr><td>(STEAM2-EMEP), %</td><td>+8.6</td><td>+17.1</td><td>+17.4</td><td>+9.9</td></tr><tr><td>Baltic, SOx (EMEP)</td><td>190.1</td><td>167.4</td><td>144.7</td><td>122.0</td></tr><tr><td>Baltic, SOx (STEAM)</td><td>159.0</td><td>137.0</td><td>135.0</td><td>N/A</td></tr><tr><td>Baltic, SOx (STEAM2)</td><td>144.2</td><td>131.7</td><td>131.8</td><td>124.3</td></tr><tr><td>(STEAM2-EMEP), %</td><td>-24.2</td><td>-21.3</td><td>-8.9</td><td>+1.9</td></tr><tr><td>Baltic, CO (EMEP)</td><td>36.1</td><td>37.0</td><td>37.9</td><td>38.8</td></tr><tr><td>Baltic, CO (STEAM2)</td><td>51.6</td><td>58.1</td><td>64.5</td><td>64.3</td></tr><tr><td>(STEAM2-EMEP), %</td><td>+42.9</td><td>+57.0</td><td>+70.2</td><td>+65.7</td></tr><tr><td>Baltic, PM2.5 (EMEP)</td><td>22.7</td><td>20.7</td><td>18.6</td><td>16.6</td></tr><tr><td>Baltic, PM (STEAM2)</td><td>30.5</td><td>29.6</td><td>30.0</td><td>28.3</td></tr><tr><td>(STEAM2-EMEP), %</td><td>+34.4</td><td>+43.0</td><td>+61.3</td><td>+70.5</td></tr></table>

in an incomplete combustion of fuel, and therefore significantly increase the emissions. This influence of emissions in the vicinity of major harbors is therefore clearly visible in Fig. 12. The emissions of PM are focused in the vicinity of the most congested ship routes in this region and in harbor areas of Gothenburg (SWE), Copenhagen (DK), Kiel (GER), Lubeck (GER), Rostock (GER), Sassnitz (PL) and Swinoujscie/Szczecin (PL). The images on top share the numerical scale and indicate emissions of PM (in  $\mathrm{kg~km}^{-2}$ ) according to Centre on Emission Inventories and Projections (EMEP, www.ceip.at, left) and STEAM2 (right). Emissions of CO (in  $\mathrm{kg~km}^{-2}$ ) are illustrated in the two lower images. In addition to the obvious difference in resolution, the emissions of PM and CO in STEAM2 are higher than in EMEP. Particularly, the emissions of PM and CO in the Øresund channel near Malmö/Copenhagen and also north of the island of Bornholm are significantly higher according to STEAM2, compared with the corresponding values according to EMEP.

The available ship emission inventories have used emission factors that are not dependent on the changes of vessel speed and engine load. The detailed shipping inventories using the presented modeling system have therefore resulted in a substantially different geographical distribution of ship emissions, compared with the previous available ship emission inventories. In most cases, it is not possible to compare the seasonal differences between ship emission inventories, as the temporal variation of emissions has commonly been neglected in previous studies.

A comparison of annually averaged ship emissions for the Baltic Sea by EMEP and computed using the STEAM and

STEAM2 models in 2006-2009 is presented in Table 2. The updated STEAM2 produces estimates for  $\mathrm{NO}_{\mathrm{x}}$  emissions, which are  $9.2\%$ ,  $7.7\%$  and  $4.0\%$  lower than those computed using the previous model version in 2006-2009. In case of  $\mathrm{SO}_{\mathrm{x}}$ , the corresponding differences are negative,  $-9.3\%$ ,  $-3.9\%$  and  $-2.4\%$ . These differences in case of  $\mathrm{NO}_{\mathrm{x}}$  predictions are caused mainly by the dissimilar methods used for resistance calculation, as well as the refinement of the methods for the power estimation of auxiliary engines. In case of  $\mathrm{SO}_{\mathrm{x}}$  predictions, the contribution of SFOC change is also significant. Factors that have affected  $\mathrm{SO}_{\mathrm{x}}$ , PM and  $\mathrm{CO}_{2}$  emissions include both (i) the load dependency and (ii) the inclusion of engine age, stroke type and power output on SFOC, in accordance with Buhaug et al. (2009).

Data from the EMEP can be compared with the predictions of the STEAM and STEAM2 models. According to STEAM2, the predicted levels of  $\mathrm{NO}_{\mathrm{x}}$  were  $8.6 - 17.4\%$  higher than those of EMEP in 2006-2009. For  $\mathrm{SO}_{\mathrm{x}}$  emissions, the STEAM2 predictions were  $24.2\%$ ,  $21.3\%$  and  $8.9\%$  lower than those by EMEP in 2006-2008, but  $1.9\%$  higher in 2009. The temporal trend in the EMEP data for the  $\mathrm{SO}_{\mathrm{x}}$  emissions from 2006 to 2007 exhibits a decrease that is steeper compared with that predicted by STEAM2; both inventories include the effect of SECA rules for the marine fuel sulphur content. For CO and PM, the STEAM2 predictions are higher than those of EMEP; both the annually averaged emissions and their geographical distribution are different. The inclusion of the load dependency of the emission factors (in STEAM2) results in relatively higher emissions in congested marine areas, in contrast to using a fixed emission factor that leads to linearly increasing emissions as a function of instantaneous engine power.

Uncertainties in the actual fuel sulphur content of each ship will affect the predicted  $\mathrm{SO}_{\mathrm{x}}$  and PM emissions. By default, in the Baltic Sea during 2006-2009, STEAM2 assumes a fuel sulphur content of  $1.5\%$  and  $0.5\%$  for main and auxiliary engines, respectively. The fuel sulphur content used in STEAM2 produces  $\mathrm{SO}_{\mathrm{x}}$  emissions that are in reasonable agreement with the experimental results of Berg et al. (2011). The influence of a decrease of fuel sulphur content to  $1.0\%$  and  $0.1\%$  was numerically tested in the Baltic Sea for a single year. This change emulated the situation in 2010, when sulphur content in marine fuels was lowered to  $1\%$  and vessels were required to use  $0.1\%$  sulphur fuel in harbor areas. It resulted in  $\mathrm{SO}_{\mathrm{x}}$  and PM levels, which are about  $20\%$  and  $9\%$  lower, respectively. We therefore conclude that the uncertainties of the fuel sulphur content of ships are not probably large enough to explain all the differences in the emissions of PM and  $\mathrm{SO}_{\mathrm{x}}$  between the EMEP and STEAM2 inventories. The effects of the differences in the underlying methodological assumptions are particularly important in case of the PM and CO emissions; the differences between the STEAM2 and EMEP emissions can vary between  $35 - 70\%$ , depending on the selected year.

The STEAM2 model has up to date been applied in the Baltic Sea, in the North Sea and the English Channel. The access to the AIS data has been granted by the countries in these regions. Such a data access can either be purchased from commercial providers or it can be requested from government entities that maintain AIS networks. Both of these options have to be considered, if one aims for a global AIS signal coverage. However, there are some limitations on the use of these datasets: satellite reception of AIS signals can be masked by ground level interference in some areas, and terrestrial AIS network does not cover large open sea regions.

# 5 Conclusions

The use of the AIS data facilitates an accurate mapping of the ship traffic, including the detailed instantaneous location and speed and of each vessel in the considered area. The presented model allows for the influences of a comprehensive range of relevant factors, including accurate travel routes and ship speed, engine load, fuel sulphur content, multiengine setups, abatement methods and waves. The presented model is the only method in the available literature that includes such a range of effects. The shipping routes and the temporal changes of ship speed and engine operation are included based on directly measured (AIS) values; the uncertainties associated with numerically evaluated ship routes are therefore avoided.

The relatively largest uncertainties of the model predictions presented probably arise from the use of various types of fuel (Hulskotte and Denier van der Gon, 2010); however, these uncertainties are included in all ship emission inventories. However, the fuel sulphur defaults in STEAM2 produce emissions that in agreement with experimental results of Berg et al. (2011). It is challenging to extract the detailed data regarding the fuel types used in ships in various geographical areas. However, if the data will be available on the fuel type or the sulphur content on ship level, these can readily be taken into account in the model. The model presented in this paper also allows direct comparisons of modeled instantaneous exhaust emissions with experimental stack measurements of individual ships on an unprecedentedly fine temporal and spatial resolution. It is therefore possible to evaluate the performance of the model in more detail using the data of such measurement campaigns in the future and decrease the uncertainty of ship emission inventories.

Another challenge is the scarcity of detailed composition-resolved experimental data on PM emissions. The emissions of the chemical components of PM should be analyzed at various engine loads, and using various fuels, in order to be able to more comprehensively analyze and evaluate the performance of the modeling approaches. Further research is also needed to model various environmental effects, such as the influence of sea ice and marine currents; the former has

Table A1. Fraction of draught values for different ship types to be used in estimation of propeller diameter unless it is specifically known or can be estimated with methods described in the text.  

<table><tr><td>Ship Type</td><td>Fraction of Draught</td><td>Ship Type</td><td>Fraction of draught</td></tr><tr><td>RoRo/Passenger</td><td>0.75</td><td>General Cargo</td><td>0.52</td></tr><tr><td>Cruise Ship</td><td>0.75</td><td>Icebreaker</td><td>0.5</td></tr><tr><td>RoRo Cargo</td><td>0.75</td><td>Other Ship</td><td>0.63</td></tr><tr><td>Bulk Cargo</td><td>0.46</td><td>Crude Oil Tanker</td><td>0.44</td></tr><tr><td>Container Cargo</td><td>0.62</td><td>LPG Tanker</td><td>0.53</td></tr><tr><td>Dredger</td><td>0.5</td><td>Oil Product Tanker</td><td>0.48</td></tr><tr><td>Chemical Tanker</td><td>0.5</td><td>Car Carrier</td><td>0.65</td></tr><tr><td>Fishing vessel</td><td>0.66</td><td>Tug, default</td><td>0.5</td></tr></table>

a significant impact especially in the arctic and sub-arctic regions.

In previous emission inventories of marine traffic, constant load points and fixed emission factors have commonly been used and harbor emissions have been neglected. However, in order to obtain more accurate predictions, at least the dependence of shipping emissions on the location of the shipping routes, the actual speeds and engine loads have also to be taken into account. Changes of emission factors are especially important in port areas, as the European sulphur directive (EC/2005/33) states that the fuel used in EU harbor areas must not contain more than  $0.1\%$  sulphur since the beginning of 2010. This directive will have a significant impact on the PM emissions from ships at berth, which should be taken into account by any model used in local scale modeling of harbor regions. There is an urgent need to reliably evaluate the effects of various policy options that focus on reducing the PM emissions from ships. The health and climatic influences can be substantially different for the various chemical constituents of PM; the modeling should therefore disaggregate the chemical fractions of PM emissions from ships.

The model presented can be extended for other marine regions besides the Baltic Sea, if the model input data will be available, including especially the AIS data. However, the AIS data cannot be received across extensive sea areas, unless a satellite-based AIS reception is used. A flexible international cooperation between maritime authorities would therefore be most valuable to be able to construct more accurate emission inventories on a global scale.

# Appendix A

# The values of the fraction of draught for various ship types

The values of the fraction of draught are required in propeller size estimation for multi-propeller cases, and if propeller data is unavailable. The values, which are presented in Table A1,

Table B1. Measured specific fuel-oil consumption values as a function of engine load, as reported in Wärtsilä (2007) for four-stroke engines. This set of data includes the measurements of "46" engine family, the reported power of which ranges from 5850 kW (engine code 6L46) to 18480 kW (16V46).  

<table><tr><td>Load, %</td><td>SFOC g kWh-1, 
base = 170, 
STEAM2</td><td>SFOC, g kWh-1, 
Wärtsiälä 46, 
1155 kW/cylinder</td><td>Relative 
consumption</td></tr><tr><td>10</td><td>216</td><td></td><td>1.212</td></tr><tr><td>15</td><td>210</td><td></td><td>1.182</td></tr><tr><td>25</td><td>201</td><td>204</td><td>1.130</td></tr><tr><td>30</td><td>197</td><td>199</td><td>1.107</td></tr><tr><td>35</td><td>193</td><td></td><td>1.086</td></tr><tr><td>40</td><td>190</td><td>190</td><td>1.067</td></tr><tr><td>45</td><td>187</td><td></td><td>1.051</td></tr><tr><td>50</td><td>185</td><td>183</td><td>1.037</td></tr><tr><td>55</td><td>183</td><td></td><td>1.026</td></tr><tr><td>60</td><td>181</td><td>181</td><td>1.016</td></tr><tr><td>65</td><td>180</td><td></td><td>1.009</td></tr><tr><td>70</td><td>179</td><td></td><td>1.005</td></tr><tr><td>75</td><td>178</td><td>178</td><td>1.002</td></tr><tr><td>80</td><td>178</td><td>178</td><td>1.002</td></tr><tr><td>85</td><td>179</td><td>178</td><td>1.004</td></tr><tr><td>90</td><td>179</td><td></td><td>1.008</td></tr><tr><td>95</td><td>181</td><td></td><td>1.015</td></tr><tr><td>100</td><td>182</td><td>183</td><td>1.024</td></tr></table>

Table B2. Specific fuel-oil consumption measurements as a function of engine load, extracted from MAN product guide for two-stroke engines. Data for MAN 6S90ME-C7 engine (two-stroke with fixed pitch propeller and high efficiency turbocharger) were extracted from available product specifications. Relative SFOC-values (increase of SFOC in comparison to minimum value given in product specifications) have been computed using the specified SFOC value for each engine.  

<table><tr><td colspan="2">MAN 6S80ME-C8.2
25 080 kW</td><td colspan="2">MAN 6S80MC-C8.2
25 080 kW</td><td colspan="2">MAN 6S90ME-C7
29 340 kW</td></tr><tr><td>Load, %</td><td>Rel. SFOC</td><td>Load, %</td><td>Rel. SFOC</td><td>Load, %</td><td>Rel. SFOC</td></tr><tr><td>35</td><td>1.043</td><td>35</td><td>1.041</td><td>50</td><td>1.022</td></tr><tr><td>50</td><td>1.016</td><td>50</td><td>1.016</td><td>70</td><td>1</td></tr><tr><td>65</td><td>1</td><td>65</td><td>1.002</td><td>100</td><td>1.024</td></tr><tr><td>85</td><td>1.004</td><td>85</td><td>1</td><td>-</td><td>-</td></tr><tr><td>100</td><td>1.023</td><td>100</td><td>1.016</td><td>-</td><td>-</td></tr></table>

have been estimated in this study based on the ship database, using regression analysis.

# Appendix B

# Evaluation of the relative SFOC values against engine load

Relative SFOC curve used in the model is derived from the relative consumption values in Table B1 using regression analysis.

Table B3. Specific fuel-oil consumption measurements as a function of engine load, extracted from CAT engine documentations for four-stroke engines. Relative SFOC-values have been computed using the specified SFOC value for each engine.  

<table><tr><td colspan="2">CAT 3516
1350 kW</td><td colspan="2">CAT 3508-B
1425 kW</td><td colspan="2">CAT 3516-C
2240 kW</td></tr><tr><td>Load, %</td><td>Rel. SFOC</td><td>Load, %</td><td>Rel. SFOC</td><td>Load, %</td><td>Rel. SFOC</td></tr><tr><td>16.3</td><td>1.345</td><td>18.8</td><td>1.095</td><td>14.8</td><td>1.134</td></tr><tr><td>23.1</td><td>1.261</td><td>32.8</td><td>1.051</td><td>21.1</td><td>1.075</td></tr><tr><td>32.1</td><td>1.203</td><td>54.2</td><td>1.013</td><td>27.1</td><td>1.069</td></tr><tr><td>55.1</td><td>1.090</td><td>71.0</td><td>1.000</td><td>62.7</td><td>1.000</td></tr><tr><td>91.1</td><td>1.005</td><td>88.8</td><td>1.014</td><td>81.1</td><td>1.009</td></tr><tr><td>94.4</td><td>1.044</td><td>94.7</td><td>1.071</td><td>84.8</td><td>1.080</td></tr></table>

The engines of two other prominent marine engine manufactures, Caterpillar and MAN, have been studied in the same manner, although less thoroughly, using available information from engine specifications. Relative SFOC data was not available, but using the lowest SFOC value as the base value, the following data was acquired.

Acknowledgements. We gratefully acknowledge the support of the Finnish Transport Safety Agency (TraFi) and the member states of the Marine Environment Protection Committee of the Baltic Sea (Helcom) in this work. The research leading to these results has received funding from the European Regional Development Fund, Central Baltic INTERREG IV A Programme within the project SNOOP. The publication has been partly-produced in co-operation with the BSR InnoShip project (project no #051 in the Grant Contract). The project is part-financed by the EU Baltic Sea Region Programme 2007-2013, which supports transnational cooperation in the Baltic Sea region. The research leading to these results has also received funding from the European Union's Seventh Framework Programme FP/2007-2011 within the projects MEGAPOLI, grant agreement no 212520, and TRANSPHORM, grant agreement no 243406. This publication reflects the author's views and the Managing Authority of Central Baltic INTERREG IV A programme 2007-2013 cannot be held liable for the information published by project partners. This publication cannot be taken to reflect the views of the European Union.

Edited by: V.-M. Kerminen

# References

Agrawal, H., Malloy, Q. G. J., Welch, W. A., Miller, J. W., and Cocker III, D. R.: Atmos. Environ., 42, 5504-5510, doi:10.1016/j.atmosenv.2008.02.053, 2008a.  
Agrawal, H., Welch, W. A., Miller, J. W., and Cocker, D. R.: Emission Measurements from a Crude Oil Tanker at Sea, Environ. Sci. Tech., 42, 7098-7103, doi:10.1021/es703102y, 2008b.  
Agrawal, H., Welch, W. A., Henningsen, S., Miller, J. W., and Cocker III, D. R.: Emissions from main propulsion engine on container ship at sea, J. Geophys. Res., 115, D23205, doi:10.1029/2009JD013346, 2010.

Andreae, M. O. and Gelencsér, A.: Black carbon or brown carbon? The nature of light-absorbing carbonaceous aerosols, Atmos. Chem. Phys., 6, 3131-3148, doi:10.5194/ACP-6-3131-2006, 2006.  
Berg, N., Mellqvist, J., Jalkanen, J.-P., and Balzani, J.: Ship emissions of  $\mathrm{SO}_2$  and  $\mathrm{NO}_2$ : DOAS measurements from airborne platforms, Atmos. Meas. Tech. Discuss., 4, 6273-6313, doi:10.5194/amtd-4-6273-2011, 2011.  
Buhaug, Ø., Corbett, J. J., Endresen, Ø., Eyring, V., Faber, J., Hanayama, S., Lee, D. S., Lee, D., Lindstad, H., Markowska, A. Z., Mjelde, A., Nelissen, D., Nilsen, J., Pålsson, C., Winebrake, J. J., Wu, W.-Q., and Yoshida, K.: Second IMO GHG study 2009; International Maritime Organization (IMO) London, UK, April 2009.  
Caterpillar Inc.: Caterpillar 3208 Marine engine specification sheet, 2010.  
Cooper, D. A.: Exhaust emissions from high-speed passenger ferries, Atmos. Environ., 35, 4189-4200, doi:10.1016/S1352-2310(01)00192-3, 2001.  
Cooper, D. A.: Exhaust emissions from ships at berth, Atmos. Environ., 37, 3817-3830, doi:10.1016/S1352-2310(03)00446-1, 2003.  
Corbett, J. J., Winebrake, J. J., Green, E. H., Kasibhatle, P., Eyring, V., and Lauer, A.: Mortality from ship emissions: a global Assessment, Environ. Sci. Tech., 41, 8512-8518, doi:10.1021/es071686z, 2007.  
Corbett, J. J., Lack, D. A., Winebrake, J. J., Harder, S., Silberman, J. A., and Gold, M.: Arctic shipping emissions inventories and future scenarios, Atmos. Chem. Phys., 10, 9689-9704, doi:10.5194/ACP-10-9689-2010, 2010.  
De Meyer, P., Maes, F., and Volckaert, A.: Emissions from international shipping in the Belgian part of the North Sea and the Belgian seaports, Atmos. Environ., 42, 196-206, doi:10.1016/j.atmosenv.2007.06.059, 2008.  
European Commission Directorate General Environment: Service contract on ship emissions: Assignment, Abatement and Market-Based Instruments, Task 2c, SO2 abatement, ENTEC UK Ltd, 2005.  
Eyring, V., Isaksenm, I. S. A., Berntsen, T., Collins, W. J., Corbett, J. J., Endresen, O., Grainger, R. G., Moldanova, J., Schlager, H., and Stevenson, D. S.: Transport impacts on atmosphere and climate: shipping, Atmos. Environ., 44, 4735-4771, doi:10.1016/j.atmosenv.2009.04.059, 2010.  
Fridell, E., Steen, E., and Peterson, K.: Primary particles in ship emissions, Atmos. Environ., 42, 1160-1168, doi:10.1016/j.atmosenv.2007.10.042, 2008.  
Hollenbach, K. U.: Estimating resistance and propulsion for single-screw and twin screw ships, *Ship Technology Research*, 45/2, 1998.  
Holtrop, J. and Mennen, G. G.: A statistical power prediction method, International Shipbuilding Progress, 25, 253-256, 1978.  
Holtrop, J. and Mennen, G. G.: An approximate power prediction method, International Shipbuilding Progress, 7, 166-170, 1982.  
Hulskotte, J. H. J. and Denier van der Gon, H.: Fuel consumption and associated emissions from seagoing ships at berth derived from an on-board survey, Atmos. Environ., 44, 1229-1236, doi:10.1016/j.atmosenv.2009.10.018, 2010.  
IHS Fairplay: Lombard House, 3 Princess Way, Redhill, Surrey, RH1 1UP, UK, 2011.

International Maritime Organization (IMO): Regulations for the prevention of air pollution from ships and  $\mathrm{NO}_{\mathrm{x}}$  technical code, Annex VI of the MARPOL convention 73/78, London, 1998.  
Jalkanen, J.-P., Brink, A., Kalli, J., Pettersson, H., Kukkonen, J., and Stipa, T.: A modelling system for the exhaust emissions of marine traffic and its application in the Baltic Sea area, Atmos. Chem. Phys., 9, 9209-9223, doi:10.5194/ACP-9-9209-2009, 2009.  
Kasper, A., Aufdenblatten, S., Forss, A., and Burtscher, H.: Particulate emissions from a low-speed marine diesel engine, Aerosol Sci. Tech., 41, 24-32, doi:10.1080/02786820601055392, 2007.  
Lack, D. A., Corbett, J. J., Onasch, T., Lerner, B., Massoli, P., Quinn, P. K., Bates, T. S., Covert, D. S., Coffman, D., Sierau, B., Herndon, S., Allan, J., Baynard, T., Lovejoy, E., Ravishankara, A. R., and Williams, E.: Particulate emissions from commercial shipping: Chemical, physical, and optical properties, J. Geophys. Res., 114, D00F04, doi:10.1029/2008JD011300, 2009.  
Man Diesel and Turbo, MAN B&W: 6S90ME-C7 Project guide, electronically controlled two-stroked engines, 5 Edn., MAN Diesel, Teglholmsgade 41, DK-2450 Copenhagen, Denmark, 2009.  
Matthias, V., Bewersdorff, I., Aulinger, A., and Quante, M.: The Contribution of Ship Emissions to Air Pollution in the North Sea Regions, Environ. Pollut., 158, 2241-2250, doi:10.1016/j.envpol.2010.02.013, 2010.  
Matulja, D. and Dejhalla, R.: A Comparison of a ship hull resistance determined by different methods, Eng. Rev., 27, 13-24, 2007.  
Moldanova, J., Fridell, E., Popovicheva, O., Demirdjian, B., Tishkova, V., Faccinotto, A., and Focsa, C.: Characterisation of particulate matter and gaseous emissions from a large ship diesel engine, Atmos. Environ., 43, 2632-2641, doi:10.1016/j.atmosenv.2009.02.008, 2009.  
Murphy, S. M., Agrawal, H., Sorooshian, A., Padro, L. T., Gates, H., Hersey, S., Welch, W. A., Jung, H., Miller, J. W., Cocker III, D. R., Nenes, A., Jonsson, H. H., Flagan, R. C., and Seinfeld, J. H.: Comprehensive simultaneous shipboard and airborne characterization of exhaust from a modern container ship at sea, Environ. Sci. Technol., 43, 4626-4640, doi:10.1021/es802413j, 2009.  
Paxian, A., Eyring, V., Beer, W., Sausen, R., and Wright, C.: Present-Day and Future Global Bottom-Up Ship Emission Inventories Including Polar Routes, Environ. Sci. Tech., 44, 1333-1339, doi:10.1021/es9022859, 2010.  
Petzold, A., Hasselbach, J., Lauer, P., Baumann, R., Franke, K., Gurk, C., Schlager, H., and Weingartner, E.: Experimental studies on particle emissions from cruising ship, their characteristic properties, transformation and atmospheric lifetime in the marine boundary layer, Atmos. Chem. Phys., 8, 2387-2403, doi:10.5194/ACP-8-2387-2008, 2008.  
Petzold, A., Weingartner, E., Hasselbach, J., Lauer, P., Kurok, C., and Fleischer, F.: Physical properties, chemical composition and cloud forming potential of particulate emissions from a marine diesel engine at various load conditions, Environ. Sci. Tech., 44, 3800-3805, doi:10.1021/es903681z, 2010.  
Sarvi, A., Fogelholm, C.-J., and Zevenhoven, R.: Emissions from large-scale medium-speed diesel engines: 1. Influence of engine operation mode and turbocharger, Fuel Proc. Tech., 89, 510-519, doi:10.1016/j.fuproc.2007.10.006, 2008a.  
Sarvi, A., Fogelholm, C.-J., and Zevenhoven, R.: Emissions from large-scale medium-speed diesel engines: 2. Influence of

fuel type and operating mode, Fuel Proc. Tech., 89, 520-527, doi:10.1016/j.fuproc.2007.10.005, 2008b.  
Schneekluth, H. and Bertram, V.: Ship Design for Efficiency and Economy, Butterworth & Heinemann, Oxford, UK, 1998.  
Schrooten, L., De Vlieger, I., Panis, L. I., Chiffi, C., and Pastori, E.: Emissions of maritime transport: A European reference system, Sci. Total Environ., 408, 318-323, doi:10.1016/j.scitotenv.2009.07.037, 2009.  
Townsin, R. L., Kwon, Y. J., Baree, M. S., and Kim, D. Y.: Estimating the influence of weather on ship performance, RINA Transactions, 135, 1993.  
Wartsila 46 Project guide, http://www.wartsila.com/en/engines/medium-speed-engines/Wartsila46, last access: 9 March 2012, 2007.

Watson, D. G. M.: Practical Ship Design, Elsevier, Oxford, UK, p. 76, p. 219, 1998.  
Watson, D. G. M. and Gilfillan, A. W.: Some ship design methods, Transactions of the Royal Institute of Naval Architects, 119, 279-289, 1976.  
Wild, Y.: Container Handbook, Vol. 3, Refrigerated containers and CA technology, Gesamtverband der Deutschen Versicherungswirtschaft e.V., Berlin, 2009.  
Winnes, H. and Fridell, E.: Emissions of  $\mathrm{NO}_{\mathrm{x}}$  and particles from Maneuvering Ships, Transport Res. D-Tr. E, 15, 204-211, doi:10.1016/j.trd.2010.02.003, 2010a.  
Winnes, H. and Fridell, E.: Particle emissions from ships: Dependence on fuel type, J. Air Waste Manage., 59, 1391-1398, doi:10.3155/1047-3289.59.12.1391, 2010b.