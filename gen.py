import json, random, csv
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter

random.seed(20260915)
ARIAL = Font(name="Arial", size=10); BOLD = Font(name="Arial", size=10, bold=True)
HEAD = PatternFill("solid", fgColor="DDDDDD")

# ---------- cast ----------
cast = [
 # name, class, spec, role, team, main, discord, notes
 ("Dunmar","Warrior","Protection","Tank","vanguard",True,"dunmar_mt","raid lead; org admin"),
 ("Maelis","Priest","Holy","Healer","vanguard",True,"maelis.heals","officer; loot master"),
 ("Thorvik","Warrior","Fury","Melee","vanguard",True,"thorvik_fury","review opt-in"),
 ("Kessa","Rogue","Combat","Melee","vanguard",True,"kessa_daggers","top parser"),
 ("Orla","Druid","Restoration","Healer","vanguard",True,"orla_moon","also alt on hearth"),
 ("Orlette","Mage","Frost","Ranged","hearth",False,"orla_moon","Orla's alt"),
 ("Brann","Hunter","Marksmanship","Ranged","hearth",True,"brann_bows","family; dies to whelps"),
 ("Pip","Mage","Frost","Ranged","hearth",True,"pip_frost","APPLICANT — not in roster sheet; applies via form"),
]
syl_a = ["Ael","Bor","Cal","Dra","El","Fen","Gar","Hal","Isk","Jor","Kel","Lor","Mor","Nal","Ory","Pel","Quen","Ral","Sel","Tor","Ul","Vae","Wyn","Yor","Zan"]
syl_b = ["ric","wen","dan","mir","thas","gorn","lith","vyn","dor","ael","ana","ric","ise","mund","dis","vor"]
used = {c[0] for c in cast}
def name():
    while True:
        n = random.choice(syl_a)+random.choice(syl_b)
        if n not in used: used.add(n); return n
def handle(n): return n.lower()+"_"+random.choice(["wow","raids","era","classic","az"])

# Alliance Era class/spec/role pools
def build_team(slug, comp):
    rows=[]
    for cls,spec,role,count in comp:
        for _ in range(count):
            n=name(); rows.append((n,cls,spec,role,slug,True,handle(n),""))
    return rows
vanguard = build_team("vanguard",[
 ("Warrior","Protection","Tank",2),("Druid","Feral","Tank",1),
 ("Priest","Holy","Healer",4),("Paladin","Holy","Healer",3),("Druid","Restoration","Healer",1),
 ("Warrior","Fury","Melee",8),("Rogue","Combat","Melee",4),
 ("Mage","Frost","Ranged",6),("Warlock","Destruction","Ranged",4),("Hunter","Marksmanship","Ranged",4),("Priest","Shadow","Ranged",1),
])
ember = build_team("ember",[
 ("Warrior","Protection","Tank",2),("Priest","Holy","Healer",3),("Paladin","Holy","Healer",2),
 ("Warrior","Fury","Melee",4),("Rogue","Combat","Melee",3),("Mage","Frost","Ranged",4),("Warlock","Destruction","Ranged",2),("Hunter","Marksmanship","Ranged",2),
])
hearth = build_team("hearth",[
 ("Warrior","Protection","Tank",1),("Paladin","Holy","Healer",1),("Priest","Holy","Healer",1),
 ("Warrior","Fury","Melee",2),("Rogue","Combat","Melee",1),("Mage","Frost","Ranged",1),("Warlock","Destruction","Ranged",1),("Hunter","Marksmanship","Ranged",1),
])
roster = [c for c in cast if c[0]!="Pip"] + vanguard + ember + hearth
teams = {"vanguard":"Vanguard","ember":"Ember","hearth":"Hearth"}

# ---------- helpers ----------
def sheet(wb, title, headers, rows, widths=None, legend=None):
    ws = wb.create_sheet(title) if wb.worksheets and wb.worksheets[0].title=="Sheet" and False else wb.create_sheet(title)
    ws.append(headers)
    for c in ws[1]: c.font=BOLD; c.fill=HEAD
    for r in rows: ws.append(list(r))
    for row in ws.iter_rows(min_row=2):
        for c in row: c.font=ARIAL
    ws.freeze_panes="A2"
    for i,h in enumerate(headers,1):
        ws.column_dimensions[get_column_letter(i)].width = (widths[i-1] if widths else max(12, min(40, len(str(h))+6)))
    if legend:
        lg = wb.create_sheet("Legend")
        for line in legend: lg.append([line])
        for row in lg.iter_rows():
            for c in row: c.font=ARIAL; c.alignment=Alignment(wrap_text=False)
        lg.column_dimensions["A"].width=110
    return ws
