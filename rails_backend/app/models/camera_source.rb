class CameraSource < ApplicationRecord
    has_many :detected_objects, dependent: :destroy
end
