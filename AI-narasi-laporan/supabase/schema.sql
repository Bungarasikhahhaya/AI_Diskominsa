create table if not exists public.dataset_katalog (
  uuid text primary key,
  judul text not null,
  diperbarui_pada timestamptz not null default now()
);

alter table public.dataset_katalog enable row level security;

-- Backend memakai SUPABASE_SECRET_KEY dan dapat melewati RLS.
-- Tidak ada kebijakan anon karena browser selalu mengakses backend, bukan tabel Supabase secara langsung.
