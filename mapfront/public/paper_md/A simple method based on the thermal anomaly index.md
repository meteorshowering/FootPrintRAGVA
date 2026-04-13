# A simple method based on the thermal anomaly index to detect industrial heat sources

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/e1da7619-a569-41e9-8814-f94c05973134/6f57f024c8782bfc79aea2516948c93eeb117d02a8732f8433e4b0002f245e51.jpg)

Haiping Xia $^{a}$ , Yunhao Chen $^{a,b,*}$ , Jinling Quan $^{c}$

$^{a}$  State Key Laboratory of Earth Surface Processes and Resource Ecology, Faculty of Geographical Science, Beijing Normal University, Beijing 100875, China  
<sup>b</sup> Beijing Advanced Innovation Center for Future Urban Design, Beijing 100044, China  
c State Key Laboratory of Resources and Environmental Information System, Institute of Geographic Sciences and Natural Resources Research, CAS, Beijing 100101, China

# ARTICLEINFO

Keywords:

Industrial heat sources

Thermal anomaly index

ASTER

# ABSTRACT

Because waste gas from industrial burning has a significant effect on urban environment, it is important to detect industrial heat sources from remote sensing data. Given existing pyrometry, it is difficult to identify small factories with low burning temperatures. In addition, existing fire detection methods (such as the contextual algorithm) are cumbersome, complex, and contain multiple thresholds to be determined. With the purpose of detecting industrial heat sources efficiently and simply, we introduced a simple method based on the thermal anomaly index (TAI) to detect industrial heat sources. This index was constructed based on Advanced Spaceborne Thermal Emission and Reflection Radiometer (ASTER) thermal infrared (TIR) data with a detectable temperature of  $400\mathrm{K}$ , which is lower than that used in most high-temperature detection methods. By confirming with the Visible Infrared Imaging Radiometer Suite (VIIRS) Nightfire product and high-resolution images, the TAI confidently detected almost all hot spots with the VIIRS Nightfire product and detected many hot spots that were undetected by the VIIRS Nightfire product. Based on six images acquired over Tangshan, we determined that  $54.52\%$  of hot spots were undetected by the VIIRS Nightfire product, while the TAI method was able to detect these hot spots. With the MODTRAN 5 radiative transfer model, we simulated the high-temperature detection ability of the TAI. Compared with the VIIRS Nightfire product, the TAI is more sensitive when detecting hot spots below  $700\mathrm{K}$ . Thus, this method can potentially detect family workshops engaged in the small-scale combustion of fuel.

# 1. Introduction

The combustion of oil and gas via fossil fuels in factories (e.g., cement factories, coking plants, and steel plants) produces carbon dioxide and other pollutants (Liu et al., 2018). A large amount of carbon dioxide has the potential to enhance global warming (Cherubini et al., 2011). The detection of industrial heat sources aids environmental monitoring and carbon flux cycle analyses (Oda and Maksyutov, 2011). Since strategies focusing on urban-industrial symbiosis aim for carbon mitigation in China (Ramaswami et al., 2017), detailed industrial locations (i.e., factories with combustion processes) will benefit for government management. Because fieldwork and manual visual interpretation are expensive and time consuming, detecting these industrial heat sources with remote sensing methods is a better choice.

However, studies on the identification and extraction of industrial heat sources via remote sensing data are still rare since most fire detection methods seldom distinguish industrial heat sources from

wildfire (Schroeder et al., 2008). Liu pioneered the identification and classification of industrial heat sources via time series from the Visible Infrared Imaging Radiometer Suite (VIIRS) Nightfire product. By combining of spatial and temporal aggregations, Liu distinguished static- and persistent industrial heat sources from ubiquitous biomass burnings (Liu et al., 2018). The Nightfire products used for object segmentation and classification in Liu's study were obtained from multispectral bands, including the visible, near-infrared (NIR), shortwave infrared (SWIR), and midwave infrared (MWIR) bands. The results of the fire products include estimated temperature, source size, and radiant heat of the subpixel heat sources, which are obtained via a Planck curve fit using the simplex optimization method (Elvidge et al., 2013). Temperatures of the thermal anomalies used for classifying industrial heat sources ranged from  $500\mathrm{K}$  to  $2500\mathrm{K}$  because detected temperatures below  $500\mathrm{K}$  had a lower confidence (Liu et al., 2018). With this Nightfire product, the identification of industrial heat sources might miss some small or cooler factories, and these small factories tend to be

family workshops, whose operating statuses cannot be traced. Therefore, a high-temperature detection method for lower detectable temperatures is required.

Pyrometry combined with remotely sensed data was proposed early by Dozier (1981) to identify the temperature of a subpixel via two thermal infrared (TIR) bands  $(3.8\mu \mathrm{m}$  thermal channel and  $11\mu \mathrm{m}$  thermal channel). This method was based on Wien's law and Planck's law, and radiance increased more rapidly in the midwave infrared channel at high temperature. Most of the following methods were also based on these two principles. In addition, there was an assumption that mixed pixels were linearly constructed by a target temperature and background temperature. Based on this assumption and the observed radiance in the two channels, the target temperature can be calculated. This method was used to detect high-temperature sources, such as steel plants, waste gas flares (Matson, 1981) and fires (Matson et al. 1987). However, the saturation temperature (i.e.,  $320\mathrm{K}$  in both Advanced Very High-resolution Radiometer (AVHRR) channels) was fixed by a sensor design that limited the estimation of fire sizes (Kaufman et al., 1989), but an increase in the saturation threshold and a stretched dynamic range for the sensor can help avoid this problem (Kennedy, 1992). Moreover, a single threshold (e.g., an empirically defined threshold value for the digital number (DN) or temperature) is inappropriate for universal application (GréGoire, 1990); therefore, multiple thresholds were used to distinguish biomass burning from clouds and hot soil (Kaufman et al., 1989). Hence, bispectral infrared detection (Matson, 1981) has developed into multispectral detection (Ricardo et al., 1995) with the purpose of eliminating as many problems as possible related to large surface heterogeneity, confusion and bias, which are produced by clouds, smoke, haze, and background emissivity. This multispectral detection method was later developed into a contextual algorithm (Flasse and Ceccato, 1996), which is self-adaptive and consistent over large areas and seasons. The contextual algorithm consists of two stages: the first is the detection of potential fire pixels, and the second is the confirmation of potential fire pixels (Flasse and Ceccato, 1996). It has been successfully used on remote sensing data, such as Moderate Resolution Imaging Spectroradiometer (MODIS) (Giglio et al., 2006, 2003) and VIIRS (Csiszar et al., 2014; Schroeder et al., 2014) data. This method uses fixed thresholds to identify potential fire pixels, while only large flaming fires can be detected with high probability (Koltunov and Ustin, 2007).

To detect small-scale fires, a nonlinear multitemporal detection method modified based on the dynamic detection model (DDM) was applied. This nonlinear DDM adopted a set of basis images combined in a nonlinear way to predict background pixel intensities, and the pixels whose observed intensities were statistically and significantly different from the predicted intensities were flagged as anomalies (Koltunov and Ustin, 2007). In addition, a multitemporal Kalman filter approach was used to detect actively burning fires and quantify their fire radiative power (FRP) because the nonlinear DDM cannot estimate the fire size (Roberts and Wooster, 2014). Although multitemporal detection inherits the advantages of a contextual algorithm and makes full use of high temporal imaging frequencies, it is still limited by costly computation and requires full-day observations (Roberts and Wooster, 2014).

