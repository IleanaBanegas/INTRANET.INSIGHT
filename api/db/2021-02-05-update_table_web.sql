ALTER TABLE `webs_web` CHANGE `country_id` `country_id` INT NULL;
ALTER TABLE db_insight_new.webs_web DROP FOREIGN KEY webs_web_country_id_dcd989d5_fk_countries_country_id;
ALTER TABLE `webs_web` DROP `country_id`;

ALTER TABLE `webs_web` CHANGE `search_parameters` `description` LONGTEXT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL;
ALTER TABLE `webs_web` CHANGE `description` `description` VARCHAR(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL;

ALTER TABLE `webs_web` ADD `countries_ids` VARCHAR(255) NULL AFTER `status`;

INSERT INTO `countries_country` (`id`, `name`, `code`) VALUES (NULL, 'Todos los paises', 'ALL');

// TABALA TENDERS
ALTER TABLE db_insight_new.tenders_tender DROP FOREIGN KEY tenders_tender_country_id_086cdd76_fk_countries_country_id;
ALTER TABLE `tenders_tender` DROP `country_id`;
ALTER TABLE `tenders_tender` ADD `countries_ids` VARCHAR(255) NULL AFTER `closing_date`;
