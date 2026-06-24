;;; =============================================================
;;; CORRIDOR GOVERNANCE MODEL — v6
;;; =============================================================

breed [ humans human ]

humans-own [
  is-active?
  willingness-to-accept
  prob-to-leave
  income-growth
  opportunity-perception
  predator-damage-experienced  ;; cumulative bear damage index
  action-reduce-hunting
  action-reduce-logging
  action-reduce-grazing
  action-reduce-agriculture
  action-patrol
  action-planting
  action-plot-merging
  accepted-agreement?
  has-emigrated?
]

globals [
  pop-nontarget
  pop-chamois
  pop-bear
  pop-deer
  pop-broadleaf

  raw-start-nontarget
  raw-start-chamois
  raw-start-bear
  raw-start-deer
  raw-start-broadleaf

  K-nontarget
  K-chamois
  K-bear
  K-deer
  K-broadleaf

  r-nontarget
  r-chamois
  r-bear
  r-deer
  r-broadleaf

  hunt-nontarget
  hunt-chamois
  hunt-bear
  hunt-deer
  log-broadleaf

  agri-intensity
  grazing-intensity
  ecosystem-status

  community-patrol-level
  community-planting-level
  community-agri-level
  community-grazing-level
  community-plot-merging-level

  rangers-active?
  ranger-patrol-level
  investor-active?

  human-pop
  human-start-pop
  emigrants-this-year

  community-income-index
  years-elapsed
  grazing-hay-facility-paid?

  ;; Agreement duration tracking
  agreement-year-start
  agreement-active?
]

;; ---------------------------------------------------------------
;; SETUP
;; ---------------------------------------------------------------
to setup
  clear-all
  reset-ticks
  set years-elapsed 0
  set grazing-hay-facility-paid? false
  set emigrants-this-year 0
  set agreement-year-start 0
  set agreement-active? (scenario = 2)

  set pop-chamois    200    set K-chamois    600
  set pop-bear        40    set K-bear       120
  set pop-deer       400    set K-deer      1200
  set pop-broadleaf  100    set K-broadleaf  200
  set pop-nontarget  100    set K-nontarget  200

  set raw-start-chamois   pop-chamois
  set raw-start-bear      pop-bear
  set raw-start-deer      pop-deer
  set raw-start-broadleaf pop-broadleaf
  set raw-start-nontarget pop-nontarget

  set r-chamois   0.10   ;; netto con kill 0.08 = +0.02 -> quasi piatto, poi logistic
  set r-bear      0.05   ;; netto con kill 0.03 = +0.02 -> ma bear ha hunt=0 quindi scende poco
  set r-deer      0.11   ;; netto con kill 0.08 = +0.03 -> quasi piatto
  set r-broadleaf 0.03   ;; netto con kill 0.04 = -0.01 -> lieve declino
  set r-nontarget 0.06   ;; netto con kill 0.08+0.03 = -0.05 -> declino

  set hunt-chamois   1
  set hunt-bear      0
  set hunt-deer      1
  set hunt-nontarget 1
  set log-broadleaf  1

  set agri-intensity    1
  set grazing-intensity 1
  set ecosystem-status  1

  set rangers-active?     false
  set ranger-patrol-level 0
  set investor-active?    false

  set human-pop       300
  set human-start-pop 300
  set community-income-index 100

  apply-scenario-setup
  create-humans 300 [ initialise-human ]
  reset-ticks
end

