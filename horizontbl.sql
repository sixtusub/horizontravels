USE horizondb; 

DROP TABLE IF EXISTS routes; 
DROP TABLE IF EXISTS bookings;
DROP TABLE  IF EXISTS users; 

CREATE TABLE routes (
  idRoutes INT NOT NULL, 
  deptCity VARCHAR(45) NOT NULL, 
  deptTime VARCHAR(5) NOT NULL, 
  arrivCity VARCHAR(45) NOT NULL, 
  arrivTime VARCHAR(45) NOT NULL, 
  stFare double NOT NULL,
  PRIMARY KEY (idRoutes)); 
  
INSERT INTO routes VALUES 
  (1000, 'Bristol', '08:00', 'Manchester', '08:45', 80.00), 
  (1001, 'Bristol', '12:00', 'Manchester', '12:45', 60.00), 
  (1002, 'Bristol', '20:00', 'Manchester', '20:45', 70.00), 
  (1003, 'Bristol', '10:00', 'Glasgow', '11:00', 60.00), 
  (1004, 'Bristol', '15:00', 'London', '15:45', 50.00), 
  (1005, 'Glasgow', '20:00', 'Bristol', '20:45', 80.00), 
  (1006, 'Bristol', '08:00', 'Plymouth', '08:45', 40.00), 
  (1007, 'Birmingham', '08:00', 'Dundee', '08:45', 70.00), 
  (1008, 'Nottingham', '11:00', 'Edinburgh', '11:45', 50.00), 
  (1009, 'Southampton', '08:00', 'Manchester', '08:45', 60.00), 
  (1010, 'Cardiff', '12:00', 'Edinburgh', '12:45', 90.00), 
  (1011, 'Manchester', '11:00', 'Dundee', '11:45', 100.00), 
  (1012, 'Manchester', '08:00', 'Southampton', '08:45', 80.00), 
  (1013, 'Glasgow', '08:00', 'London', '08:45', 120.00), 
  (1014, 'London', '08:00', 'Manchester', '08:45', 90.00),
  (1015, 'London', '08:00', 'Glasgow', '08:45', 90.00),
  (1016, 'London', '08:00', 'Edinburgh', '08:45', 100.00);
  
CREATE TABLE bookings (
  idBooking INT NOT NULL auto_increment, 
  userId INT NOT NULL,
  deptDate  datetime NOT NULL,   
  arrivDate datetime NOT NULL, 
  idRoutes INT NOT NULL,  
  noOfSeats INT NOT NULL default 1, 
  totFare Double NOT NULL,  
  FOREIGN KEY (idRoutes) REFERENCES routes (idRoutes),
  PRIMARY KEY (idBooking)
);

CREATE table users (id INTEGER NOT NULL AUTO_INCREMENT, username VARCHAR(64) NOT NULL UNIQUE , email VARCHAR(120) NOT NULL UNIQUE, password_hash VARCHAR(128), usertype VARCHAR(8) DEFAULT 'standard', primary key (id));
INSERT INTO users VALUES 
	('test','123','test@test.com', 'standard'),
	('sixtus','123456','sixtus@gmail.com', 'standard');