def finish(wb, path):
    if "Sheet" in wb.sheetnames: del wb["Sheet"]
    wb.save(path)
def write_csv(path, headers, rows):
    with open(path,"w",newline="") as f:
        w=csv.writer(f); w.writerow(headers); w.writerows(rows)

# ---------- 1. roster.xlsx ----------
headers=["Character","Realm","Class","Spec","Role","Team","Main/Alt","Discord","Notes"]
rows=[(n,"Whitemane",cls,spec,role,teams[team],"Main" if main else "Alt",disc,notes) for (n,cls,spec,role,team,main,disc,notes) in roster]
wb=Workbook(); sheet(wb,"Roster",headers,rows,[14,12,10,13,9,10,9,18,34],legend=[
 "ROSTER IMPORT SHEET — test data for the Classic Era test environment (Module J, kind = roster).",
 "One row per character. Column names are matched by synonym in the mapping UI; keep them or rename freely.",
 "Character: in-game name (unique per realm). Realm: Era realm. Class/Spec/Role: vocabulary per patch (Role = Tank | Healer | Melee | Ranged).",
 "Team: Vanguard (40-man, Naxx/Ony) | Ember (20-man, ZG/AQ20) | Hearth (10-man, UBRS). Main/Alt: one Main per person; alts share the Discord handle.",
 "Discord: username; onboarding auto-claims characters whose handle matches. Notes: free text (ignored by import except stored).",
 "Pip is intentionally absent: he applies through the recruitment form (applications.json) and is added on acceptance.",
 "Expected import result: %d creates, 0 errors; re-import → 0 creates, %d updates/skips, 0 duplicates." % (len(rows), len(rows)),
]); finish(wb,"roster.xlsx"); write_csv("roster.csv",headers,rows)

# ---------- 2. raid-night roster (Vanguard Thu Naxx) ----------
van = [r for r in roster if r[4]=="vanguard"]
tanks=[r for r in van if r[3]=="Tank"]; heals=[r for r in van if r[3]=="Healer"]
melee=[r for r in van if r[3]=="Melee"]; ranged=[r for r in van if r[3]=="Ranged"]
order = tanks+heals+melee+ranged
seats=[]; special={"Dunmar":"MT · Patchwerk hateful soaker 1 (high)","Kessa":"Thaddius charge caller · left (high)","Maelis":"Loatheb spore group lead G2 (low)","Thorvik":"Loatheb spore group lead G5 (low)"}
i=0
for g in range(1,9):
    for s in range(1,6):
        if i < 40:
            r=order[i]; seats.append((g,s,r[0],r[1],r[2],r[3],special.get(r[0],""))); i+=1
bench=[(0,0,r[0],r[1],r[2],r[3],"BENCH (rotation)") for r in order[40:]]
headers=["Group","Slot","Character","Class","Spec","Role","Assignment / special seat"]
wb=Workbook(); sheet(wb,"Thu Naxx + Ony",headers,seats+bench,[8,6,14,10,13,9,44],legend=[
 "RAID-NIGHT ROSTER SHEET — test data (Module J, kind = raid_roster). Team: Vanguard. Zone: Naxxramas (Construct/Plague wings) + Onyxia. Date: next Thursday 20:00 server.",
 "Group/Slot map to Raid-Helper groups; Group 0 = bench. Assignment text becomes seat_assignments.note; special seats are matched by name to boss_guides.special_seats.",
 "Expected: raid_events(planned) created, Raid-Helper event created (fixture mode), 40 pending seats + 3 bench rows, DMs to pre-assigned players; fixture signups confirm 38 seats, 2 stay pending.",
]); finish(wb,"raid-roster-vanguard-naxx-thu.xlsx"); write_csv("raid-roster-vanguard-naxx-thu.csv",headers,seats+bench)

