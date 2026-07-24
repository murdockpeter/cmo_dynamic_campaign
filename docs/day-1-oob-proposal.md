# South China Sea campaign: proposed Day 1 order of battle

Status: planning baseline, not yet frozen

Database target: `DB3K_515.db3`

## Situation frame

This is a fictional mid/late-2026 crisis, not a claim about actual deployments.
Following a lethal confrontation near a Philippine-held feature in the Spratlys,
both coalitions have surged forces but have not yet entered unrestricted war.

- **BLUE:** United States and Republic of the Philippines.
- **RED:** People's Republic of China.
- Vietnam, Malaysia, Brunei, Indonesia, and civilian traffic are neutral.
- Attacks on the Chinese mainland, Guam, or civilian infrastructure require an
  explicit escalation event during the first game-day.
- The initial playable area covers the Philippine archipelago, Hainan/Guangdong,
  the Paracels, Spratlys, and the approaches to the Luzon Strait.

The Philippine basing choice is grounded in publicly identified EDCA locations.
Basa, Antonio Bautista, and Mactan are all existing agreed locations. The precise
aircraft detachments below are deliberately fictional.

## BLUE air component

### Basa Air Base, Luzon

CMO template: `Philippines/Basa Air Base 2011.inst` (46 members)

| Element | Assigned | Initially mission-capable | Role |
|---|---:|---:|---|
| PAF FA-50PH | 12 | 10 | Point defense, light maritime strike |
| USAF F-16C Block 50 | 12 | 10 | CAP, SEAD, maritime strike |
| C-130H/J | 2 | 1 | Theater lift |
| Combat rescue helicopters | 2 | 1 | Local SAR |

Base defense/accounting formations:

- 1 PAF base-defense battalion;
- 1 medium-range SAM battalion, represented by subordinate batteries;
- runway, access points, fuel, magazines, radar, shelters, and parking tracked as
  individual site elements beneath the airbase formation.

### Antonio Bautista Air Base, Palawan

CMO template:
`Philippines/Puerto Princesa International Airport-Antonio Bautista AB.inst`
(21 members)

| Element | Assigned | Initially mission-capable | Role |
|---|---:|---:|---|
| USMC F-35B | 10 | 8 | Counter-air, ISR, maritime strike |
| USN P-8A | 4 | 3 | ASW and maritime surveillance |
| MQ-9A | 4 | 3 | Persistent maritime ISR |
| KC-130J | 2 | 1 | Refueling and lift |
| Utility/SAR helicopters | 4 | 3 | SAR and local lift |

Base defense/accounting formations:

- 1 combined base-defense battalion;
- 1 short/medium-range air-defense battalion;
- one Philippine coastal-defense battalion in the Palawan sector.

### Mactan–Benito Ebuen Air Base, Cebu

CMO template:
`Philippines/Benito Ebeun (Mactan) AB Mactan-Cebu International Airport 2011.inst`
(62 members)

| Element | Assigned | Initially mission-capable | Role |
|---|---:|---:|---|
| USAF F-35A | 12 | 10 | Counter-air, strike, ISR |
| KC-135R | 4 | 3 | Forward tanker support |
| E-3G | 2 | 1 | Theater airborne warning |
| RC-135V/W | 1 | 1 | Electronic intelligence |
| C-130J | 4 | 3 | Distributed logistics |
| HH-60W | 4 | 3 | Combat search and rescue |

Base defense/accounting formations:

- 1 combined base-defense battalion;
- 1 U.S. air-and-missile-defense battalion split into deployable batteries;
- the primary BLUE theater fuel and air-munition reserve.

### Rear-area reinforcement node

Andersen AFB remains in the campaign ledger but is initially represented as an
off-map/reduced-detail support node rather than importing its 564-member template.
It holds four KC-46A, two E-11A, and a small bomber alert detachment that is not
released on Day 1. This avoids spending simulation performance on hundreds of
facilities outside the immediate battle area.

### BLUE land-based aviation total

- 46 assigned fighters/strike fighters, about 38 initially mission-capable;
- 4 maritime-patrol aircraft and 4 MALE UAVs;
- 2 land-based AEW aircraft and 1 SIGINT aircraft;
- 6 forward tankers, plus the unreleased rear-area pool;
- lift, rescue, and utility aircraft tracked individually.

## BLUE maritime component

### TG B-1: George Washington Carrier Strike Group

- 1 `CVN 73 George Washington` (`DBID 5167` is a current 2024 DB3K entry);
- 1 Arleigh Burke Flight III destroyer;
- 2 Arleigh Burke Flight IIA destroyers;
- 1 fast combat-support/replenishment ship.

Notional embarked air wing:

| Element | Quantity |
|---|---:|
| F-35C | 10 |
| F/A-18E/F | 24 |
| EA-18G | 5 |
| E-2D | 5 |
| MH-60R/S | 10 |
| CMV-22B | 3 |

Starting disposition: east of Luzon, moving southwest under EMCON with an outer
air-defense patrol and an ASW screen already active.

### TG B-2: Philippine West Sea Surface Action Group