;; ---------------------------------------------------------------
;; SCENARIO SETUP
;; ---------------------------------------------------------------
to apply-scenario-setup

  if scenario = 1 [
    set rangers-active?  false
    set investor-active? false
  ]

  if scenario = 2 [
    set rangers-active?     rangers-in-agreement?
    set ranger-patrol-level (ifelse-value rangers-active? [ 2 ] [ 0 ])
    set investor-active?    (random-float 1.0 < 0.6)
  ]

  if scenario = 3 [
    set rangers-active?     true
    set ranger-patrol-level 3
    set investor-active?    false
  ]

  if scenario = 4 [
  set rangers-active?     false
  set investor-active?    true
  set ecosystem-status    0
  set hunt-nontarget 0  set hunt-chamois 0
  set hunt-bear      0  set hunt-deer    0
  set log-broadleaf  0
  set agri-intensity 0  set grazing-intensity 0

  ;; Popolazioni già degradate al momento della privatizzazione
  set pop-chamois    (pop-chamois    * 0.5)
  set pop-bear       (pop-bear       * 0.5)
  set pop-deer       (pop-deer       * 0.5)
  set pop-broadleaf  (pop-broadleaf  * 0.6)
  set pop-nontarget  (pop-nontarget  * 0.5)
]

end

;; ---------------------------------------------------------------
;; INITIALISE HUMAN
;; ---------------------------------------------------------------
to initialise-human
  set is-active? (random-float 1.0 < 0.80)
  set willingness-to-accept clamp01 (random-normal 0.45 0.20)
  set prob-to-leave clamp01 (random-normal 0.08 0.05)
  set income-growth          100
  set opportunity-perception clamp01 (random-normal 0.20 0.08)
  set predator-damage-experienced 0

  set action-reduce-hunting     0
  set action-reduce-logging     0
  set action-reduce-grazing     0
  set action-reduce-agriculture 0
  set action-patrol             0
  set action-planting           0
  set action-plot-merging       0

  set accepted-agreement? false
  if scenario = 2 [
    ;; Land tenure raises initial WTA if active
    let tenure-boost (ifelse-value agreement-land-tenure? [ 0.10 ] [ 0 ])
    if random-float 1.0 < (willingness-to-accept + tenure-boost) [
      set accepted-agreement? true
    ]
  ]
  if scenario = 3 [ set accepted-agreement? true  ]
  if scenario = 1 [ set accepted-agreement? false ]
  if scenario = 4 [ set accepted-agreement? false ]

  set has-emigrated? false
  hide-turtle
end

;; ---------------------------------------------------------------
;; GO
;; ---------------------------------------------------------------
to go
  if years-elapsed >= simulation-years [ stop ]
  set years-elapsed (years-elapsed + 1)
  set emigrants-this-year 0

  ;; Check agreement duration expiry (Scenario 2)
  if scenario = 2 [
    if years-elapsed > agreement-duration [
      set agreement-active? false
    ]
  ]

  apply-scenario-tick-rules

  ask humans with [ is-active? and not has-emigrated? ] [
    update-predator-damage
    update-willingness-to-accept
    if (accepted-agreement? and agreement-active?) [ take-conservation-actions  ]
    if not (accepted-agreement? and agreement-active?) [ take-non-compliant-actions ]
    maybe-emigrate
  ]

  aggregate-community-actions
  update-hunting-logging-intensity
  update-agri-grazing-intensity
  update-ecosystem-status
  update-species-populations
  update-income
  update-human-population

  update-plots
  tick
end

;; ---------------------------------------------------------------
;; SCENARIO TICK RULES
;; ---------------------------------------------------------------
to apply-scenario-tick-rules

  if scenario = 3 [
    if years-elapsed >= 2 [
      set hunt-nontarget 0  set hunt-chamois 0
      set hunt-bear      0  set hunt-deer    0
      set log-broadleaf  0
      set agri-intensity 0  set grazing-intensity 0
    ]
  ]

  if scenario = 4 [
    set hunt-nontarget 0  set hunt-chamois 0
    set hunt-bear      0  set hunt-deer    0
    set log-broadleaf  0
    set agri-intensity 0  set grazing-intensity 0
  ]

end

;; ---------------------------------------------------------------
;; PREDATOR DAMAGE (bear damaging livestock)
;; Bear population growing -> more conflict with pastoralists
;; Reduces WTA unless predator compensation is active
;; ---------------------------------------------------------------
to update-predator-damage
  ;; Bear damage scales with bear population relative to start
  let bear-pressure (pop-bear / raw-start-bear)
  ;; Each farmer/pastoralist exposed proportionally
  let damage-this-year bear-pressure * 0.02
  set predator-damage-experienced (predator-damage-experienced + damage-this-year)
