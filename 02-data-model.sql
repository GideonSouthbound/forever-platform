-- 02 · Reference data model. Translate to Drizzle; keep names. All timestamps UTC.
-- Every table with org-scoped data carries org_id. Every derived table carries patch.
-- External combat-log ids use neutral log_* names and are text (opaque). The `logs` adapter fills them from Forever Logs in FOREVER
-- (encounters.log_encounter_id = boss_id, raids.log_report_id = report id) and from Warcraft Logs only for the optional poc.

-- ===== Identity & tenancy =====
create table orgs (id serial primary key, name text not null, discord_guild_id text unique not null, created_at timestamptz default now());
create table users (id serial primary key, org_id int references orgs(id), discord_id text unique not null, display_name text, log_user_id text, timezone text, review_opt_in boolean default false, created_at timestamptz default now());
create table teams (id serial primary key, org_id int references orgs(id), slug text not null, name text not null, realm text, ruleset text, region text, faction text, /* Forever: ruleset (normal|pvp|rp|rp_pvp|hardcore; rp_pvp added for launch per Blizzard, 22 Oct 2026) + region replace realm; faction and ruleset are hard grouping walls */ timezone text, raid_days jsonb, recruitment_status text default 'closed', discord_role_id text, signup_channel_id text, officer_channel_id text, sr_token_thread_id text, ui_updates_channel_id text, log_guild_id text, loot_config_id int, unique (org_id, slug));
create table characters (id serial primary key, org_id int, user_id int references users(id), team_id int references teams(id), name text not null, first_name text, surname text, realm text, ruleset text, region text, faction text, class text not null, /* Forever names are two-part and unique per region; `name` stores the full display name, `realm` stays for Classic Era test data */ spec text, role text, is_main boolean default false, status text not null default 'active', claimed_at timestamptz, import_id int, log_character_id text, created_at timestamptz default now(), unique nulls not distinct (org_id, name, realm, region)); -- status: pending | active | retired; NULLS NOT DISTINCT (Postgres 15+) so a realmless Forever name cannot be duplicated
create table team_memberships (id serial primary key, user_id int references users(id), character_id int references characters(id), team_id int references teams(id), role text not null, status text not null default 'active', import_id int, joined_at timestamptz default now(), left_at timestamptz, unique (user_id, team_id)); -- status: pending | active | inactive; user_id null while pending and unclaimed
create table social_edges (id serial primary key, org_id int, user_a int references users(id), user_b int references users(id), kind text not null, note text, unique (user_a, user_b, kind)); -- kind: must_with | prefer_with | keep_apart

-- ===== Game data (versioned) =====
create table patches (id serial primary key, label text unique not null, game text not null, released_at date);
create table zones (id serial primary key, patch text not null, name text not null, size int, lockout_days int, log_zone_id text, softres_instance_id int, credit_weight numeric default 1, unique (patch, name));
create table encounters (id serial primary key, zone_id int references zones(id), name text not null, log_encounter_id text, order_index int, unique (zone_id, name));
create table items (id int primary key, patch text not null, name text not null, slot text, armor_class text, quality text, ilvl int, stats jsonb, class_mask jsonb, set_name text, source_type text, source_name text, encounter_id int references encounters(id), icon text, sources_meta jsonb);
create table attunements (id serial primary key, patch text not null, zone_id int references zones(id), name text not null, faction text, scope text not null default 'character', requirement text, steps jsonb not null, source_url text, unique (patch, zone_id, name, faction)); -- faction null = both factions; steps: ordered [{key, label, group_step, location, final}], the final step means attuned; Module A W6
create table source_snapshots (id serial primary key, source text not null, version_label text, etag text, checksum text not null, fetched_at timestamptz default now(), payload_ref text, payload jsonb, unique (source, checksum));

