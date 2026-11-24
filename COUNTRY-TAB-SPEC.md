# Country tab: spec and data gaps
dashelectrify, 24 November 2026

## What the framing means (verified)

The COP31 Global Electrification Initiative (cop31.tr concept note, 22 Oct 2026) runs on three pillars:

1. Electrification Forum (IEA) - end-use electrification policy.
2. Tracking Progress (IEA) - the 35-by-35 metric: electricity from ~23% of final energy in 2026 to 35% by 2035.
3. Enabling Distribution Grids, D-GRIDs (Turkish MENR with IRENA) - distribution grid planning, investment, digitalisation, flexibility, resilience.

IRENA's number in that note: global grid investment must more than double, to a cumulative USD 10 trillion by 2035. So "electrification with renewables backed by grids" is not one metric. It is a chain: more end uses on electricity, that electricity clean, and a network able to carry it. A country can be strong on one and fail on the others.

## What the country tab should show

One country at a time, chosen from a search box, in three columns that map to the pillars.

Pledge intel (header strip)
- status: signed nationally / covered by EU endorsement / likely / considering / not a signatory
- region, population, GDP, GDP per capita
- Ember 2030 capacity target and share target with target year

Pillar 1, Electrify
- access rate, rural access, people without access
- electricity consumption per capita (kWh)
- electricity share of final energy, derived (see gap 1)
- distance to the 35% line in percentage points

Pillar 2, Renewables
- renewable share of electricity
- renewable share of final energy
- 2030 share target and the gap to it
- implied annual growth needed to hit the target

Pillar 3, Grids
- transmission and distribution losses as % of output
- RISE score for grid and utility regulation, if loaded
- a plain verdict line: "grid losses above 15% with access below 90%" style

A single diagnosis sentence at the bottom, computed not hardcoded, naming the weakest of the three.

## What is missing today

1. Electricity share of final energy. The 35-by-35 metric itself. Not in the build. Derivable from WDI: electricity consumption per capita against energy use per capita (1 kWh = 0.086 kg oil equivalent). Approximate but free and global.
2. Grid losses. WDI EG.ELC.LOSS.ZS, free, one call. Absent now.
3. RISE regulatory scores. World Bank RISE dataset, xlsx, free. Absent.
4. Grid investment need per country. IRENA's USD 10tn is global only; no open country split. Would need IRENA or IEA paid data. Leave as a global context line.
5. National electrification roadmap existence. No machine-readable global register. The 9 plans I found earlier (France, Indonesia, Korea, Canada, UK, China, EU, Ireland, Nepal) are hand-curated. Could ship as a curated flag with a date.
6. Reliability. SAIDI and SAIFI are not free and global. RISE has a monitoring dimension only.

Items 1 to 3 are buildable this week with three free sources. Items 4 to 6 need curation or paid data and should be labelled as such rather than faked.