end

;; ---------------------------------------------------------------
;; WILLINGNESS TO ACCEPT
;; ---------------------------------------------------------------
to update-willingness-to-accept

  if scenario = 1 [ set accepted-agreement? false  stop ]
  if scenario = 4 [ set accepted-agreement? false  stop ]
  if scenario = 3 [ set accepted-agreement? true   stop ]

  ;; Agreement expired: agents revert
  if not agreement-active? [ set accepted-agreement? false  stop ]

  ;; Once accepted, permanent within active agreement
  if accepted-agreement? [
    ;; BUT: predator damage erodes WTA unless compensated
    if (not agreement-predator-compensation? and predator-damage-experienced > 0.5) [
      ;; High uncompensated damage -> risk of dropping out
      if random-float 1.0 < 0.05 [ set accepted-agreement? false ]
    ]
    stop
  ]

  let income-nudge (income-growth - 100) * 0.003
  let opport-nudge opportunity-perception * 0.08

  ;; Land tenure security increases commitment
  let tenure-nudge (ifelse-value agreement-land-tenure? [ 0.02 ] [ 0 ])

  ;; Predator damage reduces WTA unless compensated
  let predator-penalty (ifelse-value
    (not agreement-predator-compensation? and predator-damage-experienced > 0.3) [ -0.03 ]
    [ 0 ])

  ;; Self-sustenance incentives (beekeeping, eco-tourism) raise WTA
  let selfsustain-nudge (ifelse-value agreement-selfsustain-incentive? [ 0.01 ] [ 0 ])

  ;; Incentive for taking more actions raises WTA
  let action-count-bonus (ifelse-value agreement-action-incentive? [ 0.008 ] [ 0 ])

  set willingness-to-accept clamp01 (
    willingness-to-accept
    + income-nudge + opport-nudge + tenure-nudge
    + predator-penalty + selfsustain-nudge + action-count-bonus
  )

  if random-float 1.0 < willingness-to-accept [
    set accepted-agreement? true
  ]

end

;; ---------------------------------------------------------------
;; CONSERVATION ACTIONS
;; ---------------------------------------------------------------
to take-conservation-actions
  if scenario != 2 [ stop ]

  let lvl (ifelse-value
    willingness-to-accept >= 0.75 [ 3 ]
    willingness-to-accept >= 0.66 [ 2 ]
    willingness-to-accept >= 0.50 [ 1 ]
    [ 0 ])

  ;; Action incentive: more actions taken -> higher level unlocked
  let incentive-bonus (ifelse-value agreement-action-incentive? [ 1 ] [ 0 ])
  set lvl min list 3 (lvl + incentive-bonus)

  set action-reduce-hunting     lvl
  set action-reduce-logging     lvl
  set action-patrol             (ifelse-value rangers-in-agreement? [ lvl ] [ 0 ])
  set action-planting           (ifelse-value agreement-planting?           [ lvl ] [ 0 ])
  set action-plot-merging       (ifelse-value agreement-plot-merging?       [ lvl ] [ 0 ])
  set action-reduce-grazing     (ifelse-value agreement-grazing-reduction?  [ lvl ] [ 0 ])
  set action-reduce-agriculture (ifelse-value agreement-grazing-reduction?  [ lvl ] [ 0 ])

  set opportunity-perception clamp01 (
    opportunity-perception
    + (ifelse-value investor-active?                  [ 0.008 ] [ 0 ])
    + (ifelse-value agreement-market-access?          [ 0.005 ] [ 0 ])
    + (ifelse-value agreement-education?              [ 0.005 ] [ 0 ])
    + (ifelse-value agreement-selfsustain-incentive?  [ 0.006 ] [ 0 ])
  )
end

;; ---------------------------------------------------------------
;; NON-COMPLIANT ACTIONS
;; ---------------------------------------------------------------
to take-non-compliant-actions
  set action-reduce-hunting     0
  set action-reduce-logging     0
  set action-reduce-grazing     0
  set action-reduce-agriculture 0
  set action-patrol             0
  set action-planting           0
  set action-plot-merging       0
  set opportunity-perception clamp01 (opportunity-perception - 0.002)
