-- phpMyAdmin SQL Dump
-- version 5.1.1deb5ubuntu1
-- https://www.phpmyadmin.net/
--
-- Host: localhost:3306
-- Erstellungszeit: 02. Apr 2026 um 06:23
-- Server-Version: 10.6.22-MariaDB-0ubuntu0.22.04.1
-- PHP-Version: 8.1.2-1ubuntu2.22

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Datenbank: `livextrem`
--

-- --------------------------------------------------------

--
-- Tabellenstruktur für Tabelle `content`
--

CREATE TABLE `content` (
  `content_id` bigint(20) UNSIGNED NOT NULL,
  `titel` varchar(150) NOT NULL,
  `beschreibung` text DEFAULT NULL,
  `kategorie` varchar(50) DEFAULT NULL,
  `plattform` varchar(50) DEFAULT NULL,
  `erstellt_am` datetime DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Daten für Tabelle `content`
--

INSERT INTO `content` (`content_id`, `titel`, `beschreibung`, `kategorie`, `plattform`, `erstellt_am`) VALUES
(1, 'Midnight Club L.A. Drift', 'Live vom Autotreff', 'Racing', 'Twitch', '2025-10-15 10:46:22'),
(2, 'Night Drift Munich', 'Live Drift Challenge in München', 'Racing', 'TikTok', '2025-10-20 19:00:00'),
(3, 'Trackday Nürburgring', 'RoadKing testet neue Reifen', 'Motorsport', 'Twitch', '2025-10-22 18:00:00'),
(4, 'Crew Talk #5', 'Livestream mit Community Q&A', 'Talkshow', 'TikTok', '2025-10-23 21:15:00'),
(5, 'Tech Setup Behind the Scenes', 'RoadKing zeigt sein Streaming-Setup', 'Tutorial', 'Twitch', '2025-10-25 17:30:00'),
(6, 'derFlaavius Einweihung', NULL, 'IRL', 'Twitch', '2026-02-19 10:36:11'),
(7, 'dieFlaavius Test', NULL, 'IRL', 'Twitch', '2026-02-19 10:37:08'),
(8, 'Test 135135', NULL, 'Test', 'Twitch', '2026-02-19 10:51:17'),
(9, 'Guten Morgen', NULL, 'IRL', 'Twitch', '2026-03-10 21:40:50'),
(10, 'Autorennen Norisring', NULL, 'IRL', 'Twitch', '2026-03-10 22:11:20'),
(12, 'rdf.connect liveXtrem Pitch Live', NULL, 'IRL', 'Twitch', '2026-03-10 22:13:27'),
(14, 'Papaaakaka', NULL, 'Pitches', 'Twitch', '2026-03-17 16:26:36'),
(15, 'rdf.connect Aftershow Party Live', NULL, 'IRL', 'Twitch', '2026-03-19 08:39:06'),
(16, 'Communityfrühstück', NULL, 'Just Chatting', 'Twitch', '2026-03-19 08:40:38'),
(17, 'GTA4 Online Stream', NULL, 'GTA IV', 'Twitch', '2026-03-19 08:41:04'),
(18, 'Heimlicher Stream im Unterricht', NULL, 'IRL', 'Twitch', '2026-03-19 08:42:29');

-- --------------------------------------------------------

--
-- Tabellenstruktur für Tabelle `finanzen`
--

CREATE TABLE `finanzen` (
  `finanz_id` bigint(20) UNSIGNED NOT NULL,
  `streamer_id` bigint(20) UNSIGNED NOT NULL,
  `betrag` decimal(10,2) NOT NULL,
  `typ` enum('Einnahme','Ausgabe') NOT NULL,
  `quelle` varchar(50) DEFAULT NULL,
  `kategorie` varchar(50) DEFAULT NULL,
  `datum` datetime NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Tabellenstruktur für Tabelle `moderator`
--

CREATE TABLE `moderator` (
  `moderator_id` bigint(20) UNSIGNED NOT NULL,
  `name` varchar(100) NOT NULL,
  `rechte_level` tinyint(3) UNSIGNED NOT NULL DEFAULT 1,
  `user_id` bigint(20) UNSIGNED DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Tabellenstruktur für Tabelle `roles`
--

CREATE TABLE `roles` (
  `role_id` bigint(20) UNSIGNED NOT NULL,
  `name` varchar(30) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Daten für Tabelle `roles`
--

INSERT INTO `roles` (`role_id`, `name`) VALUES
(4, 'ADMIN'),
(3, 'MANAGER'),
(2, 'MODERATOR'),
(1, 'STREAMER');

-- --------------------------------------------------------

--
-- Tabellenstruktur für Tabelle `streamer`
--

CREATE TABLE `streamer` (
  `streamer_id` bigint(20) UNSIGNED NOT NULL,
  `name` varchar(100) NOT NULL,
  `plattform` varchar(50) DEFAULT NULL,
  `email` varchar(100) DEFAULT NULL,
  `user_id` bigint(20) UNSIGNED DEFAULT NULL,
  `status` enum('Aktiv','Pause','Archiviert') NOT NULL DEFAULT 'Aktiv',
  `farbe` varchar(7) DEFAULT '#34C759'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Tabellenstruktur für Tabelle `streamer_finances`
--

CREATE TABLE `streamer_finances` (
  `finance_id` int(11) NOT NULL,
  `streamer_id` int(11) NOT NULL,
  `booking_date` datetime NOT NULL,
  `description` varchar(255) NOT NULL,
  `amount` decimal(10,2) NOT NULL,
  `entry_type` varchar(20) NOT NULL,
  `created_at` datetime NOT NULL DEFAULT current_timestamp(),
  `updated_at` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Tabellenstruktur für Tabelle `streamer_manager`
--

CREATE TABLE `streamer_manager` (
  `streamer_id` bigint(20) UNSIGNED NOT NULL,
  `user_id` bigint(20) UNSIGNED NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Tabellenstruktur für Tabelle `streamer_moderator`
--

CREATE TABLE `streamer_moderator` (
  `streamer_id` bigint(20) UNSIGNED NOT NULL,
  `moderator_id` bigint(20) UNSIGNED NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Tabellenstruktur für Tabelle `streamer_todos`
--

CREATE TABLE `streamer_todos` (
  `todo_id` int(11) NOT NULL,
  `streamer_id` int(11) NOT NULL,
  `task` varchar(60) NOT NULL,
  `done` tinyint(1) NOT NULL DEFAULT 0,
  `created_at` datetime NOT NULL DEFAULT current_timestamp(),
  `updated_at` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Tabellenstruktur für Tabelle `stream_planung`
--

CREATE TABLE `stream_planung` (
  `plan_id` bigint(20) UNSIGNED NOT NULL,
  `streamer_id` bigint(20) UNSIGNED NOT NULL,
  `content_id` bigint(20) UNSIGNED DEFAULT NULL,
  `datum` datetime NOT NULL,
  `thema` varchar(200) DEFAULT NULL,
  `status` enum('geplant','bestaetigt','abgesagt','fertig') DEFAULT 'geplant'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Tabellenstruktur für Tabelle `todo_liste`
--

CREATE TABLE `todo_liste` (
  `todo_id` bigint(20) UNSIGNED NOT NULL,
  `streamer_id` bigint(20) UNSIGNED NOT NULL,
  `titel` varchar(150) NOT NULL,
  `beschreibung` text DEFAULT NULL,
  `status` enum('offen','in_arbeit','erledigt') DEFAULT 'offen',
  `prioritaet` enum('hoch','mittel','niedrig') DEFAULT 'mittel',
  `faellig_am` date DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Tabellenstruktur für Tabelle `twitch_tokens`
--

CREATE TABLE `twitch_tokens` (
  `id` bigint(20) UNSIGNED NOT NULL,
  `user_id` bigint(20) UNSIGNED NOT NULL,
  `twitch_userid` varchar(50) DEFAULT NULL,
  `twitch_login` varchar(50) DEFAULT NULL,
  `twitch_displayname` varchar(50) DEFAULT NULL,
  `access_token` text DEFAULT NULL,
  `refresh_token` text DEFAULT NULL,
  `expires_in` int(11) DEFAULT NULL,
  `created_at` datetime NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Tabellenstruktur für Tabelle `users`
--

CREATE TABLE `users` (
  `user_id` bigint(20) UNSIGNED NOT NULL,
  `email` varchar(255) NOT NULL,
  `username` varchar(50) NOT NULL,
  `password_hash` varchar(255) NOT NULL,
  `created_at` datetime NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Tabellenstruktur für Tabelle `user_roles`
--

CREATE TABLE `user_roles` (
  `user_id` bigint(20) UNSIGNED NOT NULL,
  `role_id` bigint(20) UNSIGNED NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Indizes der exportierten Tabellen
--

--
-- Indizes für die Tabelle `content`
--
ALTER TABLE `content`
  ADD PRIMARY KEY (`content_id`);

--
-- Indizes für die Tabelle `finanzen`
--
ALTER TABLE `finanzen`
  ADD PRIMARY KEY (`finanz_id`),
  ADD KEY `streamer_id` (`streamer_id`,`datum`),
  ADD KEY `typ` (`typ`);

--
-- Indizes für die Tabelle `moderator`
--
ALTER TABLE `moderator`
  ADD PRIMARY KEY (`moderator_id`),
  ADD UNIQUE KEY `user_id` (`user_id`);

--
-- Indizes für die Tabelle `roles`
--
ALTER TABLE `roles`
  ADD PRIMARY KEY (`role_id`),
  ADD UNIQUE KEY `name` (`name`);

--
-- Indizes für die Tabelle `streamer`
--
ALTER TABLE `streamer`
  ADD PRIMARY KEY (`streamer_id`),
  ADD UNIQUE KEY `email` (`email`),
  ADD UNIQUE KEY `user_id` (`user_id`);

--
-- Indizes für die Tabelle `streamer_finances`
--
ALTER TABLE `streamer_finances`
  ADD PRIMARY KEY (`finance_id`),
  ADD KEY `idx_streamer_finances_streamer` (`streamer_id`),
  ADD KEY `idx_streamer_finances_date` (`booking_date`);

--
-- Indizes für die Tabelle `streamer_manager`
--
ALTER TABLE `streamer_manager`
  ADD PRIMARY KEY (`streamer_id`,`user_id`),
  ADD KEY `idx_streamer_manager_user` (`user_id`);

--
-- Indizes für die Tabelle `streamer_moderator`
--
ALTER TABLE `streamer_moderator`
  ADD PRIMARY KEY (`streamer_id`,`moderator_id`),
  ADD KEY `fk_sm_moderator` (`moderator_id`);

--
-- Indizes für die Tabelle `streamer_todos`
--
ALTER TABLE `streamer_todos`
  ADD PRIMARY KEY (`todo_id`),
  ADD KEY `idx_streamer_todos_streamer` (`streamer_id`);

--
-- Indizes für die Tabelle `stream_planung`
--
ALTER TABLE `stream_planung`
  ADD PRIMARY KEY (`plan_id`),
  ADD KEY `fk_sp_streamer` (`streamer_id`),
  ADD KEY `fk_sp_content` (`content_id`),
  ADD KEY `datum` (`datum`),
  ADD KEY `status` (`status`);

--
-- Indizes für die Tabelle `todo_liste`
--
ALTER TABLE `todo_liste`
  ADD PRIMARY KEY (`todo_id`),
  ADD KEY `fk_td_streamer` (`streamer_id`),
  ADD KEY `status` (`status`),
  ADD KEY `prioritaet` (`prioritaet`),
  ADD KEY `faellig_am` (`faellig_am`);

--
-- Indizes für die Tabelle `twitch_tokens`
--
ALTER TABLE `twitch_tokens`
  ADD PRIMARY KEY (`id`),
  ADD KEY `user_id` (`user_id`);

--
-- Indizes für die Tabelle `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`user_id`),
  ADD UNIQUE KEY `email` (`email`),
  ADD UNIQUE KEY `username` (`username`);

--
-- Indizes für die Tabelle `user_roles`
--
ALTER TABLE `user_roles`
  ADD PRIMARY KEY (`user_id`,`role_id`),
  ADD KEY `role_id` (`role_id`);

--
-- AUTO_INCREMENT für exportierte Tabellen
--

--
-- AUTO_INCREMENT für Tabelle `content`
--
ALTER TABLE `content`
  MODIFY `content_id` bigint(20) UNSIGNED NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=19;

--
-- AUTO_INCREMENT für Tabelle `finanzen`
--
ALTER TABLE `finanzen`
  MODIFY `finanz_id` bigint(20) UNSIGNED NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=6;

--
-- AUTO_INCREMENT für Tabelle `moderator`
--
ALTER TABLE `moderator`
  MODIFY `moderator_id` bigint(20) UNSIGNED NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=8;

--
-- AUTO_INCREMENT für Tabelle `roles`
--
ALTER TABLE `roles`
  MODIFY `role_id` bigint(20) UNSIGNED NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

--
-- AUTO_INCREMENT für Tabelle `streamer`
--
ALTER TABLE `streamer`
  MODIFY `streamer_id` bigint(20) UNSIGNED NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=33;

--
-- AUTO_INCREMENT für Tabelle `streamer_finances`
--
ALTER TABLE `streamer_finances`
  MODIFY `finance_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=7;

--
-- AUTO_INCREMENT für Tabelle `streamer_todos`
--
ALTER TABLE `streamer_todos`
  MODIFY `todo_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=8;

--
-- AUTO_INCREMENT für Tabelle `stream_planung`
--
ALTER TABLE `stream_planung`
  MODIFY `plan_id` bigint(20) UNSIGNED NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=36;

--
-- AUTO_INCREMENT für Tabelle `todo_liste`
--
ALTER TABLE `todo_liste`
  MODIFY `todo_id` bigint(20) UNSIGNED NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

--
-- AUTO_INCREMENT für Tabelle `twitch_tokens`
--
ALTER TABLE `twitch_tokens`
  MODIFY `id` bigint(20) UNSIGNED NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

--
-- AUTO_INCREMENT für Tabelle `users`
--
ALTER TABLE `users`
  MODIFY `user_id` bigint(20) UNSIGNED NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=16;

--
-- Constraints der exportierten Tabellen
--

--
-- Constraints der Tabelle `finanzen`
--
ALTER TABLE `finanzen`
  ADD CONSTRAINT `fk_fi_streamer` FOREIGN KEY (`streamer_id`) REFERENCES `streamer` (`streamer_id`) ON DELETE CASCADE;

--
-- Constraints der Tabelle `moderator`
--
ALTER TABLE `moderator`
  ADD CONSTRAINT `fk_moderator_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`) ON DELETE SET NULL;

--
-- Constraints der Tabelle `streamer`
--
ALTER TABLE `streamer`
  ADD CONSTRAINT `fk_streamer_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`) ON DELETE SET NULL;

--
-- Constraints der Tabelle `streamer_manager`
--
ALTER TABLE `streamer_manager`
  ADD CONSTRAINT `fk_streamer_manager_streamer` FOREIGN KEY (`streamer_id`) REFERENCES `streamer` (`streamer_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  ADD CONSTRAINT `fk_streamer_manager_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Constraints der Tabelle `streamer_moderator`
--
ALTER TABLE `streamer_moderator`
  ADD CONSTRAINT `fk_sm_moderator` FOREIGN KEY (`moderator_id`) REFERENCES `moderator` (`moderator_id`) ON DELETE CASCADE,
  ADD CONSTRAINT `fk_sm_streamer` FOREIGN KEY (`streamer_id`) REFERENCES `streamer` (`streamer_id`) ON DELETE CASCADE;

--
-- Constraints der Tabelle `stream_planung`
--
ALTER TABLE `stream_planung`
  ADD CONSTRAINT `fk_sp_content` FOREIGN KEY (`content_id`) REFERENCES `content` (`content_id`),
  ADD CONSTRAINT `fk_sp_streamer` FOREIGN KEY (`streamer_id`) REFERENCES `streamer` (`streamer_id`) ON DELETE CASCADE;

--
-- Constraints der Tabelle `todo_liste`
--
ALTER TABLE `todo_liste`
  ADD CONSTRAINT `fk_td_streamer` FOREIGN KEY (`streamer_id`) REFERENCES `streamer` (`streamer_id`) ON DELETE CASCADE;

--
-- Constraints der Tabelle `twitch_tokens`
--
ALTER TABLE `twitch_tokens`
  ADD CONSTRAINT `twitch_tokens_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`) ON DELETE CASCADE;

--
-- Constraints der Tabelle `user_roles`
--
ALTER TABLE `user_roles`
  ADD CONSTRAINT `user_roles_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`) ON DELETE CASCADE,
  ADD CONSTRAINT `user_roles_ibfk_2` FOREIGN KEY (`role_id`) REFERENCES `roles` (`role_id`) ON DELETE CASCADE;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
