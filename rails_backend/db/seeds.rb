# This file should ensure the existence of records required to run the application in every environment (production,
# development, test). The code here should be idempotent so that it can be executed at any point in every environment.
# The data can then be loaded with the bin/rails db:seed command (or created alongside the database with db:setup).
#
# Example:
#
#   ["Action", "Comedy", "Drama", "Horror"].each do |genre_name|
#     MovieGenre.find_or_create_by!(name: genre_name)
#   end

cam = CameraSource.find_or_create_by!(
  name: "Gate Camera",
  location: "Entrance",
  stream_url: "rtsp://example.com/live",
  is_active: true
)

obj = DetectedObject.find_or_create_by!(
  track_id: "T001",
  object_type: "bag",
  confidence: 0.91,
  bbox: "[120,80,240,190]",
  first_seen_at: Time.now - 2.minutes,
  last_seen_at: Time.now,
  status: "abandoned",
  camera_source: cam
)

Alert.find_or_create_by!(
  detected_object: obj,
  message: "Abandoned bag detected near entrance",
  severity: "high",
  is_sent: false
)

User.create!(
  name: "Admin",
  email: "admin@example.com",
  password: "admin123",
  password_confirmation: "admin123",
  role: "admin"
) if User.count == 0


