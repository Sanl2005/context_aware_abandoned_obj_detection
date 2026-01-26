class DetectedObject < ApplicationRecord
  belongs_to :camera_source
  has_many :object_events, dependent: :destroy
  has_many :risk_assessments, dependent: :destroy
  has_many :alerts, dependent: :destroy
  validates :track_id, presence: true
  validates :object_type, presence: true
end
