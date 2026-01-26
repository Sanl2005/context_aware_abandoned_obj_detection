class Alert < ApplicationRecord
  belongs_to :detected_object
  validates :message, presence: true
  validates :severity, presence: true
end
