* Figure of dulaglutide prescribing in the year after the index date

clear all
set more off

capture mkdir output

import delimited using "output/dataset_t2dm.csv", clear varnames(1) case(lower) bindquote(strict) stringcols(_all)
gen byte dulaglutide = inlist(lower(has_dulaglutide), "true", "1")

tempfile source results
save `source'

use `source', clear
collapse (count) n_patients=dulaglutide (sum) n_dulaglutide=dulaglutide, by(sex)
rename sex group
gen characteristic = "Sex"
gen sort_group = .
replace sort_group = 1 if group == "female"
replace sort_group = 2 if group == "male"
save `results'

use `source', clear
collapse (count) n_patients=dulaglutide (sum) n_dulaglutide=dulaglutide, by(age_band)
rename age_band group
gen characteristic = "Age band"
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
gen sort_group = .
replace sort_group = 1 if group == "White"
replace sort_group = 2 if group == "Mixed"
replace sort_group = 3 if group == "South Asian"
replace sort_group = 4 if group == "Black"
replace sort_group = 5 if group == "Other"
replace sort_group = 6 if group == "Missing"
append using `results'

use `results', clear
gen percent_dulaglutide = round(100 * n_dulaglutide / n_patients, 0.1)
gen label = string(n_dulaglutide) + "/" + string(n_patients)
save `results', replace

program drop _all
program define draw_panel
    syntax , CHARACTERISTIC(string) NAME(name)
    preserve
    keep if characteristic == "`characteristic'"
    sort sort_group
    gen ypos = _n
    local ylab
    forvalues i = 1/`=_N' {
        local g = group[`i']
        local ylab `"`ylab' `i' "`g'""'
    }
    twoway ///
        bar percent_dulaglutide ypos, horizontal barwidth(0.7) ///
            fcolor("44 127 184") lcolor(none) ///
        || scatter ypos percent_dulaglutide, ///
            msymbol(none) mlabel(label) mlabpos(3) mlabcolor(black) ///
        , ylabel(`ylab', angle(0) nogrid) yscale(reverse) ///
        xlabel(0(20)100) xscale(range(0 145)) ///
        xtitle("Percent of patients") ytitle("") ///
        title("`characteristic'") legend(off) ///
        name(`name', replace)
    restore
end

use `results', clear
draw_panel, characteristic("Sex") name(g_sex)
draw_panel, characteristic("Age band") name(g_age)
draw_panel, characteristic("Ethnicity") name(g_ethnicity)

graph combine g_sex g_age g_ethnicity, cols(3) xsize(12) ysize(5) ///
    title("Dulaglutide prescription in the year after the index date") ///
    note("Patients with type 2 diabetes who are registered and alive on 1 January 2025. Bar labels are counts.")
graph export "output/dulaglutide_figure_stata.png", replace width(2400)