- 2 Jose Rizal-class frigates;
- 1 Pohang-class corvette;
- 1 Philippine Coast Guard large patrol vessel as a separate, non-frontline
  element when the scenario's escalation rules permit.

Starting disposition: west of Palawan, protecting a resupply convoy and avoiding
an offensive approach to the main RED surface groups.

### TG B-3: America Amphibious Ready Group

- 1 America-class LHA;
- 1 San Antonio-class LPD;
- 1 Arleigh Burke Flight IIA destroyer.

Embarked:

- 10 F-35B;
- 12 MV-22B;
- 4 CH-53K;
- 4 AH-1Z;
- 4 UH-1Y;
- a battalion landing team kept as a campaign formation, with its mobile elements
  represented only if a landing or island-defense mission is activated.

Starting disposition: Philippine Sea east of Palawan, moving toward a launch area
but not committed to an amphibious assault.

## BLUE submarine force

Every submarine begins with an actual course and patrol mission rather than being
placed motionless.

| Element | Quantity | Initial task |
|---|---:|---|
| Virginia Block III/IV SSN | 2 | Western Luzon barrier; central-basin trail |
| Virginia Block I/II SSN | 1 | Spratly eastern approach patrol |
| Improved Los Angeles SSN | 1 | Palawan passage/intercept patrol |

The submarines are administratively separate campaign elements even when they
support the same patrol mission. Their exact positions should be randomized inside
bounded patrol-start areas and recorded only in the generated Day 1 manifest.

## RED air component

### PLAN Lingshui Air Base, Hainan

CMO template: `China/Hainan Island/PLAN Lingshui AB 2011.inst` (92 members)

| Element | Assigned | Initially mission-capable | Role |
|---|---:|---:|---|
| J-16 | 24 | 20 | Maritime strike, escort, counter-air |
| H-6J | 6 | 4 | Long-range maritime strike |
| KQ-200 | 4 | 3 | ASW and maritime patrol |
| KJ-500H | 2 | 1 | Naval airborne warning |
| GJ-2 | 4 | 3 | Maritime ISR/strike |

### PLAAF Suixi Air Base, Guangdong

CMO template: `China/Guangzhou/PLAAF Suixi AB 2011.inst` (110 members)

| Element | Assigned | Initially mission-capable | Role |
|---|---:|---:|---|
| J-10C | 24 | 20 | Counter-air |
| J-20A | 12 | 10 | Offensive counter-air |
| J-16D | 4 | 3 | Electronic attack |
| KJ-500A | 2 | 1 | Airborne warning |
| YY-20A | 3 | 2 | Tanking |

### Woody Island

CMO template:
`China/South China Sea Islands and Reefs/Woody Island 2022.inst`
(113 members)

| Element | Assigned | Initially mission-capable | Role |
|---|---:|---:|---|
| J-10C | 8 | 6 | Local CAP/intercept |
| KQ-200 | 2 | 1 | Paracel ASW patrol |
| GJ-2 | 2 | 1 | Local ISR |

### Fiery Cross Reef

CMO template:
`China/South China Sea Islands and Reefs/Fiery Cross Reef 2022.inst`
(111 members)

| Element | Assigned | Initially mission-capable | Role |
|---|---:|---:|---|
| J-10C | 8 | 6 | Spratly CAP/intercept |
| GJ-2 | 4 | 3 | Persistent ISR |
| Y-9 electronic-intelligence variant | 2 | 1 | Theater collection |

Each RED airfield is a campaign formation. Its SAMs, coastal missiles, radars,
runways, fuel, magazines, and garrison are subordinate elements. Lingshui and
Suixi receive one long-range air-defense battalion apiece. Woody Island and Fiery
Cross each receive one composite island-defense battalion with medium/long-range
SAM and anti-ship missile batteries.

### RED land-based aviation total

- 80 assigned fighters/strike fighters/electronic-attack aircraft, about 65
  initially mission-capable;
- 6 bombers;
- 6 maritime-patrol aircraft and 10 MALE UAVs;
- 4 AEW aircraft and 3 tankers;
- 2 electronic-intelligence aircraft.

This gives RED a deliberate land-based numerical and distance advantage.

## RED maritime component

### TG R-1: Shandong Carrier Group

- 1 `Shandong` (`DBID 3187`);
- 1 Type 055 cruiser/destroyer;
- 2 Type 052D/DL destroyers;
- 1 Type 054A frigate;
- 1 Type 901 fast combat-support ship.

Embarked:

| Element | Quantity |
|---|---:|
| J-15 | 24 |
| J-15D | 4 |
| Z-18J/Z-18F and Z-9 helicopters | 10 |

Starting disposition: north-central South China Sea, moving toward the Paracels
behind a land-based reconnaissance and fighter screen.

### TG R-2: Southern Theater Surface Action Group

- 1 Type 055;
- 2 Type 052DL;
- 1 Type 054A/AG;
- 1 Type 903A replenishment ship.

Starting disposition: central basin, positioned to pressure the Palawan approaches
without beginning inside immediate Philippine weapon range.

### TG R-3: Hainan Amphibious Group

- 1 Type 075 LHD;
- 2 Type 071 LPDs;
- 1 Type 052D destroyer;
- 1 Type 054A frigate.

