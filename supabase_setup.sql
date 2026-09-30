-- À exécuter une seule fois dans Supabase > SQL Editor
create table if not exists likes (
  visitor text primary key,
  ts timestamptz default now()
);
create table if not exists docs (
  id bigserial primary key,
  owner text not null,
  kind text, poste text, tpl text, date text,
  data text not null,
  created timestamptz default now()
);
create index if not exists idx_docs_owner on docs(owner);
-- Sécurité : RLS activé sans aucune policy = accès public impossible.
-- Seule la clé secrète (service_role) stockée dans Streamlit Secrets peut lire/écrire.
alter table likes enable row level security;
alter table docs enable row level security;

-- Avis et étoiles (à exécuter aussi si vous aviez déjà créé les tables ci-dessus)
create table if not exists reviews (
  id bigserial primary key,
  name text,
  stars int not null check (stars between 1 and 5),
  comment text,
  created timestamptz default now()
);
alter table reviews enable row level security;
-- Pour supprimer un commentaire abusif : delete from reviews where id = 123;