To figure out the limitation of fix thresholds, dynamic thresholds were used to develop the Sentinel-3 Sea and Land Surface Temperature Radiometer (SLSTR) pre-launch active fire product (Wooster et al., 2012) and the MODIS collection 6 fire product (Giglio et al., 2016). In addition, the SWIR channel was also applied to the high-temperature detection method to replace the midinfrared channel due to the peak radiant emissions of high temperatures are at substantially shorter wavelengths (Elvidge et al., 2013). This change makes it possible for data without midinfrared channels to detect thermal anomalies and was successfully achieved in Landsat 8 (Schroeder et al., 2016) and Advanced Spaceborne Thermal Emission and Reflection Radiometer (ASTER) (Giglio et al., 2008). These modifications help to enrich the study of pyrometry and make available fire products more reliable.

However, when we aim to detect small-scale industrial heat sources, existing high-temperature detection methods are still limited, because the well-behaved method (i.e., the contextual algorithm) is cumbersome and complex (Giglio et al., 2003) and relies closely on midinfrared (Giglio et al., 2016) or short-infrared data (Elvidge et al., 2013). In addition, the most widely used data with midinfrared or short-infrared channels for fire detection have low spatial resolutions (e.g.,  $375\mathrm{m}$  (Schroeder et al., 2014),  $750\mathrm{m}$  (Elvidge et al., 2013),  $1\mathrm{km}$  (Giglio et al., 2016), and  $3\mathrm{km}$  (Roberts and Wooster, 2014)). Moreover, high-spatial resolution data, such as Landsat 8, used for the extraction of offshore platforms (Liu et al., 2016) are mostly obtained in the daytime, while small factories in China tend to operate at nighttime due to the supervision of the government. Thus, data with a high spatial resolution acquired at nighttime are ideal. Here, we use ASTER data collected at nighttime to detect hot spots for the following reasons:

(1) ASTER data have a high sensor sensitivity in the TIR region with a spatial resolution of  $90\mathrm{m}$  (Yamaguchi et al., 1998), which means that a higher brightness temperature saturation and has the potential to detect cooler or smaller hot spots;  
(2) ASTER data have five TIR channels ranging from 8.125 to  $11.65\mu \mathrm{m}$ , which make up for the short of midinfrared and SWIR channels (SWIR channels are not always available at nighttime) (Abrams, 2000; Yamaguchi et al., 1998).

With ASTER TIR data, we present a simple thermal anomaly index (TAI) for the rapid extraction of thermal anomaly information according to Wien's law and Planck's law. This index is fast and efficient in detecting hot spots, and can extract several thermal anomalies with low temperatures (i.e., approximately  $400\mathrm{K}$ ). Then, industrial heat sources are supposed to be derived from those unclassified hot spots. While industrial heat sources derived from time series data (Casadio et al., 2012; Liu et al., 2018, 2016) require a large number of images, we intend to use the VIIRS Day/Night Band (DNB) Nighttime Lights product to simplify this classification process. The reason is that the Defense Meteorological Satellite Program (DMSP) nighttime lights data have already been used for extracting gas flares (Elvidge et al., 2009, 2007) and acted as reference data to confirm the discrimination of flaring sites (Casadio et al., 2012). Although the image for a single date might miss some factories that were not operating when the image was obtained, we aim to operate this TAI to see whether it works.

# 2. Study area and data

# 2.1. Study area

Tangshan is the industrial center of the Beijing, Tianjin and Hebei province; it is located northeast of the North China Plain, with a total area of 13,472 square kilometers. With mountains to the north, and plains to the south, Tangshan has a warm, temperate, semihumid continental monsoon climate. There is an abundance of mineral resources in Tangshan, which makes the heavy industries prosperous and the leading type of industry. According to the Statistical Yearbook in 2016 (Aimin, 2016), the total industrial production generated 273.92 billion yuan, ranking first in Hebei Province. In addition, the proportion of steel, coking, cement and other high-energy-consuming industries accounted for  $37\%$  of the total industry. Moreover, the proportion of equipment manufacturing accounted for  $20\%$  of the total industry. Because the proportion of heavy industries in the entire industry is large, and the type of industry is complex, Tangshan is the representative area to be studied.

# 2.2.Data

ASTER contains separate visible and NIR (VNIR), SWIR, and TIR optical subsystems. Moreover, the ASTER TIR subsystem has five bands

in the TIR region ranging from 8.125 to  $11.65\mu \mathrm{m}$  at a  $90\mathrm{m}$  spatial resolution (Yamaguchi et al., 1998). We downloaded the AST_1 T products from https://glovis.usgs.gov/ from spring to winter. A total of six images collected at nighttime were adopted in this paper in the TIR bands.

Landsat 8 data collected on May 13, 2016 were obtained from https://glovis.usgs.gov/ as well, with a spatial resolution of  $30\mathrm{m}$  in NIR region. These data were used for removing water bodies since the nighttime ASTER data were lacking in the visible channels.

The Soumi National Polar-orbiting Partnership (SNPP) satellite launched on October 28, 2011, carries VIIRS sensor. The lowlight imaging capability of the DNB draws its heritage from the DMSP/ Operational Linescan System (OLS) visible band sensors (Baugh et al., 2013). Since the VIIRS DNB is also a calibrated sensor, it is much easier and more reliable to map temporal changes in lighting than the DMSP OLS (Baugh et al., 2013).

Here, we utilize the annual composite of the VIIRS DNB Nighttime Lights product (version 1) in 2015, acquired from https://ngdc.noaa.gov/eog/. This product includes monthly and annual composites. The annual composite product is the average annual DNB radiance, which excludes stray light. There are four average DNB radiance values. We choose the VIIRS Cloud Mask-Outlier Removed-Nighttime Lights (VCM-ORM-NTL) product, which contains average cloud-free radiance values that have undergone an outlier removal process to filter out fires and other ephemeral lights, with a background (i.e., no lights) set to zero.

High-spatial-resolution images available via Google Earth were utilized to confirm whether the selected hot spots were located in industrial area. In addition, place names of the factories via Google Earth will indicated the type of factories to see whether combustion existed.