Its embarked marine brigade remains organized into explicit battalions in the
ledger. Only the battalion landing team selected for Day 1 receives detailed CMO
mobile elements.

Starting disposition: southeast of Hainan, apparently exercising but capable of
moving toward the Paracels or Spratlys.

## RED submarine force

| Element | Quantity | Initial task |
|---|---:|---|
| Type 093B SSN | 2 | Outer carrier screen; Luzon approach patrol |
| Type 039C Yuan SSK | 2 | Spratly choke-point patrols |
| Type 039B Yuan SSK | 1 | Palawan approach patrol |
| Type 094A SSBN | 1 | Protected Hainan bastion patrol |

The SSBN is a strategic asset and does not receive an offensive surface-hunting
mission unless escalation rules release it. RED's diesel boats begin nearer likely
contact areas, while its SSNs start farther away and in motion.

## Initial support-mission set

### BLUE

- one E-3 orbit over the central Philippines, with the second aircraft in reserve;
- one E-2D carrier orbit and a second launch-ready section;
- tanker tracks east of Luzon and over the central Philippines;
- P-8 patrol boxes west of Luzon and west/southwest of Palawan;
- MQ-9 surveillance corridors that remain outside declared RED SAM envelopes;
- standing CAPs over Basa, Palawan, the carrier group, and the amphibious group;
- organic helicopter ASW screens for both major naval groups;
- one land-based and one carrier/ARG combat-SAR package.

### RED

- one KJ-500 orbit over Hainan and one nearer the Paracels;
- YY-20 tanker support behind the Hainan fighter screen;
- KQ-200 patrols in the northern basin, Paracels, and east of the Spratlys;
- standing CAP over Hainan, Woody Island, Fiery Cross, and Shandong;
- J-16/J-16D maritime-strike packages held ready but not airborne at scenario start;
- H-6J strike aircraft on staged alert, requiring a positive release event;
- organic helicopter ASW screens for all three surface groups.

## Land formations tracked from the outset

Even though Day 1 is predominantly air and maritime, the ledger should include:

### BLUE

- three airbase-defense battalions;
- two air-and-missile-defense battalions, divided into named batteries;
- two Philippine BrahMos coastal-defense battalions;
- one U.S. Marine littoral anti-ship battalion/task force with an NMESIS battery;
- the ARG battalion landing team.

### RED

- two long-range mainland/Hainan air-defense battalions;
- two composite island-defense battalions;
- two Hainan coastal anti-ship missile battalions;
- three amphibious marine battalions under the embarked brigade;
- airfield security/garrison battalions at all four populated bases.

A battalion is always an explicit campaign record. Its batteries, companies, and
individual CMO units are child elements, which allows partial losses without
declaring an entire battalion destroyed.

## Why this is a useful starting balance

- RED has more local aircraft, more surface combatants, more submarines, shorter
  logistics lines, and strong forward SAM coverage.
- BLUE has four capable SSNs, better distributed airborne ISR, two aviation ships,
  Philippine geography, and stronger long-range reinforcement options.
- Neither side begins with its maximum strategic force. A second carrier, Guam
  bomber surge, Japanese/Australian combat entry, additional PLA bomber regiments,
  more missile forces, and follow-on submarines remain campaign decisions.
- Initial readiness below 100 percent creates real repair and sortie-generation
  decisions instead of treating every platform as perpetually available.

## Items to freeze before generation

1. Exact scenario date and 24-hour start time.
2. The triggering incident and initial political/weapon-release constraints.
3. Whether Japan and Australia are neutral supporters, full BLUE members, or
   possible later entrants.
4. Whether Andersen is off-map, simplified, or fully represented.
5. Whether the campaign permits attacks on mainland bases during Day 1.
6. Exact aircraft DBID and loadout variants, verified in CMO's Database Viewer.
7. Named ships and submarine identities versus fictional hull names of the same
   database classes.
8. Desired uncertainty: known OOB with hidden positions, or partially uncertain
   OOB with probabilistic deployments.

## Public grounding

- U.S. Department of Defense, EDCA locations:
  https://www.defense.gov/serve-from-netstorage/News/News-Stories/Article/Article/3350297/new-edca-sites-named-in-the-philippines/index.html
- Pacific Air Forces, Cope Thunder operations from Basa in 2025:
  https://www.pacaf.af.mil/News/Article-Display/Article/4235528/press-release-us-and-philippine-air-forces-to-begin-exercise-cope-thunder/
- U.S. Department of Defense, 2025 China Military Power Report:
  https://media.defense.gov/2025/Dec/23/2003849070/-1/-1/1/ANNUAL-REPORT-TO-CONGRESS-MILITARY-AND-SECURITY-DEVELOPMENTS-INVOLVING-THE-PEOPLES-REPUBLIC-OF-CHINA-2025.PDF
- U.S. Marine Corps, NMESIS deployment in the Philippines during Balikatan 2025:
  https://www.imef.marines.mil/Media-Room/Stories/Article/Article/4168255/us-marine-corps-joint-force-deploy-nmesis-to-batanes-for-exercise-balikatan-2025/