end

;; ---------------------------------------------------------------
;; AGGREGATE COMMUNITY ACTIONS
;; ---------------------------------------------------------------
to aggregate-community-actions
  let actives humans with [ is-active? and not has-emigrated? ]
  ifelse count actives > 0 [
    set community-patrol-level       mean [ action-patrol ]             of actives
    set community-planting-level     mean [ action-planting ]           of actives
    set community-agri-level         mean [ action-reduce-agriculture ] of actives
    set community-grazing-level      mean [ action-reduce-grazing ]     of actives
    set community-plot-merging-level mean [ action-plot-merging ]       of actives
  ][
    set community-patrol-level       0
    set community-planting-level     0
    set community-agri-level         0
    set community-grazing-level      0
    set community-plot-merging-level 0
  ]
end

;; ---------------------------------------------------------------
;; HUNTING / LOGGING INTENSITY
;; ---------------------------------------------------------------
to update-hunting-logging-intensity

  if scenario = 3 and years-elapsed >= 2 [ stop ]
  if scenario = 4 [ stop ]
  if scenario = 1 [ stop ]

  let eff-patrol min list 3 (floor community-patrol-level + ranger-patrol-level)

  set hunt-nontarget apply-patrol-effect hunt-nontarget eff-patrol
  set hunt-chamois   apply-patrol-effect hunt-chamois   eff-patrol
  set hunt-bear      apply-patrol-effect hunt-bear      eff-patrol
  set hunt-deer      apply-patrol-effect hunt-deer      eff-patrol
  set log-broadleaf  apply-patrol-effect log-broadleaf  eff-patrol

end

to-report apply-patrol-effect [ intensity patrol-lvl ]
  if patrol-lvl = 0 [
    ifelse years-elapsed > 20
      [ report min list 2 (intensity + 1) ]
      [ report intensity ]
  ]
  if patrol-lvl = 1 [ report intensity ]
  if patrol-lvl = 2 [ report max list 0 (intensity - 1) ]
  if patrol-lvl >= 3 [ report max list 0 (intensity - 2) ]
  report intensity
end

;; ---------------------------------------------------------------
;; AGRICULTURE AND GRAZING INTENSITY
;; ---------------------------------------------------------------
to update-agri-grazing-intensity

  if scenario = 3 and years-elapsed >= 2 [ stop ]
  if scenario = 4 [ stop ]
  if scenario = 1 [ stop ]

  let agri-action floor community-agri-level
  if agri-action = 0 [
    if years-elapsed > 20 [ set agri-intensity min list 2 (agri-intensity + 1) ]
  ]
  if agri-action = 2 [ set agri-intensity max list 0 (agri-intensity - 1) ]
  if agri-action >= 3 [ set agri-intensity max list 0 (agri-intensity - 2) ]

  let graz-action floor community-grazing-level
  if graz-action = 0 [
    if years-elapsed > 20 [ set grazing-intensity min list 2 (grazing-intensity + 1) ]
  ]
  if graz-action = 2 [ set grazing-intensity max list 0 (grazing-intensity - 1) ]
  if graz-action >= 3 [ set grazing-intensity max list 0 (grazing-intensity - 2) ]

end

;; ---------------------------------------------------------------
;; ECOSYSTEM STATUS
;; ---------------------------------------------------------------
to update-ecosystem-status
  let bio report-total-biodiversity-raw
  set ecosystem-status (ifelse-value
    bio < 75   [ 0 ]
    bio <= 130 [ 1 ]
    [ 2 ])
end