Daily VIIRS Nightfire product V2.1 (obtained from https://ngdc.noaa.gov/eog/viirs/) was produced via an algorithm that was combined with the visible, NIR, SWIR, and MWIR (Elvidge et al., 2013). Here, we classified the results of this product into two parts: one is hot spots without FRP and fire areas (i.e., white placemarks that failed the Planck curve fit), which is termed as nonconfirmed; the other is hot spots with FRP and fire area (i.e., purple, blue, green, yellow and red place marks), which is termed as confirmed (Fig. 1).

MODIS fire products (obtained from https://ladsweb.modaps.eosdis.nasa.gov/) were produced via a contextual algorithm (Giglio et al., 2003, 2016). Here, we used MOD14A1/MYD14A1 in collection 6 for comparison with the thermal anomalies derived by the TAI. This version used dynamic thresholds instead of fixed thresholds (used in collection 5) to identify potential fire pixels, which helps identify thermal anomalies with lower temperatures or small areas (Giglio et al., 2016).

# 3. Methods

The extraction of industrial heat sources includes two stages (Fig. 2(a)). The first stage is the detection of thermal anomalies from thermal images via the TAI. The second stage is the discernment of industrial heat sources from thermal anomalies that contain wildfires and water. Clouds and hot soil were not considered here because we only selected data without clouds, and soil at nighttime would not confuse the detection results (Giglio et al., 2003; Schroeder et al., 2014). Then, we used high-resolution images from Google Earth and the VIIRS Nightfire product to verify this method (corresponding to the content in the blue box in Fig. 2(a)). The principles of these processes are shown in Fig. 2(b), and the details are referred to in the following description of the methodology.

# 3.1. Thermal anomaly index (TAI)

The TAI proposed in this paper was based on Wien's law of displacement, where the temperature of an object increases the wavelength of the peak radiant emission and shifts it to shorter wavelengths, which is similar to former methods (e.g., the contextual algorithm). This way, the radiance at shorter wavelengths increases more than that at longer wavelengths when the temperature is increasing. For a detailed illustration, we selected several factories that truly include operations with high temperatures, and we found the brightness temperatures of these factories to be quite different from those in normal areas. As shown in Fig. 3, the curves of brightness temperature for the coking plant, steel plant, cement factory and mine are irregular. In fact, there is one commonality: the brightness temperature of these thermal anomalies tends to increase in the first three thermal bands, while that in normal areas tends to increase in the last two thermal bands. For further illustration, we chose spots from residential, vegetation, soil and water body areas that do not have thermal anomalies, then counted the mean, maximum, minimum, and standard deviation values of the brightness temperature. As shown in Fig. 4, the brightness temperature of these normal spots increases approximately linearly as the wavelength increases. Hence, we decided to take advantage of the brightness temperature difference between the thermal anomalies and normal spots to create this index.

Since the TAI is derived from the brightness temperatures of the five TIR bands, conversion of the DN values for top of the atmosphere spectral radiance is required. The radiance rescaling factors provided in the metadata file are applied in Eq. (1).

$$
B _ {\lambda} = M _ {L} \cdot D N + A _ {L} \tag {1}
$$

where  $B_{\lambda}$  represents the spectral radiance at wavelength  $\lambda$  with a unit of

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/e1da7619-a569-41e9-8814-f94c05973134/12713cfe1c9d99fd2e5ad9dcc0c50ff2a1e5c50038ec9935259b00bd7a77bfcf.jpg)  
Fig. 1. Study area. The blue line encompasses the region of Jinjingji, including Beijing, Tianjin and Hebei province. (a) China's territory, (b) the study area (Tangshan); this image is obtained from the red, green, and blue bands of Landsat 8 (For interpretation of the references to colour in this figure legend, the reader is referred to the web version of this article).

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/e1da7619-a569-41e9-8814-f94c05973134/6ccd7a61df3c7ae92b6bf365d1a297e1cf37142f1f8194941135a79adc8bee02.jpg)

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/e1da7619-a569-41e9-8814-f94c05973134/ac17baea72176d4c2fba0c2625b526207337f8add2ddc3fafe7cf09af9f7ea57.jpg)  
Fig. 2. Flowchart and method details. (a) The method flowchart for the extraction of industrial heat sources; (b) the method details and decision criteria to guide the flowchart.

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/e1da7619-a569-41e9-8814-f94c05973134/816b4df08d1843e98d0f96483d9f30ba5fecb832a2169280a305191e29513fdc.jpg)

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/e1da7619-a569-41e9-8814-f94c05973134/cf22b80bceb27a609a9894766d101dc89866daa330cffad9494a5a85a1001190.jpg)  
Coking Plant

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/e1da7619-a569-41e9-8814-f94c05973134/0a743287623c0c734911f11d285fc6c134e21a21ff0d3a988c866967a6b9348a.jpg)  
Mine

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/e1da7619-a569-41e9-8814-f94c05973134/48d334489f3d11375739c035ac2cde44ebf17ce19df8b74f0e40c081862f2485.jpg)  
Steel Plant

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/e1da7619-a569-41e9-8814-f94c05973134/083bd0aedc6278419d52ea1844dcdd659d81fc8aa3715bbb9a6641c4905f59ef.jpg)  
Cement factory

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/e1da7619-a569-41e9-8814-f94c05973134/c85bfd94b9a7bf42e05121212ecae7a946a755fa135e963003ed14d7b5ce5dbb.jpg)  
Fig. 3. Brightness temperatures of the coking plant, steel plant, cement factory and mine, which definitely have existing thermal anomalies. These thermal anomalies were confirmed with the VIIRS Nightfire product, since they occurred on the same date and in the same area. These curves were derived from ASTER thermal data, with a spatial resolution of  $90\mathrm{m}$ , and one curve represents a single pixel. The orange circles indicate the hot spots' locations corresponding to the curves.

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/e1da7619-a569-41e9-8814-f94c05973134/211d93cdfe6c878d6f9f307323c6ac737d188e5591b13013d801a7859caf8277.jpg)

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/e1da7619-a569-41e9-8814-f94c05973134/160f62bc11a7e131d284dd1f9855f2ff09e2c4180eeaa95fe81f0b9090543bc6.jpg)

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/e1da7619-a569-41e9-8814-f94c05973134/21f84221e43c98e5d4b71a3e0fb2a404974e1378a39810438aaf0a250b2a6db4.jpg)

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/e1da7619-a569-41e9-8814-f94c05973134/fa95a936438569cf9fa913c6480e37b11a444f84f5ec1267c0cc3642f3a22a7c.jpg)

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/e1da7619-a569-41e9-8814-f94c05973134/f2c21b6c89ddea258b500a5294ac37592585495051e1bfba37a5eedbebb390cb.jpg)  
Fig. 4. Brightness temperatures of the residential (107 spots), vegetation (98 spots), soil (202 spots) and water body (220 spots) areas collected at night on June 2, 2017. In addition, StdDev indicates the standard deviation of the brightness temperature.

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/e1da7619-a569-41e9-8814-f94c05973134/9f4e75da77a5811391fa29f9d75747324b3bfc1b39fc9418a4430c5b59561cc4.jpg)

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/e1da7619-a569-41e9-8814-f94c05973134/a8c2702031ad9713846baa654faa829d16c748aa62fdc4f9897cd12275668642.jpg)

$W\cdot m^{-2}\cdot sr^{-1}\cdot \mu m^{-1}$ ,  $M_L$  and  $A_{L}$  represent rescaling factors from the metadata file, and DN represents the quantized and calibrated standard product pixel value.

Once the spectral radiance of the five TIR bands is generated, Planck's radiation function is employed for the brightness temperature (Dozier, 1981). The mathematical expression used in the derivation of the brightness temperature image is as follows:

$$
B _ {\lambda} (T) = \frac {C _ {1}}{\lambda^ {5} [ \exp \left(C _ {2} / \lambda T\right) - 1 ]} \tag {2}
$$