# ---------- 3. wishlists.xlsx ----------
pools={
 ("Warrior","Fury"):["Iblis, Blade of the Fallen Seraph","The Hungering Cold","Kiss of the Spider","Slayer's Crest","Ring of the Dreadnaught","Deathbringer","Vis'kag the Bloodletter","Dreadnaught Breastplate"],
 ("Warrior","Protection"):["Dreadnaught Breastplate","Glyph of Deflection","The Face of Death","Ring of the Dreadnaught","Claymore of Unholy Might","Shield of Condemnation","Eskhandar's Collar"],
 ("Rogue","Combat"):["Kingsfall","Maexxna's Fang","Slayer's Crest","Kiss of the Spider","Bonescythe Breastplate","The Hungering Cold","Vis'kag the Bloodletter"],
 ("Priest","Holy"):["Wraith Blade","Eye of Diminution","Ring of the Dreamwalker","Redemption Robes? no","Robes of Faith","The Soul Harvester's Bindings","Halo of Transcendence"],
 ("Priest","Shadow"):["Wraith Blade","Plagueheart Robe","Ring of the Dreadnaught","The Restrained Essence of Sapphiron"],
 ("Paladin","Holy"):["Redemption Tunic","Ring of the Dreamwalker","Eye of Diminution","The Soul Harvester's Bindings","Judgement Crown"],
 ("Druid","Restoration"):["Dreamwalker Tunic","Ring of the Dreamwalker","Eye of Diminution","Stormrage Cover"],
 ("Druid","Feral"):["Dreamwalker Tunic","Ring of the Dreadnaught","The Face of Death","Stormrage Cover"],
 ("Mage","Frost"):["Frostfire Robe","Wraith Blade","The Restrained Essence of Sapphiron","Ring of the Dreadnaught? no","Band of Reanimation","Netherwind Crown"],
 ("Warlock","Destruction"):["Plagueheart Robe","Wraith Blade","The Restrained Essence of Sapphiron","Band of Reanimation","Nemesis Skullcap"],
 ("Hunter","Marksmanship"):["Nerubian Slavemaker","Cryptstalker Tunic","Kiss of the Spider","Slayer's Crest","Dragonstalker's Helm"],
}
pools = {k:[x for x in v if "no" not in x] for k,v in pools.items()}
wl=[]
for (n,cls,spec,role,team,main,disc,notes) in roster:
    items=pools.get((cls,spec),pools[("Warrior","Fury")])
    k=random.randint(3,min(5,len(items)))
    picks=random.sample(items,k) if n!="Thorvik" else ["Deathbringer","Iblis, Blade of the Fallen Seraph","The Hungering Cold","Kiss of the Spider","Slayer's Crest"]
    for rank,it in enumerate(picks,1): wl.append((n,it,rank,"" if n!="Thorvik" or rank!=1 else "SR target this week"))
headers=["Character","Item","Rank","Note"]
wb=Workbook(); sheet(wb,"Wishlists",headers,wl,[14,38,7,28],legend=[
 "WISHLIST IMPORT SHEET — test data (Module J, kind = wishlists). Items are Classic Era Naxxramas/Onyxia names; resolved by name against the items table (seed loads these names).",
 "Rank 1 = most wanted. Rows are flagged 'imported' until the member edits once.",
 "Thorvik rank 1 = Deathbringer (his Onyxia SR); the loot-sheet expectation depends on it.",
]); finish(wb,"wishlists.xlsx"); write_csv("wishlists.csv",headers,wl)

