"""Generate the deterministic South China Sea Day 1 CMO build package."""

from __future__ import annotations

import json
import shutil
import uuid
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DAY = ROOT / "days" / "day-001"
CMO_ROOT = Path(r"C:\Program Files (x86)\Steam\steamapps\common\Command - Modern Operations")
DEPLOY = CMO_ROOT / "Lua" / "DynamicCampaign" / "SCS_Day1"
EXPORT = CMO_ROOT / "ImportExport" / "DynamicCampaign" / "SCS"
NAMESPACE = uuid.UUID("4fd9bafa-b625-4ae4-b881-938edec3335f")


def guid(campaign_id: str) -> str:
    return str(uuid.uuid5(NAMESPACE, campaign_id))


air_packages = [
    # side, prefix, dbid, base, assigned, ready, ready loadouts
    ("BLUE", "BLU-PH-FA50", 6905, "Basa Air Base", 12, 10, [21785]),
    ("BLUE", "BLU-USAF-F16", 5639, "Basa Air Base", 12, 10, [11128] * 6 + [12075] * 2 + [30385] * 2),
    ("BLUE", "BLU-USMC-F35B-AB", 4701, "Puerto Princesa International Airport/Antonio Bautista AB", 10, 8, [10064] * 6 + [18064] * 2),
    ("BLUE", "BLU-USN-P8", 5759, "Puerto Princesa International Airport/Antonio Bautista AB", 4, 3, [30778]),
    ("BLUE", "BLU-USMC-MQ9", 7473, "Puerto Princesa International Airport/Antonio Bautista AB", 4, 3, [8600]),
    ("BLUE", "BLU-USMC-KC130", 6631, "Puerto Princesa International Airport/Antonio Bautista AB", 2, 1, [8408]),
    ("BLUE", "BLU-USAF-F35A", 3835, "Benito Ebeun (Mactan) AB/Mactan-Cebu International Airport", 12, 10, [1836] * 8 + [35085] * 2),
    ("BLUE", "BLU-USAF-KC135", 6621, "Benito Ebeun (Mactan) AB/Mactan-Cebu International Airport", 4, 3, [8835]),
    ("BLUE", "BLU-USAF-E3", 3853, "Benito Ebeun (Mactan) AB/Mactan-Cebu International Airport", 2, 1, [8076]),
    ("BLUE", "BLU-USAF-RC135", 5832, "Benito Ebeun (Mactan) AB/Mactan-Cebu International Airport", 1, 1, [8824]),
    ("BLUE", "BLU-USAF-C130J", 7008, "Benito Ebeun (Mactan) AB/Mactan-Cebu International Airport", 4, 3, [30209]),
    ("BLUE", "BLU-USAF-HH60W", 4366, "Benito Ebeun (Mactan) AB/Mactan-Cebu International Airport", 4, 3, [29536]),
    ("RED", "RED-PLANAF-J16", 2853, "Lingshui AB (PLAN)", 24, 20, [26234] * 10 + [21743] * 10),
    ("RED", "RED-PLANAF-H6J", 7184, "Lingshui AB (PLAN)", 6, 4, [26241]),
    ("RED", "RED-PLANAF-Y8Q-LS", 7418, "Lingshui AB (PLAN)", 4, 3, [27636]),
    ("RED", "RED-PLANAF-KJ500H", 7176, "Lingshui AB (PLAN)", 2, 1, [18300]),
    ("RED", "RED-PLAAF-GJ2-LS", 4725, "Lingshui AB (PLAN)", 4, 3, [25718]),
    ("RED", "RED-PLAAF-J10-SX", 7658, "Suixi AB  (PLAAF)", 24, 20, [25177]),
    ("RED", "RED-PLAAF-J20", 5014, "Suixi AB  (PLAAF)", 12, 10, [28028]),
    ("RED", "RED-PLAAF-J16D", 4632, "Suixi AB  (PLAAF)", 4, 3, [25212]),
    ("RED", "RED-PLAAF-KJ500", 6004, "Suixi AB  (PLAAF)", 2, 1, [18300]),
    ("RED", "RED-PLAAF-YY20", 4975, "Suixi AB  (PLAAF)", 3, 2, [27886]),
    ("RED", "RED-PLAAF-J10-WI", 7658, "Woody Island", 8, 6, [25178]),
    ("RED", "RED-PLANAF-Y8Q-WI", 7418, "Woody Island", 2, 1, [27636]),
    ("RED", "RED-PLAAF-GJ2-WI", 4725, "Woody Island", 2, 1, [25718]),
    ("RED", "RED-PLAAF-J10-FC", 7658, "Fiery Cross Reef", 8, 6, [25178]),
    ("RED", "RED-PLAAF-GJ2-FC", 4725, "Fiery Cross Reef", 4, 3, [25718]),
    ("RED", "RED-PLANAF-Y9JB", 3692, "Fiery Cross Reef", 2, 1, [21676]),
]

