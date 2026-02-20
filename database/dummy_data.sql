-- Dummy Data for Marine-Web Dashboard
-- Comprehensive & Realistic | Rockworks EXCLUDED
-- =============================================

-- =============================================
-- 1. OPERATION SCHEMA
-- =============================================

-- Contacts (30 records)
INSERT INTO operation.contacts (code_contact, phone, email, mobile, fax, created_at) VALUES
('CT001','0215551234','admin.ops@marineweb.com','081211112222','0215551235',NOW()-INTERVAL'12 months'),
('CT002','0215555678','budi.santoso@surveyor.id','081333334444',NULL,NOW()-INTERVAL'11 months'),
('CT003','0215559012','capt.ahmad@vessel.net','081155556666',NULL,NOW()-INTERVAL'11 months'),
('CT004','0318881234','siti.aminah@mgmt.com','081277778888','0318881235',NOW()-INTERVAL'10 months'),
('CT005','0411444555','agus.kurniawan@crew.com','085299990000',NULL,NOW()-INTERVAL'10 months'),
('CT006','0217890123','procurement@wika.co.id','081123456789','0217890124',NOW()-INTERVAL'9 months'),
('CT007','0614567890','projects@pelindo.co.id','081234567890','0614567891',NOW()-INTERVAL'9 months'),
('CT008','0411123456','dinas.pu@sulselprov.go.id','081345678901','0411123457',NOW()-INTERVAL'8 months'),
('CT009','0219998888','ops@logisticsindo.com','081188889999','0219998889',NOW()-INTERVAL'8 months'),
('CT010','0317776666','sales@heavyequip.com','081266667777',NULL,NOW()-INTERVAL'7 months'),
('CT011','0215001111','hse.officer@site.com','081200001111',NULL,NOW()-INTERVAL'7 months'),
('CT012','0213222333','chief.eng@vessel.net','081322223333',NULL,NOW()-INTERVAL'6 months'),
('CT013','0211444555','geo.specialist@survey.com','081144445555',NULL,NOW()-INTERVAL'6 months'),
('CT014','0861123456','finance@client.com','086112345678',NULL,NOW()-INTERVAL'5 months'),
('CT015','0888999000','port.master@harbor.com','088899990000',NULL,NOW()-INTERVAL'5 months'),
('CT016','0243546789','logistics.smg@supply.com','081234560001','0243546790',NOW()-INTERVAL'4 months'),
('CT017','0542765432','ops.bpp@marine.id','081345670002',NULL,NOW()-INTERVAL'4 months'),
('CT018','0361987654','bali.project@resort.com','081156780003',NULL,NOW()-INTERVAL'3 months'),
('CT019','0778456123','batam.shipyard@repair.com','081267890004','0778456124',NOW()-INTERVAL'3 months'),
('CT020','0911321654','papua.infra@gov.id','081378900005',NULL,NOW()-INTERVAL'2 months'),
('CT021','0215771234','rina.kusuma@marine.id','081211113333',NULL,NOW()-INTERVAL'14 months'),
('CT022','0316882345','hartono.s@port.co.id','081322224444',NULL,NOW()-INTERVAL'13 months'),
('CT023','0412993456','capt.benny@fleet.com','081433335555',NULL,NOW()-INTERVAL'12 months'),
('CT024','0219104567','sri.wahyuni@office.com','081544446666',NULL,NOW()-INTERVAL'11 months'),
('CT025','0317215678','dimas.prayoga@eng.com','081655557777',NULL,NOW()-INTERVAL'10 months'),
('CT026','0543326789','fernanda.rio@ops.com','081766668888',NULL,NOW()-INTERVAL'9 months'),
('CT027','0778437890','amir.harun@survey.id','081877779999',NULL,NOW()-INTERVAL'8 months'),
('CT028','0214548901','lestari.dewi@mgmt.com','081988880000',NULL,NOW()-INTERVAL'7 months'),
('CT029','0411659012','saiful.bahri@crew.net','082099991111',NULL,NOW()-INTERVAL'6 months'),
('CT030','0215760123','yanti.puspita@admin.com','082111112222',NULL,NOW()-INTERVAL'5 months');

-- Method Payments
INSERT INTO operation.method_payments (code_methodpay, transaction_name, bank_name) VALUES
('MP001','Bank Transfer IDR','Bank Mandiri 1230011223345'),
('MP002','Bank Transfer USD','BCA 8880123456'),
('MP003','Petty Cash','Finance Dept'),
('MP004','Corporate Cheque','Bank BRI'),
('MP005','Letter of Credit','BNI 46');

-- Parameters
INSERT INTO operation.parameters (parent_desc, kode_desc, description) VALUES
('SYSTEM','CURRIDR','Indonesian Rupiah'),
('SYSTEM','TZWIB','Western Indonesia Time UTC7'),
('SYSTEM','TZWITA','Central Indonesia Time UTC8'),
('OPERATION','MAXSPEED','12 Knots'),
('OPERATION','DREDGEDEPTH','max minus 20m LWS'),
('OPERATION','FUELTYPE','MFO 380'),
('VESSEL','MAXCREW','25 persons'),
('FINANCIAL','TAXRATE','11 percent PPN');

-- Sites (12 records)
INSERT INTO operation.sites (code_site, type, location, city, state, zip, country, port, latitude, longitude, status) VALUES
('ST001','Dredging','Pengerukan Alur Pelayaran Priok','Jakarta Utara','DKI Jakarta','14310','Indonesia','Tanjung Priok',-6.1025,106.8805,'Active'),
('ST002','Reclamation','Teluk Lamong Expansion Phase 2','Surabaya','Jawa Timur','60191','Indonesia','Tanjung Perak',-7.2105,112.7250,'Active'),
('ST003','Survey','Studi Bathymetri Muara Baru','Semarang','Jawa Tengah','50174','Indonesia','Tanjung Emas',-6.9450,110.4250,'Inactive'),
('ST004','Dredging','Maintenance Belawan Channel','Medan','Sumatera Utara','20411','Indonesia','Belawan',3.7850,98.6900,'Active'),
('ST005','Reclamation','Makassar New Port Phase 2','Makassar','Sulawesi Selatan','90163','Indonesia','Soekarno-Hatta',-5.1150,119.4100,'Active'),
('ST006','Reclamation','Benoa Tourism Waterfront','Denpasar','Bali','80111','Indonesia','Benoa',-8.7450,115.2150,'Active'),
('ST007','Dredging','Mahakam River Maintenance','Samarinda','Kalimantan Timur','75111','Indonesia','Samarinda',-0.5350,117.1350,'Active'),
('ST008','Survey','Natuna Gas Pipeline Route','Ranai','Kepulauan Riau','29711','Indonesia','Selat Lampa',3.9450,108.3850,'Active'),
('ST009','Dredging','Pontianak Port Access Channel','Pontianak','Kalimantan Barat','78111','Indonesia','Dwikora',-0.0260,109.3425,'Active'),
('ST010','Reclamation','New Ambon Waterfront','Ambon','Maluku','97126','Indonesia','Yos Sudarso',-3.6950,128.1810,'Active'),
('ST011','Survey','Bitung Deep Sea Port Survey','Bitung','Sulawesi Utara','95525','Indonesia','Bitung',1.4420,125.2050,'Active'),
('ST012','Dredging','Cilacap Fuel Jetty Dredging','Cilacap','Jawa Tengah','53211','Indonesia','Tanjung Intan',-7.7250,109.0150,'Active');

