-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1:3306
-- Generation Time: Nov 14, 2025 at 06:53 AM
-- Server version: 11.7.2-MariaDB
-- PHP Version: 8.3.14

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `services_particuliers`
--

-- --------------------------------------------------------

--
-- Table structure for table `categories`
--

DROP TABLE IF EXISTS `categories`;
CREATE TABLE IF NOT EXISTS `categories` (
  `id_categorie` int(11) NOT NULL AUTO_INCREMENT,
  `nom_categorie` varchar(100) NOT NULL,
  `description` text DEFAULT NULL,
  PRIMARY KEY (`id_categorie`)
) ENGINE=InnoDB AUTO_INCREMENT=22 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `categories`
--

INSERT INTO `categories` (`id_categorie`, `nom_categorie`, `description`) VALUES
(10, 'Fitness', 'Entraînement physique et musculation'),
(11, 'Sports de raquette', 'Tennis, Badminton, Squash'),
(12, 'Bien-être & Récupération', 'Massages, Yoga, Nutrition'),
(20, 'Coaching', NULL),
(21, 'Coaching', NULL);

-- --------------------------------------------------------

--
-- Table structure for table `reservations`
--

DROP TABLE IF EXISTS `reservations`;
CREATE TABLE IF NOT EXISTS `reservations` (
  `id_reservation` int(11) NOT NULL AUTO_INCREMENT,
  `id_service` int(11) NOT NULL,
  `id_utilisateur` int(11) NOT NULL,
  `date_reservation` date NOT NULL DEFAULT current_timestamp(),
  `date_souhaitee` time NOT NULL,
  PRIMARY KEY (`id_reservation`),
  KEY `nom_service` (`id_service`),
  KEY `nom_utilisateur` (`id_utilisateur`),
  KEY `idx_reservations_service` (`id_service`),
  KEY `idx_reservations_utilisateur` (`id_utilisateur`),
  KEY `idx_reservations_dates` (`date_reservation`,`date_souhaitee`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

--
-- Dumping data for table `reservations`
--

INSERT INTO `reservations` (`id_reservation`, `id_service`, `id_utilisateur`, `date_reservation`, `date_souhaitee`) VALUES
(2, 102, 4, '2025-11-28', '09:50:00'),
(3, 102, 4, '2025-11-28', '09:50:00'),
(4, 101, 4, '2025-11-29', '10:05:00'),
(5, 101, 4, '2025-11-22', '10:05:00'),
(6, 101, 4, '2025-11-21', '01:00:00'),
(7, 102, 4, '2025-11-21', '09:10:00');

-- --------------------------------------------------------

--
-- Table structure for table `services`
--

DROP TABLE IF EXISTS `services`;
CREATE TABLE IF NOT EXISTS `services` (
  `id_service` int(11) NOT NULL AUTO_INCREMENT,
  `id_categorie` int(11) NOT NULL,
  `titre` varchar(50) NOT NULL,
  `description` varchar(2000) NOT NULL,
  `localisation` varchar(50) NOT NULL,
  `date_creation` datetime DEFAULT current_timestamp(),
  `actif` tinyint(1) DEFAULT 1,
  `cout` decimal(8,2) DEFAULT 0.00,
  `nom_image` varchar(255) DEFAULT NULL,
  `id_utilisateur` int(11) NOT NULL,
  PRIMARY KEY (`id_service`),
  KEY `id_categorie` (`id_categorie`),
  KEY `nom` (`id_utilisateur`),
  KEY `idx_services_categorie` (`id_categorie`),
  KEY `idx_services_utilisateur` (`id_utilisateur`),
  KEY `idx_services_actif_date` (`actif`,`date_creation`)
) ENGINE=InnoDB AUTO_INCREMENT=108 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `services`
--

INSERT INTO `services` (`id_service`, `id_categorie`, `titre`, `description`, `localisation`, `date_creation`, `actif`, `cout`, `nom_image`, `id_utilisateur`) VALUES
(100, 10, 'Cours de Yoga débutant', 'Séance de yoga doux pour améliorer la flexibilité.', 'Gymnase A', '2025-11-10 01:35:35', 1, 10.00, 'yoga.jpg', 2),
(101, 11, 'Partenariat Tennis (Intermédiaire)', 'Recherche partenaire pour des matchs amicaux intensifs.', 'Parc Central', '2025-11-10 01:35:35', 1, 5.00, 'tennis.jpg', 3),
(102, 12, 'Massage sportif - 60 min', 'Récupération musculaire après effort.', 'Local 101', '2025-11-10 01:35:35', 1, 30.00, 'massage.jpg', 1),
(103, 10, 'Programme de Musculation', 'Plan d\'entraînement personnalisé (INACTIF).', 'En ligne', '2025-11-10 01:35:35', 0, 40.00, 'muscu.jpg', 2),
(104, 12, 'Natation', 'spot pour fille', '', '2025-11-11 16:54:18', 1, 10.00, NULL, 4),
(105, 11, 'football', 'Besoin de coequipier', 'Limoilou', '2025-11-13 20:06:13', 1, 25.00, '20251113_204323.png', 4),
(106, 10, 'yoga', 'Relaxation', 'quebec', '2025-11-13 20:29:58', 1, 0.00, '20251113_215509.png', 4),
(107, 10, 'Fitness', 'Rélaxation', 'Limoilou', '2025-11-13 21:56:53', 1, 15.00, '20251113_215712.png', 4);

-- --------------------------------------------------------

--
-- Table structure for table `utilisateurs`
--

DROP TABLE IF EXISTS `utilisateurs`;
CREATE TABLE IF NOT EXISTS `utilisateurs` (
  `id_utilisateur` int(11) NOT NULL AUTO_INCREMENT,
  `nom` varchar(20) NOT NULL,
  `prenom` varchar(20) NOT NULL,
  `courriel` varchar(50) NOT NULL,
  `mot_de_passe` varchar(255) NOT NULL,
  `credit` decimal(10,2) NOT NULL DEFAULT 0.00,
  `role` varchar(20) NOT NULL DEFAULT 'utilisateur',
  PRIMARY KEY (`id_utilisateur`),
  UNIQUE KEY `courriel` (`courriel`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

--
-- Dumping data for table `utilisateurs`
--

INSERT INTO `utilisateurs` (`id_utilisateur`, `nom`, `prenom`, `courriel`, `mot_de_passe`, `credit`, `role`) VALUES
(2, 'Dubois', 'Alice', 'alice@test.ca', 'sha256$r3o9p5d2$1c3d1f0a1e3d9f3b7c2d8e4f1a9c3e2f5b8a6d4e2c0e1a3d9b8c7f6e5d4a3b2c', 15.00, 'utilisateur'),
(3, 'Tremblay', 'Bob', 'bob@test.ca', 'sha256$a7b1c3d9$5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f', 20.00, 'utilisateur'),
(4, 'Admin', 'Garneau', 'admin@garneau.ca', 'e6065d6c3350792f283cdb5aa772a13c9393a453b06c96b24da38661a8baeeeb38b123647d7fd1e9873b1d6fe30a75451f83deebf5de17c0c52cc87485a66766', 95.00, 'admin');

--
-- Constraints for dumped tables
--

--
-- Constraints for table `reservations`
--
ALTER TABLE `reservations`
  ADD CONSTRAINT `fk_reservations_service` FOREIGN KEY (`id_service`) REFERENCES `services` (`id_service`) ON DELETE CASCADE ON UPDATE CASCADE,
  ADD CONSTRAINT `fk_reservations_utilisateur` FOREIGN KEY (`id_utilisateur`) REFERENCES `utilisateurs` (`id_utilisateur`) ON DELETE CASCADE ON UPDATE CASCADE,
  ADD CONSTRAINT `reservations_ibfk_1` FOREIGN KEY (`id_service`) REFERENCES `services` (`id_service`),
  ADD CONSTRAINT `reservations_ibfk_2` FOREIGN KEY (`id_utilisateur`) REFERENCES `utilisateurs` (`id_utilisateur`);

--
-- Constraints for table `utilisateurs`
--
ALTER TABLE `utilisateurs`
  ADD CONSTRAINT `utilisateurs_ibfk_1` FOREIGN KEY (`id_utilisateur`) REFERENCES `utilisateurs` (`id_utilisateur`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
