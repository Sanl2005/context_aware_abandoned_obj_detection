class DetectedObject < ApplicationRecord
  belongs_to :camera_source
  has_many :object_events, dependent: :destroy
  has_many :risk_assessments, dependent: :destroy
  has_many :alerts, dependent: :destroy

  validates :track_id, presence: true
  validates :object_type, presence: true
  
  enum :state, {
    visible: "VISIBLE",
    occluded: "OCCLUDED",
    reappeared: "REAPPEARED",
    confirmed_removed: "CONFIRMED_REMOVED",
    stationary: "STATIONARY",
    moving: "MOVING",
    unattended: "UNATTENDED",
    abandoned: "ABANDONED",
    lost: "LOST",
    new_state: "NEW"
  }, default: :visible, prefix: true

  enum :threat_level, {
    low_risk: "LOW_RISK",
    medium_risk: "MEDIUM_RISK",
    high_risk: "HIGH_RISK",
    unknown: "UNKNOWN"
  }, default: :unknown, prefix: true

  scope :active, -> { where.not(state: :confirmed_removed) }
  scope :high_risk, -> { where(threat_level: :high_risk) }
  scope :abandoned, -> { where("confidence > ?", 0.8) }
end