-- Users (20 records)
INSERT INTO operation.users (id_contact, code_user, name, citizen, role, status, organs) VALUES
('CT001','USR001','SysAdmin','Indonesia','Admin','Active','Internal'),
('CT002','USR002','Budi Santoso','Indonesia','Surveyor','Active','Field'),
('CT003','USR003','Capt Ahmad Fauzi','Indonesia','Captain','Active','Vessel'),
('CT004','USR004','Dewi Sartika','Singapore','Manager','Active','Office'),
('CT005','USR005','Agus Kurniawan','Indonesia','Crew','Inactive','Vessel'),
('CT011','USR006','Rudi Hartono','Indonesia','HSE','Active','Field'),
('CT012','USR007','John Doe','Philippines','Crew','Active','Vessel'),
('CT013','USR008','Eko Prasetyo','Indonesia','Surveyor','Active','Field'),
('CT014','USR009','Sari Indah','Indonesia','Finance','Active','Office'),
('CT015','USR010','Capt Michael Wong','Malaysia','Captain','Active','Vessel'),
('CT016','USR011','Dedi Supriadi','Indonesia','Logistics','Active','Office'),
('CT017','USR012','Bambang Pamungkas','Indonesia','Crew','Active','Vessel'),
('CT018','USR013','Made Wijaya','Indonesia','HSE','Active','Field'),
('CT019','USR014','Robert Smith','Australia','Manager','Active','Office'),
('CT020','USR015','Yusuf Mansur','Indonesia','Surveyor','Active','Field'),
('CT021','USR016','Rina Kusuma','Indonesia','Surveyor','Active','Field'),
('CT022','USR017','Hartono Setiawan','Indonesia','Operations','Active','Office'),
('CT023','USR018','Capt Benny Irawan','Indonesia','Captain','Active','Vessel'),
('CT024','USR019','Sri Wahyuni','Indonesia','Finance','Active','Office'),
('CT025','USR020','Dimas Prayoga','Indonesia','Crew','Active','Vessel');

-- User Managements (login accounts for all Active users)
INSERT INTO operation.user_managements (id_user, password, status, last_login) VALUES
('USR001','admin123','Active',NOW()-INTERVAL'1 hour'),
('USR002','survey2024','Active',NOW()-INTERVAL'3 hours'),
('USR003','captain01','Active',NOW()-INTERVAL'6 hours'),
('USR004','manager99','Active',NOW()-INTERVAL'2 hours'),
('USR006','hse2024','Active',NOW()-INTERVAL'1 day'),
('USR007','crew007','Active',NOW()-INTERVAL'12 hours'),
('USR008','surv2024','Active',NOW()-INTERVAL'4 hours'),
('USR009','finance09','Active',NOW()-INTERVAL'2 hours'),
('USR010','captain10','Active',NOW()-INTERVAL'8 hours'),
('USR011','logis2024','Active',NOW()-INTERVAL'1 day'),
('USR012','crew012','Active',NOW()-INTERVAL'5 hours'),
('USR013','hse013','Active',NOW()-INTERVAL'2 days'),
('USR014','mgr014','Active',NOW()-INTERVAL'3 hours'),
('USR015','surv015','Active',NOW()-INTERVAL'6 hours'),
('USR016','surv016','Active',NOW()-INTERVAL'1 day'),
('USR017','ops017','Active',NOW()-INTERVAL'4 hours'),
('USR018','capt018','Active',NOW()-INTERVAL'7 hours'),
('USR019','fin019','Active',NOW()-INTERVAL'2 hours'),
('USR020','crew020','Active',NOW()-INTERVAL'1 day');

-- Clients (10 records)
INSERT INTO operation.clients (code_client, name, industry, region, deposit, id_contact, status) VALUES
('CL001','PT Wika Konstruksi','Construction','Java',50000000.00,'CT006','Active'),
('CL002','PT Pelindo III','Port Operator','National',150000000.00,'CT007','Active'),
('CL003','Dinas PU Sulsel','Government','Sulawesi',200000000.00,'CT008','Active'),
('CL004','Pertamina Hulu','Oil Gas','Kalimantan',300000000.00,'CT017','Active'),
('CL005','Bali Resort Dev','Hospitality','Bali',75000000.00,'CT018','Active'),
('CL006','PT Adhi Karya','Construction','Java',80000000.00,'CT021','Active'),
('CL007','KSOP Bitung','Government','Sulawesi',120000000.00,'CT022','Active'),
('CL008','Medco Energi','Oil Gas','Kalimantan',250000000.00,'CT026','Active'),
('CL009','PT Pembangunan Riau','Construction','Sumatra',60000000.00,'CT027','Inactive'),
('CL010','Pemda Ambon','Government','Maluku',90000000.00,'CT028','Active');

-- Partners (6 records)
INSERT INTO operation.partners (id_contact, code_partner, name, industry, status) VALUES
('CT009','PT001','PT Samudera Logistics','Logistics','Active'),
('CT010','PT002','PT Traktor Nusantara','Supply','Active'),
('CT016','PT003','Java Marine Services','Marine','Active'),
('CT019','PT004','Batam Shipyard Ops','Repair','Active'),
('CT029','PT005','Sulawesi Marine Works','Marine','Active'),
('CT030','PT006','Papua Infra Support','Logistics','Active');

-- Vessels (14 records)
INSERT INTO operation.vessels (id_partner, code_vessel, flag, name, status) VALUES
('PT001','VSL001','Indonesia','MV Baruna Jaya I','Active'),
('PT001','VSL002','Singapore','SV Geo Explorer','Active'),
('PT002','VSL003','Panama','TB Ocean Horse','Maintenance'),
('PT001','VSL004','Malaysia','BG Coal Carrier 300','Active'),
('PT002','VSL005','Indonesia','TB Harbour Tug 05','Active'),
('PT003','VSL006','Indonesia','Dredger King I','Active'),
('PT003','VSL007','Indonesia','Dredger Queen II','Active'),
('PT004','VSL008','Vietnam','SV Deep Sea','Inactive'),
('PT001','VSL009','Indonesia','BG Sand Master','Active'),
('PT002','VSL010','Indonesia','TB Power Pull','Active'),
('PT005','VSL011','Indonesia','MV Sulawesi Express','Active'),
('PT005','VSL012','Indonesia','BG Flat Top 400','Active'),
('PT006','VSL013','Indonesia','TB Timur Jaya','Active'),
('PT001','VSL014','Singapore','SV Marine Scout','Active');

