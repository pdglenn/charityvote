#create Database charityvote;
use charityvote;
drop table if exists comp_option;
drop table if exists user_comp;
drop table if exists competitions;
drop table if exists connection;
drop table if exists roles_users;
drop table if exists role;
drop table if exists user;



create table competitions
(
   id int Primary key,
   title varchar(20),
   description varchar(200),
   amount numeric(20,0),
   date date,
   image_url varchar(200),
   user_id int
   
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



insert into user (id, username, password) values ("1", "fred", "fred");
