"""A list of known stimulators and coil types"""

stimulator_types = {
    0: 'R30',
    1: 'X100',
    2: 'R30+Option',
    3: 'X100+Option',
    4: 'R30+Option+Mono',
    5: 'MST'
}

coil_types = {
    0: 'MRi-B91 Air cooled',  # or any unrecognized coil from stimulator
    56: 'Cool-B35 RO',  # with active cooling. get_status()[0]['Temperature'] == 90 -> no cooling connected.
    62: 'MCF-B65',
    63: 'MCF-P-B65',
    73: 'C-B70',
    82: 'MC-B70'
}
