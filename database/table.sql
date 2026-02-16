CREATE SCHEMA operation 	AUTHORIZATION postgres;
CREATE SCHEMA log 			AUTHORIZATION postgres;
CREATE SCHEMA audit 		AUTHORIZATION postgres;
CREATE SCHEMA rockworks 	AUTHORIZATION postgres;
CREATE SCHEMA survey		AUTHORIZATION postgres;

--- Table
-- al
CREATE TABLE operation.contacts (
	id 				serial4 	NOT NULL,
	code_contact 	varchar(20) NOT NULL,
	phone 			varchar(18),
	email 			varchar(255) NOT NULL,
	mobile 			varchar(18),
	fax 			varchar(18),
	created_at 		timestamp 	DEFAULT NOW(),
	updated_at 		timestamp,
	deleted_at 		timestamp,
	CONSTRAINT contacts_pkey 			PRIMARY KEY (id),
	CONSTRAINT contacts_id_contact_key 	UNIQUE (code_contact)
);

CREATE TABLE operation.method_payments (
	id 					serial4 	NOT NULL,
	code_methodpay 		varchar(20) NOT NULL,
	transaction_name 	varchar(100) NOT NULL,
	bank_name 			varchar(100) NOT NULL,
	created_at 			timestamp 	DEFAULT NOW(),
	CONSTRAINT method_payments_pkey PRIMARY KEY (id),
	CONSTRAINT site_id_payments_key UNIQUE (code_methodpay)
);

CREATE TABLE operation.parameters (
	id 				serial4 	NOT NULL,
	parent_desc 	varchar(20),
	kode_desc 		varchar(20),
	description 	text,
	created_at 		timestamp 	DEFAULT NOW(),
	updated_at 		timestamp,
	CONSTRAINT parameter_pkey PRIMARY KEY (id)
);

CREATE TABLE operation.sites (
	id 				serial4 				NOT NULL,
	code_site 		varchar(20) 			NOT NULL,
	type	 		varchar(20) 			NOT NULL,
	location	 	text 					NOT NULL,
	city 			varchar(20) 			NOT NULL,
	state			varchar(20) 			NOT NULL,
	zip 			varchar(10),
	country 		varchar(20) 			NOT NULL,
	port 			varchar(20) 			NOT NULL,
	latitude 		double precision 		NOT NULL,
	longitude 		double precision 		NOT NULL,
	status	 		varchar(20) 			NOT NULL, -- Active, Inactive
	created_at 		timestamp 				DEFAULT NOW(),
	updated_at 		timestamp,
	deleted_at 		timestamp,
	CONSTRAINT sites_pkey 			PRIMARY KEY (id),
	CONSTRAINT sites_id_site_key 	UNIQUE (code_site)
);