where  $B_{\lambda}(T)$  represents the Planck's function and  $C_1$  and  $C_2$  are constants  $(C_1 = 1.191\times 10^8\mathrm{W}\cdot \mu \mathrm{m}^{-4}\cdot \mathrm{Sr}^{-1}\mathrm{m}^{-2}$  and  $C_2 = 1.439\times 10^4\mu \mathrm{m}\cdot \mathrm{K})$  Then, the brightness temperature can be obtained by Eq. (3).

$$
T _ {s} = \frac {k _ {2}}{\ln \left(\frac {k _ {1}}{B _ {\lambda} (T)} + 1\right)} \tag {3}
$$

where  $T_{s}$  represents the brightness temperature in band s,  $k_{1} = C_{1} / \lambda^{5}$ , and  $k_{2} = C_{2} / \lambda$ .

Then, the TAI is introduced in Eq. (4).

$$
T A I = \frac {\operatorname* {m a x} \left(T _ {1 0} , T _ {1 1} , T _ {1 2}\right) - \operatorname* {m a x} \left(T _ {1 3} , T _ {1 4}\right)}{\operatorname* {m a x} \left(T _ {1 0} , T _ {1 1} , T _ {1 2}\right) + \operatorname* {m a x} \left(T _ {1 3} , T _ {1 4}\right)} \times 1 0 0 \tag {4}
$$

where  $T_{10}, T_{11}, T_{12}, T_{13}, T_{14}$  represent the brightness temperatures of bands 10, 11, 12, 13, and 14, respectively. This index can pinpoint thermal anomalies due to the significant increase in brightness temperature at shorter wavelengths.

# 3.2. Thermal anomalies derived from the thermal anomaly index (TAI)

As introduced in Section 3.1, the TAI has an obvious characteristic in that it can exaggerate the temperature difference between short and long TIR bands. Once there is an extreme temperature increase, which can be caused by factors such as biomass burning, the value of the TAI increases. To classify the thermal anomalies, a discriminant condition is given as

$$
T A I > 0 \text {a n d} T _ {1 3} > \text {m e a n} \left(T _ {1 3}\right) + T _ {0} \tag {5}
$$

where  $mean(T_{13})$  represents the mean value of the image brightness temperature in band 13. The reason for the choice of  $T_{13}$  is that  $T_{13}$  is less affected by atmospheric conditions than other thermal bands (i.e., band 13 has a higher atmospheric transmittance) (Jacob et al., 2004; Jimenez-Munoz and Sobrino, 2010; Mao et al., 2006) and is often used to retrieve land surface temperature (Jimenez-Munoz and Sobrino, 2007, 2010). The TAI threshold is determined based on our experience, and we set  $T_0$  as  $1\mathrm{K}$  in this paper. This threshold can be adjusted when the region is changed. The details of this selection are shown in Section 4.2.

# 3.3. Industrial heat sources derived from thermal anomalies

Industrial heat sources are always in a fixed position; therefore, they can be detected via time series fire products (Casadio et al., 2012; Liu et al., 2018, 2016). Moreover, the surface type of factories is a manmade surface, which can be derived by DMSP/OLS (L.Imhoff et al., 1997; Zhou et al., 2014). Hence, we used VIIRS DNB Nighttime Lights product to identify industrial heat sources from thermal anomalies by setting a simple threshold. Since the Nighttime Lights product applied here already filtered out fires and other ephemeral lights, we simply set the threshold to zero in case small factories were missing. That means the pixel whose nighttime light value is larger than zero is potential to be a factory. When this pixel is also detected via the TAI, it can be recorded as the industrial heat source. In addition, water pixels should be removed before we get access to the industrial heat sources.

Here, we employed Landsat 8 data to separate water pixels from the image. In addition, water bodies can be classified using the modified normalized difference water index (MNDWI) (Xu, 2006):

$$
M N D W I = \left(\rho_ {3} - \rho_ {6}\right) / \left(\rho_ {3} + \rho_ {6}\right) \tag {6}
$$

where  $\rho_{3}$ , and  $\rho_{6}$  represent the reflectance of band 3 and band 6 in the Landsat 8 data, respectively. When the value of the MNDWI is greater than zero, the pixel can be recorded as water. The reason for the

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/e1da7619-a569-41e9-8814-f94c05973134/c1917f604d2a2f8c4da1a67b4fa92405a974b9a752cfee85d335072106aae14a.jpg)

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/e1da7619-a569-41e9-8814-f94c05973134/ce280594b6cd096efbe193e49caea9fb40061850cf5036f67974d21ee0d0ea8c.jpg)

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/e1da7619-a569-41e9-8814-f94c05973134/afe5eb9cf2c067658fa32c68df551f4f90f647a6126a42345e5998c50e2c6010.jpg)

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/e1da7619-a569-41e9-8814-f94c05973134/6df102ec12de8aa0f69bca118b09c7593c6842fbcea6d741e4947c9ed2af3d58.jpg)  
Fig. 5. Three types of hot spots. (a)-(c) The first type of hot spot. (d)-(e) The second type of hot spot. (f) The third type of hot spots.

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/e1da7619-a569-41e9-8814-f94c05973134/7392361febb116a7977f5350cfd8ead0b1c1c73d46fb71e47e7b63df53cc99ff.jpg)

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/e1da7619-a569-41e9-8814-f94c05973134/df85737a7e15bcb9b3e58e5cfcf00d509a517f170f832ebb6babbbdfe23ec56c.jpg)

removing water using Landsat 8 data is that Landsat 8 covers more area than ASTER, and ASTER lacks NIR region at nighttime.

# 4. Results

# 4.1. Judgment standard

Industrial heat sources derived from ASTER data were confirmed with high-resolution images from Google Earth. For more accurate confirmation, the VIIRS Nightfire product V2.1 was used for comparison. The criteria for judging whether a hot spot was an industrial heat source are shown in Fig. 5. Here, we classify these hot spots into three types.

The first type is high-confidence industrial heat sources. This type of hot spot includes hot spots confirmed with the VIIRS Nightfire product (Fig. 5(a) and (b)) and hot spots that are evidently located in factories (Fig. 5(c)). As shown in Fig. 5(a) and (b), the hot spots are located in factories, and the hot spots derived from the VIIRS Nightfire products (the green spot and purple spot in Fig. 5(a) and (b), respectively) are also located in the same factories. Hence, we consider these hot spots, which are confirmed with both confirmed and nonconfirmed VIIRS hot spots (details in Section 2.2) are all high-confidence industrial heat sources. In addition, hot spots evidently located in factories (see Fig. 5(c)) but without any VIIRS hot spots located in the same areas are also considered high-confidence industrial heat sources.

The second type is low-confidence industrial heat sources. This type of hot spot is located next to factories but not totally located in the factories (see Fig. 5(d) and (e)). We consider these hot spots as industrial heat sources because there is a difference in coordinates between the ASTER images and Google Earth images, and we take this difference into account.

The third type is nonindustrial heat sources. This type of hot spot is located in nonindustrial regions (see Fig. 5(f)), and there are no factories next to these hot spots. We also consider this type of spot as an

incorrect hot spot.

# 4.2. Selecting the threshold

