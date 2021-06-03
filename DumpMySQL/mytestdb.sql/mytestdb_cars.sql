-- MySQL dump 10.13  Distrib 8.0.24, for Win64 (x86_64)
--
-- Host: localhost    Database: mytestdb
-- ------------------------------------------------------
-- Server version	8.0.24

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `cars`
--

DROP TABLE IF EXISTS `cars`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `cars` (
  `id` int NOT NULL AUTO_INCREMENT,
  `brand` varchar(15) DEFAULT NULL,
  `model` varchar(15) DEFAULT NULL,
  `year_of_release` year DEFAULT NULL,
  `color` varchar(20) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=34 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `cars`
--

LOCK TABLES `cars` WRITE;
/*!40000 ALTER TABLE `cars` DISABLE KEYS */;
INSERT INTO `cars` VALUES (1,'mercedes','gle',2020,'black'),(2,'bmv','m5',2018,'blue'),(3,'audi','a8',2019,'red'),(4,'audi','a7',2015,'white'),(5,'VW','polo',2021,'silver'),(6,'VW','polo',2021,'silver'),(7,'VW','polo',2021,'silver'),(8,'VW','polo',2021,'silver'),(9,'VW','polo',2021,'silver'),(10,'VW','polo',2021,'silver'),(11,'VW','polo',2021,'silver'),(12,'VW','polo',2021,'silver'),(13,'VW','polo',2021,'silver'),(14,'VW','polo',2021,'silver'),(15,'GAZ','3110',2015,'green'),(16,'GAZ','3110',2015,'red'),(17,'GAZ','3110',2015,'red'),(18,'GAZ','3110',2015,'red'),(19,'VAZ','Niva',2015,'white'),(20,'ZZZ','Z2000',2015,'green'),(21,'ford','focus',2005,'red'),(22,'fiat','albea',2009,'green'),(23,'UAZ','112',2003,'green'),(24,'UAZ','112',2003,'green'),(25,'UAZ','112',2003,'green'),(26,'UAZ','112',2001,'blue'),(27,'UAZ','112',2000,'red'),(28,'kia','ceed',2012,'silver'),(29,'nissan','almera',2000,'black'),(30,'nissan','almera',2000,'black'),(31,'nissan','almera',2000,'black'),(32,'nissan','almera',2000,'black'),(33,'nissan','almera',2000,'black');
/*!40000 ALTER TABLE `cars` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2021-05-06 15:25:42
