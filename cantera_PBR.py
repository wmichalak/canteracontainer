"""Example Cantera PFR simulation"""

import cantera as ct
import pandas as pd
import os

# Define Cantera Solution for system
reaction_mechanism = 'gri30.xml'
rxr_gas = ct.Solution(reaction_mechanism)
env_gas = ct.Solution(reaction_mechanism)

# Define process conditions
tref = 273.15
T = 500 + tref # [K]
P = ct.one_atm # [Pa]
furnace_T = 500 + tref # [K]
mass_flow_rate = 0.0001 #[kg/s]

# Define gas phase properties
rxr_gas.TPX = T, P, 'CH4:.1, O2:1, AR:0.1'

# Define furnace properties
env_gas.TPX = furnace_T, ct.one_atm, 'AR:1'

# Define reactor object
rxr = ct.Reactor(contents=rxr_gas, energy='on')

# Define CSTR properties
n_reactors = 100. # number of CSTRs for PFR
reactor_diameter = 0.2 # [m]
reactor_length = 1 # [m]
total_volume = pd.np.pi * reactor_diameter**2 / 4.0  # [m^3]
total_area = pd.np.pi * reactor_diameter * reactor_length # [m^2]
rxr.volume = total_volume / n_reactors

# We need an environment for the outside of the reactor wall.
furnace_env = ct.Reservoir(env_gas)

# Define upstream gas to feed into PFR (or rather into each CSTR)
upstream_reservoir = ct.Reservoir(rxr_gas, name='upstream')

# create a reservoir for the reactor to exhaust into. The composition of this reservoir is irrelevant.
downstream_reservoir = ct.Reservoir(rxr_gas, name='downstream')

# We need a valve between the reactor and the downstream reservoir.
mcontroller_cstr = ct.MassFlowController(upstream=upstream_reservoir, downstream=rxr,
                                             mdot=mass_flow_rate)

# Pressure valve - defined as dF / dP [m^3/s/Pa] should control to ~1 Pa
vol_flow_rate0 = mass_flow_rate / rxr_gas.density_mass
pvalve_cstr = ct.PressureController(upstream=rxr, downstream=downstream_reservoir,
                                        master=mcontroller_cstr, K=vol_flow_rate0)

# Define Reactor wall for heat exchange - value of xHtc sets degree of isothermal or adiabatic
# Define overall heat transfer coefficient to start and heat exchange area in the single CSTR
Utotal = 1000 # W/m^2/K
heat_exchange_area = total_area / n_reactors # [m^2]
rxr_wall = ct.Wall(left=furnace_env, right=rxr, A=heat_exchange_area, U=Utotal)

# Create Reactor network
reactor = ct.ReactorNet([rxr])

# Calculate solutions for each reactor
data = pd.DataFrame(columns=['z [m]', 'T [C]', 'O2', 'H2', 'CH4']) # Use this to check that it is working
for i,n in enumerate(range(int(n_reactors))):
    # Set the state of the reservoir to match that of the previous reactor
    rxr_gas.TDY = rxr.thermo.TDY
    # Get values from upstream. This is required because of the use of microreactors to simulate axial stage
    # down reactor
    upstream_reservoir.syncState()
    reactor.reinitialize()
    reactor.advance_to_steady_state()

    # If you want to update the heat transfer coefficient, for example, if the internal heat transfer changes with the
    #linear velocity in the reactor, you can write
    #rxr_wall.heat_transfer_coeff = overall_heat_transfer_coeff()

    # Write outputs
    data.loc[n, 'z [m]'] = n * reactor_length / n_reactors
    data.loc[n, 'T [C]'] = rxr_gas.T - tref #
    data.loc[n, ['O2', 'H2', 'CH4']] = rxr_gas[['O2', 'H2', 'CH4']].X

# Write the output file
output_dir = os.path.expanduser('~/Simulations/Outputs/')
if not os.path.exists(output_dir):
    os.makedirs(output_dir)
data.to_csv(output_dir + 'output.csv')