The  $\mathrm{T_0}$  threshold in Eq. (5) used to discriminate industrial heat sources from nonindustrial heat sources was difficult to define because the threshold was slightly different under various conditions. When the threshold was too high, some heat sources were missed. When the threshold was too low, some nonindustrial heat sources were extracted. Here, we set the  $\mathrm{T_0}$  threshold from 0 to  $5\mathrm{K}$  to identify the behaviors of various thresholds. As shown in Fig. 6(a), the number of derived hot spots decreases as the threshold increases. Meanwhile, the number of incorrect industrial heat sources increases as the threshold decreases (see Fig. 6(b)). To reduce the number of missing hot spots and improve the accuracy of the industrial heat source extraction, we set the threshold to  $1\mathrm{K}$ .

# 4.3. Industrial heat sources derived via the thermal anomaly index (TAI)

Following the criteria set in Section 4.1 and using the threshold selected in Section 4.2 we extracted industrial heat sources from six ASTER images. The results are shown in Table 1 and Fig. 7; while November 16, 2017, and August 25, 2016, have two images, June 2, 2017, and September 19, 2016, have one image. The mean accuracy of this method was  $85.13\%$ . The accuracy was obtained by calculating the proportion of the first and second types of hot spots in the extracted hot spots. In addition, compared with MODIS fire products, which were a combination of those via MOD14A1 and MYD14A1, the results (shown in Fig. 7) indicate that hot spots via the MODIS fire products can almost be completely detected by the TAI. Moreover, the TAI can also detect hot spots that are neglected in MODIS fire products.

In addition, this method can detect almost all industrial heat sources that are detected by the VIIRS product. Due to the different spatial resolutions of the ASTER thermal images and VIIRS Nightfire product, it

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/e1da7619-a569-41e9-8814-f94c05973134/7d4985546c17b81a8b11549b564ef363bef8cbd31c98f9cf6b5831b54c905614.jpg)  
Fig. 6. Hot spots derived via different TAI thresholds. (a) The number of derived hot spots and (b) the number of confirmed incorrect industrial heat sources (i.e., the third type of hot spot).

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/e1da7619-a569-41e9-8814-f94c05973134/0fef58d4064f9686aa48a175bdf962642158846f2914537d669a8469201e2d03.jpg)

is common that one VIIRS hot spot corresponds to multiple ASTER hot spots. In this case, we consider that the ASTER hotspots surrounding a VIIRS hotspot are all extracted correctly (see in Fig. 8(b)), although they might be in the same factory. As Fig. 8(c) shows, the number of hot spots via the VIIRS Nightfire product is less than the number of TAI-derived hot spots. There are a total of 54 hot spots (summed over four dates) via the VIIRS Nightfire product, and 53 hot spots are detected by the TAI. In addition, the hot spots derived via the TAI that are undetected by the VIIRS account for  $54.52\%$  of the confirmed industrial heat sources.

# 5. Discussion

# 5.1. Sensitivity of the thermal anomaly index (TAI)

The detection ability of the TAI is effected by complex atmospheric conditions, including the water column, absolute vertical ozone, and concentrations of  $\mathrm{CO}_{2}$ ,  $\mathrm{CO}$ , and  $\mathrm{CH}_4$ . In addition, the background temperature also has a significant effect on the TAI. The background temperature indicates the area without thermal anomalies. The total radiance of a pixel is the sum of the radiance in the hot spots and the background temperature (Dozier, 1981).

Here, we used the MODTRAN 5 radiative transfer model (Berk et al., 2005) and the spectral response function of the ASTER instrument to simulate the sensor radiance of temperature ranging from 270 to  $1300\mathrm{K}$ , with an interval of  $10\mathrm{K}$ . The pixels were assumed to be blackbody emitters, and the atmospheric parameters were obtained from the MOD07_L2 product (https://ladsweb.modaps.eosdis.nasa.gov/). Then, the theoretical thermal anomaly identification ability of the TAI was simulated, as shown in Fig. 9. This detection ability of the TAI indicates the temperature detectability of the hot spot, and the minimum area of the hot spot corresponds to the detectable temperature. The x-axis represents the minimum thermal anomaly area, and the y-axis represents the temperature of the hot spots. This curve indicates

the minimum area of the hot spot at a specified temperature when  $\mathrm{TAI} = 0$ . The hot spots above this curve are detectable via TAI, but not below. In Fig. 9(a), we assume that the background temperature is  $285\mathrm{K}$  and the thermal anomaly temperature ranges from 320 to  $1300\mathrm{K}$  with an interval of  $10\mathrm{K}$ . With the same atmospheric parameters, we determine the thermal detection under different water vapor conditions. As shown in Fig. 9(a), when the water vapor increases, the detection ability of the TAI improves. When the water column is 2000 atm-cm, the smallest detection temperature is  $430\mathrm{K}$  with a hotspot area of  $222\mathrm{m}^2$ . However, when the water column is 4000 atm-cm, the smallest detected temperature reduces to  $380\mathrm{K}$  with a hotspot area of  $241\mathrm{m}^2$  which means that high water vapor has the potential to enhance the performance of the TAI when detecting thermal anomalies.

Another factor affecting the sensitivity of the TAI is the background temperature. This factor is seldom mentioned because the detectable temperatures in existing methods are mostly greater than  $500\mathrm{K}$ . The TAI has the potential to identify temperatures below  $500\mathrm{K}$ , and the detection ability is affected by background temperatures significantly. As shown in Fig. 9(b), low background temperatures have a high thermal detection ability. A background temperature of  $270\mathrm{K}$  can detect a hot spot of  $390\mathrm{K}$ , with an area of  $243\mathrm{m}^2$ , and a background temperature of  $290\mathrm{K}$  can detect a hot spot of  $440\mathrm{K}$ , with an area of  $226\mathrm{m}^2$ . This factor has a greater impact on the detection ability of hot spots at lower temperatures and a weaker impact on hot spots at high temperatures.

# 5.2. Detection ability of the TAI compared with that of the VIIRS Nightfire product

The detection ability of the TAI was analyzed for September 19, 2016, via the MODTRAN 5 radiative transfer model, with a background temperature of  $285\mathrm{K}$  (details are the same as those in Section 5.1). Here, we collected the detection ability of VIIRS Nightfire products from (Elvidge et al., 2013), the lowest detectable temperature was

Table 1 The results of the industrial heat sources at nighttime.  

<table><tr><td>Date
(Year/Month/
Day)</td><td>Mean(T13) 
(K)</td><td>Detected
industrial heat sources</td><td>High-confidence industrial heat
sources</td><td>Low-confidence industrial heat
sources</td><td>Incorrect industrial heat
sources</td><td>Accuracy</td></tr><tr><td>2017/06/02</td><td>280.428</td><td>43</td><td>30</td><td>1</td><td>12</td><td>72.10%</td></tr><tr><td>2017/11/16</td><td>267.807</td><td>84</td><td>73</td><td>4</td><td>7</td><td>91.67%</td></tr><tr><td>2016/09/19</td><td>284.366</td><td>214</td><td>176</td><td>15</td><td>23</td><td>89.25%</td></tr><tr><td>2016/08/25</td><td>288.921</td><td>88</td><td>69</td><td>8</td><td>11</td><td>87.50%</td></tr></table>

aHigh-confidence industrial heat sources correspond to the first type of hot spot defined in Section 4.1, which includes hot spots that are both detected and undetected via the VIIRS Nightfire product; low-confidence industrial heat sources correspond to the second type of hot spot, while incorrect industrial heat sources correspond to the last type of hot spot.

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/e1da7619-a569-41e9-8814-f94c05973134/61cafc9ef1fe14c22faecf3d850b1b60d898df920b8c079c14470950fc873368.jpg)

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/e1da7619-a569-41e9-8814-f94c05973134/76dc9acca9cabfda4dc0d25a6695df1d6159a2af003be1a52a1a83572fcd7451.jpg)

