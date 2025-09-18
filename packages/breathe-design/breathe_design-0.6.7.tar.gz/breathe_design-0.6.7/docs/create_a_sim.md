# Creating a Simulation

In this section, we will demonstrate how simple it is to create a simulation using the `breathe_design` API. We will fetch a list of available batteries, retrieve base parameters for a specific battery, and calculate equilibrium KPIs.

```python
# Import the api_interface module from the breathe_design package
from breathe_design import api_interface as api

# Fetch a list of available batteries from the server
batteries = api.get_batteries()

# Print the list of batteries
print(batteries)

# Retrieve base parameters for the "Molicel P45B" battery
base_params = api.get_design_parameters("Molicel P45B")

# Calculate equilibrium KPIs and generate a plot for the "Molicel P45B" battery
eqm_kpis, fig = api.get_eqm_kpis("Molicel P45B")

# Print the equilibrium KPIs
print(eqm_kpis)

# Display the plot
fig.show()
```
