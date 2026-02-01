module Api
  class DetectedObjectsController < ApplicationController
    skip_before_action :authorize_request, only: [:index, :show]
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
        # Auto create event log
        ObjectEvent.create!(
          detected_object: detected_object,
          event_type: "detected",
          details: "Detected from ML Service",
          occurred_at: Time.current
        )

        # Auto create risk assessment
        RiskAssessment.create!(
          detected_object: detected_object,
          risk_score: detected_object.confidence,
          risk_level: (detected_object.confidence.to_f >= 0.7 ? "high" : "low"),
          reason: "Auto generated from confidence score",
          assessed_at: Time.current
        )
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