;; ---------------------------------------------------------------
;; SPECIES POPULATIONS — LOGISTIC GROWTH
;; ---------------------------------------------------------------
to update-species-populations

  let eco-mod (ifelse-value
    ecosystem-status = 0 [ -0.05 ]
    ecosystem-status = 1 [  0.00 ]
    [  0.05 ])

  let graz-competition (ifelse-value
    community-grazing-level >= 2.5 [ -0.02 ]
    community-grazing-level >= 1.5 [  0.00 ]
    [  0.01 ])

  let plant-boost (ifelse-value
    community-planting-level >= 2.5 [ 0.04 ]
    community-planting-level >= 1.5 [ 0.02 ]
    community-planting-level >= 0.5 [ 0.01 ]
    [ 0 ])

  ;; Non-target: planting + beekeeping/habitat quality boost
  let selfsustain-eco-boost (ifelse-value
    (agreement-selfsustain-incentive? and scenario = 2) [ 0.01 ] [ 0 ])

  let k-nt (hunt-to-kill-rate hunt-nontarget + agri-to-mortality agri-intensity)
  set pop-nontarget max list 0 (
    pop-nontarget
    + pop-nontarget * (r-nontarget + eco-mod + selfsustain-eco-boost)
      * (1 - pop-nontarget / K-nontarget)
    - pop-nontarget * k-nt
  )

  let k-ch (hunt-to-kill-rate hunt-chamois)
  set pop-chamois max list 0 (
    pop-chamois
    + pop-chamois * (r-chamois + eco-mod) * (1 - pop-chamois / K-chamois)
    - pop-chamois * k-ch
    - pop-chamois * graz-competition
  )

  let k-br (hunt-to-kill-rate hunt-bear)
  set pop-bear max list 0 (
    pop-bear
    + pop-bear * (r-bear + eco-mod) * (1 - pop-bear / K-bear)
    - pop-bear * k-br
  )

  let k-de (hunt-to-kill-rate hunt-deer)
  set pop-deer max list 0 (
    pop-deer
    + pop-deer * (r-deer + eco-mod) * (1 - pop-deer / K-deer)
    - pop-deer * k-de
    - pop-deer * graz-competition
  )
;; Broadleaf
  let k-bf (log-to-kill-rate log-broadleaf)
  set pop-broadleaf max list 0 (
    pop-broadleaf
    + pop-broadleaf * (r-broadleaf + eco-mod + plant-boost)
      * (1 - pop-broadleaf / K-broadleaf)
    - pop-broadleaf * k-bf
  )

  ;; Sc4: habitat fragmentation da privatizzazione
  if scenario = 4 [
    let habitat-loss 0.06
    set pop-nontarget  max list 0 (pop-nontarget  - pop-nontarget  * habitat-loss)
    set pop-chamois    max list 0 (pop-chamois    - pop-chamois    * habitat-loss)
    set pop-bear       max list 0 (pop-bear       - pop-bear       * habitat-loss)
    set pop-deer       max list 0 (pop-deer       - pop-deer       * habitat-loss * 0.5)
    set pop-broadleaf  max list 0 (pop-broadleaf  - pop-broadleaf  * habitat-loss * 0.3)
  ]
end

to-report hunt-to-kill-rate [ intensity ]
  if intensity = 0 [ report 0.03 ]
  if intensity = 1 [ report 0.08 ]
  if intensity = 2 [ report 0.18 ]
  report 0.08
end

to-report log-to-kill-rate [ intensity ]
  if intensity = 0 [ report 0.01 ]
  if intensity = 1 [ report 0.04 ]
  if intensity = 2 [ report 0.10 ]
  report 0.04
end

to-report agri-to-mortality [ intensity ]
  if intensity = 0 [ report 0.01 ]
  if intensity = 1 [ report 0.03 ]
  if intensity = 2 [ report 0.06 ]
  report 0.03
end