-- Vessel Details (14 records)
INSERT INTO operation.vessel_details (id_vessel, gross_tonnage, net_tonnage, deadweight_tonnage, length_overall, beam, draft, depth_details, special_features) VALUES
('VSL001',1200,360,1500,60,12,4,6,'Multipurpose Research Vessel'),
('VSL002',850,255,900,52,11,3,5,'High Res Multibeam Echosounder'),
('VSL003',450,135,500,32,9,3,4,'Bollard Pull 40T'),
('VSL004',3500,1050,5000,91,24,5,6,'Flat Top Barge 300ft'),
('VSL005',250,75,300,28,8,3,4,'Azimuth Stern Drive'),
('VSL006',5000,1500,7000,100,25,6,8,'Trailing Suction Hopper Dredger'),
('VSL007',4500,1350,6500,95,24,6,8,'Cutter Suction Dredger'),
('VSL008',1000,300,1200,55,12,4,5,'ROV Support Vessel'),
('VSL009',4000,1200,5500,92,24,5,6,'Side Dump Barge'),
('VSL010',300,90,400,30,9,3,4,'Towing Winch 50T'),
('VSL011',2200,660,3000,75,16,5,7,'RoRo Ferry Converted'),
('VSL012',5500,1650,7500,110,28,6,9,'Flat Top Barge 400ft'),
('VSL013',280,84,350,26,8,3,4,'Harbour Tug 35T BP'),
('VSL014',900,270,1100,55,12,4,6,'Sub-bottom Profiler Survey');

-- Orders (25 records across 2024-2025)
INSERT INTO operation.orders (id_client, code_order, order_date, required_delivery_date, priority, quantity, special_requirements, scheduled_delivery_date, actual_delivery_date, destination, destination_longitude, destination_latitude, status) VALUES
('CL001','ORD001',NOW()-INTERVAL'180 days',NOW()-INTERVAL'150 days','High',15000,'Capital Dredging 14m LWS',NOW()-INTERVAL'150 days',NOW()-INTERVAL'148 days','Tanjung Priok',106.88,-6.10,'Completed'),
('CL002','ORD002',NOW()-INTERVAL'30 days',NOW()+INTERVAL'10 days','Medium',50000,'Sand Fill Construction',NOW()+INTERVAL'10 days',NOW()+INTERVAL'15 days','Tanjung Perak',112.73,-7.21,'On Progress'),
('CL001','ORD003',NOW()-INTERVAL'2 days',NOW()+INTERVAL'30 days','Low',2000,'Dumping Area Survey',NOW()+INTERVAL'30 days',NOW()+INTERVAL'35 days','Semarang',110.42,-6.95,'Open'),
('CL003','ORD004',NOW()-INTERVAL'60 days',NOW()-INTERVAL'10 days','High',120000,'Reclamation Material Fill',NOW()-INTERVAL'10 days',NOW()-INTERVAL'5 days','Makassar',119.41,-5.12,'Completed'),
('CL002','ORD005',NOW(),NOW()+INTERVAL'45 days','Medium',500,'Soil Investigation SI',NOW()+INTERVAL'45 days',NOW()+INTERVAL'50 days','Belawan',98.69,3.79,'Open'),
('CL005','ORD006',NOW()-INTERVAL'15 days',NOW()+INTERVAL'20 days','High',5000,'Breakwater Rock Supply',NOW()+INTERVAL'20 days',NOW()+INTERVAL'25 days','Benoa',115.22,-8.75,'On Progress'),
('CL004','ORD007',NOW()-INTERVAL'5 days',NOW()+INTERVAL'14 days','Medium',0,'Pre Dredge Survey',NOW()+INTERVAL'15 days',NOW()+INTERVAL'18 days','Samarinda',117.14,-0.54,'Open'),
('CL001','ORD008',NOW()-INTERVAL'120 days',NOW()-INTERVAL'30 days','Low',60000,'Sand Stockpile Delivery',NOW()-INTERVAL'30 days',NOW()-INTERVAL'25 days','Jakarta Utara',106.89,-6.11,'Completed'),
('CL004','ORD009',NOW()-INTERVAL'10 days',NOW()+INTERVAL'60 days','High',500000,'Channel Deepening Program',NOW()+INTERVAL'60 days',NOW()+INTERVAL'65 days','Pontianak',109.34,-0.02,'On Progress'),
('CL003','ORD010',NOW()-INTERVAL'90 days',NOW()-INTERVAL'60 days','Medium',20000,'Coastal Protection Works',NOW()-INTERVAL'60 days',NOW()-INTERVAL'58 days','Makassar',119.42,-5.13,'Completed'),
('CL005','ORD011',NOW()-INTERVAL'45 days',NOW()-INTERVAL'10 days','High',1000,'Environmental Impact Survey',NOW()-INTERVAL'10 days',NOW()-INTERVAL'9 days','Benoa',115.21,-8.74,'Completed'),
('CL002','ORD012',NOW()-INTERVAL'3 days',NOW()+INTERVAL'25 days','Low',5000,'Maintenance Dredging Pass',NOW()+INTERVAL'25 days',NOW()+INTERVAL'30 days','Ambon',128.18,-3.69,'Open'),
('CL001','ORD013',NOW()-INTERVAL'200 days',NOW()-INTERVAL'150 days','High',80000,'Land Reclamation Phase 1',NOW()-INTERVAL'150 days',NOW()-INTERVAL'140 days','Jakarta Utara',106.90,-6.08,'Completed'),
('CL004','ORD014',NOW()-INTERVAL'20 days',NOW()+INTERVAL'40 days','Medium',15000,'Pipeline Trench Dredging',NOW()+INTERVAL'40 days',NOW()+INTERVAL'45 days','Natuna',108.38,3.94,'On Progress'),
('CL003','ORD015',NOW()-INTERVAL'1 day',NOW()+INTERVAL'5 days','High',0,'Emergency Hydrographic Survey',NOW()+INTERVAL'5 days',NOW()+INTERVAL'7 days','Makassar',119.40,-5.11,'Open'),
('CL006','ORD016',NOW()-INTERVAL'50 days',NOW()-INTERVAL'20 days','High',25000,'Bridge Foundation Dredge',NOW()-INTERVAL'20 days',NOW()-INTERVAL'18 days','Surabaya',112.74,-7.20,'Completed'),
('CL007','ORD017',NOW()-INTERVAL'25 days',NOW()+INTERVAL'15 days','Medium',0,'Port Development Survey',NOW()+INTERVAL'15 days',NOW()+INTERVAL'18 days','Bitung',125.21,1.44,'On Progress'),
('CL008','ORD018',NOW()-INTERVAL'40 days',NOW()+INTERVAL'20 days','High',200000,'Deepwater Channel Dredge',NOW()+INTERVAL'20 days',NOW()+INTERVAL'25 days','Balikpapan',116.83,-1.27,'On Progress'),
('CL006','ORD019',NOW()-INTERVAL'70 days',NOW()-INTERVAL'40 days','Low',10000,'Sediment Sampling Campaign',NOW()-INTERVAL'40 days',NOW()-INTERVAL'38 days','Semarang',110.43,-6.94,'Completed'),
('CL010','ORD020',NOW()-INTERVAL'15 days',NOW()+INTERVAL'30 days','Medium',30000,'Waterfront Reclamation',NOW()+INTERVAL'30 days',NOW()+INTERVAL'35 days','Ambon',128.19,-3.68,'On Progress'),
('CL002','ORD021',NOW()-INTERVAL'250 days',NOW()-INTERVAL'200 days','High',100000,'Port Expansion Dredge',NOW()-INTERVAL'200 days',NOW()-INTERVAL'195 days','Surabaya',112.72,-7.22,'Completed'),
('CL004','ORD022',NOW()-INTERVAL'8 days',NOW()+INTERVAL'50 days','High',350000,'LNG Terminal Dredge',NOW()+INTERVAL'50 days',NOW()+INTERVAL'55 days','Bontang',117.48,0.14,'On Progress'),
('CL005','ORD023',NOW()-INTERVAL'100 days',NOW()-INTERVAL'70 days','Medium',8000,'Coral Survey Baseline',NOW()-INTERVAL'70 days',NOW()-INTERVAL'68 days','Benoa',115.20,-8.76,'Completed'),
('CL007','ORD024',NOW()-INTERVAL'5 days',NOW()+INTERVAL'20 days','Low',0,'Bathymetric Update Survey',NOW()+INTERVAL'20 days',NOW()+INTERVAL'22 days','Bitung',125.22,1.43,'Open'),
('CL008','ORD025',NOW()-INTERVAL'35 days',NOW()-INTERVAL'5 days','High',180000,'Oil Terminal Access Dredge',NOW()-INTERVAL'5 days',NOW()-INTERVAL'3 days','Balikpapan',116.84,-1.28,'Completed');