-- ===== Raid ops =====
create table raid_templates (id serial primary key, team_id int references teams(id), zone_id int references zones(id), name text, seats jsonb not null); -- seats: [{role, class_allow, criticality, label}]
create table raid_events (id serial primary key, org_id int, team_id int references teams(id), zone_id int references zones(id), template_id int references raid_templates(id), starts_at timestamptz not null, status text not null default 'planned', raid_helper_event_id text, softres_raid_id text, softres_admin_token_enc text, needs_attention jsonb, created_by int references users(id), created_at timestamptz default now());
create table signups (id serial primary key, raid_event_id int references raid_events(id), character_id int references characters(id), raw_name text, class_as_signed text, spec_as_signed text, status text not null, signed_at timestamptz, unique (raid_event_id, raw_name));
create table signup_snapshots (id serial primary key, raid_event_id int references raid_events(id), taken_at timestamptz default now(), payload jsonb not null);
create table availability (id serial primary key, user_id int references users(id), weekday int, start_min int, end_min int, raid_event_id int references raid_events(id), note text);
create table raids (id serial primary key, raid_event_id int references raid_events(id) unique, log_report_id text, started_at timestamptz, ended_at timestamptz, bosses_killed int, attendees jsonb, bench jsonb, late jsonb, closed_by int references users(id));
create table attendance_credits (id serial primary key, user_id int references users(id), team_id int references teams(id), lockout_week date not null, zone_id int references zones(id), credit numeric not null, source_raid_id int references raids(id), excused boolean default false, created_at timestamptz default now());
create table absences (id serial primary key, user_id int references users(id), raid_event_id int references raid_events(id), reason text, excused boolean default true, created_at timestamptz default now());
create table character_attunements (id serial primary key, character_id int references characters(id), attunement_id int references attunements(id), step_key text, status text not null default 'in_progress', source text not null, verified_by int references users(id), verified_at timestamptz, updated_at timestamptz default now(), unique (character_id, attunement_id)); -- status: in_progress | attuned (no row = not started); source: self | officer | log; every change also writes audit_log
create table lockouts (id serial primary key, character_id int references characters(id), zone_id int references zones(id), lockout_week date not null, source_raid_id int references raids(id), unique (character_id, zone_id, lockout_week));

-- ===== Spreadsheet imports (Module J) =====
create table roster_imports (id serial primary key, org_id int, team_id int references teams(id), kind text not null, filename text, mapping jsonb not null, status text not null default 'previewed', summary jsonb, uploaded_by int references users(id), applied_at timestamptz, rolled_back_at timestamptz, created_at timestamptz default now()); -- kind: roster | raid_roster | wishlists | availability
create table roster_import_rows (id serial primary key, import_id int references roster_imports(id), row_no int, raw jsonb not null, parsed jsonb, action text, entity text, entity_id int, error text); -- action: create | update | skip | error
create table seat_assignments (id serial primary key, raid_event_id int references raid_events(id), seat_index int, character_id int references characters(id), raw_name text, source text not null, status text not null default 'pending', import_id int, decided_by int references users(id), created_at timestamptz default now(), unique (raid_event_id, seat_index)); -- source: import | solver | manual; status: pending | confirmed | declined

-- ===== Loot =====
create table loot_configs (id serial primary key, team_id int references teams(id), method text not null default 'sr_roll', attendance_window_weeks int default 6, weights jsonb, recency_penalty jsonb, restricted_rules jsonb, patch text);
create table wishlists (id serial primary key, character_id int references characters(id), item_id int references items(id), rank int, note text, received_at timestamptz, updated_at timestamptz default now(), unique (character_id, item_id));
create table soft_reserves (id serial primary key, raid_event_id int references raid_events(id), character_id int references characters(id), raw_name text, item_id int references items(id), imported_at timestamptz default now());
create table loot_awards (id serial primary key, raid_id int references raids(id), item_id int references items(id), character_id int references characters(id), method text, note text, source text, awarded_at timestamptz default now(), superseded_by int); -- append-only; corrections add a row and set superseded_by
create table loot_sheets (id serial primary key, raid_event_id int references raid_events(id), generated_at timestamptz default now(), rows jsonb not null, xlsx_ref text);
create table loot_forecasts (id serial primary key, team_id int references teams(id), item_id int references items(id), expected_drops_per_week numeric, contenders int, weeks_to_satisfy numeric, computed_at timestamptz default now());

