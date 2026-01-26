# This file is auto-generated from the current state of the database. Instead
# of editing this file, please use the migrations feature of Active Record to
# incrementally modify your database, and then regenerate this schema definition.
#
# This file is the source Rails uses to define your schema when running `bin/rails
# db:schema:load`. When creating a new database, `bin/rails db:schema:load` tends to
# be faster and is potentially less error prone than running all of your
# migrations from scratch. Old migrations may fail to apply correctly if those
# migrations use external dependencies or application code.
#
# It's strongly recommended that you check this file into your version control system.

ActiveRecord::Schema[8.1].define(version: 2026_01_26_134556) do
  # These are extensions that must be enabled in order to support this database
  enable_extension "pg_catalog.plpgsql"

  create_table "alerts", force: :cascade do |t|
    t.datetime "created_at", null: false
    t.bigint "detected_object_id", null: false
    t.boolean "is_sent", default: false
    t.text "message"
    t.datetime "sent_at"
    t.string "severity"
    t.datetime "updated_at", null: false
    t.index ["detected_object_id"], name: "index_alerts_on_detected_object_id"
  end

  create_table "camera_sources", force: :cascade do |t|
    t.datetime "created_at", null: false
    t.boolean "is_active", default: true
    t.string "location"
    t.string "name"
    t.string "stream_url"
    t.datetime "updated_at", null: false
  end

  create_table "detected_objects", force: :cascade do |t|
    t.text "bbox"
    t.bigint "camera_source_id", null: false
    t.float "confidence"
    t.datetime "created_at", null: false
    t.datetime "first_seen_at"
    t.datetime "last_seen_at"
    t.string "object_type"
    t.string "status"
    t.string "track_id"
    t.datetime "updated_at", null: false
    t.index ["camera_source_id"], name: "index_detected_objects_on_camera_source_id"
  end

  create_table "object_events", force: :cascade do |t|
    t.datetime "created_at", null: false
    t.text "details"
    t.bigint "detected_object_id", null: false
    t.string "event_type"
    t.datetime "occurred_at"
    t.datetime "updated_at", null: false
    t.index ["detected_object_id"], name: "index_object_events_on_detected_object_id"
  end

  create_table "risk_assessments", force: :cascade do |t|
    t.datetime "assessed_at"
    t.datetime "created_at", null: false
    t.bigint "detected_object_id", null: false
    t.text "reason"
    t.string "risk_level"
    t.float "risk_score"
    t.datetime "updated_at", null: false
    t.index ["detected_object_id"], name: "index_risk_assessments_on_detected_object_id"
  end

  create_table "users", force: :cascade do |t|
    t.datetime "created_at", null: false
    t.string "email"
    t.string "name"
    t.string "password_digest"
    t.string "role"
    t.datetime "updated_at", null: false
  end

  add_foreign_key "alerts", "detected_objects"
  add_foreign_key "detected_objects", "camera_sources"
  add_foreign_key "object_events", "detected_objects"
  add_foreign_key "risk_assessments", "detected_objects"
end