-- Order Details (20 records)
INSERT INTO operation.order_details (id_order, id_vessel, code_task, sand_quantity, clay_quantity, status) VALUES
('ORD001','VSL001','TSK001',12000,3000,'Completed'),
('ORD002','VSL006','TSK002',40000,10000,'On Progress'),
('ORD004','VSL004','TSK003',100000,20000,'Completed'),
('ORD006','VSL009','TSK004',0,5000,'On Progress'),
('ORD007','VSL002','TSK005',0,0,'Open'),
('ORD008','VSL004','TSK006',60000,0,'Completed'),
('ORD009','VSL007','TSK007',300000,200000,'On Progress'),
('ORD010','VSL004','TSK008',0,20000,'Completed'),
('ORD011','VSL002','TSK009',0,0,'Completed'),
('ORD013','VSL006','TSK010',80000,0,'Completed'),
('ORD014','VSL007','TSK011',0,15000,'On Progress'),
('ORD016','VSL006','TSK012',20000,5000,'Completed'),
('ORD017','VSL014','TSK013',0,0,'On Progress'),
('ORD018','VSL007','TSK014',150000,50000,'On Progress'),
('ORD019','VSL002','TSK015',0,0,'Completed'),
('ORD020','VSL012','TSK016',25000,5000,'On Progress'),
('ORD021','VSL006','TSK017',100000,0,'Completed'),
('ORD022','VSL007','TSK018',300000,50000,'On Progress'),
('ORD023','VSL002','TSK019',0,0,'Completed'),
('ORD025','VSL006','TSK020',150000,30000,'Completed');

-- Payments (18 records)
INSERT INTO operation.payments (id_client, id_order, id_methodpay, code_payment, total_amount, payment_date, payment_number, status) VALUES
('CL001','ORD001','MP001','PAY001',150000000.00,NOW()-INTERVAL'160 days','INV202401','Completed'),
('CL003','ORD004','MP002','PAY002',500000000.00,NOW()-INTERVAL'20 days','INV202402','Completed'),
('CL002','ORD002','MP001','PAY003',75000000.00,NOW()-INTERVAL'5 days','INV202403','Hold'),
('CL005','ORD006','MP001','PAY004',25000000.00,NOW()-INTERVAL'12 days','INV202404','Completed'),
('CL004','ORD009','MP004','PAY005',1000000000.00,NOW()-INTERVAL'8 days','INV202405','Completed'),
('CL003','ORD010','MP002','PAY006',80000000.00,NOW()-INTERVAL'65 days','INV202406','Completed'),
('CL001','ORD003','MP001','PAY007',10000000.00,NOW()-INTERVAL'1 day','INV202407','Hold'),
('CL001','ORD008','MP001','PAY008',200000000.00,NOW()-INTERVAL'110 days','INV202408','Completed'),
('CL001','ORD013','MP001','PAY009',350000000.00,NOW()-INTERVAL'185 days','INV202409','Completed'),
('CL006','ORD016','MP001','PAY010',120000000.00,NOW()-INTERVAL'45 days','INV202410','Completed'),
('CL005','ORD011','MP003','PAY011',15000000.00,NOW()-INTERVAL'40 days','INV202411','Completed'),
('CL004','ORD014','MP004','PAY012',250000000.00,NOW()-INTERVAL'15 days','INV202412','Hold'),
('CL002','ORD021','MP001','PAY013',480000000.00,NOW()-INTERVAL'230 days','INV202413','Completed'),
('CL008','ORD025','MP002','PAY014',700000000.00,NOW()-INTERVAL'10 days','INV202414','Completed'),
('CL006','ORD019','MP001','PAY015',45000000.00,NOW()-INTERVAL'60 days','INV202415','Completed'),
('CL005','ORD023','MP001','PAY016',30000000.00,NOW()-INTERVAL'90 days','INV202416','Completed'),
('CL004','ORD022','MP005','PAY017',800000000.00,NOW()-INTERVAL'3 days','INV202417','Hold'),
('CL010','ORD020','MP001','PAY018',90000000.00,NOW()-INTERVAL'10 days','INV202418','Completed');

-- Payment Details
INSERT INTO operation.payment_details (id_payment, doc_no, tax, exchange_rate, amount, payment_date) VALUES
('PAY001','DOCPAY001',11,1,150000000.00,NOW()-INTERVAL'160 days'),
('PAY002','DOCPAY002',11,15500,500000000.00,NOW()-INTERVAL'20 days'),
('PAY003','DOCPAY003',11,1,75000000.00,NOW()-INTERVAL'5 days'),
('PAY004','DOCPAY004',11,1,25000000.00,NOW()-INTERVAL'12 days'),
('PAY005','DOCPAY005',11,1,1000000000.00,NOW()-INTERVAL'8 days'),
('PAY006','DOCPAY006',11,15500,80000000.00,NOW()-INTERVAL'65 days'),
('PAY008','DOCPAY008',11,1,200000000.00,NOW()-INTERVAL'110 days'),
('PAY009','DOCPAY009',11,1,350000000.00,NOW()-INTERVAL'185 days'),
('PAY010','DOCPAY010',11,1,120000000.00,NOW()-INTERVAL'45 days'),
('PAY013','DOCPAY013',11,1,480000000.00,NOW()-INTERVAL'230 days'),
('PAY014','DOCPAY014',11,16000,700000000.00,NOW()-INTERVAL'10 days'),
('PAY015','DOCPAY015',11,1,45000000.00,NOW()-INTERVAL'60 days'),
('PAY016','DOCPAY016',11,1,30000000.00,NOW()-INTERVAL'90 days'),
('PAY018','DOCPAY018',11,1,90000000.00,NOW()-INTERVAL'10 days');