;; ---------------------------------------------------------------
;; INCOME INDEX (baseline = 100)
;; ---------------------------------------------------------------
to update-income

  let accepted-actives humans with [ is-active? and not has-emigrated? and accepted-agreement? ]

  let hunt-lvl  (ifelse-value count accepted-actives > 0
    [ mean [ action-reduce-hunting ] of accepted-actives ] [ 0 ])
  let log-lvl   (ifelse-value count accepted-actives > 0
    [ mean [ action-reduce-logging ] of accepted-actives ] [ 0 ])
  let merge-lvl  community-plot-merging-level
  let agri-lvl   community-agri-level
  let graz-lvl   community-grazing-level
  let patrol-lvl community-patrol-level

  ;; POSITIVE
  let merge-boost (ifelse-value
    merge-lvl >= 2.5 [ 5.0 ]
    merge-lvl >= 1.5 [ 2.5 ]
    merge-lvl >= 0.5 [ 0.5 ]
    [ 0 ])

  let investor-boost     (ifelse-value (investor-active? and scenario = 2)            [ 3.0 ] [ 0 ])
  let edu-boost          (ifelse-value (agreement-education?          and scenario = 2) [ 0.5 ] [ 0 ])
  let market-boost       (ifelse-value (agreement-market-access?      and scenario = 2) [ 0.3 ] [ 0 ])
  let selfsustain-boost  (ifelse-value (agreement-selfsustain-incentive? and scenario = 2) [ 1.5 ] [ 0 ])
  ;; Marginal loss incentive: direct cash transfer for foregone income
  let marginal-loss-comp (ifelse-value (agreement-marginal-loss-incentive? and scenario = 2) [ 1.0 ] [ 0 ])
  ;; Action count incentive: bonus per action taken
  let action-bonus (ifelse-value (agreement-action-incentive? and scenario = 2) [ 0.8 ] [ 0 ])

  let patrol-income (ifelse-value
    patrol-lvl >= 2.5 [ 1.5 ]
    patrol-lvl >= 1.5 [ 1.0 ]
    patrol-lvl >= 0.5 [ 0.5 ]
    [ 0 ])

  ;; NEGATIVE
  let hunt-cost (ifelse-value
    hunt-lvl >= 2.5 [ 2.0 ]
    hunt-lvl >= 1.5 [ 1.0 ]
    hunt-lvl >= 0.5 [ 0.5 ]
    [ 0 ])
  if (scenario = 2 and compensation-enabled?) [ set hunt-cost 0 ]

  let log-cost (ifelse-value
    log-lvl >= 2.5 [ 2.0 ]
    log-lvl >= 1.5 [ 1.0 ]
    log-lvl >= 0.5 [ 0.5 ]
    [ 0 ])
  if (scenario = 2 and compensation-enabled?) [ set log-cost 0 ]

  let agri-cost (ifelse-value
    agri-lvl >= 2.5 [ 1.0 ]
    agri-lvl >= 1.5 [ 0.5 ]
    agri-lvl >= 0.5 [ 0.3 ]
    [ 0 ])
  if merge-lvl > 0.5 [ set agri-cost (agri-cost * 0.5) ]

  let graz-cost (ifelse-value
    graz-lvl >= 2.5 [ 1.5 ]
    graz-lvl >= 1.5 [ 0.7 ]
    graz-lvl >= 0.5 [ 0.3 ]
    [ 0 ])
  if (graz-lvl > 0.5 and not grazing-hay-facility-paid?) [
    set graz-cost (graz-cost + 3.0)
    set grazing-hay-facility-paid? true
  ]

  ;; Predator damage cost (uncompensated bear attacks on livestock)
  let predator-cost (ifelse-value
    (not agreement-predator-compensation? and scenario = 2 and pop-bear > raw-start-bear)
    [ (pop-bear - raw-start-bear) / raw-start-bear * 1.5 ]
    [ 0 ])

  ;; SCENARIO PENALTY
  let scenario-penalty (ifelse-value
    scenario = 3 [ -5.0 ]
    scenario = 4 [ 2.0 ]
    [ 0 ])

  let sc1-drift (ifelse-value
    (scenario = 1 and years-elapsed > 15) [ -0.3 ]
    [ 0 ])

  let net-change (
    merge-boost + investor-boost + edu-boost + market-boost
    + selfsustain-boost + marginal-loss-comp + action-bonus + patrol-income
    - hunt-cost - log-cost - agri-cost - graz-cost - predator-cost
    + scenario-penalty + sc1-drift
  )

  set community-income-index max list 10 (community-income-index + net-change)

  ask humans with [ is-active? and not has-emigrated? ] [
    set income-growth max list 10 (income-growth + net-change)
  ]

