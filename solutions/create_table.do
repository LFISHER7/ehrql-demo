* Table of dulaglutide prescribing in the year after the index date

clear all
set more off

capture mkdir output

import delimited using "output/dataset_t2dm.csv", clear varnames(1) case(lower) bindquote(strict) stringcols(_all)
gen byte dulaglutide = inlist(lower(has_dulaglutide), "true", "1")

tempfile source results
save `source'

use `source', clear
gen n_patients = 1
collapse (sum) n_patients n_dulaglutide=dulaglutide
gen characteristic = "Overall"
gen group = "All patients"
gen sort_characteristic = 0
gen sort_group = 0
save `results'

use `source', clear
collapse (count) n_patients=dulaglutide (sum) n_dulaglutide=dulaglutide, by(sex)
rename sex group
gen characteristic = "Sex"
gen sort_characteristic = 1
gen sort_group = .
replace sort_group = 1 if group == "female"
replace sort_group = 2 if group == "male"
append using `results'
save `results', replace

use `source', clear
collapse (count) n_patients=dulaglutide (sum) n_dulaglutide=dulaglutide, by(age_band)
rename age_band group
gen characteristic = "Age band"
gen sort_characteristic = 2
gen sort_group = .
replace sort_group = 1 if group == "0-19"
replace sort_group = 2 if group == "20-39"
replace sort_group = 3 if group == "40-59"
replace sort_group = 4 if group == "60-79"
replace sort_group = 5 if group == "80+"
replace sort_group = 6 if group == "missing"
append using `results'
save `results', replace

use `source', clear
collapse (count) n_patients=dulaglutide (sum) n_dulaglutide=dulaglutide, by(ethnicity)
rename ethnicity group
gen characteristic = "Ethnicity"
gen sort_characteristic = 3
gen sort_group = .
replace sort_group = 1 if group == "White"
replace sort_group = 2 if group == "Mixed"
replace sort_group = 3 if group == "South Asian"
replace sort_group = 4 if group == "Black"
replace sort_group = 5 if group == "Other"
replace sort_group = 6 if group == "Missing"
append using `results'
save `results', replace

use `results', clear
gen percent_dulaglutide = round(100 * n_dulaglutide / n_patients, 0.1)
sort sort_characteristic sort_group
keep characteristic group n_patients n_dulaglutide percent_dulaglutide
export delimited using "output/dulaglutide_table_stata.csv", replace