ship_groups = [
    ("BLUE", "TG B-1 George Washington CSG", 15.0, 125.1, [
        ("BLU-USN-CVN-0001", 5167), ("BLU-USN-DDG-0001", 2718),
        ("BLU-USN-DDG-0002", 5110), ("BLU-USN-DDG-0003", 5122),
        ("BLU-USN-AOE-0001", 5036)]),
    ("BLUE", "TG B-2 Philippine West Sea SAG", 10.8, 117.8, [
        ("BLU-PHN-FFG-0001", 3545), ("BLU-PHN-FFG-0002", 3545),
        ("BLU-PHN-COR-0001", 3325)]),
    ("BLUE", "TG B-3 America ARG", 10.2, 121.1, [
        ("BLU-USN-LHA-0001", 3563), ("BLU-USN-LPD-0001", 4300),
        ("BLU-USN-DDG-0004", 5169)]),
    ("RED", "TG R-1 Shandong CSG", 16.3, 114.5, [
        ("RED-PLAN-CV-0001", 3187), ("RED-PLAN-DDG-0001", 3883),
        ("RED-PLAN-DDG-0002", 4719), ("RED-PLAN-DDG-0003", 4937),
        ("RED-PLAN-FFG-0001", 4725), ("RED-PLAN-AOE-0001", 2980)]),
    ("RED", "TG R-2 Southern Theater SAG", 12.5, 113.8, [
        ("RED-PLAN-DDG-0004", 3883), ("RED-PLAN-DDG-0005", 4719),
        ("RED-PLAN-DDG-0006", 4937), ("RED-PLAN-FFG-0002", 4725),
        ("RED-PLAN-AOR-0001", 2927)]),
    ("RED", "TG R-3 Hainan Amphibious Group", 17.8, 111.8, [
        ("RED-PLAN-LHD-0001", 3153), ("RED-PLAN-LPD-0001", 4922),
        ("RED-PLAN-LPD-0002", 2006), ("RED-PLAN-DDG-0007", 4719),
        ("RED-PLAN-FFG-0003", 4725)]),
]

submarines = [
    ("BLUE", "BLU-USN-SSN-0001", 828, 16.2, 118.4, [(15.4, 117.8), (14.5, 117.6)]),
    ("BLUE", "BLU-USN-SSN-0002", 827, 12.7, 115.7, [(11.8, 115.2), (11.0, 115.8)]),
    ("BLUE", "BLU-USN-SSN-0003", 830, 10.6, 116.7, [(9.8, 116.2), (9.2, 115.7)]),
    ("BLUE", "BLU-USN-SSN-0004", 837, 9.5, 117.4, [(10.2, 117.1), (11.0, 117.2)]),
    ("RED", "RED-PLAN-SSN-0001", 665, 17.0, 116.0, [(16.0, 116.4), (15.0, 116.0)]),
    ("RED", "RED-PLAN-SSN-0002", 665, 13.5, 117.3, [(12.8, 117.0), (12.0, 117.5)]),
    ("RED", "RED-PLAN-SSK-0001", 695, 11.2, 114.8, [(10.5, 115.0), (9.8, 114.7)]),
    ("RED", "RED-PLAN-SSK-0002", 695, 9.6, 115.5, [(9.0, 115.1), (8.5, 115.7)]),
    ("RED", "RED-PLAN-SSK-0003", 580, 15.0, 119.0, [(14.3, 118.5), (13.5, 118.8)]),
    ("RED", "RED-PLAN-SSBN-0001", 773, 18.1, 111.0, [(17.6, 110.7), (18.0, 110.3)]),
]