end

;; ---------------------------------------------------------------
;; HUMAN POPULATION
;; ---------------------------------------------------------------
to update-human-population

  let base-growth 0.008
  let edu-mod   (ifelse-value (agreement-education? and scenario = 2) [ 0.002 ] [ 0 ])
  let merge-mod (ifelse-value community-plot-merging-level > 1.5 [ 0.001 ] [ 0 ])

  let income-mod (ifelse-value
    community-income-index < 70  [ -0.015 ]
    community-income-index < 90  [ -0.005 ]
    community-income-index < 100 [ -0.002 ]
    [ 0 ])

  let eff-growth base-growth + edu-mod + merge-mod + income-mod
  set human-pop (human-pop + human-pop * eff-growth)
  set human-pop max list 0 (human-pop - emigrants-this-year)

end

;; ---------------------------------------------------------------
;; EMIGRATION
;; ---------------------------------------------------------------
to maybe-emigrate
  let effective-prob prob-to-leave

  if income-growth > 105 [ set effective-prob effective-prob * 0.5  ]
  if income-growth > 115 [ set effective-prob effective-prob * 0.3  ]
  if income-growth < 90  [ set effective-prob min list 1 (effective-prob * 1.5) ]
  if income-growth < 75  [ set effective-prob min list 1 (effective-prob * 2.5) ]

  if ecosystem-status = 0 [
    set effective-prob min list 1 (effective-prob + 0.015)
  ]

  set effective-prob min list 1 (effective-prob + years-elapsed * 0.003)

  if scenario = 3 [ set effective-prob min list 1 (effective-prob * 1.4) ]
  if scenario = 4 [ set effective-prob min list 1 (effective-prob * 2.0) ]

  if random-float 1.0 < effective-prob [
    set has-emigrated? true
    set emigrants-this-year emigrants-this-year + 1
  ]
end

;; ---------------------------------------------------------------
;; REPORTERS
;; ---------------------------------------------------------------
to-report report-total-biodiversity-raw
  let raw-sum   (pop-nontarget + pop-chamois + pop-bear + pop-deer + pop-broadleaf)
  let start-sum (raw-start-nontarget + raw-start-chamois + raw-start-bear + raw-start-deer + raw-start-broadleaf)
  report (raw-sum / start-sum) * 100
end

to-report report-pop-deer
  report (pop-deer / raw-start-deer) * 100
end
to-report report-pop-chamois
  report (pop-chamois / raw-start-chamois) * 100
end
to-report report-pop-bear
  report (pop-bear / raw-start-bear) * 100
end
to-report report-pop-broadleaf
  report (pop-broadleaf / raw-start-broadleaf) * 100
end
to-report report-pop-nontarget
  report (pop-nontarget / raw-start-nontarget) * 100
end
to-report report-ecosystem-status
  report ecosystem-status
end
to-report report-community-income
  report community-income-index
end
to-report report-total-biodiversity
  report report-total-biodiversity-raw
end
to-report report-human-pop
  report human-pop
end
to-report report-human-pop-indexed
  report (human-pop / human-start-pop) * 100
end
to-report report-emigration-rate
  let base-rate 8.0

  ;; Secular trend solo se income NON sta crescendo
  let secular-trend (ifelse-value
    community-income-index > 105 [ 0 ]
    [ years-elapsed * 0.12 ])

  let income-effect (ifelse-value
    community-income-index > 150 [ -5.0 ]
    community-income-index > 120 [ -3.0 ]
    community-income-index > 105 [ -1.0 ]
    community-income-index < 75  [  6.0 ]
    community-income-index < 90  [  3.0 ]
    [ 0 ])

  let eco-effect (ifelse-value ecosystem-status = 0 [ 2.5 ] [ 0 ])

  let scenario-effect (ifelse-value
    scenario = 3 [  4.0 ]
    scenario = 4 [ 10.0 ]
    [ 0 ])

  report min list 40 max list 0
    (base-rate + secular-trend + income-effect + eco-effect + scenario-effect)
