ALTER TABLE `tenders_tender` CHANGE `status` `status` VARCHAR(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '0: Nuevo 1: Presentada 2: No Presentada ';
ALTER TABLE `webs_web` ADD `note` TEXT NULL AFTER `countries_ids`;