embarked_packages = [
    ("BLUE", "BLU-USN-F35C", 4874, "TG B-1 George Washington CSG", 10, 10, [10098] * 6 + [33864] * 4),
    ("BLUE", "BLU-USN-FA18E", 3483, "TG B-1 George Washington CSG", 16, 16, [15483] * 12 + [22742] * 4),
    ("BLUE", "BLU-USN-FA18F", 3482, "TG B-1 George Washington CSG", 8, 8, [15485] * 4 + [22742] * 4),
    ("BLUE", "BLU-USN-EA18G", 4518, "TG B-1 George Washington CSG", 5, 5, [22929] * 3 + [27345] * 2),
    ("BLUE", "BLU-USN-E2D", 7114, "TG B-1 George Washington CSG", 5, 5, [14629]),
    ("BLUE", "BLU-USN-MH60R", 5338, "TG B-1 George Washington CSG", 6, 6, [1101]),
    ("BLUE", "BLU-USN-MH60S", 5337, "TG B-1 George Washington CSG", 4, 4, [25707]),
    ("BLUE", "BLU-USN-CMV22", 4558, "TG B-1 George Washington CSG", 3, 3, [23143]),
    ("BLUE", "BLU-USMC-F35B-ARG", 4701, "TG B-3 America ARG", 10, 10, [10064] * 6 + [18064] * 4),
    ("BLUE", "BLU-USMC-MV22", 7516, "TG B-3 America ARG", 6, 6, [3557]),
    ("BLUE", "BLU-USMC-CH53K", 4029, "TG B-3 America ARG", 2, 2, [20057]),
    ("BLUE", "BLU-USMC-AH1Z", 7514, "TG B-3 America ARG", 2, 2, [26107]),
    ("BLUE", "BLU-USMC-UH1Y", 7515, "TG B-3 America ARG", 2, 2, [13983]),
    ("RED", "RED-PLANAF-J15", 7139, "TG R-1 Shandong CSG", 24, 24, [30185] * 16 + [34295] * 8),
    ("RED", "RED-PLANAF-J15D", 4817, "TG R-1 Shandong CSG", 4, 4, [25212]),
    ("RED", "RED-PLANAF-Z18J", 7357, "TG R-1 Shandong CSG", 2, 2, [17471]),
    ("RED", "RED-PLANAF-Z18F", 7359, "TG R-1 Shandong CSG", 4, 4, [18368]),
    ("RED", "RED-PLANAF-Z9D", 7349, "TG R-1 Shandong CSG", 4, 4, [11837]),
]

templates = [
    ("BLUE", "Philippines/Basa Air Base 2011.inst"),
    ("BLUE", "Philippines/Puerto Princesa International Airport-Antonio Bautista AB.inst"),
    ("BLUE", "Philippines/Benito Ebeun (Mactan) AB Mactan-Cebu International Airport 2011.inst"),
    ("RED", "China/Hainan Island/PLAN Lingshui AB 2011.inst"),
    ("RED", "China/Guangzhou/PLAAF Suixi AB 2011.inst"),
    ("RED", "China/South China Sea Islands and Reefs/Woody Island 2022.inst"),
    ("RED", "China/South China Sea Islands and Reefs/Fiery Cross Reef 2022.inst"),
]


def lua_string(value: str) -> str:
    return json.dumps(value, ensure_ascii=True)


