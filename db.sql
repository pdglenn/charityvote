#create Database charityvote;
use charityvote;
drop table if exists comp_option;
drop table if exists competitions;

create table competitions
(
   id int Primary key,
   title varchar(20),
   description varchar(200),
   amount numeric(20,0),
   date date,
   image_url varchar(200),
   user_id varchar(30)

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

create table orders
(
   id int primary key,
   name varchar(200),
   address varchar(200),
   city varchar(200),
   state varchar(200),
   zip_code varchar(200),
   billing_name varchar(200),
   credit_card_number varchar(200),
   competition_id varchar(200),
   option_id varchar(200)
);