-- ===== Performance (combat logs; Forever Logs primary, see 13-forever-logs-api.md) =====
-- Mapping for Forever Logs: reports.code = report id; fight_id = encounter id; master_data = actors; fights = encounters;
-- raw_events.data_type = event group (damage, avoidance, casts, buffs, deaths, ...); cursor/next_cursor = keyset paging.
-- Report, encounter and actor ids are opaque, so they are stored as text.
create table reports (code text primary key, source text not null default 'forever_logs', org_id int, team_id int references teams(id), title text, start_time bigint, end_time bigint, game_version text, patch text, zone_name text, master_data jsonb not null, fights jsonb not null, rankings jsonb, live boolean default false, fetched_at timestamptz default now());
create table raw_events (id serial primary key, report_code text not null, fight_id text not null, data_type text not null, source_id text, target_id text, cursor text, next_cursor text, data jsonb, data_ref text, fetched_at timestamptz default now());
create index on raw_events (report_code, fight_id, data_type, source_id);
create table ranked_parses (id serial primary key, encounter_id int references encounters(id), class text, spec text, band text, percentile_est numeric, player_name text, report_code text, fight_id text, source_id text, amount numeric, duration_ms int, kill_bucket text, patch text, context_score jsonb, generalizable boolean, raw jsonb, unique (report_code, fight_id, player_name));
create table parse_metrics (id serial primary key, report_code text not null, fight_id text not null, player_name text not null, character_id int references characters(id), source_id text, encounter_id int references encounters(id), class text, spec text, assignment text, is_reference boolean default false, band text, rank_percent numeric, kill_bucket text, duration_ms int, patch text, vector jsonb not null, details jsonb, computed_at timestamptz default now(), unique (report_code, fight_id, player_name));
create table reference_bands (id serial primary key, encounter_id int references encounters(id), class text, spec text, kill_bucket text, band text, patch text, n int, stats jsonb not null, built_at timestamptz default now(), unique (encounter_id, class, spec, kill_bucket, band, patch, built_at));
create table rotation_standards (id serial primary key, encounter_id int references encounters(id), class text, spec text, kill_bucket text, patch text, priority_list jsonb, cooldown_template jsonb, uptime_targets jsonb, n int, built_at timestamptz default now());
create table outlier_annotations (id serial primary key, ranked_parse_id int references ranked_parses(id), enabling_conditions jsonb not null, summary text, created_at timestamptz default now());
create table reviews (id serial primary key, user_id int references users(id), character_id int references characters(id), report_code text, fight_id text, encounter_id int references encounters(id), facts jsonb not null, technical_text text not null, plain_text text not null, attribution jsonb not null, focus_items jsonb not null, coach_note text, delivered_at timestamptz, created_at timestamptz default now(), unique (report_code, fight_id, character_id));
create table review_focus_history (id serial primary key, user_id int references users(id), metric text, set_at timestamptz, before_value numeric, after_value numeric, resolved boolean default false);
create table coaching_queue (id serial primary key, team_id int references teams(id), user_id int references users(id), reason text, weeks_stalled int, mentor_user_id int references users(id), status text default 'open', created_at timestamptz default now());
create table boss_abilities (id serial primary key, encounter_id int references encounters(id), patch text, name text, casts_per_pull numeric, avg_damage numeric, deaths_attributed int, tank_deaths int, raid_deaths int, lethality_rank int, officer_note text, unique (encounter_id, patch, name));
create table boss_deaths (id serial primary key, encounter_id int references encounters(id), report_code text, fight_id text, kill boolean, player_name text, is_tank boolean, death_time_ms int, killing_blow_ability text, healer_gap_ms int, avoidable boolean, cascade_id int);
create table cascades (id serial primary key, encounter_id int references encounters(id), report_code text, fight_id text, first_death_ms int, deaths int, attributed_ability text, boss_pct numeric);

