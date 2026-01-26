class DetectedObject < ApplicationRecord
  belongs_to :camera_source
  has_many :object_events, dependent: :destroy
  has_many :risk_assessments, dependent: :destroy
  has_many :alerts, dependent: :destroy
end