-- Client Deposit Histories
INSERT INTO operation.client_deposit_histories (id_client, id_methodpay, deposit, created_at) VALUES
('CL001','MP001',50000000.00,NOW()-INTERVAL'200 days'),
('CL002','MP001',150000000.00,NOW()-INTERVAL'60 days'),
('CL003','MP002',200000000.00,NOW()-INTERVAL'120 days'),
('CL004','MP004',300000000.00,NOW()-INTERVAL'30 days'),
('CL005','MP001',75000000.00,NOW()-INTERVAL'20 days'),
('CL001','MP001',100000000.00,NOW()-INTERVAL'100 days'),
('CL006','MP001',80000000.00,NOW()-INTERVAL'90 days'),
('CL007','MP002',120000000.00,NOW()-INTERVAL'70 days'),
('CL008','MP005',250000000.00,NOW()-INTERVAL'50 days'),
('CL010','MP001',90000000.00,NOW()-INTERVAL'25 days');

-- Vessel Crews (20 assignments)
INSERT INTO operation.vessel_crews (id_user, id_vessel, status, flag) VALUES
('USR003','VSL001','Active','Indonesia'),
('USR005','VSL001','Leave','Indonesia'),
('USR002','VSL002','Active','Indonesia'),
('USR007','VSL004','Active','Philippines'),
('USR006','VSL005','Active','Indonesia'),
('USR010','VSL006','Active','Malaysia'),
('USR012','VSL006','Active','Indonesia'),
('USR015','VSL007','Active','Indonesia'),
('USR013','VSL009','Active','Indonesia'),
('USR007','VSL008','Inactive','Philippines'),
('USR018','VSL011','Active','Indonesia'),
('USR020','VSL011','Active','Indonesia'),
('USR003','VSL012','Active','Indonesia'),
('USR012','VSL012','Active','Indonesia'),
('USR016','VSL014','Active','Indonesia'),
('USR008','VSL014','Active','Indonesia'),
('USR017','VSL013','Active','Indonesia'),
('USR020','VSL009','Active','Indonesia'),
('USR019','VSL004','Active','Indonesia'),
('USR002','VSL001','Inactive','Indonesia');

-- Vessel Activities (20 records)
INSERT INTO operation.vessel_activities (code_activity, id_vessel, id_order, id_task, seq_activity, start_date, end_date, estimate_date, status) VALUES
('ACT001','VSL001','ORD001','TSK001','001',NOW()-INTERVAL'170 days',NOW()-INTERVAL'160 days',NOW()-INTERVAL'160 days','Dredging'),
('ACT002','VSL001','ORD001','TSK001','002',NOW()-INTERVAL'160 days',NOW()-INTERVAL'150 days',NOW()-INTERVAL'150 days','Discharge Cargo'),
('ACT003','VSL002','ORD011','TSK009','001',NOW()-INTERVAL'40 days',NOW()-INTERVAL'10 days',NOW()-INTERVAL'10 days','Settling'),
('ACT004','VSL003',NULL,NULL,'000',NOW()-INTERVAL'5 days',NULL,NULL,'Prev Maintenance'),
('ACT005','VSL004','ORD006','TSK004','001',NOW()-INTERVAL'7 days',NULL,NOW()+INTERVAL'3 days','Delivering'),
('ACT006','VSL005',NULL,NULL,'000',NOW()-INTERVAL'1 day',NULL,NULL,'Idle'),
('ACT007','VSL006','ORD002','TSK002','001',NOW()-INTERVAL'20 days',NULL,NOW()+INTERVAL'10 days','Dredging'),
('ACT008','VSL007','ORD014','TSK011','001',NOW()-INTERVAL'10 days',NULL,NOW()+INTERVAL'30 days','Dredging'),
('ACT009','VSL009','ORD006','TSK004','001',NOW()-INTERVAL'5 days',NULL,NOW()+INTERVAL'5 days','Delivering'),
('ACT010','VSL002','ORD007','TSK005','001',NOW(),NULL,NOW()+INTERVAL'14 days','Preparation'),
('ACT011','VSL006','ORD004','TSK003','001',NOW()-INTERVAL'60 days',NOW()-INTERVAL'50 days',NOW()-INTERVAL'50 days','Dredging'),
('ACT012','VSL004','ORD008','TSK006','001',NOW()-INTERVAL'120 days',NOW()-INTERVAL'110 days',NOW()-INTERVAL'110 days','Delivering'),
('ACT013','VSL007','ORD009','TSK007','001',NOW()-INTERVAL'10 days',NULL,NOW()+INTERVAL'60 days','Dredging'),
('ACT014','VSL011','ORD020','TSK016','001',NOW()-INTERVAL'8 days',NULL,NOW()+INTERVAL'30 days','Delivering'),
('ACT015','VSL012','ORD022','TSK018','001',NOW()-INTERVAL'5 days',NULL,NOW()+INTERVAL'50 days','Dredging'),
('ACT016','VSL014','ORD017','TSK013','001',NOW()-INTERVAL'20 days',NULL,NOW()+INTERVAL'15 days','Settling'),
('ACT017','VSL006','ORD025','TSK020','001',NOW()-INTERVAL'35 days',NOW()-INTERVAL'25 days',NOW()-INTERVAL'25 days','Dredging'),
('ACT018','VSL002','ORD019','TSK015','001',NOW()-INTERVAL'65 days',NOW()-INTERVAL'55 days',NOW()-INTERVAL'55 days','Settling'),
('ACT019','VSL013',NULL,NULL,'000',NOW()-INTERVAL'2 days',NULL,NULL,'Idle'),
('ACT020','VSL008',NULL,NULL,'000',NOW()-INTERVAL'30 days',NULL,NULL,'Docking');

-- Vessel Positions (30 tracking records across all active vessels)
INSERT INTO operation.vessel_positions (id_vessel, id_activity, longitude, latitude, speed, heading, note) VALUES
('VSL001','ACT001',106.885,-6.105,3,45,'Manouvre Priok'),
('VSL001','ACT001',106.886,-6.104,2,45,'Dredging Run 1'),
('VSL001','ACT001',106.887,-6.103,2,50,'Dredging Run 2'),
('VSL001','ACT002',106.890,-6.100,6,180,'Heading Disposal'),
('VSL002','ACT003',115.210,-8.740,4,180,'Survey Line 01'),
('VSL002','ACT003',115.211,-8.741,4,180,'Survey Line 02'),
('VSL002','ACT003',115.212,-8.742,4,180,'Survey Line 03'),
('VSL002','ACT010',106.880,-6.108,5,90,'Transit to site'),
('VSL004','ACT005',115.220,-8.750,6,90,'Approaching Benoa'),
('VSL004','ACT005',115.218,-8.748,5,95,'Anchoring Benoa'),
('VSL005','ACT006',117.140,-0.540,0,0,'Anchored Samarinda'),
('VSL006','ACT007',112.725,-7.215,1,270,'Dredging at Lamong'),
('VSL006','ACT007',112.724,-7.215,1,275,'Turning Head'),
('VSL006','ACT007',112.723,-7.216,2,270,'Dredging Run 2'),
('VSL007','ACT008',108.385,3.945,0,0,'Positioning Natuna'),
('VSL007','ACT013',109.340,-0.025,2,315,'Pontianak Channel'),
('VSL009','ACT009',115.225,-8.755,7,95,'Laden passage Benoa'),
('VSL011','ACT014',128.185,-3.690,8,270,'Transit to Ambon'),
('VSL012','ACT015',117.480,0.140,1,0,'Positioning Bontang'),
('VSL012','ACT015',117.479,0.141,0,0,'Dredging Bontang'),
('VSL014','ACT016',125.210,1.440,4,180,'Survey Line Bitung'),
('VSL014','ACT016',125.211,1.441,4,180,'Survey Line Bitung 2'),
('VSL006','ACT017',116.840,-1.280,3,45,'Balikpapan Channel'),
('VSL002','ACT018',110.425,-6.940,5,90,'Survey Semarang'),
('VSL001','ACT002',106.895,-6.090,8,0,'Returning to Base'),
('VSL004','ACT012',112.740,-7.200,6,270,'Barge Transit SBY'),
('VSL007','ACT008',108.388,3.948,0,5,'Re-positioning'),
('VSL009','ACT009',115.222,-8.752,3,90,'Offloading Benoa'),
('VSL013','ACT019',109.350,-0.030,0,0,'Idle Pontianak'),
('VSL003','ACT004',106.900,-6.115,0,0,'Dry Dock Maintenance');

