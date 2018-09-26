#!/bin/python
"""

"""
# Import the following programs:
from __future__ import division
import tupak
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

# Define the following to convert values to seconds:
seconds_in_year = 86400 * 365
seconds_in_day = 86400

# Set up some labels for the file and the directory it is saved in:
label = 'PSR-B1828-11_precession_constant_period'
outdir = 'outdir_precession_constant_period'

# Read in the data - this requires you to save the data in /data:
file_name = 'data/1828-11_100vf_fig.dat'
cols = (0, 3, 4)
names = ["MJD", "F1", "F1_err"]
df = pd.read_csv(file_name, sep=' ', usecols=cols, header=None, names=names,
                 dtype=None, skipinitialspace=True, index_col=False)

# This is the independent variable and the dependent variable:
MJD = df.MJD.values
MJD_seconds = MJD * seconds_in_day
nudot = df.F1.values * 1e-15

# Plot the data: 
fig = plt.figure(figsize=(10,6))
plt.plot(MJD_seconds, nudot, label='PRECESSION DATA')
plt.title('PRECESSION DATA FOR PULSAR B1828-11')
plt.legend()
plt.xlabel('TIME (s)')
plt.ylabel('$\dot\\nu$ (Hz/s)')
txt = "Graph of the data points of the pulsar shown as a line graph."
plt.figtext(0.5, 0.01, txt, wrap=True, horizontalalignment='center', 
            fontsize=10)
plt.tight_layout()
plt.savefig('precession_data.pdf')

# Fill in the function to describe precession:
def model(MJD_seconds, tau_age, P, n, t_ref, theta, chi, tau_p, psi_initial, 
          **kwargs):
    
    # Define the function in parts:
    psi = (2 * np.pi * (MJD_seconds - t_ref) / tau_p) + psi_initial
    mean = 1 / (tau_age * P)
    
    a = -1
    b = (n * (MJD_seconds - t_ref)) / tau_age
    c = 2 * theta * (np.cos(chi) / np.sin(chi)) * np.sin(psi)
    d = (- theta**2 / 2) * np.cos(2 * psi)
    
    # Define the function as a whole:
    return mean * (a + b + c + d)

# This is the 'likelihood' function:
likelihood = tupak.core.likelihood.GaussianLikelihood(x=MJD_seconds, y=nudot, 
                                                      function=model)

# Fill in the priors/parameters for the appropriate values:
priors = {}

# These values do not have parameters:
priors['tau_age'] = 213827.91 * seconds_in_year
priors['P'] = 0.405
priors['n'] = 16.08
priors['t_ref'] = 49621 * seconds_in_day

# Define the above fixed priors explicitly:
fixed_priors = priors.copy()

# These values have a minimum and maximum parameter:
priors['tau_p'] = tupak.prior.Uniform(minimum=450 * 86400, maximum=550 * 86400, 
      name='tau_p')
priors['theta'] = tupak.prior.Uniform(minimum=0, maximum=0.1, name='theta')
priors['chi'] = tupak.prior.Uniform(minimum=2 * np.pi / 5, maximum=np.pi / 2, 
      name='chi')
priors['psi_initial'] = tupak.prior.Uniform(minimum=0, maximum=2 * np.pi, 
      name='psi_initial')

priors['sigma'] = tupak.core.prior.Uniform(0, 1e-15, 'sigma')

# Run the sampler:
result = tupak.run_sampler(
    likelihood=likelihood, priors=priors, sampler='dynesty', npoints=100,
    walks=10, outdir=outdir, label=label, clean=True)
result.plot_corner()

# Define a new plot:
fig, ax = plt.subplots()

# Run values from 'result.posterior' and fit the data:
for i in range(4000):
    sample_dictionary = result.posterior.sample().to_dict('records')[0]
    sample_dictionary.update(fixed_priors)
    ax.plot(MJD_seconds, model(MJD_seconds, **sample_dictionary), color='gray', 
            alpha=0.05)

# Plot the fitted data:
ax.scatter(MJD_seconds, nudot, marker='.')
txt = ("Graph of the precession function with multiple data fitted parameters,"
       " and the pulsar's data points.")
plt.figtext(0.5, 0.01, txt, wrap=True, horizontalalignment='center', 
            fontsize=10)
fig.savefig('{}/data_with_fit.pdf'.format(outdir))
# Save .pdf as .png for high resolution image.