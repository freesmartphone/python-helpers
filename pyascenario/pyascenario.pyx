"""
    pyascenario high level functions
    Authored by Michael 'Mickey' Lauer <mlauer@vanille-media.de>
    (C) 2008 OpenMoko, Inc.
    LGPL v3
"""

__version__ = "1.0.0"

cdef extern from "alsa/ascenario.h":
    struct snd_scenario

    snd_scenario* snd_scenario_init(char *card_name)

    int snd_scenario_reload(snd_scenario *scn)

    void snd_scenario_exit(snd_scenario *scn)

    int snd_scenario_set_scn(snd_scenario *scn, char *scenario)

    char *snd_scenario_get_scn(snd_scenario *scn)

    int snd_scenario_list(snd_scenario *scn, char ***l)

    int snd_scenario_set_qos(snd_scenario *scn, int qos)

    int snd_scenario_get_qos(snd_scenario *scn)

    int snd_scenario_get_master_playback_volume(snd_scenario *scn)

    int snd_scenario_get_master_playback_switch(snd_scenario *scn)

    int snd_scenario_get_master_capture_volume(snd_scenario *scn)

    int snd_scenario_get_master_capture_switch(snd_scenario *scn)

    int scn_scenario_dump(char *card_name)

def list_scenarios():
    return _list_scenarios()

cdef _list_scenarios():
    cdef snd_scenario* manager = snd_scenario_init( "default" )
    cdef char** l
    snd_scenario_list( manager, &l )
    retval = []
    cdef i = 0
    if l:
        while l[i]:
            retval.append( l[i] )
    return retval