Fig. 7. (a), (b), (c) and (d) show the results from June 2, 2017, November 16, 2017, September 19, 2016, and August 25, 2016, respectively.  
![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/e1da7619-a569-41e9-8814-f94c05973134/fa9cd26b8b931d281391b12b3e12b2cc47495c391bd4f1c741e21a8e47d49b7f.jpg)  
- MOD14A1 Fire Product □ASTER Image region  
VIIRS Nightfire Product Tangshan  
Hot spots from ASTER

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/e1da7619-a569-41e9-8814-f94c05973134/aa72f130c2ce63cb056dfa816427982bd880253d0c418edeecb5cc9fe5c08c4f.jpg)  
0 15 30 60 90 Kilometers

500 K. Moreover, we changed the unit of the source area from  $\mathrm{m}^2$  to  $1\%$  by dividing source area by  $562,500\mathrm{m}^2$ , since the resolution of the VIIRS Nightfire product was  $750\mathrm{m}$ . The minimum hotspot detection area was divided by  $8100\mathrm{m}^2$  since the resolution of ASTER was  $90\mathrm{m}$ . As shown in Fig. 10, the detection ability of the VIIRS Nightfire product was stronger than that of the TAI when the temperature was greater than  $700\mathrm{K}$ . In contrast, the detection ability of the TAI was much stronger than that of the VIIRS Nightfire product when the temperature was less than  $700\mathrm{K}$ , which can explain the result that more hot spots were detected by the TAI than the VIIRS Nightfire product (Fig. 8); however, some factories do not perform processes with large heat emissions, and some factories are too small to release large heat emissions.

# 5.3. The possibility of characterizing hot spots

The characterization of hot spots includes the temperature and area of the hot spot. To characterize hot spots, spaceborne sensors must have one or two spectral channels that can estimate the radiance of hot spots (Wooster et al., 2005). Since thermal channels have limits on the brightness temperature saturation, the midinfrared and SWIR channels

are better for estimation. With the SWIR channels, we can measure the sizes of the hot spots by using a bispectral method modified by (Giglio and Kendall, 2001), which was developed by (Dozier, 1981). However, there are some limitations with respect to the ASTER instrument. On the one hand, it is hard to estimate the background radiance within a fire pixel; on the other hand, only a small fraction of ASTER scenes contain SWIR bands (Giglio et al., 2008). These difficulties make it less practical for ASTER to measure the temperature and area of a hot spot (Giglio et al., 2008).

(Giglio et al., 2008) attempted to measure the fire radiative power of ASTER by seeking an empirical relationship between the FRP and observed radiance using the following equation,

$$
F R P = c _ {1 0} \left(L _ {1 0} - L _ {b, 1 0}\right) + c _ {1 2} \left(L _ {1 2} - L _ {b, 1 2}\right) + c _ {1 4} \left(L _ {1 4} - L _ {b, 1 4}\right) \tag {7}
$$

where  $c_{10}, c_{12}$ , and  $c_{14}$  are band-specific constants;  $L_{10}, L_{12}$  and  $L_{14}$  represent the observed radiance for a fire pixel in bands 10, 12 and 14, respectively; and  $L_{b,10}, L_{b,12}$  and  $L_{b,14}$  represent the individual estimation of the non-fire background radiance in band 10, 12 and 14, respectively.

This method was designed for biomass burning, and might be less

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/e1da7619-a569-41e9-8814-f94c05973134/cfe49f18d095ff1bdba7dd2cca9976e09ee7272df34c8855f7abf85ff3a22b9a.jpg)

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/e1da7619-a569-41e9-8814-f94c05973134/48fc751c17d50650c87bbf732b234aefe2572de5d9cd8b1faf557c9f2451d8d4.jpg)  
Fig. 8. Hot spots via the VIIRS Nightfire product and hot spots derived via the TAI. (a) An example of the classification of hot spots, (b) the subset of (a), and (c) the results of the classification. Hot spots detected via the VIIRS product indicate that hot spots derived via the TAI surround the hot spots detected via the VIIRS Nightfire product, which belong to the first type of hot spot (hot-spot type details in Section 4.1). Hot spots undetected in the VIIRS indicate that the hot spots derived via the TAI do not surround the hot spots via the VIIRS Nightfire product, which include hot spots of the first and second types.

efficient in small factories. Here, we simulated four industrial heat sources with different areas and temperatures and predicted their FRPs with the method introduced by Giglio (see Table 2). The observed radiances of the industrial heat sources were simulated by the MODTRAN 5 radiative transfer model, and the atmospheric parameters were

collected on September 19, 2016. We set the background temperature to be  $285\mathrm{K}$  and predicted the FRP via Eq. (7). In addition, the band-specific constants used in this paper were regressed via 100,000 samples with random hot-spot areas and temperatures. The simulated true FRP was obtained from Eq. (8), which was defined by (Wooster, 2003)

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/e1da7619-a569-41e9-8814-f94c05973134/7b38646b64da50d282e7b02f71aecaeae4a22235c2c46d5c61b7b8e9df57ea24.jpg)  
Fig. 9. Thermal detection ability under different conditions. (a) The results effected by water vapor (unit: atm-cm) and (b) the results effected by the background temperature. In addition, the atmospheric parameters were both obtained on September 19, 2016.

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/e1da7619-a569-41e9-8814-f94c05973134/f00caca45ff7963d49c16eaaeca360a455f6c5946ad150f7930ef86166e75b9c.jpg)

