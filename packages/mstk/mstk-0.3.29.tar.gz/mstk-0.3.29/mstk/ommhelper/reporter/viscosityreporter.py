from openmm import app, unit
from ..unit import *


class ViscosityReporter:
    '''
    ViscosityReporter report the velocity amplitude and reciprocal of viscosity using cosine periodic perturbation method.
    An integrator supporting this method is required.
    E.g. the VVIntegrator from https://github.com/z-gong/openmm-velocityVerlet.

    Parameters
    ----------
    file : string or file
        The file to write to, specified as a file name or file object
    reportInterval : int
        The interval (in time steps) at which to write frames
    append : bool
        Whether or not append to the existing file.
    '''

    def __init__(self, file, reportInterval, append=False):
        self._reportInterval = reportInterval
        self._openedFile = isinstance(file, str)
        if self._openedFile:
            if append:
                self._out = open(file, 'a')
            else:
                self._out = open(file, 'w')
        else:
            self._out = file
        self._hasInitialized = False

    def describeNextReport(self, simulation):
        """Get information about the next report this object will generate.

        Parameters
        ----------
        simulation : Simulation
            The Simulation to generate a report for

        Returns
        -------
        tuple
            A six element tuple. The first element is the number of steps
            until the next report. The next four elements specify whether
            that report will require positions, velocities, forces, and
            energies respectively.  The final element specifies whether
            positions should be wrapped to lie in a single periodic box.
        """
        try:
            simulation.integrator.getCosAcceleration()
        except AttributeError:
            raise Exception('This integrator does not calculate viscosity')

        steps = self._reportInterval - simulation.currentStep % self._reportInterval
        return (steps, False, False, False, False)

    def report(self, simulation: app.Simulation, state):
        """Generate a report.

        Parameters
        ----------
        simulation : Simulation
            The Simulation to generate a report for
        state : State
            The current state of the simulation
        """
        if not self._hasInitialized:
            self._hasInitialized = True
            print('#"Step"\t"Acceleration (nm/ps^2)"\t"VelocityAmplitude (nm/ps)"\t"1/Viscosity (1/Pa.s)"',
                  file=self._out)

        acceleration = simulation.integrator.getCosAcceleration().value_in_unit(nm / ps ** 2)
        vMax, invVis = simulation.integrator.getViscosity()
        vMax = vMax.value_in_unit(nm / ps)
        invVis = invVis.value_in_unit((unit.pascal * unit.second) ** -1)
        print(simulation.currentStep, acceleration, vMax, invVis, sep='\t', file=self._out)

        if hasattr(self._out, 'flush') and callable(self._out.flush):
            self._out.flush()

    def __del__(self):
        if self._openedFile:
            self._out.close()