end
to-report report-pct-accepted
  let actives count humans with [ is-active? and not has-emigrated? ]
  ifelse actives > 0
    [ report (count humans with [ is-active? and not has-emigrated? and accepted-agreement? ]) / actives * 100 ]
    [ report 0 ]
end
to-report report-total-emigrants
  report human-start-pop - human-pop
end
to-report report-hunt-pressure
  report (hunt-deer + hunt-chamois + hunt-bear + hunt-nontarget) / 4
end
to-report report-pct-emigrated
  report ((human-start-pop - human-pop) / human-start-pop) * 100
end
to-report report-predator-damage
  ;; Community average predator damage index
  let actives humans with [ is-active? and not has-emigrated? ]
  ifelse count actives > 0
    [ report mean [ predator-damage-experienced ] of actives ]
    [ report 0 ]
end
to-report report-agreement-active
  ifelse agreement-active? [ report 1 ] [ report 0 ]
end

;; ---------------------------------------------------------------
;; UTILITY
;; ---------------------------------------------------------------
to-report clamp01 [ x ]
  report max list 0 (min list 1 x)
end

;; ---------------------------------------------------------------
;; INTERFACE SPEC
;;
;; SLIDERS:
;;   scenario            1-4   step 1   default 1
;;   simulation-years   10-50  step 1   default 30
;;   agreement-duration  5-50  step 5   default 20
;;     (how many years the Sc2 agreement lasts before expiry)
;;
;; SWITCHES (Scenario 2):
;;
;;   --- EXTRACTION CONTROLS ---
;;   rangers-in-agreement?          patrol lv2, riduce hunting
;;   compensation-enabled?          compensa perdite hunting/logging
;;
;;   --- MARKET & INCOME ---
;;   agreement-market-access?       opportunity +0.005/yr, income +0.3/yr
;;   agreement-education?           opportunity +0.005/yr, income +0.5/yr
;;   agreement-selfsustain-incentive?  beekeeping/ecoturismo:
;;                                     income +1.5/yr, opportunity +0.006/yr
;;                                     nontarget species boost +0.01
;;
;;   --- INCENTIVE STRUCTURE ---
;;   agreement-marginal-loss-incentive?  cash transfer for foregone income +1.0/yr
;;   agreement-action-incentive?         bonus per nr actions taken:
;;                                       income +0.8/yr, action level +1
;;   agreement-predator-compensation?    bear damage compensated:
;;                                       prevents WTA erosion, removes income cost
;;
;;   --- LAND & AGREEMENT ---
;;   agreement-land-tenure?          WTA initial boost +0.10, nudge +0.02/yr
;;   (agreement-duration slider)     agreement expires after N years:
;;                                   agents revert to non-compliant if not renewed
;;
;;   --- ECOLOGICAL ACTIONS ---
;;   agreement-planting?             broadleaf recovery plant-boost
;;   agreement-plot-merging?         income +0.5-5.0/yr (strongest lever)
;;   agreement-grazing-reduction?    ungulate recovery + one-off hay cost
;;
;; PLOTS:
;;   "target species"     -> deer / chamois / bear / broadleaf / nontarget
;;   "Biodiversity"       -> report-total-biodiversity
;;   "Income (index)"     -> report-community-income
;;   "Human Pop"          -> report-human-pop-indexed
;;   "Emigration Rate"    -> report-emigration-rate
;;   "% Accepting"        -> report-pct-accepted
;;   "Ecosystem Status"   -> report-ecosystem-status
;;   "Hunt Pressure"      -> report-hunt-pressure
;;   "Predator Damage"    -> report-predator-damage
;;   "Agreement Active"   -> report-agreement-active
;; ---------------------------------------------------------------
@#$#@#$#@
@#$#@#$#@
@#$#@#$#@
NetLogo 7.0.0
@#$#@#$#@
@#$#@#$#@
@#$#@#$#@
@#$#@#$#@
@#$#@#$#@
0
@#$#@#$#@
0
@#$#@#$#@
