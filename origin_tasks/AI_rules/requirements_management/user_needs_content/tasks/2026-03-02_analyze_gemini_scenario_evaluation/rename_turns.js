#!/usr/bin/env node
// Renames split/turn_NN.json files to descriptive names based on conversation content.

const fs = require('fs');
const path = require('path');

const SPLIT_DIR = path.join(__dirname, 'split');

const NAMES = {
  '01': 'gap_analysis_initial_overview',
  '02': 'systematic_review_start_app_provider',
  '03': 'david_category_correction_analysis_vs_capture',
  '04': 'david_therapy_motivation_and_why_tracking',
  '05': 'david_confirmed_dr_turan_start',
  '06': 'dr_turan_interdisciplinary_collab_with_psychotherapists',
  '07': 'dr_turan_german_medical_bureaucracy_scenarios',
  '08': 'dr_turan_done_david_addendum_adhd_relapse_loop',
  '09': 'dr_sarah_start_review',
  '10': 'dr_sarah_praxissoftware_and_pia',
  '11': 'dr_sarah_remaining_gaps',
  '12': 'dr_sarah_confirmed_elias_start',
  '13': 'elias_category_correction_exposure_tracking',
  '14': 'elias_confirmed_cluster_representation',
  '15': 'jana_start',
  '16': 'jana_confirmed_cluster_representation',
  '17': 'jana_finalized_lena_start',
  '18': 'lena_multicultural_migration_layer',
  '19': 'lena_confirmed_lisa_start',
  '20': 'lisa_cluster_representation_more_scenarios',
  '21': 'lisa_pmds_masking_confirmed_max_start',
  '22': 'max_clusters_and_additional_scenarios',
  '23': 'max_confirmed_michael_start',
  '24': 'michael_cluster_scenarios',
  '25': 'michael_confirmed_nina_start',
  '26': 'nina_cluster_scenarios',
  '27': 'alphabet_completeness_check_prof_weber_start',
  '28': 'prof_weber_cluster_scenarios',
  '29': 'prof_weber_confirmed_sophie_start',
  '30': 'sophie_confirmed_blind_spots_review',
  '31': 'blind_spot_1_new_persona_amina_migration',
  '32': 'amina_characteristics_and_clusters',
  '33': 'amina_redesign_remove_education_bias',
  '34': 'blind_spot_2_accessibility_a11y_scenarios',
  '35': 'blind_spot_2_confirmed_blind_spot_3_start',
  '36': 'final_count_deduplication_completeness_review',
};

let renamed = 0;
for (const [num, name] of Object.entries(NAMES)) {
  const oldPath = path.join(SPLIT_DIR, `turn_${num}.json`);
  const newPath = path.join(SPLIT_DIR, `turn_${num}_${name}.json`);
  if (fs.existsSync(oldPath)) {
    fs.renameSync(oldPath, newPath);
    console.log(`turn_${num}.json  →  turn_${num}_${name}.json`);
    renamed++;
  } else {
    console.warn(`  SKIP (not found): turn_${num}.json`);
  }
}

console.log(`\nDone. ${renamed} files renamed.`);