def generate() -> None:
    DAY.mkdir(parents=True, exist_ok=True)
    EXPORT.mkdir(parents=True, exist_ok=True)
    manifest: list[dict[str, object]] = []
    lines = [
        "-- Generated by tools/generate_day1.py; do not hand-edit.",
        "Tool_EmulateNoConsole(true)",
        "local function must(v, label) if v == nil or v == false then error(label .. ': ' .. tostring(_errmsg_)) end return v end",
        "must(Tool_BuildBlankScenario('DB3K_515.db3'), 'blank scenario')",
        "SetScenarioTitle('Fault Line - South China Sea Day 1')",
        "ScenEdit_SetTime({dateformat='YYYYMMDD', date='2026.08.15', time='00:00:00', StartDate='2026.08.15', StartTime='00:00:00', Duration='30:00:00'})",
        "ScenEdit_SetWeather(28, 3, 0.35, 3)",
        "must(ScenEdit_AddSide({side='BLUE'}), 'add BLUE')",
        "must(ScenEdit_AddSide({side='RED'}), 'add RED')",
        "ScenEdit_SetSidePosture('BLUE','RED','H')",
        "ScenEdit_SetSidePosture('RED','BLUE','H')",
        "ScenEdit_SetSideOptions({side='BLUE', awareness='normal', proficiency='Regular', switchto=true})",
        "ScenEdit_SetSideOptions({side='RED', awareness='normal', proficiency='Regular', computerControlledOnly=true})",
        "ScenEdit_SetKeyValue('dc.campaign','SCS-2026')",
        "ScenEdit_SetKeyValue('dc.day','001')",
        "ScenEdit_SetKeyValue('dc.mainland_strikes','false')",
        "ScenEdit_SetKeyValue('dc.guam_strikes','false')",
        "local U = {}",
        "local function add(cid, spec)",
        "  local u = must(ScenEdit_AddUnit(spec), 'add '..cid)",
        "  U[cid] = u.guid",
        "  ScenEdit_SetKeyValue('dc.unit.'..u.guid, cid)",
        "  print('DCMANIFEST|'..cid..'|'..u.guid..'|'..tostring(u.dbid))",
        "  return u",
        "end",
    ]
    for side, filename in templates:
        lines.append(f"must(ScenEdit_ImportInst({lua_string(side)}, {lua_string(filename)}) > 0, 'import {filename}')")

    def emit_air(pkg: tuple) -> None:
        side, prefix, dbid, base, assigned, ready, loadouts = pkg
        for i in range(1, assigned + 1):
            cid = f"{prefix}-{i:02d}"
            loadout = loadouts[(i - 1) % len(loadouts)] if i <= ready else 4
            pguid = guid(cid)
            lines.append(
                f"add({lua_string(cid)},{{side={lua_string(side)},type='Air',unitname={lua_string(cid)},"
                f"dbid={dbid},loadoutid={loadout},base={lua_string(base)},guid={lua_string(pguid)},proficiency='Regular'}})"
            )
            manifest.append({"campaign_id": cid, "side": side, "kind": "aircraft", "dbid": dbid,
                             "loadout_id": loadout, "base": base, "planned_guid": pguid})

    for pkg in air_packages:
        emit_air(pkg)

    offsets = [(0.0, 0.0), (.05, .04), (-.05, .04), (.04, -.05), (-.04, -.05), (.08, 0), (-.08, 0)]
    for side, group, lat, lon, members in ship_groups:
        for index, (cid, dbid) in enumerate(members):
            dy, dx = offsets[index]
            pguid = guid(cid)
            lines.append(
                f"add({lua_string(cid)},{{side={lua_string(side)},type='Ship',unitname={lua_string(cid)},"
                f"dbid={dbid},latitude={lat+dy:.4f},longitude={lon+dx:.4f},heading=225,speed=15,"
                f"group={lua_string(group)},guid={lua_string(pguid)},proficiency='Regular'}})"
            )
            manifest.append({"campaign_id": cid, "side": side, "kind": "ship", "dbid": dbid,
                             "group": group, "planned_guid": pguid})

    group_courses = [
        ("BLUE", "TG B-1 George Washington CSG", [(14.5, 124.9), (13.8, 124.5)]),
        ("BLUE", "TG B-2 Philippine West Sea SAG", [(11.4, 117.3), (12.0, 116.9)]),
        ("BLUE", "TG B-3 America ARG", [(10.6, 120.3), (11.2, 119.7)]),
        ("RED", "TG R-1 Shandong CSG", [(15.5, 114.2), (14.7, 114.0)]),
        ("RED", "TG R-2 Southern Theater SAG", [(11.8, 114.0), (10.8, 114.5)]),
        ("RED", "TG R-3 Hainan Amphibious Group", [(17.0, 112.3), (16.0, 112.9)]),
    ]
    for side, group, points in group_courses:
        course_lua = ",".join(f"{{latitude={p[0]},longitude={p[1]}}}" for p in points)
        lines.append(
            f"local g=must(ScenEdit_GetUnit({{side={lua_string(side)},unitname={lua_string(group)}}}),"
            f"'get group {group}'); g.course={{{course_lua}}}"
        )

    for side, cid, dbid, lat, lon, course in submarines:
        pguid = guid(cid)
        course_lua = ",".join(f"{{latitude={p[0]},longitude={p[1]}}}" for p in course)
        lines.append(
            f"local su=add({lua_string(cid)},{{side={lua_string(side)},type='Submarine',unitname={lua_string(cid)},"
            f"dbid={dbid},latitude={lat},longitude={lon},heading=210,speed=8,guid={lua_string(pguid)},"
            f"proficiency='Regular'}}); su.course={{{course_lua}}}; su.manualAltitude=-150"
        )
        manifest.append({"campaign_id": cid, "side": side, "kind": "submarine", "dbid": dbid,
                         "planned_guid": pguid, "start": [lat, lon], "course": course})

    for pkg in embarked_packages:
        emit_air(pkg)

    lines.extend(mission_lua())
    final_save = (DAY / "day-001-final.save").as_posix()
    build_save = (DAY / "Day1.scen").as_posix()
    finalizer = finalizer_lua(final_save)
    lines.extend([
        "ScenEdit_AddSpecialAction({side='BLUE',ActionNameOrID='Finalize Game-Day 1',"
        "description='Pause at the 24-hour boundary, then execute this once to save and export campaign state.',"
        f"IsActive=true,IsRepeatable=false,ScriptText={lua_string(finalizer)}}})",
        "ScenEdit_SetKeyValue('dc.build.complete','true')",
        f"print('DCBUILD|COMPLETE|tracked={len(manifest)}')",
        f"Command_SaveScen({lua_string(build_save)})",
        "ScenEdit_SpecialMessage('BLUE','Day 1 build complete. Inspect missions and save once through Editor > Save As Scenario before play.')",
    ])
    (DAY / "build.lua").write_text("\n".join(lines) + "\n", encoding="utf-8")
    (DAY / "manifest.json").write_text(json.dumps({"campaign": "SCS-2026", "day": 1, "database": "DB3K_515.db3",
                                                   "units": manifest}, indent=2) + "\n", encoding="utf-8")
    input_data = {
        "campaign": "SCS-2026", "day": 1, "title": "Fault Line - South China Sea Day 1",
        "start": "2026-08-15T00:00:00Z", "operational_pause": "2026-08-16T00:00:00Z",
        "database": "DB3K_515.db3", "player_side": "BLUE",
        "rules": {"mainland_strikes": False, "guam_strikes": False},
        "templates": [{"side": s, "file": f} for s, f in templates],
        "tracked_unit_count": len(manifest),
    }
    (DAY / "input.json").write_text(json.dumps(input_data, indent=2) + "\n", encoding="utf-8")
    (DAY / "validate.lua").write_text(validation_lua(manifest), encoding="utf-8")
    (DAY / "RUNME.txt").write_text(
        "CMO Scenario Editor instructions\n\n"
        "1. Open CMO and enter Scenario Editor mode.\n"
        "2. Open Editor > Lua Script Console.\n"
        "3. Run:\n"
        "   ScenEdit_RunScript('DynamicCampaign/SCS_Day1/build.lua')\n"
        "4. Wait for the Day 1 build-complete message.\n"
        "5. Run validation:\n"
        "   ScenEdit_RunScript('DynamicCampaign/SCS_Day1/validate.lua')\n"
        f"6. Use Editor > Save As Scenario and save to:\n   {DAY / 'Day1.scen'}\n",
        encoding="utf-8",
    )
    DEPLOY.mkdir(parents=True, exist_ok=True)
    for name in ("build.lua", "validate.lua"):
        shutil.copy2(DAY / name, DEPLOY / name)


