drop table if exists fssounds;
create table fssounds (
    id integer primary key autoincrement,
    fsid integer not null,
    search_text text not null
);
