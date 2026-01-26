module Api
  class DetectedObjectsController < ApplicationController
    def index
      render json: DetectedObject.order(created_at: :desc)
    end

    def show
      detected_object = DetectedObject.find(params[:id])
      render json: detected_object
    end

    def create
      detected_object = DetectedObject.new(detected_object_params)

      if detected_object.save
        # Auto create alert if abandoned
        if detected_object.status == "abandoned"
          Alert.create!(
            detected_object: detected_object,
            message: "Abandoned object detected: #{detected_object.object_type}",
            severity: "high",
            is_sent: false
          )
        end

        render json: detected_object, status: :created
      else
        render json: { errors: detected_object.errors.full_messages }, status: :unprocessable_entity
      end
    end

    private

    def detected_object_params
      params.require(:detected_object).permit(
        :track_id, :object_type, :confidence, :bbox,
        :first_seen_at, :last_seen_at, :status, :camera_source_id
      )
    end
  end
end
