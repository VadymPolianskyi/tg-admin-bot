CREATE TABLE "admin_strike" (
  "id" varchar(64) NOT NULL,
  "reported_user_id" int NOT NULL,
  "from_user_id" int NOT NULL,
  "reason" varchar(254) NOT NULL,
  "time" timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY ("id")
)