# DisplayFPVS
Python (PsychoPy) Code for displaying custom visual stimuli for Fast Periodic Visual Stimulation (FPVS, a.k.a Steady-State Visual Evoked Potentials, SSVEP).  Designed to be used in the context of electroencephalography (EEG) experiments.

To run for your own experiment:

1) Make sure Python and psychoPy are installed
2) Make appropriate stimuli (images) to be displayed
3) Set the psychoPy preferences and monitor settings to reflect your particular experimental setup.
4) Place SSVEP.py into the desired experiment directory
5) In the same directory, place a folder called "stimuli"

6) If the experiment is a base category vs. oddball category type of paradigm:
a) Inside the "stimuli" folder put two more folders, one for each stimulus category (e.g. "objects","faces").  Put all the respective stimulus image files in those sub-folders.
b) In the SSVEP.py code go to the __init__ function and set the self.StimDir variable to the names of the two stimulus category folders (e.g. ["objects","faces"]) with the second listed category being the intended oddball category.  Also uncomment the indicated line in the code for the relevant stimulus list generation for this type of paradigm.

6) If the experiment is an exemplar oddball type of paradigm:
a) Put all the stimulus image files within the "stimuli" folder.
b)  In the SSVEP.py code, go to the __init__ function and uncomment the indicated line in the code for the relevant stimulus list generation for this type of paradigm.

7) Set the ACTUAL_SCREEN_RESOLUTION variable to the resolution of your monitor.  Customize any other things in the code to your needs (e.g., stimulus size, background colors, random stimulus sizes, Fade in, etc).
8) Set your monitor's screen refresh rate to the desired frequency.
9) Open SSVEP.py in the psychoPy coder viewer and run it.


Additional Notes:
If your stimulus image x/y proportions do not match those in the SSVEP.py stimSize parameter, you must change that parameter or else your stimuli will be displayed stretched.

The stimulation frequency you choose from the dropdown menu will not necessarily be exact because the actual possible stimulation frequency depends on the screen refresh rate.  The code automatically finds a stimulation rate close to the target frequency based upon the screen refresh rate that it detects.  If your monitor refresh rate is not stable, the calculated stimulation frequency will not be correct and the experiment may additionally fail near the end because it miscalculated the number of stimuli needed for the whole run.

Anyone may use and customize this code for their own purposes, but I would appreciate a mention in the acknowledgements section of any resulting publication.  Hope you enjoy!
