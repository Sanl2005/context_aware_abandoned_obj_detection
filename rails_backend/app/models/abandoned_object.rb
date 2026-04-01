class AbandonedObject < ApplicationRecord
  belongs_to :camera_source

  has_one_attached :object_image
  has_one_attached :person_image

  scope :active, -> { where("expires_at > ? OR is_permanent = ?", Time.current, true) }
  scope :expired, -> { where("expires_at <= ? AND is_permanent = ?", Time.current, false) }
end
