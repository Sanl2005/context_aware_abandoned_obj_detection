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

ActiveRecord::Schema[8.1].define(version: 2026_03_05_034025) do
  # These are extensions that must be enabled in order to support this database
  enable_extension "pg_catalog.plpgsql"
  enable_extension "pgcrypto"

  create_table "abandoned_objects", id: :uuid, default: -> { "gen_random_uuid()" }, force: :cascade do |t|
    t.float "abandonment_score"
    t.bigint "camera_source_id", null: false
    t.datetime "created_at", null: false
    t.datetime "detected_at"
    t.datetime "expires_at"
    t.boolean "is_permanent", default: false
    t.string "location_type"
    t.string "object_type"
    t.string "person_id"
    t.string "threat_level"
    t.string "tracking_id"
    t.datetime "updated_at", null: false
    t.index ["camera_source_id"], name: "index_abandoned_objects_on_camera_source_id"
    t.index ["detected_at"], name: "index_abandoned_objects_on_detected_at"
    t.index ["expires_at"], name: "index_abandoned_objects_on_expires_at"
    t.index ["is_permanent"], name: "index_abandoned_objects_on_is_permanent"
  end

  create_table "active_storage_attachments", force: :cascade do |t|
    t.bigint "blob_id", null: false
    t.datetime "created_at", null: false
    t.string "name", null: false
    t.bigint "record_id", null: false
    t.string "record_type", null: false
    t.index ["blob_id"], name: "index_active_storage_attachments_on_blob_id"
    t.index ["record_type", "record_id", "name", "blob_id"], name: "index_active_storage_attachments_uniqueness", unique: true
  end

  create_table "active_storage_blobs", force: :cascade do |t|
    t.bigint "byte_size", null: false
    t.string "checksum"
    t.string "content_type"
    t.datetime "created_at", null: false
    t.string "filename", null: false
    t.string "key", null: false
    t.text "metadata"
    t.string "service_name", null: false
    t.index ["key"], name: "index_active_storage_blobs_on_key", unique: true
  end

  create_table "active_storage_variant_records", force: :cascade do |t|
    t.bigint "blob_id", null: false
    t.string "variation_digest", null: false
    t.index ["blob_id", "variation_digest"], name: "index_active_storage_variant_records_uniqueness", unique: true
  end

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
    t.string "location_type"
    t.string "name"
    t.jsonb "risk_profile_config"
    t.string "stream_url"
    t.datetime "updated_at", null: false
  end

  create_table "detected_objects", force: :cascade do |t|
    t.text "bbox"
    t.bigint "camera_source_id", null: false
    t.string "color"
    t.float "confidence"
    t.datetime "created_at", null: false
    t.datetime "first_seen_at"
    t.datetime "last_seen_at"
    t.string "object_type"
    t.integer "owner_id"
    t.string "risk_level"
    t.string "state"
    t.string "status"
    t.string "threat_level"
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

  add_foreign_key "abandoned_objects", "camera_sources"
  add_foreign_key "active_storage_attachments", "active_storage_blobs", column: "blob_id"
  add_foreign_key "active_storage_variant_records", "active_storage_blobs", column: "blob_id"
  add_foreign_key "alerts", "detected_objects"
  add_foreign_key "detected_objects", "camera_sources"
  add_foreign_key "object_events", "detected_objects"
  add_foreign_key "risk_assessments", "detected_objects"
end
