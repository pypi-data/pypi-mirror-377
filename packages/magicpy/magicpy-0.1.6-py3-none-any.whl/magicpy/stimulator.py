"""
This stores dictionaries to translate from function parameters to stimulator bits.
"""
page_dict = {
    1: 'Main',
    2: 'Train',
    3: 'Trig',
    4: 'Config',
    6: 'Download',
    7: 'Protocol',
    8: 'MEP',
    13: 'Service',
    15: 'Treatment',
    16: 'Treat Select'
}

waveform_dict = {
    0: 'Monophasic',
    1: 'Biphasic',
    2: 'Half Sine',
    3: 'Biphasic Burst',
    11: 'Biphasic Burst'
}

mode_dict = {
    0: 'Standard',
    1: 'Power',
    2: 'Twin',
    3: 'Dual'
}
