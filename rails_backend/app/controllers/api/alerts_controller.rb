module Api
  class AlertsController < ApplicationController
    def index
      render json: Alert.order(created_at: :desc)
    end

    def show
      alert = Alert.find(params[:id])
      render json: alert
    end

    def create
      alert = Alert.new(alert_params)
      if alert.save
        render json: alert, status: :created
      else
        render json: { errors: alert.errors.full_messages }, status: :unprocessable_entity
      end
    end

    private

    def alert_params
      params.require(:alert).permit(:detected_object_id, :message, :severity, :is_sent, :sent_at)
    end
  end
end
