Weather data from Bleiswijk, The Netherlands. From 19/10/2009 at 15:15, until 08/02/2010 at 15:10.

The data is from:
Katzin, D., Kempkes, F., van Mourik, S., van Henten, E., Dieleman, A., Dueck, T., Schapendonk, A., Scheffers, K., Pot, S., & Trouwborst, G. (2025). Data from: ‘GreenLight - An open source model for greenhouses with supplemental lighting: Evaluation of heat requirements under LED and HPS lamps’ (Version 2) [Csv, xlsx, mat]. 4TU.ResearchData. https://doi.org/10.4121/78968E1B-EAEA-4F37-89F9-2B98BA3ED865.V2

Specifically, the file: 
Simulation data/CSV output/climateModel_hps_manuscriptParams.csv
was used.

The file was modified in the following ways:
	- The Time column was modified to relative times in seconds - starting from 0, in 300 seconds increments
	- Outdoor CO2 concentration was converted from mg/m3 to kg/m3 by dividing by 1e6
	- Outdoor humidity concentration was calculated using the ideal gas law:
	V_h = vp*m_water./(r*(t+273.15))
		where V_h is the outdoor humidity concentration (kg/m3)
		vp is the outdoor vapor pressure (Pa)
		m_water = 18.01528e-3 kg/mol is the molar mass of water 
		r = J/mol/K is the molar gas constant
		t is outdoor temperature (°C)
		
This file created by David Katzin, Wageningen University & Research, September 2025
	