-- ===== Placement =====
create table player_profiles (id serial primary key, user_id int references users(id), character_id int references characters(id), patch text, ceiling numeric, execution_ratio numeric, reliability numeric, attendance_pct numeric, carry_load numeric, computed_at timestamptz default now()); -- officer-only
create table team_capacity (id serial primary key, team_id int references teams(id), zone_id int references zones(id), patch text, expected_output numeric, requirement numeric, margin numeric, carry_capacity numeric, computed_at timestamptz default now());
create table placement_runs (id serial primary key, org_id int, created_by int references users(id), inputs jsonb not null, assignments jsonb not null, objective numeric, notes text, applied boolean default false, created_at timestamptz default now());

-- ===== Boss guide =====
create table boss_guides (id serial primary key, encounter_id int references encounters(id), patch text, summary text, special_seats jsonb, officer_notes jsonb, updated_by int references users(id), updated_at timestamptz default now());
create table strats (id serial primary key, encounter_id int references encounters(id), team_id int references teams(id), patch text, version int, layout jsonb not null, phases jsonb not null, published boolean default false, created_by int references users(id), created_at timestamptz default now()); -- see 07-strat-format.json
create table reminder_exports (id serial primary key, encounter_id int references encounters(id), strat_id int references strats(id), kind text not null, export_string text, external_url text, version int, created_at timestamptz default now()); -- kind: dbm_note | bigwigs_note | raid_note | macro | weakaura (conditional; WA does not run on Forever's API as of Sep 2026)

-- ===== Characters: talents, gear, sim =====
create table talent_builds (id serial primary key, character_id int references characters(id), snapshot_id int references source_snapshots(id), label text, points jsonb not null, share_code text, is_main boolean default false, created_at timestamptz default now());
create table gear_sets (id serial primary key, character_id int references characters(id), patch text, label text, source text, items jsonb not null, enchants jsonb, stats jsonb, from_report_code text, created_at timestamptz default now()); -- source: log | manual
create table sim_results (id serial primary key, character_id int references characters(id), gear_set_id int references gear_sets(id), talent_build_id int references talent_builds(id), engine text, encounter_id int references encounters(id), settings jsonb, dps numeric, created_at timestamptz default now());

-- ===== Recruitment & retention =====
create table applications (id serial primary key, team_id int references teams(id), discord_id text, character_name text, class text, spec text, availability jsonb, log_profile_url text, screen jsonb, answers jsonb, status text default 'new', officer_notes jsonb, discord_thread_id text, created_at timestamptz default now());
create table trial_scorecards (id serial primary key, user_id int references users(id), team_id int references teams(id), started_at date, week int, attendance_pct numeric, band_relative jsonb, reliability numeric, mechanic_deaths int, recommendation text, votes jsonb, created_at timestamptz default now());
create table retention_flags (id serial primary key, user_id int references users(id), team_id int references teams(id), kind text, weeks int, actioned boolean default false, created_at timestamptz default now());

-- ===== UI & onboarding =====
create table ui_resources (id serial primary key, org_id int, class text, kind text, name text, url text, required boolean default false, note text, order_index int);
create table wago_watch (id serial primary key, org_id int, label text, url text, kind text, last_version text, last_updated_at timestamptz, last_checked_at timestamptz, notify_channel_id text);
create table onboarding_progress (id serial primary key, user_id int references users(id), step text, done_at timestamptz, unique (user_id, step));

-- ===== Platform =====
create table jobs (id serial primary key, org_id int, name text not null, status text not null, progress jsonb, resume_at timestamptz, error text, created_at timestamptz default now(), updated_at timestamptz default now());
create table api_calls (id serial primary key, source text not null, query_name text not null, cache_hit boolean not null, points_cost numeric, duration_ms int, created_at timestamptz default now());
create table integration_status (id serial primary key, name text unique not null, healthy boolean, last_ok_at timestamptz, last_error text, checked_at timestamptz);
create table audit_log (id serial primary key, org_id int, user_id int references users(id), action text not null, entity text, entity_id text, before jsonb, after jsonb, created_at timestamptz default now());
create table settings (org_id int, key text, value jsonb not null, primary key (org_id, key));
create table exports (id serial primary key, org_id int, user_id int references users(id), scope text, ref text, created_at timestamptz default now());
