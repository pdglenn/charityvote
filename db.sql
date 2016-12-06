#create Database charityvote;
use charityvote;
drop table if exists comp_option;
drop table if exists competitions;
drop table if exists orders;

-- stores each campaign
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

-- stores the options for each campaign and references the campaign id
create table comp_option
(
   id int Primary Key,
   description varchar(200),
   image_url varchar(200),
   comp_id int,
   votes int,
   foreign key (comp_id)  references competitions (id)
);

-- initial dummy value
insert into competitions VALUES (1, 'Initial Competition', 'Initial Competition', 200, '2015-01-01', 'static/test.jpg', '1');

-- stores orders for options as voted by users
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
