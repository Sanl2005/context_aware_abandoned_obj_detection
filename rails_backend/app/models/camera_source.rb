class CameraSource < ApplicationRecord
  has_many :detected_objects, dependent: :destroy
  
  validates :name, presence: true
  validates :stream_url, presence: true
  validates :location_type, presence: true
  
  enum :location_type, {
    public_open_crowded: "PUBLIC_OPEN_CROWDED",
    public_remote_area: "PUBLIC_REMOTE_AREA",
    semi_restricted_zone: "SEMI_RESTRICTED_ZONE"
  }, default: :public_open_crowded, prefix: true
  
  # Helper to get risk profile (could be parsed from JSONB)
  def risk_profile
    return {} unless risk_profile_config.present?
    risk_profile_config
  end
end