def mission_lua() -> list[str]:
    return [
        "local function zone(side,prefix,pts) local z={} for i,p in ipairs(pts) do local n=prefix..'-'..i; "
        "must(ScenEdit_AddReferencePoint({side=side,name=n,latitude=p[1],longitude=p[2]}),'rp '..n); z[#z+1]=n end return z end",
        "local function patrol(side,name,subtype,pts,onstation,active) local m=must(ScenEdit_AddMission(side,name,'Patrol',{type=subtype,zone=zone(side,name,pts)}),'mission '..name); "
        "ScenEdit_SetMission(side,m.guid,{isactive=active,OneThirdRule=true,OnStation=onstation,CheckOPA=true,CheckWWR=true}); return m.guid end",
        "local function support(side,name,pts,onstation) local m=must(ScenEdit_AddMission(side,name,'Support',{zone=zone(side,name,pts)}),'mission '..name); "
        "ScenEdit_SetMission(side,m.guid,{isactive=true,OneThirdRule=true,OnStation=onstation,LoopType=1}); return m.guid end",
        "local function assign(ids,m) for _,id in ipairs(ids) do if U[id] then ScenEdit_AssignUnitToMission(U[id],m) end end end",
        "local bcap=patrol('BLUE','BLUE West Luzon CAP','AAW',{{14.0,117.5},{18.0,117.5},{18.0,120.0},{14.0,120.0}},2,true)",
        "assign({'BLU-USAF-F16-01','BLU-USAF-F16-02','BLU-USAF-F16-03','BLU-USAF-F16-04','BLU-USAF-F16-05','BLU-USAF-F16-06','BLU-PH-FA50-01','BLU-PH-FA50-02'},bcap)",
        "local bpcap=patrol('BLUE','BLUE Palawan CAP','AAW',{{8.0,116.8},{12.5,116.8},{12.5,119.3},{8.0,119.3}},2,true)",
        "assign({'BLU-USMC-F35B-AB-01','BLU-USMC-F35B-AB-02','BLU-USMC-F35B-AB-03','BLU-USMC-F35B-AB-04','BLU-USMC-F35B-AB-05','BLU-USMC-F35B-AB-06'},bpcap)",
        "local baew=support('BLUE','BLUE AEW Central',{{12.3,122.0},{14.0,122.0}},1); assign({'BLU-USAF-E3-01'},baew)",
        "local btk=support('BLUE','BLUE Tanker Central',{{11.5,122.5},{14.5,122.5}},1); assign({'BLU-USAF-KC135-01','BLU-USAF-KC135-02','BLU-USMC-KC130-01'},btk)",
        "local basw=patrol('BLUE','BLUE Palawan ASW','ASW',{{8.0,115.0},{12.5,115.0},{12.5,117.5},{8.0,117.5}},1,true); assign({'BLU-USN-P8-01','BLU-USN-P8-02','BLU-USN-P8-03'},basw)",
        "local rc1=patrol('RED','RED Hainan CAP','AAW',{{16.5,109.5},{22.0,109.5},{22.0,114.0},{16.5,114.0}},4,true)",
        "assign({'RED-PLANAF-J16-01','RED-PLANAF-J16-02','RED-PLANAF-J16-03','RED-PLANAF-J16-04','RED-PLAAF-J10-SX-01','RED-PLAAF-J10-SX-02','RED-PLAAF-J20-01','RED-PLAAF-J20-02'},rc1)",
        "local rc2=patrol('RED','RED Spratly CAP','AAW',{{8.0,111.0},{12.0,111.0},{12.0,115.0},{8.0,115.0}},2,true); assign({'RED-PLAAF-J10-FC-01','RED-PLAAF-J10-FC-02','RED-PLAAF-J10-FC-03','RED-PLAAF-J10-FC-04'},rc2)",
        "local raew=support('RED','RED AEW Hainan',{{17.0,112.0},{19.0,112.0}},1); assign({'RED-PLANAF-KJ500H-01','RED-PLAAF-KJ500-01'},raew)",
        "local rtk=support('RED','RED Tanker Hainan',{{18.0,113.0},{20.0,113.0}},1); assign({'RED-PLAAF-YY20-01','RED-PLAAF-YY20-02'},rtk)",
        "local rasw=patrol('RED','RED Central Basin ASW','ASW',{{11.0,114.0},{17.0,114.0},{17.0,118.0},{11.0,118.0}},1,true); assign({'RED-PLANAF-Y8Q-LS-01','RED-PLANAF-Y8Q-LS-02','RED-PLANAF-Y8Q-WI-01'},rasw)",
        "for _,id in ipairs({'BLU-USN-SSN-0001','BLU-USN-SSN-0002','BLU-USN-SSN-0003','BLU-USN-SSN-0004'}) do ScenEdit_SetEMCON('Unit',U[id],'Radar=Passive;Sonar=Passive') end",
        "for _,id in ipairs({'RED-PLAN-SSN-0001','RED-PLAN-SSN-0002','RED-PLAN-SSK-0001','RED-PLAN-SSK-0002','RED-PLAN-SSK-0003','RED-PLAN-SSBN-0001'}) do ScenEdit_SetEMCON('Unit',U[id],'Radar=Passive;Sonar=Passive') end",
        "ScenEdit_SetEMCON('Group','TG B-1 George Washington CSG','Radar=Passive;Sonar=Passive;OECM=Passive')",
        "ScenEdit_SetEMCON('Group','TG R-1 Shandong CSG','Radar=Passive;Sonar=Passive;OECM=Passive')",
    ]