-- =============================================
-- 2. BUOY SCHEMA
-- =============================================

INSERT INTO buoy.buoys (id_site, code_buoy, longitude, latitude, status, last_mtc) VALUES
('ST001','BYPRIOK01',106.882,-6.102,'Active',NOW()-INTERVAL'30 days'),
('ST001','BYPRIOK02',106.885,-6.105,'MTC',NOW()-INTERVAL'2 days'),
('ST001','BYPRIOK03',106.888,-6.100,'Active',NOW()-INTERVAL'15 days'),
('ST002','BYSBY01',112.722,-7.212,'Active',NOW()-INTERVAL'45 days'),
('ST002','BYSBY02',112.725,-7.215,'Active',NOW()-INTERVAL'10 days'),
('ST005','BYMKS01',119.408,-5.118,'Active',NOW()-INTERVAL'20 days'),
('ST005','BYMKS02',119.412,-5.112,'Inactive',NOW()-INTERVAL'60 days'),
('ST006','BYBENOA01',115.215,-8.745,'Active',NOW()-INTERVAL'20 days'),
('ST006','BYBENOA02',115.218,-8.748,'Active',NOW()-INTERVAL'5 days'),
('ST007','BYSMRD01',117.132,-0.530,'Active',NOW()-INTERVAL'35 days'),
('ST009','BYPNK01',109.340,-0.025,'Active',NOW()-INTERVAL'12 days'),
('ST011','BYBITUNG01',125.208,1.440,'Active',NOW()-INTERVAL'8 days');

INSERT INTO buoy.buoy_sensor_histories (id_buoy, salinitas, turbidity, current, oxygen, tide, density, created_at) VALUES
('BYPRIOK01',32,15,1,6,120,1022,NOW()-INTERVAL'6 hours'),
('BYPRIOK01',32,18,2,6,110,1022,NOW()-INTERVAL'5 hours'),
('BYPRIOK01',33,20,2,5,100,1023,NOW()-INTERVAL'4 hours'),
('BYPRIOK01',33,15,1,6,90,1023,NOW()-INTERVAL'3 hours'),
('BYPRIOK01',32,14,1,6,85,1022,NOW()-INTERVAL'2 hours'),
('BYPRIOK01',31,12,1,7,80,1022,NOW()-INTERVAL'1 hour'),
('BYPRIOK01',31,11,1,7,78,1022,NOW()),
('BYPRIOK03',30,10,1,7,75,1020,NOW()-INTERVAL'4 hours'),
('BYPRIOK03',30,12,1,7,70,1020,NOW()-INTERVAL'2 hours'),
('BYPRIOK03',31,13,1,6,68,1021,NOW()),
('BYSBY01',30,40,1,4,150,1020,NOW()-INTERVAL'4 hours'),
('BYSBY01',30,38,1,4,140,1020,NOW()-INTERVAL'3 hours'),
('BYSBY01',29,35,1,5,135,1020,NOW()-INTERVAL'2 hours'),
('BYSBY01',29,33,2,5,130,1021,NOW()-INTERVAL'1 hour'),
('BYSBY02',29,35,2,5,145,1021,NOW()-INTERVAL'3 hours'),
('BYSBY02',30,32,2,5,140,1021,NOW()-INTERVAL'1 hour'),
('BYMKS01',33,8,1,6,95,1022,NOW()-INTERVAL'3 hours'),
('BYMKS01',33,9,1,6,90,1022,NOW()-INTERVAL'1 hour'),
('BYBENOA01',34,5,0,7,200,1024,NOW()-INTERVAL'4 hours'),
('BYBENOA01',34,6,0,7,190,1024,NOW()-INTERVAL'3 hours'),
('BYBENOA01',35,5,0,7,180,1025,NOW()-INTERVAL'2 hours'),
('BYBENOA01',35,4,0,8,175,1025,NOW()-INTERVAL'1 hour'),
('BYBENOA02',34,4,0,8,170,1024,NOW()-INTERVAL'2 hours'),
('BYBENOA02',35,5,0,8,165,1024,NOW()),
('BYSMRD01',28,55,3,4,80,1018,NOW()-INTERVAL'3 hours'),
('BYSMRD01',28,60,3,4,75,1018,NOW()-INTERVAL'1 hour'),
('BYPNK01',27,65,2,4,70,1017,NOW()-INTERVAL'2 hours'),
('BYPNK01',27,68,3,4,65,1017,NOW()),
('BYBITUNG01',33,12,1,7,110,1023,NOW()-INTERVAL'2 hours'),
('BYBITUNG01',33,10,1,7,105,1023,NOW());

INSERT INTO buoy.buoy_mtc_histories (id_buoy, start_date, end_date, note, created_at) VALUES
('BYPRIOK01',NOW()-INTERVAL'30 days',NOW()-INTERVAL'29 days','Sensor Cleaning Calibration',NOW()-INTERVAL'30 days'),
('BYPRIOK02',NOW()-INTERVAL'2 days',NOW(),'Battery Replacement',NOW()-INTERVAL'2 days'),
('BYSBY02',NOW()-INTERVAL'10 days',NOW()-INTERVAL'9 days','Redeployment Post Storm',NOW()-INTERVAL'10 days'),
('BYMKS01',NOW()-INTERVAL'20 days',NOW()-INTERVAL'19 days','Antifouling Coating',NOW()-INTERVAL'20 days'),
('BYBENOA01',NOW()-INTERVAL'15 days',NOW()-INTERVAL'15 days','Monthly Inspection',NOW()-INTERVAL'15 days'),
('BYSMRD01',NOW()-INTERVAL'35 days',NOW()-INTERVAL'34 days','Turbidity Sensor Replace',NOW()-INTERVAL'35 days'),
('BYMKS02',NOW()-INTERVAL'60 days',NOW(),'Anchor Chain Replace',NOW()-INTERVAL'60 days');

-- =============================================
-- 3. LOG SCHEMA
-- =============================================

INSERT INTO log.term_desc (code_term, term, compactness, created_at) VALUES
('TRM001','Very Dense','High',NOW()),
('TRM002','Medium Dense','Medium',NOW()),
('TRM003','Loose','Low',NOW()),
('TRM004','Very Soft','Very Low',NOW()),
('TRM005','Hard','Very High',NOW()),
('TRM006','Firm','Medium High',NOW()),
('TRM007','Soft','Low Medium',NOW());