![](https://cdn-mineru.openxlab.org.cn/result/2025-12-03/e1da7619-a569-41e9-8814-f94c05973134/586ccad564b0d9f54f2960b63eb8d2899c61ff91d6978e5549ad16c8e9feb787.jpg)  
Fig. 10. Hotspots detection abilities of the VIIRS Nightfire product and TAI.

Table 2 Characterization of simulated industrial heat sources.  

<table><tr><td>Sample</td><td>Area (m2)</td><td>Temperature (K)</td><td>Simulated true FRP (MW)</td><td>Predicted FRP(MW)</td></tr><tr><td>1</td><td>50</td><td>700</td><td>0.68</td><td>0.54</td></tr><tr><td>2</td><td>100</td><td>700</td><td>1.36</td><td>1.17</td></tr><tr><td>3</td><td>500</td><td>700</td><td>6.81</td><td>6.26</td></tr><tr><td>4</td><td>10</td><td>1200</td><td>1.18</td><td>1.10</td></tr></table>

$$
F R P _ {\text {t r u e}} = A _ {\text {p i x}} \varepsilon \sigma \sum_ {i = 1} ^ {N} p _ {i} T _ {i} ^ {4} \tag {8}
$$

where  $FRP_{true}$  represents the simulated true FRP of the hot spot,  $A_{pix}$  represents the pixel area  $(\mathrm{m}^2)$ ,  $\varepsilon$  represents the emissivity,  $\sigma$  is the Stefan-Boltzmann constant,  $p_i$  represents the fractional area of the nth surface thermal component within the individual ground pixel, and  $T_i$  represents the temperature of the nth thermal component (K).

As shown in Table 2, the predicted FRP is highly related to the simulated true FRP, with a correlation coefficient of 0.99. This result indicates that we could use this empirical regression method to quantify the characterization of hot spots.

# 6. Conclusion

This paper introduced a method based on the TAI to detect hot spots with temperature greater than  $400\mathrm{K}$ . The detectable temperatures are lower than those via most existing methods, which makes it possible to monitor the operation of small-scale factories with combustion processes. This result will be significant for urban environmental monitoring since industrial emissions from some small factories are not up to standard and harm the environment.

Confirmed with the VIIRS Nightfire product and high-spatial-resolution images, the TAI is definitely able to detect industrial heat sources with high confidence. Compared with the VIIRS Nightfire product, the TAI is more sensitive at low temperatures, allowing it to detect cooler or smaller hot spots. Nevertheless, the detection ability of the TAI is a little worse than that of the VIIRS Nightfire product at high temperatures. This feature confirms the low-temperature thermal detection ability of the TAI, and the inefficiency of TAI at extremely high temperatures does not weaken the detection of thermal anomalies. High water vapor and low background temperatures also improve the thermal detection ability of the TAI. In addition, we can use an empirical regression method to measure the FRP of the derived industrial heat sources, regardless of the difficulties for ASTER to obtain the areas and temperatures of hot spots. These characteristics make this method promising for urban environmental monitoring.

# Acknowledgments

This work was funded by the National Natural Science Foundation of China (41471348, 41771448), the Project of State Key Laboratory of Earth Surface Processes and Resource Ecology (2017-ZY-03), Science and Technology Plans of Ministry of Housing and Urban-Rural Development of the People's Republic of China and Opening Projects of Beijing Advanced Innovation Center for Future Urban Design, Beijing University of Civil Engineering and Architecture (UDC2017030212, UDC201650100), and the Beijing Laboratory of Water Resources Security.

# References

Abrams, M., 2000. The Advanced Spaceborne Thermal Emission and Reflection Radiometer (ASTER): data products for the high spatial resolution imager on NASA's Terra platform. Int. J. Remote Sens. 21, 847-859.  
Aimin, G., 2016. Xinhua publishing House. Tangshan Yearbook.  
Baugh, K., Hsu, F.C., Elvidge, C.D., Zhizhin, M., 2013. Nighttime lights compositing using the VIIRS day-night band: preliminary results. Proc. Asia-Pacific Adv. Netw. 35, 70-86. https://doi.org/10.7125/APAN.35.8.

Berk, A., Anderson, G.P., Acharya, P.K., Bernstein, L.S., Muratov, L., Lee, J., Fox, M., Adler-Golden, S.M., Chetwynd, J.H., Hoke, M.L., Lockwood, R.B., Gardner, J.A., Cooley, T.W., Borel, C.C., Lewis, P.E., 2005. MODTRAN 5: A Reformulated Atmospheric Band Model With Auxiliary Species and Practical Multiple Scattering Options: Update. Proc. SPIE, 5806. pp. 662-667. https://doi.org/10.1117/12.606026.  
Casadio, S., Arino, O., Serpe, D., 2012. Gas flaring monitoring from space using the ATSR instrument series. Remote Sens. Environ. 116, 239-249. https://doi.org/10.1016/j.rse.2010.11.022.  
Cherubini, F., Peters, G.P., Berntsen, T., StrøMman, A.H., Hertwich, E., 2011. CO2 emissions from biomass combustion for bioenergy: atmospheric decay and contribution to global warming. Gcb Bioenergy 3, 413-426. https://doi.org/10.1111/j.1757-1707.2011.01102.x.  
Csiszar, I., Schroeder, W., Giglio, L., Ellicott, E., Vadrevu, K.P., Justice, C.O., Wind, B., 2014. Active fires from the Suomi NPP visible infrared imaging radiometer suite: product status and first evaluation results. J. Geophys. Res.-Atmos. 119, 803-816. https://doi.org/10.1002/2013JD020453.  
Dozier, J., 1981. A method for satellite identification of surface temperature fields of subpixel resolution. Remote Sens. Environ. 11, 221-229. https://doi.org/10.1016/0034-4257(81)90021-3.  
Elvidge, C.D., Erwin, E.H., Baugh, K.E., Tuttle, B.T., Howard, A.T., Pack, D.W., Milesi, C., 2007. Satellite data estimate worldwide flared gas volumes. Oil Gas J. 105 50-50.  
Elvidge, C., Ziskin, D., Baugh, K., Tuttle, B., Ghosh, T., Pack, D., Erwin, E., Zhizhin, M., 2009. A fifteen year record of global natural gas flaring derived from satellite data. Energies 2, 595-622. https://doi.org/10.3390/en20300595.  
Elvidge, C.D., Zhizhin, M., Hsu, F.C., Baugh, K.E., 2013. VIIRS nighttime: satellite pyrometry at night. Remote Sens 5, 4423-4449. https://doi.org/10.3390/rs5094423.  
Flasse, S.P., Ceccato, P., 1996. A contextual algorithm for AVHRR fire detection. Int. J. Remote Sens. 17, 419-424. https://doi.org/10.1080/01431169608949018.  
Giglio, L., Kendall, J.D., 2001. Application of the Dozier retrieval to wildfire characterization: a sensitivity analysis. Remote Sens. Environ. 77, 34-49.  
Giglio, L., Descloitrets, J., Justice, C.O., Kaufman, Y.J., 2003. An enhanced contextual fire detection algorithm for MODIS. Remote Sens. Environ. 87, 273-282. https://doi.org/10.1016/S0034-4257(03)00184-6.  
Giglio, L., Csiszar, I., Justice, C.O., 2006. Global distribution and seasonality of active fires as observed with the Terra and Aqua Moderate Resolution Imaging Spectroradiometer (MODIS) sensors. J. Geophys. Res.-Biogeosci. 111, 17-23. https://doi.org/10.1029/2005jg000142.  
Giglio, L., Csiszar, I., Restas, Á., Morisette, J.T., Schroeder, W., Morton, D., Justice, C.O., 2008. Active fire detection and characterization with the advanced spaceborne thermal emission and reflection radiometer (ASTER). Remote Sens. Environ. 112, 3055-3063. https://doi.org/10.1016/j.rse.2008.03.003.  
Giglio, L., Schroeder, W., Justice, C.O., 2016. The collection 6 MODIS active fire detection algorithm and fire products. Remote Sens. Environ. 178, 31-41. https://doi.org/10.1016/j.rse.2016.02.054.  
Grégoire, J.-M., 1990. Effects of the dry season on the vegetation canopy of some river basins of West Africa as deduced from NOAA-AVHRR data. Hydrol. Sci. J. Des. Sci. Hydrol. 35, 323-338. https://doi.org/10.1080/02626669009492432.  
Imhoff, M.L., Lawrence, W.T., Stutzer, D.C., Elvidge, C.D., 1997. A technique for using composite DMSP/OLS "City Lights" satellite data to map urban area. Remote Sens. Environ. 61, 361-370. https://doi.org/10.1016/s0034-4257(97)00046-1.  
Jacob, F., Petitcolin, Fo., Schmugge, T., Vermote, E., French, A., Ogawa, K., 2004. Comparison of land surface emissivity and radiometric temperature derived from MODIS and ASTER sensors. Remote Sens. Environ. 90, 137-152. https://doi.org/10.1016/j.rse.2003.11.015.  
Jimenez-Munoz, J.C., Sobrino, J.A., 2007. Feasibility of retrieving land-surface temperature from ASTER TIR bands using two-channel algorithms: a case study of agricultural areas. IEEE Geosci. Remote. Sens. 4, 60-64. https://doi.org/10.1109/lgrs.2006.885869.  
Jimenez-Munoz, J.C., Sobrino, J.A., 2010. A single-channel algorithm for land-surface temperature retrieval from ASTER data. IEEE Geosci. Remote. Sens. 7, 176-179. https://doi.org/10.1109/lgrs.2009.2029534.  
Kaufman, Y.J., Setzer, A., Justice, C., Tucker, C.J., Pereira, M.C., Fung, I., 1989. Remote sensing of biomass burning in the tropics. Adv. Space Res. 9, 265-268.  
Kennedy, P., 1992. Biomass burning studies: the use of remote sensing. Ecol. Bull.

133-148.  
Koltunov, A., Ustin, S.L., 2007. Early fire detection using non-linear multitemporal prediction of thermal imagery. Remote Sens. Environ. 110, 18-28. https://doi.org/10.1016/j.rse.2007.02.010.  
Liu, Y., Sun, C., Yang, Y., Zhou, M., Zhan, W., Cheng, W., 2016. Automatic extraction of offshore platforms using time-series Landsat-8 operational land imager data. Remote Sens. Environ. 175, 73-91. https://doi.org/10.1016/j.rse.2015.12.047.  
Liu, Y., Hu, C., Zhan, W., Sun, C., Murch, B., Ma, L., 2018. Identifying industrial heat sources using time-series of the VIIRS Nightfire product with an object-oriented approach. Remote Sens. Environ. 204, 347-365. https://doi.org/10.1016/j.rse.2017.10.019.  
Mao, K.B., Tang, H.J., Chen, Z.X., Qiu, Y.B., Qin, Z.H., Man-Chun, L.I., 2006. A split-window algorithm for retrieving land-surface temperature from ASTER data. Remote Sensing Inf. 58, 7-11.  
Matson, M., 1981. Identification of subresolution high temperature sources using a thermal IR sensor. Photogramme Eng. Remot Sens. 47, 1311-1318.  
Matson, Michael, Stephens, George, Robinson, Jennifer, 1987. Fire detection using data from the NOAA-N satellites. Int. J. Remote Sens. 8, 961-970. https://doi.org/10.1080/01431168708954740.  
Oda, T., Maksyutov, S., 2011. A very high-resolution  $(1\mathrm{km}\times 1\mathrm{km})$  global fossil fuel  $\mathrm{CO}_{2}$  emission inventory derived using a point source database and satellite observations of nighttime lights. Atmos. Chem. Phys. 11, 543-556. https://doi.org/10.5194/acp-11-543-2011.  
Ramaswami, A., Tong, K., Fang, A., Lal, R.M., Nagpure, A.S., Li, Y., Yu, H., Jiang, D., Russell, A.G., Shi, L., Chertow, M., Wang, Y., Wang, S., 2017. Urban cross-sector actions for carbon mitigation with local health co-benefits in China. Nat. Clim. Change 7, 736-742. https://doi.org/10.1038/nclimate3373.  
Ricardo, J., De Franca, A., Brustet, J.-M., Fontan, J., 1995. Multispectral remote sensing of biomass burning in West Africa. J. Atmos. Chem. 22, 81-110. https://doi.org/10.1007/bf00708183.  
Roberts, G., Wooster, M.J., 2014. Development of a multi-temporal Kalman filter approach to geostationary active fire detection & fire radiative power (FRP) estimation. Remote Sens. Environ. 152, 392-412. https://doi.org/10.1016/j.rse.2014.06.020.  
Schroeder, W., Ruminski, M., Csiszar, I., Giglio, L., Prins, E., Morisette, J., Morisette, J., 2008. Validation analyses of an operational fire monitoring product: the Hazard Mapping System. Int. J. Remote Sens. 29, 6059-6066. https://doi.org/10.1080/01431160802235845.  
Schroeder, W., Oliva, P., Giglio, L., Csiszar, I.A., 2014. The New VIIRS 375m active fire detection data product: algorithm description and initial assessment. Remote Sens. Environ. 143, 85-96. https://doi.org/10.1016/j.rse.2013.12.008.  
Schroeder, W., Oliva, P., Giglio, L., Quayle, B., Lorenz, E., Morelli, F., 2016. Active fire detection using Landsat-8/OLI data. Remote Sens. Environ. 185, 210-220. https://doi.org/10.1016/j.rse.2015.08.032.  
Wooster, M., 2003. Fire radiative energy for quantitative study of biomass burning: derivation from the BIRD experimental satellite and comparison to MODIS fire products. Remote Sens. Environ. 86, 83-107. https://doi.org/10.1016/s0034-4257(03)00070-1.  
Wooster, M.J., Roberts, G., Perry, G.L.W., Kaufman, Y.J., 2005. Retrieval of biomass combustion rates and totals from fire radiative power observations: FRP derivation and calibration relationships between biomass consumption and fire radiative energy release. J. Geophys. Res. Atmos. 110, 311.  
Wooster, M.J., Xu, W., Nightingale, T., 2012. Sentinel-3 SLSTR active fire detection and FRP product: pre-launch algorithm development and performance evaluation using MODIS and ASTER datasets. Remote Sens. Environ. 120, 236-254. https://doi.org/10.1016/j.rse.2011.09.033.  
Xu, H., 2006. Modification of normalised difference water index (NDWI) to enhance open water features in remotely sensed imagery. Int. J. Remote Sens. 27, 3025-3033. https://doi.org/10.1080/01431160600589179.  
Yamaguchi, Y., Kahle, A.B., Tsu, H., Kawakami, T., Pniel, M., 1998. Overview of advanced spaceborne thermal emission and reflection radiometer (ASTER). IEEE Trans. Geosci. Remote Sens. 36, 1062-1071. https://doi.org/10.1109/36.700991.  
Zhou, Y., Smith, S.J., Elvidge, C.D., Zhao, K., Thomson, A., Imhoff, M., 2014. A cluster-based method to map urban area from DMSP/OLS nightlights. Remote Sens. Environ. 147, 173-185. https://doi.org/10.1016/j.rse.2014.03.004.