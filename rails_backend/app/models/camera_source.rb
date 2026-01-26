class CameraSource < ApplicationRecord
    has_many :detected_objects, dependent: :destroy
    validates :name, presence: true
    validates :stream_url, presence: true
end
