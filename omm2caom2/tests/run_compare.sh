#!/bin/bash

for obs_id in 'C050808_0249A_SCI' 'C060630_0452_SCI' 'C071112_0001_CAL' 'C080920_0194_SCI' 'C090620_0003_SCI' 'C100925_0342_CAL' 'C110114_0133_SCI' 'C120311_0700_SCI' 'C170324_0028_FOCUS' 'C120902_sh2-132_J_old_SCIRED' 'C170323_0172_CAL' 'C170217_0228_SCI' 'C170323_domeflat_K_CALRED' 'C170318_0002_FOCUS' 'C170324_0054_SCI' 'C170318_0121_SCI'
do
    echo $obs_id
    python test_compare_obs.py --observationID ${obs_id} --collection OMM
done
date
exit 0