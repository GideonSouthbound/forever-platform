-- Reference DDL. Translate to Drizzle; keep names. All timestamps UTC.

create table sources (
  id serial primary key,
  name text unique not null,                -- 'wcl', 'talentsforever'
  base_url text not null
);

create table source_snapshots (             -- versioned copies of external data files
  id serial primary key,
  source_id int references sources(id),
  version_label text,                       -- e.g. talentsforever "generated" date
  etag text,
  checksum text not null,
  fetched_at timestamptz default now(),
  payload jsonb not null,
  unique (source_id, checksum)
);

create table encounters (                   -- discovered, never hardcoded
  id int primary key,                       -- WCL encounter id
  zone_id int not null,
  zone_name text not null,
  name text not null,
  patch text                                -- game version label when discovered
);

create table reports (
  code text primary key,
  title text,
  start_time bigint,
  end_time bigint,
  game_version text,
  zone_name text,
  master_data jsonb not null,               -- actors + abilities
  fights jsonb not null,
  rankings jsonb,                           -- report.rankings payload (guild players' rankPercent)
  fetched_at timestamptz default now()
);

create table ranked_parses (                -- reference sample from characterRankings
  id serial primary key,
  encounter_id int references encounters(id),
  class text not null, spec text not null,
  band text not null,                       -- '75-94' | '95-98' | '99+'
  percentile_est numeric,                   -- estimated from page position / count
  player_name text, report_code text, fight_id int, source_id int,
  amount numeric, duration_ms int,
  kill_bucket text,                         -- '<2:00' | '2:00-3:30' | '3:30-5:30' | '>5:30'
  patch text,
  raw jsonb not null,
  unique (report_code, fight_id, player_name)
);

create table raw_events (                   -- cached event pages
  id serial primary key,
  report_code text not null,
  fight_id int not null,
  data_type text not null,                  -- Casts | Buffs | Debuffs | DamageDone | Deaths | CombatantInfo | Healing
  source_id int, target_id int,
  page_start bigint, next_page bigint,
  data jsonb not null,
  fetched_at timestamptz default now()
);
create index on raw_events (report_code, fight_id, data_type, source_id);

create table parse_metrics (                -- one vector per (report, fight, player)
  id serial primary key,
  report_code text not null, fight_id int not null,
  player_name text not null, source_id int,
  encounter_id int references encounters(id),
  class text, spec text,
  is_reference boolean default false,       -- true for ranked_parses, false for guild ingests
  band text, rank_percent numeric,
  kill_bucket text, duration_ms int, patch text,
  vector jsonb not null,                    -- { metric_name: number, ... }
  details jsonb,                            -- gaps list, consumes lists, etc.
  computed_at timestamptz default now(),
  unique (report_code, fight_id, player_name)
);

create table reference_bands (
  id serial primary key,
  encounter_id int references encounters(id),
  class text, spec text,
  kill_bucket text, band text, patch text,
  n int not null,
  stats jsonb not null,                     -- { metric_name: { median, mad } }
  built_at timestamptz default now(),
  unique (encounter_id, class, spec, kill_bucket, band, patch)
);

create table reviews (
  id serial primary key,
  report_code text not null, fight_id int not null, player_name text not null,
  facts jsonb not null,                     -- the fact table used to render
  technical_text text not null,
  plain_text text not null,
  attribution jsonb not null,               -- ranked items with expected gain
  created_at timestamptz default now(),
  unique (report_code, fight_id, player_name)
);

create table boss_deaths (                  -- for lethality
  id serial primary key,
  encounter_id int references encounters(id),
  report_code text, fight_id int, kill boolean,
  player_name text, is_tank boolean,
  death_time_ms int,
  killing_blow_ability text,
  healer_gap_ms int,
  cascade_id int                            -- null if not part of a cascade
);

create table cascades (
  id serial primary key,
  encounter_id int references encounters(id),
  report_code text, fight_id int,
  first_death_ms int, deaths int,
  attributed_ability text
);

create table jobs (
  id serial primary key,
  name text not null,
  status text not null,                     -- queued | running | paused | done | failed
  progress jsonb,                           -- { done, total, cursor }
  resume_at timestamptz,
  error text,
  created_at timestamptz default now(),
  updated_at timestamptz default now()
);

create table api_calls (
  id serial primary key,
  source text not null, query_name text not null,
  cache_hit boolean not null,
  points_cost numeric,
  duration_ms int,
  created_at timestamptz default now()
);

create table settings (
  key text primary key,
  value jsonb not null                      -- e.g. {"sample_per_band": 20}
);