INSERT INTO log.soil_desc (code_lithology, soil_type, soil_name, gr_size) VALUES
('SL001','Sand','Silty Sand','006to20mm'),
('SL002','Clay','Marine Clay','LT0002mm'),
('SL003','Silt','Sandy Silt','0002to006mm'),
('SL004','Rock','Limestone','GT60mm'),
('SL005','Gravel','Coral Debris','2to60mm'),
('SL006','Sand','Fine Sand','006to10mm'),
('SL007','Clay','Peaty Clay','LT0002mm'),
('SL008','Silt','Organic Silt','0002to004mm');

INSERT INTO log.vibrocore_logs (id_site, id_client, id_user, id_core, doc_no, total_sample_depth, total_attempt, barrel_length, penetration, recovery, heading, time, longitude, latitude, water_depth, total_soil) VALUES
('ST001','CL001','USR002','VC24001','REPVC001',600,1,600,580,550,0,'09:00:00',106.881,-6.101,14,2),
('ST002','CL002','USR002','VC24002','REPVC002',400,1,600,450,420,0,'13:30:00',112.721,-7.211,12,1),
('ST006','CL005','USR008','VC24003','REPVC003',300,2,400,250,200,45,'10:00:00',115.216,-8.746,8,3),
('ST004','CL002','USR015','VC24004','REPVC004',500,1,600,480,460,90,'15:15:00',98.691,3.786,10,2),
('ST005','CL003','USR016','VC24005','REPVC005',550,1,600,520,490,180,'08:30:00',119.409,-5.115,15,2),
('ST009','CL004','USR002','VC24006','REPVC006',450,2,600,400,370,270,'11:00:00',109.341,-0.024,11,3),
('ST007','CL004','USR008','VC24007','REPVC007',350,1,500,310,290,0,'14:00:00',117.133,-0.531,9,2),
('ST012','CL001','USR015','VC24008','REPVC008',480,1,600,460,440,135,'10:30:00',109.016,-7.722,13,2);

INSERT INTO log.vibrocore_log_details (id_term, doc_no, code_lithology, sample_depth_start, sample_depth_end, description, torvane, penetrometer, penetration, sequence) VALUES
('TRM002','REPVC001','SL001',0,300,'Greyish silty sand with shell fragments',0,10,300,1),
('TRM001','REPVC001','SL002',300,550,'Stiff dark grey marine clay',4,25,250,2),
('TRM004','REPVC002','SL003',0,420,'Very soft black river silt organic',1,2,420,1),
('TRM002','REPVC003','SL001',0,100,'Loose grey coarse sand',2,5,100,1),
('TRM005','REPVC003','SL004',100,250,'Hard limestone refusal at 250cm',10,50,150,2),
('TRM003','REPVC004','SL002',0,460,'Soft grey marine clay',2,4,460,1),
('TRM006','REPVC005','SL006',0,200,'Firm fine sand with organics',3,12,200,1),
('TRM001','REPVC005','SL002',200,490,'Dense stiff clay',5,30,290,2),
('TRM004','REPVC006','SL007',0,370,'Soft peaty clay river deposit',1,3,370,1),
('TRM003','REPVC007','SL008',0,290,'Loose organic silt dark',1,2,290,1),
('TRM002','REPVC008','SL001',0,250,'Medium dense silty sand',2,8,250,1),
('TRM001','REPVC008','SL002',250,440,'Stiff clay fissured',4,22,190,2);

INSERT INTO log.sample_logs (id_vessel, id_surveyor, id_captain, id_site, doc_no, log_date, sample_type, total_sample, packages_number) VALUES
('VSL002','USR002','USR003','ST002','LOGSPL001',CURRENT_DATE,'Grab Sample',10,3),
('VSL002','USR008','USR003','ST006','LOGSPL002',CURRENT_DATE-INTERVAL'15 days','Grab Sample',5,1),
('VSL014','USR016','USR018','ST008','LOGSPL003',CURRENT_DATE-INTERVAL'25 days','Grab Sample',8,2),
('VSL002','USR015','USR003','ST004','LOGSPL004',CURRENT_DATE-INTERVAL'10 days','Box Core',6,2),
('VSL014','USR002','USR018','ST011','LOGSPL005',CURRENT_DATE-INTERVAL'5 days','Grab Sample',12,3);

INSERT INTO log.sample_log_details (id_term, id_lithology, doc_no, sample_depth_start, sample_depth_end, description, torvane, penetrometer, penetration, sequence) VALUES
('TRM004','SL002','LOGSPL001',0,20,'Surface soft mud sediment',0,0,20,1),
('TRM002','SL001','LOGSPL002',0,15,'White coral sand sample Bali',0,0,15,1),
('TRM003','SL003','LOGSPL003',0,18,'Silt offshore Natuna',0,0,18,1),
('TRM004','SL002','LOGSPL004',0,22,'Soft clay Belawan channel',0,0,22,1),
('TRM002','SL001','LOGSPL005',0,12,'Fine sand Bitung port',0,0,12,1);

INSERT INTO log.surveis (id_site, id_surveyor, code_survey, doc_no, core_no, status) VALUES
('ST001','USR002','SRV001','DOCSRV202401','CORE01','Verified'),
('ST006','USR008','SRV002','DOCSRV202402','CORE02','Processing'),
('ST008','USR015','SRV003','DOCSRV202403','CORE03','Verified'),
('ST004','USR016','SRV004','DOCSRV202404','CORE04','Draft'),
('ST011','USR002','SRV005','DOCSRV202405','CORE05','Processing'),
('ST005','USR008','SRV006','DOCSRV202406','CORE01','Verified'),
('ST009','USR015','SRV007','DOCSRV202407','CORE01','Draft');

INSERT INTO log.survey_details (id_survey) VALUES
('SRV001'),('SRV002'),('SRV003'),('SRV004'),('SRV005'),('SRV006'),('SRV007');

-- =============================================
-- 4. SURVEY SCHEMA
-- =============================================

INSERT INTO survey.daily_report_survey_activity (project_name, code_report, id_site, id_vessel, id_user, date_survey, comment) VALUES
('Priok Channel Maintenance','DPRSRV001','ST001','VSL002','USR002',CURRENT_DATE-INTERVAL'1 day','Good weather full MBES coverage'),
('Bali Benoa Baseline','DPRSRV002','ST006','VSL002','USR008',CURRENT_DATE-INTERVAL'15 days','Pre dredge survey part 1 complete'),
('Natuna Pipeline Check','DPRSRV003','ST008','VSL014','USR002',CURRENT_DATE-INTERVAL'30 days','Side Scan Sonar operations clear'),
('Belawan Channel Survey','DPRSRV004','ST004','VSL014','USR016',CURRENT_DATE-INTERVAL'8 days','SBES bathymetry 25 lines'),
('Bitung Port Development','DPRSRV005','ST011','VSL014','USR002',CURRENT_DATE-INTERVAL'3 days','Initial coverage 80pct done'),
('Makassar Bay Baseline','DPRSRV006','ST005','VSL002','USR008',CURRENT_DATE-INTERVAL'20 days','Pre-reclamation survey'),
('Pontianak Access Survey','DPRSRV007','ST009','VSL002','USR015',CURRENT_DATE-INTERVAL'12 days','Flood current interfered AM session');

