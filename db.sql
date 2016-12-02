#create Database charityvote;
use charityvote;
drop table if exists comp_option;
drop table if exists user_comp;
drop table if exists competitions;
drop table if exists connection;
drop table if exists roles_users;
drop table if exists role;
drop table if exists user;

create table user
  (
    id int Primary Key,
    email varchar(255),
    password varchar(255),
    active tinyint(1),
    confirmed_at DateTime
  );

create table competitions
(
   id int Primary key,
   title varchar(20),
   description varchar(200),
   amount numeric(20,0),
   date date,
   image_url varchar(200),
   user_id int,
   foreign key (user_id) references user(id)
);
create table comp_option
(
   id int Primary Key,
   description varchar(200),
   image_url varchar(200),
   comp_id int,
   votes int,
   foreign key (comp_id)  references competitions (id)
);

create table role
  (
    id int Primary Key,
    name varchar(80),
    description varchar(255)
  );

create table roles_users
(
  user_id int,
  role_id int,
  foreign key(user_id) references user(id),
  foreign key(role_id) references role(id)
);

create table user_comp (
  id integer primary key,
  user_id integer not null,
  comp_id integer not null,
  foreign key(user_id) references user(id),
  foreign key(comp_id) references competitions(id)
);

insert into user (id, username, password) values ("1", "fred", "fred");