CREATE TABLE operation.buoys (
	id 			serial4				NOT NULL,
	id_site 	varchar(20) 		NOT NULL,
	code_buoy 	varchar(20) 		NOT NULL,
	longitude 	double precision 	NOT NULL,
	latitude 	double precision 	NOT NULL,
	status 		varchar(20),  -- Active, Inactinve, MTC
	last_mtc 	timestamp,
	created_at 	timestamp 			DEFAULT NOW(),
	updated_at 	timestamp,
	deleted_at 	timestamp,
	CONSTRAINT buoys_pkey 			PRIMARY KEY (id),
	CONSTRAINT buoys_id_buoy_key 	UNIQUE (code_buoy),
	CONSTRAINT buoys_id_site_fkey 	FOREIGN KEY (id_site) REFERENCES operation.sites(code_site) ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE TABLE operation.buoy_sensor_histories (
	id 			serial4		NOT NULL,
	id_buoy 	varchar(20) NOT NULL,
	salinitas 	int4,
	turbidity 	int4,
	current 	int4,
	oxygen 		int4,
	tide 		int4,
	density 	int4,
	created_at 	timestamp 	DEFAULT NOW(),
	CONSTRAINT buoy_sensor_histories_pkey 			PRIMARY KEY (id),
	CONSTRAINT buoy_sensor_histories_id_site_fkey 	FOREIGN KEY (id_buoy) REFERENCES operation.buoys(code_buoy) ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE TABLE operation.buoy_mtc_histories (
	id				serial4		NOT NULL,
	id_buoy			varchar(20)	NOT NULL,
	start_date		timestamp	NOT NULL,
	end_date		timestamp	NOT NULL,
	note			text,
	created_at		timestamp	NOT NULL,
	updated_at		timestamp,
	deleted_at		timestamp,
	CONSTRAINT buoy_mtc_histories_pkey			PRIMARY KEY (id),
	CONSTRAINT buoy_mtc_histories_id_buoy_fkey	FOREIGN KEY (id_buoy) REFERENCES operation.buoys(code_buoy) ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE TABLE operation.users (
	id 			serial4 	NOT NULL,
	id_contact 	varchar(20) NOT NULL,
	code_user 	varchar(20) NOT NULL,
	name		varchar(100)	NOT NULL,
	citizen 	varchar(20) NOT NULL,
	role 		varchar(20) NOT NULL,
	status		varchar(20)	NOT NULL, -- Active, Inactive
	organs		varchar(20)	NOT NULL,
	created_at 	timestamp 	DEFAULT NOW(),
	updated_at 	timestamp,
	deleted_at 	timestamp,
	CONSTRAINT user_pkey 			PRIMARY KEY (id),
	CONSTRAINT user_id_check_key 	UNIQUE (code_user),
	CONSTRAINT user_contact_fkey 	FOREIGN KEY (id_contact) REFERENCES operation.contacts(code_contact) ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE TABLE operation.clients (
	id 			serial4				NOT NULL,
	code_client varchar(20) 		NOT NULL,
	name 		varchar(100) 		NOT NULL,
	industry 	varchar(20) 		NOT NULL,
	region 		varchar(20) 		NOT NULL,
	deposit 	numeric(12,2) 		NOT NULL,
	id_contact 	varchar(20) 		NOT NULL,
	status 		varchar(20) 		NOT NULL, -- Active, Inactive
	created_at 	timestamp 			DEFAULT NOW(),
	updated_at 	timestamp,
	deleted_at 	timestamp,
	CONSTRAINT clients_pkey 			PRIMARY KEY (id),
	CONSTRAINT clients_id_client_key 	UNIQUE (code_client),
	CONSTRAINT clients_id_contact_fkey 	FOREIGN KEY (id_contact) REFERENCES operation.contacts(code_contact) ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE TABLE operation.partners (
	id 				serial4 	NOT NULL,
	id_contact 		varchar(20) NOT NULL,
	code_partner	varchar(20),
	name		 	varchar(100) NOT NULL,
	industry 		varchar(20),
	status			varchar(20) NOT NULL, -- Active, Inactive
	created_at 		timestamp 	DEFAULT NOW(),
	updated_at 		timestamp,
	deleted_at 		timestamp,
	CONSTRAINT partner_pkey 			PRIMARY KEY (id),
	CONSTRAINT partner_id_partner_key 	UNIQUE (code_partner),
	CONSTRAINT partner_id_contact_fkey 	FOREIGN KEY (id_contact) REFERENCES operation.contacts(code_contact) ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE TABLE operation.orders (
	id 						serial4 			NOT NULL,
	id_client 				varchar(20) 		NOT NULL,
	code_order				varchar(20) 		NOT NULL,
	order_date 				timestamp 			NOT NULL,
	required_delivery_date 	timestamp,
	priority				varchar(20),
	quantity 				int4		 		NOT NULL,
	special_requirements 	text,
	scheduled_delivery_date timestamp,
	actual_delivery_date 	timestamp 			NOT NULL,
	destination		 		varchar(20) 		NOT NULL,
	destination_longitude	double precision 	NOT NULL,
	destination_latitude 	double precision 	NOT NULL,
	status 					varchar(20), -- Open, On Progress, On Payment, Complited
	created_at 				timestamp 			DEFAULT NOW(),
	updated_at 				timestamp,
	deleted_at 				timestamp,
	CONSTRAINT order_pkey 				PRIMARY KEY (id),
	CONSTRAINT order_id_order_key 		UNIQUE (code_order),
	CONSTRAINT order_id_client_fkey 	FOREIGN KEY (id_client) 	REFERENCES operation.clients(code_client) ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE TABLE operation.payments (
	id 				serial4 		NOT NULL,
	id_client 		varchar(20) 	NOT NULL,
	id_order		varchar(20)		NOT NULL,
	id_methodpay	varchar(20)		NOT NULL,
	code_payment 	varchar(20) 	NOT NULL,
	total_amount 	numeric(12,2) 	NOT NULL,
	payment_date 	timestamp		NOT NULL,
	payment_number 	varchar(20) 	NOT NULL,
	status 			varchar(20) 	NOT NULL, -- Hold, Complited, Failed
	created_at 		timestamp 		DEFAULT NOW(),
	updated_at 		timestamp,
	CONSTRAINT payment_pkey 				PRIMARY KEY (id),
	CONSTRAINT payment_id_payment_key 		UNIQUE (code_payment),
	CONSTRAINT id_payment_client_fkey 		FOREIGN KEY (id_client) 	REFERENCES operation.clients(code_client) ON UPDATE CASCADE ON DELETE CASCADE,
	CONSTRAINT payment_id_order_fkey 		FOREIGN KEY (id_order) 		REFERENCES operation.orders(code_order) ON UPDATE CASCADE ON DELETE CASCADE,
	CONSTRAINT payment_id_mthod_pay_fkey 	FOREIGN KEY (id_methodpay) 	REFERENCES operation.method_payments(code_methodpay) ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE TABLE operation.payment_details (
	id 				serial4 		NOT NULL,
	id_payment 		varchar(20) 	NOT NULL,
	doc_no			varchar(20)		NOT NULL,
	tax				int4,
	exchange_rate	int4,
	amount 			numeric(12,2)	NOT NULL,
	payment_date 	timestamp 		NOT NULL,
	created_at 		timestamp 		DEFAULT NOW(),
	updated_at 		timestamp,
	CONSTRAINT payment_details_pkey 		PRIMARY KEY (id),
	CONSTRAINT payment_id_method_pay_fkey 	FOREIGN KEY (id_payment) REFERENCES operation.payments(code_payment) ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE TABLE operation.client_deposit_histories (
	id 				serial4 			NOT NULL,
	id_client 		varchar(20) 		NOT NULL,
	id_methodpay	varchar(20)			NOT NULL,
	deposit 		numeric(12,2) 		NULL,
	created_at 		timestamp 			NOT NULL,
	CONSTRAINT client_deposit_histories_pkey 				PRIMARY KEY (id),
	CONSTRAINT client_deposit_histories_id_client_fkey 		FOREIGN KEY (id_client) REFERENCES operation.clients(code_client) ON UPDATE CASCADE ON DELETE CASCADE,
	CONSTRAINT client_deposit_histories_id_methodpay_fkey 	FOREIGN KEY (id_methodpay) REFERENCES operation.method_payments(code_methodpay) ON UPDATE CASCADE ON DELETE CASCADE
);


CREATE TABLE operation.vessels (
	id 					serial4 	NOT NULL,
	id_partner 			varchar(20) NOT NULL,
	code_vessel 		varchar(20) NOT NULL,
	flag				varchar(20) NOT NULL,
	name				varchar(100) NOT NULL,
	status 				varchar(20) NOT NULL, --Active Inactive
	created_at 			timestamp 	DEFAULT NOW(),
	updated_at 			timestamp,
	deleted_at 			timestamp,
	CONSTRAINT vessel_pkey 				PRIMARY KEY (id),
	CONSTRAINT vessel_id_vessel_key 	UNIQUE (code_vessel),
	CONSTRAINT vessel_id_partner_fkey 	FOREIGN KEY (id_partner) 	REFERENCES operation.partners(code_partner) ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE TABLE operation.vessel_details (
	id 					serial4		NOT NULL,
	id_vessel 			varchar(20) NOT NULL,
	picture				varchar(20), -- Link Picture
	gross_tonnage 		int4,
	net_tonnage 		int4,
	deadweight_tonnage 	int4,
	length_overall 		int4,
	beam 				int4,
	draft 				int4,
	depth_details 		int4,
	special_features 	text,
	created_at 			timestamp 	DEFAULT NOW(),
	updated_at 			timestamp,
	deleted_at 			timestamp,
	CONSTRAINT vessel_details_pkey 				PRIMARY KEY (id),
	CONSTRAINT vessel_details_id_vessel_fkey 	FOREIGN KEY (id_vessel) REFERENCES operation.vessels(code_vessel) ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE TABLE operation.order_details (
	id 				serial4 	NOT NULL,
	id_order 		varchar(20) NOT NULL,
	id_vessel		varchar(20) NOT NULL,
	code_task 		varchar(20) NOT NULL,
	sand_quantity 	int4,
	clay_quantity 	int4,
	status			varchar(20),  -- Open, On Progres, Deliver, Complited
	created_at 		timestamp 	DEFAULT NOW(),
	updated_at 		timestamp,
	CONSTRAINT order_details_pkey 			PRIMARY KEY (id),
	CONSTRAINT order_details_id_task_key 	UNIQUE (code_task),
	CONSTRAINT order_details_id_order_fkey 	FOREIGN KEY (id_order) 	REFERENCES operation.orders(code_order) ON UPDATE CASCADE ON DELETE CASCADE,
	CONSTRAINT order_details_id_vessel_fkey FOREIGN KEY (id_vessel) REFERENCES operation.vessels(code_vessel) ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE TABLE operation.vessel_crews (
	id 			serial4 	NOT NULL,
	id_user 	varchar(20),
	id_vessel 	varchar(20) NOT NULL,
	status 		varchar(20), -- Active, Inactive, Leave
	flag		varchar(20),
	created_at 	timestamp 	DEFAULT NOW(),
	updated_at 	timestamp,
	deleted_at 	timestamp,
	CONSTRAINT vessel_crew_pkey 			PRIMARY KEY (id),
	CONSTRAINT vessel_crew_id_vessel_fkey 	FOREIGN KEY (id_vessel) REFERENCES operation.vessels(code_vessel) ON UPDATE CASCADE ON DELETE CASCADE,
	CONSTRAINT vessel_crew_id_user_fkey 	FOREIGN KEY (id_user) 	REFERENCES operation.users(code_user) ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE TABLE operation.vessel_activities (
	id				serial4			NOT NULL,
	id_vessel		varchar(20)		NOT NULL,
	id_order		varchar(20),
	id_task			varchar(20),
	seq_activity	varchar(20) 	NOT NULL,
	start_date		timestamp,
	end_date		timestamp,
	estimate_date	timestamp,
	status			varchar(20), -- Dreging, Docking, Settling, Delivering, Maintenance, Returning, Preparation, Discharge Waste, Preventive Maintenance, Discharge Cargo, Idle
	created_at		timestamp		DEFAULT NOW(),
	updated_at		timestamp,
	deleted_at		timestamp,
	CONSTRAINT vessel_activities_pkey			PRIMARY KEY(id),
	CONSTRAINT vessel_activities_id_vessel_fkey	FOREIGN KEY (id_vessel) REFERENCES operation.vessels(code_vessel) ON UPDATE CASCADE ON DELETE CASCADE,
	CONSTRAINT vessel_activities_id_order_fkey 	FOREIGN KEY (id_order) 	REFERENCES operation.orders(code_order) ON UPDATE CASCADE ON DELETE CASCADE,
	CONSTRAINT vessel_activities_id_task_fkey 	FOREIGN KEY (id_task) 	REFERENCES operation.order_details(code_task) ON UPDATE CASCADE ON DELETE CASCADE

);

CREATE TABLE operation.vessel_positions (
	id 				serial4 			NOT NULL,
	id_vessel		varchar(20)			NOT NULL,
	seq_activity	varchar(20)			NOT NULL,
	longitude 		double precision 	NOT NULL,
	latitude		double precision 	NOT NULL,
	speed 			int4,
	heading			int4, 
	note 			text 				NOT NULL,
	created_at 		timestamp 			DEFAULT NOW(),
	CONSTRAINT vessel_positions_pkey 				PRIMARY KEY (id),
	CONSTRAINT vessel_positions_id_vessel_fkey 		FOREIGN KEY (id_vessel) REFERENCES operation.vessels(code_vessel) ON UPDATE CASCADE ON DELETE CASCADE,
	CONSTRAINT vessel_positions_id_activity_fkey 	FOREIGN KEY (seq_activity) 	REFERENCES operation.vessel_activities(seq_activity) ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE TABLE audit.audit_logs (
  	id 			serial4 		NOT NULL,
  	action 		varchar(20) 	NOT NULL,
  	table_name 	varchar(20) 	NOT NULL,
	field		varchar(20)		NOT NULL,
  	record_id 	varchar(20) 	NOT NULL,
	old_data	varchar(20)		NOT NULL,
	new_data	varchar(20),
  	changed_by 	varchar(20),
  	changed_at 	timestamp 		DEFAULT now(),
	CONSTRAINT audit_logs_pkey PRIMARY KEY (id, changed_at)
) PARTITION BY RANGE (changed_at);

CREATE TABLE audit.audit_logs_default PARTITION OF audit.audit_logs DEFAULT; -- Default partition for unmatched dates

CREATE TABLE operation.user_managements (
	id			serial4			NOT NULL,
	id_user		varchar(20)		NOT NULL,
	password	varchar(20)		NOT NULL,
	status		varchar(20)		NOT NULL, -- Active, Inactive
	last_login	timestamp,
	created_at	timestamp 		DEFAULT NOW(),
	updated_at	timestamp,
	deleted_at	timestamp,
	CONSTRAINT user_managements_pkey			PRIMARY KEY (id),
	CONSTRAINT user_managements_id_user_fkey	FOREIGN KEY (id_user) REFERENCES operation.users(code_user) ON UPDATE CASCADE ON DELETE CASCADE
);

-- log
CREATE TABLE log.term_desc (
	id 					serial4 	NOT NULL,
	code_term			varchar(20)	NOT NULL,
	term				varchar(20)	NOT NULL, 
	compactness			varchar(20),
	created_at			timestamp	NOT NULL,
	updated_at			timestamp,
	deleted_at			timestamp,
	CONSTRAINT term_desc_pkey 	PRIMARY KEY (id),
	CONSTRAINT term_id_term_key UNIQUE (code_term)
);

CREATE TABLE log.soil_desc (
	id 					serial4 	NOT NULL,
	code_lithology		varchar(20)	NOT NULL,
	soil_type			varchar(20),
	soil_name			varchar(20)	NOT NULL, 
	gr_size				varchar(20),
	created_at			timestamp 	DEFAULT NOW(),
	updated_at			timestamp,
	deleted_at			timestamp,
	CONSTRAINT soil_desc_pkey 	PRIMARY KEY (id),
	CONSTRAINT soil_id_soil_key UNIQUE (code_lithology)
);

CREATE TABLE log.vibrocore_logs (
	id 					serial4 			NOT NULL,
	id_site				varchar(20)			NOT NULL,
	id_client			varchar(20)			NOT NULL,
	id_user				varchar(20)			NOT NULL,
	id_core				varchar(20)			NOT NULL,
	doc_no				varchar(20)			NOT NULL, 
	total_sample_depth	int4				NOT NULL,
	total_attempt		int4				NOT NULL,
	barrel_length		int4				NOT NULL,
	penetration			int4				NOT NULL,
	recovery			int4				NOT NULL,
	heading				int4				NOT NULL,
	time				time				NOT NULL,
	longitude			double precision	NOT NULL,
	latitude			double precision	NOT NULL,
	water_depth			int4				NOT NULL,
	total_soil			int4				NOT NULL,
	created_at			timestamp 			DEFAULT NOW(),
	updated_at			timestamp,
	deleted_at			timestamp,
	CONSTRAINT vibrocore_log_pkey 				PRIMARY KEY (id),
	CONSTRAINT vibrocore_log_doc_no_key 		UNIQUE (doc_no),
	CONSTRAINT vibrocore_log_id_site_fkey 		FOREIGN KEY (id_site) 	REFERENCES operation.sites(code_site) ON UPDATE CASCADE ON DELETE CASCADE,
	CONSTRAINT vibrocore_log_id_client_fkey 	FOREIGN KEY (id_client) REFERENCES operation.clients(code_client) ON UPDATE CASCADE ON DELETE CASCADE,
	CONSTRAINT vibrocore_log_id_checker_fkey 	FOREIGN KEY (id_user) 	REFERENCES operation.users(code_user) ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE TABLE log.vibrocore_log_details (
	id					serial4		NOT NULL,
	id_term				varchar(20)	NOT NULL,
	doc_no				varchar(20)	NOT NULL, 
	code_lithology		varchar(20)	NOT NULL,
	sample_depth_start	int4		NOT NULL,
	sample_depth_end	int4		NOT NULL,
	description			text,	
	torvane				int4,			
	penetrometer		int4,			
	penetration			int4		NOT NULL,
	sequence			int4		NOT NULL,
	created_at			timestamp 	DEFAULT NOW(),
	updated_at			timestamp,
	deleted_at			timestamp,
	CONSTRAINT vibrocore_log_details_pkey 				PRIMARY KEY (id),
	CONSTRAINT vibrocore_log_details_doc_no_fkey 		FOREIGN KEY (doc_no) 			REFERENCES log.vibrocore_logs(doc_no) ON UPDATE CASCADE ON DELETE CASCADE,
	CONSTRAINT vibrocore_log_details_id_term_fkey 		FOREIGN KEY (id_term) 			REFERENCES log.term_desc(code_term) ON UPDATE CASCADE ON DELETE CASCADE,
	CONSTRAINT vibrocore_log_details_id_lithology_fkey 	FOREIGN KEY (code_lithology)	REFERENCES log.soil_desc(code_lithology) ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE TABLE log.sample_logs (
	id 					serial4 	NOT NULL,
	id_vessel			varchar(20)	NOT NULL,
	id_surveyor			varchar(20) NOT NULL,
	id_captain			varchar(20)	NOT NULL,
	id_site				varchar(20)	NOT NULL,
	doc_no				varchar(20)	NOT NULL,
	log_date			date		NOT NULL,
	sample_type			varchar(20)	NOT NULL,
	total_sample		int4,
	packages_number		int4,
	created_at			timestamp 	DEFAULT NOW(),
	updated_at			timestamp,
	deleted_at			timestamp,
	CONSTRAINT sample_logs_pkey 			PRIMARY KEY (id),
	CONSTRAINT sample_doc_no_key 			UNIQUE (doc_no),
	CONSTRAINT sample_logs_id_vessel_fkey 	FOREIGN KEY (id_vessel) 	REFERENCES operation.vessels(code_vessel) ON UPDATE CASCADE ON DELETE CASCADE,
	CONSTRAINT sample_logs_id_surveyor_fkey FOREIGN KEY (id_surveyor) 	REFERENCES operation.users(code_user) ON UPDATE CASCADE ON DELETE CASCADE,
	CONSTRAINT sample_logs_id_captain_fkey 	FOREIGN KEY (id_captain) 	REFERENCES operation.users(code_user) ON UPDATE CASCADE ON DELETE CASCADE,
	CONSTRAINT sample_logs_id_site_fkey 	FOREIGN KEY (id_site) 		REFERENCES operation.sites(code_site) ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE TABLE log.sample_log_details (
	id					serial4		NOT NULL,
	id_term				varchar(20)	NOT NULL,
	id_lithology		varchar(20)	NOT NULL,
	doc_no				varchar(20)	NOT NULL, 
	sample_depth_start	int4		NOT NULL,
	sample_depth_end	int4		NOT NULL,
	description			text,	
	torvane				int4,			
	penetrometer		int4,			
	penetration			int4		NOT NULL,
	sequence			int4		NOT NULL,
	created_at			timestamp 	DEFAULT NOW(),
	updated_at			timestamp,
	deleted_at			timestamp,
	CONSTRAINT sample_log_details_pkey 					PRIMARY KEY (id),
	CONSTRAINT sample_log_details_doc_no_fkey 			FOREIGN KEY (doc_no) 		REFERENCES log.sample_logs(doc_no) ON UPDATE CASCADE ON DELETE CASCADE,
	CONSTRAINT sample_log_details_id_term_fkey 			FOREIGN KEY (id_term) 		REFERENCES log.term_desc(code_term) ON UPDATE CASCADE ON DELETE CASCADE,
	CONSTRAINT sample_log_details_id_lithology_fkey 	FOREIGN KEY (id_lithology)	REFERENCES log.soil_desc(code_lithology) ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE TABLE log.surveis (
	id			serial4			NOT NULL,
	id_site		varchar(20)		NOT NULL,
	id_surveyor	varchar(20)		NOT NULL,
	code_survey	varchar(20)		NOT NULL,
	doc_no		varchar(20)		NOT NULL,
	core_no		varchar(20)		NOT NULL,
	status		varchar(20)		NOT NULL,
	created_at	timestamp 		DEFAULT NOW(),
	updated_at	timestamp,
	deleted_at	timestamp,
	CONSTRAINT	surveis_pkey				PRIMARY KEY (id),
	CONSTRAINT	surveis_code_survey_key		UNIQUE (code_survey),
	CONSTRAINT	surveis_id_site_fkey		FOREIGN KEY (id_site)		REFERENCES operation.sites(code_site) ON UPDATE CASCADE ON DELETE CASCADE,
	CONSTRAINT	surveis_id_surveyor_fkey	FOREIGN KEY (id_surveyor)	REFERENCES operation.users(code_user) ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE TABLE log.survey_details (
	id			serial4			NOT NULL,
	id_survey	varchar(20)		NOT NULL,
	created_at	timestamp 		DEFAULT NOW(),
	updated_at	timestamp,
	deleted_at	timestamp,
	CONSTRAINT survey_details_pkey				PRIMARY KEY (id),
	CONSTRAINT survey_details_id_survey_fkey	FOREIGN KEY (id_survey)		REFERENCES log.surveis(code_survey) ON UPDATE CASCADE ON DELETE CASCADE
);

-- rockworks
CREATE TABLE rockworks.aquifertype (
	aquifertypeid int4 NOT NULL,
	"name" varchar(80) DEFAULT 'undefined'::character varying NOT NULL,
	patterntypeid int4 DEFAULT 1 NULL,
	patternsize float8 DEFAULT 3 NULL,
	patternthick int4 DEFAULT 1 NULL,
	background int4 DEFAULT 16777215 NULL,
	foreground int4 DEFAULT 0 NULL,
	fillpercent int4 DEFAULT 100 NULL,
	density float8 DEFAULT 1 NULL,
	gvalue float8 DEFAULT 1 NOT NULL,
	showinlegend bool DEFAULT true NULL,
	CONSTRAINT log_sys_pk_11413 PRIMARY KEY (aquifertypeid)
);

CREATE TABLE rockworks.bitmaptype (
	bitmaptypeid int4 NOT NULL,
	"name" varchar(80) DEFAULT 'undefined'::character varying NOT NULL,
	patterntypeid int4 DEFAULT 1 NULL,
	patternsize float8 DEFAULT 3 NULL,
	patternthick int4 DEFAULT 1 NULL,
	background int4 DEFAULT 16777215 NULL,
	foreground int4 DEFAULT 0 NULL,
	fillpercent int4 DEFAULT 100 NULL,
	density float8 DEFAULT 1 NULL,
	gvalue float8 DEFAULT 1 NOT NULL,
	showinlegend bool DEFAULT true NULL,
	CONSTRAINT log_sys_pk_11432 PRIMARY KEY (bitmaptypeid)
);

CREATE TABLE rockworks.fence (
	fenceid int4 NOT NULL,
	x1 float8 NOT NULL,
	y1 float8 NOT NULL,
	x2 float8 NOT NULL,
	y2 float8 NOT NULL,
	CONSTRAINT log_sys_pk_11440 PRIMARY KEY (fenceid)
);

CREATE TABLE rockworks.hydrostrattype (
	hydrostrattypeid int4 NOT NULL,
	"name" varchar(80) DEFAULT 'undefined'::character varying NOT NULL,
	patterntypeid int4 DEFAULT 1 NULL,
	patternsize float8 DEFAULT 3 NULL,
	patternthick int4 DEFAULT 1 NULL,
	background int4 DEFAULT 16777215 NULL,
	foreground int4 DEFAULT 0 NULL,
	fillpercent int4 DEFAULT 100 NULL,
	density float8 DEFAULT 1 NULL,
	gvalue float8 DEFAULT 1 NOT NULL,
	showinlegend bool DEFAULT true NULL,
	CONSTRAINT log_sys_pk_11478 PRIMARY KEY (hydrostrattypeid)
);

CREATE TABLE rockworks.intervaltype (
	intervaltypeid int4 NOT NULL,
	"name" varchar(80) NOT NULL,
	"minvalue" float8 NULL,
	"maxvalue" float8 NULL,
	units varchar(10) NULL,
	detectionlimit float8 NULL,
	rangechecking bool DEFAULT false NULL,
	description varchar(255) NULL,
	sortorder float8 DEFAULT 1 NULL,
	page int4 DEFAULT 1 NULL,
	visible bool DEFAULT true NULL,
	CONSTRAINT log_sys_pk_11500 PRIMARY KEY (intervaltypeid)
);

CREATE TABLE rockworks.itexttype (
	itexttypeid int4 NOT NULL,
	"name" varchar(80) NOT NULL,
	description varchar(255) NULL,
	sortorder float8 DEFAULT 1 NULL,
	page int4 DEFAULT 1 NULL,
	visible bool DEFAULT true NULL,
	CONSTRAINT log_sys_pk_11515 PRIMARY KEY (itexttypeid)
);

CREATE TABLE rockworks.lithtype (
	lithtypeid int4 NOT NULL,
	"name" varchar(80) DEFAULT 'undefined'::character varying NOT NULL,
	patterntypeid int4 DEFAULT 1 NULL,
	patternsize float8 DEFAULT 3 NULL,
	patternthick int4 DEFAULT 1 NULL,
	background int4 DEFAULT 16777215 NULL,
	foreground int4 DEFAULT 0 NULL,
	fillpercent int4 DEFAULT 100 NULL,
	density float8 DEFAULT 1 NULL,
	gvalue float8 DEFAULT 1 NOT NULL,
	showinlegend bool DEFAULT true NULL,
	CONSTRAINT log_sys_pk_11539 PRIMARY KEY (lithtypeid)
);

CREATE TABLE rockworks."location" (
	bhid int4 NOT NULL,
	"name" varchar(80) NOT NULL,
	enabled bool DEFAULT true NULL,
	easting float8 NOT NULL,
	northing float8 NOT NULL,
	elevation float8 DEFAULT 0 NOT NULL,
	totaldepth float8 DEFAULT 0 NOT NULL,
	collarelevation float8 DEFAULT 0 NOT NULL,
	"comments" text NULL,
	geicon int4 DEFAULT 1 NULL,
	color int4 DEFAULT 0 NULL,
	symboltypeid int4 DEFAULT 14 NULL,
	needxyzcalc bool DEFAULT true NULL,
	orientation int4 DEFAULT 1 NULL,
	dd_lon float8 DEFAULT 0 NULL,
	dd_lat float8 DEFAULT 0 NULL,
	lcs_x float8 DEFAULT 0 NULL,
	lcs_y float8 DEFAULT 0 NULL,
	lcs_unit int4 DEFAULT 1 NULL,
	pls_meridian int4 DEFAULT 6 NULL,
	pls_range int4 DEFAULT 0 NULL,
	pls_township int4 DEFAULT 0 NULL,
	pls_section int4 DEFAULT 0 NULL,
	pls_offset_based bool DEFAULT true NULL,
	pls_x_offset float8 DEFAULT 0 NULL,
	pls_y_offset float8 DEFAULT 0 NULL,
	pls_fwl bool DEFAULT false NULL,
	pls_fsl bool DEFAULT false NULL,
	pls_description varchar(255) DEFAULT ''::character varying NULL,
	spc_zone int4 DEFAULT 502 NULL,
	spc_x float8 DEFAULT 0 NULL,
	spc_y float8 DEFAULT 0 NULL,
	spc_unit int4 DEFAULT 1 NULL,
	utm_datum int4 DEFAULT 22 NULL,
	utm_zone int4 DEFAULT 12 NULL,
	utm_x float8 DEFAULT 0 NULL,
	utm_y float8 DEFAULT 0 NULL,
	utm_unit int4 DEFAULT 1 NULL,
	CONSTRAINT log_sys_pk_11558 PRIMARY KEY (bhid)
);

CREATE TABLE rockworks.lookuplists (
	listid int4 NOT NULL,
	tablename varchar(255) NOT NULL,
	fieldname varchar(255) NOT NULL,
	listvalue varchar(255) NOT NULL,
	CONSTRAINT log_sys_pk_11580 PRIMARY KEY (listid)
);

CREATE TABLE rockworks.pointtype (
	pointtypeid int4 NOT NULL,
	"name" varchar(80) NOT NULL,
	"minvalue" float8 NULL,
	"maxvalue" float8 NULL,
	units varchar(10) NULL,
	detectionlimit float8 NULL,
	rangechecking bool DEFAULT false NULL,
	description varchar(255) NULL,
	sortorder float8 DEFAULT 1 NULL,
	page int4 DEFAULT 1 NULL,
	visible bool DEFAULT true NULL,
	CONSTRAINT log_sys_pk_11631 PRIMARY KEY (pointtypeid)
);

CREATE TABLE rockworks.projectdesc (
	projectdescid int4 NOT NULL,
	projdesc bytea NULL,
	dlgtop int4 NULL,
	dlgleft int4 NULL,
	dlgheight int4 NULL,
	dlgwidth int4 NULL,
	CONSTRAINT log_sys_pk_11638 PRIMARY KEY (projectdescid)
);

CREATE TABLE rockworks.projectinfo (
	projectinfoid int4 NOT NULL,
	item varchar(50) NOT NULL,
	category varchar(50) NOT NULL,
	value varchar(255) NOT NULL,
	CONSTRAINT log_sys_pk_11653 PRIMARY KEY (projectinfoid)
);

CREATE TABLE rockworks.projecttables (
	projecttablesid int4 NOT NULL,
	tabletype varchar(50) NOT NULL,
	tablename varchar(50) NOT NULL,
	CONSTRAINT log_sys_pk_11662 PRIMARY KEY (projecttablesid)
);

CREATE TABLE rockworks.ptexttype (
	ptexttypeid int4 NOT NULL,
	"name" varchar(80) NOT NULL,
	description varchar(255) NULL,
	sortorder float8 DEFAULT 1 NULL,
	page int4 DEFAULT 1 NULL,
	visible bool DEFAULT true NULL,
	CONSTRAINT log_sys_pk_11688 PRIMARY KEY (ptexttypeid)
);

CREATE TABLE rockworks."section" (
	sectionid int4 NOT NULL,
	x float8 NOT NULL,
	y float8 NOT NULL,
	CONSTRAINT log_sys_pk_11705 PRIMARY KEY (sectionid)
);

CREATE TABLE rockworks.strattype (
	strattypeid int4 NOT NULL,
	"name" varchar(80) DEFAULT 'undefined'::character varying NOT NULL,
	patterntypeid int4 DEFAULT 1 NULL,
	patternsize float8 DEFAULT 3 NULL,
	patternthick int4 DEFAULT 1 NULL,
	background int4 DEFAULT 16777215 NULL,
	foreground int4 DEFAULT 0 NULL,
	fillpercent int4 DEFAULT 100 NULL,
	density float8 DEFAULT 1 NULL,
	gvalue float8 DEFAULT 1 NOT NULL,
	showinlegend bool DEFAULT true NULL,
	CONSTRAINT log_sys_pk_11728 PRIMARY KEY (strattypeid)
);

CREATE TABLE rockworks.tmintervaltype (
	tmintervaltypeid int4 NOT NULL,
	"name" varchar(80) NOT NULL,
	"minvalue" float8 NULL,
	"maxvalue" float8 NULL,
	units varchar(10) NULL,
	detectionlimit float8 NULL,
	rangechecking bool DEFAULT false NULL,
	description varchar(255) NULL,
	sortorder float8 DEFAULT 1 NULL,
	page int4 DEFAULT 1 NULL,
	visible bool DEFAULT true NULL,
	CONSTRAINT log_sys_pk_11830 PRIMARY KEY (tmintervaltypeid)
);

CREATE TABLE rockworks.wellconstructiontype (
	wellconsttypeid int4 NOT NULL,
	"name" varchar(80) DEFAULT 'undefined'::character varying NOT NULL,
	patterntypeid int4 DEFAULT 1 NULL,
	patternsize float8 DEFAULT 3 NULL,
	patternthick int4 DEFAULT 1 NULL,
	background int4 DEFAULT 16777215 NULL,
	foreground int4 DEFAULT 0 NULL,
	fillpercent int4 DEFAULT 100 NULL,
	density float8 DEFAULT 1 NULL,
	gvalue float8 DEFAULT 1 NOT NULL,
	showinlegend bool DEFAULT true NULL,
	CONSTRAINT log_sys_pk_11956 PRIMARY KEY (wellconsttypeid)
);

CREATE TABLE rockworks.aquifer (
	aquiferid int4 NOT NULL,
	bhid int4 NOT NULL,
	depth1 float8 NOT NULL,
	depth2 float8 NOT NULL,
	aquifertypeid int4 NOT NULL,
	sampledate timestamp NOT NULL,
	"comment" text NULL,
	x1 float8 NULL,
	y1 float8 NULL,
	z1 float8 NULL,
	x2 float8 NULL,
	y2 float8 NULL,
	z2 float8 NULL,
	CONSTRAINT log_sys_pk_11395 PRIMARY KEY (aquiferid),
	CONSTRAINT log_aquifer_fk_aquifertypeaquifer FOREIGN KEY (aquifertypeid) REFERENCES rockworks.aquifertype(aquifertypeid),
	CONSTRAINT log_aquifer_fk_locationaquifer FOREIGN KEY (bhid) REFERENCES rockworks."location"(bhid)
);

CREATE TABLE rockworks.bitmap (
	bitmapid int4 NOT NULL,
	bhid int4 NOT NULL,
	depth1 float8 NOT NULL,
	depth2 float8 NOT NULL,
	bitmaptypeid int4 NOT NULL,
	"header" int4 NULL,
	footer int4 NULL,
	filename varchar(255) NOT NULL,
	depth1adj float8 NULL,
	depth2adj float8 NULL,
	bitmapwidth int4 NULL,
	bitmapheight int4 NULL,
	dataok bool DEFAULT true NULL,
	x1 float8 NULL,
	y1 float8 NULL,
	z1 float8 NULL,
	x2 float8 NULL,
	y2 float8 NULL,
	z2 float8 NULL,
	CONSTRAINT log_sys_pk_11421 PRIMARY KEY (bitmapid),
	CONSTRAINT log_bitmap_fk_bitmaptypebitmap FOREIGN KEY (bitmaptypeid) REFERENCES rockworks.bitmaptype(bitmaptypeid),
	CONSTRAINT log_bitmap_fk_locationbitmap FOREIGN KEY (bhid) REFERENCES rockworks."location"(bhid)
);

CREATE TABLE rockworks.fracture (
	fractureid int4 NOT NULL,
	bhid int4 NOT NULL,
	"depth" float8 NOT NULL,
	azimuth float8 NOT NULL,
	inclination float8 NOT NULL,
	radius float8 NOT NULL,
	aperture float8 NOT NULL,
	color int4 DEFAULT 0 NOT NULL,
	"comment" varchar(255) NULL,
	x float8 NULL,
	y float8 NULL,
	z float8 NULL,
	CONSTRAINT log_sys_pk_11450 PRIMARY KEY (fractureid),
	CONSTRAINT log_fracture_fk_locationfracture FOREIGN KEY (bhid) REFERENCES rockworks."location"(bhid)
);

CREATE TABLE rockworks.hydrostratigraphy (
	hydrostratid int4 NOT NULL,
	bhid int4 NOT NULL,
	depth1 float8 NULL,
	depth2 float8 NULL,
	hydrostrattypeid int4 NOT NULL,
	"comment" text NULL,
	x1 float8 NULL,
	y1 float8 NULL,
	z1 float8 NULL,
	x2 float8 NULL,
	y2 float8 NULL,
	z2 float8 NULL,
	CONSTRAINT log_sys_pk_11463 PRIMARY KEY (hydrostratid),
	CONSTRAINT log_hydrostratigraphy_fk_hydrostrattypehydrostratigraphy FOREIGN KEY (hydrostrattypeid) REFERENCES rockworks.hydrostrattype(hydrostrattypeid),
	CONSTRAINT log_hydrostratigraphy_fk_locationhydrostratigraphy FOREIGN KEY (bhid) REFERENCES rockworks."location"(bhid)
);

CREATE TABLE rockworks."interval" (
	intervalid int4 NOT NULL,
	bhid int4 NOT NULL,
	intervaltypeid int4 NOT NULL,
	depth1 float8 NULL,
	depth2 float8 NULL,
	value float8 NULL,
	"comment" varchar(255) NULL,
	x1 float8 NULL,
	y1 float8 NULL,
	z1 float8 NULL,
	x2 float8 NULL,
	y2 float8 NULL,
	z2 float8 NULL,
	CONSTRAINT log_sys_pk_11486 PRIMARY KEY (intervalid),
	CONSTRAINT log_interval_fk_intervaltypeinterval FOREIGN KEY (intervaltypeid) REFERENCES rockworks.intervaltype(intervaltypeid),
	CONSTRAINT log_interval_fk_locationinterval FOREIGN KEY (bhid) REFERENCES rockworks."location"(bhid)
);

CREATE TABLE rockworks.itext (
	itextid int4 NOT NULL,
	bhid int4 NOT NULL,
	itexttypeid int4 NOT NULL,
	depth1 float8 NULL,
	depth2 float8 NULL,
	value varchar(255) NULL,
	"comment" varchar(255) NULL,
	x1 float8 NULL,
	y1 float8 NULL,
	z1 float8 NULL,
	x2 float8 NULL,
	y2 float8 NULL,
	z2 float8 NULL,
	CONSTRAINT log_sys_pk_11507 PRIMARY KEY (itextid),
	CONSTRAINT log_itext_fk_itexttypeitext FOREIGN KEY (itexttypeid) REFERENCES rockworks.itexttype(itexttypeid),
	CONSTRAINT log_itext_fk_locationitext FOREIGN KEY (bhid) REFERENCES rockworks."location"(bhid)
);

CREATE TABLE rockworks.lithology (
	lithid int4 NOT NULL,
	bhid int4 NOT NULL,
	depth1 float8 NOT NULL,
	depth2 float8 NOT NULL,
	lithtypeid int4 NOT NULL,
	"comment" text NULL,
	x1 float8 NULL,
	y1 float8 NULL,
	z1 float8 NULL,
	x2 float8 NULL,
	y2 float8 NULL,
	z2 float8 NULL,
	CONSTRAINT log_sys_pk_11522 PRIMARY KEY (lithid),
	CONSTRAINT log_lithology_fk_lithtypelithology FOREIGN KEY (lithtypeid) REFERENCES rockworks.lithtype(lithtypeid),
	CONSTRAINT log_lithology_fk_locationlithology FOREIGN KEY (bhid) REFERENCES rockworks."location"(bhid)
);

CREATE TABLE rockworks.orientation (
	orientationid int4 NOT NULL,
	bhid int4 NOT NULL,
	"depth" float8 NOT NULL,
	azimuth float8 NOT NULL,
	inclination float8 NOT NULL,
	CONSTRAINT log_sys_pk_11589 PRIMARY KEY (orientationid),
	CONSTRAINT log_orientation_fk_locationorientation FOREIGN KEY (bhid) REFERENCES rockworks."location"(bhid)
);

CREATE TABLE rockworks.ouroboros (
	ouroborosid int4 NOT NULL,
	bhid int4 NOT NULL,
	"depth" float8 NULL,
	azimuth float8 NULL,
	inclination float8 NULL,
	x float8 NULL,
	y float8 NULL,
	z float8 NULL,
	CONSTRAINT log_sys_pk_11599 PRIMARY KEY (ouroborosid),
	CONSTRAINT log_ouroboros_fk_locationouroboros FOREIGN KEY (bhid) REFERENCES rockworks."location"(bhid)
);

CREATE TABLE rockworks.pattern (
	patternid int4 NOT NULL,
	bhid int4 NOT NULL,
	depth1 float8 NOT NULL,
	depth2 float8 NOT NULL,
	patterntypeid int4 DEFAULT 1 NULL,
	patternsize float8 DEFAULT 3 NULL,
	patternthick int4 DEFAULT 1 NULL,
	background int4 DEFAULT 16777215 NULL,
	foreground int4 DEFAULT 0 NULL,
	"comment" varchar(255) NULL,
	x1 float8 NULL,
	y1 float8 NULL,
	z1 float8 NULL,
	x2 float8 NULL,
	y2 float8 NULL,
	z2 float8 NULL,
	CONSTRAINT log_sys_pk_11606 PRIMARY KEY (patternid),
	CONSTRAINT log_pattern_fk_locationpattern FOREIGN KEY (bhid) REFERENCES rockworks."location"(bhid)
);

CREATE TABLE rockworks.point (
	pointid int4 NOT NULL,
	bhid int4 NOT NULL,
	pointtypeid int4 NOT NULL,
	"depth" float8 NOT NULL,
	value float8 NOT NULL,
	"comment" varchar(255) NULL,
	x float8 NULL,
	y float8 NULL,
	z float8 NULL,
	CONSTRAINT log_sys_pk_11615 PRIMARY KEY (pointid),
	CONSTRAINT log_point_fk_locationpoint FOREIGN KEY (bhid) REFERENCES rockworks."location"(bhid),
	CONSTRAINT log_point_fk_pointtypepoint FOREIGN KEY (pointtypeid) REFERENCES rockworks.pointtype(pointtypeid)
);

CREATE TABLE rockworks.ptext (
	ptextid int4 NOT NULL,
	bhid int4 NOT NULL,
	ptexttypeid int4 NOT NULL,
	"depth" float8 NOT NULL,
	value varchar(255) NOT NULL,
	"comment" varchar(255) NULL,
	x float8 NULL,
	y float8 NULL,
	z float8 NULL,
	CONSTRAINT log_sys_pk_11678 PRIMARY KEY (ptextid),
	CONSTRAINT log_ptext_fk_locationptext FOREIGN KEY (bhid) REFERENCES rockworks."location"(bhid),
	CONSTRAINT log_ptext_fk_ptexttypeptext FOREIGN KEY (ptexttypeid) REFERENCES rockworks.ptexttype(ptexttypeid)
);

CREATE TABLE rockworks.rockcolor (
	rockcolorid int4 NOT NULL,
	bhid int4 NOT NULL,
	depth1 float8 NOT NULL,
	depth2 float8 NOT NULL,
	color int4 DEFAULT 16777215 NOT NULL,
	colortext varchar(255) NULL,
	x1 float8 NULL,
	y1 float8 NULL,
	z1 float8 NULL,
	x2 float8 NULL,
	y2 float8 NULL,
	z2 float8 NULL,
	CONSTRAINT log_sys_pk_11695 PRIMARY KEY (rockcolorid),
	CONSTRAINT log_rockcolor_fk_locationrockcolor FOREIGN KEY (bhid) REFERENCES rockworks."location"(bhid)
);

CREATE TABLE rockworks.stratigraphy (
	stratid int4 NOT NULL,
	bhid int4 NOT NULL,
	depth1 float8 NULL,
	depth2 float8 NULL,
	strattypeid int4 NOT NULL,
	d1dipdirection float8 NULL,
	d1dipangle float8 NULL,
	d2dipdirection float8 NULL,
	d2dipangle float8 NULL,
	"comment" text NULL,
	x1 float8 NULL,
	y1 float8 NULL,
	z1 float8 NULL,
	x2 float8 NULL,
	y2 float8 NULL,
	z2 float8 NULL,
	CONSTRAINT log_sys_pk_11713 PRIMARY KEY (stratid),
	CONSTRAINT log_stratigraphy_fk_locationstratigraphy FOREIGN KEY (bhid) REFERENCES rockworks."location"(bhid),
	CONSTRAINT log_stratigraphy_fk_strattypestratigraphy FOREIGN KEY (strattypeid) REFERENCES rockworks.strattype(strattypeid)
);

CREATE TABLE rockworks.symbol (
	symbolid int4 NOT NULL,
	bhid int4 NOT NULL,
	"depth" float8 NOT NULL,
	"comment" varchar(255) NULL,
	symboltypeid int4 DEFAULT 14 NULL,
	color int4 DEFAULT 0 NULL,
	x float8 NULL,
	y float8 NULL,
	z float8 NULL,
	CONSTRAINT log_sys_pk_11736 PRIMARY KEY (symbolid),
	CONSTRAINT log_symbol_fk_locationsymbol FOREIGN KEY (bhid) REFERENCES rockworks."location"(bhid)
);

CREATE TABLE rockworks.t3dpointmaprange (
	id int4 NOT NULL,
	projecttablesid int4 NOT NULL,
	sortorder float8 NOT NULL,
	minimum float8 NULL,
	maximum float8 NULL,
	displaysize float8 NULL,
	color int4 NULL,
	CONSTRAINT log_sys_pk_11744 PRIMARY KEY (id),
	CONSTRAINT log_t3dpointmaprange_fk_projecttablest3dpointmaprange FOREIGN KEY (projecttablesid) REFERENCES rockworks.projecttables(projecttablesid)
);

CREATE TABLE rockworks.tbargraphscale (
	id int4 NOT NULL,
	projecttablesid int4 NOT NULL,
	sortorder float8 NOT NULL,
	"minvalue" float8 NULL,
	"maxvalue" float8 NULL,
	displaysize float8 NULL,
	CONSTRAINT log_sys_pk_11752 PRIMARY KEY (id),
	CONSTRAINT log_tbargraphscale_fk_projecttablestbargraphscale FOREIGN KEY (projecttablesid) REFERENCES rockworks.projecttables(projecttablesid)
);

CREATE TABLE rockworks.tcolorindex (
	id int4 NOT NULL,
	projecttablesid int4 NOT NULL,
	sortorder float8 NOT NULL,
	color int4 NULL,
	caption varchar(60) NULL,
	CONSTRAINT log_sys_pk_11760 PRIMARY KEY (id),
	CONSTRAINT log_tcolorindex_fk_projecttablestcolorindex FOREIGN KEY (projecttablesid) REFERENCES rockworks.projecttables(projecttablesid)
);

CREATE TABLE rockworks.tcontour (
	id int4 NOT NULL,
	projecttablesid int4 NOT NULL,
	sortorder float8 NOT NULL,
	"level" float8 NULL,
	linestyle int4 DEFAULT 0 NULL,
	linewidth int4 DEFAULT 1 NULL,
	linecolor int4 DEFAULT 0 NULL,
	"label" varchar(60) NULL,
	CONSTRAINT log_sys_pk_11768 PRIMARY KEY (id),
	CONSTRAINT log_tcontour_fk_projecttablestcontour FOREIGN KEY (projecttablesid) REFERENCES rockworks.projecttables(projecttablesid)
);

CREATE TABLE rockworks.tdwgriddingsector (
	id int4 NOT NULL,
	projecttablesid int4 NOT NULL,
	sortorder float8 NOT NULL,
	minangle int4 NULL,
	maxangle int4 NULL,
	exponent float8 NULL,
	CONSTRAINT log_sys_pk_11776 PRIMARY KEY (id),
	CONSTRAINT log_tdwgriddingsector_fk_projecttablestdwgriddingsector FOREIGN KEY (projecttablesid) REFERENCES rockworks.projecttables(projecttablesid)
);

CREATE TABLE rockworks.tfaults (
	id int4 NOT NULL,
	projecttablesid int4 NOT NULL,
	sortorder float8 NOT NULL,
	x1 float8 NULL,
	y1 float8 NULL,
	x2 float8 NULL,
	y2 float8 NULL,
	CONSTRAINT log_sys_pk_11784 PRIMARY KEY (id),
	CONSTRAINT log_tfaults_fk_projecttablestfaults FOREIGN KEY (projecttablesid) REFERENCES rockworks.projecttables(projecttablesid)
);

CREATE TABLE rockworks.tidwsolidmodelingsec (
	id int4 NOT NULL,
	projecttablesid int4 NOT NULL,
	sortorder float8 NOT NULL,
	mininclination float8 NULL,
	maxinclination float8 NULL,
	minazimuth float8 NULL,
	maxazimuth float8 NULL,
	maxdistance float8 NULL,
	CONSTRAINT log_sys_pk_11792 PRIMARY KEY (id),
	CONSTRAINT log_tidwsolidmodelingsec_fk_projecttablestidwsolidmodelingsec FOREIGN KEY (projecttablesid) REFERENCES rockworks.projecttables(projecttablesid)
);

CREATE TABLE rockworks.tlinestyleindex (
	id int4 NOT NULL,
	projecttablesid int4 NOT NULL,
	sortorder float8 NOT NULL,
	linestyle int4 DEFAULT 0 NULL,
	linewidth int4 DEFAULT 1 NULL,
	linecolor int4 DEFAULT 0 NULL,
	caption varchar(60) NULL,
	CONSTRAINT log_sys_pk_11800 PRIMARY KEY (id),
	CONSTRAINT log_tlinestyleindex_fk_projecttablestlinestyleindex FOREIGN KEY (projecttablesid) REFERENCES rockworks.projecttables(projecttablesid)
);

CREATE TABLE rockworks.tminmaxcolor (
	id int4 NOT NULL,
	projecttablesid int4 NOT NULL,
	sortorder float8 NOT NULL,
	"minvalue" float8 NULL,
	"maxvalue" float8 NULL,
	color int4 DEFAULT 0 NULL,
	CONSTRAINT log_sys_pk_11808 PRIMARY KEY (id),
	CONSTRAINT log_tminmaxcolor_fk_projecttablestminmaxcolor FOREIGN KEY (projecttablesid) REFERENCES rockworks.projecttables(projecttablesid)
);

CREATE TABLE rockworks.tminterval (
	tmintervalid int4 NOT NULL,
	bhid int4 NOT NULL,
	tmintervaltypeid int4 NOT NULL,
	depth1 float8 NULL,
	depth2 float8 NULL,
	sampledate timestamp NULL,
	value float8 NULL,
	"comment" varchar(255) NULL,
	x1 float8 NULL,
	y1 float8 NULL,
	z1 float8 NULL,
	x2 float8 NULL,
	y2 float8 NULL,
	z2 float8 NULL,
	CONSTRAINT log_sys_pk_11816 PRIMARY KEY (tmintervalid),
	CONSTRAINT log_tminterval_fk_locationtminterval FOREIGN KEY (bhid) REFERENCES rockworks."location"(bhid),
	CONSTRAINT log_tminterval_fk_tmintervaltypetminterval FOREIGN KEY (tmintervaltypeid) REFERENCES rockworks.tmintervaltype(tmintervaltypeid)
);

CREATE TABLE rockworks.tpatternindex (
	id int4 NOT NULL,
	projecttablesid int4 NOT NULL,
	sortorder float8 NOT NULL,
	patterntypeid int4 DEFAULT 1 NULL,
	patternsize float8 DEFAULT 3 NULL,
	patternthick int4 DEFAULT 1 NULL,
	background int4 DEFAULT 16777215 NULL,
	foreground int4 DEFAULT 0 NULL,
	caption varchar(150) NULL,
	CONSTRAINT log_sys_pk_11837 PRIMARY KEY (id),
	CONSTRAINT log_tpatternindex_fk_projecttablestpatternindex FOREIGN KEY (projecttablesid) REFERENCES rockworks.projecttables(projecttablesid)
);

CREATE TABLE rockworks.tpointmaprange (
	id int4 NOT NULL,
	projecttablesid int4 NOT NULL,
	sortorder float8 NOT NULL,
	minimum float8 NULL,
	maximum float8 NULL,
	symboltypeid int4 NULL,
	color int4 NULL,
	displaysize float8 NULL,
	CONSTRAINT log_sys_pk_11845 PRIMARY KEY (id),
	CONSTRAINT log_tpointmaprange_fk_projecttablestpointmaprange FOREIGN KEY (projecttablesid) REFERENCES rockworks.projecttables(projecttablesid)
);

CREATE TABLE rockworks.tpolygon (
	id int4 NOT NULL,
	projecttablesid int4 NOT NULL,
	sortorder float8 NOT NULL,
	x float8 NULL,
	y float8 NULL,
	CONSTRAINT log_sys_pk_11853 PRIMARY KEY (id),
	CONSTRAINT log_tpolygon_fk_projecttablestpolygon FOREIGN KEY (projecttablesid) REFERENCES rockworks.projecttables(projecttablesid)
);

CREATE TABLE rockworks.tpolygons (
	id int4 NOT NULL,
	projecttablesid int4 NOT NULL,
	sortorder float8 NOT NULL,
	linestyle int4 DEFAULT 0 NULL,
	linewidth int4 DEFAULT 1 NULL,
	linecolor int4 DEFAULT 0 NULL,
	patterntypeid int4 DEFAULT 1 NULL,
	patternsize float8 DEFAULT 3 NULL,
	patternthick int4 DEFAULT 1 NULL,
	background int4 DEFAULT 16777215 NULL,
	foreground int4 DEFAULT 0 NULL,
	caption varchar(150) NULL,
	CONSTRAINT log_sys_pk_11869 PRIMARY KEY (id),
	CONSTRAINT log_tpolygons_fk_projecttablestpolygons FOREIGN KEY (projecttablesid) REFERENCES rockworks.projecttables(projecttablesid)
);

CREATE TABLE rockworks.tprofile (
	id int4 NOT NULL,
	projecttablesid int4 NOT NULL,
	sortorder float8 NOT NULL,
	x1 float8 NULL,
	y1 float8 NULL,
	x2 float8 NULL,
	y2 float8 NULL,
	swath float8 NULL,
	CONSTRAINT log_sys_pk_11877 PRIMARY KEY (id),
	CONSTRAINT log_tprofile_fk_projecttablestprofile FOREIGN KEY (projecttablesid) REFERENCES rockworks.projecttables(projecttablesid)
);

CREATE TABLE rockworks.tsymbolindex (
	id int4 NOT NULL,
	projecttablesid int4 NOT NULL,
	sortorder float8 NOT NULL,
	symboltypeid int4 DEFAULT 1 NULL,
	color int4 DEFAULT 0 NULL,
	caption varchar(150) NULL,
	CONSTRAINT log_sys_pk_11885 PRIMARY KEY (id),
	CONSTRAINT log_tsymbolindex_fk_projecttablestsymbolindex FOREIGN KEY (projecttablesid) REFERENCES rockworks.projecttables(projecttablesid)
);

CREATE TABLE rockworks.tsynonym (
	id int4 NOT NULL,
	projecttablesid int4 NOT NULL,
	sortorder float8 NOT NULL,
	"target" varchar(255) NULL,
	replacement varchar(255) NULL,
	CONSTRAINT log_sys_pk_11893 PRIMARY KEY (id),
	CONSTRAINT log_tsynonym_fk_projecttablestsynonym FOREIGN KEY (projecttablesid) REFERENCES rockworks.projecttables(projecttablesid)
);

CREATE TABLE rockworks.txycoordinate (
	id int4 NOT NULL,
	projecttablesid int4 NOT NULL,
	sortorder float8 NOT NULL,
	x float8 NULL,
	y float8 NULL,
	CONSTRAINT log_sys_pk_11901 PRIMARY KEY (id),
	CONSTRAINT log_txycoordinate_fk_projecttablestxycoordinate FOREIGN KEY (projecttablesid) REFERENCES rockworks.projecttables(projecttablesid)
);

CREATE TABLE rockworks.txypair (
	id int4 NOT NULL,
	projecttablesid int4 NOT NULL,
	sortorder float8 NOT NULL,
	x1 float8 NULL,
	y1 float8 NULL,
	x2 float8 NULL,
	y2 float8 NULL,
	CONSTRAINT log_sys_pk_11909 PRIMARY KEY (id),
	CONSTRAINT log_txypair_fk_projecttablestxypair FOREIGN KEY (projecttablesid) REFERENCES rockworks.projecttables(projecttablesid)
);

CREATE TABLE rockworks.txyz (
	id int4 NOT NULL,
	projecttablesid int4 NOT NULL,
	sortorder float8 NOT NULL,
	x float8 NULL,
	y float8 NULL,
	z float8 NULL,
	"comment" varchar(150) NULL,
	CONSTRAINT log_sys_pk_11917 PRIMARY KEY (id),
	CONSTRAINT log_txyz_fk_projecttablestxyz FOREIGN KEY (projecttablesid) REFERENCES rockworks.projecttables(projecttablesid)
);

CREATE TABLE rockworks.vector (
	vectorid int4 NOT NULL,
	bhid int4 NOT NULL,
	"depth" float8 NOT NULL,
	azimuth float8 NOT NULL,
	inclination float8 NOT NULL,
	color int4 DEFAULT 0 NOT NULL,
	value float8 NOT NULL,
	"comment" varchar(255) NULL,
	x float8 NULL,
	y float8 NULL,
	z float8 NULL,
	CONSTRAINT log_sys_pk_11925 PRIMARY KEY (vectorid),
	CONSTRAINT log_vector_fk_locationvector FOREIGN KEY (bhid) REFERENCES rockworks."location"(bhid)
);

CREATE TABLE rockworks.wellconstruction (
	wellconstructionid int4 NOT NULL,
	bhid int4 NOT NULL,
	"Offset" float8 DEFAULT 0 NULL,
	depth1 float8 NOT NULL,
	depth2 float8 NOT NULL,
	diameter1 float8 NOT NULL,
	diameter2 float8 NOT NULL,
	wellconsttypeid int4 NOT NULL,
	"Comment" text NULL,
	x1 float8 NULL,
	y1 float8 NULL,
	z1 float8 NULL,
	x2 float8 NULL,
	y2 float8 NULL,
	z2 float8 NULL,
	CONSTRAINT log_sys_pk_11937 PRIMARY KEY (wellconstructionid),
	CONSTRAINT log_wellconstruction_fk_locationwellconstruction FOREIGN KEY (bhid) REFERENCES rockworks."location"(bhid),
	CONSTRAINT log_wellconstruction_fk_wellconstructiontypewellconstruction FOREIGN KEY (wellconsttypeid) REFERENCES rockworks.wellconstructiontype(wellconsttypeid)
);

CREATE TABLE rockworks.wellpick (
	wellpickid int4 NOT NULL,
	bhid int4 NOT NULL,
	CONSTRAINT log_sys_pk_11970 PRIMARY KEY (wellpickid),
	CONSTRAINT log_wellpick_fk_locationwellpick FOREIGN KEY (bhid) REFERENCES rockworks."location"(bhid)
);
--- Belum
CREATE TABLE survey.daily_report_survey_activity (
	id 				serial4 	 	NOT NULL,
	project_name	varchar(255) 	NOT NULL,
	code_report		varchar(20) 	NOT NULL,
	id_site			varchar(20) 	NOT NULL,
	id_vessel		varchar(20) 	NOT NULL,
	id_user			varchar(20) 	NOT NULL,
	date_survey		timestamp 		NOT NULL,
	comment			varchar(255) 	NOT NULL,
	CONSTRAINT survey_daily_report_survey_activity_pk 			PRIMARY KEY (id),
	CONSTRAINT survey_daily_report_survey_activity_key 			UNIQUE (code_report),
	CONSTRAINT survey_daily_report_survey_activity_fk_vessel 	FOREIGN KEY (id_vessel) REFERENCES operation.vessel(id_vessel),
	CONSTRAINT survey_daily_report_survey_activity_fk_user 		FOREIGN KEY (id_user) REFERENCES operation.user(id_user),
	CONSTRAINT survey_daily_report_survey_activity_fk_site 		FOREIGN KEY (id_site) REFERENCES operation.site(id_site)
);

CREATE TABLE survey.daily_report_survey_activity_details (
	id 				serial4 	 		NOT NULL,
	id_report		varchar(20) 		NOT NULL,
	survey_date		timestamp 			NOT NULL,
	longitude		double precision 	NOT NULL,
	latitude		double precision 	NOT NULL,
	start_time		timestamp 			NOT NULL,
	end_time		timestamp 			NOT NULL,
	description		varchar(255) 		NOT NULL,
	CONSTRAINT survey_daily_report_survey_activity_details_pk 			PRIMARY KEY (id),
	CONSTRAINT survey_daily_report_survey_activity_details_fk_report 	FOREIGN KEY (id_report) REFERENCES survey.daily_report_survey_activity(code_report)
);

CREATE TABLE survey.daily_report_survey_activity_weather (
	id 				serial4		 		NOT NULL,
	id_report		varchar(20) 		NOT NULL,
	survey_date		timestamp 			NOT NULL,
	longitude		double precision 	NOT NULL,
	latitude		double precision 	NOT NULL,
	time			timestamp	 		NOT NULL,
	weather			int4		 		NOT NULL,
	wind_speed		int4 				NOT NULL,
	wave			int4 				NOT NULL,
	CONSTRAINT survey_daily_report_survey_activity_weather_pk 			PRIMARY KEY (id),
	CONSTRAINT survey_daily_report_survey_activity_weather_fk_report 	FOREIGN KEY (id_report) REFERENCES survey.daily_report_survey_activity(code_report)
);

CREATE TABLE survey.daily_report_vibrocore (
	id						serial4		 	NOT NULL,
	project_name			varchar(255) 	NOT NULL,
	code_report				varchar(20) 	NOT NULL,
	id_site					varchar(20) 	NOT NULL,
	id_vessel				varchar(20) 	NOT NULL,
	id_sample				varchar(20) 	NOT NULL,
	day_survey				varchar(20) 	NOT NULL,
	date_survey				timestamp 		NOT NULL,
	rig_type				varchar(20) 	NOT NULL,
	barrel_size				int4 			NOT NULL,
	wellsite				varchar(20) 	NOT NULL,
	total_coreing			int4 			NOT NULL,
	total_depth_coring		int4 			NOT NULL,
	total_depth_logging		int4 			NOT NULL,
	comment					varchar(255) 	NOT NULL,
	CONSTRAINT survey_daily_report_vibrocore_pk			PRIMARY KEY (id),
	CONSTRAINT survey_daily_report_vibrocore_key		UNIQUE (code_report),
	CONSTRAINT survey_daily_report_vibrocore_fk_site	FOREIGN KEY (id_site) REFERENCES operation.site(id_site),
	CONSTRAINT survey_daily_report_vibrocore_fk_vessel	FOREIGN KEY (id_vessel) REFERENCES operation.vessel(id_vessel),
	CONSTRAINT survey_daily_report_vibrocore_fk_sample	FOREIGN KEY (id_sample) REFERENCES operation.sample(id_sample)
);

CREATE TABLE survey.daily_report_vibrocore_detail (
	id				serial4		 		NOT NULL,
	id_report		varchar(20) 		NOT NULL,
	hole_id			varchar(20) 		NOT NULL,
	longitude		double precision 	NOT NULL,
	latitude		double precision 	NOT NULL,
	from_depth		int4 				NOT NULL,
	to_depth		int4 				NOT NULL,
	core_length		int4 				NOT NULL,
	recovery_rate	int4 				NOT NULL,
	description		varchar(255) 		NOT NULL,
	CONSTRAINT survey_daily_report_vibrocore_detail_pk			PRIMARY KEY (id),
	CONSTRAINT survey_daily_report_vibrocore_detail_fk_report	FOREIGN KEY (id_report) REFERENCES survey.daily_report_vibrocore(code_report)
);

--- INDEX
-- Log
CREATE INDEX idx_surveis_search							ON log.surveis 							USING btree (code_survey, doc_no, core_no);
CREATE INDEX idx_sample_log_details_search 				ON log.sample_log_details 				USING btree (doc_no, id_term);
CREATE INDEX idx_sample_logs_search						ON log.sample_logs 						USING btree (doc_no);
CREATE INDEX idx_vibrocore_log_details_search 			ON log.vibrocore_log_details 			USING btree (doc_no);
CREATE INDEX idx_vibrocore_log_search 					ON log.vibrocore_logs 					USING btree (doc_no);
CREATE INDEX idx_vibrocore_logs_site 					ON log.vibrocore_logs 					USING btree (id_site);
CREATE INDEX idx_vibrocore_details_litho 				ON log.vibrocore_log_details 			USING btree (code_lithology);
CREATE INDEX idx_sample_details_litho 					ON log.sample_log_details 				USING btree (id_lithology);
CREATE INDEX idx_vessel_activities_search 				ON operation.vessel_activities 			USING btree (id_vessel, id_order, id_task, seq_activity);
CREATE INDEX idx_vessel_positions_search 				ON operation.vessel_positions 			USING btree (id_vessel, seq_activity);
CREATE INDEX idx_client_deposit_histories_search 		ON operation.client_deposit_histories 	USING btree (id_client);
CREATE INDEX idx_payment_details_search 				ON operation.payment_details 				USING btree (id_payment, doc_no);
CREATE INDEX idx_payment_search 						ON operation.payments 					USING btree (id_client, status);
CREATE INDEX idx_order_search 							ON operation.orders 						USING btree (id_client, status);
CREATE INDEX idx_partner_search 						ON operation.partners 					USING btree (status);
CREATE INDEX idx_clients_region_search 					ON operation.clients 						USING btree (region, status);
CREATE INDEX idx_users_search 							ON operation.users 						USING btree (organs, role);
CREATE INDEX idx_buoy_sensor_histories_search 			ON operation.buoy_sensor_histories 		USING btree (created_at);


-- Audit
CREATE INDEX idx_audit_logs_search 						ON audit.audit_logs 						USING btree (table_name);

-- Rockworks
CREATE INDEX rockworks_aquifertype_gvalue_ix ON rockworks.aquifertype USING btree (gvalue);
CREATE INDEX rockworks_hydrostrattype_gvalue_ix ON rockworks.hydrostrattype USING btree (gvalue);
CREATE INDEX rockworks_itexttype_name_ix ON rockworks.itexttype USING btree (name);
CREATE INDEX rockworks_lithtype_gvalue_ix ON rockworks.lithtype USING btree (gvalue);
CREATE INDEX rockworks_ptexttype_name_ix ON rockworks.ptexttype USING btree (name);
CREATE INDEX rockworks_strattype_gvalue_ix ON rockworks.strattype USING btree (gvalue);
CREATE INDEX rockworks_wellconstructiontype_gvalue_ix ON rockworks.wellconstructiontype USING btree (gvalue);
CREATE INDEX rockworks_aquifer_date_ix ON rockworks.aquifer USING btree (bhid, sampledate, depth1, depth2);
CREATE INDEX rockworks_aquifer_top_ix ON rockworks.aquifer USING btree (bhid, depth1, depth2, sampledate);
CREATE INDEX rockworks_sys_idx_aquifer_fk_aquifertypeaquifer_11980 ON rockworks.aquifer USING btree (aquifertypeid);
CREATE INDEX rockworks_sys_idx_aquifer_fk_locationaquifer_11993 ON rockworks.aquifer USING btree (bhid);
CREATE INDEX rockworks_bitmap_top_ix ON rockworks.bitmap USING btree (bhid, depth1, depth2);
CREATE INDEX rockworks_sys_idx_bitmap_fk_bitmaptypebitmap_12006 ON rockworks.bitmap USING btree (bitmaptypeid);
CREATE INDEX rockworks_sys_idx_bitmap_fk_locationbitmap_12019 ON rockworks.bitmap USING btree (bhid);
CREATE INDEX rockworks_fracture_depth_ix ON rockworks.fracture USING btree (bhid, depth);
CREATE INDEX rockworks_sys_idx_fracture_fk_locationfracture_12032 ON rockworks.fracture USING btree (bhid);
CREATE INDEX rockworks_hydrostratigraphy_top_ix ON rockworks.hydrostratigraphy USING btree (bhid, depth1, depth2);
CREATE INDEX rockworks_sys_idx_hydrostratigraphy_fk_hydrostrattypehydrostratigraph ON rockworks.hydrostratigraphy USING btree (hydrostrattypeid);
CREATE INDEX rockworks_sys_idx_hydrostratigraphy_fk_locationhydrostratigraphy_1205 ON rockworks.hydrostratigraphy USING btree (bhid);
CREATE INDEX rockworks_interval_top_ix ON rockworks."interval" USING btree (bhid, depth1, depth2);
CREATE INDEX rockworks_sys_idx_interval_fk_intervaltypeinterval_12067 ON rockworks."interval" USING btree (intervaltypeid);
CREATE INDEX rockworks_sys_idx_interval_fk_locationinterval_12077 ON rockworks."interval" USING btree (bhid);
CREATE INDEX rockworks_itext_top_ix ON rockworks.itext USING btree (bhid, depth1, depth2);
CREATE INDEX rockworks_sys_idx_itext_fk_itexttypeitext_12087 ON rockworks.itext USING btree (itexttypeid);
CREATE INDEX rockworks_sys_idx_itext_fk_locationitext_12097 ON rockworks.itext USING btree (bhid);
CREATE INDEX rockworks_lithology_top_ix ON rockworks.lithology USING btree (bhid, depth1, depth2);
CREATE INDEX rockworks_sys_idx_lithology_fk_lithtypelithology_12107 ON rockworks.lithology USING btree (lithtypeid);
CREATE INDEX rockworks_sys_idx_lithology_fk_locationlithology_12119 ON rockworks.lithology USING btree (bhid);
CREATE INDEX rockworks_orientation_depth_ix ON rockworks.orientation USING btree (bhid, depth);
CREATE INDEX rockworks_sys_idx_orientation_fk_locationorientation_12131 ON rockworks.orientation USING btree (bhid);
CREATE INDEX rockworks_ouroboros_top_ix ON rockworks.ouroboros USING btree (bhid, depth);
CREATE INDEX rockworks_sys_idx_ouroboros_fk_locationouroboros_12143 ON rockworks.ouroboros USING btree (bhid);
CREATE INDEX rockworks_pattern_top_ix ON rockworks.pattern USING btree (bhid, depth1, depth2);
CREATE INDEX rockworks_sys_idx_pattern_fk_locationpattern_12152 ON rockworks.pattern USING btree (bhid);
CREATE INDEX rockworks_point_top_ix ON rockworks.point USING btree (bhid, depth);
CREATE INDEX rockworks_sys_idx_point_fk_locationpoint_12163 ON rockworks.point USING btree (bhid);
CREATE INDEX rockworks_sys_idx_point_fk_pointtypepoint_12175 ON rockworks.point USING btree (pointtypeid);
CREATE INDEX rockworks_ptext_top_ix ON rockworks.ptext USING btree (bhid, depth);
CREATE INDEX rockworks_sys_idx_ptext_fk_locationptext_12187 ON rockworks.ptext USING btree (bhid);
CREATE INDEX rockworks_sys_idx_ptext_fk_ptexttypeptext_12199 ON rockworks.ptext USING btree (ptexttypeid);
CREATE INDEX rockworks_rockcolor_top_ix ON rockworks.rockcolor USING btree (bhid, depth1, depth2);
CREATE INDEX rockworks_sys_idx_rockcolor_fk_locationrockcolor_12211 ON rockworks.rockcolor USING btree (bhid);
CREATE INDEX rockworks_stratigraphy_top_ix ON rockworks.stratigraphy USING btree (bhid, depth1, depth2);
CREATE INDEX rockworks_sys_idx_stratigraphy_fk_locationstratigraphy_12223 ON rockworks.stratigraphy USING btree (bhid);
CREATE INDEX rockworks_sys_idx_stratigraphy_fk_strattypestratigraphy_12233 ON rockworks.stratigraphy USING btree (strattypeid);
CREATE INDEX rockworks_symbol_depth_ix ON rockworks.symbol USING btree (bhid, depth);
CREATE INDEX rockworks_sys_idx_symbol_fk_locationsymbol_12243 ON rockworks.symbol USING btree (bhid);
CREATE INDEX rockworks_sys_idx_t3dpointmaprange_fk_projecttablest3dpointmaprange_1 ON rockworks.t3dpointmaprange USING btree (projecttablesid);
CREATE INDEX rockworks_t3dpointmaprange_minimummaximum_ix ON rockworks.t3dpointmaprange USING btree (projecttablesid, minimum, maximum);
CREATE INDEX rockworks_sys_idx_tbargraphscale_fk_projecttablestbargraphscale_12263 ON rockworks.tbargraphscale USING btree (projecttablesid);
CREATE INDEX rockworks_tbargraphscale_minvalue_ix ON rockworks.tbargraphscale USING btree (projecttablesid, minvalue);
CREATE INDEX rockworks_sys_idx_tcolorindex_fk_projecttablestcolorindex_12273 ON rockworks.tcolorindex USING btree (projecttablesid);
CREATE INDEX rockworks_tcolorindex_caption_ix ON rockworks.tcolorindex USING btree (projecttablesid, caption);
CREATE INDEX rockworks_sys_idx_tcontour_fk_projecttablestcontour_12283 ON rockworks.tcontour USING btree (projecttablesid);
CREATE INDEX rockworks_tcontour_level_ix ON rockworks.tcontour USING btree (projecttablesid, level);
CREATE INDEX rockworks_sys_idx_tdwgriddingsector_fk_projecttablestdwgriddingsector ON rockworks.tdwgriddingsector USING btree (projecttablesid);
CREATE INDEX rockworks_tdwgriddingsector_minanglemaxangle_idx ON rockworks.tdwgriddingsector USING btree (projecttablesid, minangle, maxangle);
CREATE INDEX rockworks_sys_idx_tfaults_fk_projecttablestfaults_12303 ON rockworks.tfaults USING btree (projecttablesid);
CREATE INDEX rockworks_tfaults_pair_ix ON rockworks.tfaults USING btree (projecttablesid, sortorder);
CREATE INDEX rockworks_sys_idx_tidwsolidmodelingsec_fk_projecttablestidwsolidmodel ON rockworks.tidwsolidmodelingsec USING btree (projecttablesid);
CREATE INDEX rockworks_tidwsolidmodelingsec_mininclinationmaxinclinationminazimuth ON rockworks.tidwsolidmodelingsec USING btree (projecttablesid, mininclination, maxinclination, minazimuth);
CREATE INDEX rockworks_sys_idx_tlinestyleindex_fk_projecttablestlinestyleindex_123 ON rockworks.tlinestyleindex USING btree (projecttablesid);
CREATE INDEX rockworks_tlinestyleindex_caption_ix ON rockworks.tlinestyleindex USING btree (projecttablesid, caption);
CREATE INDEX rockworks_sys_idx_tminmaxcolor_fk_projecttablestminmaxcolor_12333 ON rockworks.tminmaxcolor USING btree (projecttablesid);
CREATE INDEX rockworks_tminmaxcolor_minvalue_ix ON rockworks.tminmaxcolor USING btree (projecttablesid, minvalue);
CREATE INDEX rockworks_sys_idx_tminterval_fk_locationtminterval_12343 ON rockworks.tminterval USING btree (bhid);
CREATE INDEX rockworks_sys_idx_tminterval_fk_tmintervaltypetminterval_12353 ON rockworks.tminterval USING btree (tmintervaltypeid);
CREATE INDEX rockworks_tminterval_top_ix ON rockworks.tminterval USING btree (bhid, depth1, depth2, sampledate);
CREATE INDEX rockworks_sys_idx_tpatternindex_fk_projecttablestpatternindex_12363 ON rockworks.tpatternindex USING btree (projecttablesid);
CREATE INDEX rockworks_tpatternindex_caption_ix ON rockworks.tpatternindex USING btree (projecttablesid, caption);CREATE INDEX rockworks_sys_idx_tpointmaprange_fk_projecttablestpointmaprange_12373 ON rockworks.tpointmaprange USING btree (projecttablesid);
CREATE INDEX rockworks_tpointmaprange_minimummaximum_ix ON rockworks.tpointmaprange USING btree (projecttablesid, minimum, maximum);
CREATE INDEX rockworks_sys_idx_tpolygon_fk_projecttablestpolygon_12383 ON rockworks.tpolygon USING btree (projecttablesid);
CREATE INDEX rockworks_tpolygon_vertex_ix ON rockworks.tpolygon USING btree (projecttablesid, sortorder);
CREATE INDEX rockworks_sys_idx_tpolygons_fk_projecttablestpolygons_12393 ON rockworks.tpolygons USING btree (projecttablesid);
CREATE INDEX rockworks_sys_idx_tprofile_fk_projecttablestprofile_12403 ON rockworks.tprofile USING btree (projecttablesid);
CREATE INDEX rockworks_sys_idx_tsymbolindex_fk_projecttablestsymbolindex_12413 ON rockworks.tsymbolindex USING btree (projecttablesid);
CREATE INDEX rockworks_sys_idx_tsynonym_fk_projecttablestsynonym_12423 ON rockworks.tsynonym USING btree (projecttablesid);
CREATE INDEX rockworks_tsynonym_target_ix ON rockworks.tsynonym USING btree (projecttablesid, target);
CREATE INDEX rockworks_sys_idx_txycoordinate_fk_projecttablestxycoordinate_12433 ON rockworks.txycoordinate USING btree (projecttablesid);
CREATE INDEX rockworks_txycoordinate_coordinate_ix ON rockworks.txycoordinate USING btree (projecttablesid, sortorder);
CREATE INDEX rockworks_sys_idx_txypair_fk_projecttablestxypair_12443 ON rockworks.txypair USING btree (projecttablesid);
CREATE INDEX rockworks_txypair_pair_ix ON rockworks.txypair USING btree (projecttablesid, sortorder);
CREATE INDEX rockworks_sys_idx_txyz_fk_projecttablestxyz_12453 ON rockworks.txyz USING btree (projecttablesid);
CREATE INDEX rockworks_txyz_index_ix ON rockworks.txyz USING btree (projecttablesid, sortorder);
CREATE INDEX rockworks_sys_idx_vector_fk_locationvector_12463 ON rockworks.vector USING btree (bhid);
CREATE INDEX rockworks_vector_depth_ix ON rockworks.vector USING btree (bhid, depth);
CREATE INDEX rockworks_sys_idx_wellconstruction_fk_locationwellconstruction_12477 ON rockworks.wellconstruction USING btree (bhid);
CREATE INDEX rockworks_sys_idx_wellconstruction_fk_wellconstructiontypewellconstru ON rockworks.wellconstruction USING btree (wellconsttypeid);
CREATE INDEX rockworks_wellconstruction_depth_ix ON rockworks.wellconstruction USING btree (bhid, depth1, depth2);
CREATE INDEX rockworks_sys_idx_wellpick_fk_locationwellpick_12505 ON rockworks.wellpick USING btree (bhid);

CREATE UNIQUE INDEX rockworks_sys_idx_strattype_name_ix_11721 ON rockworks.strattype USING btree (name);
CREATE UNIQUE INDEX rockworks_sys_idx_tmintervaltype_name_ix_11824 ON rockworks.tmintervaltype USING btree (name);
CREATE UNIQUE INDEX rockworks_sys_idx_wellconstructiontype_name_ix_11949 ON rockworks.wellconstructiontype USING btree (name);
CREATE UNIQUE INDEX rockworks_sys_idx_wellpick_bhid_ix_11964 ON rockworks.wellpick USING btree (bhid);
CREATE UNIQUE INDEX rockworks_sys_idx_tpolygons_caption_ix_11862 ON rockworks.tpolygons USING btree (projecttablesid, caption);
CREATE UNIQUE INDEX rockworks_sys_idx_lithtype_name_ix_11532 ON rockworks.lithtype USING btree (name);
CREATE UNIQUE INDEX rockworks_sys_idx_location_name_ix_11547 ON rockworks.location USING btree (name);
CREATE UNIQUE INDEX rockworks_sys_idx_lookuplists_lookuplist_ix_11572 ON rockworks.lookuplists USING btree (tablename, fieldname, listvalue);
CREATE UNIQUE INDEX rockworks_sys_idx_pointtype_name_ix_11625 ON rockworks.pointtype USING btree (name);
CREATE UNIQUE INDEX rockworks_sys_idx_projectinfo_info_ix_11645 ON rockworks.projectinfo USING btree (category, item);
CREATE UNIQUE INDEX rockworks_sys_idx_projecttables_typename_ix_11671 ON rockworks.projecttables USING btree (tabletype, tablename);
CREATE UNIQUE INDEX rockworks_sys_idx_hydrostrattype_name_ix_11471 ON rockworks.hydrostrattype USING btree (name);
CREATE UNIQUE INDEX rockworks_sys_idx_intervaltype_name_ix_11494 ON rockworks.intervaltype USING btree (name);
CREATE UNIQUE INDEX rockworks_sys_idx_aquifertype_name_ix_11406 ON rockworks.aquifertype USING btree (name);

-- Survey
CREATE INDEX idx_daily_report_survey_activity_search 			ON survey.daily_report_survey_activity 				USING btree (code_report);
CREATE INDEX idx_daily_report_survey_activity_site 				ON survey.daily_report_survey_activity 				USING btree (id_site);
CREATE INDEX idx_daily_report_survey_activity_vessel 			ON survey.daily_report_survey_activity 				USING btree (id_vessel);
CREATE INDEX idx_daily_report_survey_activity_user 				ON survey.daily_report_survey_activity 				USING btree (id_user);

CREATE INDEX idx_daily_report_survey_activity_details_search 	ON survey.daily_report_survey_activity_details 		USING btree (id_report);

CREATE INDEX idx_daily_report_survey_activity_weather_search 	ON survey.daily_report_survey_activity_weather 		USING btree (id_report);

CREATE INDEX idx_daily_report_vibrocore_search 					ON survey.daily_report_vibrocore 					USING btree (code_report);
CREATE INDEX idx_daily_report_vibrocore_site 					ON survey.daily_report_vibrocore 					USING btree (id_site);
CREATE INDEX idx_daily_report_vibrocore_vessel 					ON survey.daily_report_vibrocore 					USING btree (id_vessel);

CREATE INDEX idx_daily_report_vibrocore_detail_search 			ON survey.daily_report_vibrocore_detail 			USING btree (id_report); 

-- Optimization Indexes for Foreign Keys (Fast Joins)
CREATE INDEX idx_buoys_site 					ON operation.buoys (id_site);
CREATE INDEX idx_clients_contact 				ON operation.clients (id_contact);
CREATE INDEX idx_partners_contact 				ON operation.partners (id_contact);
CREATE INDEX idx_vessels_partner 				ON operation.vessels (id_partner);
CREATE INDEX idx_order_details_order 			ON operation.order_details (id_order);
CREATE INDEX idx_order_details_vessel 			ON operation.order_details (id_vessel);
CREATE INDEX idx_vessel_crews_vessel 			ON operation.vessel_crews (id_vessel);
CREATE INDEX idx_vessel_crews_user 				ON operation.vessel_crews (id_user);

-- Auto-generation Sequences
CREATE SEQUENCE operation.seq_contact_code;
CREATE SEQUENCE operation.seq_methodpay_code;
CREATE SEQUENCE operation.seq_site_code;
CREATE SEQUENCE operation.seq_buoy_code;
CREATE SEQUENCE operation.seq_user_code;
CREATE SEQUENCE operation.seq_client_code;
CREATE SEQUENCE operation.seq_partner_code;
CREATE SEQUENCE operation.seq_order_code;
CREATE SEQUENCE operation.seq_payment_code;
CREATE SEQUENCE operation.seq_vessel_code;
CREATE SEQUENCE operation.seq_task_code;
CREATE SEQUENCE log.seq_term_code;
CREATE SEQUENCE log.seq_lithology_code;
CREATE SEQUENCE log.seq_survey_code;

-- Auto-generation Function
CREATE OR REPLACE FUNCTION operation.generate_code_auto()
RETURNS TRIGGER AS $$
DECLARE
    next_val BIGINT;
    code_len INT;
    prefix TEXT;
    seq_name TEXT;
BEGIN
    -- 1. Identify Prefix & Sequence
    IF TG_TABLE_NAME = 'contacts' THEN prefix := 'CT'; seq_name := 'operation.seq_contact_code';
    ELSIF TG_TABLE_NAME = 'method_payments' THEN prefix := 'MP'; seq_name := 'operation.seq_methodpay_code';
    ELSIF TG_TABLE_NAME = 'sites' THEN prefix := 'ST'; seq_name := 'operation.seq_site_code';
    ELSIF TG_TABLE_NAME = 'buoys' THEN prefix := 'BY'; seq_name := 'operation.seq_buoy_code';
    ELSIF TG_TABLE_NAME = 'users' THEN prefix := 'USR'; seq_name := 'operation.seq_user_code';
    ELSIF TG_TABLE_NAME = 'clients' THEN prefix := 'CL'; seq_name := 'operation.seq_client_code';
    ELSIF TG_TABLE_NAME = 'partners' THEN prefix := 'PT'; seq_name := 'operation.seq_partner_code';
    ELSIF TG_TABLE_NAME = 'orders' THEN prefix := 'ORD'; seq_name := 'operation.seq_order_code';
    ELSIF TG_TABLE_NAME = 'payments' THEN prefix := 'PAY'; seq_name := 'operation.seq_payment_code';
    ELSIF TG_TABLE_NAME = 'vessels' THEN prefix := 'VSL'; seq_name := 'operation.seq_vessel_code';
    ELSIF TG_TABLE_NAME = 'order_details' THEN prefix := 'TSK'; seq_name := 'operation.seq_task_code';
    ELSIF TG_TABLE_NAME = 'term_desc' THEN prefix := 'TRM'; seq_name := 'log.seq_term_code';
    ELSIF TG_TABLE_NAME = 'soil_desc' THEN prefix := 'SL'; seq_name := 'log.seq_lithology_code';
    ELSIF TG_TABLE_NAME = 'surveis' THEN prefix := 'SRV'; seq_name := 'log.seq_survey_code';
    END IF;

    -- 2. fetch next value
    EXECUTE format('SELECT nextval(''%s'')', seq_name) INTO next_val;

    -- 3. Calculate dynamic padding (at least 3 digits, grow if larger)
    -- If next_val is 5 -> '005'
    -- If next_val is 1000 -> '1000' (no overflow crash)
    code_len := GREATEST(3, length(next_val::text));

    -- 4. Assign to the correct column
    IF TG_TABLE_NAME = 'contacts' THEN NEW.code_contact := prefix || LPAD(next_val::text, code_len, '0');
    ELSIF TG_TABLE_NAME = 'method_payments' THEN NEW.code_methodpay := prefix || LPAD(next_val::text, code_len, '0');
    ELSIF TG_TABLE_NAME = 'sites' THEN NEW.code_site := prefix || LPAD(next_val::text, code_len, '0');
    ELSIF TG_TABLE_NAME = 'buoys' THEN NEW.code_buoy := prefix || LPAD(next_val::text, code_len, '0');
    ELSIF TG_TABLE_NAME = 'users' THEN NEW.code_user := prefix || LPAD(next_val::text, code_len, '0');
    ELSIF TG_TABLE_NAME = 'clients' THEN NEW.code_client := prefix || LPAD(next_val::text, code_len, '0');
    ELSIF TG_TABLE_NAME = 'partners' THEN NEW.code_partner := prefix || LPAD(next_val::text, code_len, '0');
    ELSIF TG_TABLE_NAME = 'orders' THEN NEW.code_order := prefix || LPAD(next_val::text, code_len, '0');
    ELSIF TG_TABLE_NAME = 'payments' THEN NEW.code_payment := prefix || LPAD(next_val::text, code_len, '0');
    ELSIF TG_TABLE_NAME = 'vessels' THEN NEW.code_vessel := prefix || LPAD(next_val::text, code_len, '0');
    ELSIF TG_TABLE_NAME = 'order_details' THEN NEW.code_task := prefix || LPAD(next_val::text, code_len, '0');
    ELSIF TG_TABLE_NAME = 'term_desc' THEN NEW.code_term := prefix || LPAD(next_val::text, code_len, '0');
    ELSIF TG_TABLE_NAME = 'soil_desc' THEN NEW.code_lithology := prefix || LPAD(next_val::text, code_len, '0');
    ELSIF TG_TABLE_NAME = 'surveis' THEN NEW.code_survey := prefix || LPAD(next_val::text, code_len, '0');
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Triggers (Execute BEFORE INSERT)
CREATE TRIGGER trg_generate_code_contacts BEFORE INSERT ON operation.contacts FOR EACH ROW WHEN (NEW.code_contact IS NULL) EXECUTE FUNCTION operation.generate_code_auto();
CREATE TRIGGER trg_generate_code_methodpay BEFORE INSERT ON operation.method_payments FOR EACH ROW WHEN (NEW.code_methodpay IS NULL) EXECUTE FUNCTION operation.generate_code_auto();
CREATE TRIGGER trg_generate_code_sites BEFORE INSERT ON operation.sites FOR EACH ROW WHEN (NEW.code_site IS NULL) EXECUTE FUNCTION operation.generate_code_auto();
CREATE TRIGGER trg_generate_code_buoys BEFORE INSERT ON operation.buoys FOR EACH ROW WHEN (NEW.code_buoy IS NULL) EXECUTE FUNCTION operation.generate_code_auto();
CREATE TRIGGER trg_generate_code_users BEFORE INSERT ON operation.users FOR EACH ROW WHEN (NEW.code_user IS NULL) EXECUTE FUNCTION operation.generate_code_auto();
CREATE TRIGGER trg_generate_code_clients BEFORE INSERT ON operation.clients FOR EACH ROW WHEN (NEW.code_client IS NULL) EXECUTE FUNCTION operation.generate_code_auto();
CREATE TRIGGER trg_generate_code_partners BEFORE INSERT ON operation.partners FOR EACH ROW WHEN (NEW.code_partner IS NULL) EXECUTE FUNCTION operation.generate_code_auto();
CREATE TRIGGER trg_generate_code_orders BEFORE INSERT ON operation.orders FOR EACH ROW WHEN (NEW.code_order IS NULL) EXECUTE FUNCTION operation.generate_code_auto();
CREATE TRIGGER trg_generate_code_payments BEFORE INSERT ON operation.payments FOR EACH ROW WHEN (NEW.code_payment IS NULL) EXECUTE FUNCTION operation.generate_code_auto();
CREATE TRIGGER trg_generate_code_vessels BEFORE INSERT ON operation.vessels FOR EACH ROW WHEN (NEW.code_vessel IS NULL) EXECUTE FUNCTION operation.generate_code_auto();
CREATE TRIGGER trg_generate_code_order_details BEFORE INSERT ON operation.order_details FOR EACH ROW WHEN (NEW.code_task IS NULL) EXECUTE FUNCTION operation.generate_code_auto();
CREATE TRIGGER trg_generate_code_term BEFORE INSERT ON log.term_desc FOR EACH ROW WHEN (NEW.code_term IS NULL) EXECUTE FUNCTION operation.generate_code_auto();
CREATE TRIGGER trg_generate_code_soil BEFORE INSERT ON log.soil_desc FOR EACH ROW WHEN (NEW.code_lithology IS NULL) EXECUTE FUNCTION operation.generate_code_auto();
CREATE TRIGGER trg_generate_code_survey BEFORE INSERT ON log.surveis FOR EACH ROW WHEN (NEW.code_survey IS NULL) EXECUTE FUNCTION operation.generate_code_auto();