INSERT INTO survey.daily_report_survey_activity_details (id_report, survey_date, longitude, latitude, start_time, end_time, description) VALUES
('DPRSRV001',CURRENT_DATE-INTERVAL'1 day',106.885,-6.105,CURRENT_DATE-INTERVAL'1 day'+INTERVAL'08:00',CURRENT_DATE-INTERVAL'1 day'+INTERVAL'17:00','MBES Lines 01 to 20 completed'),
('DPRSRV002',CURRENT_DATE-INTERVAL'15 days',115.215,-8.745,CURRENT_DATE-INTERVAL'15 days'+INTERVAL'07:30',CURRENT_DATE-INTERVAL'15 days'+INTERVAL'16:00','SBES Check lines all 12 lines'),
('DPRSRV003',CURRENT_DATE-INTERVAL'30 days',108.385,3.945,CURRENT_DATE-INTERVAL'30 days'+INTERVAL'06:00',CURRENT_DATE-INTERVAL'30 days'+INTERVAL'18:00','SSS debris check along route A'),
('DPRSRV004',CURRENT_DATE-INTERVAL'8 days',98.691,3.786,CURRENT_DATE-INTERVAL'8 days'+INTERVAL'07:00',CURRENT_DATE-INTERVAL'8 days'+INTERVAL'15:30','Main channel lines 1 to 25'),
('DPRSRV005',CURRENT_DATE-INTERVAL'3 days',125.208,1.440,CURRENT_DATE-INTERVAL'3 days'+INTERVAL'08:00',CURRENT_DATE-INTERVAL'3 days'+INTERVAL'16:30','Port basin 80pct coverage'),
('DPRSRV006',CURRENT_DATE-INTERVAL'20 days',119.409,-5.115,CURRENT_DATE-INTERVAL'20 days'+INTERVAL'07:00',CURRENT_DATE-INTERVAL'20 days'+INTERVAL'17:00','All planned lines acquired'),
('DPRSRV007',CURRENT_DATE-INTERVAL'12 days',109.341,-0.024,CURRENT_DATE-INTERVAL'12 days'+INTERVAL'09:00',CURRENT_DATE-INTERVAL'12 days'+INTERVAL'15:00','AM session only due to current');

INSERT INTO survey.daily_report_survey_activity_weather (id_report, survey_date, longitude, latitude, time, weather, wind_speed, wave) VALUES
('DPRSRV001',CURRENT_DATE-INTERVAL'1 day',106.885,-6.105,CURRENT_DATE-INTERVAL'1 day'+INTERVAL'12:00',1,8,0),
('DPRSRV002',CURRENT_DATE-INTERVAL'15 days',115.215,-8.745,CURRENT_DATE-INTERVAL'15 days'+INTERVAL'12:00',1,10,0),
('DPRSRV003',CURRENT_DATE-INTERVAL'30 days',108.385,3.945,CURRENT_DATE-INTERVAL'30 days'+INTERVAL'12:00',2,15,1),
('DPRSRV004',CURRENT_DATE-INTERVAL'8 days',98.691,3.786,CURRENT_DATE-INTERVAL'8 days'+INTERVAL'12:00',1,12,0),
('DPRSRV005',CURRENT_DATE-INTERVAL'3 days',125.208,1.440,CURRENT_DATE-INTERVAL'3 days'+INTERVAL'12:00',1,8,0),
('DPRSRV006',CURRENT_DATE-INTERVAL'20 days',119.409,-5.115,CURRENT_DATE-INTERVAL'20 days'+INTERVAL'12:00',1,10,0),
('DPRSRV007',CURRENT_DATE-INTERVAL'12 days',109.341,-0.024,CURRENT_DATE-INTERVAL'12 days'+INTERVAL'12:00',3,20,2);

INSERT INTO survey.daily_report_vibrocore (project_name, code_report, id_site, id_vessel, id_sample, day_survey, date_survey, rig_type, barrel_size, wellsite, total_coreing, total_depth_coring, total_depth_logging, comment) VALUES
('Priok Geotech Investigation','DPRVC001','ST001','VSL001','VC01','Day 01',CURRENT_DATE-INTERVAL'3 days','Elec Vibro',10,'WSP1',3,12,10,'All samples recovered good'),
('Bali Soil Investigation','DPRVC002','ST006','VSL001','VC02','Day 01',CURRENT_DATE-INTERVAL'20 days','Gravity Corer',3,'WSB1',5,8,6,'Short recovery due to limestone'),
('Belawan Geotech','DPRVC003','ST004','VSL001','VC03','Day 01',CURRENT_DATE-INTERVAL'7 days','Elec Vibro',10,'WSB2',4,16,14,'Soft clay good recovery'),
('Pontianak SI','DPRVC004','ST009','VSL001','VC04','Day 01',CURRENT_DATE-INTERVAL'11 days','Gravity Corer',5,'WSP2',2,10,8,'Interrupted by rain morning'),
('Makassar Geotech','DPRVC005','ST005','VSL001','VC05','Day 01',CURRENT_DATE-INTERVAL'18 days','Elec Vibro',10,'WSM1',3,14,12,'Dense sand layer encountered');

INSERT INTO survey.daily_report_vibrocore_detail (id_report, hole_id, longitude, latitude, from_depth, to_depth, core_length, recovery_rate, description) VALUES
('DPRVC001','BH01',106.882,-6.102,0,400,380,95,'Sand to Clay transition at 300cm'),
('DPRVC001','BH02',106.883,-6.103,0,350,320,91,'Clay throughout with shell hash'),
('DPRVC001','BH03',106.884,-6.104,0,450,420,93,'Sandy clay mixed'),
('DPRVC002','BH01',115.216,-8.746,0,100,80,80,'Coral sand then limestone refusal'),
('DPRVC003','BH01',98.692,3.787,0,550,520,94,'Soft muddy clay good recovery'),
('DPRVC003','BH02',98.690,3.785,0,480,460,95,'Marine clay with silt lenses'),
('DPRVC004','BH01',109.342,-0.025,0,300,270,90,'Peaty clay river deposit'),
('DPRVC005','BH01',119.410,-5.116,0,420,380,90,'Dense sand below 200cm clay above');

-- =============================================
-- 5. AUDIT SCHEMA
-- =============================================

INSERT INTO audit.audit_logs_default (action, table_name, field, record_id, old_data, new_data, changed_by) VALUES
('UPDATE','orders','status','ORD001','On Progress','Completed','USR001'),
('INSERT','sites','all','ST008','none','Natuna added','USR001'),
('UPDATE','vessels','status','VSL003','Active','Maintenance','USR004'),
('UPDATE','orders','status','ORD004','On Progress','Completed','USR001'),
('INSERT','clients','all','CL006','none','CL006 added','USR001'),
('UPDATE','vessel_crews','status','USR005','Active','Leave','USR004'),
('UPDATE','payments','status','PAY003','Completed','Hold','USR009'),
('INSERT','vessels','all','VSL011','none','VSL011 added','USR001'),
('UPDATE','orders','status','ORD016','On Progress','Completed','USR017'),
('UPDATE','sites','status','ST003','Active','Inactive','USR001');

-- End of Dummy Data




