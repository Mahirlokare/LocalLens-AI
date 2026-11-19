-- LocalLens AI initial Supabase schema.
-- Apply with: supabase db push (after linking your own Supabase project).
create extension if not exists pgcrypto;

create table if not exists public.neighbourhoods (
  id uuid primary key default gen_random_uuid(),
  slug text not null unique,
  name text not null,
  city text not null,
  latitude double precision not null check (latitude between -90 and 90),
  longitude double precision not null check (longitude between -180 and 180),
  description text,
  data_status text not null default 'verified_pending',
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists public.indicators (
  id uuid primary key default gen_random_uuid(),
  neighbourhood_id uuid not null references public.neighbourhoods(id) on delete cascade,
  indicator_key text not null,
  value numeric(5,2) check (value between 0 and 100),
  source_name text not null,
  source_url text,
  observed_at date,
  is_illustrative boolean not null default false,
  created_at timestamptz not null default now(),
  unique (neighbourhood_id, indicator_key, source_name, observed_at)
);

create table if not exists public.saved_comparisons (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  title text not null default 'My comparison',
  neighbourhood_slugs text[] not null default '{}',
  weights jsonb not null default '{"healthcare":25,"transit":25,"education":25,"environment":25}'::jsonb,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create index if not exists indicators_neighbourhood_idx on public.indicators(neighbourhood_id);
create index if not exists saved_comparisons_user_idx on public.saved_comparisons(user_id);

alter table public.neighbourhoods enable row level security;
alter table public.indicators enable row level security;
alter table public.saved_comparisons enable row level security;

-- Neighbourhoods and source-labelled indicators are public read-only data.
create policy "Public can read neighbourhoods" on public.neighbourhoods
  for select to anon, authenticated using (true);
create policy "Public can read indicators" on public.indicators
  for select to anon, authenticated using (true);

-- Users can only manage their own saved comparisons.
create policy "Users read own comparisons" on public.saved_comparisons
  for select to authenticated using ((select auth.uid()) = user_id);
create policy "Users create own comparisons" on public.saved_comparisons
  for insert to authenticated with check ((select auth.uid()) = user_id);
create policy "Users update own comparisons" on public.saved_comparisons
  for update to authenticated using ((select auth.uid()) = user_id) with check ((select auth.uid()) = user_id);
create policy "Users delete own comparisons" on public.saved_comparisons
  for delete to authenticated using ((select auth.uid()) = user_id);

comment on table public.indicators is 'Every production indicator must cite a source and observation date. Illustrative values must be marked is_illustrative=true.';