# ---------- 4. availability.xlsx ----------
days=["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]
def avail(n):
    if n=="Thorvik": return ["19:00-23:00","19:00-23:00","","19:00-23:30","","18:00-23:00",""]
    if n=="Pip": return ["","","","","","14:00-23:00","14:00-22:00"]
    if n=="Brann": return ["","","","","","18:00-22:00","18:00-22:00"]
    if n=="Dunmar": return ["19:00-23:00"]*5+["18:00-23:00","18:00-22:00"]
    if n=="Orla": return ["","19:00-23:00","19:00-23:00","19:00-23:30","","18:00-22:00","18:00-22:00"]
    base=[]
    for d in days:
        p = 0.85 if d in ("Tue","Wed","Thu") else (0.6 if d in ("Sat","Sun") else 0.35)
        base.append(random.choice(["19:00-23:00","19:30-23:00","20:00-23:30"]) if random.random()<p else "")
    return base
av=[(r[0],*avail(r[0])) for r in roster]+[("Pip",*avail("Pip"))]
headers=["Character"]+days
wb=Workbook(); sheet(wb,"Availability",headers,av,[14]+[13]*7,legend=[
 "AVAILABILITY IMPORT SHEET — test data (Module J, kind = availability). Windows in server time (24h); blank = unavailable.",
 "Expected: recurring availability rows; heatmap shows Tue–Thu strongest for Vanguard; Hearth is a weekend team; Pip is Sat/Sun only (drives placement to Saturday).",
]); finish(wb,"availability.xlsx"); write_csv("availability.csv",headers,av)

# ---------- 5. seed.json ----------
seed={
 "org":{"name":"Test Org","discord_guild_id":"TEST_GUILD_ID","patch":"classic_era","realm":"Whitemane","faction":"Alliance"},
 "teams":[
  {"slug":"vanguard","name":"Vanguard","size":40,"zones":["Naxxramas","Onyxia's Lair"],"raid_days":["Tue","Thu"],"timezone":"America/New_York","channels":{"signup":"TEST_CH_VANGUARD_SIGNUPS","officer":"TEST_CH_VANGUARD_OFFICERS","sr_token_thread":"TEST_TH_VANGUARD_SR","ui_updates":"TEST_CH_UI_UPDATES"},"loot_config":{"method":"sr_roll","attendance_window_weeks":6,"weights":{"attendance":0.6,"recency":0.3,"wishlist_rank":0.1}}},
  {"slug":"ember","name":"Ember","size":20,"zones":["Zul'Gurub","Ruins of Ahn'Qiraj"],"raid_days":["Wed"],"timezone":"America/New_York","channels":{"signup":"TEST_CH_EMBER_SIGNUPS","officer":"TEST_CH_EMBER_OFFICERS","sr_token_thread":"TEST_TH_EMBER_SR","ui_updates":"TEST_CH_UI_UPDATES"},"loot_config":{"method":"priority_points","attendance_window_weeks":8}},
  {"slug":"hearth","name":"Hearth","size":10,"zones":["Upper Blackrock Spire"],"raid_days":["Sat"],"timezone":"America/New_York","channels":{"signup":"TEST_CH_HEARTH_SIGNUPS","officer":"TEST_CH_HEARTH_OFFICERS","sr_token_thread":"TEST_TH_HEARTH_SR","ui_updates":"TEST_CH_UI_UPDATES"},"loot_config":{"method":"sr_roll","attendance_window_weeks":4}}
 ],
 "zones":[
  {"name":"Naxxramas","size":40,"lockout_days":7,"credit_weight":1.0,"softres_instance_id":None},
  {"name":"Onyxia's Lair","size":40,"lockout_days":5,"credit_weight":0.5,"softres_instance_id":None},
  {"name":"Zul'Gurub","size":20,"lockout_days":3,"credit_weight":0.5,"softres_instance_id":None},
  {"name":"Ruins of Ahn'Qiraj","size":20,"lockout_days":3,"credit_weight":0.5,"softres_instance_id":None},
  {"name":"Upper Blackrock Spire","size":10,"lockout_days":3,"credit_weight":0.25,"softres_instance_id":None}
 ],
 "raid_templates":[
  {"team":"vanguard","zone":"Naxxramas","name":"Naxx 40","seats":[{"role":"Tank","count":4,"criticality":"high"},{"role":"Healer","count":10,"criticality":"medium"},{"role":"Melee","count":12,"criticality":"low"},{"role":"Ranged","count":14,"criticality":"low"}]},
  {"team":"vanguard","zone":"Onyxia's Lair","name":"Ony 40","seats":[{"role":"Tank","count":4,"criticality":"high"},{"role":"Healer","count":10,"criticality":"medium"},{"role":"Melee","count":12,"criticality":"low"},{"role":"Ranged","count":14,"criticality":"low"}]},
  {"team":"hearth","zone":"Upper Blackrock Spire","name":"UBRS 10","seats":[{"role":"Tank","count":1,"criticality":"high"},{"role":"Healer","count":2,"criticality":"medium"},{"role":"Melee","count":3,"criticality":"low"},{"role":"Ranged","count":4,"criticality":"low"}]}
 ],
 "boss_guides":[
  {"encounter":"Patchwerk","special_seats":[{"label":"Hateful Strike soaker 1","criticality":"high"},{"label":"Hateful Strike soaker 2","criticality":"high"},{"label":"Hateful Strike soaker 3","criticality":"high"}],"officer_notes":{"Hateful Strike":"Top-3 HP melee soak; healers assign two per soaker."}},
  {"encounter":"Loatheb","special_seats":[{"label":"Spore group lead G%d" % g,"criticality":"low"} for g in range(1,9)],"officer_notes":{"Fungal Bloom":"Rotate spores by group; pop cooldowns inside the buff."}},
  {"encounter":"Thaddius","special_seats":[{"label":"Charge caller · left","criticality":"high"},{"label":"Charge caller · right","criticality":"high"}],"officer_notes":{"Polarity Shift":"Move by charge; stacking wrong charge kills the raid."}},
  {"encounter":"Onyxia","special_seats":[{"label":"Whelp tank","criticality":"high"},{"label":"Add kiter","criticality":"high"}],"officer_notes":{"Bellowing Roar":"Fear at phase 3; spread before Flame Breath."}}
 ],
 "social_edges":[{"a":"thorvik_fury","b":"pip_frost","kind":"must_with"},{"a":"brann_bows","b":"orla_moon","kind":"prefer_with"}],
 "settings":{"app_env":"test","game_patch":"classic_era","softres_auto_create":False,"raid_helper_mode":"fixture","discord_mode":"sandbox","softres_mode":"fixture","logs_mode":"fixture","logs_ingest":False,"reviews_enabled":True,"llm_rephrase":False,"sample_per_band":20,"band_min_n":20},
 "items_seed_note":"Load the Era item names used in wishlists.xlsx into items (patch classic_era) with slot/class_mask from any Era item source; ids may be provisional in test."
}
json.dump(seed,open("seed.json","w"),indent=1)

# ---------- 6. fixtures ----------
disc_users=[{"discordId":"TEST_%05d"%i,"username":r[6],"displayName":r[0],"roles":["team:"+r[4]],"joinedAt":"2026-09-10T18:00:00Z"} for i,r in enumerate(roster,1)]
disc_users.append({"discordId":"TEST_PIP","username":"pip_frost","displayName":"Pip","roles":[],"joinedAt":"2026-09-14T21:00:00Z"})
present=[r[6] for r in order[:40] if r[0]!="Thorvik"]
discord={"guildId":"TEST_GUILD_ID","channels":{k:v for t in seed["teams"] for k,v in {t["slug"]+"_"+kk:vv for kk,vv in t["channels"].items()}.items()},
 "users":disc_users,
 "onboarding":{"thorvik_fury":{"claimed":"Thorvik","plays_with":["pip_frost"],"review_opt_in":True,"timezone":"America/New_York"},"pip_frost":{"claimed":None,"routed_to":"application"}},
 "voice_presence":{"event:vanguard-thu":{"at_start":present,"late":{"thorvik_fury":"20:07"}}}}
json.dump(discord,open("fixtures/discord.json","w"),indent=1)
signups=[]
for r in order[:40]:
    st="accepted"
    signups.append({"name":r[0],"class":r[1],"spec":r[2],"status":st,"signedAt":"2026-09-16T02:00:00Z"})
for r in order[40:44]: signups.append({"name":r[0],"class":r[1],"spec":r[2],"status":"bench","signedAt":"2026-09-16T03:00:00Z"})
signups[5]["status"]="tentative"; signups[9]["status"]="tentative"
rh={"events":[
 {"id":"RH_EVENT_VANGUARD_THU","teamSlug":"vanguard","channelId":"TEST_CH_VANGUARD_SIGNUPS","title":"Naxx (Construct/Plague) + Ony","zone":"Naxxramas","startTime":"2026-09-17T20:00:00-04:00","softresId":"SR_TEST_NAXX_1","signups":signups},
 {"id":"RH_EVENT_HEARTH_SAT","teamSlug":"hearth","channelId":"TEST_CH_HEARTH_SIGNUPS","title":"UBRS family run","zone":"Upper Blackrock Spire","startTime":"2026-09-19T19:00:00-04:00","softresId":None,
  "signups":[{"name":r[0],"class":r[1],"spec":r[2],"status":"accepted","signedAt":"2026-09-17T01:00:00Z"} for r in hearth]+[{"name":"Thorvik","class":"Warrior","spec":"Fury","status":"accepted","signedAt":"2026-09-17T01:10:00Z"},{"name":"Pip","class":"Mage","spec":"Frost","status":"accepted","signedAt":"2026-09-17T01:12:00Z"}]}
]}
json.dump(rh,open("fixtures/raid-helper.json","w"),indent=1)
reserves=[]
for r in order[:40]:
    top=[w for w in wl if w[0]==r[0]]
    if top: reserves.append({"name":r[0],"class":r[1],"item":top[0][1]})
reserves.append({"name":"Kessa","class":"Rogue","item":"Kingsfall"})  # flagged: already wears it per gear fixture
sr={"raids":[{"raidId":"SR_TEST_NAXX_1","instance":"naxxramas","reservesPerPlayer":2,"reserves":reserves}]}
json.dump(sr,open("fixtures/softres.json","w"),indent=1)
open("fixtures/gargul-award-export.txt","w").write("""# ILLUSTRATIVE award export — replace with a real Gargul export string/CSV; the gargul adapter parses by header row.
# columns: date,character,item,method,note
2026-09-17,Thorvik,Deathbringer,sr_roll,won roll 87 vs 62
2026-09-17,Maelis,Ring of the Dreamwalker,sr_roll,uncontested SR
2026-09-17,Kessa,Kiss of the Spider,roll,ms roll 94
2026-09-17,Dunmar,Glyph of Deflection,priority,tank priority
""")
json.dump({
 "_readme":"Fill in PUBLIC Classic Era report codes (vanilla.warcraftlogs.com) and map test characters to real player names in those reports. The test-env ingest applies log_name_map BEFORE matching by character name. Choose a Naxx report with Patchwerk, Loatheb, Thaddius kills and at least one wipe.",
 "reports":[{"code":"FILL_ME_1","team":"vanguard","note":"Naxx kills + wipes for lethality"},{"code":"FILL_ME_2","team":"vanguard","note":"Onyxia kill (for the Thorvik review)"}],
 "log_name_map":{"Thorvik":"<Fury Warrior in report>","Kessa":"<Combat Rogue in report>","Dunmar":"<Prot Warrior tank in report>","Maelis":"<Holy Priest in report>","Orla":"<Resto Druid in report>"},
 "gear_fixture_note":"CombatantInfo from FILL_ME_2 populates gear_sets; for the SR sanity-check expectation, ensure Kessa's mapped player is wearing Kingsfall, or edit fixtures/softres.json."
},open("fixtures/wcl-reports.json","w"),indent=1)

# ---------- 6b. attunements (Module A W6) ----------
# Step labels are illustrative placeholders for the Classic Era test. FOREVER's steps are entered by officers as data (patch forever-1.0).
att_steps = {
 "Alliance":[
  {"key":"start","label":"Questline started","group_step":False,"location":None,"final":False},
  {"key":"brd","label":"Blackrock Depths step","group_step":True,"location":"Blackrock Depths","final":False},
  {"key":"drakkisath","label":"General Drakkisath","group_step":True,"location":"Upper Blackrock Spire","final":False},
  {"key":"amulet","label":"Drakefire Amulet in bags","group_step":False,"location":None,"final":True}],
 "Horde":[
  {"key":"start","label":"Questline started","group_step":False,"location":None,"final":False},
  {"key":"skulls","label":"Test of Skulls step","group_step":True,"location":"open world","final":False},
  {"key":"drakkisath","label":"General Drakkisath","group_step":True,"location":"Upper Blackrock Spire","final":False},
  {"key":"amulet","label":"Drakefire Amulet in bags","group_step":False,"location":None,"final":True}]}
att_stuck, att_fresh, att_brd = order[40][0], order[41][0], order[42][0]   # the three Vanguard bench characters
att_progress=[]
for r in order:
    n=r[0]
    if n==att_stuck: att_progress.append({"character":n,"step":"drakkisath","status":"in_progress","source":"self"})
    elif n==att_fresh: att_progress.append({"character":n,"step":"start","status":"in_progress","source":"self"})
    elif n==att_brd: att_progress.append({"character":n,"step":"brd","status":"in_progress","source":"self"})
    else: att_progress.append({"character":n,"step":"amulet","status":"attuned","source":"officer" if n in ("Dunmar","Maelis") else "self"})
json.dump({
 "_readme":"Module A W6 fixture. Load after the roster import. Characters without a progress row (every non-Vanguard character, including Orlette, Orla's alt) have not started. Step labels are illustrative placeholders for the Classic Era test; FOREVER's Onyxia row is seeded from Blizzard's 20 Oct 2026 raid overview and officers fill in the live quest steps.",
 "attunements":[{"patch":"classic_era","zone":"Onyxia's Lair","name":"Drakefire Amulet","faction":f,"scope":"character","requirement":"Drakefire Amulet in bags (need not be equipped)","steps":st} for f,st in att_steps.items()],
 "progress":[dict(attunement="Drakefire Amulet",**p) for p in att_progress]
},open("fixtures/attunements.json","w"),indent=1)

# ---------- 7. applications.json ----------
json.dump({"applications":[
 {"team":"hearth","discord":"pip_frost","character":"Pip","class":"Mage","spec":"Frost","availability":{"Sat":"14:00-23:00","Sun":"14:00-22:00"},"log_profile_url":"https://vanilla.warcraftlogs.com/character/us/whitemane/FILL_ME","answers":{"why":"Thorvik's brother-in-law; wants to raid with him on weekends.","experience":"Levelled a mage in Era; a few UBRS pugs."},"expected_screen":{"spec":"Frost","median_percentile":41,"kills_logged":12,"avoidable_deaths_per_10_pulls":2}},
 {"team":"vanguard","discord":"sylvaric_wow","character":"Sylvaric","class":"Priest","spec":"Holy","availability":{"Tue":"19:00-23:00","Thu":"19:00-23:00"},"log_profile_url":"","answers":{"why":"Vanguard needs a healer per the team page."},"expected_screen":None}
]},open("applications.json","w"),indent=1)

# ---------- 8. expectations ----------
json.dump({
 "roster_import":{"creates":len(rows),"errors":0,"reimport_creates":0,"duplicates":0},
 "onboarding":{"thorvik_fury":{"auto_claimed":"Thorvik","review_opt_in":True},"pip_frost":{"routed_to":"application"}},
 "placement":{"pip_and_thorvik_same_team_saturday":True,"brann_off_high_criticality_seat":True,"hearth_margin_pct_range":[0,4]},
 "raid_create":{"steps_recorded":5,"softres_step":"skipped (softres_mode=fixture)","needs_attention":["sr_link"] ,"resolved_by_fixture":"SR_TEST_NAXX_1"},
 "signups":{"accepted":38,"tentative":2,"bench":3},
 "attunement":{"vanguard_onyxia_readiness":{"attuned":len(order)-3,"of":len(order)},
   "stuck_list":{"Upper Blackrock Spire":[att_stuck],"Blackrock Depths":[att_brd]},
   "seat_blocked":{"character":att_fresh,"template":"Ony 40","reason_contains":["Drakefire Amulet","Questline started"]},
   "per_character":{"Orla":"attuned","Orlette":"not_started"},
   "after_officer_verify":{"character":att_stuck,"seat_allowed":True,"readiness":{"attuned":len(order)-2,"of":len(order)}}},
 "walls":{"other_faction_blocked":True,"other_ruleset_blocked":True,"note":"the test inserts one Horde character and one character on another ruleset (set teams.ruleset for the test); neither can be seated on a Vanguard event, and each refusal shows a reason"},
 "lockout_guard":{"flagged":True,"note":"the test inserts a lockouts row for one seated character, same zone and week; the roster builder flags it"},
 "loot_sheet":{"Deathbringer":{"first":"Thorvik","reason_contains":["SR","attendance","no loot"]},"flags":[{"name":"Kessa","item":"Kingsfall","reason":"already worn (gear from log)"}]},
 "close_out":{"late":["thorvik_fury"],"awards":4,"thorvik_wishlist_received":"Deathbringer"},
 "review_thorvik_onyxia":{"percentile":68,"band":"50-74","next_band":"75-94","gap_points":11,"swings":{"actual":118,"expected":137,"efficiency":0.86,"lost_unexplained":19,"parries":4},"focus_items_max":3,"plain_paragraph":{"sentences":[3,5],"numbers_max":1},
   "note":"Numbers come from the sample review; with a real Era report they will differ — assert shapes and rules, and assert the specific numbers only against the recorded fixture used in poc/tests."},
 "lethality":{"cascade_detected_from_wipe":True},
 "digest":{"vanguard_open_roles_contains":"healer"}
},open("expected/walkthrough-expectations.json","w"),indent=1)
print("roster rows", len(rows), "| wishlist rows", len(wl), "| availability rows", len(av))
