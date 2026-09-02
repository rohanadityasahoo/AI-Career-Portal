-- MySQL dump 10.13  Distrib 9.7.0, for Win64 (x86_64)
--
-- Host: localhost    Database: careerpilot_ai
-- ------------------------------------------------------
-- Server version	8.0.46

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `interview_results`
--

DROP TABLE IF EXISTS `interview_results`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `interview_results` (
  `interview_id` int NOT NULL AUTO_INCREMENT,
  `student_id` int DEFAULT NULL,
  `role` varchar(100) NOT NULL,
  `domain` varchar(100) NOT NULL,
  `difficulty` varchar(20) NOT NULL,
  `average_score` decimal(5,2) NOT NULL,
  `question_scores` text NOT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`interview_id`),
  KEY `idx_interview_results_student_id` (`student_id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `interview_results`
--

LOCK TABLES `interview_results` WRITE;
/*!40000 ALTER TABLE `interview_results` DISABLE KEYS */;
INSERT INTO `interview_results` VALUES (1,1,'software_engineer','Information Technology','easy',21.00,'14, 27, 16, 34, 14','2026-08-23 06:18:24');
/*!40000 ALTER TABLE `interview_results` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `resume_analysis`
--

DROP TABLE IF EXISTS `resume_analysis`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `resume_analysis` (
  `analysis_id` int NOT NULL AUTO_INCREMENT,
  `resume_filename` varchar(255) NOT NULL,
  `ats_score` decimal(5,2) DEFAULT NULL,
  `jd_match_percentage` decimal(5,2) DEFAULT NULL,
  `skill_score` decimal(5,2) DEFAULT NULL,
  `section_score` decimal(5,2) DEFAULT NULL,
  `content_score` decimal(5,2) DEFAULT NULL,
  `matched_skills` text,
  `missing_skills` text,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `student_id` int DEFAULT NULL,
  PRIMARY KEY (`analysis_id`),
  KEY `fk_resume_student` (`student_id`),
  CONSTRAINT `fk_resume_student` FOREIGN KEY (`student_id`) REFERENCES `students` (`student_id`)
) ENGINE=InnoDB AUTO_INCREMENT=56 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `resume_analysis`
--

LOCK TABLES `resume_analysis` WRITE;
/*!40000 ALTER TABLE `resume_analysis` DISABLE KEYS */;
INSERT INTO `resume_analysis` VALUES (1,'Deep_Purple_Professional_College_Student_CV_Resume.pdf',52.15,54.55,30.00,66.67,80.00,'python, java, c, mysql, sql, machine learning','javascript, flask, react, git, docker','2026-08-13 15:45:54',NULL),(2,'Deep_Purple_Professional_College_Student_CV_Resume.pdf',57.00,66.67,30.00,66.67,80.00,'c, machine learning','docker','2026-08-13 15:46:29',NULL),(3,'Mobile-Application-Testing-Resume.pdf',35.54,36.36,13.33,50.00,70.00,'java, c, sql, git','python, javascript, flask, react, mysql, machine learning, docker','2026-08-13 15:49:38',NULL),(4,'quality-analyst-1-year-exp.pdf',30.11,18.18,10.00,66.67,65.00,'java, c','python, javascript, flask, react, mysql, sql, machine learning, git, docker','2026-08-13 15:52:11',NULL),(5,'quality-analyst-1-year-exp.pdf',30.11,18.18,10.00,66.67,65.00,'java, c','python, javascript, flask, react, mysql, sql, machine learning, git, docker','2026-08-13 15:55:38',NULL),(6,'quality-analyst-1-year-exp.pdf',30.11,18.18,10.00,66.67,65.00,'java, c','python, javascript, flask, react, mysql, sql, machine learning, git, docker','2026-08-13 15:56:05',NULL),(7,'manual-testing-with-qtp-resume.pdf',38.66,33.33,13.33,66.67,80.00,'c','python, machine learning','2026-08-13 15:58:08',NULL),(8,'Mobile-Application-Testing-Resume.pdf',21.00,0.00,13.33,50.00,70.00,'','','2026-08-14 14:57:38',NULL),(9,'Mobile-Application-Testing-Resume.pdf',21.00,0.00,13.33,50.00,70.00,'','','2026-08-14 14:57:57',NULL),(10,'Mobile-Application-Testing-Resume.pdf',21.00,0.00,13.33,50.00,70.00,'','','2026-08-14 15:10:44',NULL),(11,'Stockholm-Resume-Template-Simple.pdf',22.33,0.00,3.33,66.67,80.00,'','','2026-08-14 15:23:12',NULL),(12,'Stockholm-Resume-Template-Simple.pdf',22.33,0.00,3.33,66.67,80.00,'','','2026-08-14 15:34:32',NULL),(13,'Stockholm-Resume-Template-Simple.pdf',22.33,0.00,3.33,66.67,80.00,'','','2026-08-14 15:35:34',NULL),(14,'ilide.info-naresh-python-developer-fresher-pr_bd84d1c5fc31d52ba803ad72003baf86.pdf',64.00,100.00,20.00,50.00,80.00,'python','','2026-08-14 15:42:51',NULL),(15,'ilide.info-naresh-python-developer-fresher-pr_bd84d1c5fc31d52ba803ad72003baf86.pdf',64.00,100.00,20.00,50.00,80.00,'python','','2026-08-14 18:39:31',NULL),(16,'ilide.info-naresh-python-developer-fresher-pr_bd84d1c5fc31d52ba803ad72003baf86.pdf',64.00,100.00,20.00,50.00,80.00,'python','','2026-08-16 06:42:45',1),(17,'it-manager-resume.pdf',23.83,0.00,13.33,66.67,65.00,'','','2026-08-17 10:16:04',1),(18,'it-project-manager-resume.pdf',49.90,55.17,26.67,66.67,65.00,'python','','2026-08-17 10:55:02',1),(19,'it-project-manager-resume.pdf',49.90,55.17,26.67,66.67,65.00,'python','','2026-08-17 10:58:40',1),(20,'it-project-manager-resume.pdf',50.17,50.17,26.67,66.67,65.00,'python, java, c, javascript, django, node.js, git, github','','2026-08-17 12:36:30',1),(21,'it-project-manager-resume.pdf',50.17,50.17,26.67,66.67,65.00,'python, java, c, javascript, django, node.js, git, github','','2026-08-17 12:36:42',1),(22,'it-project-manager-resume.pdf',50.17,50.17,26.67,66.67,65.00,'python, java, c, javascript, django, node.js, git, github','','2026-08-17 12:36:54',1),(23,'it-project-manager-resume.pdf',50.17,50.17,26.67,66.67,65.00,'python, java, c, javascript, django, node.js, git, github','','2026-08-17 12:41:05',1),(24,'it-project-manager-resume.pdf',50.17,50.17,26.67,66.67,65.00,'python, java, c, javascript, django, node.js, git, github','','2026-08-17 12:48:25',1),(25,'it-project-manager-resume.pdf',50.17,50.17,26.67,66.67,65.00,'python, java, c, javascript, django, node.js, git, github','','2026-08-17 12:48:39',1),(26,'it-project-manager-resume.pdf',50.17,50.17,26.67,66.67,65.00,'python, java, c, javascript, django, node.js, git, github','','2026-08-17 12:54:06',1),(27,'it-project-manager-resume.pdf',44.04,44.04,26.67,66.67,65.00,'python, java, c, javascript, django, node.js, git, github','','2026-08-17 13:13:14',1),(28,'Dublin-Resume-Template-Modern.pdf',39.54,39.54,3.33,66.67,80.00,'c','','2026-08-17 13:17:01',1),(29,'Dublin-Resume-Template-Modern.pdf',39.54,39.54,3.33,66.67,80.00,'c','','2026-08-17 13:25:37',1),(30,'Dublin-Resume-Template-Modern.pdf',39.28,39.28,2.02,66.67,80.00,'c, go','','2026-08-17 13:30:12',1),(31,'Dublin-Resume-Template-Modern.pdf',38.88,38.88,0.00,66.67,80.00,'','','2026-08-17 13:35:54',1),(32,'Dublin-Resume-Template-Modern.pdf',38.88,38.88,0.00,66.67,80.00,'','','2026-08-17 13:36:09',1),(33,'Dublin-Resume-Template-Modern.pdf',38.88,38.88,0.00,66.67,80.00,'','','2026-08-17 13:43:36',1),(34,'Dublin-Resume-Template-Modern.pdf',38.88,38.88,0.00,66.67,80.00,'','','2026-08-17 13:52:14',1),(35,'it-project-manager-resume.pdf',39.90,39.90,6.00,66.67,65.00,'python, javascript, javascript, node.js, django, github','','2026-08-17 13:56:19',1),(36,'it-project-manager-resume.pdf',41.70,41.70,15.00,66.67,65.00,'python, javascript, node.js, django, github','','2026-08-17 14:06:52',1),(37,'it-project-manager-resume.pdf',55.43,55.43,15.00,66.67,65.00,'python, javascript, node.js, django, github','','2026-08-17 14:11:53',1),(38,'it-project-manager-resume.pdf',55.43,55.43,15.00,66.67,65.00,'python, javascript, node.js, django, github','','2026-08-17 14:41:45',1),(39,'it-project-manager-resume.pdf',55.43,55.43,15.00,66.67,65.00,'python, javascript, node.js, django, github','','2026-08-17 14:41:56',1),(40,'it-project-manager-resume.pdf',55.43,55.43,15.00,66.67,65.00,'python, javascript, node.js, django, github','','2026-08-17 14:50:35',1),(41,'it-project-manager-resume.pdf',56.23,56.23,18.97,66.67,65.00,'python, javascript, node.js, django, github, project manager, agile, scrum, jira, sdlc','','2026-08-17 15:04:13',1),(42,'it-project-manager-resume.pdf',56.23,56.23,18.97,66.67,65.00,'python, javascript, node.js, django, github, project manager, agile, scrum, jira, sdlc','','2026-08-17 15:06:16',1),(43,'it-project-manager-resume.pdf',62.33,62.33,49.50,66.67,65.00,'python, javascript, node.js, django, github, project manager, agile, scrum, jira, sdlc','','2026-08-17 15:11:40',1),(44,'it-project-manager-resume.pdf',62.33,62.33,49.50,66.67,65.00,'python, javascript, node.js, django, github, project manager, agile, scrum, jira, sdlc','','2026-08-17 15:16:23',1),(45,'it-project-manager-resume.pdf',62.33,62.33,49.50,66.67,65.00,'python, javascript, node.js, django, github, project manager, agile, scrum, jira, sdlc','','2026-08-17 15:20:46',1),(46,'it-project-manager-resume.pdf',62.33,62.33,49.50,66.67,65.00,'python, javascript, node.js, django, github, project manager, agile, scrum, jira, sdlc','','2026-08-17 15:32:53',1),(47,'Rohan_Aditya_Sahoo_Resume.pdf',72.15,72.15,66.00,83.33,90.00,'python, java, c++, c, javascript, html, css, flask, mysql, sql, machine learning, artificial intelligence, data analysis, nlp, git, github, vs code, sdlc, software development lifecycle','','2026-08-17 15:33:39',1),(48,'Dublin-Resume-Template-Modern.pdf',53.61,53.61,0.00,66.67,80.00,'','','2026-08-17 15:34:09',1),(49,'Dublin-Resume-Template-Modern.pdf',53.61,53.61,0.00,66.67,80.00,'','','2026-08-17 15:48:09',1),(50,'Dublin-Resume-Template-Modern.pdf',65.83,65.83,61.11,66.67,80.00,'travel, tourism, travel agent, travel consulting, itineraries, reservations, hospitality, customer service, travel coordination, event planning, international travel, accounting, budgeting, sales','','2026-08-17 16:04:30',1),(51,'Dublin-Resume-Template-Modern.pdf',65.83,65.83,61.11,66.67,80.00,'travel, tourism, travel agent, travel consulting, itineraries, reservations, hospitality, customer service, travel coordination, event planning, international travel, accounting, budgeting, sales','','2026-08-17 16:15:53',1),(52,'Sydney-Resume-Template-Modern.pdf',54.60,54.60,6.25,66.67,80.00,'advertising','','2026-08-18 08:31:02',1),(53,'Stockholm-Resume-Template-Simple.pdf',52.69,52.69,0.00,66.67,80.00,'','','2026-08-18 08:31:28',1),(54,'Dublin-Resume-Template-Modern.pdf',65.83,65.83,61.11,66.67,80.00,'travel, tourism, travel agent, travel consulting, itineraries, reservations, hospitality, customer service, travel coordination, event planning, international travel, accounting, budgeting, sales','','2026-08-18 08:31:46',1),(55,'Dublin-Resume-Template-Modern.pdf',65.83,65.83,61.11,66.67,80.00,'travel, tourism, travel agent, travel consulting, itineraries, reservations, hospitality, customer service, travel coordination, event planning, international travel, accounting, budgeting, sales','','2026-08-18 08:32:10',1);
/*!40000 ALTER TABLE `resume_analysis` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `student_profile`
--

DROP TABLE IF EXISTS `student_profile`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `student_profile` (
  `profile_id` int NOT NULL AUTO_INCREMENT,
  `student_id` int NOT NULL,
  `semester` varchar(30) DEFAULT NULL,
  `cgpa` decimal(4,2) DEFAULT NULL,
  `career_goal` varchar(150) DEFAULT NULL,
  `target_role` varchar(150) DEFAULT NULL,
  `preferred_industry` varchar(150) DEFAULT NULL,
  `preferred_location` varchar(150) DEFAULT NULL,
  PRIMARY KEY (`profile_id`),
  UNIQUE KEY `student_id` (`student_id`),
  CONSTRAINT `student_profile_ibfk_1` FOREIGN KEY (`student_id`) REFERENCES `students` (`student_id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `student_profile`
--

LOCK TABLES `student_profile` WRITE;
/*!40000 ALTER TABLE `student_profile` DISABLE KEYS */;
INSERT INTO `student_profile` VALUES (1,1,'8',9.00,'software development','python developer','IT','odisha');
/*!40000 ALTER TABLE `student_profile` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `students`
--

DROP TABLE IF EXISTS `students`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `students` (
  `student_id` int NOT NULL AUTO_INCREMENT,
  `full_name` varchar(100) NOT NULL,
  `email` varchar(100) NOT NULL,
  `phone` varchar(15) NOT NULL,
  `password` varchar(255) NOT NULL,
  `gender` enum('Male','Female','Other') DEFAULT NULL,
  `college` varchar(150) DEFAULT NULL,
  `branch` varchar(100) DEFAULT NULL,
  `year` int DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `profile_photo` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`student_id`),
  UNIQUE KEY `email` (`email`),
  UNIQUE KEY `phone` (`phone`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `students`
--

LOCK TABLES `students` WRITE;
/*!40000 ALTER TABLE `students` DISABLE KEYS */;
INSERT INTO `students` VALUES (1,'Rohan','rohan@gmail.com','1234567890','scrypt:32768:8:1$306sdRdDJ7dyZcbO$404c4e6b3126e9816702ad91b47d012701a1fe180569dd5449e70f3a837389cd257cd96027f716df7d67f2c06d97b400d36243bf1e298097159d2ca194990f74','Male','KIIT University','cse',4,'2026-08-11 11:07:51','student_1.jpeg');
/*!40000 ALTER TABLE `students` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-09-02 23:32:44