def finalizer_lua(final_save: str) -> str:
    return f"""Tool_EmulateNoConsole(true)
if ScenEdit_GetKeyValue('dc.day001.finalized') == 'true' then ScenEdit_MsgBox('Day 1 was already finalized.',0); return end
ScenEdit_SetKeyValue('dc.day001.finalized','true')
local function report(sideName)
  local s=VP_GetSide({{side=sideName}})
  print('DCREPORT|SIDE|'..sideName)
  for _,v in ipairs(s.losses or {{}}) do print('DCREPORT|LOSS|'..sideName..'|'..tostring(v.type)..'|'..tostring(v.dbid)..'|'..tostring(v.number)..'|'..tostring(v.name)) end
  for _,v in ipairs(s.expenditures or {{}}) do print('DCREPORT|EXP|'..sideName..'|'..tostring(v.type)..'|'..tostring(v.dbid)..'|'..tostring(v.number)..'|'..tostring(v.name)) end
  local ids={{}}
  for _,v in ipairs(s.units or {{}}) do
    local u=ScenEdit_GetUnit({{guid=v.guid}})
    if u then
      ids[#ids+1]=u.guid
      local d=u.damage or {{}}
      print('DCUNIT|'..sideName..'|'..tostring(u.guid)..'|'..tostring(u.name)..'|'..tostring(u.dbid)..'|'..tostring(u.latitude)..'|'..tostring(u.longitude)..'|'..tostring(d.DP_PERCENT_NOW or d.DP_PERCENT or 0)..'|'..tostring(u.fuelstate)..'|'..tostring(u.weaponstate))
    end
  end
  ScenEdit_ExportInst(sideName,ids,{{filename='DynamicCampaign/SCS/day001_'..string.lower(sideName)..'_final.inst',name='SCS Day 1 '..sideName..' final'}})
end
report('BLUE')
report('RED')
Command_SaveScen({lua_string(final_save)})
print('DCREPORT|FINALIZED|001|'..tostring(ScenEdit_CurrentTime()))
ScenEdit_MsgBox('Day 1 final save and exports were created. You may now return to the campaign workspace.',0)"""


def validation_lua(manifest: list[dict[str, object]]) -> str:
    ids = ",".join(lua_string(str(row["campaign_id"])) for row in manifest)
    return f"""Tool_EmulateNoConsole(true)
local ids={{{ids}}}
local missing=0
for _,id in ipairs(ids) do
  local found=false
  for _,sideName in ipairs({{'BLUE','RED'}}) do
    local s=VP_GetSide({{side=sideName}})
    for _,v in ipairs(s.units or {{}}) do
      local u=ScenEdit_GetUnit({{guid=v.guid}})
      if u and u.name==id then found=true break end
    end
    if found then break end
  end
  if not found then missing=missing+1 print('DCVALIDATE|MISSING|'..id) end
end
print('DCVALIDATE|SUMMARY|expected={len(manifest)}|missing='..tostring(missing))
if missing==0 then ScenEdit_MsgBox('Day 1 validation passed: all {len(manifest)} tracked mobile elements are present.',0) else ScenEdit_MsgBox('Day 1 validation failed. Missing: '..missing,0) end
"""


if __name__ == "__main__":
    generate()
